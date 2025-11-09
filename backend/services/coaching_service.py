import openai
import json
from typing import Dict, Any, Optional

class CoachingService:
    def __init__(self, openai_key: Optional[str] = None):
        self.client = openai.OpenAI(api_key=openai_key) if openai_key and openai_key != "your_openai_api_key_here" else None

    async def generate_coaching_insights(self, transcript: str, context: str) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Coaching service not configured"}
        
        if context == "interview":
            return await self._get_interview_feedback(transcript)
        elif context == "coffee_chat":
            return await self._get_coffee_chat_tips(transcript)
        
        return {} # No special coaching for 'general' or 'lecture'

    async def _get_interview_feedback(self, transcript: str) -> Dict[str, Any]:
        prompt = f"""
        You are an expert FAANG interview coach. Analyze this mock interview transcript between "Speaker A" (Interviewer) and "Speaker B" (Interviewee).
        Your goal is to provide actionable feedback for "Speaker B".
        
        Transcript:
        {transcript}
        
        Return a JSON object with two keys:
        1. "strengths": A list of 3-5 bullet points where "Speaker B" performed well.
        2. "areas_for_improvement": A list of 3-5 actionable bullet points. For each, include the original quote and a "Suggested Improvement".
        
        Example JSON:
        {{
            "strengths": ["Clearly articulated their thinking process.", "Used the STAR method effectively for behavioral questions."],
            "areas_for_improvement": [
                {{
                    "quote": "I guess I don't have much experience with that.",
                    "suggestion": "Instead of highlighting a negative, pivot to a related strength: 'While I haven't used that specific tool, I'm a fast learner and have experience with [Related Tool], which shares a similar concept.'"
                }}
            ]
        }}
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a FAANG interview coach who provides structured, actionable feedback in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            result = response.choices[0].message.content
            return json.loads(result) if result else {}
        except Exception as e:
            print(f"Error getting interview feedback: {e}")
            return {"error": str(e)}

    async def _get_coffee_chat_tips(self, transcript: str) -> Dict[str, Any]:
        prompt = f"""
        You are a career advisor. Analyze this coffee chat transcript.
        Extract 3-5 "Key Career Tips" or "Actionable Takeaways" mentioned by the professional (Speaker A).
        Also, identify 2-3 "Follow-Up Actions" the user (Speaker B) should take.
        
        Transcript:
        {transcript}
        
        Return a JSON object: {{"key_tips": [...], "follow_ups": [...]}}
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a career advisor who extracts key tips and follow-up actions into a structured JSON response."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=600,
                response_format={"type": "json_object"}
            )
            result = response.choices[0].message.content
            return json.loads(result) if result else {}
        except Exception as e:
            print(f"Error getting coffee chat tips: {e}")
            return {"error": str(e)}
