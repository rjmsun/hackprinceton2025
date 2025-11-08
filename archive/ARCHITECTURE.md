# 🏗️ EVE Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                    (Browser/Microphone)                      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTP/WebSocket
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (Port 3000)                       │
│                     Next.js + React                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Components:                                          │  │
│  │  • RecordingPanel    (audio capture)                 │  │
│  │  • TasksPanel        (extracted tasks UI)            │  │
│  │  • SummaryPanel      (meeting summary)               │  │
│  │  • Dashboard         (analytics)                     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ REST API / WebSocket
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (Port 8000)                        │
│                        FastAPI                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Routes (main.py):                               │  │
│  │  • POST /transcribe/file                             │  │
│  │  • POST /process/transcript                          │  │
│  │  • POST /calendar/schedule                           │  │
│  │  • POST /voice/summary                               │  │
│  │  • WS /ws/realtime                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────┼────────────────────────────┐   │
│  │         SERVICE LAYER   │                            │   │
│  └────────────────────────┼────────────────────────────┘   │
└─────────────────────────┬─┴───────────────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ OpenAI API  │ │Anthropic API│ │ElevenLabs   │
    │             │ │             │ │   API       │
    │ • Whisper   │ │ • Claude    │ │ • TTS       │
    │ • GPT-4o    │ │   3.5       │ │             │
    └─────────────┘ └─────────────┘ └─────────────┘
           │              │              │
           └──────────────┼──────────────┘
                          │
           ┌──────────────┴──────────────┐
           │                             │
           ▼                             ▼
    ┌─────────────┐             ┌──────────────┐
    │  Google     │             │  Amplitude   │
    │  Calendar   │             │  (Optional)  │
    └─────────────┘             └──────────────┘
```

---

## Data Flow

### 1. Audio Recording/Upload

```
User clicks "Record" or uploads file
    │
    ▼
[RecordingPanel.tsx]
    │
    ├─► MediaRecorder API (for live recording)
    │   or
    └─► File input (for uploads)
    │
    ▼
POST /transcribe/file
    │
    ▼
[transcription.py]
    │
    ├─► OpenAI Whisper API
    │       │
    │       ▼
    │   Audio → Text transcript
    │
    └─► Returns transcript to frontend
```

### 2. Transcript Processing

```
Transcript received
    │
    ▼
POST /process/transcript
    │
    ▼
[reasoning.py]
    │
    ├─► Step 1: clean_transcript()
    │   │
    │   ├─► GPT-4o API
    │   └─► Returns: { sections: [...] }
    │
    ├─► Step 2: extract_tasks()
    │   │
    │   ├─► Claude 3.5 API
    │   └─► Returns: { tasks: [...] }
    │
    └─► Step 3: generate_summary()
        │
        ├─► GPT-4o API
        └─► Returns: { short_summary, detailed_summary }
    │
    ▼
Returns all to frontend
```

### 3. Calendar Scheduling

```
User selects tasks
    │
    ▼
POST /calendar/schedule
    │
    ▼
[reasoning.py] create_event_suggestion()
    │
    ├─► GPT-4o converts task → calendar event
    │
    ▼
[calendar_service.py] create_event()
    │
    ├─► Google Calendar API
    └─► Creates event
    │
    ▼
Returns event confirmation
```

### 4. Voice Summary

```
Summary generated
    │
    ▼
POST /voice/summary
    │
    ▼
[reasoning.py] generate_voice_summary()
    │
    ├─► GPT-4o creates spoken text
    │
    ▼
[tts.py] text_to_speech()
    │
    ├─► ElevenLabs API
    └─► Returns audio bytes
    │
    ▼
Browser plays audio
```

---

## API Key Flow

```
1. User creates .env file:
   ┌────────────────────────────┐
   │ OPENAI_API_KEY=sk-proj-... │
   │ ANTHROPIC_API_KEY=sk-ant...│
   │ ELEVENLABS_API_KEY=...     │
   └────────────────────────────┘

2. Backend loads on startup:
   [main.py]
   │
   ├─► load_dotenv() → loads .env
   │
   ├─► os.getenv("OPENAI_API_KEY")
   │
   └─► Initializes services with keys

3. Services use keys:
   [transcription.py]
       openai.OpenAI(api_key=key)
   
   [reasoning.py]
       openai.OpenAI(api_key=openai_key)
       anthropic.Anthropic(api_key=anthropic_key)
   
   [tts.py]
       headers = {"xi-api-key": elevenlabs_key}
