# EVE Backend

FastAPI backend with AI integrations

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
# or
python run.py
# or
uvicorn main:app --reload
```

Backend runs on http://localhost:8000

API docs: http://localhost:8000/docs

## Environment

Create `.env` in project root:

```bash
OPENAI_API_KEY=sk-proj-...
ELEVENLABS_API_KEY=...
GEMINI_API_KEY=...
```

## Services

### `transcription.py` - Audio to Text
- OpenAI Whisper API
- Handles file uploads and streaming

### `reasoning.py` - AI Processing
- OpenAI GPT-4o for summarization and task extraction
- Prompt engineering for structured outputs

### `tts.py` - Text to Speech
- ElevenLabs API
- Voice summaries

### `calendar_service.py` - Calendar Integration
- Google Calendar API
- OAuth 2.0 flow
- Event creation

### `analytics.py` - Usage Tracking
- Amplitude API (optional)

## API Endpoints

- `POST /transcribe/file` - Upload audio
- `POST /process/transcript` - Extract tasks
- `POST /calendar/schedule` - Create events
- `POST /voice/summary` - Generate voice
- `WS /ws/realtime` - Real-time streaming

## Adding New Services

1. Create `services/new_service.py`
2. Initialize in `main.py`
3. Add routes in `main.py`

