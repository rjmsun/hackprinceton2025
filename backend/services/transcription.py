import openai
from typing import Optional
import io

class TranscriptionService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key) if api_key and api_key != "your_openai_api_key_here" else None
        self.stream_buffer = []
    
    async def transcribe_file_obj(self, file_obj, filename: str) -> str:
        """Transcribe using a file-like object to support large uploads without loading into memory."""
        if not self.client:
            return "[DEMO MODE] Transcription placeholder - add OPENAI_API_KEY to .env"
        try:
            # Ensure file is at the beginning
            file_obj.seek(0)
            
            # Read the file data into bytes for OpenAI SDK compatibility
            audio_data = file_obj.read()
            
            # Create BytesIO object with proper name attribute
            audio_file = io.BytesIO(audio_data)
            audio_file.name = filename or "audio.webm"
            
            print(f"Transcribing file: {filename}, size: {len(audio_data)} bytes")
            
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            return transcript
        except Exception as e:
            error_msg = str(e)
            print(f"Transcription error for {filename}: {error_msg}")
            raise Exception(f"Transcription failed: {error_msg}")
    
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
    
    async def validate_and_enhance_transcript(self, transcript: str) -> str:
        """Fact-check and enhance transcript using GPT-4o"""
        if not self.client:
            return transcript
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a transcript validator. Check for transcription errors, fix obvious mistakes (e.g., 'CS214' not 'see 214'), correct technical terms, and improve clarity while preserving the original meaning. Return only the corrected transcript text."},
                    {"role": "user", "content": f"Review and correct this transcript:\n\n{transcript}"}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            enhanced = response.choices[0].message.content
            return enhanced if enhanced else transcript
        except Exception as e:
            # If validation fails, return original
            return transcript
    
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

