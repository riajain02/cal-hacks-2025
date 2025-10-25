# agents/voice_agent.py
from uagents import Agent, Context
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fetch_models import VoiceRequest, VoiceData, ErrorMessage
import httpx, json, uuid
from dotenv import load_dotenv

load_dotenv()

voice_agent = Agent(
    name="voice_agent",
    seed="voice_seed_22222",
    port=8004,
    endpoint=["http://localhost:8004/submit"]
)

FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@voice_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"🎵 Voice Agent started: {voice_agent.address}")

@voice_agent.on_message(model=VoiceRequest)
async def generate_voices(ctx: Context, sender: str, msg: VoiceRequest):
    ctx.logger.info(f"🎤 [4/5] Generating voices for {msg.session_id}")

    try:
        voice_files = []

        # Generate main narration
        narration_text = msg.narration_data.get("main_narration", "")
        if narration_text:
            voice_url = await generate_tts(narration_text, "main_narrator", msg.emotion_data)
            voice_files.append({"type": "narration", "position": "center", "url": voice_url})

        # Generate person dialogues
        dialogues = msg.narration_data.get("person_dialogues", [])
        for i, dialogue in enumerate(dialogues):
            person_id = dialogue.get("person_id", i+1)
            text = dialogue.get("dialogue", "")
            if text:
                position = "left" if person_id == 1 else "right"
                voice_url = await generate_tts(text, f"person_{person_id}", msg.emotion_data)
                voice_files.append({"type": "dialogue", "position": position, "person_id": person_id, "url": voice_url})

        result = VoiceData(session_id=msg.session_id, voice_files=voice_files)
        await ctx.send(sender, result)
        ctx.logger.info(f"✅ Voice: {len(voice_files)} audio files generated")

    except Exception as e:
        ctx.logger.error(f"❌ Error: {e}")
        await ctx.send(sender, ErrorMessage(session_id=msg.session_id, error=str(e), step="voice"))

async def generate_tts(text: str, speaker: str, emotion_data: dict) -> str:
    """Generate TTS using Fish Audio or fallback to OpenAI"""
    try:
        # Try Fish Audio first
        if FISH_AUDIO_API_KEY:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.fish.audio/v1/tts",
                    headers={"Authorization": f"Bearer {FISH_AUDIO_API_KEY}"},
                    json={
                        "text": text,
                        "reference_id": "your_reference_voice_id",  # You'll need to set up voice cloning
                        "format": "mp3",
                        "mp3_bitrate": 128
                    }
                )
                if response.status_code == 200:
                    # Save to file and return URL
                    filename = f"storage/audio/{uuid.uuid4()}.mp3"
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    return f"http://localhost:8000/audio/{os.path.basename(filename)}"
    except:
        pass

    # Fallback to OpenAI TTS
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "tts-1",
                "input": text,
                "voice": "alloy"
            }
        )
        filename = f"storage/audio/{uuid.uuid4()}.mp3"
        with open(filename, "wb") as f:
            f.write(response.content)
        return f"http://localhost:8000/audio/{os.path.basename(filename)}"

if __name__ == "__main__":
    voice_agent.run()
