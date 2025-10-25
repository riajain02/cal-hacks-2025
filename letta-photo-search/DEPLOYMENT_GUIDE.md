# Deployment Guide - Voice-to-Image Search System

This guide will help you get the complete system up and running.

---

## Prerequisites

- Python 3.8 or higher
- pip
- 8GB+ RAM (for embedding models)
- Internet connection

---

## Step-by-Step Deployment

### Step 1: Install Dependencies

```bash
cd letta-photo-search
pip install -r requirements.txt
```

**Note**: This may take 5-10 minutes as it installs PyTorch and transformers.

### Step 2: Verify Environment Variables

Check that `.env` contains all API keys:

```bash
cat .env
```

Should show:
- LETTA_API_KEY
- FETCH_API_KEY
- FISH_AUDIO_API_KEY
- OPENAI_API_KEY

All keys are already configured!

### Step 3: Test the System

Run the test suite to verify everything works:

```bash
python test_system.py
```

This will test:
- ✓ Environment variables
- ✓ Photo database
- ✓ Voice processing agent
- ✓ Embedding search agent
- ✓ Photo embeddings (generates if needed)

### Step 4: Generate Embeddings

The embedding generation happens automatically on first run, but you can pre-generate:

```bash
python -c "from agents.embedding_search_agent import EmbeddingSearchAgent; EmbeddingSearchAgent()"
```

This creates `data/photo_embeddings.npy` with vector representations of all photos.

### Step 5: Launch the System

#### Option A: Quick Launch (Recommended)

```bash
./launch_system.sh
```

Select option 1 (Web app only) for the easiest demo.

#### Option B: Manual Launch

```bash
python app_enhanced.py
```

Then open: http://localhost:5000

---

## Testing the Features

### 1. Text Search

1. Open http://localhost:5000
2. Type "dog" in the search box
3. Click "Search"
4. See results with similarity scores

### 2. Voice Search

1. Click the microphone button 🎤
2. Say "Find me a happy dog"
3. System will:
   - Transcribe your speech
   - Extract intent ("search") and entities ("dog")
   - Search using embeddings
   - Display results

### 3. Hear Descriptions

1. Click any photo card
2. Hear the full description read aloud
3. Or click the "🔊 Hear Description" button

---

## Deploying Fetch.ai Agents

To deploy all agents on the Fetch.ai network:

### Terminal 1: Run Agents

```bash
python run_all_agents.py
```

This starts:
- Voice Processing Agent (localhost:8002)
- Image Search Agent (localhost:8003)
- Coordinator Agent (localhost:8004)

### Terminal 2: Run Web App

```bash
python app_enhanced.py
```

### Verify Agents Are Running

Check the logs - you should see agent addresses like:

```
Agent Address: agent1qf...
Agent listening on port 8002
```

---

## System Architecture Explained

### Flow 1: Direct Web Search (Simple)

```
User types "dog"
  ↓
Flask Backend
  ↓
Voice Agent (extract intent/entities)
  ↓
Embedding Search (find similar images)
  ↓
Results returned to user
```

### Flow 2: Voice Search with TTS (Advanced)

```
User speaks "happy dog"
  ↓
Browser captures audio
  ↓
Flask Backend processes
  ↓
Letta Voice Agent extracts:
  - Intent: search
  - Entities: [dog]
  - Context: {mood: happy}
  ↓
Embedding Search with context
  ↓
Top 3 results found
  ↓
Fish Audio TTS generates description
  ↓
Audio played to user
```

### Flow 3: Fetch.ai Agent Communication

```
HTTP Request
  ↓
Coordinator Agent (port 8004)
  ↓
Sends VoiceInputRequest → Voice Agent (port 8002)
  ↓
Receives VoiceProcessingResponse
  ↓
Sends ImageSearchRequest → Search Agent (port 8003)
  ↓
Receives ImageSearchResponse
  ↓
Returns CompleteSearchResponse
```

---

## API Usage Examples

