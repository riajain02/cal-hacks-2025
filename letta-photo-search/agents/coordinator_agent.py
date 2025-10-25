# agents/coordinator_agent.py
from uagents import Agent, Context
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fetch_models import (
    VisionAnalysisRequest, PerceptionData, EmotionRequest, EmotionData,
    NarrationRequest, NarrationData, VoiceRequest, VoiceData,
    AudioMixRequest, AudioMixData, ExperienceComplete, ErrorMessage,
    StoryGenerationResponse
)
import asyncio
import json
from pathlib import Path

# Agent addresses (hardcoded - deterministic from seeds)
PERCEPTION_AGENT_ADDRESS = "agent1q26xyx0j7jszd9uhah2s2kvp2my555zvywhnxh7x0dz6u3z354k65229de5"
EMOTION_AGENT_ADDRESS = "agent1qtdj6yrjtl4ydgflspm4pznfdehpuav8hgwv5jmgcs9hx6rwvv635l0xk9s"
NARRATION_AGENT_ADDRESS = "agent1qdvng2wkvfs3efq7k6xv2snwtvqfh27evujurz8ajcnaztusf85ly2wnqwm"
VOICE_AGENT_ADDRESS = "agent1q2ugazshc4f8paa2933z4pw4f0v89q6xhrng8xwhy347vu66mqx6zp7tc2y"
AUDIO_MIXER_AGENT_ADDRESS = "agent1qw7zh2kcplhl92720udztcux5u5x4q9qs03yf5k3zhasjkgheh8s5rr7pp6"

coordinator_agent = Agent(
    name="coordinator_agent",
    seed="coordinator_seed_12345",
    port=8006,
    endpoint=["http://localhost:8006/submit"]
)

# Global storage for agent responses
agent_responses = {}

@coordinator_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"🎯 Coordinator Agent started: {coordinator_agent.address}")
    ctx.logger.info(f"🔗 Connected to agents:")
    ctx.logger.info(f"  Perception: {PERCEPTION_AGENT_ADDRESS}")
    ctx.logger.info(f"  Emotion: {EMOTION_AGENT_ADDRESS}")
    ctx.logger.info(f"  Narration: {NARRATION_AGENT_ADDRESS}")
    ctx.logger.info(f"  Voice: {VOICE_AGENT_ADDRESS}")
    ctx.logger.info(f"  AudioMixer: {AUDIO_MIXER_AGENT_ADDRESS}")
    ctx.logger.info(f"📁 Monitoring for requests...")
    ctx.logger.info(f"🌐 REST API available at: http://localhost:8006/api/generate")

# REST API endpoint for HTTP requests
@coordinator_agent.on_rest_post("/api/generate", VisionAnalysisRequest, StoryGenerationResponse)
async def handle_http_request(ctx: Context, req: VisionAnalysisRequest) -> StoryGenerationResponse:
    """
    HTTP REST endpoint to trigger story generation
    Accepts JSON: {"photo_url": "...", "session_id": "..."}
    """
    ctx.logger.info(f"🌐 HTTP REST request received for session: {req.session_id}")

    # Store photo URL for later use
    agent_responses[f"{req.session_id}_photo_url"] = req.photo_url

    # Start the agent workflow by sending to perception agent
    ctx.logger.info(f"🚀 [COORDINATOR] Starting experience for {req.session_id}")
    ctx.logger.info(f"📸 [1/5] → Perception Agent")

    vision_request = VisionAnalysisRequest(photo_url=req.photo_url, session_id=req.session_id)
    await ctx.send(PERCEPTION_AGENT_ADDRESS, vision_request)

    ctx.logger.info(f"⏳ Waiting for agent responses for session {req.session_id}")

    # Return immediately - the workflow will complete asynchronously
    return StoryGenerationResponse(
        success=True,
        message="Story generation started",
        session_id=req.session_id
    )

@coordinator_agent.on_message(model=PerceptionData)
async def handle_perception_response(ctx: Context, sender: str, msg: PerceptionData):
    """Handle perception agent response"""
    session_id = msg.session_id
    agent_responses[f"{session_id}_perception"] = msg
    ctx.logger.info(f"📸 Received perception data for {session_id}")

    # Now send to emotion agent with perception data
    photo_url = agent_responses.get(f"{session_id}_photo_url", "")
    ctx.logger.info(f"😊 [2/5] → Emotion Agent (with perception data)")
    emotion_request = EmotionRequest(
        session_id=session_id,
        photo_url=photo_url,
        perception_data=msg.__dict__
    )
    await ctx.send(EMOTION_AGENT_ADDRESS, emotion_request)

    # Note: We no longer check for both here, emotion will come after

