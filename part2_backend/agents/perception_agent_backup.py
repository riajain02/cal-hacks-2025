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
        ctx.logger.info(f"📊 Perception JSON: {result.__dict__}")

    except Exception as e:
        ctx.logger.error(f"❌ Error: {e}")
        await ctx.send(sender, ErrorMessage(session_id=msg.session_id, error=str(e), step="perception"))

def parse_vision_fallback(vision_text: str) -> dict:
    """Parse GPT-4o vision response into structured perception data"""
    vision_lower = vision_text.lower()

    # Extract objects mentioned
    objects = []
    if "wave" in vision_lower or "ocean" in vision_lower or "water" in vision_lower:
        objects.extend(["waves", "ocean", "water"])
    if "sand" in vision_lower or "beach" in vision_lower:
        objects.extend(["sand", "beach"])
    if "cloud" in vision_lower or "sky" in vision_lower:
        objects.extend(["clouds", "sky"])
    if "palm" in vision_lower or "tree" in vision_lower:
        objects.extend(["palm trees", "trees"])
    if "sun" in vision_lower:
        objects.extend(["sun"])
    if "mountain" in vision_lower or "peak" in vision_lower:
        objects.extend(["mountains", "peaks"])
    if "building" in vision_lower or "city" in vision_lower:
        objects.extend(["buildings", "city"])
    if "car" in vision_lower or "vehicle" in vision_lower:
        objects.extend(["cars", "vehicles"])

    # Remove duplicates and filter
    objects = list(set(objects))[:8]  # Limit to 8 objects

    # Extract people count
    people_count = 0
    people_details = []
    if "person" in vision_lower or "people" in vision_lower or "man" in vision_lower or "woman" in vision_lower:
        # Simple heuristic - look for numbers before "person/people"
        import re
        numbers = re.findall(r'(\d+)\s*(?:person|people|man|woman)', vision_lower)
        if numbers:
            people_count = sum(int(n) for n in numbers)
        else:
            people_count = 1  # Default to 1 if mentioned but no number

        # Create basic people details
        for i in range(min(people_count, 3)):  # Max 3 people details
            position = "center" if i == 0 else ("left" if i == 1 else "right")
            people_details.append({
                "position": position,
                "description": f"person {i+1}",
                "apparent_age": "adult",
                "apparent_mood": "neutral"
            })

    # Determine scene type and setting
    if "beach" in vision_lower or "ocean" in vision_lower or "wave" in vision_lower:
        scene_type = "outdoor_beach"
        setting = "tropical beach at sunset"
        ambient_sounds = ["waves", "seagulls", "wind"]
    elif "mountain" in vision_lower or "peak" in vision_lower:
        scene_type = "outdoor_mountain"
        setting = "mountain landscape"
        ambient_sounds = ["wind", "birds"]
    elif "city" in vision_lower or "urban" in vision_lower or "building" in vision_lower:
        scene_type = "urban_city"
        setting = "urban cityscape"
        ambient_sounds = ["traffic", "people"]
    elif "forest" in vision_lower or "tree" in vision_lower:
        scene_type = "outdoor_forest"
        setting = "peaceful forest"
        ambient_sounds = ["birds", "wind", "leaves"]
    else:
        scene_type = "outdoor_nature"
        setting = "natural outdoor scene"
        ambient_sounds = ["nature sounds"]

    # Extract colors
    colors = []
    color_keywords = ["blue", "green", "yellow", "orange", "red", "purple", "pink", "white", "black", "brown", "gold", "silver"]
    for color in color_keywords:
        if color in vision_lower:
            colors.append(color)
    colors = colors[:5]  # Limit to 5 colors

    # Determine lighting
    if "sunset" in vision_lower or "sun" in vision_lower:
        lighting = "warm golden hour"
    elif "night" in vision_lower or "dark" in vision_lower:
        lighting = "nighttime"
    elif "cloud" in vision_lower or "overcast" in vision_lower:
        lighting = "diffuse natural light"
    else:
        lighting = "natural daylight"

    # Create layout based on scene
    layout = {
        "foreground": " | ".join(objects[:3]),
        "center": f"main {scene_type.split('_')[1]} scene",
        "background": f"distant {scene_type.split('_')[0]} elements"
    }

    return {
        "objects": objects,
        "people_count": people_count,
        "people_details": people_details,
        "layout": layout,
        "scene_type": scene_type,
        "setting": setting,
        "colors": colors,
        "lighting": lighting,
        "ambient_sounds": ambient_sounds
    }

if __name__ == "__main__":
    perception_agent.run()
