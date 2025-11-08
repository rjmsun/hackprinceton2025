# EVE: The Everyday Virtual Executive

**AI Productivity Companion that listens, understands, and acts autonomously.**

EVE transforms conversations (coffee chats, lectures, meetings) into organized, actionable information. It uses multiple AI models working together to provide accurate, validated, and actionable results.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** installed
- **Node.js 18+** and npm installed
- API keys (see below)

### Step 1: Get API Keys

**Required:**
- **OpenAI**: https://platform.openai.com/api-keys (for Whisper transcription + GPT-4o)
- **ElevenLabs**: https://elevenlabs.io/ (for voice summaries)

**Optional (but recommended):**
- **Google Calendar**: https://console.cloud.google.com/ (for auto-scheduling)
- **Gemini**: https://aistudio.google.com/apikey (for cross-validation)

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your API keys
nano .env  # or use any text editor
```

**Minimum required in `.env`:**
```bash
OPENAI_API_KEY=sk-proj-your_key_here
ELEVENLABS_API_KEY=your_key_here
GEMINI_API_KEY=your_gemini_key_here
```

**For Google Calendar (optional):**
```bash
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
```

See `GOOGLE_CALENDAR_SETUP.md` for detailed OAuth setup instructions.

### Step 3: Install Dependencies

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Step 4: Run the Application

**⚠️ IMPORTANT: Run backend FIRST, then frontend**

**Terminal 1 - Start Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Verify backend is running:**
```bash
curl http://localhost:8000/
# Should return: {"status":"EVE API running","version":"1.0.0"}
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

You should see:
```
  ▲ Next.js 14.0.3
  - Local:        http://localhost:3000
  ✓ Ready in 2.3s
```

**Open your browser:**
👉 **http://localhost:3000**

**To stop the services:**
- Press `Ctrl+C` in each terminal
- Or kill processes: `lsof -ti:8000 | xargs kill -9` and `lsof -ti:3000 | xargs kill -9`

---

## 📖 How to Use

### 1. Record or Upload Audio

- **Click "Start Recording"** to record live audio from your microphone
- **Click the Upload button** to upload an audio file (supports large files)
- Supported formats: `mp3`, `wav`, `webm`, `m4a`, `ogg`, `flac`, `mp4`, `mpeg`, `mpga`, `oga`

### 2. Automatic Processing

EVE automatically:
1. **Transcribes** audio using OpenAI Whisper
2. **Fact-checks** transcript using GPT-4o (fixes errors, corrects technical terms)
3. **Extracts tasks** using GPT-4o
4. **Generates summaries** using GPT-4o
5. **Cross-validates** with Gemini 2.5 Flash (alternative summaries)

### 3. Review Results

- **Live Transcript**: See the fact-checked transcript
- **Summary**: Short and detailed summaries
- **Tasks**: Extracted action items with due dates, owners, priorities

### 4. Add to Google Calendar

**First time:**
1. Click **"Connect Google Calendar"** button
2. Authorize EVE to access your calendar
3. You'll be redirected back to the app

**Then:**
- Click **"Add to Google Calendar"** on individual tasks with due dates
- Or select multiple tasks and click **"Schedule Selected"**

---

## ✨ Features

### Core Features

- 🎙️ **Real-time Transcription** (OpenAI Whisper)
  - Supports large audio files
  - Multiple audio formats
  - High accuracy

- ✅ **Fact-Checking** (GPT-4o)
  - Validates and corrects transcripts
  - Fixes transcription errors
  - Corrects technical terms (e.g., "CS214" not "see 214")

- 🧠 **Smart Task Extraction** (GPT-4o)
  - Extracts actionable items
  - Identifies due dates and owners
  - Assigns priorities (high/medium/low)
  - Confidence scoring

- 📝 **Intelligent Summaries** (GPT-4o)
  - Short 1-sentence summary
  - Detailed bullet-point summary
  - Covers decisions, tasks, and risks

- 🔍 **Cross-Validation** (Google Gemini)
  - Provides second opinion on extracted data
  - Additional insights and validation

