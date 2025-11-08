# 🔑 How to Integrate API Keys in EVE

## The Only 3 Keys You Need

1. **OpenAI** → https://platform.openai.com/api-keys
2. **Anthropic** → https://console.anthropic.com/
3. **ElevenLabs** → https://elevenlabs.io/

---

## Step-by-Step: Adding Your Keys

### 1. Create `.env` file

In project root (`/Users/robertsun/Documents/hackprinceton2025/`):

```bash
cp env.example .env
```

### 2. Edit `.env` with your text editor

```bash
# Use any of these:
nano .env
code .env
vim .env
```

### 3. Replace these 3 lines with YOUR keys

```bash
OPENAI_API_KEY=sk-proj-PUT_YOUR_OPENAI_KEY_HERE
ANTHROPIC_API_KEY=sk-ant-PUT_YOUR_ANTHROPIC_KEY_HERE
ELEVENLABS_API_KEY=PUT_YOUR_ELEVENLABS_KEY_HERE
```

**Example with real key format:**
```bash
OPENAI_API_KEY=sk-proj-Ab3Cd4Ef5Gh6...
ANTHROPIC_API_KEY=sk-ant-xyz789abc123...
ELEVENLABS_API_KEY=a1b2c3d4e5f6...
```

### 4. Save the file

That's it!

---

## How Keys Are Loaded (Backend)

### 1. Backend starts (`backend/main.py`)

```python
from dotenv import load_dotenv
import os

# This line loads your .env file
load_dotenv()

# Now your keys are available:
openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
```

### 2. Services are initialized with keys

```python
# backend/main.py (lines 20-35)

transcription_service = TranscriptionService(
    api_key=os.getenv("OPENAI_API_KEY")  # ← Your OpenAI key
)

reasoning_service = ReasoningService(
    openai_key=os.getenv("OPENAI_API_KEY"),      # ← OpenAI key
    anthropic_key=os.getenv("ANTHROPIC_API_KEY")  # ← Anthropic key
)

tts_service = TTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY")  # ← ElevenLabs key
)
```

### 3. Services use keys to call APIs

**Example: OpenAI Whisper (transcription)**

```python
# backend/services/transcription.py (lines 4-7)

class TranscriptionService:
    def __init__(self, api_key: str):
        # Initialize OpenAI client with your key
        self.client = openai.OpenAI(api_key=api_key)
```

```python
# backend/services/transcription.py (lines 10-18)

async def transcribe_file(self, audio_data: bytes, filename: str):
    audio_file = io.BytesIO(audio_data)
    audio_file.name = filename
    
    # Call OpenAI API with your key
    transcript = self.client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )
    
    return transcript
```

**Example: Anthropic Claude (task extraction)**

```python
# backend/services/reasoning.py (lines 7-9)

class ReasoningService:
    def __init__(self, openai_key: str, anthropic_key: str):
        self.openai_client = openai.OpenAI(api_key=openai_key)
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
```

```python
# backend/services/reasoning.py (lines 52-60)

async def extract_tasks(self, sections: List[Dict]):
    # Call Anthropic API with your key
    message = self.anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1500,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(message.content[0].text)
```

**Example: ElevenLabs (text-to-speech)**

```python
# backend/services/tts.py (lines 5-8)

class TTSService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
```

```python
# backend/services/tts.py (lines 18-28)

async def text_to_speech(self, text: str):
    url = f"{self.base_url}/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": self.api_key  # ← Your ElevenLabs key
    }
    
    # Call ElevenLabs API
    response = await client.post(url, json=data, headers=headers)
    return response.content
```

---

## Key Flow Diagram

```
.env file
    │
    │ OPENAI_API_KEY=sk-proj-...
    │ ANTHROPIC_API_KEY=sk-ant-...
    │ ELEVENLABS_API_KEY=...
    │
    ▼
load_dotenv() in backend/main.py
    │
    ├─► os.getenv("OPENAI_API_KEY")
    ├─► os.getenv("ANTHROPIC_API_KEY")
    └─► os.getenv("ELEVENLABS_API_KEY")
    │
    ▼
Initialize services with keys
    │
    ├─► TranscriptionService(openai_key)
    ├─► ReasoningService(openai_key, anthropic_key)
    └─► TTSService(elevenlabs_key)
    │
    ▼
Services call external APIs
    │
    ├─► openai.OpenAI(api_key=key)
    ├─► anthropic.Anthropic(api_key=key)
    └─► requests with {"xi-api-key": key}
```

---

## Testing Your Keys

### Quick Test

```bash
./test-api-keys.sh
```

Expected output:
```
✅ OPENAI_API_KEY configured
✅ ANTHROPIC_API_KEY configured
✅ ELEVENLABS_API_KEY configured
```

