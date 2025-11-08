# EVE Final Feature Set - HackPrinceton 2025

## 🎯 Core Capabilities

### 1. **Real-Time Live Transcription** ✅
- **Technology**: OpenAI Whisper via WebSocket streaming
- **Latency**: ~2-3 seconds per chunk
- **Features**:
  - Audio captured in 100ms chunks
  - Transcripts appear as you speak
  - No waiting until recording stops
  - Optimized for low-latency performance

### 2. **Dual Smart Summaries** ✅
- **OpenAI GPT-4o Summary**:
  - Adaptive analysis that captures both understanding AND confusion
  - Explicitly identifies knowledge gaps
  - Highlights demonstrated strengths
  - Generates targeted clarifying questions
  
- **Gemini 2.5 Flash Summary**:
  - Alternative perspective on the same content
  - Quick, efficient processing
  - Comparison helps validate insights

**Why Dual Summaries?**
- Multiple AI perspectives provide more comprehensive analysis
- Cross-validation ensures accuracy
- Different models catch different nuances

### 3. **Task Extraction** ✅
- **Technology**: OpenAI GPT-4o
- **Features**:
  - Extracts actionable items from conversations
  - Assigns priority levels (low/medium/high)
  - Confidence scoring
  - Date/deadline detection
  - Owner assignment

### 4. **Google Calendar Integration** ✅
- **Technology**: Google Calendar API with OAuth2
- **Features**:
  - Autonomous event creation from extracted tasks
  - Secure OAuth authentication
  - One-click calendar scheduling
  - Automatic time suggestions

### 5. **Voice Synthesis with Personality** ✅
- **Technology**: ElevenLabs TTS
- **Features**:
  - Motivational recaps of summaries
  - Encouragement for knowledge gaps
  - Natural, engaging voice
  - Adds personality to feedback

---

## 🏆 Sponsor API Integration

| Sponsor | API/Technology | Purpose | Status |
|---------|----------------|---------|--------|
| **OpenAI** | Whisper, GPT-4o | Transcription, summaries, task extraction | ✅ |
| **Google** | Calendar API, Gemini 2.5 | Autonomous scheduling, alternative summaries | ✅ |
| **ElevenLabs** | TTS API | Voice synthesis, motivational feedback | ✅ |
| **MLH** | Amplitude, Snowflake | Analytics, data storage (optional) | ✅ |

**Note**: Claude/Anthropic was REMOVED per user request. All processing now uses OpenAI GPT-4o.

---

## 🎬 User Flow

### Live Recording Mode:
```
1. User clicks "Start Recording"
   ↓
2. MediaRecorder captures audio → WebSocket sends chunks
   ↓
3. Backend accumulates ~2 seconds → Whisper transcribes
   ↓
4. Partial transcript sent to frontend → Displays in real-time
   ↓
5. User clicks "Stop Recording"
   ↓
6. Final processing begins:
   - Validate & enhance transcript (GPT-4o)
   - Clean & segment (GPT-4o)
   - Extract tasks (GPT-4o)
   - Generate OpenAI summary (GPT-4o)
   - Generate Gemini summary (Gemini 2.5 Flash)
   ↓
7. User reviews:
   - Live transcript
   - Dual summaries (toggle between OpenAI/Gemini)
   - Extracted tasks
   - Knowledge gaps & strengths
   - Clarifying questions
   ↓
8. User can:
   - Connect Google Calendar
   - Schedule tasks autonomously
   - Listen to motivational voice recap (ElevenLabs)
```

### File Upload Mode:
```
1. User uploads audio file (MP3, WAV, WebM, etc.)
   ↓
2. Backend transcribes entire file (Whisper)
   ↓
3. Same processing pipeline as live mode (steps 6-8 above)
```

---

## 🧠 Adaptive Summary Intelligence

### What Makes It "Adaptive"?

**Traditional Summaries**:
- ❌ Just extract the "good parts"
- ❌ Ignore confusion or gaps
- ❌ Generic, one-size-fits-all

