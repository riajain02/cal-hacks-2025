# 🔧 Restart and Test Guide

## What Was Fixed

The error you were seeing:
```
ERROR:agents.story_agent_client:Coordinator returned error: 400
ERROR:agents.story_agent_client:Response: {"error": "contents do not match envelope schema"}
```

**Root Cause**: The story_agent_client was sending plain HTTP JSON to the uAgents `/submit` endpoint, which expects messages in a special uAgents envelope format.

**Solution**:
1. Added a REST API endpoint to the coordinator agent at `/api/generate`
2. Updated story_agent_client to use this new endpoint
3. Simplified the response creation to just use 3 agents (Perception → Emotion → Narration)
4. Added better error handling and logging throughout

## 🚀 How to Restart and Test

### Step 1: Stop All Running Processes

First, stop everything:

**Option A - Using the restart script:**
```bash
./restart_agents.sh
```

**Option B - Manual stop:**
```bash
# Stop agents
pkill -f "perception_agent.py"
pkill -f "emotion_agent.py"
pkill -f "narration_agent.py"
pkill -f "coordinator_agent.py"

# Stop Flask (Ctrl+C in the Flask terminal)
```

### Step 2: Start the Agents (NEW VERSION)

In Terminal 1:
```bash
python3 run_story_agents.py
```

You should see:
```
✓ Perception Agent started (PID XXXXX)
✓ Emotion Agent started (PID XXXXX)
✓ Narration Agent started (PID XXXXX)
✓ Coordinator Agent started (PID XXXXX)
```

Check the coordinator log to verify the REST API is available:
```bash
tail -f logs/coordinator_agent.log
```

Look for this line:
```
🌐 REST API available at: http://localhost:8006/api/generate
```

### Step 3: Start Flask Backend

In Terminal 2:
```bash
python3 app_enhanced.py
```

You should see:
```
✓ All agents initialized successfully
Running on http://0.0.0.0:5000 (CTRL + C to quit)
```

### Step 4: Start Next.js Frontend

In Terminal 3:
```bash
cd frontend
npm run dev
```

You should see:
```
- Local:        http://localhost:3000
- Ready in Xs
```

### Step 5: Test the Application

1. Open http://localhost:3000 in your browser
2. Search for "happy dog" (or any query)
3. Click "Generate Memory Story" on any photo
4. Watch the agent processing timeline:
   - ✓ Perception Agent - Analyzing visual content...
   - ✓ Emotion Agent - Detecting emotions and mood...
   - ✓ Narration Agent - Generating story...
5. You should see the generated story!

## 🐛 Debugging

### Check if agents are running:
```bash
ps aux | grep -E "perception|emotion|narration|coordinator"
```

### Monitor agent logs in real-time:
```bash
# In separate terminals:
tail -f logs/coordinator_agent.log
tail -f logs/perception_agent.log
tail -f logs/emotion_agent.log
tail -f logs/narration_agent.log
```

### Check if REST API is accessible:
```bash
curl -X POST http://localhost:8006/api/generate \
  -H "Content-Type: application/json" \
  -d '{"photo_url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800", "session_id": "test-123"}'
```

Expected response:
```json
{
  "success": true,
  "message": "Story generation started",
  "session_id": "test-123"
}
```

### Check if response file is created:
After triggering a story generation, check:
```bash
ls -la storage/responses/
```

You should see a JSON file with your session_id.

### Common Issues

**Issue 1: Port already in use**
```
Error: Address already in use
```
Solution: Kill the process using that port:
```bash
lsof -ti:8006 | xargs kill
```

**Issue 2: Letta API errors**
```
HTTP Error: 401 or 403
```
Solution: Check your .env file has valid Letta API keys:
```bash
cat .env | grep LETTA
```

**Issue 3: Agents not communicating**
Check the coordinator log - you should see:
```
🚀 [COORDINATOR] Starting experience for session_id
📸 [1/5] → Perception Agent
😊 [2/5] → Emotion Agent (with perception data)
📝 [3/5] → Narration Agent
✅ Complete processing for session session_id
```