@coordinator_agent.on_message(model=EmotionData)
async def handle_emotion_response(ctx: Context, sender: str, msg: EmotionData):
    """Handle emotion agent response"""
    session_id = msg.session_id
    agent_responses[f"{session_id}_emotion"] = msg
    ctx.logger.info(f"😊 Received emotion data for {session_id}")

    # Now we have both perception and emotion, proceed with narration
    await proceed_with_narration(ctx, session_id)

@coordinator_agent.on_message(model=NarrationData)
async def handle_narration_response(ctx: Context, sender: str, msg: NarrationData):
    """Handle narration agent response - create final response for simple story"""
    session_id = msg.session_id
    agent_responses[f"{session_id}_narration"] = msg
    ctx.logger.info(f"📝 Received narration data for {session_id}")

    # Create final response with perception, emotion, and narration
    # (Voice and audio mixing can be added later if needed)
    await create_simple_final_response(ctx, session_id)

@coordinator_agent.on_message(model=VoiceData)
async def handle_voice_response(ctx: Context, sender: str, msg: VoiceData):
    """Handle voice agent response"""
    session_id = msg.session_id
    agent_responses[f"{session_id}_voice"] = msg
    ctx.logger.info(f"🎤 Received voice data for {session_id}")

    # Proceed with audio mixing
    await proceed_with_audio_mixing(ctx, session_id)

@coordinator_agent.on_message(model=AudioMixData)
async def handle_audio_mix_response(ctx: Context, sender: str, msg: AudioMixData):
    """Handle audio mixer response - final step"""
    session_id = msg.session_id
    agent_responses[f"{session_id}_audio"] = msg
    ctx.logger.info(f"🎵 Received final audio for {session_id}")

    # Create final response
    await create_final_response(ctx, session_id)

@coordinator_agent.on_message(model=ErrorMessage)
async def handle_error(ctx: Context, sender: str, msg: ErrorMessage):
    """Handle any agent errors"""
    ctx.logger.error(f"❌ Agent error from {sender}: {msg.error}")

async def proceed_with_narration(ctx: Context, session_id: str):
    """Start narration with perception and emotion data"""
    perception_key = f"{session_id}_perception"
    emotion_key = f"{session_id}_emotion"

    perception_data = agent_responses.get(perception_key)
    emotion_data = agent_responses.get(emotion_key)

    if not perception_data or not emotion_data:
        ctx.logger.error(f"❌ Missing data for narration: perception={bool(perception_data)}, emotion={bool(emotion_data)}")
        return

    # Start narration
    ctx.logger.info(f"📝 [3/5] → Narration Agent")
    narration_request = NarrationRequest(
        session_id=session_id,
        perception=perception_data.__dict__,
        emotion=emotion_data.__dict__
    )
    await ctx.send(NARRATION_AGENT_ADDRESS, narration_request)

async def create_simple_final_response(ctx: Context, session_id: str):
    """Create final response with just perception, emotion, and narration (simplified)"""
    # Get all the data
    perception_data = agent_responses.get(f"{session_id}_perception")
    emotion_data = agent_responses.get(f"{session_id}_emotion")
    narration_data = agent_responses.get(f"{session_id}_narration")

    if not all([perception_data, emotion_data, narration_data]):
        ctx.logger.error(f"❌ Missing data for final response: perception={bool(perception_data)}, emotion={bool(emotion_data)}, narration={bool(narration_data)}")
        return

    # Create final response
    final_response = {
        "session_id": session_id,
        "success": True,
        "perception": perception_data.__dict__,
        "emotion": emotion_data.__dict__,
        "narration": narration_data.__dict__
    }

    # Write to response file for Flask to pick up
    response_dir = Path("storage/responses")
    response_dir.mkdir(parents=True, exist_ok=True)
    response_file = response_dir / f"{session_id}.json"

    with open(response_file, "w") as f:
        json.dump(final_response, f, indent=2)

    ctx.logger.info(f"✅ Complete processing for session {session_id}")
    ctx.logger.info(f"📁 Response saved to: {response_file}")

    # Clean up agent responses
    for key in list(agent_responses.keys()):
        if key.startswith(session_id):
            del agent_responses[key]