**EVE's Adaptive Summaries**:
- ✅ **Captures confusion**: Detects "I don't understand X"
- ✅ **Identifies gaps**: Creates dedicated "Knowledge Gaps" section
- ✅ **Shows strengths**: Highlights what you DO understand
- ✅ **Targeted questions**: Generates questions specific to YOUR gaps

### Example Input:
> "I'm studying for my interview. I know arrays and linked lists pretty well. But I'm really struggling with dynamic programming. I don't understand how to break problems down into subproblems."

### EVE's Output:
**✅ Strengths**:
- Understanding of arrays and linked lists

**⚠️ Knowledge Gaps**:
- Dynamic programming problem decomposition
- Subproblem identification

**❓ Clarifying Questions**:
- "Can you explain the process of breaking down a DP problem into smaller subproblems?"
- "What are some common patterns for identifying DP problems?"

---

## 🎙️ Voice Synthesis with Motivation

### Features:
- **Personality**: Friendly, encouraging tone
- **Adaptive**: Acknowledges knowledge gaps with encouragement
- **Motivational**: "Keep pushing forward!", "You're making progress!"
- **Context-aware**: References specific topics from the summary

### Example Voice Output:
> "Great work! You've covered Rich Caruana's work on GAMs and medical data models. I noticed you're working on understanding interaction terms and backfitting algorithms. Keep pushing forward - you're making excellent progress!"

---

## 📊 Technical Stack

### Backend (FastAPI):
- `transcription.py`: Whisper API, real-time streaming
- `reasoning.py`: GPT-4o for cleaning, extraction, summaries
- `gemini_service.py`: Gemini API for alternative summaries
- `calendar_service.py`: Google OAuth & event creation
- `tts.py`: ElevenLabs voice synthesis
- `coffee_chat.py`: Vibe scoring, coaching (optional)

### Frontend (Next.js + React):
- `RecordingPanel.tsx`: WebSocket audio streaming
- `SummaryPanel.tsx`: Dual summary display with tabs
- `TasksPanel.tsx`: Task management & calendar integration
- `Dashboard.tsx`: Analytics display

---

## 🚀 Performance

| Metric | Value |
|--------|-------|
| Live Transcription Latency | 2-3 seconds |
| File Upload Max Size | 100MB |
| Processing Time (full pipeline) | 5-15 seconds |
| WebSocket Connection | < 1 second |
| Voice Synthesis | 2-3 seconds |

---

## 🔑 Required API Keys

1. **OpenAI** (https://platform.openai.com/api-keys)
   - Used for: Whisper, GPT-4o
   
2. **ElevenLabs** (https://elevenlabs.io/)
   - Used for: Voice synthesis
   
3. **Gemini** (https://ai.google.dev/)
   - Used for: Alternative summaries
   
4. **Google Cloud** (https://console.cloud.google.com/)
   - Used for: Calendar API OAuth

---

## 🎉 What Makes EVE Special

1. **Truly Adaptive**: Captures what you DON'T know, not just what you DO
2. **Multi-Model**: OpenAI + Gemini for comprehensive analysis
3. **Low Latency**: Real-time transcription as you speak
4. **Autonomous**: Automatically schedules tasks to your calendar
5. **Motivational**: Voice feedback with personality and encouragement
6. **Multimodal**: Audio → Text → Structure → Voice

---

## 📖 Usage Example

**Scenario**: Studying for a technical interview

1. **Record** yourself explaining concepts out loud
2. **See** live transcription as you speak
3. **Get** dual summaries identifying:
   - ✅ What you explained well
   - ⚠️ What you struggled with
   - ❓ Questions to help you improve
4. **Extract** study tasks automatically
5. **Schedule** review sessions to your calendar
6. **Listen** to motivational voice recap

**Result**: A personalized study plan based on YOUR specific gaps!

---

Built with ❤️ for HackPrinceton 2025

