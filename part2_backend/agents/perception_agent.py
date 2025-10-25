# agents/perception_agent.py
from uagents import Agent, Context
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fetch_models import VisionAnalysisRequest, PerceptionData, ErrorMessage
import httpx, json
from dotenv import load_dotenv

load_dotenv()

perception_agent = Agent(
    name="perception_agent",
    seed="perception_seed_12345"
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LETTA_API_KEY = os.getenv("LETTA_API_KEY")
PERCEPTION_AGENT_ID = os.getenv("PERCEPTION_AGENT_ID")

@perception_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"🔍 Perception Agent started: {perception_agent.address}")

@perception_agent.on_message(model=VisionAnalysisRequest)
async def analyze_image(ctx: Context, sender: str, msg: VisionAnalysisRequest):
    ctx.logger.info(f"📸 [1/5] Analyzing image for {msg.session_id}")

    try:
        # Step 1: OpenAI Vision
        ctx.logger.info("   → GPT-4o Vision analysis...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            vision_response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this image in extreme detail. Describe: 1) ALL objects, 2) Number of people and their positions/moods, 3) Spatial layout, 4) Colors/lighting, 5) Scene context. Be exhaustive."},
                            {"type": "image_url", "image_url": {"url": msg.photo_url}}
                        ]
                    }],
                    "max_tokens": 800
                }
            )
            vision_desc = vision_response.json()["choices"][0]["message"]["content"]
            ctx.logger.info(f"   ✓ Vision complete ({len(vision_desc)} chars)")

        # Step 2: Letta AI structured extraction
        ctx.logger.info("   → Letta AI extraction...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            letta_response = await client.post(
                f"https://api.letta.ai/v1/agents/{PERCEPTION_AGENT_ID}/messages",
                headers={"Authorization": f"Bearer {LETTA_API_KEY}"},
                json={"message": f"Extract structured data:\n\n{vision_desc}", "stream": False}
            )
            letta_data = letta_response.json()
            perception_text = next((m.get("content", "") for m in letta_data.get("messages", []) if m.get("message_type") == "assistant_message"), "{}")

            # Parse JSON
            json_start = perception_text.find('{')
            json_end = perception_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                parsed = json.loads(perception_text[json_start:json_end])
            else:
                parsed = {"objects": ["scene"], "people_count": 0, "people_details": [], "layout": {}, "scene_type": "unknown", "setting": "unknown", "colors": [], "lighting": "natural", "ambient_sounds": []}

        result = PerceptionData(
            session_id=msg.session_id,
            objects=parsed.get("objects", []),
            people_count=parsed.get("people_count", 0),
            people_details=parsed.get("people_details", []),
            layout=parsed.get("layout", {}),
            scene_type=parsed.get("scene_type", "unknown"),
            setting=parsed.get("setting", "unknown"),
            colors=parsed.get("colors", []),
            lighting=parsed.get("lighting", "natural"),
            ambient_sounds=parsed.get("ambient_sounds", [])
        )

        await ctx.send(sender, result)
        ctx.logger.info(f"✅ Perception: {result.people_count} people, {len(result.objects)} objects")

    except Exception as e:
        ctx.logger.error(f"❌ Error: {e}")
        await ctx.send(sender, ErrorMessage(session_id=msg.session_id, error=str(e), step="perception"))

if __name__ == "__main__":
    perception_agent.run()