- 📅 **Auto Calendar Scheduling** (Google Calendar)
  - One-click calendar integration
  - Auto-creates events from tasks
  - Supports individual or bulk scheduling

- 🗣️ **Voice Summaries** (ElevenLabs TTS)
  - Spoken confirmation of actions
  - Natural voice feedback

### Advanced Features

- 📊 **Analytics Dashboard** (Amplitude)
  - Track sessions and productivity
  - Usage statistics

- 💾 **History Storage** (Snowflake)
  - Store conversation history
  - Retrieve past sessions

- 📚 **Study Materials** (GPT-4o)
  - Generate flashcards
  - Create quizzes from transcripts

- 💬 **Communication Analysis**
  - Sentiment analysis
  - Interruption detection
  - Speaking time metrics

---

## 🏗️ Architecture

```
EVE/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   └── services/         # AI service integrations
│       ├── transcription.py    # Whisper + GPT-4o fact-check
│       ├── reasoning.py         # GPT-4o task extraction & summaries
│       ├── coffee_chat.py       # Tips, vibe scoring, coaching
│       ├── gemini_service.py   # Cross-validation
│       ├── tts.py              # ElevenLabs TTS
│       ├── calendar_service.py # Google Calendar OAuth
│       └── snowflake_service.py # Storage
│
├── frontend/             # Next.js frontend
│   ├── app/             # Pages and routing
│   │   ├── page.tsx     # Main dashboard
│   │   └── auth/        # OAuth callbacks
│   └── components/      # React components
│       ├── RecordingPanel.tsx
│       ├── TasksPanel.tsx
│       ├── SummaryPanel.tsx
│       └── Dashboard.tsx
│
└── .env                 # Your API keys (create this)
```

---

## 🔌 API Endpoints

### Main Processing
- `POST /transcribe/file` - Upload audio, get fact-checked transcript
- `POST /process/transcript` - Full pipeline: validate → clean → extract → summarize
- `POST /coffee/process` - Coffee chat mode with tips, vibe scoring

### Actions
- `GET /calendar/auth` - Get Google OAuth URL
- `GET /calendar/callback` - OAuth callback handler
- `POST /calendar/schedule` - Create calendar events from tasks
- `POST /voice/summary` - Generate spoken summary
- `POST /followup/draft` - Draft follow-up email

### Storage & Analytics
- `POST /snowflake/store` - Save session to Snowflake
- `GET /snowflake/conversations/{user_id}` - Get conversation history

**API Documentation:** http://localhost:8000/docs

---

## 🔧 Troubleshooting

### Backend Issues

**"Module not found" or import errors:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**"Port 8000 already in use":**
```bash
lsof -ti:8000 | xargs kill -9  # macOS/Linux
# Or change port in main.py
```

**"API key not found":**
- Check that `.env` exists in project root (not in `backend/`)
- Verify keys are correctly copied (no extra spaces)
- Restart backend after editing `.env`

### Frontend Issues

**"Cannot find module" or npm errors:**
```bash
cd frontend
rm -rf node_modules
npm install
```

**"Port 3000 already in use":**
```bash
lsof -ti:3000 | xargs kill -9  # macOS/Linux
# Or change port: npm run dev -- -p 3001
```

**Buttons not working:**
- Check browser console (F12) for errors
- Verify backend is running on http://localhost:8000
- Check CORS settings if accessing from different origin

### API Issues

**"Transcription failed":**
- Ensure OpenAI API key is valid
- Check you have API credits
- Verify audio file format is supported
- For large files, wait longer (processing may take time)

**"No tasks extracted":**
- Check OpenAI API key is set
- Verify transcript has actionable content
- Ensure GPT-4o has sufficient credits

**"Summary not generated":**
- Check OpenAI API key
- Verify transcript was successfully processed
- Check browser console for API errors

**"Calendar integration error":**
- Ensure Google OAuth credentials are set in `.env`
- Check redirect URI matches Google Cloud Console
- See `GOOGLE_CALENDAR_SETUP.md` for detailed setup

