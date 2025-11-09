import openai
import google.generativeai as genai
from typing import Dict, Any, Optional, List
import base64
from pathlib import Path
import json
import asyncio
import os

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
        """Analyze a single batch of frames with robust error handling"""
        try:
            # Build content with simple, clear prompt
            content = [
                {
                    "type": "text", 
                    "text": f"""Analyze these {len(batch)} video frames in order. Return ONLY a JSON array with {len(batch)} objects:

[{{"description":"what you see", "scene_type":"meeting", "has_people":true, "objects":["person","computer"]}}, {{"description":"next frame", "scene_type":"presentation", "has_people":false, "objects":["slide","text"]}}]

Return valid JSON only, no other text."""
                }
            ]
            
            # Add images with error checking
            for i, frame in enumerate(batch):
                try:
                    if not os.path.exists(frame["path"]):
                        print(f"❌ Frame file not found: {frame['path']}")
                        continue
                        
                    with open(frame["path"], "rb") as image_file:
                        image_data = image_file.read()
                        if len(image_data) == 0:
                            print(f"❌ Empty image file: {frame['path']}")
                            continue
                            
                        base64_image = base64.b64encode(image_data).decode('utf-8')
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low"  # Use low detail for faster processing
                            }
                        })
                        print(f"✅ Added frame {i+1}/{len(batch)} to batch (size: {len(image_data)} bytes)")
                except Exception as e:
                    print(f"❌ Failed to process frame {frame['path']}: {e}")
                    continue
            
            if len(content) == 1:  # Only text, no images loaded
                print("❌ No valid images in batch")
                return []
                
            print(f"🔍 Sending {len(content)-1} images to GPT-4o Vision...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                max_tokens=1000,
                temperature=0.0  # Zero temperature for consistent results
            )
            
            response_content = response.choices[0].message.content
            print(f"📝 GPT-4o Vision response: {response_content[:200]}...")
            
            if not response_content or response_content.strip() == "":
                print("❌ Empty response from GPT-4o Vision")
                return []
            
            # Clean and parse JSON
            json_text = response_content.strip()
            if json_text.startswith("```json"):
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif json_text.startswith("```"):
                json_text = json_text.split("```")[1].split("```")[0].strip()
                
            batch_results = json.loads(json_text)
            
            if not isinstance(batch_results, list):
                print(f"❌ Expected list, got {type(batch_results)}")
                return []
            
            print(f"✅ Successfully parsed {len(batch_results)} results")
            
            # Add metadata safely
            for j, result in enumerate(batch_results):
                if j < len(batch):
                    result["timestamp"] = batch[j]["timestamp"]
                    result["frame_number"] = batch[j]["number"]
                    result["path"] = batch[j]["path"]
                    result["analyzer"] = "gpt-4o-vision-batch"
            
            return batch_results
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"Raw response: {response_content if 'response_content' in locals() else 'No response'}")
            return []
        except Exception as e:
            print(f"❌ Batch analysis failed: {e}")
            return []
    
    async def analyze_batch(self, frames: List[Dict[str, Any]], max_frames_per_request: int = 6) -> List[Dict[str, Any]]:
        """
        Analyze multiple frames with ROBUST error handling and fallbacks
        ULTRA-RELIABLE: Multiple fallback strategies
        """
        if not self.client:
            print("❌ OpenAI API key not configured")
            return [{"error": "OpenAI API key not configured"} for _ in frames]
        
        print(f"🎞️ Starting GPT-4o Vision analysis for {len(frames)} frames")
        
        # STRATEGY 1: Try small batch processing first (most reliable)
        try:
            batch_size = min(4, len(frames))  # Very small batches for reliability
            print(f"📊 Strategy 1: Small batch processing (batch_size={batch_size})")
            
            if len(frames) <= batch_size:
                # Single small batch
                results = await self._analyze_single_batch(frames)
                if results and len(results) > 0:
                    print(f"✅ Batch processing successful: {len(results)} results")
                    return results
                else:
                    print("⚠️ Batch processing returned empty results")
            else:
                # Multiple small batches
                all_results = []
                for i in range(0, len(frames), batch_size):
                    batch = frames[i:i + batch_size]
                    print(f"🔍 Processing batch {i//batch_size + 1}/{(len(frames) + batch_size - 1)//batch_size}")
                    
                    batch_results = await self._analyze_single_batch(batch)
                    if batch_results:
                        all_results.extend(batch_results)
                    else:
                        print(f"⚠️ Batch {i//batch_size + 1} failed, continuing...")
                
                if all_results and len(all_results) > 0:
                    print(f"✅ Multi-batch processing successful: {len(all_results)} results")
                    return all_results
                    
        except Exception as e:
            print(f"❌ Strategy 1 (batch) failed: {e}")
        
        # STRATEGY 2: Fallback to sequential processing
        print("🔄 Strategy 2: Sequential processing fallback")
        try:
            results = await self._fallback_sequential_analysis(frames)
            if results and len(results) > 0:
                print(f"✅ Sequential processing successful: {len(results)} results")
                return results
        except Exception as e:
            print(f"❌ Strategy 2 (sequential) failed: {e}")
        
        # STRATEGY 3: Last resort - create minimal results
        print("🆘 Strategy 3: Creating minimal fallback results")
        fallback_results = []
        for frame in frames[:5]:  # Limit to first 5 frames
            fallback_results.append({
                "timestamp": frame["timestamp"],
                "frame_number": frame["number"],
                "path": frame["path"],
                "description": "Frame analysis unavailable - GPT-4o Vision processing failed",
                "scene_type": "other",
                "has_people": False,
                "objects": [],
                "analyzer": "fallback-minimal",
                "error": "Vision analysis failed - check API key and quota"
            })
        
        print(f"⚠️ Using minimal fallback: {len(fallback_results)} results")
        return fallback_results
    
    async def _fallback_sequential_analysis(self, frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback to sequential analysis if batch processing fails"""
        print(f"🔄 Falling back to sequential analysis for {len(frames)} frames...")
        results = []
        
        # Process frames one by one with simpler analysis
        for i, frame in enumerate(frames[:8]):  # Limit to 8 frames for speed
            try:
                print(f"🔍 Analyzing frame {i+1}/{min(len(frames), 8)} sequentially...")
                
                # Simple individual frame analysis
                with open(frame["path"], "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Describe what you see in this video frame. Return JSON: {\"description\":\"what you see\", \"scene_type\":\"meeting|presentation|other\", \"has_people\":true|false, \"objects\":[\"list\",\"of\",\"objects\"]}"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                        "detail": "low"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=200,
                    temperature=0.0
                )
                
                content = response.choices[0].message.content
                if content:
                    # Parse JSON from response
                    try:
                        if content.startswith("```json"):
                            content = content.split("```json")[1].split("```")[0].strip()
                        elif content.startswith("```"):
                            content = content.split("```")[1].split("```")[0].strip()
                            
                        result = json.loads(content)
                        result["timestamp"] = frame["timestamp"]
                        result["frame_number"] = frame["number"]
                        result["path"] = frame["path"]
                        result["analyzer"] = "gpt-4o-vision-sequential"
                        results.append(result)
                        print(f"✅ Frame {i+1} analyzed: {result.get('description', 'N/A')[:50]}...")
                    except json.JSONDecodeError:
                        # Fallback: use raw text as description
                        results.append({
                            "timestamp": frame["timestamp"],
                            "frame_number": frame["number"],
                            "path": frame["path"],
                            "description": content[:100],
                            "scene_type": "other",
                            "has_people": False,
                            "objects": [],
                            "analyzer": "gpt-4o-vision-text-fallback"
                        })
                        print(f"⚠️ Frame {i+1} used text fallback")
                else:
                    results.append({
                        "timestamp": frame["timestamp"],
                        "frame_number": frame["number"],
                        "error": "Empty response from GPT-4o Vision"
                    })
                    
            except Exception as e:
                print(f"❌ Sequential analysis failed for frame {frame['number']}: {e}")
                results.append({
                    "timestamp": frame["timestamp"],
                    "frame_number": frame["number"],
                    "error": str(e)
                })
                
        print(f"✅ Sequential analysis complete: {len(results)} results")
        return results


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
        
        else:  # "detailed" or any other mode - always use GPT-4o only
            # Use GPT-4o Vision with optimized batching
            print(f"🔍 Analyzing {len(frames)} frames with GPT-4o Vision ONLY (no Gemini)")
            return await self.gpt4o.analyze_batch(frames, max_frames_per_request=12)

