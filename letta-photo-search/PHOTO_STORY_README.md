# 📸 Photo Story Generator - Setup Guide

This feature uses three specialized Letta AI agents to analyze photos and generate compelling narratives:

1. **Perception Agent** - Analyzes visual content (objects, people, colors, lighting)
2. **Emotion Agent** - Detects mood, tone, and emotional atmosphere
3. **Narration Agent** - Creates a story from the analysis

## 🚀 Quick Start

### Step 1: Start the Story Agents

In one terminal, run the story agents:

```bash
python run_story_agents.py
```

This will start all four agents:
- Perception Agent (port 8001)
- Emotion Agent (port 8002)
- Narration Agent (port 8003)
- Coordinator Agent (port 8006)

You should see:
```
======================================================================
✅ ALL STORY AGENTS RUNNING
======================================================================

Started 4 agents:
  ✓ Perception Agent (PID 12345)
  ✓ Emotion Agent (PID 12346)
  ✓ Narration Agent (PID 12347)
  ✓ Coordinator Agent (PID 12348)
```

### Step 2: Start the Flask Backend

In another terminal, run the Flask app:

```bash
python app_enhanced.py
```

You should see:
```
==============================================================
ENHANCED ACCESSIBLE PHOTO SEARCH - BACKEND SERVER
==============================================================

Starting server...
UI will be available at: http://localhost:5000
```

### Step 3: Open the Photo Story Generator

Visit: **http://localhost:5000/story**

Or click the "📸 Generate Photo Story" button on the home page.

## 📖 How to Use

### Upload a Photo

1. **Drag & Drop**: Drag an image file onto the upload area
2. **Click to Browse**: Click the upload area to select a file
3. **Use Camera**: Click "Use Camera" to capture a photo directly

### Generate Story

1. After uploading/capturing a photo, click "✨ Generate Story"
2. The agents will process your photo (this takes 30-60 seconds)
3. Watch the progress as each agent completes its analysis
4. View the complete story with:
   - Visual analysis (objects, scene type, colors, lighting)
   - Emotional analysis (mood, tone, intensity)
   - Generated narrative

## 🏗️ Architecture

```
User uploads photo
    ↓
Flask uploads to /data/photos/uploaded/
    ↓
Flask sends request to Coordinator Agent (port 8006)
    ↓
Coordinator triggers two agents in parallel:
    ├─ Perception Agent (GPT-4o Vision + Letta Perception)
    └─ Emotion Agent (Letta Emotion)
    ↓
Both complete → Coordinator triggers Narration Agent
    ↓
Narration Agent generates story (Letta Narration)
    ↓
Coordinator saves result to storage/responses/{session_id}.json
    ↓
Flask reads result and returns to UI
    ↓
UI displays the story
```

## 🔧 Technical Details

### Agent Communication

The agents use the **uagents** framework (Fetch.ai) for message passing:

- Each agent runs as an independent service
- Agents communicate using typed messages (defined in `fetch_models.py`)
- The Coordinator orchestrates the workflow

### Letta Integration

Each agent calls Letta AI APIs:

```python
# Perception Agent
PERCEPTION_AGENT_ID = os.getenv("PERCEPTION_AGENT_ID")
# Uses: GPT-4o for vision → Letta AI for structured extraction

# Emotion Agent
EMOTION_AGENT_ID = os.getenv("EMOTION_AGENT_ID")
# Analyzes perception data → extracts emotions

# Narration Agent
NARRATION_AGENT_ID = os.getenv("NARRATION_AGENT_ID")
# Takes perception + emotion → generates story
```

### API Endpoints

**Backend Endpoints:**

```
POST /api/photos/upload
  - Upload a photo
  - Returns: { photo_url, filename, filepath }

POST /api/story/generate
  - Generate story from photo
  - Body: { photo_url, photo_path }
  - Returns: { perception, emotion, narration, session_id }

GET /api/photos/uploaded/<filename>
  - Serve uploaded photos
```

**UI Routes:**

```
GET /story
  - Photo story generator page

GET /
  - Main search page (with link to story generator)
```

## 📁 File Structure

```
letta-photo-search/
├── agents/
│   ├── perception_agent.py      # Analyzes visual content
│   ├── emotion_agent.py          # Detects emotions
│   ├── narration_agent.py        # Generates story
│   ├── coordinator_agent.py      # Orchestrates workflow
│   └── story_agent_client.py    # HTTP client for Flask
├── ui/
│   ├── story.html                # Photo story UI
│   ├── story.js                  # Frontend logic
│   └── style_new.css             # Shared styles
├── data/
│   └── photos/
│       └── uploaded/             # User-uploaded photos
├── storage/
│   └── responses/                # Agent response cache
├── logs/                         # Agent logs
├── fetch_models.py               # Data models for agents
├── run_story_agents.py           # Start all story agents
└── app_enhanced.py               # Flask backend
```

## 🐛 Troubleshooting

### Agents Not Starting

**Problem:** Agents fail to start or crash immediately

