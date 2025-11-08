# 🎯 START HERE - EVE Setup

## What You Need (3 things)

1. **OpenAI API Key** → https://platform.openai.com/api-keys
2. **Anthropic API Key** → https://console.anthropic.com/
3. **ElevenLabs API Key** → https://elevenlabs.io/

All have FREE tiers - no credit card required for hackathon demo!

---

## Setup (3 steps)

### 1. Copy the env file

```bash
cp env.example .env
```

### 2. Edit `.env` and paste your keys

Open `.env` in any text editor and replace these 3 lines:

```bash
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
ELEVENLABS_API_KEY=YOUR_KEY_HERE
```

**That's it!** Save the file.

### 3. Run EVE

```bash
./start.sh
```

Or manually:

**Terminal 1:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Terminal 2:**
```bash
cd frontend
npm install
npm run dev
```

Open: **http://localhost:3000**

---

## How the APIs Are Used

### OpenAI (`backend/services/transcription.py` + `reasoning.py`)
```python
# In transcription.py:
self.client = openai.OpenAI(api_key=api_key)
transcript = self.client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file
)

# In reasoning.py:
response = self.openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "system", "content": "..."}]
)
```

**What it does:** Transcribes audio + extracts tasks

---

### Anthropic (`backend/services/reasoning.py`)
```python
self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

message = self.anthropic_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": prompt}]
)
```

**What it does:** Deep reasoning on transcripts, structured task extraction

---

### ElevenLabs (`backend/services/tts.py`)
```python
headers = {"xi-api-key": self.api_key}
response = await client.post(
    f"{self.base_url}/text-to-speech/{voice}",
    json={"text": text},
    headers=headers
)
```

**What it does:** Text-to-speech for voice summaries

---

### Google Calendar (Optional - `backend/services/calendar_service.py`)
```python
credentials = Credentials(token=access_token)
service = build('calendar', 'v3', credentials=credentials)
service.events().insert(calendarId='primary', body=event).execute()
```

**What it does:** Creates calendar events automatically

---

## API Key Loading Flow

1. **`.env` file** in project root:
   ```
   OPENAI_API_KEY=sk-proj-abc123
   ANTHROPIC_API_KEY=sk-ant-xyz789
   ELEVENLABS_API_KEY=def456
   ```

2. **Backend loads** with `python-dotenv`:
   ```python
   # backend/main.py
   from dotenv import load_dotenv
   load_dotenv()  # Loads .env into os.environ
   
   transcription_service = TranscriptionService(
       api_key=os.getenv("OPENAI_API_KEY")
   )
   ```

3. **Services use keys** to initialize API clients:
   ```python
   self.client = openai.OpenAI(api_key=api_key)
   self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
   ```

---

## Verify Keys Work

```bash
./test-api-keys.sh
```

Should output:
```
✅ OPENAI_API_KEY configured
✅ ANTHROPIC_API_KEY configured
✅ ELEVENLABS_API_KEY configured
```

---

## Test the APIs

### Test OpenAI (Transcription)
1. Start backend: `cd backend && python main.py`
2. Upload an audio file at http://localhost:8000/docs
3. Try `/transcribe/file` endpoint

### Test Anthropic (Task Extraction)
1. Backend running
2. Go to http://localhost:8000/docs
3. Try `/process/transcript` with sample text

### Test ElevenLabs (Voice)
1. Backend running
2. Try `/voice/summary` endpoint
3. Should return audio file

---

## Code Structure - Where Keys Are Used

```
backend/
├── main.py                    # Loads .env, initializes services
├── services/
│   ├── transcription.py      # Uses OPENAI_API_KEY
│   ├── reasoning.py          # Uses OPENAI_API_KEY + ANTHROPIC_API_KEY
│   ├── tts.py               # Uses ELEVENLABS_API_KEY
│   ├── calendar_service.py  # Uses GOOGLE_CLIENT_ID + SECRET
│   └── analytics.py         # Uses AMPLITUDE_API_KEY (optional)
```

All services receive keys via constructor:
```python
# main.py
transcription_service = TranscriptionService(
    api_key=os.getenv("OPENAI_API_KEY")
)

reasoning_service = ReasoningService(
    openai_key=os.getenv("OPENAI_API_KEY"),
    anthropic_key=os.getenv("ANTHROPIC_API_KEY")
)

tts_service = TTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)
```

---

## Troubleshooting

**"API key not found"**
- Check `.env` is in project root (not backend/ or frontend/)
- Verify you edited `.env` (not `env.example`)
- Restart backend after editing `.env`

**"Invalid API key"**
- Double-check you copied the full key
- OpenAI keys start with `sk-proj-`
- Anthropic keys start with `sk-ant-`

**"Rate limit exceeded"**
- Free tier limits hit
- Wait 60 seconds or add credits

---

## Adding New API Keys (if you want)

1. Add to `env.example`:
   ```
   NEW_API_KEY=your_key_here
   ```

2. Load in `backend/main.py`:
   ```python
   new_service = NewService(
       api_key=os.getenv("NEW_API_KEY")
   )
   ```

3. Use in service:
   ```python
   # backend/services/new_service.py
   class NewService:
       def __init__(self, api_key: str):
           self.api_key = api_key
   ```

---

## Quick Reference

| API | Used For | Cost (Free Tier) |
|-----|----------|------------------|
| OpenAI Whisper | Audio transcription | $5 credit |
| OpenAI GPT-4o | Task extraction | $5 credit |
| Anthropic Claude | Deep reasoning | $5 credit |
| ElevenLabs | Voice synthesis | 10K chars free |
| Google Calendar | Auto-scheduling | Free forever |

---

**That's it!** Get your 3 keys, put them in `.env`, run `./start.sh` 🚀

Questions? Check:
- `API_KEYS_GUIDE.md` - Detailed key setup
- `SETUP.md` - Full setup instructions
- `DEMO_SCRIPT.md` - How to demo for judges
- `README.md` - Complete documentation

