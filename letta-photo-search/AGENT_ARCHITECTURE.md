# 🤖 Agent Architecture Documentation

## Overview

This system uses a **multi-agent architecture** combining **Fetch.ai** agents for distributed deployment with **Letta AI** for natural language understanding. Here's how they work together:

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│                  (Flask Backend + Web UI)                   │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                  FETCH.AI AGENT LAYER                       │
│              (Distributed Microservices)                    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Coordinator  │  │    Voice     │  │    Search    │    │
│  │   Agent      │──│   Agent      │──│    Agent     │    │
│  │   :8004      │  │   :8002      │  │   :8003      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│              PROCESSING LOGIC LAYER                         │
│                (Python Libraries)                           │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │    Letta     │  │   Sentence   │  │  Fish Audio  │    │
│  │     AI       │  │ Transformers │  │     API      │    │
│  │   (NLU)      │  │ (Embeddings) │  │    (TTS)     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Agent Inventory

### **FETCH.AI AGENTS** (Deployed as Microservices)

These are autonomous agents running on the Fetch.ai network:

#### 1. **Voice Processor Agent**
- **Name:** `voice_processor_agent`
- **Port:** `8002`
- **Seed:** `voice_processor_seed_phrase_secure_12345`
- **File:** `agents/fetch_voice_agent.py`
- **Purpose:** Receives voice/text input and extracts intent, entities, context
- **Uses:** Letta AI internally for NLU processing
- **Endpoint:** `http://127.0.0.1:8002/submit`

**Message Protocol:**
```python
# INPUT
VoiceInputRequest:
    voice_text: str          # The user's query
    session_id: str          # Session identifier

# OUTPUT
VoiceProcessingResponse:
    intent: str              # "search", "browse", etc.
    entities: List[str]      # ["dog", "happy"]
    context: Dict            # {"mood": "happy"}
    search_query: str        # Processed query
    success: bool
```

#### 2. **Image Search Agent**
- **Name:** `image_search_agent`
- **Port:** `8003`
- **Seed:** `image_search_seed_phrase_secure_67890`
- **File:** `agents/fetch_search_agent.py`
- **Purpose:** Performs vector similarity search on image embeddings
- **Uses:** Sentence Transformers for embeddings
- **Endpoint:** `http://127.0.0.1:8003/submit`

**Message Protocol:**
```python
# INPUT
ImageSearchRequest:
    query: str               # Search query
    entities: List[str]      # Extracted entities
    context: Dict            # Additional context
    top_k: int = 3          # Number of results
    session_id: str

# OUTPUT
ImageSearchResponse:
    photos: List[Dict]       # Matching photos with scores
    success: bool
    message: str
```

#### 3. **Coordinator Agent**
- **Name:** `coordinator_agent`
- **Port:** `8004`
- **Seed:** `coordinator_seed_phrase_secure_99999`
- **File:** `agents/fetch_coordinator_agent.py`
- **Purpose:** Orchestrates the complete workflow (voice → search → results)
- **Uses:** Communicates with both Voice and Search agents
- **Endpoint:** `http://127.0.0.1:8004/submit`

**Message Protocol:**
```python
# INPUT
UserVoiceQuery:
    query: str               # User's query
    is_voice: bool = True    # Voice vs text
    session_id: str

# OUTPUT
CompleteSearchResponse:
    original_query: str
    processed_query: str
    intent: str
    entities: List[str]
    photos: List[Dict]
    audio_description: Optional[str]
    success: bool
```

---

### **LETTA AI AGENT** (Processing Library)

This is **NOT** a deployed agent—it's a library used by the Voice Processor Agent:

#### **Letta Voice Processing Agent**
- **File:** `agents/letta_voice_agent.py`
- **Class:** `VoiceProcessingAgent`
- **Purpose:** Natural language understanding using Letta AI framework
- **Used by:** Fetch Voice Processor Agent (port 8002)
- **No direct deployment:** Called as a Python library

**How it works:**
```python
# Inside fetch_voice_agent.py
from agents.letta_voice_agent import VoiceProcessingAgent

letta_agent = VoiceProcessingAgent()
result = letta_agent.process_voice_input("Find me a happy dog")

# Returns:
{
    "intent": "search",
    "entities": ["dog"],
    "context": {"mood": "happy"},
    "search_query": "happy dog",
    "description": "User wants to search for photos of happy dogs"
}
```

---

### **EMBEDDING SEARCH AGENT** (Processing Library)

Also **NOT** a deployed agent—used by the Search Agent:

#### **Embedding Search Agent**
- **File:** `agents/embedding_search_agent.py`
- **Class:** `EmbeddingSearchAgent`
- **Purpose:** Vector similarity search using Sentence Transformers
- **Used by:** Fetch Image Search Agent (port 8003)
- **Model:** `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **No direct deployment:** Called as a Python library

**How it works:**
```python
# Inside fetch_search_agent.py
from agents.embedding_search_agent import EmbeddingSearchAgent

