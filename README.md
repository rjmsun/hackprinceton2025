# EVE: The Everyday Virtual Executive

**AI Productivity Companion that listens, understands, and acts autonomously.**

EVE transforms conversations (meetings, lectures, interviews, coffee chats) into organized, actionable information. Record or upload audio/video, and EVE will transcribe, extract tasks, generate summaries, and optionally add events to your Google Calendar.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** installed
- **Node.js 18+** and npm installed
- **FFmpeg** installed (required for video processing)
  - macOS: `brew install ffmpeg`
  - Linux: `apt install ffmpeg`
- API keys (see below)

### Step 1: Get API Keys

**Required:**
- **OpenAI**: https://platform.openai.com/api-keys (for Whisper transcription, GPT-4o processing, and GPT-4o Vision)

**Highly Recommended (core features):**
- **Google Calendar**: https://console.cloud.google.com/ (for auto-scheduling tasks to your calendar)
- **Gemini**: https://aistudio.google.com/apikey (for cross-validation and enhanced analysis)
- **ElevenLabs**: https://elevenlabs.io/ (for AI voice summaries)

**Optional (advanced features):**
- **AWS Bedrock**: https://aws.amazon.com/bedrock/ (for Claude-powered vibe analysis during video processing)

### Step 2: Configure Environment

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=sk-proj-your_openai_key_here

# Highly recommended (core features will use these)
GEMINI_API_KEY=your_gemini_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
FRONTEND_URL=http://localhost:3000

# Optional (advanced features)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

**For Google Calendar OAuth setup:**
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Web application)
5. Add authorized redirect URI: `http://localhost:8000/calendar/callback`
6. Add your email as a test user in OAuth consent screen

### Step 3: Install Dependencies

**System Dependencies:**
```bash
# Install FFmpeg (required for video processing)
brew install ffmpeg  # macOS
# or
sudo apt install ffmpeg  # Linux
```

**Backend:**
```bash
cd backend
python3 -m pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install --legacy-peer-deps
```

> Note: You may see some dependency warnings - these can be safely ignored for development.

### Step 4: Run the Application

**⚠️ Run backend FIRST, then frontend in separate terminals**

**Terminal 1 - Backend:**
```bash
cd backend
python3 main.py
```

Should see: `INFO:     Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Should see: `- Local:        http://localhost:3000`

**Open browser:**
👉 **http://localhost:3000**

**To stop:**
- Press `Ctrl+C` in each terminal

---

## 📖 How to Use

### 1. Choose Your Mode

**Media Type:**
- **Audio Only**: mp3, webm, wav, m4a, ogg, flac files
- **Video + Audio**: mp4 files with advanced visual analysis
  - GPT-4o Vision analyzes video frames
  - Extracts text from slides/presentations (OCR)
  - Detects key moments and scene changes
  - Identifies objects, people, and visual context

**Context Type:**
- **General Meeting**: Standard meeting notes and action items
- **Interview Practice**: Get coaching, feedback, and vibe analysis
- **Coffee Chat**: Networking tips with AI-powered social dynamics analysis
- **Lecture/Study**: Generate study materials, flashcards, and summaries

### 2. Record or Upload

- **Click "Start Recording"** for live audio/video
- **Upload file** button for existing files
- Supports: `mp3`, `wav`, `webm`, `mp4`, `m4a`, `ogg`, `flac`

### 3. Generate Smart Analysis

Click **"Generate Smart Analysis & Tasks"** to:
1. **Transcribe** audio with OpenAI Whisper (industry-leading accuracy)
2. **Validate** transcript with GPT-4o (fact-checking and error correction)
3. **Extract tasks** with GPT-4o (dates, priorities, owners)
4. **Generate summaries** with GPT-4o (context-aware)
5. **Cross-validate** with Gemini (additional insights)
6. **Analyze video frames** if video upload (GPT-4o Vision + Gemini)
   - Scene-by-scene visual analysis
   - OCR text extraction from slides
   - Key moment detection
   - Visual context aggregation
7. **Social dynamics analysis** with Claude 3 Haiku (AWS Bedrock) for interviews/networking

### 4. Review & Act

