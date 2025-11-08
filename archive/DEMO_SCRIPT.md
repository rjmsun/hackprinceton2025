# 🎯 EVE Demo Script (2 minutes)

## Setup (Before Demo)

1. **Backend running** on http://localhost:8000
2. **Frontend running** on http://localhost:3000
3. **Browser open** to frontend
4. **Audio file ready** (`demo-transcript.txt` read aloud and recorded)
5. **Internet connection** verified

---

## Demo Flow (2 minutes)

### Opening (15 seconds)

> "Hi judges! This is **EVE - the Everyday Virtual Executive**. EVE is an AI companion that listens to your conversations, extracts actionable insights, and autonomously schedules your calendar."

> "Let me show you how it works."

---

### Part 1: Audio Transcription (30 seconds)

**Action:** Click "Start Recording" OR upload pre-recorded audio

> "I'm going to [record/upload] a quick team meeting conversation..."

**[Audio plays or is recorded - 20 seconds of demo-transcript.txt]**

> "Watch as EVE transcribes in real-time using OpenAI's Whisper API..."

**What judges see:**
- ✅ Live transcript appearing
- ✅ Professional UI

---

### Part 2: Intelligent Task Extraction (30 seconds)

**[EVE automatically processes after transcription]**

> "Now watch the magic happen. EVE uses Claude 3.5 and GPT-4o to understand the conversation and extract actionable tasks..."

**What judges see:**
- ✅ Tasks panel populates with 4-5 items
- ✅ Each task shows:
  - Action description
  - Due date/time
  - Owner (Maya, Alex)
  - Priority level
  - Confidence score
  - Context

> "Notice EVE identified the owner, deadline, and priority for each task. It even extracted implicit dates like 'Friday at 3 PM' and 'Monday afternoon.'"

---

### Part 3: Summary & Voice (30 seconds)

**Point to Summary panel:**

> "EVE also generates a concise summary of the meeting..."

**Read the short summary aloud, then:**

**Action:** Click "Listen" button

> "And here's the best part - EVE can speak the summary back to you using ElevenLabs voice synthesis..."

**[AI voice plays: "Got it - I scheduled the API documentation review..."]**

**What judges see:**
- ✅ Voice plays through speakers
- ✅ Professional AI voice quality

---

### Part 4: Autonomous Actions (15 seconds)

**Point to Tasks panel:**

> "Now I can select tasks and EVE will automatically create calendar events using Google Calendar API..."

**Action:** Select 2 tasks, click "Schedule Selected"

> "In a production environment, these would be added to my Google Calendar instantly. For this demo, you can see the integration is ready."

---

### Closing (10 seconds)

> "EVE combines **4 major sponsor APIs** - OpenAI for transcription and reasoning, Anthropic Claude for deep context understanding, ElevenLabs for voice, and Google Calendar for autonomous actions."

> "It's not just AI that listens - it's AI that **acts**. Thank you!"

---

## Backup Plan (if API fails)

**Have screenshots ready showing:**
1. Full transcript
2. Extracted tasks
3. Summary
4. Calendar event created

**Say:** "Let me show you the results from our test run earlier..."

---

## Key Points to Emphasize

✅ **Multimodal** - Voice in, text out, voice out  
✅ **Autonomous** - Actually takes actions (calendar)  
✅ **Practical** - Solves real productivity problems  
✅ **Multi-API** - 4+ sponsor integrations  
✅ **Production-ready UI** - Clean, modern, responsive  

---

## Judge Q&A Prep

**Q: How does it handle ambiguous dates?**
> "EVE assigns a confidence score. If < 80%, it asks for clarification instead of guessing."

**Q: What about privacy?**
> "Audio is processed in real-time and not stored by default. Users opt-in to save transcripts for long-term learning."

**Q: Can it handle longer meetings?**
> "Yes - Claude 3.5 has 200K context window. We can process hours of conversation and consolidate into project timelines."

**Q: What's the pricing?**
> "On free tiers, EVE can process ~100 meeting minutes. With paid tiers, costs ~$0.10 per hour of audio."

**Q: Future features?**
> "We're working on email/Slack integration, emotion detection, multi-agent debate mode with Photon API, and slide understanding with vision models."

---

## Timing Breakdown

| Section | Time | Cumulative |
|---------|------|------------|
| Opening | 15s | 0:15 |
| Transcription | 30s | 0:45 |
| Task Extraction | 30s | 1:15 |
| Summary + Voice | 30s | 1:45 |
| Calendar Actions | 15s | 2:00 |

Total: **2 minutes**

---

## Technical Checklist

- [ ] Backend running (`python backend/main.py`)
- [ ] Frontend running (`npm run dev` in frontend/)
- [ ] API keys in `.env`
- [ ] Browser open to localhost:3000
- [ ] Demo audio file ready (or mic tested)
- [ ] Volume turned up for voice playback
- [ ] Network connection stable
- [ ] Screenshots as backup

---

Good luck! 🚀

