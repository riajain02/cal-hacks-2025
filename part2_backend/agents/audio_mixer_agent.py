# agents/audio_mixer_agent.py
from uagents import Agent, Context
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fetch_models import AudioMixRequest, AudioMixData, ErrorMessage
from pydub import AudioSegment
import uuid
from dotenv import load_dotenv

load_dotenv()

audio_mixer_agent = Agent(
    name="audio_mixer_agent",
    seed="mixer_seed_33333"
)

@audio_mixer_agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(f"🎛️  Audio Mixer Agent started: {audio_mixer_agent.address}")

@audio_mixer_agent.on_message(model=AudioMixRequest)
async def mix_audio(ctx: Context, sender: str, msg: AudioMixRequest):
    ctx.logger.info(f"🔊 [5/5] Mixing audio for {msg.session_id}")

    try:
        # This is a simplified mixer - in production you'd use proper spatial audio
        mixed_audio = AudioSegment.empty()
        ctx.logger.info(f"🎛️ Starting mix with empty audio segment")

        # Add main narration (center)
        for voice in msg.voice_files:
            if voice["type"] == "narration":
                # Load and add to center
                audio_path = f"storage/audio/{os.path.basename(voice['url'])}"
                ctx.logger.info(f"🎛️ Looking for narration file: {audio_path}")
                if os.path.exists(audio_path):
                    ctx.logger.info(f"🎛️ Narration file exists, loading...")
                    narration = AudioSegment.from_file(audio_path)
                    ctx.logger.info(f"🎛️ Narration duration: {len(narration)}ms")
                    if len(mixed_audio) == 0:
                        mixed_audio = narration
                        ctx.logger.info(f"🎛️ Set mixed_audio to narration: {len(mixed_audio)}ms")
                    else:
                        mixed_audio = mixed_audio.overlay(narration, position=0)
                        ctx.logger.info(f"🎛️ After overlay, mixed_audio duration: {len(mixed_audio)}ms")
                else:
                    ctx.logger.error(f"🎛️ Narration file NOT found: {audio_path}")

        # Add dialogues (left/right - simplified as overlay)
        for voice in msg.voice_files:
            if voice["type"] == "dialogue":
                audio_path = f"storage/audio/{os.path.basename(voice['url'])}"
                if os.path.exists(audio_path):
                    dialogue = AudioSegment.from_file(audio_path)
                    # Simple pan left/right
                    if voice.get("position") == "left":
                        dialogue = dialogue.pan(-0.5)
                    elif voice.get("position") == "right":
                        dialogue = dialogue.pan(0.5)
                    mixed_audio = mixed_audio.overlay(dialogue, position=1000)  # Slight delay

        # Add ambient sounds
        for sound in msg.ambient_sounds:
            # Generate or load ambient sound
            if "waves" in sound.lower():
                ambient = AudioSegment.from_file("storage/audio/waves.mp3") if os.path.exists("storage/audio/waves.mp3") else AudioSegment.silent(30000)
                mixed_audio = mixed_audio.overlay(ambient, loop=True)

        # Save final mix
        output_filename = f"storage/audio/mix_{msg.session_id}_{uuid.uuid4()}.mp3"
        mixed_audio.export(output_filename, format="mp3")

        final_url = f"http://localhost:9000/static/{os.path.basename(output_filename)}"
        result = AudioMixData(session_id=msg.session_id, final_audio_url=final_url)

        await ctx.send(sender, result)
        ctx.logger.info(f"✅ Audio Mix: {len(mixed_audio)}ms final audio")
        ctx.logger.info(f"📊 Audio Mix JSON: {result.__dict__}")

    except Exception as e:
        ctx.logger.error(f"❌ Error: {e}")
        await ctx.send(sender, ErrorMessage(session_id=msg.session_id, error=str(e), step="mixing"))

if __name__ == "__main__":
    audio_mixer_agent.run()
