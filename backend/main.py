from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime

from services.transcription import TranscriptionService
from services.reasoning import ReasoningService
from services.calendar_service import CalendarService
from services.tts import TTSService
from services.analytics import AnalyticsService
from services.gemini_service import GeminiService

load_dotenv()

app = FastAPI(title="EVE API")

# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for file uploads
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
transcription_service = TranscriptionService(api_key=os.getenv("OPENAI_API_KEY"))
reasoning_service = ReasoningService(
    openai_key=os.getenv("OPENAI_API_KEY"),
    anthropic_key=os.getenv("ANTHROPIC_API_KEY")
)
calendar_service = CalendarService(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
)
tts_service = TTSService(api_key=os.getenv("ELEVENLABS_API_KEY"))
analytics_service = AnalyticsService(api_key=os.getenv("AMPLITUDE_API_KEY"))
gemini_service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))

# Models
class TranscriptRequest(BaseModel):
    text: str
    user_id: Optional[str] = "default"
    timezone: Optional[str] = "America/New_York"



class TaskApproval(BaseModel):
    task_id: str
    approved: bool
    modifications: Optional[Dict[str, Any]] = None

class CalendarAuth(BaseModel):
    code: str

@app.get("/")
async def root():
    return {"status": "EVE API running", "version": "1.0.0"}

@app.post("/transcribe/file")
async def transcribe_audio_file(file: UploadFile = File(...), validate: bool = True):
    """Upload audio file for transcription with optional fact-checking"""
    try:
        # Log file info for debugging
        print(f"Received file: {file.filename}, content_type: {file.content_type}, size: {file.size if hasattr(file, 'size') else 'unknown'}")
        
        # Stream-friendly: use underlying file object instead of reading all to memory
        file.file.seek(0)
        transcript = await transcription_service.transcribe_file_obj(file.file, file.filename or "audio.mp3")
        
        # Fact-check and enhance transcript using GPT-4o
        if validate:
            transcript = await transcription_service.validate_and_enhance_transcript(transcript)
        
        return {"transcript": transcript, "status": "success", "validated": validate}
    except Exception as e:
        error_msg = str(e)
        print(f"Transcription error: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {error_msg}")

