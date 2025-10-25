"""
Fetch.ai Agent Integration
This agent runs on the Fetch.ai network and interfaces with the Letta photo search agent
"""
import os
import json
from typing import Dict, List
from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Letta photo search agent
try:
    from agents.letta_photo_agent import PhotoSearchAgent
except ImportError:
    from letta_photo_agent import PhotoSearchAgent


# Define message models
class PhotoSearchRequest(Model):
    """Model for photo search requests"""
    query: str
    user_id: str = "anonymous"


class PhotoSearchResponse(Model):
    """Model for photo search responses"""
    success: bool
    photos: List[Dict]
    message: str
    query: str


class PhotoDetailsRequest(Model):
    """Model for requesting specific photo details"""
    photo_id: int


class PhotoDetailsResponse(Model):
    """Model for photo details responses"""
    success: bool
    photo: Dict
    message: str


# Initialize the Fetch.ai agent
fetch_agent = Agent(
    name="photo_search_agent",
    port=8001,
    seed="photo_search_secret_seed_phrase_12345",  # Use a secure seed in production
    endpoint=["http://127.0.0.1:8001/submit"],
)

# Fund agent if needed
fund_agent_if_low(fetch_agent.wallet.address())

# Initialize Letta photo search agent (will be created on first use)
letta_agent = None


def get_letta_agent():
    """Get or create the Letta agent instance"""
    global letta_agent
    if letta_agent is None:
        print("Initializing Letta Photo Search Agent...")
        letta_agent = PhotoSearchAgent()
    return letta_agent


# Create protocol for photo search
photo_protocol = Protocol("PhotoSearch")


@photo_protocol.on_message(model=PhotoSearchRequest)
async def handle_search_request(ctx: Context, sender: str, msg: PhotoSearchRequest):
    """Handle incoming photo search requests"""
    ctx.logger.info(f"Received search query from {sender}: {msg.query}")

    try:
        # Get Letta agent
        agent = get_letta_agent()

        # Search for photos
        results = agent.search_photos(msg.query)

        # Convert results to serializable format
        photos_data = []
        for photo in results:
            photo_copy = dict(photo)
            # Remove non-serializable fields if any
            if 'relevance_score' in photo_copy:
                photo_copy['relevance_score'] = float(photo_copy['relevance_score'])
            photos_data.append(photo_copy)

        # Send response
        response = PhotoSearchResponse(
            success=True,
            photos=photos_data,
            message=f"Found {len(photos_data)} matching photo(s)",
            query=msg.query
        )

        await ctx.send(sender, response)
        ctx.logger.info(f"Sent {len(photos_data)} photo results to {sender}")

    except Exception as e:
        ctx.logger.error(f"Error processing search request: {e}")
        error_response = PhotoSearchResponse(
            success=False,
            photos=[],
            message=f"Error: {str(e)}",
            query=msg.query
        )
        await ctx.send(sender, error_response)


@photo_protocol.on_message(model=PhotoDetailsRequest)
async def handle_details_request(ctx: Context, sender: str, msg: PhotoDetailsRequest):
    """Handle requests for specific photo details"""
    ctx.logger.info(f"Received photo details request from {sender} for photo ID: {msg.photo_id}")

    try:
        # Get Letta agent
        agent = get_letta_agent()

        # Get photo by ID
        photo = agent.get_photo_by_id(msg.photo_id)

        if photo:
            response = PhotoDetailsResponse(
                success=True,
                photo=dict(photo),
                message="Photo details retrieved successfully"
            )
        else:
            response = PhotoDetailsResponse(
                success=False,
                photo={},
                message=f"Photo with ID {msg.photo_id} not found"
            )

        await ctx.send(sender, response)

    except Exception as e:
        ctx.logger.error(f"Error retrieving photo details: {e}")
        error_response = PhotoDetailsResponse(
            success=False,
            photo={},
            message=f"Error: {str(e)}"
        )
        await ctx.send(sender, error_response)


# Include the protocol in the agent
fetch_agent.include(photo_protocol)


@fetch_agent.on_event("startup")
async def startup(ctx: Context):
    """Startup event handler"""
    ctx.logger.info(f"Photo Search Agent started")
    ctx.logger.info(f"Agent address: {fetch_agent.address}")
    ctx.logger.info(f"Agent name: {fetch_agent.name}")

    # Pre-initialize Letta agent
    try:
        get_letta_agent()
        ctx.logger.info("Letta agent initialized successfully")
    except Exception as e:
        ctx.logger.error(f"Failed to initialize Letta agent: {e}")


@fetch_agent.on_interval(period=60.0)
async def heartbeat(ctx: Context):
    """Periodic heartbeat to show agent is alive"""
    ctx.logger.info("Agent heartbeat - running and ready for requests")


if __name__ == "__main__":
    print(f"Starting Fetch.ai Photo Search Agent...")
    print(f"Agent Address: {fetch_agent.address}")
    print(f"Agent will listen on port 8001")
    print(f"Send PhotoSearchRequest messages to search for photos")
    fetch_agent.run()
