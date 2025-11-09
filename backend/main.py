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
from pathlib import Path
import tempfile

from services.transcription import TranscriptionService
from services.reasoning import ReasoningService
from services.calendar_service import CalendarService
from services.tts import TTSService
from services.gemini_service import GeminiService
from services.coaching_service import CoachingService
from services.vibe_service import VibeService
from services.interactive_coaching_service import InteractiveCoachingService
from services.video_service import VideoProcessor, VideoAnalysisAggregator
from services.vision_analyzers import HybridVisionAnalyzer

load_dotenv()

app = FastAPI(
    title="EVE API",
    description="AI-powered video and audio analysis platform",
    version="1.0.0"
)

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
gemini_service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))
coaching_service = CoachingService(openai_key=os.getenv("OPENAI_API_KEY"))
vibe_service = VibeService()
interactive_coaching_service = InteractiveCoachingService(openai_key=os.getenv("OPENAI_API_KEY"))
video_processor = VideoProcessor()
vision_analyzer = HybridVisionAnalyzer(
    openai_key=os.getenv("OPENAI_API_KEY"),
    gemini_key=os.getenv("GEMINI_API_KEY")
)
video_aggregator = VideoAnalysisAggregator()

# Models
class TranscriptRequest(BaseModel):
    text: str
    user_id: Optional[str] = "default"
    timezone: Optional[str] = "America/New_York"
    context: Optional[str] = "general"
    media_type: Optional[str] = "audio"



class TaskApproval(BaseModel):
    task_id: str
    approved: bool
    modifications: Optional[Dict[str, Any]] = None

class InteractiveRequest(BaseModel):
    transcript: str
    context: str
    coaching_insights: Optional[Dict] = None

class FeedbackRequest(BaseModel):
    original_question: str
    user_response: str
    context: str
    coaching_tip: Optional[str] = ""
    scenario_type: str

class ConversationStartRequest(BaseModel):
    transcript: str
    context: str
    coaching_insights: Optional[Dict] = None

class ConversationContinueRequest(BaseModel):
    user_message: str
    conversation_history: List[Dict]
    context_data: Dict
    session_type: str

class CalendarAuth(BaseModel):
    code: str

@app.get("/")
async def root():
    return {"status": "EVE API running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    import subprocess
    
    # Check ffmpeg
    ffmpeg_installed = False
    ffmpeg_version = "Not installed"
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            ffmpeg_installed = True
            ffmpeg_version = result.stdout.split('\n')[0].split('version')[1].split()[0] if 'version' in result.stdout else "installed"
    except:
        pass
    
    openai_configured = bool(os.getenv("OPENAI_API_KEY")) and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here"
    gemini_configured = bool(os.getenv("GEMINI_API_KEY")) and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here"
    bedrock_configured = bool(os.getenv("AWS_ACCESS_KEY_ID")) or bool(os.getenv("AWS_BEARER_TOKEN_BEDROCK"))
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "video_analysis_ready": ffmpeg_installed and openai_configured,
        "services": {
            "ffmpeg": {
                "installed": ffmpeg_installed,
                "version": ffmpeg_version,
                "required_for": "video analysis"
            },
            "openai_api": {
                "configured": openai_configured,
                "required_for": "GPT-4o Vision, Whisper transcription"
            },
            "gemini_api": {
                "configured": gemini_configured,
                "required_for": "optional (not used for video)"
            },
            "aws_bedrock": {
                "configured": bedrock_configured,
                "required_for": "emotional vibe analysis"
            }
        },
        "warnings": [
            "⚠️ ffmpeg not installed - video analysis will NOT work. Install: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)" if not ffmpeg_installed else None,
            "⚠️ OpenAI API key not configured - core features will not work" if not openai_configured else None,
            "⚠️ AWS Bedrock not configured - vibe analysis will not work" if not bedrock_configured else None
        ]
    }

