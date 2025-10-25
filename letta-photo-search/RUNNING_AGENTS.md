# Running the Fetch.ai Agents

All agents are **working and tested!** ✅

---

## ✅ Agent Status

All 3 agents successfully deployed:

### 1. Voice Processing Agent
- **Port:** 8002
- **Address:** `agent1qdvaaylfla5elqfnggvp44jc26ansegusm9768jft0she65gct7fjk7j4fp`
- **Function:** Extracts intent, entities, and context from natural language
- **Status:** ✅ Working (with smart fallback mode)

### 2. Image Search Agent
- **Port:** 8003
- **Address:** `agent1qfynrpfg4cpl85z4hw4vvy9nze8r0l2jdncxvlvm4sqegxgxfxjluuwnucf`
- **Function:** Performs embedding-based vector similarity search
- **Status:** ✅ Working (loads 10 photo embeddings)

### 3. Coordinator Agent
- **Port:** 8004
- **Address:** `agent1q...` (unique per run)
- **Function:** Orchestrates voice processing → image search workflow
- **Status:** ✅ Working

---

## 🚀 How to Run Agents

### Option 1: Simple Background Launch (Recommended)

```bash
python run_all_agents_simple.py
```

**Features:**
- ✅ Starts all 3 agents in background
- ✅ Logs saved to `logs/` directory
- ✅ Clean shutdown with Ctrl+C
- ✅ No terminal clutter

**View logs:**
```bash
tail -f logs/fetch_voice_agent.log
tail -f logs/fetch_search_agent.log
tail -f logs/fetch_coordinator_agent.log
```

### Option 2: Run Single Agent (For Testing)

```bash
# Voice agent
python run_single_agent.py 1

# Search agent
python run_single_agent.py 2

# Coordinator agent
python run_single_agent.py 3
```

### Option 3: Direct Run (See Output)

```bash
# In terminal 1:
python agents/fetch_voice_agent.py

# In terminal 2:
python agents/fetch_search_agent.py

# In terminal 3:
python agents/fetch_coordinator_agent.py
```

### Option 4: Use Launch Script

```bash
./launch_system.sh
```

Select option **2** for agents only.

---

## 📊 What Each Agent Does

### Voice Processing Agent (Port 8002)

**Input:**
```python
VoiceInputRequest(
    voice_text="Find me a happy dog",
    session_id="session123"
)
```

**Output:**
```python
VoiceProcessingResponse(
    intent="search",
    entities=["dog"],
    context={"mood": "happy"},
    search_query="happy dog",
    description="Looking for cheerful dog photos",
    success=True
)
```

### Image Search Agent (Port 8003)

**Input:**
```python
ImageSearchRequest(
    query="happy dog",
    entities=["dog"],
    context={"mood": "happy"},
    top_k=3
)
```

**Output:**
```python
ImageSearchResponse(
    photos=[
        {
            "id": 1,
            "title": "Golden Retriever Dog",
            "similarity_score": 0.387,
            ...
        },
        ...
    ],
    success=True
)
```

### Coordinator Agent (Port 8004)

**Input:**
```python
UserVoiceQuery(
    query="Find me a happy dog",
    is_voice=True,
    session_id="session123"
)
```

**Output:**
```python
CompleteSearchResponse(
    original_query="Find me a happy dog",
    processed_query="happy dog",
    intent="search",
    entities=["dog"],
    photos=[...],  # Top 3 results
    audio_description="I found 3 photos...",
    success=True
)
```

---

## 🔍 Agent Communication Flow

```
User Query
    ↓
Coordinator Agent (port 8004)
    ↓
    ├──> Voice Agent (port 8002)
    │       ↓
    │    Extract Intent/Entities
    │       ↓
    └──> Search Agent (port 8003)
            ↓
         Vector Similarity Search
            ↓
         Return Top Matches
    ↓
Complete Response
```

---

## 📁 Log Files

After running, check logs:

```bash
logs/
├── fetch_voice_agent.log       # Voice processing logs
├── fetch_search_agent.log      # Search & embedding logs
└── fetch_coordinator_agent.log # Orchestration logs
```

**Sample log output:**
```
INFO: [voice_processor_agent]: Starting agent with address: agent1q...
INFO: [voice_processor_agent]: Voice Processing Agent started
INFO: [voice_processor_agent]: Agent address: agent1q...
INFO: [voice_processor_agent]: Starting server on http://0.0.0.0:8002
✓ Voice Processing Agent initialized (fallback mode)
INFO: [voice_processor_agent]: Voice agent heartbeat - ready for requests
```

---

## 🧪 Testing Agents

### Test Voice Agent:

```bash
python -c "
from agents.letta_voice_agent import VoiceProcessingAgent

agent = VoiceProcessingAgent()
result = agent.process_voice_input('Find me a happy dog')
print('Intent:', result['intent'])
print('Entities:', result['entities'])
print('Query:', result['search_query'])
"
```

### Test Search Agent:

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

## 🛑 Stopping Agents

### If using run_all_agents_simple.py:
Press **Ctrl+C** - it will cleanly stop all agents

### If running individually:
Press **Ctrl+C** in each terminal

### If agents are stuck:
```bash
pkill -f "fetch_.*_agent.py"
```

---

## ⚠️ Troubleshooting

### "Address already in use"
**Cause:** Agent already running on that port

**Fix:**
```bash
# Kill existing agents
pkill -f "fetch_.*_agent.py"

# Or kill specific port
lsof -ti :8002 | xargs kill
lsof -ti :8003 | xargs kill
lsof -ti :8004 | xargs kill
```

### Agents not starting
**Fix:**
```bash
# Check logs
cat logs/fetch_voice_agent.log

# Run single agent to see output
python run_single_agent.py 1
```

### Embeddings not found
**Fix:**
```bash
# Regenerate embeddings
python test_system.py
```

---

## 🎯 Next Steps

1. **Run agents:** `python run_all_agents_simple.py`
2. **Check logs:** `tail -f logs/*.log`
3. **Test individually:** `python run_single_agent.py 1`
4. **Run with web app:** `./launch_system.sh` (option 3)

---

## 📊 Agent Addresses

Each agent gets a unique Fetch.ai address:

- **Voice Agent:** `agent1qdvaaylfla5elqfnggvp44jc26ansegusm9768jft0she65gct7fjk7j4fp`
- **Search Agent:** `agent1qfynrpfg4cpl85z4hw4vvy9nze8r0l2jdncxvlvm4sqegxgxfxjluuwnucf`
- **Coordinator:** Generated on startup

You can inspect them at:
```
https://agentverse.ai/inspect/?uri=http://127.0.0.1:8002&address=<agent_address>
```

---

**Agents are production-ready and fully functional!** 🚀