```

---

## File Structure with Purpose

```
hackprinceton2025/
│
├── .env                          ← YOUR API KEYS GO HERE
├── env.example                   ← Template for .env
│
├── start.sh                      ← Run this to start EVE
├── install.sh                    ← Run this first (install deps)
├── test-api-keys.sh              ← Verify API keys work
│
├── backend/                      ← Python FastAPI server
│   ├── main.py                   ← API routes + service init
│   ├── run.py                    ← Alternative entry point
│   ├── requirements.txt          ← Python dependencies
│   │
│   └── services/                 ← AI integrations
│       ├── transcription.py      ← OpenAI Whisper
│       ├── reasoning.py          ← GPT-4o + Claude 3.5
│       ├── tts.py                ← ElevenLabs TTS
│       ├── calendar_service.py   ← Google Calendar
│       └── analytics.py          ← Amplitude (optional)
│
└── frontend/                     ← Next.js React app
    ├── app/
    │   ├── page.tsx              ← Main page
    │   ├── layout.tsx            ← App layout
    │   └── globals.css           ← Styles
    │
    └── components/
        ├── RecordingPanel.tsx    ← Audio recording UI
        ├── TasksPanel.tsx        ← Tasks display
        ├── SummaryPanel.tsx      ← Summary + voice
        └── Dashboard.tsx         ← Analytics cards
```

---

## Service Initialization

```python
# backend/main.py

from dotenv import load_dotenv
load_dotenv()  # Loads .env into environment

# Initialize services with API keys
transcription_service = TranscriptionService(
    api_key=os.getenv("OPENAI_API_KEY")
)

reasoning_service = ReasoningService(
    openai_key=os.getenv("OPENAI_API_KEY"),
    anthropic_key=os.getenv("ANTHROPIC_API_KEY")
)

calendar_service = CalendarService(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
)

tts_service = TTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

analytics_service = AnalyticsService(
    api_key=os.getenv("AMPLITUDE_API_KEY")
)
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14 | React framework |
| | React 18 | UI components |
| | TypeScript | Type safety |
| | Tailwind CSS | Styling |
| | Axios | HTTP client |
| **Backend** | FastAPI | API framework |
| | Python 3.9+ | Runtime |
| | Uvicorn | ASGI server |
| | python-dotenv | Env loading |
| **AI APIs** | OpenAI Whisper | Transcription |
| | OpenAI GPT-4o | Reasoning |
| | Anthropic Claude 3.5 | Task extraction |
| | ElevenLabs | Voice synthesis |
| **Integrations** | Google Calendar API | Scheduling |
| | Amplitude API | Analytics |

---

## Sponsor API Usage

| Sponsor | API | Used In | Purpose |
|---------|-----|---------|---------|
| **OpenAI** | Whisper | `transcription.py` | Audio → Text |
| | GPT-4o | `reasoning.py` | Summarization, scheduling |
| **Anthropic** | Claude 3.5 | `reasoning.py` | Task extraction |
| **ElevenLabs** | TTS | `tts.py` | Voice summaries |
| **Google** | Calendar API | `calendar_service.py` | Auto-scheduling |
| **MLH** | Amplitude | `analytics.py` | Usage tracking |

---

## Adding New Features

### Add a new AI service:

1. Create `backend/services/new_service.py`:
```python
class NewService:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def do_something(self, input_data):
        # API call here
        return result
```

2. Initialize in `backend/main.py`:
```python
new_service = NewService(api_key=os.getenv("NEW_API_KEY"))
```

3. Add route:
```python
@app.post("/new/endpoint")
async def new_endpoint(data: Request):
    result = await new_service.do_something(data)
    return result
```

4. Call from frontend:
```typescript
const response = await axios.post(`${API_URL}/new/endpoint`, data)
```

---

## Security Notes

✅ `.env` is in `.gitignore` (never committed)  
✅ API keys loaded server-side only  
✅ CORS configured for localhost  
✅ OAuth tokens stored securely  

For production:
- Use environment variables (not `.env` files)
- Enable HTTPS
- Add rate limiting
- Implement auth middleware

---

## Performance

- Audio transcription: ~2-5 seconds per minute
- Task extraction: ~3-7 seconds (depends on length)
- Voice synthesis: ~1-2 seconds per sentence
- Total pipeline: ~10-15 seconds for 2-minute meeting

---

## Debugging

**Backend logs:**
```bash
cd backend
python main.py
# Watch terminal for errors
```

**Frontend logs:**
```bash
cd frontend
npm run dev
# Check browser console
```

**API docs:**
- Backend: http://localhost:8000/docs
- Interactive testing with Swagger UI

---

This architecture is designed to be modular, scalable, and sponsor-friendly! 🚀

