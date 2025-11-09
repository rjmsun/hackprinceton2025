import boto3
import json
import os
import requests
from typing import Dict, Any, Optional

class VibeService:
    def __init__(self):
        # Try bearer token first (new method)
        self.bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        # Fallback to standard AWS credentials
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        if self.bearer_token and "YOUR_AWS" not in self.bearer_token:
            # Use bearer token authentication
            self.client = None
            self.use_bearer_token = True
            print("✅ Using AWS Bedrock Bearer Token authentication")
        elif aws_access_key_id and aws_secret_access_key and "YOUR_AWS" not in aws_access_key_id:
            # Use standard boto3 credentials
            try:
                self.client = boto3.client(
                    'bedrock-runtime',
                    region_name=self.region,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key
                )
                self.use_bearer_token = False
                print("✅ Using AWS Bedrock standard credentials")
            except Exception as e:
                print(f"Failed to initialize Boto3 client: {e}")
                self.client = None
                self.use_bearer_token = False
        else:
            self.client = None
            self.use_bearer_token = False
    
    async def analyze_vibe(self, transcript: str, context: str = "general") -> Dict[str, Any]:
        if not self.client and not self.use_bearer_token:
            return {"vibe": "Not configured", "evidence": ["AWS Bedrock credentials not found in .env"]}

        # Use a fast, capable model available on Bedrock, like Claude 3 Haiku
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        # Enhanced emotional analysis prompt
        if context in ['interview', 'coffee_chat']:
            prompt = f"""
            You are an expert in social dynamics and emotional intelligence. Analyze this transcript deeply.
            
            Focus on emotional cues, body language mentions, tone indicators, and interpersonal dynamics.
            
            Analyze:
            1. Overall emotional vibe/sentiment (Happy, Sad, Neutral, Anxious, Confident, Excited, etc.)
            2. Does the other person seem interested in you? (Engaged, Neutral, Disinterested)
            3. Emotional shifts throughout the conversation
            4. Key emotional moments with evidence
            
            Transcript:
            {transcript}
            
            Return ONLY a valid JSON object:
            {{
                "vibe": "primary emotion (Happy/Sad/Neutral/Anxious/Confident/Excited)",
                "interest_level": "Engaged/Neutral/Disinterested",
                "confidence": 0.0-1.0,
                "emotional_moments": ["moment 1", "moment 2"],
                "evidence": ["quote 1", "quote 2", "quote 3"],
                "interpretation": "brief explanation of what these emotions/signals mean"
            }}
            """
        else:
            # General video analysis - focus on visible emotions
            prompt = f"""
            You are analyzing emotional content and vibe from a video transcript.
            
            Analyze the overall emotional tone and atmosphere:
            1. What emotions are expressed? (Happy, Sad, Frustrated, Excited, Calm, etc.)
            2. What's the overall vibe/mood?
            3. Any emotional shifts or notable moments?
        
        Transcript:
        {transcript}
        
        Return ONLY a valid JSON object:
            {{
                "vibe": "primary emotion/mood",
                "confidence": 0.0-1.0,
                "emotional_moments": ["moment 1", "moment 2"],
                "evidence": ["quote or observation 1", "quote 2"],
                "interpretation": "what this emotional content suggests"
            }}
        """

        # Construct the Bedrock request body for Claude
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
            "system": "Return only valid JSON."
        })

        try:
            if self.use_bearer_token:
                # Use bearer token with direct HTTP request
                endpoint = f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{model_id}/invoke"
                headers = {
                    "Authorization": f"Bearer {self.bearer_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                response = requests.post(endpoint, headers=headers, data=body, timeout=30)
                response.raise_for_status()
                response_body = response.json()
                json_text = response_body.get('content', [{}])[0].get('text', '{}')
                return json.loads(json_text)
            else:
                # Use boto3 client
                response = self.client.invoke_model(
                    body=body,
                    modelId=model_id,
                    contentType='application/json',
                    accept='application/json'
                )
                response_body = json.loads(response.get('body').read())
                json_text = response_body.get('content', [{}])[0].get('text', '{}')
                return json.loads(json_text)
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            print(f"Bedrock vibe check failed (bearer token): {error_message}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    return {"vibe": "Error", "evidence": [f"Bearer token error: {error_detail}"]}
                except:
                    return {"vibe": "Error", "evidence": [f"HTTP {e.response.status_code}: {error_message}"]}
            return {"vibe": "Error", "evidence": [error_message]}
        except Exception as e:
            error_message = str(e)
            print(f"Bedrock vibe check failed: {error_message}")
            # Check for common configuration errors
            if "AccessDeniedException" in error_message:
                return {"vibe": "Error", "evidence": ["Access Denied. Check your AWS IAM permissions for Bedrock."]}
            if "ResourceNotFoundException" in error_message:
                return {"vibe": "Error", "evidence": [f"Model '{model_id}' not found. Ensure you have access in region '{self.region}'."]}
            return {"vibe": "Error", "evidence": [error_message]}