@app.post("/transcribe/file")
async def transcribe_audio_file(
    file: UploadFile = File(...), 
    validate: bool = True,
    analyze_video: bool = False,
    vision_mode: str = "balanced"  # "fast", "balanced", "detailed"
):
    """
    Upload audio/video file for transcription and analysis
    
    Args:
        file: Audio or video file
        validate: Whether to validate/enhance transcript with GPT-4o
        analyze_video: If video, whether to run visual analysis
        vision_mode: "fast" (Gemini only), "balanced" (hybrid), "detailed" (GPT-4o only)
    """
    temp_files = []  # Track files to cleanup
    session_id = None
    
    try:
        filename = file.filename or "media.mp3"
        file_size_mb = file.size / (1024 * 1024) if file.size else 0
        print(f"Received file: {filename}, content_type: {file.content_type}, size: {file_size_mb:.2f}MB")
        
        # Check file size (200MB limit for videos, 100MB for audio)
        max_size = 200 * 1024 * 1024  # 200MB for videos
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {file_size_mb:.1f}MB. Maximum size is 200MB for videos, 100MB for audio."
            )
        
        # Check if this is a video file (prefer content-type over extension)
        content_type = file.content_type or ""
        is_audio_ct = content_type.startswith("audio/")
        is_video_ct = content_type.startswith("video/")
        is_video_ext = video_processor.is_video_file(filename)
        # If content-type says audio, force audio even if extension is e.g. .webm
        is_video = (is_video_ct or (is_video_ext and not is_audio_ct))
        print(f"File type detected: {'Video' if is_video else 'Audio'} (content_type={content_type})")
        
        if is_video and analyze_video:
            print(f"🎥 Video file detected: {filename}")
            print(f"Video analysis requested: {analyze_video}")
            
            # Check if required API keys are available for video analysis
            if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
                return {
                    "transcript": "ERROR: OpenAI API key required for video analysis",
                    "video_analysis": {
                        "error": "OPENAI_API_KEY not configured. Video analysis requires GPT-4o Vision.",
                        "solution": "Add OPENAI_API_KEY=sk-... to your .env file"
                    },
                    "is_video": True,
                    "status": "error"
                }
            
            if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_gemini_api_key_here":
                print("⚠️ Warning: Gemini API key not configured. Using OpenAI only (slower).")
            
            # Save uploaded file temporarily
            print("💾 Saving uploaded video to temporary file...")
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix)
            file_content = await file.read()
            print(f"📁 Read {len(file_content)} bytes from upload")
            temp_video.write(file_content)
            temp_video.flush()
            temp_video_path = temp_video.name
            temp_files.append(temp_video_path)
            print(f"💾 Saved to: {temp_video_path}")
            
            # 1. Extract audio from video
            print("📻 Extracting audio from video...")
            audio_path = video_processor.extract_audio(temp_video_path)
            temp_files.append(audio_path)
            
            # 2. Transcribe audio
            print("🎤 Transcribing audio with Whisper...")
            with open(audio_path, 'rb') as audio_file:
                transcript = await transcription_service.transcribe_file_obj(audio_file, "extracted_audio.wav")
            
            if validate:
                transcript = await transcription_service.validate_and_enhance_transcript(transcript)
            
            # 3. Extract frames from video (OPTIMIZED MODE - smart sampling)
            print(f"🎞️ Extracting frames (mode: {vision_mode})...")
            # OPTIMIZED: Smart frame sampling based on video length
            video_duration = video_processor.get_video_duration(temp_video_path)
            
            if video_duration <= 30:  # Short videos: more frames
                max_frames = 15
                fps = max(0.5, max_frames / max(video_duration, 1))
            elif video_duration <= 120:  # Medium videos: balanced sampling
                max_frames = 12
                fps = max(0.1, max_frames / max(video_duration, 1))
            else:  # Long videos: sparse sampling
                max_frames = 10
                fps = max(0.05, max_frames / max(video_duration, 1))
            
            # Use higher resolution for better analysis quality
            frames = video_processor.extract_frames(temp_video_path, fps=fps, max_dimension=512)
            
            # Limit to max_frames if we got too many
            if len(frames) > max_frames:
                import random
                frames = random.sample(frames, max_frames)
                frames.sort(key=lambda x: x['timestamp'])
            
            print(f"🎯 Selected {len(frames)} key frames for analysis (duration: {video_duration:.1f}s)")
            session_id = frames[0]["session_id"] if frames else None
            
            # 4. Analyze frames with GPT-4o Vision in BATCHES (fast but quality)
            print(f"👁️ Analyzing {len(frames)} frames with GPT-4o Vision (batched)...")
            if not frames:
                print("⚠️ No frames extracted from video!")
                return {
                    "transcript": transcript,
                    "video_analysis": {
                        "total_frames": 0,
                        "error": "No frames could be extracted from video",
                        "solution": "Check video format and content"
                    },
                    "is_video": True,
                    "status": "success"
                }
            
            try:
                frame_results = await vision_analyzer.analyze_video_frames(frames, mode="detailed")
                print(f"🔍 Vision analysis returned {len(frame_results)} results")
                
                # Filter out any error frames
                valid_frames = [f for f in frame_results if "error" not in f and "timestamp" in f]
                if not valid_frames:
                    print("⚠️ All frames failed analysis")
                    return {
                        "transcript": transcript,
                        "video_analysis": {
                            "total_frames": len(frames),
                            "error": "Vision analysis failed for all frames",
                            "solution": "Check OpenAI API key and quota"
                        },
                        "is_video": True,
                        "status": "success"
                    }
                frame_results = valid_frames
            except Exception as e:
                print(f"❌ Vision analysis failed: {e}")
                return {
                    "transcript": transcript,
                    "video_analysis": {
                        "total_frames": len(frames),
                        "error": f"Vision analysis failed: {str(e)}",
                        "solution": "Check OpenAI API key and network"
                    },
                    "is_video": True,
                    "status": "success"
                }
        
            # 5. Quick aggregation + vibe check with Amazon Bedrock
            print("📊 Aggregating results...")
            video_summary = video_aggregator.aggregate_frame_results(frame_results, transcript)
            
            # ALWAYS add Amazon Bedrock vibe analysis for videos - this is a key feature
            print("🎭 Running Amazon Bedrock emotional analysis...")
            try:
                from services.vibe_service import VibeService
                vibe_service_bedrock = VibeService()
                vibe_result = await vibe_service_bedrock.analyze_vibe(transcript, context="video")
                
                # Check if it's an error response
                if vibe_result.get('vibe') == 'Error':
                    error_msg = vibe_result.get('evidence', ['Unknown error'])[0]
                    if 'Model use case details' in error_msg or 'AccessDenied' in error_msg:
                        video_summary['bedrock_vibe_analysis'] = {
                            "vibe": "Bedrock access not enabled",
                            "confidence": 0,
                            "note": "AWS Bedrock requires account setup. Visit AWS Console to enable Claude model access.",
                            "error_type": "access_denied"
                        }
                    else:
                        video_summary['bedrock_vibe_analysis'] = {
                            "vibe": "Bedrock error", 
                            "confidence": 0, 
                            "note": error_msg,
                            "error_type": "configuration_error"
                        }
                elif vibe_result.get('vibe') == 'Not configured':
                    video_summary['bedrock_vibe_analysis'] = {
                        "vibe": "Bedrock not configured",
                        "confidence": 0,
                        "note": "AWS credentials not found in .env file. Add AWS_ACCESS_KEY_ID or AWS_BEARER_TOKEN_BEDROCK",
                        "error_type": "not_configured"
                    }
                else:
                    # Successfully got vibe analysis
                    video_summary['bedrock_vibe_analysis'] = vibe_result
                    print(f"✅ Amazon Bedrock analysis complete: {vibe_result.get('vibe', 'N/A')} (confidence: {vibe_result.get('confidence', 0):.2f})")
            except Exception as e:
                print(f"⚠️ Bedrock vibe analysis failed: {e}")
                video_summary['bedrock_vibe_analysis'] = {
                    "vibe": "Bedrock unavailable", 
                    "confidence": 0, 
                    "note": f"Error: {str(e)}",
                    "error_type": "system_error"
                }
            video_summary["narrative"] = f"Analyzed {len(frames)} frames from {video_summary.get('video_duration_seconds', 0):.0f}s video. Found {len(video_summary.get('key_scenes', []))} key moments."
            
            print(f"✅ Video analysis complete: {len(frames)} frames, {len(video_summary.get('key_scenes', []))} key scenes")
            
            return {
                "transcript": transcript,
                "video_analysis": video_summary,
                "raw_frames": frame_results if vision_mode == "detailed" else [],  # Include raw data only in detailed mode
                "is_video": True,
                "status": "success",
                "validated": validate,
                "vision_mode": vision_mode
            }
        
        else:
            # Standard audio transcription (existing flow)
            print("🎤 Audio file - using standard transcription")
            file.file.seek(0)
            transcript = await transcription_service.transcribe_file_obj(file.file, filename)
        if validate:
            transcript = await transcription_service.validate_and_enhance_transcript(transcript)
        return {
            "transcript": transcript,
            "is_video": False,
            "status": "success",
            "validated": validate
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"Transcription/Analysis error: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {error_msg}")
    
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        
        # Cleanup frame session
        if session_id:
            try:
                video_processor.cleanup_session(session_id)
            except:
                pass

