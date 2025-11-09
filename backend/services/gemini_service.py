import google.genai as genai
from typing import Optional, Dict, List, Any
import json
import re

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        # Initialize client if key is provided
        if api_key and api_key != "your_gemini_api_key_here":
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None
    
    def generate_content(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        """Generate content using Gemini API (synchronous)"""
        if not self.client:
            return "[DEMO MODE] Add GEMINI_API_KEY to .env to use Gemini"
        
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")

    @staticmethod
    def _parse_json_best_effort(text: str) -> Dict[str, Any]:
        """Attempt to parse JSON from a Gemini response that may include code fences or extra text.
        Returns a dictionary; on failure returns a minimal fallback structure.
        """
        if not isinstance(text, str):
            return text  # Already JSON-like

        # Strip markdown code fences
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*$", "", cleaned)

        # Replace smart quotes with regular quotes
        cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'")
        cleaned = cleaned.replace("“", '"').replace("”", '"').replace("’", "'")

        # If the model wrapped JSON in prose, extract the first {...} block
        if '{' in cleaned and '}' in cleaned:
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            candidate = cleaned[start:end]
        else:
            candidate = cleaned

        # Some responses include LaTeX like \( ... \); remove those backslashes to avoid invalid escapes
        candidate = candidate.replace("\\(", "(").replace("\\)", ")")

        try:
            return json.loads(candidate)
        except Exception:
            # Final fallback – return as text inside a standard schema
            snippet = cleaned[:300]
            return {
                "short_summary": snippet,
                "detailed_summary": [cleaned]
            }
    
    async def extract_insights(self, transcript: str) -> Dict:
        """Extract insights from transcript using Gemini"""
        if not self.client:
            return {
                "insights": ["[DEMO] Add GEMINI_API_KEY to extract real insights"],
                "key_points": [],
                "action_items": []
            }
        
        prompt = f"""Analyze this meeting transcript and extract:
1. Key insights (3-5 main points)
2. Important decisions made
3. Action items mentioned

Return as JSON: {{"insights": [...], "key_points": [...], "action_items": [...]}}

Transcript:
{transcript}"""

        try:
            response_text = self.generate_content(prompt)
            parsed = self._parse_json_best_effort(response_text)
            # Ensure keys exist
            return {
                "insights": parsed.get("insights", parsed if isinstance(parsed, list) else []),
                "key_points": parsed.get("key_points", []),
                "action_items": parsed.get("action_items", [])
            }
        except Exception as e:
            # Never raise for parsing issues – return textual fallback
            return {
                "insights": [str(e)],
                "key_points": [],
                "action_items": []
            }
    
    async def generate_summary_gemini(self, transcript: str) -> Dict:
        """Generate comprehensive summary using Gemini with same structure as OpenAI"""
        if not self.client:
            return {
                "short_summary": "[DEMO] Add GEMINI_API_KEY for Gemini summaries",
                "detailed_summary": [],
                "insights": [],
                "clarifying_questions": [],
                "knowledge_gaps": [],
                "strengths": []
            }
        
        # Adaptive sizing based on transcript length (same as OpenAI)
        word_count = len(transcript.split())
        if word_count < 300:
            summary_bullets = "2-3"
            insights_count = "2-3"
            questions_count = "2-3"
        elif word_count < 800:
            summary_bullets = "4-6"
            insights_count = "3-4"
            questions_count = "3-4"
        else:
            summary_bullets = "6-10"
            insights_count = "4-6"
            questions_count = "4-6"
        
        prompt = f"""Create a comprehensive summary for this {word_count}-word transcript.

Analyze for:
- Understanding vs confusion
- Strengths vs knowledge gaps  
- Main topics and decisions
- Communication patterns

Return JSON with EXACT structure:
{{
  "short_summary": "1-2 sentences capturing essence and struggles",
  "detailed_summary": ["{summary_bullets} bullet points covering topics, decisions, tasks, confusion"],
  "insights": ["{insights_count} observations about understanding and communication"],
  "clarifying_questions": ["{questions_count} questions to improve understanding"],
  "knowledge_gaps": ["areas where knowledge is missing or unclear"],
  "strengths": ["demonstrated competencies and positive aspects"]
}}

Transcript: {transcript}"""

        try:
            response_text = self.generate_content(prompt)
            parsed = self._parse_json_best_effort(response_text)
            
            # Ensure all required fields exist with proper structure
            return {
                "short_summary": parsed.get("short_summary", (response_text or "")[:200]),
                "detailed_summary": parsed.get("detailed_summary", [response_text] if response_text else []),
                "insights": parsed.get("insights", []),
                "clarifying_questions": parsed.get("clarifying_questions", []),
                "knowledge_gaps": parsed.get("knowledge_gaps", []),
                "strengths": parsed.get("strengths", [])
            }
        except Exception as e:
            # Comprehensive fallback with all fields
            text = str(e)
            return {
                "short_summary": text[:200],
                "detailed_summary": [text],
                "insights": ["Error generating insights with Gemini"],
                "clarifying_questions": [],
                "knowledge_gaps": ["Unable to analyze knowledge gaps"],
                "strengths": []
            }

