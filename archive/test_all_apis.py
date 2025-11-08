#!/usr/bin/env python3
"""Test all API integrations"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_openai():
    """Test OpenAI API"""
    print("\n🔵 Testing OpenAI...")
    try:
        from services.transcription import TranscriptionService
        service = TranscriptionService(api_key=os.getenv("OPENAI_API_KEY"))
        
        if not service.client:
            print("   ❌ OpenAI client not initialized (check API key)")
            return False
        
        # Test with a simple text (we'll use reasoning service for actual API call)
        from services.reasoning import ReasoningService
        reasoning = ReasoningService(
            openai_key=os.getenv("OPENAI_API_KEY"),
            anthropic_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        if not reasoning.openai_client:
            print("   ❌ OpenAI reasoning client not initialized")
            return False
        
        # Test a simple API call
        test_text = "This is a test meeting. We need to finish the project by Friday."
        result = await reasoning.clean_transcript(test_text)
        
        if result and "sections" in result:
            print("   ✅ OpenAI GPT-4o working!")
            print(f"   📝 Processed transcript into {len(result.get('sections', []))} section(s)")
            return True
        else:
            print("   ⚠️  OpenAI responded but format unexpected")
            print(f"   Response: {result}")
            return False
    except Exception as e:
        print(f"   ❌ OpenAI error: {str(e)}")
        return False

async def test_anthropic():
    """Test Anthropic API"""
    print("\n🟣 Testing Anthropic Claude...")
    try:
        from services.reasoning import ReasoningService
        service = ReasoningService(
            openai_key=os.getenv("OPENAI_API_KEY"),
            anthropic_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        if not service.anthropic_client:
            print("   ❌ Anthropic client not initialized (check API key)")
            return False
        
        # Test task extraction
        test_sections = [{
            "title": "Test Meeting",
            "speakered_text": [{
                "speaker": "Speaker A",
                "text": "We need to finish the project by Friday at 3 PM."
            }]
        }]
        
        result = await service.extract_tasks(test_sections)
        
        if result and "tasks" in result:
            print("   ✅ Anthropic Claude 3.5 working!")
            print(f"   📋 Extracted {len(result['tasks'])} task(s)")
            return True
        else:
            print("   ⚠️  Anthropic responded but format unexpected")
            return False
    except Exception as e:
        print(f"   ❌ Anthropic error: {str(e)}")
        return False

async def test_elevenlabs():
    """Test ElevenLabs API"""
    print("\n🟢 Testing ElevenLabs...")
    try:
        from services.tts import TTSService
        service = TTSService(api_key=os.getenv("ELEVENLABS_API_KEY"))
        
        if not service.api_key or service.api_key == "your_elevenlabs_api_key_here":
            print("   ⚠️  ElevenLabs API key not set")
            return False
        
        # Test TTS
        test_text = "Hello, this is a test."
        result = await service.text_to_speech(test_text)
        
        if isinstance(result, bytes) and len(result) > 100:  # Should return audio bytes
            print("   ✅ ElevenLabs TTS working!")
            print(f"   🎵 Generated {len(result)} bytes of audio")
            return True
        elif isinstance(result, bytes) and len(result) == 0:
            print("   ⚠️  ElevenLabs returned empty response (check API key/credits)")
            return False
        elif isinstance(result, str) and "[DEMO MODE]" in result:
            print("   ⚠️  ElevenLabs in demo mode (check API key)")
            return False
        else:
            print(f"   ⚠️  Unexpected response: {type(result)} - {str(result)[:100]}")
            return False
    except Exception as e:
        print(f"   ❌ ElevenLabs error: {str(e)}")
        return False

async def test_gemini():
    """Test Gemini API"""
    print("\n🟡 Testing Google Gemini...")
    try:
        from services.gemini_service import GeminiService
        service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))
        
        if not service.client:
            print("   ❌ Gemini client not initialized (check API key)")
            return False
        
        # Test content generation
        test_prompt = "Say hello in one sentence."
        result = service.generate_content(test_prompt)
        
        if result and len(result) > 0 and "[DEMO MODE]" not in result:
            print("   ✅ Google Gemini working!")
            print(f"   💬 Response: {result[:50]}...")
            return True
        else:
            print("   ⚠️  Gemini returned demo mode or empty response")
            return False
    except Exception as e:
        print(f"   ❌ Gemini error: {str(e)}")
        return False

def test_google_calendar():
    """Test Google Calendar OAuth setup"""
    print("\n🔴 Testing Google Calendar OAuth...")
    try:
        from services.calendar_service import CalendarService
        service = CalendarService(
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
        )
        
        if not service.client_id or not service.client_secret:
            print("   ❌ Google OAuth credentials not set")
            return False
        
        # Test auth URL generation
        redirect_uri = "http://localhost:3000/auth/google/callback"
        auth_url = service.get_auth_url(redirect_uri)
        
        if auth_url and "accounts.google.com" in auth_url:
            print("   ✅ Google Calendar OAuth configured!")
            print(f"   🔗 Auth URL generated: {auth_url[:80]}...")
            print("   📝 Make sure redirect URI is added in Google Console")
            return True
        else:
            print("   ⚠️  Auth URL generation failed")
            return False
    except Exception as e:
        print(f"   ❌ Google Calendar error: {str(e)}")
        return False

async def test_calendar_endpoint():
    """Test calendar API endpoint"""
    print("\n📅 Testing Calendar API Endpoint...")
    try:
        import httpx
        response = httpx.get("http://localhost:8000/calendar/auth", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "auth_url" in data:
                print("   ✅ Calendar auth endpoint working!")
                print(f"   🔗 Endpoint: http://localhost:8000/calendar/auth")
                return True
            else:
                print("   ⚠️  Endpoint responded but missing auth_url")
                return False
        else:
            print(f"   ❌ Endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Calendar endpoint error: {str(e)}")
        print("   💡 Make sure backend is running: cd backend && python main.py")
        return False

async def main():
    print("=" * 60)
    print("🧪 EVE API Integration Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test APIs
    results['OpenAI'] = await test_openai()
    results['Anthropic'] = await test_anthropic()
    results['ElevenLabs'] = await test_elevenlabs()
    results['Gemini'] = await test_gemini()
    results['Google Calendar OAuth'] = test_google_calendar()
    results['Calendar Endpoint'] = await test_calendar_endpoint()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {service}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All APIs working perfectly!")
    elif passed >= total * 0.8:
        print("\n⚠️  Most APIs working, check failures above")
    else:
        print("\n❌ Multiple API failures, check configuration")

if __name__ == "__main__":
    asyncio.run(main())

