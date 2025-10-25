# main.py - FastAPI Gateway with Coordinator Agent
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from uagents import Agent, Context
import asyncio, uuid, os
from fetch_models import *
from dotenv import load_dotenv
import httpx
import shutil

load_dotenv()

app = FastAPI(title="Photo-to-Audio API", version="1.0.0")

# Mount static files
app.mount("/audio", StaticFiles(directory="storage/audio"), name="audio")
app.mount("/uploads", StaticFiles(directory="storage/uploads"), name="uploads")

# Coordinator Agent
coordinator = Agent(
    name="coordinator",
    seed="coordinator_seed_00000",
    port=8000,
    endpoint=["http://localhost:8000/submit"]
)

# Agent addresses - Update these with actual addresses from agent startup logs
AGENT_ADDRESSES = {
    "perception": "agent1q26xyx0j7jszd9uhah2s2kvp2my555zvywhnxh7x0dz6u3z354k65229de5",  # Perception agent
    "emotion": None,    # Will be filled when emotion agent starts
    "narration": None,  # Will be filled when narration agent starts
    "voice": None,      # Will be filled when voice agent starts
    "mixer": None       # Will be filled when mixer agent starts
}

class PhotoRequest(BaseModel):
    photo_url: str

class AudioResponse(BaseModel):
    session_id: str
    status: str
    final_audio_url: str = None
    error: str = None

sessions = {}  # In production, use Redis/database
pending_responses = {}  # Store pending message responses

@coordinator.on_event("startup")
async def coordinator_startup(ctx: Context):
    ctx.logger.info(f"🎯 Coordinator Agent started: {coordinator.address}")

# Message handlers for responses from agents
@coordinator.on_message(model=PerceptionData)
async def handle_perception_response(ctx: Context, sender: str, msg: PerceptionData):
    ctx.logger.info(f"📸 Received perception data for {msg.session_id}")
    pending_responses[f"perception_{msg.session_id}"] = msg

@coordinator.on_message(model=EmotionData)
async def handle_emotion_response(ctx: Context, sender: str, msg: EmotionData):
    ctx.logger.info(f"💭 Received emotion data for {msg.session_id}")
    pending_responses[f"emotion_{msg.session_id}"] = msg

@coordinator.on_message(model=NarrationData)
async def handle_narration_response(ctx: Context, sender: str, msg: NarrationData):
    ctx.logger.info(f"📖 Received narration data for {msg.session_id}")
    pending_responses[f"narration_{msg.session_id}"] = msg

@coordinator.on_message(model=VoiceData)
async def handle_voice_response(ctx: Context, sender: str, msg: VoiceData):
    ctx.logger.info(f"🎤 Received voice data for {msg.session_id}")
    pending_responses[f"voice_{msg.session_id}"] = msg

@coordinator.on_message(model=AudioMixData)
async def handle_mix_response(ctx: Context, sender: str, msg: AudioMixData):
    ctx.logger.info(f"🔊 Received final audio for {msg.session_id}")
    pending_responses[f"mix_{msg.session_id}"] = msg

@coordinator.on_message(model=ErrorMessage)
async def handle_error(ctx: Context, sender: str, msg: ErrorMessage):
    ctx.logger.error(f"❌ Error in {msg.step} for {msg.session_id}: {msg.error}")
    sessions[msg.session_id] = {"status": "error", "error": f"{msg.step}: {msg.error}"}

@app.post("/process-photo", response_model=AudioResponse)
async def process_photo(request: PhotoRequest):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"status": "processing", "step": "perception"}

    # Start async processing
    asyncio.create_task(process_pipeline(session_id, request.photo_url))

    return AudioResponse(session_id=session_id, status="processing")

@app.post("/upload-photo", response_model=AudioResponse)
async def upload_photo(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"status": "processing", "step": "perception"}

    # Save uploaded file
    upload_dir = "storage/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{session_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create accessible URL (in production, upload to cloud storage)
    photo_url = f"http://localhost:8000/uploads/{session_id}_{file.filename}"

    # Start async processing
    asyncio.create_task(process_pipeline(session_id, photo_url))

    return AudioResponse(session_id=session_id, status="processing")