**"TTS failed":**
- ElevenLabs API key is optional
- Voice generation will fail gracefully
- Tasks and summaries will still work

### General Issues

**Backend won't start:**
```bash
cd backend
source venv/bin/activate
python -c "import fastapi; print('FastAPI installed')"  # Test import
python main.py  # Check for error messages
```

**Frontend won't compile:**
```bash
cd frontend
rm -rf .next  # Clear Next.js cache
npm run dev
```

**Services not connecting:**
- Verify backend is running: `curl http://localhost:8000/`
- Verify frontend is running: `curl http://localhost:3000`
- Check `.env` file location (should be in project root)

---

## 🎯 Current Capabilities

### What Works Now

✅ **Audio Transcription** - OpenAI Whisper with fact-checking  
✅ **Task Extraction** - GPT-4o  
✅ **Summary Generation** - GPT-4o + Gemini 2.5 Flash (dual summaries)  
✅ **Google Calendar** - Full OAuth integration, one-click scheduling  
✅ **Large File Support** - Handles big audio files efficiently  
✅ **Voice Summaries** - ElevenLabs TTS integration  
✅ **Cross-Validation** - Gemini insights (optional)  
✅ **Error Handling** - Graceful fallbacks for missing APIs  

### Demo Mode

If you don't have all API keys, EVE works in demo mode:
- UI functions fully
- Shows placeholder messages for missing APIs
- You can still test the flow
- Transcription requires OpenAI key
- Task extraction requires OpenAI API key

---

## 📚 Documentation

- `START_HERE.md` - Quick setup guide
- `HOW_IT_WORKS.md` - Complete pipeline explanation
- `PROJECT_OVERVIEW.md` - System architecture
- `GOOGLE_CALENDAR_SETUP.md` - Calendar OAuth setup
- `SNOWFLAKE_SETUP.md` - Snowflake storage setup
- `COMPLETE_PIPELINE.md` - API usage breakdown
- `DEMO_SCRIPT.md` - Demo presentation guide

---

## 🏆 Sponsor Integrations

✅ **OpenAI** - Whisper (transcription) + GPT-4o (fact-checking, summaries, task extraction)  
✅ **Google** - Calendar API (scheduling) + Gemini 2.5 Flash (alternative summaries)  
✅ **ElevenLabs** - TTS (voice feedback)  
✅ **MLH** - Snowflake (storage) + Amplitude (analytics)  

---

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

**Backend:**
- FastAPI
- Python 3.9+
- OpenAI SDK
- Google APIs

**AI Services:**
- OpenAI (Whisper, GPT-4o)
- Google (Gemini 2.5 Flash, Calendar)
- ElevenLabs (TTS)
- Snowflake (Storage)

---

## 📝 Example Workflow

1. **Record a meeting:**
   - Click "Start Recording"
   - Speak or have a conversation
   - Click "Stop Recording"

2. **EVE processes:**
   - Transcribes audio
   - Fact-checks transcript
   - Extracts tasks with dates
   - Generates summary

3. **Take action:**
   - Review extracted tasks
   - Click "Connect Google Calendar" (first time)
   - Click "Add to Google Calendar" on tasks
   - Listen to voice summary

4. **Result:**
   - Tasks added to your calendar
   - Summary saved
   - Voice confirmation played

---

## 🐛 Known Issues

- Large files (>100MB) may take longer to process
- Google Calendar requires OAuth setup (see `GOOGLE_CALENDAR_SETUP.md`)
- Some audio formats may not be supported (check Whisper docs)

---

## 📄 License

Built for HackPrinceton 2025

---

## 💡 Tips

- **For best results:** Use clear audio, minimize background noise
- **For large files:** Be patient, processing may take 1-2 minutes
- **For calendar:** Set up OAuth once, then it works seamlessly
- **For demos:** Have pre-recorded audio files ready as backup

---

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review `HOW_IT_WORKS.md` for pipeline details
3. Check browser console (F12) for frontend errors
4. Check backend terminal for API errors
5. Verify all API keys are set in `.env`

---

**Ready to use EVE? Follow the Quick Start guide above! 🚀**
