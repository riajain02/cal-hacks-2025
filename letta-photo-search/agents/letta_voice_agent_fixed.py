"""
Letta Voice Processing Agent (FIXED)
Extracts intent and entities from natural language speech input
Uses Letta AI framework properly
"""
import os
import json
import logging
from typing import Dict, List
from dotenv import load_dotenv

try:
    from letta_client import Letta, LettaRequest
    LETTA_AVAILABLE = True
except ImportError:
    LETTA_AVAILABLE = False
    print("Warning: Letta client not available, using fallback processing")

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceProcessingAgent:
    """
    Letta-powered agent for processing voice input and extracting:
    - Intent: What the user wants to do (search, find, show, etc.)
    - Entities: Specific items being searched for (dog, sunset, coffee, etc.)
    - Context: Additional descriptive information
    """

    def __init__(self):
        """Initialize the Letta voice processing agent"""
        self.api_key = os.getenv('LETTA_API_KEY')
        self.base_url = os.getenv('LETTA_BASE_URL', 'https://api.letta.com')

        if not LETTA_AVAILABLE:
            logger.warning("Letta not available, using fallback mode")
            self.client = None
            self.agent_id = None
            return

        if not self.api_key:
            logger.warning("LETTA_API_KEY not found, using fallback mode")
            self.client = None
            self.agent_id = None
            return

        try:
            # Initialize Letta client
            self.client = Letta(
                api_key=self.api_key,
                base_url=self.base_url
            )

            # Create or get agent
            self.agent_id = self._create_or_get_agent()

            logger.info("✅ Letta Voice Processing Agent initialized")
        except Exception as e:
            logger.error(f"Error initializing Letta: {e}")
            logger.info("Using fallback processing mode")
            self.client = None
            self.agent_id = None

    def _create_or_get_agent(self):
        """Create or retrieve a Letta agent configured for voice processing"""

        if not self.client:
            return None

        # System message for the agent
        system_message = """You are an intelligent voice processing assistant for a photo search system designed for blind users.

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
            # List existing agents
            agents = self.client.agents.list()

            # Look for existing voice agent
            for agent in agents:
                if agent.name == "voice_processor":
                    logger.info("Found existing voice processing agent")
                    return agent.id

            # Create new agent if not found
            logger.info("Creating new voice processing agent...")
            agent = self.client.agents.create(
                name="voice_processor",
                system=system_message,
                llm_config={
                    "model": "gpt-4o-mini",
                    "context_window": 8000
                },
                embedding_config={
                    "embedding_model": "text-embedding-3-small"
                }
            )

            logger.info(f"Created Letta agent with ID: {agent.id}")
            return agent.id

        except Exception as e:
            logger.error(f"Error creating/getting agent: {e}")
            import traceback
            traceback.print_exc()
            return None

    def process_voice_input(self, voice_text: str) -> Dict:
        """
        Process voice/text input and extract structured information

        Args:
            voice_text: The user's natural language query

        Returns:
            Dict with intent, entities, context, search_query, and description
        """
        logger.info(f"Processing input: '{voice_text}'")

        # Use Letta if available, otherwise fallback
        if self.client and self.agent_id:
            return self._letta_process(voice_text)
        else:
            return self._fallback_process(voice_text)

    def _letta_process(self, voice_text: str) -> Dict:
        """Process using Letta AI"""

        try:
            # Send message to Letta agent
            response = self.client.agents.messages.send(
                agent_id=self.agent_id,
                messages=[
                    {
                        "role": "user",
                        "content": voice_text
                    }
                ]
            )

            # Extract response content
            if response and response.messages:
                content = response.messages[-1].content

                # Try to parse JSON response
                try:
                    result = json.loads(content)
                    logger.info(f"✅ Letta extracted: {result}")
                    return result
                except json.JSONDecodeError:
                    # If not JSON, try to extract it
                    logger.warning("Response not JSON, using fallback")
                    return self._fallback_process(voice_text)
            else:
                logger.warning("No response from Letta, using fallback")
                return self._fallback_process(voice_text)

        except Exception as e:
            logger.error(f"Letta processing error: {e}")
            return self._fallback_process(voice_text)

    def _fallback_process(self, voice_text: str) -> Dict:
        """Simple rule-based processing when Letta is not available"""
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
