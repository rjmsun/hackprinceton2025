import openai
import json
from typing import Dict, Any, Optional, List
import re

class InteractiveCoachingService:
    def __init__(self, openai_key: Optional[str] = None):
        self.client = openai.OpenAI(api_key=openai_key) if openai_key and openai_key != "your_openai_api_key_here" else None

    async def generate_interactive_scenarios(self, transcript: str, context: str, coaching_insights: Dict = None) -> Dict[str, Any]:
        """Generate interactive coaching scenarios based on context"""
        if not self.client:
            return {"error": "Interactive coaching service not configured"}
        
        if context == "interview":
            return await self._generate_interview_replay(transcript, coaching_insights)
        elif context == "lecture":
            return await self._generate_lecture_questions(transcript)
        elif context == "coffee_chat":
            return await self._generate_coffee_practice(transcript)
        
        return {} # No interactive coaching for general meetings

    async def _generate_interview_replay(self, transcript: str, coaching_insights: Dict = None) -> Dict[str, Any]:
        """Create interactive interview replay scenarios - like chess.com analysis"""
        
        # First, extract key Q&A moments
        moments = await self._extract_interview_moments(transcript)
        
        # Then, identify coaching opportunities
        coaching_opportunities = []
        if coaching_insights and coaching_insights.get("areas_for_improvement"):
            for improvement in coaching_insights["areas_for_improvement"]:
                # Find the moment that corresponds to this improvement
                original_quote = improvement.get("quote", "")
                matching_moment = self._find_matching_moment(original_quote, moments)
                if matching_moment:
                    coaching_opportunities.append({
                        "moment_id": matching_moment["id"],
                        "type": "improvement_opportunity",
                        "severity": "blunder" if "guess" in original_quote.lower() or "don't know" in original_quote.lower() else "inaccuracy",
                        "original_question": matching_moment["question"],
                        "original_answer": matching_moment["answer"],
                        "issue": improvement.get("quote"),
                        "coaching_tip": improvement.get("suggestion"),
                        "replay_prompt": f"Let's replay this question. Try to avoid: '{improvement.get('quote')}'. Here's the question again:"
                    })

        return {
            "type": "interview_replay",
            "moments": moments,
            "coaching_opportunities": coaching_opportunities,
            "replay_instructions": "Click 'Replay Question' to hear the interviewer ask again. Record your new response for instant feedback."
        }

    async def _extract_interview_moments(self, transcript: str) -> List[Dict]:
        """Extract Q&A pairs from interview transcript"""
        prompt = f"""
        Analyze this interview transcript and extract clear question-answer pairs.
        Focus on substantive interview questions (not small talk).
        
        Return JSON array of moments:
        {{
            "id": "unique_id",
            "question": "exact interviewer question",
            "answer": "exact interviewee response", 
            "topic": "brief topic (e.g., 'technical skills', 'behavioral')",
            "timestamp_hint": "rough position in conversation"
        }}
        
        Transcript:
        {transcript}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Extract clear Q&A pairs from interview transcripts. Return valid JSON array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content or "{}")
            return result.get("moments", [])
        except Exception as e:
            print(f"Error extracting interview moments: {e}")
            return []

    def _find_matching_moment(self, quote: str, moments: List[Dict]) -> Optional[Dict]:
        """Find which moment contains the problematic quote"""
        quote_words = set(quote.lower().split())
        best_match = None
        best_score = 0
        
        for moment in moments:
            answer_words = set(moment.get("answer", "").lower().split())
            overlap = len(quote_words.intersection(answer_words))
            if overlap > best_score and overlap > 1:  # At least 2 word overlap
                best_score = overlap
                best_match = moment
        
        return best_match

    async def _generate_lecture_questions(self, transcript: str) -> Dict[str, Any]:
        """Generate conceptual questions for lecture content"""
        prompt = f"""
        Based on this lecture transcript, generate 5-7 conceptual questions that test understanding.
        Mix question types: definitions, applications, comparisons, examples.
        
        Return JSON:
        {{
            "questions": [
                {{
                    "id": "q1", 
                    "question": "Can you explain [concept] in your own words?",
                    "topic": "concept understanding",
                    "difficulty": "basic|intermediate|advanced",
                    "expected_points": ["key point 1", "key point 2"]
                }}
            ]
        }}
        
        Lecture content:
        {transcript}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Generate thoughtful questions that test conceptual understanding. Return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content or "{}")
            
            return {
                "type": "lecture_practice",
                "questions": result.get("questions", []),
                "practice_instructions": "Answer each question verbally. The AI will provide feedback and explanations."
            }
        except Exception as e:
            return {"error": f"Failed to generate lecture questions: {str(e)}"}

    async def _generate_coffee_practice(self, transcript: str) -> Dict[str, Any]:
        """Generate networking conversation practice"""
        return {
            "type": "coffee_practice", 
            "scenarios": [
                {
                    "id": "follow_up",
                    "prompt": "Practice asking a thoughtful follow-up question based on what you learned.",
                    "context": "networking"
                }
            ]
        }

    async def provide_response_feedback(self, original_question: str, user_response: str, context: str, coaching_tip: str = "") -> Dict[str, Any]:
        """Analyze user's new response and provide immediate feedback"""
        if not self.client:
            return {"error": "Feedback service not configured"}

        prompt = f"""
        The user just re-answered an interview question. Provide immediate, actionable feedback.
        
        Original Question: "{original_question}"
        User's New Response: "{user_response}"
        Previous Coaching Tip: "{coaching_tip}"
        
        Analyze the response and return JSON:
        {{
            "overall_rating": "excellent|good|needs_improvement|poor",
            "improvements": ["What was better than before"],
            "still_needs_work": ["What still needs improvement"],
            "specific_feedback": "2-3 sentence detailed feedback",
            "voice_feedback": "Encouraging spoken feedback (1-2 sentences for TTS)"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an encouraging interview coach. Provide constructive, specific feedback that helps users improve."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content or "{}")
        except Exception as e:
            return {"error": f"Feedback generation failed: {str(e)}"}

    async def generate_conceptual_explanation(self, question: str, user_answer: str, topic: str) -> Dict[str, Any]:
        """Generate explanation for lecture questions"""
        if not self.client:
            return {"error": "Explanation service not configured"}

        prompt = f"""
        The student answered a conceptual question. Provide educational feedback.
        
        Question: "{question}"
        Student Answer: "{user_answer}"
        Topic: "{topic}"
        
        Return JSON:
        {{
            "understanding_level": "strong|partial|needs_work",
            "correct_points": ["What they got right"],
            "missing_points": ["Key concepts they missed"],
            "explanation": "Clear explanation of the concept",
            "follow_up_question": "Optional deeper question to test understanding"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a patient teacher. Provide clear explanations that build understanding."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content or "{}")
        except Exception as e:
            return {"error": f"Explanation generation failed: {str(e)}"}

    async def start_conversation_session(self, transcript: str, context: str, coaching_insights: Dict = None) -> Dict[str, Any]:
        """Start a new conversational practice session with initial greeting"""
        if not self.client:
            return {"error": "Conversation service not configured"}

        if context == "interview":
            return await self._start_interview_conversation(transcript, coaching_insights)
        elif context == "lecture":
            return await self._start_lecture_conversation(transcript)
        elif context == "coffee_chat":
            return await self._start_coffee_chat_conversation(transcript)
        else:
            return {"error": "Unsupported context for conversational practice"}

    async def _start_interview_conversation(self, transcript: str, coaching_insights: Dict = None) -> Dict[str, Any]:
        """Start interview practice conversation"""
        
        # Extract key moments from the original interview
        moments = await self._extract_interview_moments(transcript)
        
        # Find areas for improvement
        weak_points = []
        if coaching_insights and coaching_insights.get("areas_for_improvement"):
            weak_points = coaching_insights["areas_for_improvement"][:3]  # Top 3 issues
        
        # Generate opening message
        opening_prompt = f"""
        You are an AI interview coach. The user just finished a practice interview. 
        Start a friendly, conversational practice session to help them improve.
        
        Original interview had these key moments: {json.dumps(moments[:3])}
        Areas that need work: {json.dumps(weak_points)}
        
        Generate a warm opening that:
        1. Greets them conversationally
        2. Mentions 1-2 specific things they can work on
        3. Asks if they're ready to practice one of the tricky questions again
        
        Keep it natural, encouraging, and under 50 words. This will be spoken aloud via TTS.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a friendly, encouraging interview coach. Speak naturally and conversationally."},
                    {"role": "user", "content": opening_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            opening_message = response.choices[0].message.content.strip()
            
            return {
                "session_type": "interview_practice",
                "opening_message": opening_message,
                "conversation_history": [
                    {"role": "assistant", "content": opening_message}
                ],
                "context_data": {
                    "moments": moments,
                    "weak_points": weak_points,
                    "current_focus": weak_points[0] if weak_points else None
                }
            }
        except Exception as e:
            return {"error": f"Failed to start conversation: {str(e)}"}

    async def _start_lecture_conversation(self, transcript: str) -> Dict[str, Any]:
        """Start lecture study conversation"""
        
        opening_prompt = f"""
        You are an AI tutor. The student just finished watching/attending a lecture.
        Start a friendly study session to test their understanding.
        
        Lecture content preview: {transcript[:500]}...
        
        Generate a warm opening that:
        1. Greets them and acknowledges they want to study
        2. Offers to either: quiz them on concepts OR explain anything they found confusing
        3. Asks what they'd like to focus on
        
        Keep it natural, supportive, and under 50 words. This will be spoken aloud.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a patient, encouraging tutor. Speak naturally and make learning engaging."},
                    {"role": "user", "content": opening_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            opening_message = response.choices[0].message.content.strip()
            
            return {
                "session_type": "lecture_practice",
                "opening_message": opening_message,
                "conversation_history": [
                    {"role": "assistant", "content": opening_message}
                ],
                "context_data": {
                    "lecture_content": transcript
                }
            }
        except Exception as e:
            return {"error": f"Failed to start conversation: {str(e)}"}

    async def _start_coffee_chat_conversation(self, transcript: str) -> Dict[str, Any]:
        """Start networking practice conversation"""
        
        opening_prompt = f"""
        You are an AI networking coach. The user just had a coffee chat.
        Start a friendly practice session to help them improve their networking skills.
        
        Coffee chat summary: {transcript[:500]}...
        
        Generate a warm opening that:
        1. Asks how the chat went
        2. Offers to practice follow-up questions or conversation skills
        3. Keeps it casual and encouraging
        
        Keep it natural and under 50 words. This will be spoken aloud.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a friendly networking coach. Keep it casual and conversational."},
                    {"role": "user", "content": opening_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            opening_message = response.choices[0].message.content.strip()
            
            return {
                "session_type": "networking_practice",
                "opening_message": opening_message,
                "conversation_history": [
                    {"role": "assistant", "content": opening_message}
                ],
                "context_data": {
                    "chat_content": transcript
                }
            }
        except Exception as e:
            return {"error": f"Failed to start conversation: {str(e)}"}

    async def continue_conversation(self, user_message: str, conversation_history: List[Dict], context_data: Dict, session_type: str) -> Dict[str, Any]:
        """Continue the conversational practice with user's response"""
        if not self.client:
            return {"error": "Conversation service not configured"}

        # Add user message to history
        conversation_history.append({"role": "user", "content": user_message})
        
        # Build context-aware system prompt
        if session_type == "interview_practice":
            system_prompt = f"""You are an AI interview coach having a natural conversation.
            
Context: The user is practicing for interviews. Focus areas: {json.dumps(context_data.get('weak_points', []))}

Your role:
- Have a natural back-and-forth conversation
- Ask one interview question at a time
- Provide brief, encouraging feedback on their answers
- Point out improvements and what to work on
- Use "you" and "I" naturally (e.g., "I noticed you...", "try this...")
- Keep responses concise (2-3 sentences) since they'll be spoken aloud
- After feedback, either ask a follow-up or move to the next topic

Be conversational, not robotic. This is practice, not an exam."""

        elif session_type == "lecture_practice":
            system_prompt = f"""You are an AI tutor having a natural study conversation.

Your role:
- Test understanding with questions
- Explain concepts they're confused about
- Provide examples to clarify
- Encourage curiosity
- Keep responses conversational and concise (2-4 sentences)
- Build on their answers - if they're partly right, acknowledge it and add details

Be supportive and make learning feel like a conversation with a study buddy."""

        else:  # networking_practice
            system_prompt = f"""You are an AI networking coach having a casual conversation.

Your role:
- Practice networking conversation skills
- Suggest better ways to ask questions or follow up
- Keep it light and encouraging
- Responses should be brief and conversational (2-3 sentences)
- Help them sound more natural and engaging

Be friendly and casual, like chatting with a mentor."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *conversation_history
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            assistant_message = response.choices[0].message.content.strip()
            conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return {
                "assistant_message": assistant_message,
                "conversation_history": conversation_history,
                "continue": True  # Session can continue
            }
            
        except Exception as e:
            return {"error": f"Conversation failed: {str(e)}"}
