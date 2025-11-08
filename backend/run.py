#!/usr/bin/env python3
"""
Alternative entry point for EVE backend
Usage: python run.py
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Check for required API keys
    required_keys = ["OPENAI_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print("\n❌ Missing required API keys in .env file:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n📝 Please add these keys to your .env file")
        print("   See API_KEYS_GUIDE.md for instructions\n")
        exit(1)
    
    print("\n✅ API keys loaded successfully")
    print("🚀 Starting EVE backend on http://localhost:8000\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

