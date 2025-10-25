# Part 2 Backend - Photo to Audio System

## 🎯 Complete Setup & Testing

### Prerequisites
1. **All API Keys** in `.env`:
   - OpenAI API key
   - Letta AI API key + 3 agent IDs
   - Fish Audio API key (optional - will fallback to OpenAI TTS)

2. **FFmpeg** for audio processing:
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt install ffmpeg

   # Windows - download from https://ffmpeg.org/download.html
   ```

### 🚀 Quick Start (Recommended)

1. **Activate virtual environment**:
   ```bash
   cd part2_backend
   source venv/bin/activate
   ```

2. **Start all agents automatically**:
   ```bash
   python start_all_agents.py
   ```
   This will start all 5 agents and show their addresses. Copy them to `main.py`.

3. **Start the FastAPI server** (in a new terminal):
   ```bash
   cd part2_backend
   source venv/bin/activate
   python main.py
   ```

4. **Test with a photo**:
   ```bash
   python test_full_pipeline.py /path/to/your/photo.jpg
   ```

### Manual Agent Startup (Alternative)

If you prefer manual control, start each agent in separate terminals:

```bash
cd part2_backend
source venv/bin/activate

# Terminal 1 - Perception
python agents/perception_agent.py

# Terminal 2 - Emotion
python agents/emotion_agent.py

# Terminal 3 - Narration
python agents/narration_agent.py

# Terminal 4 - Voice
python agents/voice_agent.py

# Terminal 5 - Audio Mixer
python agents/audio_mixer_agent.py

# Terminal 6 - FastAPI
python main.py
```

## 🧪 Testing

### Test with Photo Upload
```bash
python test_full_pipeline.py /path/to/photo.jpg
```

### Test with Photo URL (via API)
```bash
curl -X POST "http://localhost:8000/process-photo" \
  -H "Content-Type: application/json" \
  -d '{"photo_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"}'
```

### Check Status
```bash
curl "http://localhost:8000/status/YOUR_SESSION_ID"
```

## 🎵 Fish Audio Setup (Optional)

For the best voice quality, set up Fish Audio:

1. Go to https://fish.audio
2. Sign up for an account
3. Get your API key from dashboard
4. Add it to `.env` as `FISH_AUDIO_API_KEY`

The system will automatically use Fish Audio if available, otherwise fallback to OpenAI TTS.

## 📋 API Endpoints

- `POST /upload-photo` - Upload photo file and start processing
- `POST /process-photo` - Process photo from URL
- `GET /status/{session_id}` - Check processing status
- `GET /audio/{filename}` - Download generated audio
- `GET /uploads/{filename}` - Access uploaded photos

## 🔧 Troubleshooting

### Agent Connection Issues
- Run `python start_all_agents.py` to get all agent addresses
- Update `AGENT_ADDRESSES` in `main.py` with the addresses shown
- Make sure all agents are running before starting FastAPI

### API Key Errors
- Check that all keys in `.env` are valid and not expired
- Letta AI agents must be created and their IDs copied correctly

### Audio Issues
- Install FFmpeg (required for pydub audio processing)
- Check that `storage/audio` and `storage/uploads` directories exist
- Fish Audio may require specific voice IDs - currently uses defaults

### Timeout Errors
- Processing can take 2-5 minutes depending on image complexity
- Check agent logs for errors during processing
- Network timeouts may occur with large images

## 🏗️ Architecture

```
User Uploads Photo
         ↓
    FastAPI Gateway (file/URL)
         ↓
Fetch.ai Coordinator Agent (orchestrates)
         ↓
    ┌─────────────────────────────────────┐
    │        Agent Pipeline               │
    ├─────────────────────────────────────┤
    │ Perception → Emotion → Narration    │
    │     ↓           ↓        ↓          │
    │  GPT-4 Vision  Letta AI  Letta AI   │
    │                                     │
    │     Voice → Audio Mix               │
    │     ↓           ↓                   │
    │  Fish Audio    pydub                │
    └─────────────────────────────────────┘
         ↓
    Immersive Audio Output
```

## 🎯 What Happens When You Upload a Photo

1. **Perception Agent**: Analyzes the photo with GPT-4 Vision + Letta AI
2. **Emotion Agent**: Detects mood and atmosphere from the scene
3. **Narration Agent**: Generates spatial audio description with dialogue
4. **Voice Agent**: Creates voice audio using Fish Audio or OpenAI TTS
5. **Audio Mixer**: Combines all audio layers into final immersive experience

The result is a rich, spatial audio description that brings your photo to life!