### Example 1: Simple Search

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "dog"}'
```

### Example 2: Voice Processing

```bash
curl -X POST http://localhost:5000/api/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Find me a happy dog playing in a park"}'
```

Response:
```json
{
  "success": true,
  "data": {
    "intent": "search",
    "entities": ["dog"],
    "context": {"mood": "happy", "setting": "outdoor"},
    "search_query": "happy dog park",
    "description": "Looking for a cheerful dog in a park setting"
  }
}
```

### Example 3: Generate TTS

```bash
curl -X POST http://localhost:5000/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "I found 3 photos of dogs for you"}'
```

Response:
```json
{
  "success": true,
  "audio_url": "/api/audio/abc-123.mp3"
}
```

Then access the audio at:
```
http://localhost:5000/api/audio/abc-123.mp3
```

---

## Troubleshooting Common Issues

### Issue: "ModuleNotFoundError: No module named 'sentence_transformers'"

**Solution:**
```bash
pip install sentence-transformers
```

### Issue: "torch not found"

**Solution:**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue: "Embeddings generation is slow"

**Explanation:** First-time embedding generation takes 30-60 seconds.

**Solution:** Wait for it to complete. Embeddings are cached in `data/photo_embeddings.npy`.

### Issue: "Fish Audio API returns 401"

**Solution:** Verify your Fish Audio API key in `.env`:
```bash
FISH_AUDIO_API_KEY=207d52338aa448ae8ef709c3d59c3f30
```

The system will automatically fallback to OpenAI TTS if Fish Audio fails.

### Issue: "Port 5000 already in use"

**Solution:** Change the port in `app_enhanced.py`:
```python
config.bind = ["0.0.0.0:5001"]  # Change from 5000
```

### Issue: "Voice input not working in browser"

**Solutions:**
1. Use Chrome or Edge (best support)
2. Allow microphone permissions
3. Use HTTPS in production (required for mic access)

---

## Production Deployment

### Using Gunicorn (Production WSGI Server)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_enhanced:app
```

### Using Docker (Coming Soon)

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app_enhanced.py"]
```

### Environment Variables for Production

Create a production `.env.production`:

```bash
LETTA_API_KEY=your_production_key
FETCH_API_KEY=your_production_key
FISH_AUDIO_API_KEY=your_production_key
OPENAI_API_KEY=your_production_key
FLASK_ENV=production
```

---

## Monitoring & Logging

### View Agent Logs

Each agent logs to stdout. Run in separate terminals or use tmux:

```bash
# Terminal 1
python agents/fetch_voice_agent.py 2>&1 | tee voice_agent.log

# Terminal 2
python agents/fetch_search_agent.py 2>&1 | tee search_agent.log

# Terminal 3
python agents/fetch_coordinator_agent.py 2>&1 | tee coordinator_agent.log
```

### Health Check

```bash
curl http://localhost:5000/api/health
```

Response:
```json
{
  "status": "healthy",
  "voice_agent": "ready",
  "search_agent": "ready",
  "tts_service": "ready"
}
```

### Agent Status

```bash
curl http://localhost:5000/api/agent-status
```

---

## Performance Optimization

### 1. Preload All Agents

Agents lazy-load by default. Preload on startup:

```python
# In app_enhanced.py
if __name__ == '__main__':
    get_voice_agent()
    get_search_agent()
    get_tts_service()
```

### 2. Use Faster Embedding Model

For faster search (slightly lower accuracy):

```python
agent = EmbeddingSearchAgent(model_name='all-MiniLM-L6-v2')  # Current (fast)
# vs
agent = EmbeddingSearchAgent(model_name='all-mpnet-base-v2')  # Slower but better
```

### 3. Cache TTS Results

Save frequently used audio:

```python
# Cache common phrases
CACHED_AUDIO = {
    "welcome": "storage/audio/welcome.mp3",
    "no_results": "storage/audio/no_results.mp3"
}
```

---

## Scaling to 1000+ Photos

### 1. Use FAISS for Vector Search

Install FAISS:
```bash
pip install faiss-cpu
```

Modify `embedding_search_agent.py`:
```python
import faiss

# Create FAISS index
index = faiss.IndexFlatL2(embedding_dim)
index.add(embeddings)

# Search
D, I = index.search(query_embedding, k=3)
```

### 2. Use PostgreSQL for Metadata

```python
import psycopg2

# Store photos in PostgreSQL
# Store embeddings in pgvector extension
```

---

## Next Steps

1. **Add More Photos**: Edit `data/photo_database.json`
2. **Customize Voice Prompts**: Edit `letta_voice_agent.py` system prompt
3. **Train Custom Embeddings**: Use your own embedding model
4. **Deploy to Cloud**: Use AWS, GCP, or Azure
5. **Add Authentication**: Protect API endpoints
6. **Enable HTTPS**: Required for microphone access

---

## Support & Contact

For issues, check:
1. Test suite: `python test_system.py`
2. Agent logs
3. API health endpoints
4. This deployment guide

---

**System is ready! Run `./launch_system.sh` to start!** 🚀
