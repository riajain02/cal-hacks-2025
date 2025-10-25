"""
Fetch.ai Embedding Search Agent
Deployed on Fetch.ai network to handle embedding-based image search
"""
import os
import sys
import uuid
import logging
from datetime import datetime
from typing import Dict, List
from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import the embedding search agent
from agents.embedding_search_agent import EmbeddingSearchAgent

# Define message models
class ImageSearchRequest(Model):
    """Request to search for images"""
    query: str
    entities: List[str] = []
    context: Dict = {}
    top_k: int = 3
    session_id: str = "default"
    message_id: str = ""  # For tracking

class ImageSearchResponse(Model):
    """Response with search results"""
    session_id: str
    message_id: str  # Same as request for tracking
    photos: List[Dict]
    success: bool
    message: str
    query: str
    processing_time_ms: float = 0.0  # Track processing time
    num_results: int = 0  # Number of results found

# Initialize the Fetch.ai agent
search_agent = Agent(
    name="image_search_agent",
    port=8003,
    seed="image_search_seed_phrase_secure_67890",
    endpoint=["http://127.0.0.1:8003/submit"],
)

# Fund agent if needed
fund_agent_if_low(search_agent.wallet.address())

# Initialize embedding search agent (lazy loading)
embedding_search_agent = None

def get_search_agent():
    """Get or create the embedding search agent instance"""
    global embedding_search_agent
    if embedding_search_agent is None:
        print("Initializing Embedding Search Agent...")
        embedding_search_agent = EmbeddingSearchAgent()
    return embedding_search_agent

# Create protocol for image search
search_protocol = Protocol("ImageSearch")

@search_protocol.on_message(model=ImageSearchRequest)
async def handle_search_request(ctx: Context, sender: str, msg: ImageSearchRequest):
    """Handle incoming image search requests"""
    start_time = datetime.now()
    msg_id = msg.message_id or str(uuid.uuid4())

    logger.info("=" * 80)
    logger.info(f"📥 INCOMING SEARCH REQUEST [ID: {msg_id}]")
    logger.info(f"   From: {sender}")
    logger.info(f"   Session: {msg.session_id}")
    logger.info(f"   Query: '{msg.query}'")
    logger.info(f"   Entities: {msg.entities}")
    logger.info(f"   Context: {msg.context}")
    logger.info(f"   Top K: {msg.top_k}")
    logger.info(f"   Timestamp: {start_time.isoformat()}")
    logger.info("=" * 80)

    ctx.logger.info(f"Received search request from {sender}: '{msg.query}'")

    try:
        # Get search agent
        agent = get_search_agent()
        logger.info(f"🔄 Performing vector similarity search...")

        # Perform search with or without context
        if msg.entities or msg.context:
            logger.info(f"   Using context-aware search")
            results = agent.search_with_context(
                query=msg.query,
                entities=msg.entities,
                context=msg.context,
                top_k=msg.top_k
            )
        else:
            logger.info(f"   Using standard embedding search")
            results = agent.search(msg.query, top_k=msg.top_k)

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        # Convert results to serializable format
        photos_data = []
        for photo in results:
            photo_copy = dict(photo)
            # Ensure all numeric values are serializable
            if 'similarity_score' in photo_copy:
                photo_copy['similarity_score'] = float(photo_copy['similarity_score'])
            if 'relevance_score' in photo_copy:
                photo_copy['relevance_score'] = int(photo_copy['relevance_score'])
            photos_data.append(photo_copy)

        logger.info(f"✅ Search complete in {processing_time:.2f}ms")
        logger.info(f"   Found: {len(photos_data)} results")
        for i, photo in enumerate(photos_data[:3]):  # Log top 3
            score = photo.get('similarity_score', 0)
            logger.info(f"   #{i+1}: {photo.get('title', 'Unknown')} (score: {score:.3f})")

        # Send response
        response = ImageSearchResponse(
            session_id=msg.session_id,
            message_id=msg_id,
            photos=photos_data,
            success=True,
            message=f"Found {len(photos_data)} matching photo(s)",
            query=msg.query,
            processing_time_ms=processing_time,
            num_results=len(photos_data)
        )

        await ctx.send(sender, response)
        logger.info(f"📤 Response sent to {sender}")
        logger.info("=" * 80)
        ctx.logger.info(f"Sent {len(photos_data)} photo results to {sender}")

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"❌ ERROR processing search request: {e}")
        logger.error(f"   Message ID: {msg_id}")
        logger.error(f"   Session: {msg.session_id}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")

        ctx.logger.error(f"Error processing search request: {e}")
        error_response = ImageSearchResponse(
            session_id=msg.session_id,
            message_id=msg_id,
            photos=[],
            success=False,
            message=f"Error: {str(e)}",
            query=msg.query,
            processing_time_ms=processing_time,
            num_results=0
        )
        await ctx.send(sender, error_response)
        logger.info("=" * 80)

# Include the protocol
search_agent.include(search_protocol)

@search_agent.on_event("startup")
async def startup(ctx: Context):
    """Startup event handler"""
    logger.info("🚀 " + "=" * 78)
    logger.info("🚀 IMAGE SEARCH AGENT STARTUP")
    logger.info("🚀 " + "=" * 78)
    logger.info(f"   Agent Name: {search_agent.name}")
    logger.info(f"   Agent Address: {search_agent.address}")
    logger.info(f"   Port: 8003")
    logger.info(f"   Endpoint: http://127.0.0.1:8003/submit")
    logger.info(f"   Protocol: ImageSearch")
    logger.info("=" * 80)

    ctx.logger.info(f"Image Search Agent started")
    ctx.logger.info(f"Agent address: {search_agent.address}")
    ctx.logger.info(f"Agent name: {search_agent.name}")

    # Pre-initialize search agent
    try:
        logger.info("🔧 Initializing Embedding Search Agent...")
        get_search_agent()
        logger.info("✅ Embedding search agent initialized successfully")
        ctx.logger.info("Embedding search agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize search agent: {e}")
        ctx.logger.error(f"Failed to initialize search agent: {e}")

@search_agent.on_interval(period=120.0)
async def heartbeat(ctx: Context):
    """Periodic heartbeat"""
    ctx.logger.info("Search agent heartbeat - ready for requests")

if __name__ == "__main__":
    print(f"Starting Fetch.ai Image Search Agent...")
    print(f"Agent Address: {search_agent.address}")
    print(f"Agent listening on port 8003")
    print(f"Send ImageSearchRequest messages to search for images")
    search_agent.run()
