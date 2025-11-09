import os
import uuid
import subprocess
import shutil
import base64
from pathlib import Path
from typing import List, Dict, Any, Protocol, Optional
import asyncio
from PIL import Image
import io

class FrameAnalyzer(Protocol):
    """Protocol for pluggable frame analyzers"""
    async def analyze(self, frame_path: str, timestamp: float, frame_number: int) -> Dict[str, Any]:
        """Analyze a single frame and return structured results"""
        ...

class VideoProcessor:
    def __init__(self, temp_dir: str = "/tmp/eve_video"):
        self.temp_dir = temp_dir
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
    
    def extract_frames(self, video_path: str, fps: float = 0.2, max_dimension: int = 256) -> List[Dict[str, Any]]:
        """
        Extract keyframes from video using ffmpeg
        
        Args:
            video_path: Path to input video file
            fps: Frames per second to extract (default 1 = 1 frame/second)
            max_dimension: Maximum width/height for extracted frames (saves API costs)
            
        Returns:
            List of dicts with frame info: {"path": str, "timestamp": float, "number": int}
        """
        session_id = str(uuid.uuid4())
        output_dir = os.path.join(self.temp_dir, session_id)
        os.makedirs(output_dir, exist_ok=True)
        
        output_pattern = os.path.join(output_dir, "frame_%04d.png")
        
        # ffmpeg command to extract frames at specified fps
        # -vf fps=1 means 1 frame per second
        # scale filter maintains aspect ratio
        # Use the simplest possible command that works
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"fps={fps}",
            "-y",  # Overwrite existing files
            output_pattern
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 min timeout
            )
            
            print(f"ffmpeg command: {' '.join(cmd)}")
            print(f"ffmpeg stdout: {result.stdout}")
            print(f"ffmpeg stderr: {result.stderr}")
            
            if result.returncode != 0:
                print(f"ffmpeg error (return code {result.returncode}): {result.stderr}")
                if "not found" in result.stderr.lower() or "no such file" in result.stderr.lower():
                    raise Exception("ffmpeg not installed. Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)")
                raise Exception(f"Frame extraction failed: {result.stderr}")
            
            # Get list of extracted frames
            frames = []
            for i, frame_file in enumerate(sorted(Path(output_dir).glob("frame_*.png"))):
                timestamp = i / fps  # Calculate timestamp based on fps
                frames.append({
                    "path": str(frame_file),
                    "timestamp": timestamp,
                    "number": i + 1,
                    "session_id": session_id
                })
            
            print(f"✅ Extracted {len(frames)} frames from video (fps={fps})")
            return frames
            
        except subprocess.TimeoutExpired:
            raise Exception("Video processing timed out (>5 minutes)")
        except FileNotFoundError:
            raise Exception("ffmpeg not found. Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)")
        except Exception as e:
            # Cleanup on error
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            raise Exception(f"Frame extraction failed: {str(e)}")
    
    def extract_audio(self, video_path: str) -> str:
        """
        Extract audio track from video to temporary file
        
        Returns:
            Path to extracted audio file (WAV format)
        """
        session_id = str(uuid.uuid4())
        audio_path = os.path.join(self.temp_dir, f"{session_id}_audio.wav")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # WAV format
            "-ar", "16000",  # 16kHz sample rate (good for Whisper)
            "-ac", "1",  # Mono
            audio_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                raise Exception(f"Audio extraction failed: {result.stderr}")
            
            print(f"✅ Extracted audio from video: {audio_path}")
            return audio_path
            
        except Exception as e:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            raise Exception(f"Audio extraction failed: {str(e)}")
    
    def cleanup_session(self, session_id: str):
        """Clean up temporary files for a session"""
        session_dir = os.path.join(self.temp_dir, session_id)
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
            print(f"🧹 Cleaned up session: {session_id}")
    
    def cleanup_audio(self, audio_path: str):
        """Clean up extracted audio file"""
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"🧹 Cleaned up audio: {audio_path}")
    
    @staticmethod
    def get_video_duration(video_path: str) -> float:
        """Get video duration in seconds"""
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip())
        except:
            return 0.0
    
    @staticmethod
    def is_video_file(filename: str) -> bool:
        """Check if file is a video"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v'}
        return Path(filename).suffix.lower() in video_extensions
    
    @staticmethod
    def encode_image_to_base64(image_path: str, max_size: int = 256) -> str:
        """
        Load image and encode to base64 as JPEG for speed
        
        Args:
            image_path: Path to image file
            max_size: Maximum dimension (resize if larger)
            
        Returns:
            Base64 encoded image string
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed (remove alpha channel)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize aggressively for speed
                if max(img.size) > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Save as JPEG with quality 75 for smaller file size
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=75, optimize=True)
                img_bytes = buffer.getvalue()
                
                # Encode to base64
                return base64.b64encode(img_bytes).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to encode image: {str(e)}")


