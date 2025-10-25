# agents/coordinator_agent.py
from uagents import Agent, Context, Bureau
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fetch_models import (
    VisionAnalysisRequest, PerceptionData, EmotionRequest, EmotionData,
    NarrationRequest, NarrationData, VoiceRequest, VoiceData,
    AudioMixRequest, AudioMixData, ExperienceComplete, ErrorMessage
)
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Agent addresses (hardcoded - deterministic from seeds)
PERCEPTION_AGENT_ADDRESS = "agent1q26xyx0j7jszd9uhah2s2kvp2my555zvywhnxh7x0dz6u3z354k65229de5"
EMOTION_AGENT_ADDRESS = "agent1qtdj6yrjtl4ydgflspm4pznfdehpuav8hgwv5jmgcs9hx6rwvv635l0xk9s"
NARRATION_AGENT_ADDRESS = "agent1qdvng2wkvfs3efq7k6xv2snwtvqfh27evujurz8ajcnaztusf85ly2wnqwm"
VOICE_AGENT_ADDRESS = "agent1q2ugazshc4f8paa2933z4pw4f0v89q6xhrng8xwhy347vu66mqx6zp7tc2y"
AUDIO_MIXER_AGENT_ADDRESS = "agent1qw7zh2kcplhl92720udztcux5u5x4q9qs03yf5k3zhasjkgheh8s5rr7pp6"

coordinator_agent = Agent(
    name="coordinator_agent",
    seed="coordinator_seed_12345",
    endpoint=["http://localhost:8006/submit"]
)

@coordinator_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"🎯 Coordinator Agent started: {coordinator_agent.address}")
    ctx.logger.info(f"🔗 Connected to agents:")
    ctx.logger.info(f"  Perception: {PERCEPTION_AGENT_ADDRESS}")
    ctx.logger.info(f"  Emotion: {EMOTION_AGENT_ADDRESS}")
    ctx.logger.info(f"  Narration: {NARRATION_AGENT_ADDRESS}")
    ctx.logger.info(f"  Voice: {VOICE_AGENT_ADDRESS}")
    ctx.logger.info(f"  AudioMixer: {AUDIO_MIXER_AGENT_ADDRESS}")
    ctx.logger.info(f"🌐 HTTP Endpoint: http://localhost:8006/submit")

@coordinator_agent.on_message(model=VisionAnalysisRequest)
async def orchestrate_experience(ctx: Context, sender: str, msg: VisionAnalysisRequest):
    session_id = msg.session_id
    ctx.logger.info(f"🚀 [COORDINATOR] Starting experience for {session_id}")

    try:
        # Step 1: Perception Analysis
        ctx.logger.info(f"📸 [1/5] → Perception Agent")
        await ctx.send(PERCEPTION_AGENT_ADDRESS, msg)
        perception_response = await ctx.receive(PerceptionData, timeout=120)
        if isinstance(perception_response.payload, ErrorMessage):
            raise Exception(f"Perception failed: {perception_response.payload.error}")
        perception_data = perception_response.payload

        # Step 2: Emotion Detection
        ctx.logger.info(f"😊 [2/5] → Emotion Agent")
        emotion_request = EmotionRequest(session_id=session_id, perception_data=perception_data.__dict__)
        await ctx.send(EMOTION_AGENT_ADDRESS, emotion_request)
        emotion_response = await ctx.receive(EmotionData, timeout=60)
        if isinstance(emotion_response.payload, ErrorMessage):
            raise Exception(f"Emotion failed: {emotion_response.payload.error}")
        emotion_data = emotion_response.payload

        # Step 3: Narration Generation
        ctx.logger.info(f"📝 [3/5] → Narration Agent")
        narration_request = NarrationRequest(
            session_id=session_id,
            perception=perception_data.__dict__,
            emotion=emotion_data.__dict__
        )
        await ctx.send(NARRATION_AGENT_ADDRESS, narration_request)
        narration_response = await ctx.receive(NarrationData, timeout=60)
        if isinstance(narration_response.payload, ErrorMessage):
            raise Exception(f"Narration failed: {narration_response.payload.error}")
        narration_data = narration_response.payload

        # Step 4: Voice Synthesis
        ctx.logger.info(f"🎤 [4/5] → Voice Agent")
        voice_request = VoiceRequest(
            session_id=session_id,
            narration_data=narration_data.__dict__,
            emotion_data=emotion_data.__dict__
        )
        await ctx.send(VOICE_AGENT_ADDRESS, voice_request)
        voice_response = await ctx.receive(VoiceData, timeout=120)
        if isinstance(voice_response.payload, ErrorMessage):
            raise Exception(f"Voice failed: {voice_response.payload.error}")
        voice_data = voice_response.payload

        # Step 5: Audio Mixing
        ctx.logger.info(f"🎵 [5/5] → Audio Mixer Agent")
        audio_mix_request = AudioMixRequest(
            session_id=session_id,
            voice_files=voice_data.voice_files,
            ambient_sounds=perception_data.ambient_sounds
        )
        await ctx.send(AUDIO_MIXER_AGENT_ADDRESS, audio_mix_request)
        audio_mix_response = await ctx.receive(AudioMixData, timeout=60)
        if isinstance(audio_mix_response.payload, ErrorMessage):
            raise Exception(f"Audio Mix failed: {audio_mix_response.payload.error}")
        audio_mix_data = audio_mix_response.payload

        # Step 6: Complete Experience
        ctx.logger.info(f"✅ Experience complete for {session_id}")

        # Create audio layers for UI
        audio_layers = []
        for voice_file in voice_data.voice_files:
            audio_layers.append({
                "type": voice_file["type"],
                "position": voice_file["position"],
                "text": voice_file["text"][:100] + "..." if len(voice_file["text"]) > 100 else voice_file["text"]
            })

        experience_complete = ExperienceComplete(
            session_id=session_id,
            perception=perception_data.__dict__,
            emotion=emotion_data.__dict__,
            narration=narration_data.__dict__,
            audio_layers=audio_layers,
            final_audio_url=audio_mix_data.final_audio_url
        )

        await ctx.send(sender, experience_complete)

    except Exception as e:
        ctx.logger.error(f"❌ Coordinator error for {session_id}: {e}")
        await ctx.send(sender, ErrorMessage(session_id=session_id, error=str(e), step="coordinator"))

if __name__ == "__main__":
    coordinator_agent.run()
