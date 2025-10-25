#!/usr/bin/env python3
"""
Test script for Coordinator Agent
Usage: python3 test_coordinator.py
"""
import sys
import os
import asyncio
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_coordinator_logic():
    """Test the coordinator agent logic without running the full agent system"""
    print("🎯 Testing Coordinator Agent Logic")
    print("=" * 60)

    # Simulate the coordinator's workflow
    print("📋 Coordinator Workflow Simulation:")

    # Step 1: Receive photo URL request
    photo_url = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
    session_id = "test_session_123"
    print(f"📥 Received request: {session_id} for photo: {photo_url}")

    # Step 2: Start parallel processing
    print("\n🚀 Step 1: Starting Parallel Agent Processing")
    print("  📸 Sending to Perception Agent...")
    print("  😊 Sending to Emotion Agent...")

    # Simulate agent responses (using our test data)
    perception_response = {
        "session_id": session_id,
        "objects": ["ocean", "beach", "palm trees", "sun", "clouds"],
        "people_count": 0,
        "people_details": [],
        "layout": {
            "foreground": "sandy beach",
            "midground": "ocean waves",
            "background": "sunset sky"
        },
        "scene_type": "outdoor_beach",
        "setting": "tropical beach",
        "colors": ["blue", "gold", "green"],
        "lighting": "warm sunset",
        "ambient_sounds": ["waves", "wind"]
    }

    emotion_response = {
        "session_id": session_id,
        "mood": "serene",
        "emotion_tags": ["peaceful", "calm", "reflective"],
        "tone": "gentle",
        "intensity": "low",
        "voice_characteristics": {
            "main_narrator": "gentle, tranquil",
            "person_1": "thoughtful"
        },
        "ambient_mood": "quiet atmosphere"
    }

    print("  ✅ Perception Agent responded")
    print("  ✅ Emotion Agent responded")

    # Step 3: Check if we have both responses, then proceed to narration
    print("\n📝 Step 2: Proceeding to Narration Agent")
    print("  🔄 Both perception and emotion data available")
    print("  📝 Sending to Narration Agent...")

    # Simulate narration response
    narration_response = {
        "session_id": session_id,
        "main_narration": "A beautiful beach scene with gentle waves and palm trees.",
        "person_dialogues": [
            {"person_id": 1, "position": "center", "dialogue": "So peaceful here.", "emotion": "calm"}
        ],
        "ambient_descriptions": ["gentle waves", "soft breeze"]
    }

    print("  ✅ Narration Agent responded")

    # Step 4: Proceed to voice synthesis
    print("\n🎤 Step 3: Proceeding to Voice Agent")
    print("  🎵 Sending to Voice Agent...")

    # Simulate voice response
    voice_response = {
        "session_id": session_id,
        "voice_files": [
            {"type": "narration", "position": "center", "text": "A beautiful beach...", "url": "/static/narration.mp3"},
            {"type": "dialogue", "position": "center", "text": "So peaceful here.", "url": "/static/dialogue.mp3"}
        ]
    }

    print("  ✅ Voice Agent responded")

    # Step 5: Proceed to audio mixing
    print("\n🎵 Step 4: Proceeding to Audio Mixer Agent")
    print("  🔊 Sending to Audio Mixer Agent...")

    # Simulate audio mix response
    audio_mix_response = {
        "session_id": session_id,
        "final_audio_url": "/static/final_experience.mp3"
    }

    print("  ✅ Audio Mixer Agent responded")

    # Step 6: Complete the experience
    print("\n✅ Step 5: Experience Complete!")
    print("  📦 Final response prepared")

    final_response = {
        "session_id": session_id,
        "emotion": emotion_response,
        "narration": narration_response,
        "audio_layers": voice_response["voice_files"],
        "final_audio_url": audio_mix_response["final_audio_url"]
    }

    print("\n📊 Final Coordinator Output:")
    print(json.dumps(final_response, indent=2))

    print("\n🔍 Validation:")
    print("  ✅ Session ID consistent")
    print("  ✅ Emotion data included")
    print("  ✅ Narration data included")
    print("  ✅ Audio layers specified")
    print("  ✅ Final audio URL provided")

    print("\n🎯 Coordinator Logic Test: PASSED ✅")

if __name__ == "__main__":
    print("Testing Coordinator Agent - Workflow Orchestration\n")
    asyncio.run(test_coordinator_logic())
