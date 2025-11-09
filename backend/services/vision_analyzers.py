import openai
import google.generativeai as genai
from typing import Dict, Any, Optional, List
import base64
from pathlib import Path
import json
import asyncio

class GPT4oVisionAnalyzer:
    """OpenAI GPT-4o Vision analyzer - best for OCR and detailed reasoning"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key) if api_key and api_key != "your_openai_api_key_here" else None
        self.model = "gpt-4o"
    
    async def analyze(self, frame_path: str, timestamp: float, frame_number: int) -> Dict[str, Any]:
        """
        Analyze a single frame using GPT-4o Vision
        
        Returns structured data about what's in the frame
        """
        if not self.client:
            return {
                "timestamp": timestamp,
                "frame_number": frame_number,
                "error": "OpenAI API key not configured"
            }
        
        try:
            # Encode image to base64
            with open(frame_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create analysis prompt
            prompt = """
            Analyze this video frame and return a JSON object with:
            {
              "description": "Brief description of what's shown (1-2 sentences)",
              "people_count": number of people visible,
              "emotions": ["emotion1", "emotion2"] if faces visible, else [],
              "dominant_emotion": "most prominent emotion" or "none",
              "objects": ["object1", "object2", ...] - key objects/items visible,
              "scene_type": "presentation|meeting|lecture|interview|other",
              "has_text": true/false - is there readable text?,
              "ocr_text": "extracted text content" if has_text, else "",
              "slide_number": number if it's a presentation slide, else null,
              "scene_change": true if this looks like a major scene change, else false,
              "confidence": 0-1 score for analysis quality
            }
            
            Focus on factual observations. Extract ALL readable text if present (slides, captions, etc.).
            Return ONLY valid JSON, no markdown formatting.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"  # High detail for better OCR
                                }
                            }
                        ]
                    }
                ],
                max_tokens=800,
                temperature=0.1  # Low temperature for factual analysis
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to extract JSON (handle markdown formatting)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            # Add metadata
            result["timestamp"] = timestamp
            result["frame_number"] = frame_number
            result["path"] = frame_path
            result["analyzer"] = "gpt-4o-vision"
            result["faces_count"] = result.get("people_count", 0)
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse GPT-4o Vision response as JSON: {e}")
            print(f"Raw response: {content[:200]}...")
            return {
                "timestamp": timestamp,
                "frame_number": frame_number,
                "error": "JSON parse error",
                "raw_response": content[:200]
            }
        except Exception as e:
            print(f"GPT-4o Vision analysis failed for frame {frame_number}: {e}")
            return {
                "timestamp": timestamp,
                "frame_number": frame_number,
                "error": str(e)
            }
    
    async def _analyze_single_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze a single batch of frames"""
        content = [
            {
                "type": "text", 
                "text": f"""Analyze these {len(batch)} video frames. Return JSON array:
