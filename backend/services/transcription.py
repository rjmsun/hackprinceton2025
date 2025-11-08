import openai
from typing import Optional
import io

class TranscriptionService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key) if api_key and api_key != "your_openai_api_key_here" else None
        self.stream_buffer = []
    
    async def transcribe_file(self, audio_data: bytes, filename: str) -> str:
        """Transcribe uploaded audio file using Whisper"""
        if not self.client:
            return "[DEMO MODE] Transcription placeholder - add OPENAI_API_KEY to .env"
        
        try:
            audio_file = io.BytesIO(audio_data)
            audio_file.name = filename
            
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            
            return transcript
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    async def transcribe_stream(self, audio_chunk: bytes) -> Optional[str]:
        """
        Stream transcription - for real-time processing
        In production, you'd use OpenAI Realtime API
        For MVP, we accumulate and transcribe periodically
        """
        self.stream_buffer.append(audio_chunk)
        
        # Every ~3 seconds of audio (arbitrary threshold)
        if len(self.stream_buffer) > 30:
            combined = b''.join(self.stream_buffer)
            self.stream_buffer = []
            
            try:
                # Create temp file-like object
                audio_file = io.BytesIO(combined)
                audio_file.name = "stream.wav"
                
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
                
                return transcript
            except:
                return None
        
        return None

