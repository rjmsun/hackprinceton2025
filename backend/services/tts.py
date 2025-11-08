import httpx
from typing import Optional

class TTSService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        # Default voice ID (Rachel)
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"
    
    async def text_to_speech(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """Convert text to speech using ElevenLabs"""
        if not self.api_key or self.api_key == "your_elevenlabs_api_key_here" or not self.api_key.startswith(("eleven_", "sk-")):
            # Fallback for demo without API key
            return b"[DEMO MODE] Add ELEVENLABS_API_KEY for voice synthesis"
        
        voice = voice_id or self.voice_id
        
        url = f"{self.base_url}/text-to-speech/{voice}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers, timeout=30.0)
                
                if response.status_code == 200:
                    return response.content
                else:
                    raise Exception(f"TTS failed: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"TTS request failed: {str(e)}")

