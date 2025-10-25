# Quick Command Reference

## 🚀 Launch Commands

### Web App Only (Recommended for Demo)
```bash
python app_enhanced.py
# Open: http://localhost:5000
```

### All Agents (Background)
```bash
python run_all_agents_simple.py
# Logs: logs/*.log
```

### Complete System
```bash
./launch_system.sh
# Select option 1, 2, or 3
```

### Single Agent (Testing)
```bash
python run_single_agent.py 1  # Voice (port 8002)
python run_single_agent.py 2  # Search (port 8003)
python run_single_agent.py 3  # Coordinator (port 8004)
```

---

## 🧪 Test Commands

### Full System Test
```bash
python test_system.py
```

### Test Voice Agent
```bash
python -c "
from agents.letta_voice_agent import VoiceProcessingAgent
agent = VoiceProcessingAgent()
print(agent.process_voice_input('Find me a happy dog'))
"
```

### Test Search Agent
```bash
python -c "
from agents.embedding_search_agent import EmbeddingSearchAgent
agent = EmbeddingSearchAgent()
results = agent.search('dog', top_k=3)
for r in results:
    print(f\"{r['title']}: {r['similarity_score']:.3f}\")
"
```

---

## 📊 Monitoring

### View Logs (Real-time)
```bash
tail -f logs/fetch_voice_agent.log
tail -f logs/fetch_search_agent.log
tail -f logs/fetch_coordinator_agent.log
```

### Check Running Agents
```bash
ps aux | grep "fetch_.*_agent.py" | grep -v grep
```

### Check Ports
```bash
lsof -i :5000  # Web app
lsof -i :8002  # Voice agent
lsof -i :8003  # Search agent
lsof -i :8004  # Coordinator
```

---

## 🛑 Stop Commands

### Stop All Agents
```bash
pkill -f "fetch_.*_agent.py"
```

### Stop Web App
```bash
pkill -f "app_enhanced.py"
```

### Stop Specific Port
```bash
lsof -ti :8002 | xargs kill  # Voice agent
lsof -ti :8003 | xargs kill  # Search agent
lsof -ti :8004 | xargs kill  # Coordinator
lsof -ti :5000 | xargs kill  # Web app
```

### Force Kill Everything
```bash
pkill -9 -f "fetch_.*_agent.py"
pkill -9 -f "app_enhanced.py"
```

---

## 🔧 Utility Commands

### Regenerate Embeddings
```bash
rm data/photo_embeddings.npy
python -c "from agents.embedding_search_agent import EmbeddingSearchAgent; EmbeddingSearchAgent()"
```

### Clear Logs
```bash
rm logs/*.log
```

### Check Environment
```bash
cat .env
```

### List Photos
```bash
python -c "
import json
data = json.load(open('data/photo_database.json'))
for p in data['photos']:
    print(f\"{p['id']}. {p['title']}\")
"
```

---

## 🌐 API Test Commands

### Search
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "dog"}'
```

### Voice Processing
```bash
curl -X POST http://localhost:5000/api/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Find me a happy dog"}'
```

### Generate TTS
```bash
curl -X POST http://localhost:5000/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}' > response.json
cat response.json | jq -r '.audio_url'
```

### Health Check
```bash
curl http://localhost:5000/api/health | jq
```

### Agent Status
```bash
curl http://localhost:5000/api/agent-status | jq
```

### List All Photos
```bash
curl http://localhost:5000/api/photos | jq
```

---

## 📦 Install Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install Specific Packages
```bash
pip install sentence-transformers
pip install torch
pip install letta uagents
pip install flask flask-cors
pip install httpx
```

---

## 🎯 Quick Workflow

### 1. First Time Setup
```bash
pip install -r requirements.txt
python test_system.py
```

### 2. Launch for Demo
```bash
./launch_system.sh
# Select option 1
```

### 3. Test Everything
```bash
# Terminal 1: Run web app
python app_enhanced.py

# Terminal 2: Test search
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "happy dog"}'
```

### 4. Deploy Agents
```bash
python run_all_agents_simple.py
tail -f logs/*.log
```

---

## 🐛 Troubleshooting Commands

### Clear Everything and Restart
```bash
pkill -f "fetch_.*_agent.py"
pkill -f "app_enhanced.py"
rm logs/*.log
python test_system.py
./launch_system.sh
```

### Check What's Running
```bash
ps aux | grep python | grep -E "(app_enhanced|fetch_.*_agent)"
```

### See All Ports in Use
```bash
lsof -i -P | grep LISTEN | grep python
```

---

## 📝 Useful Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias photo-start="cd /path/to/letta-photo-search && python app_enhanced.py"
alias photo-agents="cd /path/to/letta-photo-search && python run_all_agents_simple.py"
alias photo-test="cd /path/to/letta-photo-search && python test_system.py"
alias photo-logs="tail -f /path/to/letta-photo-search/logs/*.log"
alias photo-stop="pkill -f 'fetch_.*_agent.py'; pkill -f 'app_enhanced.py'"
```

---

**Most Common Usage:**
```bash
./launch_system.sh  # Select option 1
```
