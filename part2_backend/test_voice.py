#!/usr/bin/env python3
"""
Test script for Voice Agent
Usage: python3 test_voice.py
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

# Sample narration and emotion data for testing
SAMPLE_NARRATION = {
    "main_narration": "On a tranquil tropical beach, the sun slowly sinks toward the horizon, casting warm golden hues across the sky. To your left, you hear the gentle lapping of ocean waves while a soft breeze whispers through swaying palm trees on your right.",
    "person_dialogues": [
        {
            "person_id": 1,
            "position": "left",
            "dialogue": "Isn't it amazing how each sunset feels like a unique masterpiece?",
            "emotion": "contemplative"
        },
        {
            "person_id": 2,
            "position": "right",
            "dialogue": "Absolutely! I wish we could capture this feeling forever.",
            "emotion": "joyful"
        }
    ],
    "ambient_descriptions": [
        "the rhythmic sound of waves rolling onto shore",
        "seagulls calling softly overhead",
        "a gentle breeze rustling through palm fronds"
    ]
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

async def test_voice_generation():
    """Test voice generation with sample data"""
    print("🎵 Testing Voice Agent")
    print("=" * 60)

    try:
        # Test OpenAI TTS (fallback method)
        print("🔊 Step 1: Testing OpenAI TTS (Main Narration)")

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("❌ OPENAI_API_KEY not found in .env")
            return

        narration_text = SAMPLE_NARRATION["main_narration"]
        print(f"📝 Text to convert: {narration_text[:100]}...")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={"Authorization": f"Bearer {openai_api_key}"},
                json={
                    "model": "tts-1",
                    "input": narration_text,
                    "voice": "alloy",
                    "response_format": "mp3"
                }
            )

            if response.status_code == 200:
                # Save the audio file
                audio_filename = "storage/audio/test_narration.mp3"
                os.makedirs(os.path.dirname(audio_filename), exist_ok=True)
                with open(audio_filename, "wb") as f:
                    f.write(response.content)

                file_size = len(response.content)
                print(f"✅ OpenAI TTS successful! Saved {file_size} bytes to {audio_filename}")

                # Test a dialogue
                print("\n💬 Step 2: Testing Dialogue Generation")
                dialogue_text = SAMPLE_NARRATION["person_dialogues"][0]["dialogue"]
                print(f"📝 Dialogue: {dialogue_text}")

                dialogue_response = await client.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers={"Authorization": f"Bearer {openai_api_key}"},
                    json={
                        "model": "tts-1",
                        "input": dialogue_text,
                        "voice": "alloy",
                        "response_format": "mp3"
                    }
                )

                if dialogue_response.status_code == 200:
                    dialogue_filename = "storage/audio/test_dialogue.mp3"
                    with open(dialogue_filename, "wb") as f:
                        f.write(dialogue_response.content)

                    dialogue_size = len(dialogue_response.content)
                    print(f"✅ Dialogue TTS successful! Saved {dialogue_size} bytes to {dialogue_filename}")

                    print("\n📊 Voice Generation Results:")
                    print("  ✅ Main narration audio generated")
                    print("  ✅ Dialogue audio generated")
                    print("  ✅ Files saved to storage/audio/")
                    print("\n🎵 Audio files ready for playback!")

                else:
                    print(f"❌ Dialogue TTS failed: {dialogue_response.status_code}")

            else:
                print(f"❌ OpenAI TTS failed: {response.status_code}")
                print(f"Response: {response.text}")

        # Test Fish Audio (if API key available)
        print("\n🐟 Step 3: Testing Fish Audio (if available)")
        fish_api_key = os.getenv("FISH_AUDIO_API_KEY")

        if fish_api_key:
            print("🐟 Fish Audio API key found - testing...")
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    fish_response = await client.post(
                        "https://api.fish.audio/v1/tts",
                        headers={"Authorization": f"Bearer {fish_api_key}"},
                        json={
                            "text": "Hello from Fish Audio test",
                            "reference_id": "your_reference_voice_id",
                            "format": "mp3",
                            "mp3_bitrate": 128
                        }
                    )

                    if fish_response.status_code == 200:
                        fish_filename = "storage/audio/test_fish.mp3"
                        with open(fish_filename, "wb") as f:
                            f.write(fish_response.content)

                        print(f"✅ Fish Audio successful! Saved to {fish_filename}")
                    else:
                        print(f"ℹ️  Fish Audio returned: {fish_response.status_code}")
                        print("   (This is expected if no voice reference is set up)")

            except Exception as e:
                print(f"ℹ️  Fish Audio test failed: {e}")
                print("   (This is normal if Fish Audio is not fully configured)")
        else:
            print("ℹ️  Fish Audio API key not found - skipping Fish Audio test")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

async def test_voice_agent_logic():
    """Test the voice agent logic with sample data"""
    print("\n🤖 Testing Voice Agent Logic")
    print("=" * 40)

    # Simulate what the voice agent does
    voice_files = []

    # Generate main narration
    narration_text = SAMPLE_NARRATION["main_narration"]
    print(f"📝 Processing main narration: {len(narration_text)} characters")
    # In real agent, this would call TTS and save file
    voice_files.append({
        "type": "narration",
        "position": "center",
        "text": narration_text[:100] + "...",
        "url": "/static/test_narration.mp3"
    })

    # Generate dialogues
    for dialogue in SAMPLE_NARRATION["person_dialogues"]:
        person_id = dialogue["person_id"]
        text = dialogue["dialogue"]
        position = "left" if person_id == 1 else "right"

        print(f"💬 Processing dialogue {person_id}: {text}")
        # In real agent, this would call TTS and save file
        voice_files.append({
            "type": "dialogue",
            "position": position,
            "person_id": person_id,
            "text": text,
            "url": f"/static/test_dialogue_{person_id}.mp3"
        })

    print("\n📊 Voice Agent Logic Results:")
    print(f"  Generated {len(voice_files)} audio files:")
    for vf in voice_files:
        print(f"    - {vf['type']} ({vf['position']}): {vf['text'][:50]}...")

if __name__ == "__main__":
    print("Testing Voice Agent - Audio Generation\n")
    asyncio.run(test_voice_generation())
    asyncio.run(test_voice_agent_logic())
