# How EVE Works - Complete Flow

## The Pipeline

### Step 1: Audio Input
- User uploads audio file OR records live
- Frontend sends to backend

### Step 2: Transcription (OpenAI Whisper)
```
Audio file → Whisper API → Raw transcript text
```
**Service:** `transcription.py`

### Step 3: Fact-Checking (OpenAI GPT-4o) ✨ NEW
```
Raw transcript → GPT-4o validates → Corrected transcript
```
- Fixes transcription errors
- Corrects technical terms (e.g., "CS214" not "see 214")
- Improves clarity
- Preserves meaning

**Service:** `transcription.py::validate_and_enhance_transcript()`

### Step 4: Cleaning & Segmentation (OpenAI GPT-4o)
```
Validated transcript → GPT-4o → Segmented sections with speakers
```
**Service:** `reasoning.py::clean_transcript()`

### Step 5: Task Extraction (Anthropic Claude 3.5)
```
Sections → Claude → Tasks, tips, follow-ups
```
- Extracts actionable items
- Identifies career/class tips
- Finds follow-up opportunities
- Assigns owners, dates, priorities

**Service:** `reasoning.py::extract_tasks()`

### Step 6: Cross-Validation (Google Gemini) ✨ NEW
```
Validated text → Gemini → Additional insights
```
- Provides alternative perspective
- Validates extracted information
- Adds context

**Service:** `gemini_service.py::extract_insights()`

### Step 7: Summary Generation (OpenAI GPT-4o)
```
Sections + Tasks → GPT-4o → Short + detailed summaries
```
**Service:** `reasoning.py::generate_summary()`

### Step 8: Coffee Chat Features (OpenAI GPT-4o)
```
Sections → Coffee Service → Tips, vibe score, coaching
```
- Extracts career tips
- Computes vibe score (vision + audio + content)
- Generates coaching suggestions

**Service:** `coffee_chat.py`

### Step 9: Calendar Actions (Google Calendar API)
```
Tasks with dates → Calendar Service → Events created
```
**Service:** `calendar_service.py`

### Step 10: Voice Summary (ElevenLabs)
```
Summary text → ElevenLabs → Audio file
```
**Service:** `tts.py`

### Step 11: Storage (Snowflake - Optional)
```
All data → Snowflake → Persistent storage
```
**Service:** `snowflake_service.py`

## API Usage Summary

| Step | API | Purpose |
|------|-----|----------|
| 2 | OpenAI Whisper | Audio → Text |
| 3 | OpenAI GPT-4o | Fact-check transcript |
| 4 | OpenAI GPT-4o | Clean & segment |
| 5 | Anthropic Claude | Extract structured data |
| 6 | Google Gemini | Cross-validate |
| 7 | OpenAI GPT-4o | Generate summaries |
| 8 | OpenAI GPT-4o | Tips, vibe, coaching |
| 9 | Google Calendar | Create events |
| 10 | ElevenLabs | Text → Speech |
| 11 | Snowflake | Store history |

## Example Request Flow

```bash
# 1. Upload audio
POST /transcribe/file
→ Returns: validated transcript

# 2. Process full pipeline
POST /process/transcript
→ Returns: cleaned, tasks, summary, gemini_insights

# 3. Coffee chat mode (with vibe)
POST /coffee/process
→ Returns: tasks, tips, follow_ups, vibe, coaching

# 4. Schedule tasks
POST /calendar/schedule
→ Creates Google Calendar events

# 5. Get voice summary
POST /voice/summary
→ Returns: audio file
```

## Key Features

✅ **Multi-API Validation**: Every transcript validated by GPT-4o  
✅ **Cross-Validation**: Gemini provides second opinion  
✅ **Autonomous Actions**: Calendar events created automatically  
✅ **Voice Feedback**: ElevenLabs speaks confirmations  
✅ **Vibe Scoring**: Combines vision + audio + content  
✅ **Persistent Storage**: Snowflake for history  

## All APIs Working Together

1. **Whisper** transcribes → **GPT-4o** fact-checks
2. **GPT-4o** cleans → **Claude** extracts → **Gemini** validates
3. **GPT-4o** summarizes → **Coffee service** adds tips/vibe
4. **Calendar** schedules → **ElevenLabs** confirms → **Snowflake** stores

Every step uses AI to improve accuracy and add value.