async def proceed_with_voice_synthesis(ctx: Context, session_id: str):
    """Proceed with voice synthesis after getting narration"""
    narration_key = f"{session_id}_narration"
    perception_key = f"{session_id}_perception"
    emotion_key = f"{session_id}_emotion"

    if (narration_key in agent_responses and
        perception_key in agent_responses and
        emotion_key in agent_responses):

        narration_data = agent_responses[narration_key]
        emotion_data = agent_responses[emotion_key]

        # Start voice synthesis
        ctx.logger.info(f"🎤 [4/5] → Voice Agent")
        voice_request = VoiceRequest(
            session_id=session_id,
            narration_data=narration_data.__dict__,
            emotion_data=emotion_data.__dict__
        )
        await ctx.send(VOICE_AGENT_ADDRESS, voice_request)

async def proceed_with_audio_mixing(ctx: Context, session_id: str):
    """Proceed with audio mixing after getting voice data"""
    voice_key = f"{session_id}_voice"
    perception_key = f"{session_id}_perception"

    if voice_key in agent_responses and perception_key in agent_responses:
        voice_data = agent_responses[voice_key]
        perception_data = agent_responses[perception_key]

        # Start audio mixing
        ctx.logger.info(f"🎵 [5/5] → Audio Mixer Agent")
        audio_mix_request = AudioMixRequest(
            session_id=session_id,
            voice_files=voice_data.voice_files,
            ambient_sounds=perception_data.ambient_sounds
        )
        await ctx.send(AUDIO_MIXER_AGENT_ADDRESS, audio_mix_request)

async def create_final_response(ctx: Context, session_id: str):
    """Create the final response after all processing is complete"""
    # Get all the data
    perception_data = agent_responses.get(f"{session_id}_perception")
    emotion_data = agent_responses.get(f"{session_id}_emotion")
    narration_data = agent_responses.get(f"{session_id}_narration")
    voice_data = agent_responses.get(f"{session_id}_voice")
    audio_data = agent_responses.get(f"{session_id}_audio")

    if not all([perception_data, emotion_data, narration_data, voice_data, audio_data]):
        ctx.logger.error(f"❌ Missing data for session {session_id}")
        return

    # Create audio layers
    audio_layers = []
    for voice_file in voice_data.voice_files:
        audio_layers.append({
            "type": voice_file["type"],
            "position": voice_file["position"],
            "text": voice_file["text"][:100] + "..." if len(voice_file["text"]) > 100 else voice_file["text"]
        })

    # Create final response
    final_response = {
        "session_id": session_id,
        "emotion": emotion_data.__dict__,
        "narration": narration_data.__dict__,
        "audio_layers": audio_layers,
        "final_audio_url": audio_data.final_audio_url
    }

    # Write to response file for FastAPI to pick up
    import json
    import os
    response_dir = "../storage/responses/"
    os.makedirs(response_dir, exist_ok=True)
    response_file = f"{response_dir}/{session_id}.json"

    with open(response_file, "w") as f:
        json.dump(final_response, f)

    ctx.logger.info(f"✅ Complete processing for session {session_id}")

    # Clean up agent responses
    for key in list(agent_responses.keys()):
        if key.startswith(session_id):
            del agent_responses[key]

@coordinator_agent.on_message(model=VisionAnalysisRequest)
async def orchestrate_experience(ctx: Context, sender: str, msg: VisionAnalysisRequest):
    session_id = msg.session_id
    photo_url = msg.photo_url
    ctx.logger.info(f"🚀 [COORDINATOR] Starting experience for {session_id}")

    # Store photo URL for later use
    agent_responses[f"{session_id}_photo_url"] = photo_url

    # Start with perception agent first (emotion will follow after perception completes)
    ctx.logger.info(f"📸 [1/5] → Perception Agent")
    vision_request = VisionAnalysisRequest(photo_url=photo_url, session_id=session_id)
    await ctx.send(PERCEPTION_AGENT_ADDRESS, vision_request)

    ctx.logger.info(f"⏳ Waiting for agent responses for session {session_id}")

if __name__ == "__main__":
    coordinator_agent.run()
