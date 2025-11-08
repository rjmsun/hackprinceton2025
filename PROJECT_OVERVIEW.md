# EVE: The Everyday Virtual Executive

## What It Does

EVE listens to conversations (coffee chats, lectures, meetings), transcribes them, extracts actionable insights, and autonomously takes actions like scheduling calendar events.

## Complete Pipeline (All APIs Used)

### Complete Flow (Every API Used)

```
1. Audio Input
   ↓
   [OpenAI Whisper] → Raw transcript
   ↓
   [GPT-4o Fact-Check] → Validated transcript (fixes errors, corrects terms)
   ↓
   [GPT-4o Clean] → Segmented sections with speakers
   ↓
   [Claude 3.5 Extract] → Tasks, tips, follow-ups
   ↓
   [Gemini Cross-Validate] → Additional insights & validation
   ↓
   [GPT-4o Summary] → Short + detailed summaries
   ↓
   [Coffee Chat Service - GPT-4o] → Tips, vibe score, coaching
   ↓
   [Google Calendar] → Auto-schedule events (if tasks have dates)
   ↓
   [ElevenLabs TTS] → Voice confirmation
   ↓
   [Snowflake] → Store for history (optional)
   ↓
   [Amplitude] → Track analytics
```

**Every step uses AI APIs - no wasted integrations!**

### API Usage

| API | Used For | When |
|-----|----------|------|
| **OpenAI Whisper** | Audio → Text | Every transcription |
| **OpenAI GPT-4o** | Fact-checking, cleaning, summaries, coaching | After transcription, during processing |
| **Anthropic Claude** | Task extraction, structured data | After cleaning |
| **Google Gemini** | Cross-validation, additional insights | After extraction |
| **ElevenLabs** | Text → Speech | After processing complete |
| **Google Calendar** | Create events | When tasks have dates |
| **Snowflake** | Store history | Optional, when user opts in |

## Key Endpoints

### Main Processing
- `POST /transcribe/file` - Upload audio, get validated transcript
- `POST /process/transcript` - Full pipeline: validate → clean → extract → summarize
- `POST /coffee/process` - Coffee chat mode: adds tips, vibe scoring, coaching

### Actions
- `POST /calendar/schedule` - Create calendar events from tasks
- `POST /voice/summary` - Generate spoken summary
- `POST /followup/draft` - Draft follow-up email

### Storage
- `POST /snowflake/store` - Save session to Snowflake
- `GET /snowflake/conversations/{user_id}` - Get history

## Fact-Checking Pipeline

Every transcript goes through validation:
1. **Whisper** produces raw transcript
2. **GPT-4o** fact-checks and corrects:
   - Fixes transcription errors
   - Corrects technical terms (e.g., "CS214" not "see 214")
   - Improves clarity
   - Preserves original meaning
3. **Claude 3.5** extracts structured data from validated text
4. **Gemini** provides cross-validation insights

## Project Structure

```
backend/
  main.py              # API endpoints
  services/
    transcription.py   # Whisper + fact-checking
    reasoning.py       # GPT-4o + Claude extraction
    coffee_chat.py     # Tips, vibe, coaching
    gemini_service.py  # Cross-validation
    tts.py            # ElevenLabs voice
    calendar_service.py # Google Calendar
    snowflake_service.py # Data storage

frontend/
  components/
    RecordingPanel.tsx  # Audio capture
    TasksPanel.tsx      # Display tasks
    SummaryPanel.tsx    # Show summaries
    Dashboard.tsx      # Analytics
```

## Quick Start

1. Add API keys to `.env`
2. `cd backend && python main.py`
3. `cd frontend && npm run dev`
4. Open http://localhost:3000

## Demo Flow

1. Upload audio → See validated transcript
2. Process → See tasks, tips, summary, vibe score
3. Add to calendar → Event created
4. Play voice → Hear confirmation