@app.get("/status/{session_id}")
async def get_status(session_id: str):
    if session_id not in sessions:
        return {"error": "Session not found", "session_id": session_id, "status": "not_found"}

    session = sessions[session_id]
    return {
        "session_id": session_id,
        "status": session.get("status", "unknown"),
        "final_audio_url": session.get("final_audio_url"),
        "error": session.get("error")
    }

async def process_pipeline(session_id: str, photo_url: str):
    try:
        # SIMPLIFIED VERSION: Just mark as completed with a mock audio URL
        # Remove this and uncomment the full version when agents are working

        import time
        await asyncio.sleep(3)  # Simulate processing time

        sessions[session_id] = {
            "status": "completed",
            "final_audio_url": f"http://localhost:8000/audio/sample_{session_id}.mp3",
            "perception": {"mock": "data"},
            "emotion": {"mock": "data"},
            "narration": {"mock": "data"},
            "audio_layers": [{"mock": "audio"}]
        }

        """
        # FULL VERSION (uncomment when agents are working):
        ctx = coordinator._ctx  # Get context for logging

        # Step 1: Perception
        sessions[session_id]["step"] = "perception"
        await coordinator.send(AGENT_ADDRESSES["perception"], VisionAnalysisRequest(photo_url=photo_url, session_id=session_id))

        perception_data = await wait_for_response(f"perception_{session_id}", timeout=120)
        sessions[session_id]["perception"] = perception_data.__dict__

        # Step 2: Emotion
        sessions[session_id]["step"] = "emotion"
        await coordinator.send(AGENT_ADDRESSES["emotion"], EmotionRequest(session_id=session_id, perception_data=perception_data.__dict__))

        emotion_data = await wait_for_response(f"emotion_{session_id}", timeout=60)
        sessions[session_id]["emotion"] = emotion_data.__dict__

        # Step 3: Narration
        sessions[session_id]["step"] = "narration"
        await coordinator.send(AGENT_ADDRESSES["narration"], NarrationRequest(session_id=session_id, perception=perception_data.__dict__, emotion=emotion_data.__dict__))

        narration_data = await wait_for_response(f"narration_{session_id}", timeout=60)
        sessions[session_id]["narration"] = narration_data.__dict__

        # Step 4: Voice
        sessions[session_id]["step"] = "voice"
        await coordinator.send(AGENT_ADDRESSES["voice"], VoiceRequest(session_id=session_id, narration_data=narration_data.__dict__, emotion_data=emotion_data.__dict__))

        voice_data = await wait_for_response(f"voice_{session_id}", timeout=120)
        sessions[session_id]["voice"] = voice_data.__dict__

        # Step 5: Audio Mix
        sessions[session_id]["step"] = "mixing"
        await coordinator.send(AGENT_ADDRESSES["mixer"], AudioMixRequest(session_id=session_id, voice_files=voice_data.voice_files, ambient_sounds=perception_data.ambient_sounds))

        mix_data = await wait_for_response(f"mix_{session_id}", timeout=60)

        # Complete
        sessions[session_id] = {
            "status": "completed",
            "final_audio_url": mix_data.final_audio_url,
            "perception": perception_data.__dict__,
            "emotion": emotion_data.__dict__,
            "narration": narration_data.__dict__,
            "audio_layers": voice_data.voice_files
        }
        """

    except Exception as e:
        sessions[session_id] = {"status": "error", "error": str(e)}

async def wait_for_response(key: str, timeout: int = 60):
    """Wait for a response from an agent"""
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < timeout:
        if key in pending_responses:
            response = pending_responses.pop(key)
            return response
        await asyncio.sleep(1)
    raise TimeoutError(f"Timeout waiting for response: {key}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
