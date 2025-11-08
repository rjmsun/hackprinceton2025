import openai
import json
from typing import Dict, List, Any, Optional

class ReasoningService:
    def __init__(self, openai_key: Optional[str] = None):
        self.openai_key = openai_key
        self.openai_client = openai.OpenAI(api_key=openai_key) if openai_key and openai_key != "your_openai_api_key_here" else None
    
    async def clean_transcript(self, raw_transcript: str) -> Dict:
        """Clean and segment transcript using GPT-4o"""
        if not self.openai_client:
            return {
                "sections": [{
                    "title": "Demo Section",
                    "speakered_text": [{"speaker": "Speaker A", "text": raw_transcript}]
                }]
            }
        
        prompt = f"""Input: raw transcript below. 
Tasks:
1) Normalize punctuation and capitalization.
2) Remove filler tokens like "um", "uh", "like" unless they change meaning.
3) Segment the transcript into sections whenever the topic clearly shifts. Assign each section a short title (3–6 words).
4) If speakers are labeled (Speaker 1 / Speaker 2 etc.), preserve labels. If not, try to detect changes in speaker by line breaks and mark them "Speaker A", "Speaker B", etc.
5) Return a JSON object: {{ "sections": [ {{ "title": "...", "start_time": "HH:MM:SS" (optional), "end_time": "HH:MM:SS" (optional), "speakered_text": [ {{"speaker":"Speaker A", "text":"..."}} , ... ] }} ] }}.

Raw transcript:
```
{raw_transcript}
```"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a precise text normalization assistant. Remove filler words, label speakers when indicated, and split long transcripts into logical segments. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1200,
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        if not result:
            raise Exception("OpenAI returned empty response")
        return json.loads(result)
    
    async def extract_tasks(self, sections: List[Dict], timezone: str = "America/New_York") -> Dict:
        """Extract actionable tasks using GPT-4o"""
        if not self.openai_client:
            return {
                "tasks": [{
                    "id": "demo-1",
                    "action": "[DEMO] Add OPENAI_API_KEY to extract real tasks",
                    "context": "This is a placeholder task",
                    "due": None,
                    "date_hint": None,
                    "owner": None,
                    "priority": "medium",
                    "confidence": 0.5,
                    "source_section": "Demo Section"
                }]
            }
        
        prompt = f"""Input: cleaned transcript sections (JSON). 
Task: From the transcript, extract all actionable items, decisions, and commitments. For each item, produce:
- id: short unique id
- action: concise action description
- context: brief context sentence (1-2 lines)
- due: ISO8601 datetime if explicit, otherwise null
- date_hint: natural-language hint if no explicit date (e.g., "next Friday")
- owner: person or role responsible if mentioned, otherwise null
- priority: one of ["low","medium","high"] (use judgement)
- confidence: float between 0.0 and 1.0 (how sure you are)
- source_section: title of section where it came from

Return a JSON object with key "tasks" containing an array.

Timezone: {timezone}

Here is the input:
{json.dumps(sections, indent=2)}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an exacting task extraction engine. Produce only JSON that conforms to the schema. Attempt to resolve natural-language dates into ISO 8601 where possible. If no explicit date is present, set \"due\": null and \"date_hint\": \"<text hint>\". Add a \"confidence\" (0.0–1.0). Return JSON with structure: {\"tasks\": [{id, action, context, due, date_hint, owner, priority, confidence, source_section}]}"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        if not result:
            return {"tasks": []}
        return json.loads(result)
    
    async def create_event_suggestion(self, task: Dict, timezone: str) -> Dict:
        """Create calendar event suggestion from task"""
        prompt = f"""Input: task object:
{json.dumps(task, indent=2)}

User timezone: {timezone}

Tasks:
1) Return a JSON object "event_suggestion" with fields:
- title
- start_time (ISO8601 with timezone)
- end_time (ISO8601 with timezone)
- description (brief)
- calendar_confidence (0.0-1.0)
2) If due is a date without time, provide 2 options as an array "alternatives".

Return only JSON."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a scheduling assistant. Use user's locale/timezone when resolving dates. When the task has an explicit ISO due, schedule a reasonable calendar event time (e.g., 30–60 minutes). Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=400
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    
    async def generate_clarification(self, task: Dict) -> str:
        """Generate clarification question for ambiguous tasks"""
        prompt = f"""Input: task object with fields and confidence. If confidence < 0.75 or due==null, craft a single short question that the assistant can speak or display to the user to resolve the missing info. The question should be friendly and specific.

Example task:
{json.dumps(task, indent=2)}

