# agents/emotion_agent.py
from uagents import Agent, Context
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fetch_models import EmotionRequest, EmotionData, ErrorMessage
import httpx, json
from dotenv import load_dotenv

load_dotenv()

emotion_agent = Agent(
    name="emotion_agent",
    seed="emotion_seed_67890",
    port=8002,
    endpoint=["http://localhost:8002/submit"]
)

LETTA_API_KEY = os.getenv("LETTA_API_KEY")
EMOTION_AGENT_ID = os.getenv("EMOTION_AGENT_ID")

@emotion_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"💭 Emotion Agent started: {emotion_agent.address}")

@emotion_agent.on_message(model=EmotionRequest)
async def detect_emotion(ctx: Context, sender: str, msg: EmotionRequest):
    ctx.logger.info(f"🎭 [2/5] Detecting emotion for {msg.session_id}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            letta_response = await client.post(
                f"https://api.letta.com/v1/agents/{EMOTION_AGENT_ID}/messages",
                headers={"Authorization": f"Bearer {LETTA_API_KEY}"},
                json={"messages": [{"role": "user", "content": f"Analyze emotion:\n\n{json.dumps(msg.perception_data, indent=2)}"}], "stream": False}
            )
            letta_data = letta_response.json()
            emotion_text = next((m.get("content", "") for m in letta_data.get("messages", []) if m.get("message_type") == "assistant_message"), "{}")

            # Parse JSON (handle mixed quotes from Letta AI)
            json_start = emotion_text.find('{')
            json_end = emotion_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_content = emotion_text[json_start:json_end]
                # Fix mixed quotes
                import re
                json_content = re.sub(r"'([^']*)':", r'"\1":', json_content)  # Keys
                json_content = re.sub(r": '([^']*)'", r': "\1"', json_content)  # String values
                json_content = re.sub(r": '([^']*)',", r': "\1",', json_content)  # String values with comma
                json_content = re.sub(r": '([^']*)'}", r': "\1"}', json_content)  # String values at end
                json_content = re.sub(r"'([^']*)'", r'"\1"', json_content)  # Fix single quotes in arrays

                try:
                    parsed = json.loads(json_content)
                except json.JSONDecodeError:
                    parsed = {"mood": "neutral", "emotion_tags": [], "tone": "neutral", "intensity": "medium", "voice_characteristics": {}, "ambient_mood": "calm"}

        result = EmotionData(
            session_id=msg.session_id,
            mood=parsed.get("mood", "neutral"),
            emotion_tags=parsed.get("emotion_tags", []),
            tone=parsed.get("tone", "neutral"),
            intensity=parsed.get("intensity", "medium"),
            voice_characteristics=parsed.get("voice_characteristics", {}),
            ambient_mood=parsed.get("ambient_mood", "calm")
        )

        await ctx.send(sender, result)
        # ctx.logger.info(f"✅ Emotion: {result.mood} ({result.intensity})")
        # ctx.logger.info(f"📊 Emotion JSON: {result.__dict__}")

    except Exception as e:
        ctx.logger.error(f"❌ Error: {e}")
        await ctx.send(sender, ErrorMessage(session_id=msg.session_id, error=str(e), step="emotion"))

if __name__ == "__main__":
    emotion_agent.run()