search_agent = EmbeddingSearchAgent()
results = search_agent.search("happy dog", top_k=3)

# Returns:
[
    {
        "id": 1,
        "title": "Golden Retriever",
        "similarity_score": 0.387,
        "description": "A happy golden retriever...",
        ...
    }
]
```

---

## 🔄 Message Flow Architecture

### **Complete User Query Flow:**

```
1. USER QUERY
   ↓
   "Find me a happy dog"
   ↓

2. FLASK BACKEND (/api/search)
   ↓
   POST to Voice Processor Agent (port 8002)
   ↓

3. VOICE PROCESSOR AGENT (Fetch.ai)
   ↓
   Calls Letta Voice Agent (library)
   ↓
   Letta AI processes: "Find me a happy dog"
   ↓
   Returns: {
       intent: "search",
       entities: ["dog"],
       context: {"mood": "happy"},
       search_query: "happy dog"
   }
   ↓

4. FLASK BACKEND
   ↓
   POST to Image Search Agent (port 8003)
   ↓

5. IMAGE SEARCH AGENT (Fetch.ai)
   ↓
   Calls Embedding Search Agent (library)
   ↓
   Generates embedding for "happy dog"
   ↓
   Computes cosine similarity with all photos
   ↓
   Returns: [
       {title: "Golden Retriever", score: 0.387},
       {title: "Tabby Cat", score: 0.243}
   ]
   ↓

6. FLASK BACKEND
   ↓
   Returns results to UI
   ↓

7. UI DISPLAYS RESULTS
   + Shows agent workflow step-by-step
   + Displays photos with similarity scores
   + Plays audio description
```

---

## 🎯 Key Distinctions

### **Fetch.ai Agents vs Processing Libraries**

| Aspect | Fetch.ai Agents | Processing Libraries |
|--------|----------------|---------------------|
| **Deployment** | Deployed as microservices | Imported as Python modules |
| **Ports** | Run on ports 8002-8004 | No ports (in-process) |
| **Communication** | HTTP/uAgents protocol | Direct function calls |
| **Examples** | voice_processor_agent, image_search_agent, coordinator_agent | VoiceProcessingAgent (Letta), EmbeddingSearchAgent |
| **Files** | `fetch_*_agent.py` | `letta_voice_agent.py`, `embedding_search_agent.py` |

### **Why This Architecture?**

1. **Scalability:** Fetch.ai agents can run on different machines
2. **Decentralization:** Agents can communicate over the network
3. **Modularity:** Each agent has a single responsibility
4. **Flexibility:** Processing libraries can be swapped without changing the agent layer

---

## 🔍 Agent Names Summary

### **Deployed Agents (Fetch.ai):**
1. ✅ `voice_processor_agent` (port 8002)
2. ✅ `image_search_agent` (port 8003)
3. ✅ `coordinator_agent` (port 8004)

### **Processing Libraries (Not Deployed):**
1. ❌ `VoiceProcessingAgent` (Letta AI - library only)
2. ❌ `EmbeddingSearchAgent` (Sentence Transformers - library only)

### **Services:**
1. 🔊 `UnifiedTTSService` (Fish Audio + OpenAI TTS)
2. 🎤 Web Speech API (browser-based, no agent)

---

## 🚀 How to Verify Agents are Running

### Check if Fetch agents are deployed:
```bash
# Check processes
ps aux | grep "fetch_.*_agent.py"

# Should show:
python agents/fetch_voice_agent.py       (PID xxx)
python agents/fetch_search_agent.py      (PID xxx)
python agents/fetch_coordinator_agent.py (PID xxx)

# Check logs
ls -la logs/
cat logs/voice_agent.log
cat logs/search_agent.log
cat logs/coordinator_agent.log
```

### Test agent endpoints:
```bash
# Voice Processor Agent
curl -X POST http://localhost:8002/submit \
  -H "Content-Type: application/json" \
  -d '{"voice_text": "Find me a dog", "session_id": "test"}'

# Image Search Agent
curl -X POST http://localhost:8003/submit \
  -H "Content-Type: application/json" \
  -d '{"query": "dog", "top_k": 3, "session_id": "test"}'
```

---

## 📊 Current State

### **What's Working:**
- ✅ Letta Voice Agent (with fallback mode)
- ✅ Embedding Search Agent (real vector similarity)
- ✅ Flask backend with all API endpoints
- ✅ New futuristic UI with agent visualization

### **What Needs Verification:**
- ⚠️ Fetch.ai agents actually receiving messages
- ⚠️ Message passing between agents
- ⚠️ Coordinator agent workflow
- ⚠️ Agent-to-agent communication logs

---

## 🎯 Next Steps (Logging Implementation)

To verify agents are actually working, we need to add:

1. **Comprehensive logging** in all Fetch agents
2. **Message tracking** with unique IDs
3. **Request/response logging** for all API calls
4. **Agent health monitoring**
5. **Message passing verification**

This will be implemented next!