class VideoAnalysisAggregator:
    """Aggregates frame-level analysis into high-level insights"""
    
    @staticmethod
    def aggregate_frame_results(frame_results: List[Dict[str, Any]], transcript: str = "") -> Dict[str, Any]:
        """
        Aggregate frame analysis results into summary
        
        Args:
            frame_results: List of per-frame analysis results
            transcript: Optional audio transcript for cross-modal analysis
            
        Returns:
            Aggregated video summary
        """
        if not frame_results:
            return {
                "total_frames": 0,
                "duration": 0,
                "key_scenes": [],
                "emotions_timeline": [],
                "slide_changes": [],
                "summary": "No video data analyzed"
            }
        
        # Extract key information
        total_frames = len(frame_results)
        duration = frame_results[-1].get("timestamp", 0) if frame_results else 0
        
        # Aggregate emotions (if present)
        emotions_timeline = []
        for frame in frame_results:
            if "emotions" in frame and "timestamp" in frame:
                emotions_timeline.append({
                    "timestamp": frame["timestamp"],
                    "emotions": frame["emotions"],
                    "dominant_emotion": frame.get("dominant_emotion", "neutral")
                })
        
        # Detect scene changes (look for significant content changes)
        scene_changes = []
        for i, frame in enumerate(frame_results):
            if "scene_change" in frame and frame["scene_change"] and "timestamp" in frame:
                scene_changes.append({
                    "timestamp": frame["timestamp"],
                    "description": frame.get("description", "Scene change detected"),
                    "thumbnail": frame.get("path", "")
                })
        
        # Extract slide text changes (OCR results that differ significantly)
        slide_changes = []
        prev_text = ""
        for frame in frame_results:
            if "timestamp" not in frame:
                continue
            curr_text = frame.get("ocr_text", "")
            # Significant change = >50% different
            if curr_text and len(curr_text) > 20:
                similarity = len(set(curr_text.split()) & set(prev_text.split())) / max(len(curr_text.split()), 1)
                if similarity < 0.5:
                    slide_changes.append({
                        "timestamp": frame["timestamp"],
                        "text": curr_text[:200],  # First 200 chars
                        "full_text": curr_text
                    })
                    prev_text = curr_text
        
        # Dynamic key scenes based on video duration - longer videos get more frames analyzed
        if duration <= 30:  # Short videos (≤30s)
            max_scenes = min(len(frame_results), 6)
        elif duration <= 120:  # Medium videos (≤2min)  
            max_scenes = min(len(frame_results), 9)
        elif duration <= 300:  # Long videos (≤5min)
            max_scenes = min(len(frame_results), 12)
        else:  # Very long videos (>5min)
            max_scenes = min(len(frame_results), 15)
        
        print(f"📊 Video duration: {duration:.1f}s → Using {max_scenes} key scenes from {len(frame_results)} total frames")
        
        key_scenes = []
        for i, frame in enumerate(frame_results[:max_scenes]):
            if "timestamp" not in frame:
                continue
            
            # Use the actual description from GPT-4o Vision, not generic labels
            description = frame.get("description", "")
            if not description or description == "":
                # Fallback to constructing from available data
                scene_type = frame.get("scene_type", "scene")
                objects = frame.get("objects", [])
                if objects:
                    description = f"{scene_type.capitalize()} with {', '.join(objects[:3])}"
                else:
                    description = f"{scene_type.capitalize()} view"
            
            # Count faces/people
            faces = frame.get("faces_count", 0) or frame.get("people_count", 0) or (1 if "person" in frame.get("objects", []) else 0)
            
            key_scenes.append({
                "timestamp": frame["timestamp"],
                "description": description,
                "importance": 2 if faces > 0 else 1,
                "details": {
                    "faces": faces,
                    "objects": frame.get("objects", []),
                    "text_preview": frame.get("ocr_text", "")[:100] if frame.get("has_text") else None
                }
            })
        
        # Generate visual-only summary from frame descriptions
        visual_summary = VideoAnalysisAggregator._generate_visual_summary(frame_results, key_scenes)
        
        return {
            "total_frames_analyzed": total_frames,
            "video_duration_seconds": duration,
            "key_scenes": key_scenes,  # Dynamic number based on video length
            "emotions_timeline": emotions_timeline,
            "slide_changes": slide_changes,
            "scene_changes": scene_changes,
            "has_slides": len(slide_changes) > 0,
            "has_faces": any(f.get("faces_count", 0) > 0 for f in frame_results),
            "visual_summary": visual_summary,
            "summary": f"Analyzed {total_frames} frames over {duration:.1f}s. "
                      f"Found {len(key_scenes)} key moments, {len(slide_changes)} slide changes, "
                      f"{len(emotions_timeline)} emotion readings."
        }
    
    @staticmethod
    def _generate_visual_summary(frame_results: List[Dict[str, Any]], key_scenes: List[Dict[str, Any]]) -> str:
        """
        Generate a brief visual-only summary from frame analysis
        This describes what the user appears to be doing based on visual content only
        """
        if not frame_results:
            return "No visual content analyzed"
        
        # Collect visual indicators
        scene_types = [f.get("scene_type", "") for f in frame_results if f.get("scene_type")]
        has_people = any(f.get("has_people", False) or f.get("faces_count", 0) > 0 for f in frame_results)
        objects_seen = []
        for f in frame_results:
            objects_seen.extend(f.get("objects", []))
        
        # Count unique objects
        unique_objects = list(set(objects_seen))
        common_objects = [obj for obj in unique_objects if objects_seen.count(obj) > len(frame_results) // 3]
        
        # Determine activity from scene types
        if not scene_types:
            activity = "viewing content"
        elif "presentation" in " ".join(scene_types).lower():
            activity = "presenting or viewing a presentation"
        elif "meeting" in " ".join(scene_types).lower():
            activity = "in a meeting or video call"
        elif "interview" in " ".join(scene_types).lower():
            activity = "in an interview"
        else:
            activity = "viewing or working with content"
        
        # Build summary
        summary_parts = []
        summary_parts.append(f"The user appears to be {activity}")
        
        if has_people:
            summary_parts.append("with one or more people visible")
        
        if common_objects:
            obj_str = ", ".join(common_objects[:3])
            summary_parts.append(f"Common elements include: {obj_str}")
        
        # Add visual descriptions from key scenes
        if key_scenes and len(key_scenes) > 0:
            desc = key_scenes[0].get("description", "")
            if desc and desc not in summary_parts[0]:
                summary_parts.append(f"Visually: {desc}")
        
        return ". ".join(summary_parts) + "."
    
    @staticmethod
    async def generate_narrative_summary(video_summary: Dict[str, Any], transcript: str, openai_client) -> str:
        """
        Use GPT-4o to generate a natural language summary combining video + audio
        
        Args:
            video_summary: Aggregated video analysis
            transcript: Audio transcript
            openai_client: OpenAI client instance
            
        Returns:
            Natural language summary
        """
        if not openai_client:
            return "Video analysis available, but narrative summary requires OpenAI API key"
        
        prompt = f"""
        You are analyzing a recorded video. Combine the visual and audio information to create a comprehensive summary.
        
        VIDEO ANALYSIS:
        - Duration: {video_summary.get('video_duration_seconds', 0):.1f} seconds
        - Key scenes: {len(video_summary.get('key_scenes', []))}
        - Slides detected: {video_summary.get('has_slides', False)}
        - People visible: {video_summary.get('has_faces', False)}
        - Emotions tracked: {len(video_summary.get('emotions_timeline', []))} readings
        
        SLIDE CONTENT (if any):
        {chr(10).join([f"[{s['timestamp']:.1f}s] {s['text']}" for s in video_summary.get('slide_changes', [])[:5]])}
        
        AUDIO TRANSCRIPT:
        {transcript[:1000]}...
        
        Create a 3-4 sentence summary that:
        1. Describes what was SHOWN in the video (slides, scenes, people)
        2. Cross-references with what was SAID in the audio
        3. Highlights any mismatches or interesting correlations
        4. Gives an overall quality assessment
        
        Be specific and actionable. Mention timestamps if relevant.
        """
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a video analysis expert. Provide clear, actionable summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Failed to generate narrative summary: {e}")
            return video_summary.get("summary", "Video analysis completed")