- **Transcript**: Validated, fact-checked text
- **Summary**: Key points and decisions
- **Tasks**: Action items with due dates, priorities, owners
- **Coaching**: Context-specific insights and tips

### 5. Google Calendar Integration (Optional)

1. Click **"Connect Google Calendar"** in Tasks panel
2. Authorize EVE to access your calendar
3. Select tasks with due dates
4. Click **"Schedule Selected"** to add to calendar

---

## ✨ Features

### Core Capabilities

- 🎙️ **Multi-Format Transcription** (OpenAI Whisper)
  - Audio: mp3, wav, webm, m4a, ogg, flac
  - Video: mp4 with visual analysis
  - Large file support (streaming)

- 👁️ **Advanced Video Analysis** (GPT-4o Vision + Gemini Vision)
  - **Frame extraction** with FFmpeg (smart keyframe selection)
  - **Scene-by-scene analysis** with GPT-4o Vision
  - **OCR text extraction** from slides, whiteboards, presentations
  - **Object and person detection** with confidence scores
  - **Key moment identification** with timestamps
  - **Visual context aggregation** across entire video
  - **Dual-model validation** (OpenAI + Google Gemini)
  - **Supports both fast and detailed analysis modes**

- ✅ **Intelligent Validation** (GPT-4o)
  - Fact-checks transcripts
  - Corrects transcription errors
  - Fixes technical terms

- 🧠 **Smart Task Extraction** (GPT-4o)
  - Actionable items with context
  - Due dates and owners
  - Priority levels
  - Confidence scoring

- 📝 **Contextual Summaries** (GPT-4o)
  - Adapts to meeting type
  - Key decisions and action items
  - Interview feedback and tips
  - Study notes and flashcards

- 🔍 **Cross-Validation** (Google Gemini)
  - Second opinion on analysis
  - Additional insights
  - Validation of extracted data

- 📅 **Calendar Integration** (Google Calendar)
  - OAuth 2.0 authentication
  - One-click event creation
  - Bulk task scheduling

- 🎭 **Context-Aware Modes**
  - **Interview**: Coaching, performance tips, and vibe analysis
  - **Coffee Chat**: Networking insights with social dynamics scoring
  - **Lecture**: Study materials, flashcards, and quiz generation
  - **General**: Standard meeting notes and action items

- 🤖 **AI-Powered Vibe Analysis** (AWS Bedrock - Claude 3 Haiku)
  - Analyzes social dynamics in interviews and networking
  - Categorizes engagement levels: Engaged, Neutral, Disinterested
  - Provides evidence-based insights with transcript quotes
  - Fast inference with Claude 3 Haiku model
  - Graceful degradation if AWS not configured

### UI Features

- 🌓 **Dark Mode**: Toggle between light and dark themes
- 📊 **Analytics Dashboard**: Session tracking and statistics
- 🎯 **Task Management**: Checkbox tracking and calendar sync
- 💬 **AI Practice Mode**: Conversational coaching (context-dependent)

---

## 🏗️ Architecture

### Tech Stack

**Backend (Python):**
- FastAPI - Modern async web framework with CORS
- OpenAI API - Whisper transcription, GPT-4o reasoning, GPT-4o Vision for video
- Google APIs - Calendar OAuth integration, Gemini 2.0 Flash for cross-validation
- ElevenLabs - Text-to-speech for AI voice summaries
- AWS Bedrock - Claude 3 Haiku for social dynamics analysis (optional)
- FFmpeg - Video/audio processing, frame extraction, format conversion
- Boto3 - AWS SDK for Bedrock integration

**Frontend (TypeScript):**
- Next.js 14 - React framework with App Router
- React 18 - Component library
- Tailwind CSS - Utility-first styling with dark mode support
- next-themes - Dark/light theme management
- Lucide React - Beautiful icon library
- Axios - HTTP client for API calls
- Recharts - Analytics dashboard visualizations

### Project Structure

