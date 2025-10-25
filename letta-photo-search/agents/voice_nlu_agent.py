"""
AI-Powered Voice Processing Agent
Uses OpenAI for natural language understanding
Extracts intent and entities from voice/text input
"""
import os
import json
import logging
from typing import Dict, List
from dotenv import load_dotenv

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available, using fallback processing")

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceNLUAgent:
    """
    AI-powered agent for processing voice input using OpenAI and extracting:
    - Intent: What the user wants to do (search, find, show, etc.)
    - Entities: Specific items being searched for (dog, sunset, coffee, etc.)
    - Context: Additional descriptive information
    """

    def __init__(self):
        """Initialize the AI voice processing agent"""
        self.api_key = os.getenv('OPENAI_API_KEY')

        if not OPENAI_AVAILABLE or not self.api_key:
            logger.warning("OpenAI not available, using rule-based fallback")
            self.client = None
            return

        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("✅ OpenAI Voice NLU Agent initialized")
        except Exception as e:
            logger.error(f"Error initializing OpenAI: {e}")
            self.client = None

    def process_voice_input(self, voice_text: str) -> Dict:
        """
        Process voice/text input and extract structured information

        Args:
            voice_text: The user's natural language query

        Returns:
            Dict with intent, entities, context, search_query, and description
        """
        logger.info(f"Processing input: '{voice_text}'")

        # Use AI if available, otherwise fallback
        if self.client:
            return self._ai_process(voice_text)
        else:
            return self._fallback_process(voice_text)

    def _ai_process(self, voice_text: str) -> Dict:
        """Process using OpenAI for intelligent extraction"""

        system_prompt = """You are an intelligent voice processing assistant for a photo search system designed for blind users.

Your job is to analyze natural language queries and extract:

1. INTENT: What the user wants to do
   - search: Looking for specific photos
   - describe: Want description of results
   - navigate: Browse through photos

2. ENTITIES: Specific items/objects/scenes being searched for
   - Objects: dog, cat, coffee cup, laptop, etc.
   - Scenes: sunset, beach, mountain, workspace, etc.
   - Attributes: color, mood, setting, etc.

3. CONTEXT: Additional descriptive information
   - Settings: outdoor, indoor, nature
   - Mood: happy, peaceful, energetic
   - Time: morning, sunset, night
   - Qualities: beautiful, colorful, cozy

Always return ONLY a valid JSON response in this exact format (no markdown, no code blocks):
{
    "intent": "search",
    "entities": ["primary_entity", "additional_entities"],
    "context": {
        "setting": "outdoor/indoor/nature",
        "mood": "description",
        "attributes": ["attribute1", "attribute2"]
    },
    "search_query": "refined search query for image search",
    "description": "Natural language description of what user is looking for"
}

Examples:
Input: "Find me a picture of a happy dog"
Output: {"intent": "search", "entities": ["dog"], "context": {"mood": "happy", "attributes": ["happy", "pet"]}, "search_query": "happy dog", "description": "Looking for a cheerful, happy dog photo"}

Input: "Show me a peaceful sunset at the beach"
Output: {"intent": "search", "entities": ["sunset", "beach"], "context": {"setting": "outdoor", "mood": "peaceful", "attributes": ["peaceful", "serene", "ocean"]}, "search_query": "peaceful sunset beach ocean", "description": "Looking for a tranquil beach sunset scene"}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": voice_text}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={ "type": "json_object" }
            )

            result_text = response.choices[0].message.content.strip()
            logger.info(f"AI response: {result_text}")

            # Parse JSON response
            result = json.loads(result_text)

            # Ensure all required fields exist
            result.setdefault('intent', 'search')
            result.setdefault('entities', [])
            result.setdefault('context', {})
            result.setdefault('search_query', voice_text)
            result.setdefault('description', f"Looking for: {voice_text}")

            logger.info(f"✅ Extracted: intent={result['intent']}, entities={result['entities']}")
            return result

        except Exception as e:
            logger.error(f"AI processing error: {e}")
            logger.info("Falling back to rule-based processing")
            return self._fallback_process(voice_text)

    def _fallback_process(self, voice_text: str) -> Dict:
        """Simple rule-based processing when AI is not available"""
        text_lower = voice_text.lower()

        # Extract intent
        intent = "search"
        if any(word in text_lower for word in ["show", "find", "search", "look for", "want to see"]):
            intent = "search"
        elif any(word in text_lower for word in ["describe", "tell me about", "what is"]):
            intent = "describe"

        # Extract entities using simple keyword matching
        entities = []
        keywords = {
            'dog': ['dog', 'puppy', 'retriever', 'labrador', 'beagle'],
            'cat': ['cat', 'kitten', 'tabby', 'feline'],
            'sunset': ['sunset', 'sunrise', 'dusk', 'dawn'],
            'beach': ['beach', 'ocean', 'sea', 'shore'],
            'coffee': ['coffee', 'latte', 'cappuccino', 'espresso'],
            'nature': ['nature', 'forest', 'tree', 'mountain', 'landscape'],
            'workspace': ['workspace', 'desk', 'office', 'computer', 'laptop']
        }

        for entity, synonyms in keywords.items():
            if any(syn in text_lower for syn in synonyms):
                entities.append(entity)

        # Extract context/mood
        context = {}
        if any(word in text_lower for word in ['happy', 'cheerful', 'joyful', 'playful']):
            context['mood'] = 'happy'
        elif any(word in text_lower for word in ['peaceful', 'calm', 'serene', 'tranquil']):
            context['mood'] = 'peaceful'
        elif any(word in text_lower for word in ['beautiful', 'stunning', 'gorgeous']):
            context['attributes'] = ['beautiful']

        if any(word in text_lower for word in ['outdoor', 'outside', 'nature']):
            context['setting'] = 'outdoor'
        elif any(word in text_lower for word in ['indoor', 'inside']):
            context['setting'] = 'indoor'

        # Generate search query
        search_query = ' '.join(entities) if entities else voice_text

        result = {
            'intent': intent,
            'entities': entities,
            'context': context,
            'search_query': search_query,
            'description': f"Looking for: {search_query}"
        }

        logger.info(f"✅ Fallback extracted: {result}")
        return result


# For backwards compatibility
class VoiceProcessingAgent(VoiceNLUAgent):
    """Alias for backwards compatibility"""
    pass