Return only the question text, no JSON."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a concise clarification assistant. Generate a single clear question asking only what is missing (date, owner, or ambiguity)."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip('"')
    
    async def generate_summary(self, sections: List[Dict], tasks: List[Dict]) -> Dict:
        """Generate adaptive smart summary that captures understanding, confusion, and gaps"""
        if not self.openai_client:
            return {
                "short_summary": "[DEMO] Add OPENAI_API_KEY for summaries",
                "detailed_summary": [],
                "insights": [],
                "clarifying_questions": [],
                "knowledge_gaps": [],
                "strengths": []
            }
        
        prompt = f"""You are an ADAPTIVE learning assistant analyzing this conversation. Your job is to create a summary that ADAPTS to what was actually said - both strengths AND gaps.

CRITICAL: Look for expressions of confusion, uncertainty, or gaps like:
- "I don't understand [concept]"
- "I'm not sure about [topic]"
- "This part is confusing"
- "I need to learn more about [X]"
- "What does [term] mean?"
- Any indication of struggling with a concept

Provide:

1. **short_summary**: One sentence capturing the essence (both what was covered AND any struggles)

2. **detailed_summary**: 4-6 bullet points including:
   - Main topics discussed
   - Key points made
   - Important decisions/tasks
   - **CRITICAL**: Any concepts the speaker struggled with or didn't understand

3. **insights**: 3-5 observations about:
   - What the speaker understands well
   - Communication patterns
   - Areas showing mastery
   - Underlying themes

4. **knowledge_gaps**: IMPORTANT - Explicitly list any concepts/topics where the speaker expressed:
   - Confusion or uncertainty
   - Lack of understanding
   - Need for clarification
   - Gaps in knowledge
   If NONE found, return empty array.

5. **strengths**: 2-3 areas where the speaker demonstrated strong understanding

6. **clarifying_questions**: 3-4 questions that would help:
   - Address any confusion mentioned
   - Fill knowledge gaps
   - Clarify ambiguous points
   - Deepen understanding

BE ADAPTIVE - if they say "I don't get X", your summary should say "Struggled with understanding X" not ignore it.

Return JSON: {{
  "short_summary": "...",
  "detailed_summary": ["...", "..."],
  "insights": ["...", "..."],
  "knowledge_gaps": ["concept/topic where confusion was expressed", "..."],
  "strengths": ["...", "..."],
  "clarifying_questions": ["...", "..."]
}}

Transcript Sections:
{json.dumps(sections, indent=2)}

Extracted Tasks:
{json.dumps(tasks, indent=2)}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an adaptive learning assistant. Your summaries must CAPTURE and HIGHLIGHT any expressions of confusion, uncertainty, or knowledge gaps. Don't just summarize the 'good parts' - adapt to what was actually said, including struggles. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        if not result:
            raise Exception("OpenAI returned empty response")
        
        summary_data = json.loads(result)
        
        # Ensure all fields exist
        return {
            "short_summary": summary_data.get("short_summary", ""),
            "detailed_summary": summary_data.get("detailed_summary", []),
            "insights": summary_data.get("insights", []),
            "knowledge_gaps": summary_data.get("knowledge_gaps", []),
            "strengths": summary_data.get("strengths", []),
            "clarifying_questions": summary_data.get("clarifying_questions", [])
        }
    
    async def generate_voice_summary(self, actions: List[Dict]) -> str:
        """Generate spoken summary text"""
        prompt = f"""Input: list of actions created:
{json.dumps(actions, indent=2)}

Task: produce a 1–2 sentence spoken summary confirming created events and offering help.

Return only the single text string."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a friendly productivity assistant named EVE. Keep the voice concise (1–2 sentences), confirm actions taken, and politely ask if further help is needed."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip('"')
    
    async def generate_study_materials(self, transcript: str) -> Dict:
        """Generate flashcards and quiz from transcript"""
        prompt = f"""Input: meeting transcript or summary (educational content).
Tasks:
1) Generate up to 10 flashcards as JSON array: {{id, question, answer, difficulty: ["easy","medium","hard"]}}
2) Generate a 5-question multiple-choice quiz as JSON array: {{id, question, options: ["A","B","C","D"], answer_index: 0-3, explanation}}

Return JSON: {{"flashcards": [...], "quiz": [...]}}

Transcript:
{transcript}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Produce high-quality flashcards from educational content. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    
    async def analyze_sentiment(self, transcript: str) -> Dict:
        """Analyze sentiment and communication patterns"""
        prompt = f"""Input: cleaned transcript with speaker labels and timestamps.
Tasks:
1) Estimate number of interruptions (quick overlapped phrases).
2) Provide average speaking time per speaker (in seconds).
3) Provide 3 short suggestions to improve communication.

Return JSON: {{"interruptions": int, "avg_speaking_seconds": {{"Speaker A":45}}, "suggestions":["...","...","..."]}}

Transcript:
{transcript}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a communication coach. Provide objective metrics and concise suggestions. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=400
        )
        
        result = response.choices[0].message.content
        return json.loads(result)