```
EVE/
├── backend/
│   ├── main.py                 # API endpoints & routing
│   ├── requirements.txt        # Python dependencies
│   └── services/
│       ├── transcription.py    # Whisper + validation
│       ├── reasoning.py        # Task extraction & summaries
│       ├── gemini_service.py   # Gemini cross-validation
│       ├── calendar_service.py # Google Calendar OAuth
│       ├── tts.py              # ElevenLabs voice summaries
│       ├── vibe_service.py     # AWS Bedrock Claude vibe analysis
│       ├── video_service.py    # FFmpeg video processing
│       ├── vision_analyzers.py # GPT-4o Vision + Gemini Vision
│       ├── coaching_service.py # Context-aware coaching
│       └── interactive_coaching_service.py # AI practice mode
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Main dashboard
│   │   ├── layout.tsx          # Theme provider
│   │   ├── globals.css         # Global styles
│   │   └── auth/success/       # OAuth success page
│   ├── components/
│   │   ├── RecordingPanel.tsx      # Audio/video recording UI
│   │   ├── TasksPanel.tsx          # Task list with calendar integration
│   │   ├── SummaryPanel.tsx        # Dual summaries (OpenAI + Gemini)
│   │   ├── Dashboard.tsx           # Analytics with dark mode support
│   │   ├── CoachingPanel.tsx       # Context-aware insights
│   │   ├── AIPracticePanel.tsx     # Interactive coaching chat
│   │   └── VideoAnalysisPanel.tsx  # Visual analysis results
│   ├── package.json
│   └── tailwind.config.js
│
└── .env                        # API keys (create this)
```

---

## 🔌 API Endpoints

### Main Processing
- `POST /transcribe/file` - Upload audio/video, get transcript + video analysis
  - Query params: 
    - `validate=true` - Enable GPT-4o fact-checking
    - `media_type=video` - Enable video frame analysis
    - `vision_mode=fast|detailed` - Analysis depth
  - Supports: mp3, wav, webm, m4a, ogg, flac, mp4
  - Returns: transcript, video_analysis (if video), frame_results
  
- `POST /process/transcript` - Full AI analysis pipeline
  - Body: `{text, user_id, timezone, context, media_type}`
  - Context: "general", "interview", "coffee_chat", "lecture"
  - Returns: tasks, summary (OpenAI + Gemini), coaching, vibe_analysis
  - Runs multiple AI models in parallel for speed

### Google Calendar
- `GET /calendar/auth` - Get OAuth authorization URL
- `GET /calendar/callback` - OAuth callback (redirects to frontend)
- `POST /calendar/schedule` - Create calendar events
  - Body: `{tasks: [], access_token: string}`

### Video & Vision
- `POST /video/analyze` - Analyze video frames with GPT-4o Vision
  - Body: `{video_path, mode: "fast"|"detailed"}`
  - Returns: scene descriptions, OCR text, key moments, aggregated insights
  
### AI Features
- `POST /voice/summary` - Generate TTS summary (ElevenLabs)
- `POST /study/generate` - Create flashcards/quiz for lectures
- `POST /analyze/sentiment` - Communication analysis
- `POST /coaching/insights` - Context-aware coaching tips
- `POST /coaching/interactive` - AI practice conversation
- `POST /gemini/insights` - Gemini cross-validation
- `POST /gemini/summary` - Gemini-powered summary

**API Documentation:** http://localhost:8000/docs (when backend is running)

---

## � Current Implementation

This version of EVE is a **simplified, single-user setup** designed for local development. Some features from the original design have been streamlined:

### ✅ Fully Functional
- **Audio/video transcription** with Whisper + GPT-4o validation
- **Advanced video analysis** with frame extraction and vision AI
- **Task extraction** with dates, priorities, and confidence scores
- **Google Calendar integration** with OAuth 2.0 and bulk scheduling
- **Multiple context modes** (interview, coffee chat, lecture, general)
- **Social dynamics analysis** with AWS Bedrock Claude 3 Haiku
- **Dark mode UI** with theme toggle and localStorage persistence
- **Cross-validation** with OpenAI GPT-4o + Google Gemini
- **Voice summaries** with ElevenLabs TTS
- **AI coaching** with interactive practice mode

### 🎯 Perfect For
- Personal productivity tracking
- Meeting note-taking
- Interview practice
- Lecture transcription
- Local development and testing

---

## �🔧 Troubleshooting

### Backend Issues

**Import errors:**
```bash
cd backend
python3 -m pip install -r requirements.txt
```