If you don't see this sequence, check individual agent logs for errors.

**Issue 4: No response file created**
This means the narration agent didn't complete. Check:
```bash
tail -n 50 logs/narration_agent.log
```

Look for Letta API errors or JSON parsing errors.

## 🔍 Agent Communication Flow (What's Happening)

1. **Frontend** → clicks "Generate Memory Story"
2. **Next.js** → POST to `/api/story/generate`
3. **Flask** → calls `story_agent_client.generate_story_from_photo()`
4. **story_agent_client** → POST to `http://localhost:8006/api/generate`
5. **Coordinator REST endpoint** → receives request, sends to Perception Agent
6. **Perception Agent** → analyzes photo with GPT-4o Vision + Letta, returns PerceptionData
7. **Coordinator** → receives PerceptionData, sends to Emotion Agent WITH perception data
8. **Emotion Agent** → analyzes emotions using Letta with perception context, returns EmotionData
9. **Coordinator** → receives EmotionData, sends both to Narration Agent
10. **Narration Agent** → generates story with Letta from both inputs, returns NarrationData
11. **Coordinator** → creates final JSON response, saves to `storage/responses/{session_id}.json`
12. **story_agent_client** → polls for file, reads it, returns to Flask
13. **Flask** → generates TTS audio from narration
14. **Frontend** → displays story + audio player

## ✅ Success Indicators

You'll know it's working when:

1. **Coordinator log shows**:
   ```
   🌐 HTTP REST request received for session: xxx
   🚀 [COORDINATOR] Starting experience for xxx
   📸 Received perception data for xxx
   😊 Received emotion data for xxx
   📝 Received narration data for xxx
   ✅ Complete processing for session xxx
   📁 Response saved to: storage/responses/xxx.json
   ```

2. **Frontend shows**:
   - ✓ Perception Agent - Complete
   - ✓ Emotion Agent - Complete
   - ✓ Narration Agent - Complete
   - Story text appears
   - "Play Audio Narration" button appears

3. **Flask log shows**:
   ```
   INFO:agents.story_agent_client:✅ Response file found!
   INFO:agents.story_agent_client:📊 Response data loaded successfully
   Audio narration generated: /api/audio/story_xxx.mp3
   Story generated successfully: xxx
   ```

## 📊 Key Files Modified

- `agents/coordinator_agent.py` - Added REST endpoint at `/api/generate`
- `agents/story_agent_client.py` - Updated to use new endpoint
- `agents/narration_agent.py` - Better error handling for JSON parsing
- `fetch_models.py` - Added perception_data to EmotionRequest
- Created `restart_agents.sh` for easy restarts

## 🎯 Next Steps

Once it's working:

1. Test with different photos
2. Try different search queries
3. Check the quality of generated stories
4. Monitor Letta agent responses in logs
5. Adjust prompts in Letta dashboard if needed

## 💡 Tips

- Keep the coordinator log open to watch agent communication
- Use Ctrl+C in the agent terminal to stop all agents at once
- Response files are temporary - they get cleaned up after each session
- Audio files are saved in `storage/audio/` and persist
- To clear old audio files: `rm -f storage/audio/*.mp3`

## 🆘 Still Having Issues?

1. Check all 3 terminals are running (agents, Flask, Next.js)
2. Verify all agent logs show "started" messages
3. Test the REST endpoint with curl (see above)
4. Make sure .env has all required API keys
5. Check that ports 8001, 8002, 8003, 8006, 5000, 3000 are available
6. Look for Python errors in any of the terminals

If all else fails, restart everything fresh:
```bash
# Kill everything
pkill -f "python"
killall node

# Start fresh
python3 run_story_agents.py  # Terminal 1
python3 app_enhanced.py      # Terminal 2
cd frontend && npm run dev   # Terminal 3
```