[{{"description":"brief scene description", "scene_type":"presentation|meeting|interview|other", "has_people":true/false, "has_text":true/false, "ocr_text":"any visible text", "objects":["key objects"]}}]
Be concise but accurate."""
            }
        ]
        
        # Add images
        for frame in batch:
            with open(frame["path"], "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            max_tokens=800,
            temperature=0.1
        )
        
        batch_results = json.loads(response.choices[0].message.content)
        
        # Add metadata
        for j, result in enumerate(batch_results):
            result["timestamp"] = batch[j]["timestamp"]
            result["frame_number"] = batch[j]["number"]
            result["path"] = batch[j]["path"]
        
        return batch_results
    
    async def analyze_batch(self, frames: List[Dict[str, Any]], max_frames_per_request: int = 20) -> List[Dict[str, Any]]:
        """
        Analyze multiple frames in PARALLEL batches for maximum speed
        """
        if not self.client:
            return [{"error": "OpenAI API key not configured"} for _ in frames]
        
        # Create tasks for parallel processing
        tasks = []
        for i in range(0, len(frames), max_frames_per_request):
            batch = frames[i:i + max_frames_per_request]
            tasks.append(asyncio.create_task(self._analyze_single_batch(batch)))
        
        # Process all batches in parallel
        try:
            batch_results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Flatten results
            results = []
            for batch_results in batch_results_list:
                if isinstance(batch_results, Exception):
                    print(f"Batch failed: {batch_results}")
                    continue
                results.extend(batch_results)
            
            return results
            
        except Exception as e:
            print(f"Parallel batch analysis failed: {e}")
            return []


class GeminiFlashVisionAnalyzer:
    """Google Gemini 1.5 Flash analyzer - fast and cheap for high-frequency OCR"""
    
    def __init__(self, api_key: str):
        if api_key and api_key != "your_gemini_api_key_here":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.model = None
            self.enabled = False
    
    async def analyze(self, frame_path: str, timestamp: float, frame_number: int) -> Dict[str, Any]:
        """
        Ultra-fast frame analysis - minimal processing
        """
        if not self.enabled:
            return {
                "timestamp": timestamp,
                "frame_number": frame_number,
                "error": "Gemini API key not configured"
            }
        
        try:
            # Load and resize image aggressively for speed
            from PIL import Image
            img = Image.open(frame_path)
            img.thumbnail((256, 256))  # Very small for speed
            
            # Minimal prompt for maximum speed
            prompt = """Return JSON only: {"scene": "presentation|meeting|screen|other", "has_text": true/false, "objects": ["person", "screen", "text"]}"""
            
            response = self.model.generate_content(
                [prompt, img],
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                    max_output_tokens=100,  # Much smaller for speed
                )
            )
            
            # Parse response
            content = response.text
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            # Add metadata with simplified structure
            return {
                "timestamp": timestamp,
                "frame_number": frame_number,
                "scene_type": result.get("scene", "other"),
                "has_text": result.get("has_text", False),
                "objects": result.get("objects", []),
                "analyzer": "gemini-flash-ultra"
            }
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse Gemini response as JSON: {e}")
            return {
                "timestamp": timestamp,
                "frame_number": frame_number,
                "error": "JSON parse error",
                "raw_response": content[:200] if 'content' in locals() else ""
            }
        except Exception as e:
            print(f"Gemini Flash analysis failed for frame {frame_number}: {e}")
            return {
                "timestamp": timestamp,
                "frame_number": frame_number,
                "error": str(e)
            }
    
    async def analyze_batch(self, frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple frames (Gemini can handle video input natively, but we'll use sequential for now)
        """
        if not self.enabled:
            return [{"error": "Gemini API key not configured"} for _ in frames]
        
        results = []
        for frame in frames:
            result = await self.analyze(frame["path"], frame["timestamp"], frame["number"])
            results.append(result)
        
        return results


class HybridVisionAnalyzer:
    """
    Hybrid analyzer that uses both GPT-4o and Gemini intelligently:
    - GPT-4o for key frames (detailed analysis, emotion detection)
    - Gemini Flash for all frames (fast OCR, scene detection)
    """
    
    def __init__(self, openai_key: str, gemini_key: str):
        self.gpt4o = GPT4oVisionAnalyzer(openai_key)
        self.gemini = GeminiFlashVisionAnalyzer(gemini_key)
    
    async def analyze_video_frames(
        self, 
        frames: List[Dict[str, Any]], 
        mode: str = "balanced"
    ) -> List[Dict[str, Any]]:
        """
        Analyze video frames using hybrid approach
        
        Args:
            frames: List of frame metadata
            mode: "fast" (Gemini only), "detailed" (GPT-4o only), "balanced" (both strategically)
            
        Returns:
            List of analysis results with combined insights
        """
        
        if mode == "fast":
            # Use only Gemini for speed
            print(f"🚀 Fast mode: Analyzing {len(frames)} frames with Gemini Flash")
            return await self.gemini.analyze_batch(frames)
        
        elif mode == "detailed":
            # Use GPT-4o Vision with MAX BATCHING for speed + quality
            print(f"🔍 Detailed mode: Analyzing {len(frames)} frames with GPT-4o Vision (batched, 20 per call)")
            return await self.gpt4o.analyze_batch(frames, max_frames_per_request=20)
        
        else:  # balanced - DISABLED, use detailed instead
            print(f"🔍 Using detailed mode for quality analysis")
            return await self.analyze_video_frames(frames, mode="detailed")