@app.post("/process/transcript")
async def process_transcript(request: TranscriptRequest):
    """SPEED OPTIMIZED: Process transcript with adaptive summaries and coaching"""
    try:
        start_ts = datetime.utcnow()
        text = request.text
        context = request.context
        word_count = len(text.split())
        
        print(f"[FAST] Processing {word_count} words with context: {context}...")

        # SPEED: Skip cleaning for short transcripts, run everything in parallel
        if word_count < 200:
            # Ultra-fast path for short transcripts
            sections = [{"title": "Brief", "speakered_text": [{"speaker": "Speaker", "text": text}]}]
            
            # Run tasks + both summaries + coaching in parallel
            tasks_task = asyncio.create_task(reasoning_service.extract_tasks(sections, timezone=request.timezone))
            openai_task = asyncio.create_task(reasoning_service.generate_summary(sections, []))
            gemini_task = asyncio.create_task(gemini_service.generate_summary_gemini(text))
            coaching_task = asyncio.create_task(coaching_service.generate_coaching_insights(text, context))
            vibe_task = asyncio.create_task(vibe_service.analyze_vibe(text, context))
            
            try:
                tasks_dict, summary_openai, summary_gemini, coaching_insights, vibe_analysis = await asyncio.gather(
                    tasks_task, openai_task, gemini_task, coaching_task, vibe_task, return_exceptions=True
                )
            except Exception:
                # Fallback if parallel fails
                tasks_dict = {"tasks": []}
                summary_openai, summary_gemini, coaching_insights, vibe_analysis = None, None, None, None
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
            coaching_task = asyncio.create_task(coaching_service.generate_coaching_insights(text, context))
            vibe_task = asyncio.create_task(vibe_service.analyze_vibe(text, context))
            
            # Wait for tasks first, then use for OpenAI summary
            try:
                tasks_dict = await tasks_task
                tasks_list = tasks_dict.get("tasks", []) if isinstance(tasks_dict, dict) else []
            except Exception:
                tasks_list = []
            
            openai_task = asyncio.create_task(reasoning_service.generate_summary(sections, tasks_list))
            
            try:
                summary_openai, summary_gemini, coaching_insights, vibe_analysis = await asyncio.gather(
                    openai_task, gemini_task, coaching_task, vibe_task, return_exceptions=True
                )
            except Exception:
                summary_openai, summary_gemini, coaching_insights, vibe_analysis = None, None, None, None

        # Normalize results
        tasks_list = tasks_dict.get("tasks", []) if isinstance(tasks_dict, dict) else []
        
        # Handle exceptions in results
        if isinstance(summary_openai, Exception):
            print(f"[FAST] OpenAI failed: {summary_openai}")
            summary_openai = None
        if isinstance(summary_gemini, Exception):
            print(f"[FAST] Gemini failed: {summary_gemini}")
            summary_gemini = None
        if isinstance(coaching_insights, Exception):
            print(f"[FAST] Coaching failed: {coaching_insights}")
            coaching_insights = None
        if isinstance(vibe_analysis, Exception):
            print(f"[FAST] Vibe check failed: {vibe_analysis}")
            vibe_analysis = None

        duration = (datetime.utcnow() - start_ts).total_seconds()
        print(f"[FAST] Completed in {duration:.1f}s")

        # Analytics removed for simplicity

        if not summary_openai and not summary_gemini:
            raise Exception("Both AI summaries failed. Check API keys and network.")

        return {
            "tasks": tasks_list,
            "summary_openai": summary_openai,
            "summary_gemini": summary_gemini,
            "coaching_insights": coaching_insights,
            "vibe_analysis": vibe_analysis,
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

@app.post("/interactive/scenarios")
async def generate_interactive_scenarios(request: InteractiveRequest):
    """Generate interactive coaching scenarios"""
    try:
        scenarios = await interactive_coaching_service.generate_interactive_scenarios(
            request.transcript, 
            request.context, 
            request.coaching_insights
        )
        return {"scenarios": scenarios, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interactive/feedback")
async def provide_interactive_feedback(request: FeedbackRequest):
    """Provide feedback on user's response in interactive mode"""
    try:
        if request.scenario_type == "lecture_practice":
            feedback = await interactive_coaching_service.generate_conceptual_explanation(
                request.original_question,
                request.user_response, 
                request.context
            )
        else:
            feedback = await interactive_coaching_service.provide_response_feedback(
                request.original_question,
                request.user_response,
                request.context,
                request.coaching_tip
            )
        return feedback
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation/start")
async def start_conversation(request: ConversationStartRequest):
    """Start a new conversational practice session"""
    try:
        session_data = await interactive_coaching_service.start_conversation_session(
            request.transcript,
            request.context,
            request.coaching_insights
        )
        
        # Also generate the audio for the opening message
        if session_data.get("opening_message"):
            audio_data = await tts_service.text_to_speech(session_data["opening_message"])
            
            # Return both text and audio in base64
            import base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            session_data["opening_audio"] = audio_base64
        
        return {"session": session_data, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation/continue")
async def continue_conversation(request: ConversationContinueRequest):
    """Continue the conversational practice session"""
    try:
        response_data = await interactive_coaching_service.continue_conversation(
            request.user_message,
            request.conversation_history,
            request.context_data,
            request.session_type
        )
        
        # Generate audio for the assistant's response
        if response_data.get("assistant_message"):
            audio_data = await tts_service.text_to_speech(response_data["assistant_message"])
            
            # Return both text and audio in base64
            import base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            response_data["audio"] = audio_base64
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation/speak")
async def speak_text(text: str):
    """Convert text to speech for conversation"""
    try:
        audio_data = await tts_service.text_to_speech(text)
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=speech.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

