#!/usr/bin/env python3
"""
generate_sample_audio.py - Create a sample audio file for testing
"""

from pydub import AudioSegment
from pydub.generators import Sine
import os

# Create storage directory if it doesn't exist
os.makedirs("storage/audio", exist_ok=True)

print("🎵 Generating sample audio...")

# Create a simple 10-second audio with some beeps (simulating voice narration)
audio = AudioSegment.silent(duration=1000)  # 1 second silence

# Add some beeps to simulate speech
for i in range(5):
    beep = Sine(440 + i*100).to_audio_segment(duration=500)  # Different frequencies
    audio += beep
    audio += AudioSegment.silent(duration=300)  # Pause between "words"

# Add ocean wave sounds (simulated)
wave_sound = Sine(100).to_audio_segment(duration=3000).apply_gain(-20)
audio = audio.overlay(wave_sound, loop=True)

# Export as MP3
output_path = "storage/audio/sample_audio.mp3"
audio.export(output_path, format="mp3", bitrate="128k")

print(f"✅ Sample audio created: {output_path}")
print(f"   Duration: {len(audio)/1000:.1f} seconds")
print("   This simulates: 'You stand on a beautiful beach...' + ocean waves")

# Also create the specific file from our test
import shutil
sample_session = "sample_c47c843d-e209-4804-a61b-d917bad0e2d9"
shutil.copy(output_path, f"storage/audio/{sample_session}.mp3")
print(f"✅ Copied to: storage/audio/{sample_session}.mp3")
