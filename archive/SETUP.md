# 🚀 EVE Setup Instructions

## Quick Setup (5 minutes)

### Step 1: Get Your API Keys

You need **3 API keys**. Get them from:

1. **OpenAI**: https://platform.openai.com/api-keys
   - Sign up → Create API key → Copy (starts with `sk-proj-`)

2. **Anthropic**: https://console.anthropic.com/
   - Sign up → API Keys → Create key → Copy (starts with `sk-ant-`)

3. **ElevenLabs**: https://elevenlabs.io/
   - Sign up → Profile → API Keys → Copy

**All 3 have free tiers!** Should cost $0 for hackathon demo.

---

### Step 2: Install Dependencies

```bash
# Run the install script
./install.sh
```

This installs:
- Python backend dependencies (FastAPI, OpenAI, Anthropic, etc.)
- Node.js frontend dependencies (Next.js, React, Tailwind)

---

### Step 3: Add API Keys

```bash
# Create .env file
cp env.example .env

# Edit it
nano .env   # or use: code .env, vim .env, etc.
```

**Replace these 3 lines in `.env`:**

```bash
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
ANTHROPIC_API_KEY=sk-ant-YOUR_ACTUAL_KEY_HERE
ELEVENLABS_API_KEY=YOUR_ACTUAL_KEY_HERE
```

**Save the file!**

---

### Step 4: Test Your Keys

```bash
./test-api-keys.sh
```

Should see:
```
✅ OPENAI_API_KEY configured
✅ ANTHROPIC_API_KEY configured
✅ ELEVENLABS_API_KEY configured
```

---

### Step 5: Run EVE

```bash
./start.sh
```

Open browser to: **http://localhost:3000**

---

## Manual Setup (if scripts don't work)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Keep this terminal open (backend runs on port 8000).

### Frontend

Open **new terminal**:

```bash
cd frontend
npm install
npm run dev
```

Keep this terminal open (frontend runs on port 3000).

---

## Verify It's Working

1. Open http://localhost:3000
2. You should see EVE interface
3. Click "Start Recording" or upload audio file
4. Should transcribe and extract tasks

---

## Troubleshooting

### "Command not found: python3"

Install Python: https://www.python.org/downloads/

### "Command not found: npm"

Install Node.js: https://nodejs.org/

### "API key not found"

- Check `.env` exists in project root
- Check you edited `.env` (not `env.example`)
- Check no spaces: `KEY=value` not `KEY = value`
- Restart backend after editing `.env`

### "Module not found" (Python)

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "Cannot find module" (Node)

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### "Port already in use"

```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill  # backend
lsof -ti:3000 | xargs kill  # frontend
```

### Backend won't start

```bash
cd backend
source venv/bin/activate
python run.py  # Alternative entry point
```

---

## File Structure

```
hackprinceton2025/
├── backend/              # FastAPI backend
│   ├── main.py          # API routes
│   ├── run.py           # Alternative entry point
│   ├── requirements.txt # Python dependencies
│   └── services/        # AI integrations
│       ├── transcription.py   (OpenAI Whisper)
│       ├── reasoning.py       (Claude + GPT-4o)
│       ├── tts.py            (ElevenLabs)
│       ├── calendar_service.py (Google Calendar)
│       └── analytics.py      (Amplitude)
│
├── frontend/            # Next.js frontend
│   ├── app/            # Pages
│   ├── components/     # UI components
│   └── package.json    # Node dependencies
│
├── .env                # YOUR API KEYS (create this!)
├── env.example         # Example env file
├── start.sh           # Start both servers
├── install.sh         # Install dependencies
└── test-api-keys.sh   # Test API keys
```

---

## Next Steps

1. ✅ Setup complete? Read: `QUICKSTART.md`
2. 🎯 Ready to demo? Read: `DEMO_SCRIPT.md`
3. 🔑 Need help with keys? Read: `API_KEYS_GUIDE.md`
4. 📖 Full documentation: `README.md`

---

## For Judges / Demo

Pre-demo checklist:
- [ ] Backend running (`./start.sh`)
- [ ] Frontend open in browser
- [ ] Demo audio file ready
- [ ] API keys working (test with `./test-api-keys.sh`)
- [ ] Volume up for voice playback
- [ ] Network connected

Demo flow: Record/upload audio → See tasks → Hear summary (2 minutes)

---

Good luck! 🏆

