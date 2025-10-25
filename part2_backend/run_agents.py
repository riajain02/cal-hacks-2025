# run_agents.py
import asyncio
from uagents import Bureau
from agents.perception_agent import perception_agent
from agents.emotion_agent import emotion_agent
from agents.narration_agent import narration_agent
from agents.voice_agent import voice_agent
from agents.audio_mixer_agent import audio_mixer_agent
from agents.coordinator_agent import coordinator_agent

async def run_all_agents():
    bureau = Bureau(port=8001)  # Use port 8001 for bureau

    # Add all agents to bureau
    bureau.add(perception_agent)
    bureau.add(emotion_agent)
    bureau.add(narration_agent)
    bureau.add(voice_agent)
    bureau.add(audio_mixer_agent)
    bureau.add(coordinator_agent)

    print("🤖 Starting Multi-Agent Bureau...")
    print(f"🎯 Coordinator Address: {coordinator_agent.address}")
    print("📡 Bureau running on port: 8001")
    print("🔗 Ready for requests!")

    # Keep running
    await bureau.run_async()

if __name__ == "__main__":
    bureau = Bureau(port=8001)  # Use port 8001 for bureau

    # Add all agents to bureau
    bureau.add(perception_agent)
    bureau.add(emotion_agent)
    bureau.add(narration_agent)
    bureau.add(voice_agent)
    bureau.add(audio_mixer_agent)
    bureau.add(coordinator_agent)

    print("🤖 Starting Multi-Agent Bureau...")
    print(f"🎯 Coordinator Address: {coordinator_agent.address}")
    print("📡 Bureau running on port: 8001")
    print("🔗 Ready for requests!")

    # Run the bureau (this will block)
    print("Starting bureau server...")
    try:
        bureau.run()
    except KeyboardInterrupt:
        print("Bureau stopped")
    except Exception as e:
        print(f"Bureau error: {e}")
