"""
Fetch.ai Coordinator Agent
Orchestrates the complete voice-to-image-search flow by coordinating other agents
"""
import os
import sys
from typing import Dict, List, Optional
from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Define message models
class UserVoiceQuery(Model):
    """Initial user query (can be voice or text)"""
    query: str
    is_voice: bool = True
    session_id: str = "default"

class CompleteSearchResponse(Model):
    """Final response with all results"""
    session_id: str
    original_query: str
    processed_query: str
    intent: str
    entities: List[str]
    photos: List[Dict]
    audio_description: Optional[str] = None
    success: bool
    message: str

# Response models from other agents
class VoiceProcessingResponse(Model):
    session_id: str
    intent: str
    entities: List[str]
    context: Dict
    search_query: str
    description: str
    success: bool
    message: str = ""

class ImageSearchResponse(Model):
    session_id: str
    photos: List[Dict]
    success: bool
    message: str
    query: str

# Initialize the Fetch.ai coordinator agent
coordinator_agent = Agent(
    name="coordinator_agent",
    port=8004,
    seed="coordinator_seed_phrase_secure_99999",
    endpoint=["http://127.0.0.1:8004/submit"],
)

# Fund agent if needed
fund_agent_if_low(coordinator_agent.wallet.address())

# Store agent addresses (will be populated on startup)
VOICE_AGENT_ADDRESS = "agent1qfpq..."  # Will be set dynamically
SEARCH_AGENT_ADDRESS = "agent1qwer..."  # Will be set dynamically

# Session storage for tracking multi-step workflows
sessions = {}

# Create protocol for coordination
coordinator_protocol = Protocol("Coordination")

@coordinator_protocol.on_message(model=UserVoiceQuery)
async def handle_user_query(ctx: Context, sender: str, msg: UserVoiceQuery):
    """
    Handle user query and orchestrate the complete workflow:
    1. Process voice/text input to extract intent and entities
    2. Search for images using embeddings
    3. Generate audio description
    4. Return complete results
    """
    ctx.logger.info(f"Received user query from {sender}: '{msg.query}'")

    try:
        # Initialize session
        sessions[msg.session_id] = {
            'original_query': msg.query,
            'sender': sender,
            'step': 'voice_processing'
        }

        # Import here to avoid circular dependencies
        from agents.letta_voice_agent import VoiceProcessingAgent
        from agents.clip_search_agent import CLIPSearchAgent

        # Step 1: Process voice input
        ctx.logger.info("Step 1: Processing voice input...")
        voice_agent = VoiceProcessingAgent()
        voice_result = voice_agent.process_voice_input(msg.query)

        sessions[msg.session_id]['voice_result'] = voice_result
        sessions[msg.session_id]['step'] = 'image_search'

        # Step 2: Search for images
        ctx.logger.info("Step 2: Searching for images...")
        search_agent = CLIPSearchAgent()
        photo_results = search_agent.search_with_context(
            query=voice_result['search_query'],
            entities=voice_result['entities'],
            context=voice_result['context'],
            top_k=3
        )

        sessions[msg.session_id]['photo_results'] = photo_results
        sessions[msg.session_id]['step'] = 'complete'

        # Step 3: Generate audio description (optional)
        audio_description = None
        if photo_results:
            audio_description = f"I found {len(photo_results)} photos matching your search. "
            for i, photo in enumerate(photo_results, 1):
                audio_description += f"Result {i}: {photo['title']}. {photo['description']}. "

        # Send complete response
        response = CompleteSearchResponse(
            session_id=msg.session_id,
            original_query=msg.query,
            processed_query=voice_result['search_query'],
            intent=voice_result['intent'],
            entities=voice_result['entities'],
            photos=[dict(p) for p in photo_results],
            audio_description=audio_description,
            success=True,
            message=f"Found {len(photo_results)} matching photos"
        )

        await ctx.send(sender, response)
        ctx.logger.info(f"Sent complete response to {sender} with {len(photo_results)} photos")

        # Clean up session
        if msg.session_id in sessions:
            del sessions[msg.session_id]

    except Exception as e:
        ctx.logger.error(f"Error in coordinator workflow: {e}")
        import traceback
        traceback.print_exc()

        error_response = CompleteSearchResponse(
            session_id=msg.session_id,
            original_query=msg.query,
            processed_query=msg.query,
            intent="search",
            entities=[],
            photos=[],
            audio_description=None,
            success=False,
            message=f"Error: {str(e)}"
        )
        await ctx.send(sender, error_response)

# Include the protocol
coordinator_agent.include(coordinator_protocol)

@coordinator_agent.on_event("startup")
async def startup(ctx: Context):
    """Startup event handler"""
    ctx.logger.info(f"Coordinator Agent started")
    ctx.logger.info(f"Agent address: {coordinator_agent.address}")
    ctx.logger.info(f"Agent name: {coordinator_agent.name}")
    ctx.logger.info("Coordinator ready to orchestrate voice-to-image-search workflows")

@coordinator_agent.on_interval(period=120.0)
async def heartbeat(ctx: Context):
    """Periodic heartbeat"""
    ctx.logger.info(f"Coordinator agent heartbeat - {len(sessions)} active sessions")

if __name__ == "__main__":
    print(f"Starting Fetch.ai Coordinator Agent...")
    print(f"Agent Address: {coordinator_agent.address}")
    print(f"Agent listening on port 8004")
    print(f"Send UserVoiceQuery messages to initiate search workflows")
    print("\nThis agent orchestrates:")
    print("  1. Voice/text processing (intent & entity extraction)")
    print("  2. Embedding-based image search")
    print("  3. Audio description generation")
    coordinator_agent.run()
