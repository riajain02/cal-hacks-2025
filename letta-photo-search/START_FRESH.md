# 🚀 Start Fresh - Quick Start Guide

All the bugs have been fixed! Here's how to start everything fresh:

## ✅ What Was Fixed

1. **Removed bad import**: Removed `from uagents.models import Model` that doesn't exist
2. **Fixed REST endpoint**: Added proper `StoryGenerationResponse` model for the REST API
3. **Coordinator now works**: Can now accept HTTP JSON requests and route to agents

## 🎯 Start Everything (3 Terminals)

### Terminal 1: Start Agents

```bash
cd /Users/mihikabhatnagar/Desktop/hackathon/cal-hacks-2025/letta-photo-search
python3 run_story_agents.py
```

**Expected output:**
```
✅ ALL STORY AGENTS RUNNING
Started 4 agents:
  ✓ Perception Agent (PID XXXXX)
  ✓ Emotion Agent (PID XXXXX)
  ✓ Narration Agent (PID XXXXX)
  ✓ Coordinator Agent (PID XXXXX)
```

**Verify coordinator log:**
```bash
# In another terminal:
tail -f logs/coordinator_agent.log
```

Should see:
```
🎯 Coordinator Agent started: agent1q...
🌐 REST API available at: http://localhost:8006/api/generate
```

### Terminal 2: Start Flask Backend

```bash
cd /Users/mihikabhatnagar/Desktop/hackathon/cal-hacks-2025/letta-photo-search
python3 app_enhanced.py
```

**Expected output:**
```
✓ All agents initialized successfully
Running on http://0.0.0.0:5000 (CTRL + C to quit)
```

### Terminal 3: Start Next.js Frontend

```bash
cd /Users/mihikabhatnagar/Desktop/hackathon/cal-hacks-2025/letta-photo-search/frontend
npm run dev
```

**Expected output:**
```
- Local:        http://localhost:3000
- Ready in Xs
```

## 🧪 Test the Application

### 1. Open Browser
Go to: **http://localhost:3000**

### 2. Search for Photos
- Type or speak: "happy dog"
- Click send or press Enter

### 3. Generate Memory Story
- Click "Generate Memory Story" on any photo
- Watch the agent timeline:
  - ✓ Perception Agent - Analyzing visual content...
  - ✓ Emotion Agent - Detecting emotions and mood...
  - ✓ Narration Agent - Generating story...

### 4. View the Story
- Story text appears
- Click "Play Audio Narration" to hear it

## 🔍 Quick Test from Command Line

Test the REST API directly:

```bash
curl -X POST http://localhost:8006/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "photo_url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800",
    "session_id": "test-12345"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "message": "Story generation started",
  "session_id": "test-12345"
}
```

Then check if the response file is created:
```bash
# Wait ~10-15 seconds for agents to process
ls -lh storage/responses/test-12345.json

# View the result
cat storage/responses/test-12345.json
```

## 📊 Monitor Agent Communication

Watch the coordinator orchestrating all agents:

```bash
tail -f logs/coordinator_agent.log
```

You should see this flow:
```
🌐 HTTP REST request received for session: xxx
🚀 [COORDINATOR] Starting experience for xxx
📸 [1/5] → Perception Agent
📸 Received perception data for xxx
😊 [2/5] → Emotion Agent (with perception data)
😊 Received emotion data for xxx
📝 [3/5] → Narration Agent
📝 Received narration data for xxx
✅ Complete processing for session xxx
📁 Response saved to: storage/responses/xxx.json
```

## ❌ If Something Goes Wrong

### Coordinator crashes?
```bash
# Check the log
cat logs/coordinator_agent.log

# Should NOT see any Python errors
# If you do, the fixes didn't apply correctly
```

### 400 Bad Request error?
```bash
# Make sure you restarted the agents after the fixes
pkill -9 -f "coordinator_agent.py"
python3 run_story_agents.py
```

### Agents won't start?
```bash
# Kill all processes
pkill -9 -f "perception_agent.py"
pkill -9 -f "emotion_agent.py"
pkill -9 -f "narration_agent.py"
pkill -9 -f "coordinator_agent.py"

# Start fresh
python3 run_story_agents.py
```

### Port already in use?
```bash
# Check what's using the port
lsof -i :8006

# Kill it
lsof -ti:8006 | xargs kill -9

# Restart
python3 run_story_agents.py
```

## 🎉 Success Indicators

✅ **All working when you see:**

1. **4 agents running** without crashing
2. **Coordinator log** shows "REST API available"
3. **Flask** shows "All agents initialized successfully"
4. **Next.js** shows "Ready"
5. **Browser** loads at localhost:3000
6. **Search works** and returns photos
7. **Memory generation** shows agent timeline
8. **Story appears** with narration text
9. **Audio button** is clickable

## 📝 Files Modified in This Fix

1. `fetch_models.py` - Added `StoryGenerationResponse` model
2. `agents/coordinator_agent.py`:
   - Removed bad import `from uagents.models import Model`
   - Added proper REST endpoint with `@coordinator_agent.on_rest_post`
   - Return `StoryGenerationResponse` instead of `dict`
   - Added `create_simple_final_response()` function

## 💡 Pro Tips

- **Keep coordinator log open** to watch agent communication
- **Response files** are in `storage/responses/` (one per session)
- **Audio files** are in `storage/audio/` (persisted)
- **To clear old files**: `rm storage/responses/*.json storage/audio/*.mp3`
- **Press Ctrl+C once** in the agents terminal to stop all agents cleanly

## 🐛 Still Issues?

1. Verify all 3 terminals are running
2. Check all log files for errors
3. Make sure .env has valid API keys
4. Try the curl test above to isolate the issue
5. Check browser console for frontend errors

---

**Ready? Start with Terminal 1! 🚀**
