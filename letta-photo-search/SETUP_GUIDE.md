# Letta Photo Search - Setup Guide

## Overview

This application is a multi-agent AI system that allows you to search through photos using natural language and generate immersive memory stories through agent-to-agent communication.

### Tech Stack
- **Frontend**: Next.js 15 with TypeScript and Tailwind CSS
- **Backend**: Flask (Python) with async support
- **AI Agents**: Fetch.ai uAgents + Letta AI Cloud
- **Vision**: OpenAI GPT-4o Vision
- **TTS**: Fish Audio API + OpenAI TTS

## Architecture

### Agent Communication Flow

```
User Search Query
    ↓
Voice Processing Agent (Letta AI) - Extracts intent & entities
    ↓
Embedding Search Agent - Semantic vector search
    ↓
User Selects Photo for Memory Generation
    ↓
Coordinator Agent (uAgent)
    ↓
Perception Agent (GPT-4o Vision + Letta AI) - Analyzes visual content
    ↓ (passes perception data)
Emotion Agent (Letta AI) - Detects mood/tone from perception data
    ↓ (waits for both perception & emotion)
Narration Agent (Letta AI) - Generates story from both agents' outputs
    ↓
TTS Service - Converts narration to audio
    ↓
Display in UI with agent timeline visualization
```

### Key Features Fixed

1. **Agent-to-Agent Communication**:
   - Emotion agent now receives perception data from Perception agent
   - Coordinator properly sequences agents (Perception → Emotion → Narration)
   - All agents use Letta AI for intelligent processing

2. **Memory Generation for All Photos**:
   - Every search result now has a "Generate Memory Story" button
   - Not limited to just the first photo anymore

3. **No Photo Upload**:
   - Photo upload feature has been removed
   - Memory generation works directly from search results

4. **Next.js + Tailwind UI**:
   - Modern, responsive React components
   - Beautiful gradient backgrounds and animations
   - Agent processing timeline visualization

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
# Required API Keys
LETTA_API_KEY=sk-let-YOUR_KEY_HERE
PERCEPTION_AGENT_ID=agent-YOUR_ID_HERE
EMOTION_AGENT_ID=agent-YOUR_ID_HERE
NARRATION_AGENT_ID=agent-YOUR_ID_HERE
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
FISH_AUDIO_API_KEY=YOUR_KEY_HERE

# Optional
FETCH_API_KEY=YOUR_KEY_HERE
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Step 1: Start the Agent System

In Terminal 1, start all uAgents (Perception, Emotion, Narration, Coordinator):

```bash
python run_story_agents.py
```

You should see output like:
```
🔍 Perception Agent started: agent1q26xyx0j7...
💭 Emotion Agent started: agent1qtdj6yrj...
📖 Narration Agent started: agent1qdvng2wk...
🎯 Coordinator Agent started: agent1qwdc42f...
```

### Step 2: Start the Flask Backend

In Terminal 2, start the Flask server:

```bash
python app_enhanced.py
```

You should see:
```
ENHANCED ACCESSIBLE PHOTO SEARCH - BACKEND SERVER
Starting server...
UI at: http://localhost:5000

Initializing agents...
✓ All agents initialized successfully
```

The Flask backend runs on `http://localhost:5000`

### Step 3: Start the Next.js Frontend

In Terminal 3, start the Next.js development server:

```bash
cd frontend
npm run dev
```

You should see:
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
  - Ready in Xs
```

The Next.js frontend runs on `http://localhost:3000`

## Using the Application

### 1. Search for Photos

1. Open `http://localhost:3000` in your browser
2. Click the microphone button to use voice search, or type in the text box
3. Try queries like:
   - "Happy dog"
   - "Peaceful sunset"
   - "City lights"
   - "Ocean waves"

### 2. View Search Results

- The system shows an agent timeline:
  1. **Voice Processing Agent** - Analyzes your natural language query
  2. **Embedding Search Agent** - Finds matching photos using vector similarity

- Results are displayed with:
  - Photo preview
  - Title and description
  - Tags
  - Relevance score (similarity percentage)

### 3. Generate Memory Story

1. Click "Generate Memory Story" on any photo
2. Watch the agent processing timeline:
   - **Perception Agent** (GPT-4o Vision + Letta) - Analyzes visual content
   - **Emotion Agent** (Letta) - Receives perception data, detects mood/emotions
   - **Narration Agent** (Letta) - Creates story from perception + emotion data