**Port 8000 in use:**
```bash
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

**API key errors:**
- Ensure `.env` is in project root
- No extra spaces in key values
- Restart backend after editing `.env`

### Frontend Issues

**Module not found:**
```bash
cd frontend
npm install
```

**Port 3000 in use:**
```bash
lsof -ti:3000 | xargs kill -9  # macOS/Linux
```

**Theme not working:**
- Clear browser cache
- Check that `next-themes` is installed

**Google Calendar not connecting:**
1. Verify redirect URI in Google Cloud Console: `http://localhost:8000/calendar/callback`
2. Add your email as a test user in OAuth consent screen
3. Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are in `.env`

### Common Issues

**"CORS error" in browser console:**
- Ensure backend is running
- Check backend CORS settings allow `http://localhost:3000`

**Tasks not extracting:**
- Verify `OPENAI_API_KEY` is set
- Check API key has sufficient credits
- Make sure you're using a valid OpenAI model (GPT-4o)

**Video analysis not working:**
- **Install FFmpeg first**: `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux)
- Verify FFmpeg is installed: `ffmpeg -version`
- Ensure you selected "Video + Audio" mode in UI
- Upload an mp4 file (other formats may not work for video)
- Verify `OPENAI_API_KEY` has access to GPT-4o Vision
- Check backend console for FFmpeg errors
- Restart backend after installing FFmpeg

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
- Voice generation will fail gracefully with demo message
- Tasks and summaries will still work without voice

**"Vibe analysis error":**
- AWS Bedrock is optional (only for interview/coffee chat contexts)
- Check AWS credentials if you want this feature
- System works fine without it - will show "Not configured"
- Only runs for interview and coffee chat modes

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

✅ **Audio Transcription** - OpenAI Whisper with GPT-4o fact-checking  
✅ **Video Analysis** - FFmpeg frame extraction + GPT-4o Vision + Gemini Vision  
✅ **Task Extraction** - GPT-4o with dates, priorities, confidence scores  
✅ **Summary Generation** - Dual AI (GPT-4o + Gemini 2.0 Flash)  
✅ **Google Calendar** - Full OAuth 2.0, bulk scheduling, one-click events  
✅ **Social Dynamics** - AWS Bedrock Claude 3 Haiku vibe analysis  
✅ **Voice Summaries** - ElevenLabs TTS with streaming  
✅ **Dark Mode** - Full theme support with localStorage  
✅ **Context Modes** - Interview, coffee chat, lecture, general  
✅ **AI Coaching** - Interactive practice mode  
✅ **Large File Support** - Efficient streaming and chunking  
✅ **Error Handling** - Graceful fallbacks for all optional APIs  

### Demo Mode

EVE gracefully handles missing API keys:
- **Required**: OpenAI (for transcription and core features)
- **Highly Recommended**: Gemini, ElevenLabs, Google Calendar (core features work better with these)
- **Optional**: AWS Bedrock (vibe analysis only)
- UI shows clear messages when optional services are unavailable
- All features degrade gracefully with helpful error messages
- You can test the full flow with just an OpenAI key

---

## 🏆 AI Model Integrations

✅ **OpenAI** - Whisper transcription, GPT-4o reasoning, GPT-4o Vision for video  
✅ **Google** - Calendar OAuth 2.0 scheduling, Gemini 2.0 Flash cross-validation, Gemini Vision  
✅ **AWS** - Bedrock runtime with Claude 3 Haiku for social dynamics analysis  
✅ **ElevenLabs** - High-quality text-to-speech voice summaries  
✅ **FFmpeg** - Open-source video/audio processing engine 

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
- OpenAI (Whisper, GPT-4o, GPT-4o Vision)
- Google (Gemini 2.0 Flash, Gemini Vision, Calendar API)
- AWS Bedrock (Claude 3 Haiku)
- ElevenLabs (TTS)

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

- **Large video files** (>100MB) may take 2-5 minutes to process
- **FFmpeg required** for video - must be installed separately
- **Google Calendar** requires OAuth setup (detailed instructions in Step 2)
- **AWS Bedrock** requires IAM permissions - optional feature only
- Some rare audio formats may not be supported by Whisper
- Video analysis works best with clear, well-lit videos

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
