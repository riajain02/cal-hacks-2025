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
    seed="perception_seed_12345",
    port=8001,
    endpoint=["http://localhost:8001/submit"]
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
        # Step 1: Prepare image URL - convert local paths to base64
        image_url = msg.photo_url
        if not image_url.startswith(('http://', 'https://')):
            # Local file - convert to base64
            import base64
            from pathlib import Path

            ctx.logger.info(f"   → Converting local image to base64: {image_url}")
            image_path = Path(image_url)
            if not image_path.exists():
                raise Exception(f"Image file not found: {image_url}")

            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                # Detect image type from extension
                ext = image_path.suffix.lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }.get(ext, 'image/jpeg')
                image_url = f"data:{mime_type};base64,{image_data}"
                ctx.logger.info(f"   ✓ Image converted to base64 ({len(image_data)} bytes)")

        # Step 2: OpenAI Vision
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
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }],
                    "max_tokens": 800
                }
            )
            response_json = vision_response.json()
            ctx.logger.info(f"   OpenAI response status: {vision_response.status_code}")
            if vision_response.status_code != 200:
                ctx.logger.error(f"   OpenAI error: {response_json}")
                raise Exception(f"OpenAI Vision error: {response_json.get('error', {}).get('message', 'Unknown error')}")
            vision_desc = response_json["choices"][0]["message"]["content"]
            ctx.logger.info(f"   ✓ Vision complete ({len(vision_desc)} chars)")
            ctx.logger.info(f"   📝 Vision preview: {vision_desc[:200]}...")

        # Step 3: GPT-4 structured extraction (replaced Letta for reliability)
        ctx.logger.info("   → GPT-4 structured extraction...")

        extraction_prompt = f"""Extract structured perception data from this image description in VALID JSON format.
Return ONLY the JSON object, with proper double quotes.

Description: {vision_desc}

Return this exact structure:
{{
  "objects": ["list of all objects/items seen"],
  "people_count": number,
  "people_details": [{{"description": "person description", "position": "location", "apparent_mood": "mood"}}],
  "layout": {{
    "foreground": "what's in front",
    "background": "what's behind"
  }},
  "scene_type": "type of scene",
  "setting": "indoor/outdoor description",
  "colors": ["dominant colors"],
  "lighting": "lighting description",
  "ambient_sounds": ["likely sounds in this scene"]
}}"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            extract_response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{
                        "role": "user",
                        "content": extraction_prompt
                    }],
                    "response_format": {"type": "json_object"},
                    "max_tokens": 500
                }
            )

            if extract_response.status_code != 200:
                ctx.logger.error(f"   ❌ GPT-4 extraction error: {extract_response.status_code}")
                raise Exception(f"GPT-4 extraction failed: {extract_response.text}")

            extract_data = extract_response.json()
            perception_text = extract_data["choices"][0]["message"]["content"]
            ctx.logger.info(f"   📝 Extracted content: {perception_text[:200]}...")

            try:
                parsed = json.loads(perception_text)
                ctx.logger.info("   ✓ JSON parsing successful")
            except json.JSONDecodeError as e:
                ctx.logger.error(f"   ❌ JSON parsing failed: {e}")
                raise Exception(f"Failed to parse extraction JSON: {perception_text[:200]}...")

        # Flatten layout if Letta returns nested objects
        layout = parsed.get("layout", {})
        flattened_layout = {}
        for key, value in layout.items():
            if isinstance(value, dict):
                # Flatten nested dict to string (join all values)
                nested_values = [str(v) for v in value.values() if v]
                flattened_layout[key] = " | ".join(nested_values) if nested_values else json.dumps(value)
            else:
                flattened_layout[key] = str(value) if value is not None else ""

        result = PerceptionData(
            session_id=msg.session_id,
            objects=parsed.get("objects", []),
            people_count=parsed.get("people_count", 0),
            people_details=parsed.get("people_details", []),
            layout=flattened_layout,
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
