#!/usr/bin/env python3
"""
Test script for Narration Agent
Usage: python3 test_narration.py
"""
import sys
import os
import asyncio
import httpx
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Sample perception and emotion data for testing
SAMPLE_PERCEPTION = {
    "objects": ["ocean", "beach", "palm trees", "sunset", "sand"],
    "people_count": 2,
    "people_details": [
        {"position": "left", "description": "person standing, looking at sunset"},
        {"position": "right", "description": "person sitting on sand"}
    ],
    "layout": {
        "left": "ocean waves",
        "center": "beach",
        "right": "palm trees",
        "back": "sunset horizon"
    },
    "scene_type": "outdoor",
    "setting": "tropical beach at sunset",
    "colors": ["golden", "orange", "blue", "turquoise"],
    "lighting": "warm sunset glow",
    "ambient_sounds": ["ocean waves", "seagulls", "gentle breeze"]
}

SAMPLE_EMOTION = {
    "mood": "peaceful",
    "emotion_tags": ["contemplative", "serene", "joyful"],
    "tone": "gentle",
    "intensity": "medium",
    "voice_characteristics": {
        "pace": "slow",
        "pitch": "medium",
        "warmth": "warm"
    },
    "ambient_mood": "tranquil"
}

async def test_narration_agent():
    """Test the narration agent with sample data"""
    print(f"📖 Testing Narration Agent")
    print("=" * 60)

    try:
        print("🤖 Step: Letta AI Narration Generation")
        letta_api_key = os.getenv("LETTA_API_KEY")
        narration_agent_id = os.getenv("NARRATION_AGENT_ID")

        if not letta_api_key or not narration_agent_id:
            print("❌ LETTA_API_KEY or NARRATION_AGENT_ID not found in .env")
            return

        print(f"📡 Calling Letta AI agent: {narration_agent_id}")

        # Construct the message
        message = f"Create narration:\n\nPERCEPTION:\n{json.dumps(SAMPLE_PERCEPTION, indent=2)}\n\nEMOTION:\n{json.dumps(SAMPLE_EMOTION, indent=2)}"
        print(f"📝 Input message length: {len(message)} characters")

        async with httpx.AsyncClient(timeout=60.0) as client:
            letta_response = await client.post(
                f"https://api.letta.com/v1/agents/{narration_agent_id}/messages",
                headers={"Authorization": f"Bearer {letta_api_key}"},
                json={"messages": [{"role": "user", "content": message}], "stream": False}
            )

            print(f"🔄 Letta AI response status: {letta_response.status_code}")

            if letta_response.status_code != 200:
                print(f"❌ Letta AI HTTP error: {letta_response.status_code}")
                print(f"Response headers: {dict(letta_response.headers)}")
                print(f"Response body: {letta_response.text}")
                return

            letta_data = letta_response.json()
            print("📦 Letta AI raw response:")
            print(json.dumps(letta_data, indent=2))

            narration_text = next((m.get("content", "") for m in letta_data.get("messages", []) if m.get("message_type") == "assistant_message"), "{}")
            print(f"\n📝 Extracted assistant content: {narration_text}")

            # Parse JSON
            json_start = narration_text.find('{')
            json_end = narration_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_content = narration_text[json_start:json_end]

                try:
                    parsed = json.loads(json_content)
                    print("\n✅ JSON parsing successful!")
                    print("\n📊 Final Narration Result:")
                    print(json.dumps(parsed, indent=2))

                    # Validate structure
                    print("\n🔍 Validation:")
                    if "main_narration" in parsed:
                        print(f"  ✅ main_narration: {len(parsed['main_narration'])} chars")
                    else:
                        print("  ❌ main_narration: MISSING")

                    if "person_dialogues" in parsed:
                        print(f"  ✅ person_dialogues: {len(parsed['person_dialogues'])} items")
                    else:
                        print("  ❌ person_dialogues: MISSING")

                    if "ambient_descriptions" in parsed:
                        print(f"  ✅ ambient_descriptions: {len(parsed['ambient_descriptions'])} items")
                    else:
                        print("  ❌ ambient_descriptions: MISSING")

                except json.JSONDecodeError as e:
                    print(f"\n❌ JSON parsing failed: {e}")
                    print(f"Content: {json_content}")
            else:
                print("\n❌ No valid JSON found in response")
                print(f"Text content: {narration_text}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing Narration Agent with sample perception and emotion data\n")
    asyncio.run(test_narration_agent())