**Solution:**
```bash
# Check logs for errors
tail -f logs/perception_agent.log
tail -f logs/emotion_agent.log
tail -f logs/narration_agent.log
tail -f logs/coordinator_agent.log

# Verify environment variables
cat .env | grep -E "LETTA_API_KEY|PERCEPTION_AGENT_ID|EMOTION_AGENT_ID|NARRATION_AGENT_ID"
```

### Story Generation Timeout

**Problem:** "Timeout waiting for agents to respond"

**Solution:**
- Check that all agents are running: `ps aux | grep python`
- Check agent logs for errors
- Verify Letta API is accessible
- Try with a simpler image (smaller file size)

### Photo Upload Failed

**Problem:** Error uploading photo

**Solution:**
- Verify file is a valid image (PNG, JPG, JPEG, GIF, WEBP)
- Check file size (recommended < 5MB)
- Ensure `data/photos/uploaded/` directory exists and is writable

### Coordinator Not Responding

**Problem:** Agents run but no response

**Solution:**
```bash
# Check coordinator is running
curl http://localhost:8006/submit

# Check response directory permissions
ls -la storage/responses/

# Restart coordinator
# (kill coordinator process and restart)
```

## 🧪 Testing

Test with a sample image:

```bash
# 1. Start agents
python run_story_agents.py

# 2. In another terminal, start Flask
python app_enhanced.py

# 3. Test upload endpoint
curl -X POST http://localhost:5000/api/photos/upload \
  -F "photo=@/path/to/test-image.jpg"

# 4. Test story generation (use photo_url from above)
curl -X POST http://localhost:5000/api/story/generate \
  -H "Content-Type: application/json" \
  -d '{"photo_url": "/api/photos/uploaded/xxx.jpg"}'
```

## 📊 Monitoring

### View Agent Logs in Real-Time

```bash
# Perception agent
tail -f logs/perception_agent.log

# Emotion agent
tail -f logs/emotion_agent.log

# Narration agent
tail -f logs/narration_agent.log

# Coordinator agent
tail -f logs/coordinator_agent.log

# All agents
tail -f logs/*.log
```

### Check Agent Status

```bash
# Check processes
ps aux | grep -E "(perception|emotion|narration|coordinator)_agent"

# Check ports
lsof -i :8001  # Perception
lsof -i :8002  # Emotion
lsof -i :8003  # Narration
lsof -i :8006  # Coordinator
```

## 🎯 Environment Variables

Required in `.env`:

```bash
# Letta AI
LETTA_API_KEY=sk-let-OGZjOWFkNTUtZTYyNC00MDZiLThkZDgtNTc2MDVmMDdjODZjOjc1MmIwZDgwLTc1MDQtNDgyNS04MzhkLWM0Yjk1ZGYwNGVhNg==

# Agent IDs
PERCEPTION_AGENT_ID=agent-57b8e5b6-34df-4373-9258-2879e20224a7
EMOTION_AGENT_ID=agent-dceed622-3a76-4d95-b513-d0e89bc93832
NARRATION_AGENT_ID=agent-858a7154-78e9-48cc-948d-9afa2062438e

# OpenAI (for GPT-4o Vision in Perception Agent)
OPENAI_API_KEY=sk-proj-...
```

## 🔄 Stopping Everything

To stop all agents:

```bash
# In the terminal running agents, press Ctrl+C
# Or kill processes:
pkill -f "perception_agent"
pkill -f "emotion_agent"
pkill -f "narration_agent"
pkill -f "coordinator_agent"
```

## 📝 Example Output

**Perception Data:**
```json
{
  "objects": ["sunset", "ocean", "waves", "sand", "clouds"],
  "scene_type": "outdoor_beach",
  "setting": "tropical beach at sunset",
  "people_count": 0,
  "colors": ["orange", "pink", "blue", "golden"],
  "lighting": "warm golden hour",
  "ambient_sounds": ["waves", "seagulls", "wind"]
}
```

**Emotion Data:**
```json
{
  "mood": "peaceful",
  "emotion_tags": ["serene", "tranquil", "calming"],
  "tone": "warm and inviting",
  "intensity": "medium",
  "ambient_mood": "relaxed"
}
```

**Narration:**
```
You stand on a serene beach at sunset, the warm golden light
bathing the sand and gentle waves lapping at the shore. The sky
is painted in brilliant shades of orange and pink, while wispy
clouds drift across the horizon. The peaceful atmosphere invites
contemplation, as the rhythmic sound of waves creates a soothing
natural symphony. This moment captures the tranquil beauty of
nature at its most serene.
```

## 🎨 Features

- ✅ Photo upload via drag-and-drop or file picker
- ✅ Camera capture support (on compatible devices)
- ✅ Real-time agent progress tracking
- ✅ Comprehensive visual analysis
- ✅ Emotional tone detection
- ✅ AI-generated narrative storytelling
- ✅ Beautiful, accessible UI design
- ✅ Responsive design for mobile/desktop

## 🚧 Future Enhancements

- [ ] Audio narration (text-to-speech)
- [ ] Multi-photo story generation
- [ ] Story export (PDF, audio file)
- [ ] User story history
- [ ] Social sharing
- [ ] Custom narration styles

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review agent logs in `logs/` directory
3. Verify all environment variables are set correctly
4. Ensure all required dependencies are installed

---

**Happy storytelling! 📖✨**