3. View the generated narration
4. Click "Play Audio Narration" to hear the story

## Agent Communication Details

### Perception Agent → Emotion Agent
```python
# Coordinator receives perception data
PerceptionData {
  objects: [...],
  people_count: 2,
  scene_type: "outdoor_beach",
  colors: ["blue", "orange", "gold"],
  ...
}

# Coordinator sends to Emotion Agent WITH perception data
EmotionRequest {
  session_id: "...",
  photo_url: "...",
  perception_data: { <all perception fields> }  # ✅ NEW!
}

# Emotion Agent processes with Letta AI
→ Calls Letta Emotion Agent API with perception context
→ Returns EmotionData { mood, emotion_tags, tone, intensity, ... }
```

### Emotion Agent → Narration Agent
```python
# Coordinator waits for both Perception and Emotion to complete
# Then sends to Narration Agent
NarrationRequest {
  session_id: "...",
  perception: { <all perception data> },
  emotion: { <all emotion data> }
}

# Narration Agent creates story from both contexts
→ Calls Letta Narration Agent API
→ Returns NarrationData { main_narration, person_dialogues, ambient_descriptions }
```

## Troubleshooting

### Agents Not Starting
- Make sure all agent IDs are correctly set in `.env`
- Check that ports 8001, 8002, 8003, 8006 are available
- View logs in `logs/` directory

### API Errors
- Verify all API keys are valid in `.env`
- Check Letta AI agent IDs are correct
- Ensure OpenAI API key has access to GPT-4o Vision

### Frontend Not Connecting to Backend
- Make sure Flask is running on port 5000
- Check Next.js proxy configuration in `frontend/next.config.ts`
- Verify `/api/*` requests are being forwarded correctly

### Memory Generation Fails
- Ensure all agents are running (`run_story_agents.py`)
- Check agent logs for errors
- Verify Letta AI agents are properly configured
- Look for response files in `storage/responses/`

## File Structure

```
letta-photo-search/
├── agents/
│   ├── coordinator_agent.py       # Orchestrates agent workflow
│   ├── perception_agent.py        # Vision analysis + Letta
│   ├── emotion_agent.py           # Emotion detection with Letta
│   ├── narration_agent.py         # Story generation with Letta
│   ├── letta_voice_agent.py       # Voice NLU processing
│   └── embedding_search_agent.py  # Vector similarity search
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Main app page
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css           # Global styles
│   ├── components/
│   │   ├── SearchPage.tsx        # Search interface
│   │   └── MemoryPage.tsx        # Memory generation UI
│   ├── next.config.ts            # Next.js config with API proxy
│   └── package.json
├── app_enhanced.py               # Flask backend
├── fetch_models.py               # Agent message models
├── run_story_agents.py           # Start all agents
├── requirements.txt              # Python dependencies
├── .env                          # API keys & config
└── SETUP_GUIDE.md               # This file
```

## Development Notes

### Adding New Photos
Edit `data/photo_database.json` to add new photos with metadata.

### Modifying Agent Behavior
- Perception: Edit prompt in `agents/perception_agent.py`
- Emotion: Edit prompt in `agents/emotion_agent.py`
- Narration: Edit prompt in `agents/narration_agent.py`
- Configure Letta agents at https://app.letta.com

### Customizing UI
- Edit React components in `frontend/components/`
- Modify Tailwind styles inline or in `globals.css`
- Update color schemes in component `className` props

## Summary of Changes Made

1. ✅ **Fixed Agent Communication**
   - Added `perception_data` field to `EmotionRequest` model
   - Updated coordinator to send perception data to emotion agent
   - Changed from parallel to sequential processing (Perception → Emotion → Narration)
   - Added proper error logging throughout agent pipeline

2. ✅ **Fixed Memory Tab**
   - Removed `index === 0` condition
   - All photos now have "Generate Memory Story" button

3. ✅ **Removed Photo Upload**
   - Commented out `/api/photos/upload` endpoint
   - Commented out `/story` route
   - Memory generation now works only from search results

4. ✅ **Migrated to Next.js + Tailwind**
   - Created modern Next.js 15 app with TypeScript
   - Implemented responsive Tailwind UI
   - Created SearchPage and MemoryPage components
   - Added API proxy to Flask backend
   - Beautiful gradient backgrounds and animations

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Verify all environment variables in `.env`
3. Ensure all services are running (agents, Flask, Next.js)
4. Check browser console for frontend errors
5. Review agent communication flow in coordinator logs
