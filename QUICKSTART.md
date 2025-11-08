# ⚡ Quick Start Guide

## 1️⃣ Add Your API Keys (2 minutes)

Copy `env.example` to `.env`:
```bash
cp env.example .env
```

Edit `.env` and add these **3 required keys**:

### OpenAI API Key
```
OPENAI_API_KEY=sk-proj-...
```
Get it: https://platform.openai.com/api-keys

### Anthropic API Key
```
ANTHROPIC_API_KEY=sk-ant-...
```
Get it: https://console.anthropic.com/

### ElevenLabs API Key
```
ELEVENLABS_API_KEY=...
```
Get it: https://elevenlabs.io/

---

## 2️⃣ Run EVE

### Option A: Use the start script (Mac/Linux)
```bash
chmod +x start.sh
./start.sh
```

### Option B: Manual start

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 3️⃣ Use EVE

Open http://localhost:3000

1. Click **"Start Recording"** or **upload audio file**
2. EVE will:
   - ✅ Transcribe (OpenAI Whisper)
   - ✅ Extract tasks (Claude 3.5)
   - ✅ Generate summary (GPT-4o)
   - ✅ Create voice recap (ElevenLabs)

---

## ⚠️ Troubleshooting

**"API key not found"**
- Make sure `.env` file exists in the root folder
- Verify keys start with `sk-proj-` (OpenAI) or `sk-ant-` (Anthropic)
- Restart backend after editing `.env`

**"Cannot find module" error in frontend**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**"Module not found" error in backend**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**"Port already in use"**
- Kill existing processes: `lsof -ti:8000 | xargs kill` (backend)
- Or use different ports in `.env`

---

## 🎯 For Demo / Judges

1. Pre-record a 30-second meeting clip
2. Upload to EVE
3. Watch it:
   - Transcribe in real-time
   - Extract 3-5 tasks automatically
   - Generate summary
   - Speak the summary back

**Pro tip**: Have a backup recording ready in case of API rate limits!

---

## 📚 Optional Integrations

### Google Calendar (for auto-scheduling)
1. Go to https://console.cloud.google.com/
2. Create project → Enable Calendar API
3. Create OAuth credentials
4. Add to `.env`:
```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### Amplitude (for analytics)
```
AMPLITUDE_API_KEY=...
```

### Snowflake (for data storage)
```
SNOWFLAKE_ACCOUNT=...
SNOWFLAKE_USER=...
```

---

## 🏆 What Makes EVE Win

✅ **4 Major Sponsor APIs** (OpenAI, Anthropic, Google, ElevenLabs)  
✅ **Real autonomous actions** (schedules calendar events)  
✅ **Multimodal** (voice in → text + voice out)  
✅ **Practical utility** (actually useful for students/hackers)  
✅ **Polished UI** (Next.js + Tailwind)  
✅ **2-minute "wow" demo** (upload audio → see magic happen)

---

Need help? Check `README.md` for full documentation.

