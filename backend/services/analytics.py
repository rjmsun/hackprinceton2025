import httpx
from typing import Dict, Any, Optional
from datetime import datetime

class AnalyticsService:
    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key
        self.base_url = "https://api2.amplitude.com/2/httpapi"
    
    def track_event(self, user_id: str, event_name: str, properties: Dict[str, Any] = None):
        """Track event to Amplitude (fire and forget)"""
        if not self.api_key or self.api_key == "your_amplitude_api_key_here":
            # Skip if no API key configured
            return
        
        event = {
            "user_id": user_id,
            "event_type": event_name,
            "time": int(datetime.utcnow().timestamp() * 1000),
            "event_properties": properties or {}
        }
        
        try:
            # Fire and forget - don't await
            import threading
            threading.Thread(
                target=self._send_event,
                args=(event,),
                daemon=True
            ).start()
        except:
            pass
    
    def _send_event(self, event: Dict):
        """Internal method to send event"""
        try:
            import requests
            requests.post(
                self.base_url,
                json={"api_key": self.api_key, "events": [event]},
                timeout=5
            )
        except:
            pass

