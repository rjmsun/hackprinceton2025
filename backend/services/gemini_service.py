import google.genai as genai
from typing import Optional, Dict, List, Any
import json

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
            # Try to parse as JSON, fallback to text if not valid JSON
            try:
                return json.loads(response_text)
            except:
                return {
                    "insights": [response_text],
                    "key_points": [],
                    "action_items": []
                }
        except Exception as e:
            raise Exception(f"Insight extraction failed: {str(e)}")
    
    async def generate_summary_gemini(self, transcript: str) -> Dict:
        """Generate summary using Gemini (alternative to GPT-4o)"""
        if not self.client:
            return {
                "short_summary": "[DEMO] Add GEMINI_API_KEY for Gemini summaries",
                "detailed_summary": []
            }
        
        prompt = f"""Summarize this meeting transcript:
1. Provide a 1-sentence short summary
2. Provide 3-6 detailed bullet points covering decisions, tasks, and risks

Return JSON: {{"short_summary": "...", "detailed_summary": ["...", "..."]}}

Transcript:
{transcript}"""

        try:
            response_text = self.generate_content(prompt)
            try:
                return json.loads(response_text)
            except:
                return {
                    "short_summary": response_text[:200],
                    "detailed_summary": [response_text]
                }
        except Exception as e:
            raise Exception(f"Summary generation failed: {str(e)}")

