import openai
from typing import Dict, Any, List, Optional, Tuple
import math
import json


class CoffeeChatService:
	def __init__(self, openai_key: Optional[str]):
		self.client = openai.OpenAI(api_key=openai_key) if openai_key else None

	def _chat_json(self, system: str, user: str, max_tokens: int = 1200) -> Dict[str, Any]:
		if not self.client:
			return {}
		resp = self.client.chat.completions.create(
			model="gpt-4o",
			messages=[
				{"role": "system", "content": system},
				{"role": "user", "content": user},
			],
			temperature=0.0,
			max_tokens=max_tokens,
			response_format={"type": "json_object"},
		)
		content = resp.choices[0].message.content
		return json.loads(content) if content else {}

	def extract_tips_and_followups(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
		"""Extract tips, follow-ups, and content evidence from cleaned sections JSON."""
		if not self.client:
			return {"tips": [], "follow_ups": [], "content_evidence": []}
		system = (
			"You are EVE, an assistant that extracts tasks, career/school tips, and follow-ups from a cleaned transcript JSON. "
			"Return only valid JSON with keys tips, follow_ups, content_evidence."
		)
		user = (
			"Input: " + json.dumps(sections, ensure_ascii=False) +
			"\nFor each section, identify: tips (text, category, confidence), follow_ups (text, method, confidence), and content_evidence (quote text + who/time if present).\n"
			"Schema: {\"tips\":[{\"id\":\"tip1\",\"text\":\"...\",\"category\":\"courses|internships|skills|people|career\",\"confidence\":0.0}],\n"
			"\"follow_ups\":[{\"id\":\"f1\",\"text\":\"...\",\"method\":\"email|linkedin|other\",\"confidence\":0.0}],\n"
			"\"content_evidence\":[{\"text\":\"...\",\"span\":\"Speaker A - 00:12:00\"}]}\n"
		)
		return self._chat_json(system, user, max_tokens=1200)

	def compute_content_score(self, tips: List[Dict[str, Any]], follow_ups: List[Dict[str, Any]], evidence: List[Dict[str, Any]]) -> float:
		if not tips and not follow_ups:
			return 0.2
		# average confidence where available
		conf_vals: List[float] = []
		for t in tips:
			if isinstance(t.get("confidence"), (int, float)):
				conf_vals.append(float(t["confidence"]))
		for f in follow_ups:
			if isinstance(f.get("confidence"), (int, float)):
				conf_vals.append(float(f["confidence"]))
		base = sum(conf_vals) / len(conf_vals) if conf_vals else 0.6
		boost = min(0.2, 0.05 * len(evidence))
		return max(0.0, min(1.0, base + boost))

	def combine_vibe(self, vision: Optional[Dict[str, Any]], audio: Optional[Dict[str, Any]], content_score: float) -> Dict[str, Any]:
		v = float(vision.get("vision_friendliness", vision.get("smile_confidence", 0.0))) if vision else 0.0
		# eye contact can slightly boost
		if vision and isinstance(vision.get("eye_contact_confidence"), (int, float)):
			v = (v * 0.8) + (float(vision["eye_contact_confidence"]) * 0.2)
		a = 0.0
		if audio:
			if isinstance(audio.get("sentiment"), (int, float)):
				a = float(audio["sentiment"])  # expected 0-1
			else:
				# heuristic from energy (0-1)
				a = float(audio.get("energy", 0.0))
		c = max(0.0, min(1.0, content_score))
		score = 0.4 * v + 0.35 * a + 0.25 * c
		label = "Great" if score >= 0.75 else ("Solid" if score >= 0.5 else "Caution")
		return {
			"vibe_score": round(score, 2),
			"vibe_label": label,
			"components": {"vision": round(v, 2), "audio": round(a, 2), "content": round(c, 2)}
		}

	def generate_coaching_and_spoken(self, tasks: List[Dict[str, Any]], tips: List[Dict[str, Any]], vibe_label: str) -> Dict[str, Any]:
		if not self.client:
			return {"spoken": "", "coaching": []}
		system = "You are EVE, a friendly assistant. Return JSON with keys spoken and coaching (2 items)."
		user = (
			"Inputs:\n- tasks: " + json.dumps(tasks, ensure_ascii=False) +
			"\n- tips: " + json.dumps(tips, ensure_ascii=False) +
			f"\n- vibe_label: {vibe_label}\n\nProduce a short spoken confirmation (1-2 sentences) and 2 bullet coaching suggestions. Return JSON {{\"spoken\":\"...\",\"coaching\":[\"...\",\"...\"]}}."
		)
		return self._chat_json(system, user, max_tokens=300)

	def draft_followup_email(self, person_name: Optional[str], company: Optional[str], highlights: List[str], ask: Optional[str], vibe_label: str) -> Dict[str, Any]:
		if not self.client:
			return {"email_subject": "", "email_body": ""}
		system = "You draft concise professional follow-up emails (4-6 sentences). Return JSON with email_subject and email_body."
		payload = {
			"person_name": person_name or "",
			"company": company or "",
			"highlights": highlights[:3],
			"ask": ask or "",
			"vibe_label": vibe_label,
		}
		user = (
			"Inputs: " + json.dumps(payload, ensure_ascii=False) +
			"\nReturn JSON with keys email_subject and email_body (no placeholders)."
		)
		return self._chat_json(system, user, max_tokens=400)
