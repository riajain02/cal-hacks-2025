# agents/narration_agent.py
from uagents import Agent, Context
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fetch_models import NarrationRequest, NarrationData, ErrorMessage
import httpx, json, uuid
from dotenv import load_dotenv

load_dotenv()

narration_agent = Agent(
    name="narration_agent",
    seed="narration_seed_11111",
    port=8003,
    endpoint=["http://localhost:8003/submit"]
)

LETTA_API_KEY = os.getenv("LETTA_API_KEY")
NARRATION_AGENT_ID = os.getenv("NARRATION_AGENT_ID")
FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY")
FISH_AUDIO_REFERENCE_ID = os.getenv("FISH_AUDIO_REFERENCE_ID", "b545c585f631496c914815291da4e893")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@narration_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"📖 Narration Agent started: {narration_agent.address}")

@narration_agent.on_message(model=NarrationRequest)
async def generate_narration(ctx: Context, sender: str, msg: NarrationRequest):
    ctx.logger.info(f"✍️  [3/5] Generating narration for {msg.session_id}")

    try:
        ctx.logger.info(f"   → Calling Letta Narration Agent: {NARRATION_AGENT_ID}")
        ctx.logger.info(f"   → With perception and emotion data from previous agents")

        async with httpx.AsyncClient(timeout=60.0) as client:
            letta_response = await client.post(
                f"https://api.letta.com/v1/agents/{NARRATION_AGENT_ID}/messages",
                headers={"Authorization": f"Bearer {LETTA_API_KEY}"},
                json={"messages": [{"role": "user", "content": f"Create narration:\n\nPERCEPTION:\n{json.dumps(msg.perception, indent=2)}\n\nEMOTION:\n{json.dumps(msg.emotion, indent=2)}"}], "stream": False}
            )

            ctx.logger.info(f"   HTTP Status: {letta_response.status_code}")

            if letta_response.status_code != 200:
                ctx.logger.error(f"   ❌ HTTP Error: {letta_response.status_code}")
                ctx.logger.error(f"   Response: {letta_response.text}")
                raise Exception(f"Letta AI HTTP error {letta_response.status_code}")

            letta_data = letta_response.json()
            ctx.logger.info(f"   📦 Raw API response received")
            narration_text = next((m.get("content", "") for m in letta_data.get("messages", []) if m.get("message_type") == "assistant_message"), "{}")

            json_start = narration_text.find('{')
            json_end = narration_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_content = narration_text[json_start:json_end]
                # Fix mixed quotes
                import re
                json_content = re.sub(r"'([^']*)':", r'"\1":', json_content)  # Keys
                json_content = re.sub(r": '([^']*)'", r': "\1"', json_content)  # String values
                json_content = re.sub(r": '([^']*)',", r': "\1",', json_content)  # String values with comma
                json_content = re.sub(r": '([^']*)'}", r': "\1"}', json_content)  # String values at end
                json_content = re.sub(r"'([^']*)'", r'"\1"', json_content)  # Fix single quotes in arrays

                try:
                    parsed = json.loads(json_content)
                    ctx.logger.info(f"   ✓ JSON parsing successful")
                except json.JSONDecodeError as e:
                    ctx.logger.error(f"   ❌ JSON parsing failed: {e}")
                    ctx.logger.error(f"   Content: {json_content[:200]}...")
                    parsed = {"main_narration": "Scene description unavailable.", "person_dialogues": [], "ambient_descriptions": []}
            else:
                ctx.logger.error(f"   ❌ No valid JSON found in narration response")
                ctx.logger.error(f"   Content: {narration_text[:200]}...")
                parsed = {"main_narration": "Scene description unavailable.", "person_dialogues": [], "ambient_descriptions": []}

        result = NarrationData(
            session_id=msg.session_id,
            main_narration=parsed.get("main_narration", "Scene description unavailable."),
            person_dialogues=parsed.get("person_dialogues", []),
            ambient_descriptions=parsed.get("ambient_descriptions", [])
        )

        await ctx.send(sender, result)
        ctx.logger.info(f"✅ Narration: {len(result.main_narration)} chars, {len(result.person_dialogues)} dialogues")
        ctx.logger.info(f"📊 Narration JSON: {result.__dict__}")

    except Exception as e:
        ctx.logger.error(f"❌ Error: {e}")
        await ctx.send(sender, ErrorMessage(session_id=msg.session_id, error=str(e), step="narration"))

async def generate_tts(text: str, ctx: Context) -> str:
    """Generate TTS using Fish Audio or fallback to OpenAI"""
    try:
        # Try Fish Audio first
        if FISH_AUDIO_API_KEY and FISH_AUDIO_REFERENCE_ID:
            ctx.logger.info("🔥 USING FISH AUDIO FOR TTS (PREFERRED)")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.fish.audio/v1/tts",
                    headers={"Authorization": f"Bearer {FISH_AUDIO_API_KEY}"},
                    json={
                        "text": text,
                        "reference_id": FISH_AUDIO_REFERENCE_ID,
                        "format": "mp3",
                        "mp3_bitrate": 128
                    }
                )
                if response.status_code == 200:
                    # Save to file and return URL
                    filename = f"storage/audio/{uuid.uuid4()}.mp3"
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    ctx.logger.info(f"✅ Fish Audio TTS generated: {os.path.basename(filename)}")
                    return f"http://localhost:9000/static/{os.path.basename(filename)}"
                else:
                    ctx.logger.warning(f"🔥 FISH AUDIO FAILED: Status {response.status_code}")
    except Exception as e:
        ctx.logger.warning(f"🔥 FISH AUDIO ERROR: {e}")
        pass

    # Fallback to OpenAI TTS
    ctx.logger.info("🔥 FALLBACK: USING OPENAI TTS (FISH AUDIO FAILED)")
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
        ctx.logger.info(f"✅ OpenAI TTS generated: {os.path.basename(filename)}")
        return f"http://localhost:9000/static/{os.path.basename(filename)}"

if __name__ == "__main__":
    narration_agent.run()
