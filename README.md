# EVE: The Everyday Virtual Executive

AI Productivity Companion for HackPrinceton 2025

## Setup Instructions

### 1. Get API Keys

You need API keys from:
- **OpenAI** (required): https://platform.openai.com/api-keys
- **Anthropic** (required): https://console.anthropic.com/
- **ElevenLabs** (required for voice): https://elevenlabs.io/
- **Google Cloud** (required for calendar): https://console.cloud.google.com/

Optional:
- **Amplitude**: https://amplitude.com/
- **Snowflake**: https://snowflake.com/

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use any text editor
```

**Replace these in `.env`:**
```
OPENAI_API_KEY=sk-proj-...  # Your actual OpenAI key
ANTHROPIC_API_KEY=sk-ant-...  # Your actual Anthropic key
ELEVENLABS_API_KEY=...  # Your actual ElevenLabs key
```

For Google Calendar (optional but recommended):
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Add credentials to `.env`

### 3. Install Backend Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:3000 in your browser.

## Usage

1. Click "Start Recording" to record audio
2. Or click the upload button to upload an audio file
3. EVE will automatically:
   - Transcribe the audio
   - Extract tasks and action items
   - Generate summaries
   - (Optional) Schedule to Google Calendar

## Features

- 🎙️ **Real-time Transcription** (OpenAI Whisper)
- 🧠 **Smart Task Extraction** (Claude 3.5 + GPT-4o)
- 📅 **Auto Calendar Scheduling** (Google Calendar API)
- 🗣️ **Voice Summaries** (ElevenLabs TTS)
- 📊 **Analytics Dashboard**
- 📚 **Study Materials Generator** (flashcards + quizzes)
- 💬 **Communication Analysis**

## Architecture

```
frontend/          # Next.js + React + Tailwind
  ├── app/        # Pages
  └── components/ # UI Components

backend/           # FastAPI
  ├── main.py     # API routes
  └── services/   # AI integrations
```

## API Endpoints

- `POST /transcribe/file` - Upload audio for transcription
- `POST /process/transcript` - Extract tasks and summaries
- `POST /calendar/schedule` - Create calendar events
- `POST /voice/summary` - Generate voice summary
- `POST /study/generate` - Generate study materials
- `WS /ws/realtime` - Real-time audio streaming

## Troubleshooting

**"API key not found"**
- Check that `.env` file exists in project root
- Verify API keys are correctly copied (no extra spaces)
- Restart the backend server after editing `.env`

**"Transcription failed"**
- Ensure OpenAI API key is valid
- Check you have API credits
- Verify audio file format is supported

**"TTS failed"**
- Ensure ElevenLabs API key is valid
- Voice generation is optional - tasks will still work

**"Calendar integration error"**
- Google Calendar requires OAuth setup
- For demo, you can skip this - tasks will still be extracted

## Demo Mode

If you don't have all API keys, you can still demo:
1. The UI will work fully
2. Upload pre-recorded audio files
3. Task extraction will work with OpenAI + Anthropic keys
4. Calendar + Voice features are optional

## Sponsor Integrations

✅ OpenAI (GPT-4o + Whisper)
✅ Anthropic (Claude 3.5)
✅ Google (Calendar API + Gemini option)
✅ ElevenLabs (TTS)
✅ MLH (Amplitude, Snowflake optional)
✅ Amazon Bedrock (optional)
✅ Photon (optional multi-agent)

## License

Built for HackPrinceton 2025

