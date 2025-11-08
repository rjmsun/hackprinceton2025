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
from services.snowflake_service import SnowflakeService
from services.coffee_chat import CoffeeChatService

load_dotenv()

app = FastAPI(title="EVE API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
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
snowflake_service = SnowflakeService()
coffee_service = CoffeeChatService(openai_key=os.getenv("OPENAI_API_KEY"))

# Models
class TranscriptRequest(BaseModel):
    text: str
    user_id: Optional[str] = "default"
    timezone: Optional[str] = "America/New_York"

class VisionMetrics(BaseModel):
    face_detected: Optional[bool] = None
    smile_confidence: Optional[float] = None
    eye_contact_confidence: Optional[float] = None
    avg_head_angle_degrees: Optional[float] = None
    nod_count: Optional[int] = None
    frame_count: Optional[int] = None

class AudioFeatures(BaseModel):
    avg_pitch: Optional[float] = None
    energy: Optional[float] = None
    speech_rate: Optional[float] = None
    sentiment: Optional[float] = None

class CoffeeProcessRequest(BaseModel):
    text: str
    user_id: Optional[str] = "default"
    timezone: Optional[str] = "America/New_York"
    vision_metrics: Optional[VisionMetrics] = None
    audio_features: Optional[AudioFeatures] = None
    store: Optional[bool] = False
    calendar_access_token: Optional[str] = None

class FollowupDraftRequest(BaseModel):
    person_name: Optional[str] = None
    company: Optional[str] = None
    highlights: List[str] = []
    ask: Optional[str] = None
    vibe_label: str = "Solid"

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
        content = await file.read()
        transcript = await transcription_service.transcribe_file(content, file.filename)
        
        # Fact-check and enhance transcript using GPT-4o
        if validate:
            transcript = await transcription_service.validate_and_enhance_transcript(transcript)
        
        return {"transcript": transcript, "status": "success", "validated": validate}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/snowflake/store")
async def store_in_snowflake(request: TranscriptRequest):
    """Store transcript and data in Snowflake"""
    try:
        # Get processed data
        cleaned = await reasoning_service.clean_transcript(request.text)
        tasks = await reasoning_service.extract_tasks(cleaned["sections"], timezone=request.timezone)
        summary = await reasoning_service.generate_summary(cleaned["sections"], tasks["tasks"])
        
        # Store in Snowflake
        success = snowflake_service.store_transcript(
            user_id=request.user_id,
            transcript=request.text,
            summary=summary,
            tasks=tasks["tasks"]
        )
        
        return {"status": "success" if success else "snowflake_not_configured", "stored": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/snowflake/conversations/{user_id}")
async def get_conversations(user_id: str, limit: int = 10):
    """Get user's conversation history from Snowflake"""
    try:
        conversations = snowflake_service.get_user_conversations(user_id, limit)
        return {"conversations": conversations, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/snowflake/test")
async def test_snowflake():
    """Test Snowflake connection"""
    try:
        connected = snowflake_service.test_connection()
        return {"connected": connected, "status": "success" if connected else "not_configured"}
    except Exception as e:
        return {"connected": False, "error": str(e), "status": "error"}

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

# New coffee chat processing endpoint
@app.post("/coffee/process")
async def process_coffee_chat(request: CoffeeProcessRequest):
    try:
        # 0) Validate and fact-check transcript (GPT-4o)
        validated_text = await transcription_service.validate_and_enhance_transcript(request.text)
        
        # 1) Clean transcript (GPT-4o)
        cleaned = await reasoning_service.clean_transcript(validated_text)

        # 2) Tasks via structured extraction
        tasks_dict = await reasoning_service.extract_tasks(cleaned["sections"], timezone=request.timezone)
        tasks = tasks_dict.get("tasks", [])

        # 3) Tips, follow-ups, content evidence
        tips_block = coffee_service.extract_tips_and_followups(cleaned["sections"]) or {}
        tips = tips_block.get("tips", [])
        follow_ups = tips_block.get("follow_ups", [])
        content_evidence = tips_block.get("content_evidence", [])

        # 4) Content score
        content_score = coffee_service.compute_content_score(tips, follow_ups, content_evidence)

        # 5) Vibe components
        vision_dict = request.vision_metrics.dict() if request.vision_metrics else None
        audio_dict = request.audio_features.dict() if request.audio_features else None
        vibe = coffee_service.combine_vibe(vision_dict, audio_dict, content_score)

        # 6) Summary and coaching (TTS text)
        coach = coffee_service.generate_coaching_and_spoken(tasks, tips, vibe.get("vibe_label", "Solid")) or {}

        # 7) Optional: create calendar events for due-dated tasks
        created_events: List[Dict[str, Any]] = []
        if request.calendar_access_token:
            for task in tasks:
                if task.get("due"):
                    event_suggestion = await reasoning_service.create_event_suggestion(task, timezone=request.timezone)
                    if event_suggestion.get("event_suggestion") and event_suggestion.get("event_suggestion", {}).get("start_time"):
                        evt = await calendar_service.create_event(request.calendar_access_token, event_suggestion["event_suggestion"])
                        created_events.append({"task_id": task.get("id"), **evt})

        # 8) Optional store to Snowflake
        audio_tts_url = None  # placeholder; streaming TTS endpoint returns bytes
        final_summary = await reasoning_service.generate_summary(cleaned["sections"], tasks)

        if request.store:
            try:
                snowflake_service.store_transcript(
                    user_id=request.user_id,
                    transcript=request.text,
                    summary={
                        "summary": final_summary,
                        "coach": coach,
                        "vibe": vibe,
                        "tips": tips,
                        "follow_ups": follow_ups,
                    },
                    tasks=tasks,
                )
            except Exception:
                pass

        session_payload = {
            "session_id": f"s-{datetime.utcnow().timestamp()}",
            "transcript": request.text,
            "sections": cleaned.get("sections", []),
            "tasks": tasks,
            "tips": tips,
            "follow_ups": follow_ups,
            "vibe": {
                "score": vibe.get("vibe_score"),
                "label": vibe.get("vibe_label"),
                "components": vibe.get("components"),
                "evidence": [e.get("text") for e in content_evidence][:5],
            },
            "audio_tts": audio_tts_url,
            "created_events": created_events,
            "metadata": {"duration_s": None, "consent": True},
            "coach": coach,
        }

        return {"status": "success", "data": session_payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/followup/draft")
async def draft_followup(request: FollowupDraftRequest):
    try:
        email = coffee_service.draft_followup_email(
            person_name=request.person_name,
            company=request.company,
            highlights=request.highlights,
            ask=request.ask,
            vibe_label=request.vibe_label,
        )
        return {"status": "success", "email": email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

