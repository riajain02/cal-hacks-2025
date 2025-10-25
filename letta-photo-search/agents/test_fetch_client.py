"""
Test client for the Fetch.ai Photo Search Agent
"""
import asyncio
from uagents import Agent, Context, Model
from typing import Dict, List


# Define message models (must match the agent's models)
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


# Create test client agent
test_client = Agent(
    name="test_client",
    port=8002,
    seed="test_client_secret_seed_phrase_67890",
    endpoint=["http://127.0.0.1:8002/submit"],
)

# Address of the photo search agent (will be set when we know it)
PHOTO_SEARCH_AGENT_ADDRESS = "agent1qwquu2d237gntfugrnwch38g8jkl3uek5m5s9hxlmq0j82f8ga8s67p0y6c"


@test_client.on_event("startup")
async def startup(ctx: Context):
    """Send a test search query on startup"""
    ctx.logger.info(f"Test client started with address: {test_client.address}")
    await asyncio.sleep(2)  # Wait for other agent to be ready

    # Send test query
    test_query = "dog"
    ctx.logger.info(f"Sending test query: '{test_query}'")

    await ctx.send(
        PHOTO_SEARCH_AGENT_ADDRESS,
        PhotoSearchRequest(query=test_query, user_id="test_user")
    )


@test_client.on_message(model=PhotoSearchResponse)
async def handle_response(ctx: Context, sender: str, msg: PhotoSearchResponse):
    """Handle search response"""
    ctx.logger.info(f"Received response from {sender}")
    ctx.logger.info(f"Success: {msg.success}")
    ctx.logger.info(f"Message: {msg.message}")
    ctx.logger.info(f"Number of photos: {len(msg.photos)}")

    for i, photo in enumerate(msg.photos, 1):
        ctx.logger.info(f"\nPhoto {i}:")
        ctx.logger.info(f"  Title: {photo.get('title')}")
        ctx.logger.info(f"  Description: {photo.get('description')}")


if __name__ == "__main__":
    print("Starting test client...")
    print(f"Client address: {test_client.address}")
    test_client.run()