### Manual Test (Python)

```bash
cd backend
source venv/bin/activate
python
```

```python
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
True
>>> os.getenv("OPENAI_API_KEY")[:10]
'sk-proj-Ab'  # Should show first 10 chars of your key
>>> os.getenv("ANTHROPIC_API_KEY")[:8]
'sk-ant-x'  # Should show first 8 chars
>>> bool(os.getenv("ELEVENLABS_API_KEY"))
True  # Should be True
```

### Test API Calls

```bash
cd backend
python main.py
```

Then visit: http://localhost:8000/docs

Try the `/transcribe/file` endpoint with a test audio file.

---

## Where Keys Are Used (Complete Reference)

### OpenAI API Key

Used in 2 files:

1. **`backend/services/transcription.py`**
   - Line 6: `self.client = openai.OpenAI(api_key=api_key)`
   - Purpose: Audio transcription with Whisper

2. **`backend/services/reasoning.py`**
   - Line 8: `self.openai_client = openai.OpenAI(api_key=openai_key)`
   - Lines 17-26: Transcript cleaning
   - Lines 97-107: Event suggestions
   - Lines 119-129: Clarification questions
   - Lines 142-152: Summary generation
   - Lines 165-175: Voice summary text
   - Lines 188-198: Study materials
   - Lines 211-221: Sentiment analysis

### Anthropic API Key

Used in 1 file:

1. **`backend/services/reasoning.py`**
   - Line 9: `self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)`
   - Lines 52-74: Task extraction (primary use)

### ElevenLabs API Key

Used in 1 file:

1. **`backend/services/tts.py`**
   - Line 7: `self.api_key = api_key`
   - Line 26: `"xi-api-key": self.api_key`
   - Purpose: Text-to-speech voice generation

---

## Common Issues & Fixes

### ❌ "API key not found"

**Problem:** Keys not loaded from `.env`

**Fix:**
```bash
# Check .env exists in project root
ls -la .env

# If not, create it:
cp env.example .env

# Edit with your keys:
nano .env
```

### ❌ "Invalid API key"

**Problem:** Wrong key or typo

**Fix:**
- OpenAI keys start with `sk-proj-` (new format) or `sk-` (old)
- Anthropic keys start with `sk-ant-`
- Double-check you copied the full key (no spaces)
- Regenerate key if needed

### ❌ "Module 'openai' has no attribute..."

**Problem:** Wrong openai package version

**Fix:**
```bash
cd backend
source venv/bin/activate
pip install --upgrade openai anthropic
```

### ❌ Keys loaded but API calls fail

**Problem:** Network, credits, or rate limits

**Fix:**
- Check internet connection
- Verify account has credits
- Check API status pages
- Wait 60 seconds if rate limited

---

## Security Best Practices

✅ **DO:**
- Keep `.env` in `.gitignore` (already done)
- Never commit `.env` to git
- Rotate keys if exposed
- Use separate keys for dev/prod

❌ **DON'T:**
- Share your `.env` file
- Commit keys to GitHub
- Use production keys for testing
- Hardcode keys in source files

---

## Adding More API Keys (Optional)

### Google Calendar

1. Get OAuth credentials from https://console.cloud.google.com/
2. Add to `.env`:
```bash
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret_here
```

3. Used in `backend/services/calendar_service.py`

### Amplitude (Analytics)

1. Get API key from https://amplitude.com/
2. Add to `.env`:
```bash
AMPLITUDE_API_KEY=your_amplitude_key
```

3. Used in `backend/services/analytics.py`

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│                  EVE API Keys Quick Ref                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  File: .env (project root)                              │
│                                                         │
│  Required Keys:                                         │
│  ✓ OPENAI_API_KEY=sk-proj-...                          │
│  ✓ ANTHROPIC_API_KEY=sk-ant-...                        │
│  ✓ ELEVENLABS_API_KEY=...                              │
│                                                         │
│  Get Keys:                                              │
│  • OpenAI: platform.openai.com/api-keys                 │
│  • Anthropic: console.anthropic.com                     │
│  • ElevenLabs: elevenlabs.io                            │
│                                                         │
│  Test Keys:                                             │
│  $ ./test-api-keys.sh                                   │
│                                                         │
│  Start EVE:                                             │
│  $ ./start.sh                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Summary

1. **Create `.env`**: `cp env.example .env`
2. **Add 3 keys**: OpenAI, Anthropic, ElevenLabs
3. **Test**: `./test-api-keys.sh`
4. **Run**: `./start.sh`

That's all you need! 🚀

---

For detailed setup: See `SETUP.md`
For demo script: See `DEMO_SCRIPT.md`
For architecture: See `ARCHITECTURE.md`

