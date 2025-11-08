# EVE: The Everyday Virtual Executive - App Overview

## Part 1: High-Level Overview

### What is EVE?
EVE is an AI-powered productivity assistant that helps users process and act on meeting recordings or voice notes. It combines multiple AI services to transcribe speech, extract action items, generate summaries, and even speak back to users.

### Core Features
1. **Audio Processing**
   - Record or upload audio files
   - Real-time transcription using OpenAI Whisper
   - Support for both file upload and live recording

2. **Task Management**
   - Automatic task extraction from transcripts
   - Due date recognition and scheduling
   - Priority assignment and confidence scoring
   - Google Calendar integration for task scheduling

3. **Smart Summaries**
   - Concise meeting summaries
   - Detailed bullet points of key decisions
   - Voice playback of summaries
   - Communication pattern analysis

4. **Voice Interaction**
   - Text-to-speech summary playback
   - Customizable voice settings
   - Fallback to text when voice synthesis is unavailable

### Architecture
- **Frontend**: Next.js + React + TailwindCSS
  - `frontend/app/page.tsx` - Main application page
  - `frontend/components/` - Reusable UI components
    - `RecordingPanel.tsx` - Audio recording/upload
    - `TasksPanel.tsx` - Task display and management
    - `SummaryPanel.tsx` - Summary display
    - `Dashboard.tsx` - Analytics and stats

- **Backend**: FastAPI + Python
  - `backend/main.py` - API routes and service composition
  - `backend/services/` - Individual service integrations
  - WebSocket support for real-time audio processing

## Part 2: Technical Implementation Details

### 1. Audio Processing & Transcription
**Files:**
- `backend/services/transcription.py`
- `frontend/components/RecordingPanel.tsx`

**Implementation:**
- Uses OpenAI's Whisper model via `openai.Audio.transcriptions`
- Model: `whisper-1`
- Supports both file upload and streaming audio
- WebSocket connection for real-time transcription updates

### 2. Task Extraction & Analysis
**Files:**
- `backend/services/reasoning.py`
- `frontend/components/TasksPanel.tsx`

**Implementation:**
- Uses OpenAI GPT-4o for:
  1. Transcript cleaning and segmentation
  2. Task extraction with structured JSON output
- JSON schema for tasks includes:
  - action description
  - context
  - due dates (ISO8601)
  - priority levels
  - confidence scores
  - source section references

### 3. Summary Generation
**Files:**
- `backend/services/reasoning.py`
- `frontend/components/SummaryPanel.tsx`

**Implementation:**
- Uses OpenAI GPT-4 for generating:
  - One-line summary
  - 3-6 bullet points of key details
  - Custom voice-optimized summary text
- Structured JSON output for consistent frontend rendering

### 4. Voice Synthesis
**Files:**
- `backend/services/tts.py`

**Implementation:**
- Uses ElevenLabs API
- Default voice: "Rachel" (ID: 21m00Tcm4TlvDq8ikWAM)
- Model: eleven_turbo_v2_5
- Configurable voice settings:
  - stability: 0.5
  - similarity_boost: 0.75
- Returns MP3 audio bytes
- Graceful fallback to text in demo mode

### 5. Calendar Integration
**Files:**
- `backend/services/calendar_service.py`

**Implementation:**
- Google Calendar API integration
- OAuth 2.0 authentication flow
- Automatic event creation from tasks
- Smart scheduling with confidence scoring
- Timezone-aware datetime handling

### 6. Analytics & Monitoring
**Files:**
- `backend/services/analytics.py`
- `frontend/components/Dashboard.tsx`

**Implementation:**
- Optional Amplitude integration for usage tracking
- Tracks events like:
  - Transcriptions completed
  - Tasks extracted
  - Calendar events created
- Background thread for non-blocking analytics

### API Endpoints

#### Core Endpoints
- `POST /transcribe/file` - Audio file transcription
- `POST /process/transcript` - Task extraction and summary
- `POST /voice/summary` - Generate spoken summary
- `WS /ws/realtime` - Real-time audio streaming

#### Calendar Integration
- `GET /calendar/auth` - Start OAuth flow
- `POST /calendar/schedule` - Create calendar events
- `GET /calendar/callback` - OAuth callback handling

#### Additional Features
- `POST /study/generate` - Create study materials
- `POST /analyze/sentiment` - Analyze communication
- `POST /gemini/insights` - Additional AI insights

### Environmental Configuration
Required API Keys:
- `OPENAI_API_KEY` - For GPT-4o and Whisper
- `ELEVENLABS_API_KEY` - For voice synthesis
- `GEMINI_API_KEY` - For alternative summaries
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` - For calendar

Optional:
- `AMPLITUDE_API_KEY` - For analytics

### Error Handling & Fallbacks
- Services provide demo mode responses when API keys are missing
- Graceful degradation of voice features to text
- Structured error responses via FastAPI
- WebSocket error recovery for streaming audio
- Confidence scoring for calendar scheduling

For development and testing instructions, see:
- `START_HERE.md` - Quick setup guide
- `README.md` - Complete documentation
- `test-api-keys.sh` - API key validation script