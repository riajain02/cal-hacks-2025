"""
Fish Audio Service
Provides speech-to-text and text-to-speech using Fish Audio API
"""
import os
import httpx
import base64
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class FishAudioService:
    """Service for interacting with Fish Audio API"""

    def __init__(self):
        """Initialize Fish Audio service"""
        self.api_key = os.getenv('FISH_AUDIO_API_KEY')
        self.base_url = "https://api.fish.audio"

        if not self.api_key:
            raise ValueError("FISH_AUDIO_API_KEY not found in environment variables")

        print("✓ Fish Audio Service initialized")

    async def text_to_speech(
        self,
        text: str,
        reference_id: Optional[str] = None,
        format: str = "mp3",
        save_to: Optional[str] = None
    ) -> bytes:
        """
        Convert text to speech using Fish Audio

        Args:
            text: Text to convert to speech
            reference_id: Optional reference voice ID for voice cloning
            format: Audio format (mp3, wav, etc.)
            save_to: Optional file path to save the audio

        Returns:
            Audio data as bytes
        """

        url = f"{self.base_url}/v1/tts"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "format": format,
        }

        # Add reference voice if provided
        if reference_id:
            payload["reference_id"] = reference_id

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                audio_data = response.content

                # Save to file if path provided
                if save_to:
                    Path(save_to).parent.mkdir(parents=True, exist_ok=True)
                    with open(save_to, 'wb') as f:
                        f.write(audio_data)
                    print(f"✓ Audio saved to {save_to}")

                return audio_data

            except httpx.HTTPStatusError as e:
                print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                print(f"Error in text_to_speech: {e}")
                raise

    async def speech_to_text(
        self,
        audio_file: str,
        language: str = "en"
    ) -> str:
        """
        Convert speech to text using Fish Audio

        Args:
            audio_file: Path to audio file
            language: Language code (default: 'en')

        Returns:
            Transcribed text
        """

        url = f"{self.base_url}/v1/asr"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        # Read audio file
        with open(audio_file, 'rb') as f:
            audio_data = f.read()

        files = {
            'audio': (Path(audio_file).name, audio_data, 'audio/mpeg')
        }

        data = {
            'language': language
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    files=files,
                    data=data
                )
                response.raise_for_status()

                result = response.json()
                text = result.get('text', '')

                print(f"✓ Transcribed: '{text}'")
                return text

            except httpx.HTTPStatusError as e:
                print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                print(f"Error in speech_to_text: {e}")
                raise

    async def text_to_speech_base64(
        self,
        text: str,
        reference_id: Optional[str] = None
    ) -> str:
        """
        Convert text to speech and return as base64 string

        Args:
            text: Text to convert
            reference_id: Optional reference voice ID

        Returns:
            Base64 encoded audio data
        """

        audio_data = await self.text_to_speech(text, reference_id=reference_id)
        return base64.b64encode(audio_data).decode('utf-8')


# Fallback to OpenAI TTS if Fish Audio fails
class OpenAITTSFallback:
    """Fallback TTS using OpenAI"""

    def __init__(self):
        """Initialize OpenAI TTS fallback"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        print("✓ OpenAI TTS Fallback initialized")

    async def text_to_speech(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        save_to: Optional[str] = None
    ) -> bytes:
        """
        Convert text to speech using OpenAI

        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: Model to use (tts-1 or tts-1-hd)
            save_to: Optional file path to save the audio

        Returns:
            Audio data as bytes
        """

        url = f"{self.base_url}/audio/speech"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "input": text,
            "voice": voice
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                audio_data = response.content

                # Save to file if path provided
                if save_to:
                    Path(save_to).parent.mkdir(parents=True, exist_ok=True)
                    with open(save_to, 'wb') as f:
                        f.write(audio_data)
                    print(f"✓ Audio saved to {save_to}")

                return audio_data

            except Exception as e:
                print(f"Error in OpenAI text_to_speech: {e}")
                raise


# Unified TTS service with fallback
class UnifiedTTSService:
    """Unified TTS service that tries Fish Audio first, falls back to OpenAI"""

    def __init__(self):
        """Initialize unified TTS service"""
        self.fish_audio = None
        self.openai_tts = None

        # Try to initialize Fish Audio
        try:
            self.fish_audio = FishAudioService()
        except Exception as e:
            print(f"Could not initialize Fish Audio: {e}")

        # Try to initialize OpenAI
        try:
            self.openai_tts = OpenAITTSFallback()
        except Exception as e:
            print(f"Could not initialize OpenAI TTS: {e}")

        if not self.fish_audio and not self.openai_tts:
            raise ValueError("No TTS service available. Please configure Fish Audio or OpenAI API keys.")

        print("✓ Unified TTS Service initialized")

    async def text_to_speech(
        self,
        text: str,
        save_to: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> bytes:
        """
        Convert text to speech, trying Fish Audio first, then OpenAI

        Args:
            text: Text to convert
            save_to: Optional file path to save audio
            reference_id: Optional Fish Audio voice reference ID

        Returns:
            Audio data as bytes
        """

        # Try Fish Audio first
        if self.fish_audio:
            try:
                print("🔥 USING FISH AUDIO FOR TTS (PREFERRED)")
                result = await self.fish_audio.text_to_speech(text, reference_id=reference_id, save_to=save_to)
                print("✅ Fish Audio TTS generated successfully")
                return result
            except Exception as e:
                print(f"🔥 FISH AUDIO FAILED: {e}")
                print("🔥 FALLBACK: USING OPENAI TTS")

        # Fall back to OpenAI
        if self.openai_tts:
            try:
                result = await self.openai_tts.text_to_speech(text, save_to=save_to)
                print("✅ OpenAI TTS generated successfully")
                return result
            except Exception as e:
                print(f"❌ OpenAI TTS also failed: {e}")
                raise

        raise ValueError("All TTS services failed")


# Test function
async def test_service():
    """Test the Fish Audio service"""
    print("\n" + "="*60)
    print("TESTING FISH AUDIO SERVICE")
    print("="*60 + "\n")

    try:
        service = UnifiedTTSService()

        test_text = "Hello! I found three photos matching your search for a happy dog. The first result shows a golden retriever playing in the park."

        print(f"Converting text to speech: '{test_text[:50]}...'")

        audio = await service.text_to_speech(
            text=test_text,
            save_to="test_output.mp3"
        )

        print(f"✓ Generated {len(audio)} bytes of audio")
        print("✓ Audio saved to test_output.mp3")

    except Exception as e:
        print(f"Error testing service: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_service())
