"""
Story Agent Client
Provides a simple HTTP interface to interact with the uagents story system
"""
import httpx
import uuid
import json
import os
import time
from pathlib import Path
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Coordinator agent REST API endpoint
COORDINATOR_ENDPOINT = "http://localhost:8006/api/generate"

# Response storage directory
RESPONSE_DIR = Path("storage/responses")
RESPONSE_DIR.mkdir(parents=True, exist_ok=True)


class StoryAgentClient:
    """
    Client for interacting with the story generation agent system
    """

    def __init__(self):
        """Initialize the client"""
        self.coordinator_endpoint = COORDINATOR_ENDPOINT
        self.response_dir = RESPONSE_DIR
        logger.info(f"Story Agent Client initialized")
        logger.info(f"Coordinator: {self.coordinator_endpoint}")
        logger.info(f"Response dir: {self.response_dir}")

    async def generate_story_from_photo(self, photo_url: str, timeout: int = 60) -> Dict:
        """
        Generate a story from a photo by triggering the agent pipeline

        Args:
            photo_url: URL or path to the photo
            timeout: Maximum time to wait for completion (seconds)

        Returns:
            Dict with story data including perception, emotion, and narration
        """
        # Generate session ID
        session_id = str(uuid.uuid4())

        logger.info(f"🚀 Starting story generation for session: {session_id}")
        logger.info(f"📸 Photo URL: {photo_url}")

        try:
            # Send request to coordinator agent
            request_data = {
                "photo_url": photo_url,
                "session_id": session_id
            }

            logger.info(f"Sending request to coordinator: {self.coordinator_endpoint}")

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    self.coordinator_endpoint,
                    json=request_data
                )

                if response.status_code != 200:
                    logger.error(f"Coordinator returned error: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return {
                        "success": False,
                        "error": f"Coordinator error: {response.status_code}",
                        "session_id": session_id
                    }

            logger.info(f"✅ Request sent to coordinator")

            # Poll for response file
            result = await self._wait_for_response(session_id, timeout)

            return result

        except Exception as e:
            logger.error(f"Error generating story: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }

    async def _wait_for_response(self, session_id: str, timeout: int) -> Dict:
        """
        Wait for the response file to be created by the coordinator

        Args:
            session_id: Session ID to wait for
            timeout: Maximum wait time in seconds

        Returns:
            Response data from the agents
        """
        response_file = self.response_dir / f"{session_id}.json"
        start_time = time.time()

        logger.info(f"⏳ Waiting for response file: {response_file}")

        while time.time() - start_time < timeout:
            if response_file.exists():
                logger.info(f"✅ Response file found!")

                # Read response
                try:
                    with open(response_file, 'r') as f:
                        response_data = json.load(f)

                    # Add success flag
                    response_data['success'] = True

                    logger.info(f"📊 Response data loaded successfully")

                    return response_data

                except Exception as e:
                    logger.error(f"Error reading response file: {e}")
                    return {
                        "success": False,
                        "error": f"Failed to read response: {str(e)}",
                        "session_id": session_id
                    }

            # Wait a bit before checking again
            await asyncio.sleep(0.5)

        # Timeout reached
        logger.error(f"⏰ Timeout waiting for response ({timeout}s)")
        return {
            "success": False,
            "error": f"Timeout waiting for agents to respond ({timeout}s)",
            "session_id": session_id,
            "message": "The agents are taking longer than expected. Please try again."
        }

    def cleanup_old_responses(self, max_age_hours: int = 24):
        """
        Clean up old response files

        Args:
            max_age_hours: Maximum age of files to keep (hours)
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        cleaned_count = 0
        for response_file in self.response_dir.glob("*.json"):
            file_age = current_time - response_file.stat().st_mtime
            if file_age > max_age_seconds:
                response_file.unlink()
                cleaned_count += 1

        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} old response files")


# Import asyncio at the end to avoid circular imports
import asyncio


# Test function
async def test_story_client():
    """Test the story agent client"""
    client = StoryAgentClient()

    # Test with a sample image URL
    test_url = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"

    print(f"\n🧪 Testing story generation with URL: {test_url}")

    result = await client.generate_story_from_photo(test_url, timeout=60)

    print(f"\n📊 Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(test_story_client())
