# 🔑 API Keys Setup Guide

## Required Keys (3)

### 1. OpenAI API Key

**What it does:** Transcription (Whisper) + Task extraction (GPT-4o)

**Where to get it:**
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)

**Add to `.env`:**
```bash
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
```

**Cost:** ~$0.006 per minute of audio transcription, ~$0.03 per 1K tokens for GPT-4o
**Free tier:** $5 credit for new accounts

---

### 2. Anthropic API Key

**What it does:** Deep reasoning and task extraction (Claude 3.5)

**Where to get it:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new key
5. Copy the key (starts with `sk-ant-...`)

**Add to `.env`:**
```bash
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
```

**Cost:** ~$3 per million input tokens, ~$15 per million output tokens
**Free tier:** $5 credit for new accounts

---

### 3. ElevenLabs API Key

**What it does:** Text-to-speech for voice summaries

**Where to get it:**
1. Go to https://elevenlabs.io/
2. Sign up or log in
3. Go to Profile → API Keys
4. Copy your key

**Add to `.env`:**
```bash
ELEVENLABS_API_KEY=YOUR_KEY_HERE
```

**Cost:** Free tier includes 10,000 characters/month
**Free tier:** Yes - 10K characters is ~20 voice summaries

---

## Optional Keys

### Google Calendar (for auto-scheduling)

**What it does:** Creates calendar events automatically

**Setup:**
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "Google Calendar API"
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Application type: Web application
6. Authorized redirect URIs: `http://localhost:3000/auth/callback`
7. Copy Client ID and Client Secret

**Add to `.env`:**
```bash
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET
```

**Cost:** Free (no quota limits for personal use)

---

### Amplitude (analytics)

**What it does:** Tracks usage metrics and events

**Where to get it:**
1. Go to https://amplitude.com/
2. Sign up for free
3. Create a project
4. Copy your API key from project settings

**Add to `.env`:**
```bash
AMPLITUDE_API_KEY=YOUR_KEY_HERE
```

**Cost:** Free tier up to 10M events/month

---

## How to Add Keys to EVE

1. **Create `.env` file in project root:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` with your text editor:**
   ```bash
   nano .env
   # or
   code .env
   # or
   vim .env
   ```

3. **Paste your keys** (replace the placeholder values)

4. **Verify your `.env` looks like this:**
   ```bash
   OPENAI_API_KEY=sk-proj-abc123...
   ANTHROPIC_API_KEY=sk-ant-xyz789...
   ELEVENLABS_API_KEY=def456...
   ```

5. **Save and close the file**

6. **NEVER commit `.env` to git** (it's already in `.gitignore`)

---

## Testing Your Keys

Run this to verify keys are loaded:

```bash
cd backend
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI:', 'sk-' in os.getenv('OPENAI_API_KEY', '')); print('Anthropic:', 'sk-' in os.getenv('ANTHROPIC_API_KEY', '')); print('ElevenLabs:', bool(os.getenv('ELEVENLABS_API_KEY')))"
```

Should output:
```
OpenAI: True
Anthropic: True
ElevenLabs: True
```

---

## Budget Estimates

For a full hackathon demo (2 days of testing):

| Service | Usage | Cost |
|---------|-------|------|
| OpenAI Whisper | 60 min audio | ~$0.36 |
| OpenAI GPT-4o | 50 requests | ~$2.00 |
| Anthropic Claude | 30 requests | ~$1.50 |
| ElevenLabs | 50 summaries | Free tier |
| **Total** | | **~$4** |

All services have free tiers that should cover your hackathon needs!

---

## Troubleshooting

**"API key not found" error:**
- Check `.env` is in the project root (not in backend/ or frontend/)
- Verify no extra spaces: `OPENAI_API_KEY=sk-...` (no spaces around `=`)
- Restart backend server after editing `.env`

**"Invalid API key" error:**
- Double-check you copied the full key
- Verify the key hasn't expired
- Check you're using the right key for the right service

**"Rate limit exceeded":**
- You've hit your free tier limit
- Wait 60 seconds and try again
- Or add credits to your account

---

## Security Notes

- ✅ `.env` is in `.gitignore` (never committed)
- ✅ Keys are only stored locally
- ✅ Never share your `.env` file
- ✅ Rotate keys if accidentally exposed
- ✅ Use environment variables in production

---

## Quick Reference

```bash
# Create .env
cp env.example .env

# Edit .env
nano .env

# Add these 3 keys:
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...

# Save and run EVE
./start.sh
```

That's it! 🚀

