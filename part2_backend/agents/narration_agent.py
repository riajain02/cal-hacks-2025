# agents/narration_agent.py
from uagents import Agent, Context
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fetch_models import NarrationRequest, NarrationData, ErrorMessage
import httpx, json
from dotenv import load_dotenv

load_dotenv()

narration_agent = Agent(
    name="narration_agent",
    seed="narration_seed_11111"
)

LETTA_API_KEY = os.getenv("LETTA_API_KEY")
NARRATION_AGENT_ID = os.getenv("NARRATION_AGENT_ID")

@narration_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"📖 Narration Agent started: {narration_agent.address}")

@narration_agent.on_message(model=NarrationRequest)
async def generate_narration(ctx: Context, sender: str, msg: NarrationRequest):
    ctx.logger.info(f"✍️  [3/5] Generating narration for {msg.session_id}")

    try:
        ctx.logger.warning("🔥 USING LETTA AI FOR NARRATION GENERATION (NO GPT FALLBACK)")
        prompt = f"""Create a narration JSON for an immersive audio experience based on the following data:

PERCEPTION DATA:
{json.dumps(msg.perception, indent=2)}

EMOTION DATA:
{json.dumps(msg.emotion, indent=2)}

Please output ONLY a valid JSON object with these exact keys:
- main_narration: A 3-4 sentence description of the scene, focusing on spatial elements and atmosphere
- person_dialogues: Array of objects with 'person_id', 'dialogue', and 'emotion' (use person details from perception if available)
- ambient_descriptions: Array of sound descriptions (e.g., ['waves', 'wind', 'birds'])

Example output:
{{
  "main_narration": "You stand on a serene beach at sunset, the warm golden light bathing the sand and gentle waves lapping at the shore.",
  "person_dialogues": [
    {{"person_id": 1, "dialogue": "This view is breathtaking.", "emotion": "joyful"}},
    {{"person_id": 2, "dialogue": "I could stay here forever.", "emotion": "content"}}
  ],
  "ambient_descriptions": ["ocean waves", "sea breeze", "distant seagulls"]
}}
"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            letta_response = await client.post(
                f"https://api.letta.com/v1/agents/{NARRATION_AGENT_ID}/messages",
                headers={"Authorization": f"Bearer {LETTA_API_KEY}"},
                json={"messages": [{"role": "user", "content": prompt}], "stream": False}
            )
        letta_data = letta_response.json()
        narration_text = next((m.get("content", "") for m in letta_data.get("messages", []) if m.get("message_type") == "assistant_message"), "{}")

        json_start = narration_text.find('{')
        json_end = narration_text.rfind('}') + 1
        if json_start >= 0:
            parsed = json.loads(narration_text[json_start:json_end])
        else:
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

if __name__ == "__main__":
    narration_agent.run()
