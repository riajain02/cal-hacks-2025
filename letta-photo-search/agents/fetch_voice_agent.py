"""
Fetch.ai Voice Processing Agent
Deployed on Fetch.ai network to handle voice input processing
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

# Import the Letta voice processing agent
from agents.letta_voice_agent import VoiceProcessingAgent

# Define message models
class VoiceInputRequest(Model):
    """Request to process voice input"""
    voice_text: str
    session_id: str = "default"
    message_id: str = ""  # For tracking

class VoiceProcessingResponse(Model):
    """Response with processed voice data"""
    session_id: str
    message_id: str  # Same as request for tracking
    intent: str
    entities: List[str]
    context: Dict
    search_query: str
    description: str
    success: bool
    message: str = ""
    processing_time_ms: float = 0.0  # Track processing time

# Initialize the Fetch.ai agent
voice_agent = Agent(
    name="voice_processor_agent",
    port=8002,
    seed="voice_processor_seed_phrase_secure_12345",
    endpoint=["http://127.0.0.1:8002/submit"],
)

# Fund agent if needed
fund_agent_if_low(voice_agent.wallet.address())

# Initialize Letta voice agent (lazy loading)
letta_voice_agent = None

def get_voice_agent():
    """Get or create the Letta voice agent instance"""
    global letta_voice_agent
    if letta_voice_agent is None:
        print("Initializing Letta Voice Processing Agent...")
        letta_voice_agent = VoiceProcessingAgent()
    return letta_voice_agent

# Create protocol for voice processing
voice_protocol = Protocol("VoiceProcessing")

@voice_protocol.on_message(model=VoiceInputRequest)
async def handle_voice_input(ctx: Context, sender: str, msg: VoiceInputRequest):
    """Handle incoming voice input requests"""
    start_time = datetime.now()
    msg_id = msg.message_id or str(uuid.uuid4())

    logger.info("=" * 80)
    logger.info(f"📥 INCOMING VOICE REQUEST [ID: {msg_id}]")
    logger.info(f"   From: {sender}")
    logger.info(f"   Session: {msg.session_id}")
    logger.info(f"   Text: '{msg.voice_text}'")
    logger.info(f"   Timestamp: {start_time.isoformat()}")
    logger.info("=" * 80)

    ctx.logger.info(f"Received voice input from {sender}: '{msg.voice_text}'")

    try:
        # Get voice processing agent
        agent = get_voice_agent()
        logger.info(f"🔄 Processing with Letta Voice Agent...")

        # Process the voice input
        result = agent.process_voice_input(msg.voice_text)

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        logger.info(f"✅ Processing complete in {processing_time:.2f}ms")
        logger.info(f"   Intent: {result['intent']}")
        logger.info(f"   Entities: {result['entities']}")
        logger.info(f"   Search Query: {result['search_query']}")
        logger.info(f"   Context: {result['context']}")

        # Send response
        response = VoiceProcessingResponse(
            session_id=msg.session_id,
            message_id=msg_id,
            intent=result['intent'],
            entities=result['entities'],
            context=result['context'],
            search_query=result['search_query'],
            description=result['description'],
            success=True,
            message=f"Processed voice input successfully",
            processing_time_ms=processing_time
        )

        await ctx.send(sender, response)
        logger.info(f"📤 Response sent to {sender}")
        logger.info("=" * 80)
        ctx.logger.info(f"Sent voice processing response to {sender}")
        ctx.logger.info(f"  Intent: {result['intent']}, Entities: {result['entities']}")

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"❌ ERROR processing voice input: {e}")
        logger.error(f"   Message ID: {msg_id}")
        logger.error(f"   Session: {msg.session_id}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")

        ctx.logger.error(f"Error processing voice input: {e}")
        error_response = VoiceProcessingResponse(
            session_id=msg.session_id,
            message_id=msg_id,
            intent="search",
            entities=[msg.voice_text],
            context={},
            search_query=msg.voice_text,
            description="Error processing input",
            success=False,
            message=f"Error: {str(e)}",
            processing_time_ms=processing_time
        )
        await ctx.send(sender, error_response)
        logger.info("=" * 80)

# Include the protocol
voice_agent.include(voice_protocol)

@voice_agent.on_event("startup")
async def startup(ctx: Context):
    """Startup event handler"""
    logger.info("🚀 " + "=" * 78)
    logger.info("🚀 VOICE PROCESSING AGENT STARTUP")
    logger.info("🚀 " + "=" * 78)
    logger.info(f"   Agent Name: {voice_agent.name}")
    logger.info(f"   Agent Address: {voice_agent.address}")
    logger.info(f"   Port: 8002")
    logger.info(f"   Endpoint: http://127.0.0.1:8002/submit")
    logger.info(f"   Protocol: VoiceProcessing")
    logger.info("=" * 80)

    ctx.logger.info(f"Voice Processing Agent started")
    ctx.logger.info(f"Agent address: {voice_agent.address}")
    ctx.logger.info(f"Agent name: {voice_agent.name}")

    # Pre-initialize voice agent
    try:
        logger.info("🔧 Initializing Letta Voice Processing Agent...")
        get_voice_agent()
        logger.info("✅ Voice processing agent initialized successfully")
        ctx.logger.info("Voice processing agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize voice agent: {e}")
        ctx.logger.error(f"Failed to initialize voice agent: {e}")

@voice_agent.on_interval(period=120.0)
async def heartbeat(ctx: Context):
    """Periodic heartbeat"""
    ctx.logger.info("Voice agent heartbeat - ready for requests")

if __name__ == "__main__":
    print(f"Starting Fetch.ai Voice Processing Agent...")
    print(f"Agent Address: {voice_agent.address}")
    print(f"Agent listening on port 8002")
    print(f"Send VoiceInputRequest messages to process voice input")
    voice_agent.run()
