#!/usr/bin/env python3
"""
Test script for Perception Agent
Usage: python3 test_perception.py <photo_url>
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

# No imports from agent files

async def test_perception_agent(photo_url: str):
    """Test the perception agent with a photo URL"""
    print(f"🖼️  Testing Perception Agent with: {photo_url}")
    print("=" * 60)

    try:
        # Test GPT-4o Vision call
        print("🔍 Step 1: GPT-4o Vision Analysis")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            print("❌ OPENAI_API_KEY not found in .env")
            return

        async with httpx.AsyncClient(timeout=60.0) as client:
            vision_response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {openai_api_key}"},
                json={
                    "model": "gpt-4o",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this image in extreme detail. Describe: 1) ALL objects, 2) Number of people and their positions/moods, 3) Spatial layout, 4) Colors/lighting, 5) Scene context. Be exhaustive."},
                            {"type": "image_url", "image_url": {"url": photo_url}}
                        ]
                    }],
                    "max_tokens": 800
                }
            )

            if vision_response.status_code != 200:
                print(f"❌ GPT-4o Vision failed: {vision_response.status_code}")
                print(f"Response: {vision_response.text}")
                return

            vision_desc = vision_response.json()["choices"][0]["message"]["content"]
            print(f"✅ Vision analysis complete ({len(vision_desc)} characters)")
            print(f"📝 Vision text preview: {vision_desc[:200]}...")

        # Test Letta AI extraction
        print("\n🤖 Step 2: Letta AI Structured Extraction")
        letta_api_key = os.getenv("LETTA_API_KEY")
        perception_agent_id = os.getenv("PERCEPTION_AGENT_ID")

        if not letta_api_key or not perception_agent_id:
            print("❌ LETTA_API_KEY or PERCEPTION_AGENT_ID not found in .env")
            return

        print(f"📡 Calling Letta AI agent: {perception_agent_id}")
        print(f"📝 Input text length: {len(vision_desc)} characters")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                letta_response = await client.post(
                    f"https://api.letta.com/v1/agents/{perception_agent_id}/messages",
                    headers={"Authorization": f"Bearer {letta_api_key}"},
                    json={"messages": [{"role": "user", "content": f"Extract structured data:\\n\\n{vision_desc}"}], "stream": False}
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

                perception_text = next((m.get("content", "") for m in letta_data.get("messages", []) if m.get("message_type") == "assistant_message"), "{}")

                print(f"📝 Extracted content: {perception_text}")

                # Parse JSON (handle mixed quotes from Letta AI)
                json_start = perception_text.find('{')
                json_end = perception_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = perception_text[json_start:json_end]
                    # Fix mixed quotes by replacing single quotes around keys/values
                    import re
                    # Replace single quotes around keys and string values with double quotes
                    json_content = re.sub(r"'([^']*)':", r'"\1":', json_content)  # Keys
                    json_content = re.sub(r": '([^']*)'", r': "\1"', json_content)  # String values
                    json_content = re.sub(r": '([^']*)',", r': "\1",', json_content)  # String values with comma
                    json_content = re.sub(r": '([^']*)'}", r': "\1"}', json_content)  # String values at end
                    # Fix single quotes in arrays: ['item1', 'item2'] -> ["item1", "item2"]
                    json_content = re.sub(r"'([^']*)'", r'"\1"', json_content)

                    try:
                        parsed = json.loads(json_content)
                        print("✅ JSON parsing successful!")
                        print("📊 Final Perception Result:")
                        print(json.dumps(parsed, indent=2))
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parsing failed even after quote fix: {e}")
                        print(f"Fixed content: {json_content}")
                else:
                    print("❌ No valid JSON found in response")
                    print(f"Text content: {perception_text}")

        except Exception as e:
            print(f"❌ Letta AI failed: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_perception.py <photo_url>")
        print("Example: python3 test_perception.py https://images.unsplash.com/photo-1507525428034-b723cf961d3e")
        sys.exit(1)

    photo_url = sys.argv[1]
    asyncio.run(test_perception_agent(photo_url))