@app.post("/process/transcript")
async def process_transcript(request: TranscriptRequest):
    """Process transcript: validate, clean, extract tasks, generate summary"""
    try:
        # Step 0: Validate and fact-check transcript (GPT-4o)
        validated_text = await transcription_service.validate_and_enhance_transcript(request.text)
        
        # Step 1: Clean and segment transcript (GPT-4o)
        cleaned = await reasoning_service.clean_transcript(validated_text)
        
        # Step 2: Extract tasks (Claude 3.5)
        tasks = await reasoning_service.extract_tasks(
            cleaned["sections"], 
            timezone=request.timezone
        )
        
        # Step 3: Generate summary (GPT-4o)
        summary = await reasoning_service.generate_summary(
            cleaned["sections"], 
            tasks["tasks"]
        )
        
        # Step 4: Cross-validate with Gemini for additional insights
        gemini_insights = await gemini_service.extract_insights(validated_text)
        
        # Log to analytics
        analytics_service.track_event(
            user_id=request.user_id,
            event_name="transcript_processed",
            properties={
                "task_count": len(tasks["tasks"]),
                "section_count": len(cleaned["sections"])
            }
        )
        
        return {
            "cleaned": cleaned,
            "tasks": tasks["tasks"],
            "summary": summary,
            "gemini_insights": gemini_insights.get("insights", {}),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/auth")
async def get_calendar_auth_url():
    """Get Google OAuth authorization URL"""
    try:
        redirect_uri = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/google/callback"
        auth_url = calendar_service.get_auth_url(redirect_uri)
        return {"auth_url": auth_url, "redirect_uri": redirect_uri}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/callback")
async def calendar_oauth_callback(code: str, request: Request):
    """Handle OAuth callback and exchange code for token"""
    try:
        # Get redirect URI from frontend URL
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        redirect_uri = f"{frontend_url}/auth/google/callback"
        
        # Exchange code for token
        token_data = calendar_service.exchange_code_for_token(code, redirect_uri)
        
        # Redirect to frontend with token in URL (in production, use secure cookie/session)
        return RedirectResponse(
            url=f"{frontend_url}/auth/success?access_token={token_data['access_token']}&refresh_token={token_data.get('refresh_token', '')}"
        )
    except Exception as e:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(
            url=f"{frontend_url}/auth/error?error={str(e)}"
        )

@app.post("/calendar/schedule")
async def schedule_tasks(tasks: List[Dict], access_token: str):
    """Create calendar events from tasks"""
    try:
        results = []
        for task in tasks:
            if task.get("due"):
                event_suggestion = await reasoning_service.create_event_suggestion(
                    task, 
                    timezone="America/New_York"
                )
                
                if event_suggestion.get("calendar_confidence", 0) > 0.7:
                    event = await calendar_service.create_event(
                        access_token,
                        event_suggestion["event_suggestion"]
                    )
                    results.append({
                        "task_id": task["id"],
                        "event": event,
                        "status": "created"
                    })
                else:
                    results.append({
                        "task_id": task["id"],
                        "status": "needs_confirmation",
                        "suggestion": event_suggestion
                    })
            else:
                clarification = await reasoning_service.generate_clarification(task)
                results.append({
                    "task_id": task["id"],
                    "status": "needs_clarification",
                    "question": clarification
                })
        
        return {"results": results, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/summary")
async def generate_voice_summary(actions: List[Dict]):
    """Generate spoken summary of actions"""
    try:
        # Generate text summary
        summary_text = await reasoning_service.generate_voice_summary(actions)
        
        # Convert to speech
        audio_data = await tts_service.text_to_speech(summary_text)
        
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=summary.mp3",
                "X-Summary-Text": summary_text
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/study/generate")
async def generate_study_materials(request: TranscriptRequest):
    """Generate flashcards and quiz from transcript"""
    try:
        materials = await reasoning_service.generate_study_materials(request.text)
        return materials
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/sentiment")
async def analyze_communication(request: TranscriptRequest):
    """Analyze communication patterns and sentiment"""
    try:
        analysis = await reasoning_service.analyze_sentiment(request.text)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gemini/insights")
async def get_gemini_insights(request: TranscriptRequest):
    """Extract insights using Gemini API"""
    try:
        insights = await gemini_service.extract_insights(request.text)
        return {"insights": insights, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gemini/summary")
async def get_gemini_summary(request: TranscriptRequest):
    """Generate summary using Gemini API"""
    try:
        summary = await gemini_service.generate_summary_gemini(request.text)
        return {"summary": summary, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    """WebSocket for real-time audio streaming and transcription"""
    await websocket.accept()
    
    try:
        buffer = []
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                # Audio chunk received
                audio_chunk = data["bytes"]
                buffer.append(audio_chunk)
                
                # Stream transcription
                transcript = await transcription_service.transcribe_stream(audio_chunk)
                
                if transcript:
                    await websocket.send_json({
                        "type": "transcript",
                        "data": transcript,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            elif "text" in data:
                message = json.loads(data["text"])
                
                if message.get("action") == "process":
                    # Process accumulated transcript
                    full_transcript = message.get("transcript", "")
                    
                    # Clean
                    cleaned = await reasoning_service.clean_transcript(full_transcript)
                    await websocket.send_json({
                        "type": "cleaned",
                        "data": cleaned
                    })
                    
                    # Extract tasks
                    tasks = await reasoning_service.extract_tasks(cleaned["sections"])
                    await websocket.send_json({
                        "type": "tasks",
                        "data": tasks
                    })
                    
                    # Generate summary
                    summary = await reasoning_service.generate_summary(
                        cleaned["sections"],
                        tasks["tasks"]
                    )
                    await websocket.send_json({
                        "type": "summary",
                        "data": summary
                    })
                    
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

