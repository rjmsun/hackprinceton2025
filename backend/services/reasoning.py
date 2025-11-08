import openai
import anthropic
import json
from typing import Dict, List, Any, Optional

class ReasoningService:
    def __init__(self, openai_key: Optional[str] = None, anthropic_key: Optional[str] = None):
        self.openai_key = openai_key
        self.anthropic_key = anthropic_key
        self.openai_client = openai.OpenAI(api_key=openai_key) if openai_key and openai_key != "your_openai_api_key_here" else None
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key) if anthropic_key and anthropic_key != "your_anthropic_api_key_here" else None
    
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
        """Extract actionable tasks using Claude 3.5"""
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

Return a JSON array under the key "tasks".

Timezone: {timezone}

Here is the input:
{json.dumps(sections, indent=2)}"""

                # Prefer Anthropic if available, else fall back to OpenAI
                if self.anthropic_client:
                    try:
                        message = self.anthropic_client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=1500,
                            temperature=0.0,
                            system="You are an exacting task extraction engine. Produce only JSON that conforms to the schema. Attempt to resolve natural-language dates into ISO 8601 where possible. If no explicit date is present, set \"due\": null and \"date_hint\": \"<text hint>\". Add a \"confidence\" (0.0–1.0).",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        result = message.content[0].text
                        return json.loads(result)
                    except Exception:
                        # fall through to OpenAI fallback
                        pass
                
                if self.openai_client:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are an exacting task extraction engine. Return only valid JSON matching the schema with keys: tasks: [ {id, action, context, due, date_hint, owner, priority, confidence, source_section} ]. Resolve natural-language dates using the timezone provided."},
                            {"role": "user", "content": f"Timezone: {timezone}\n\n{prompt}"}
                        ],
                        temperature=0.0,
                        max_tokens=1500
                    )
                    result = response.choices[0].message.content
                    return json.loads(result)
                
                # As last resort, return an empty list rather than failing
                return {"tasks": []}
    
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
        """Generate short and detailed summaries"""
        prompt = f"""Input: full meeting transcript sections and tasks list.
Tasks:
1) short_summary: 1 sentence
2) detailed_summary: 3-6 bullets that cover decisions, tasks, and risks.

Return JSON: {{ "short_summary": "...", "detailed_summary": ["...", "..."] }}

Sections:
{json.dumps(sections, indent=2)}

Tasks:
{json.dumps(tasks, indent=2)}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Produce two outputs: short_summary (1 sentence) and detailed_summary (array of 3–6 bullet points). Keep tone professional and neutral. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=400
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    
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

