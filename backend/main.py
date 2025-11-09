from fastapi import FastAPI, HTTPException, UploadFile, File, Request
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

# CORS configuration for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Services
transcription_service = TranscriptionService(api_key=os.getenv("OPENAI_API_KEY"))
reasoning_service = ReasoningService(
    openai_key=os.getenv("OPENAI_API_KEY")
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
    """SPEED OPTIMIZED: Process transcript with adaptive summaries"""
    try:
        start_ts = datetime.utcnow()
        text = request.text
        word_count = len(text.split())
        
        print(f"[FAST] Processing {word_count} words...")

        # SPEED: Skip cleaning for short transcripts, run everything in parallel
        if word_count < 200:
            # Ultra-fast path for short transcripts
            sections = [{"title": "Brief", "speakered_text": [{"speaker": "Speaker", "text": text}]}]
            
            # Run tasks + both summaries in parallel
            tasks_task = asyncio.create_task(reasoning_service.extract_tasks(sections, timezone=request.timezone))
            openai_task = asyncio.create_task(reasoning_service.generate_summary(sections, []))
            gemini_task = asyncio.create_task(gemini_service.generate_summary_gemini(text))
            
            try:
                tasks_dict, summary_openai, summary_gemini = await asyncio.gather(
                    tasks_task, openai_task, gemini_task, return_exceptions=True
                )
            except Exception:
                # Fallback if parallel fails
                tasks_dict = {"tasks": []}
                summary_openai = None
                summary_gemini = None
        else:
            # Standard path: clean first, then parallel processing
            try:
                cleaned = await reasoning_service.clean_transcript(text)
                sections = cleaned.get("sections", [])
            except Exception:
                sections = [{"title": "Conversation", "speakered_text": [{"speaker": "Speaker", "text": text}]}]
            
            # Run all AI calls in parallel
            tasks_task = asyncio.create_task(reasoning_service.extract_tasks(sections, timezone=request.timezone))
            gemini_task = asyncio.create_task(gemini_service.generate_summary_gemini(text))
            
            # Wait for tasks first, then use for OpenAI summary
            try:
                tasks_dict = await tasks_task
                tasks_list = tasks_dict.get("tasks", []) if isinstance(tasks_dict, dict) else []
            except Exception:
                tasks_list = []
            
            openai_task = asyncio.create_task(reasoning_service.generate_summary(sections, tasks_list))
            
            try:
                summary_openai, summary_gemini = await asyncio.gather(
                    openai_task, gemini_task, return_exceptions=True
                )
            except Exception:
                summary_openai = summary_gemini = None

        # Normalize results
        tasks_list = tasks_dict.get("tasks", []) if isinstance(tasks_dict, dict) else []
        
        # Handle exceptions in results
        if isinstance(summary_openai, Exception):
            print(f"[FAST] OpenAI failed: {summary_openai}")
            summary_openai = None
        if isinstance(summary_gemini, Exception):
            print(f"[FAST] Gemini failed: {summary_gemini}")
            summary_gemini = None

        duration = (datetime.utcnow() - start_ts).total_seconds()
        print(f"[FAST] Completed in {duration:.1f}s")

        # Analytics (fire and forget)
        try:
            analytics_service.track_event(
                user_id=request.user_id,
                event_name="transcript_processed_fast",
                properties={
                    "word_count": word_count,
                    "task_count": len(tasks_list),
                    "duration_s": duration,
                    "fast_path": word_count < 200
                }
            )
        except:
            pass

        if not summary_openai and not summary_gemini:
            raise Exception("Both AI summaries failed. Check API keys and network.")

        return {
            "tasks": tasks_list,
            "summary_openai": summary_openai,
            "summary_gemini": summary_gemini,
            "summary": summary_openai or summary_gemini,
            "word_count": word_count,
            "duration_s": duration,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/auth")
async def get_calendar_auth_url():
    """Get Google OAuth authorization URL - redirect to backend callback"""
    try:
        # Use backend callback URL
        redirect_uri = "http://localhost:8000/calendar/callback"
        auth_url = calendar_service.get_auth_url(redirect_uri)
        return {"auth_url": auth_url, "redirect_uri": redirect_uri}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/callback")
async def calendar_oauth_callback(code: str):
    """Handle OAuth callback and exchange code for token"""
    try:
        # Use backend callback URL (same as in auth)
        redirect_uri = "http://localhost:8000/calendar/callback"
        
        # Exchange code for token
        token_data = calendar_service.exchange_code_for_token(code, redirect_uri)
        
        # Redirect to frontend success page with tokens
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
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
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

