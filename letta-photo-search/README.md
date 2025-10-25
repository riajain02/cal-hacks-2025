# Accessible Photo Search System

**An AI-powered photo search system designed for blind users**

Powered by **Letta AI Agents** and **Fetch.ai Network**

---

## Features

### Core Functionality
- **Natural Language Search**: Search for photos using everyday language (e.g., "dog", "sunset", "coffee cup")
- **AI-Powered Matching**: Letta AI agent provides semantic search beyond simple keyword matching
- **Decentralized Deployment**: Agents deployed on Fetch.ai network for discovery and scalability

### Accessibility Features
- **Voice Input**: Speak your search queries using the microphone button
- **Voice Output**: Hear detailed descriptions of photos read aloud
- **Screen Reader Optimized**: Full ARIA labels and semantic HTML
- **Keyboard Navigation**: Complete keyboard support (Tab, Enter, shortcuts)
- **High Contrast Support**: Automatically adapts to system accessibility preferences
- **Detailed Descriptions**: Every photo includes comprehensive alt text and descriptions

### Technical Features
- **Letta AI Integration**: Intelligent agent-based photo search
- **Fetch.ai Network**: Decentralized agent deployment and communication
- **Modern Web UI**: Responsive, accessible, beautiful interface
- **Real Photos**: 10 curated photos from Unsplash across diverse categories

---

## Quick Start

### Option 1: Use the Launch Script (Recommended)

```bash
./launch-full-system.sh
```

Then select:
- **Option 1**: Launch Web UI only (best for demos)
- **Option 2**: Launch Fetch.ai agent only
- **Option 3**: Instructions for running both

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Web Application**
   ```bash
   python app.py
   ```

3. **Open in Browser**
   ```
   http://localhost:5000
   ```

### Option 3: Run Fetch.ai Agent

```bash
python run_agents.py
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      USER INTERFACE                      │
│  (Accessible Web UI with Voice Input/Output)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   FLASK BACKEND                          │
│              (REST API Server)                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 LETTA AI AGENT                           │
│     (Semantic Search & Intelligence)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                FETCH.AI AGENT                            │
│        (Decentralized Deployment)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                PHOTO DATABASE                            │
│         (10 Photos + Metadata)                           │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
letta-photo-search/
├── agents/
│   ├── letta_photo_agent.py      # Letta AI search agent
│   ├── fetch_agent.py             # Fetch.ai network agent
│   └── test_fetch_client.py       # Test client for Fetch agent
├── data/
│   ├── photos/                    # Downloaded photo files
│   └── photo_database.json        # Photo metadata
├── ui/
│   ├── index.html                 # Main web interface
│   ├── style.css                  # Accessible styling
│   └── app.js                     # Frontend logic + voice
├── app.py                         # Flask backend server
├── setup_photo_data.py            # Photo download script
├── run_agents.py                  # Fetch.ai agent runner
├── launch-full-system.sh          # System launcher
├── requirements.txt               # Python dependencies
├── .env                           # API keys (configured)
└── README.md                      # This file
```

---

## Photo Database

The system includes 10 diverse photos:

1. **Golden Retriever Dog** - Happy pet in a park
2. **Sunset at Beach** - Ocean sunset scene
3. **Coffee Cup** - Hot coffee on wooden table
4. **Mountain Landscape** - Snow-capped peaks
5. **Tabby Cat** - Cozy indoor cat
6. **City Skyline** - Urban night scene
7. **Fresh Fruits** - Colorful fruit bowl
8. **Forest Path** - Autumn forest trail
9. **Modern Workspace** - Laptop and desk setup
10. **Flower Garden** - Spring blooms

Each photo includes:
- High-quality image from Unsplash
- Detailed description for screen readers
- Multiple searchable tags
- Unique ID for retrieval

---

## API Endpoints

### `POST /api/search`
Search for photos by query

**Request:**
```json
{
  "query": "dog"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Found 2 photo(s)",
  "photos": [
    {
      "id": 1,
      "title": "Golden Retriever Dog",
      "description": "A happy golden retriever...",
      "tags": ["dog", "pet", "animal"],
      "filename": "golden_retriever.jpg"
    }
  ]
}
```

### `GET /api/photo/<id>`
Get photo file by ID

### `GET /api/photos`
List all photos

### `GET /api/health`
Health check endpoint

---

## How to Use the Web Interface

### Typing Search
1. Click in the search box or press `Ctrl+K`
2. Type your search query (e.g., "cat", "nature", "coffee")
3. Press Enter or click "Search"

### Voice Search
1. Click the microphone button or press `Ctrl+/`
2. Speak your search query clearly
3. The system will automatically search

### Browsing Results
- **Tab** through photo cards
- **Enter** or **Click** a card to hear its description
- Click **"Hear Description"** button for audio description
- All images have detailed alt text for screen readers

### Keyboard Shortcuts
- `Ctrl/Cmd + K` - Focus search box
- `Ctrl/Cmd + /` - Start voice input
- `Tab` - Navigate through results
- `Enter` - Activate selected item

---

## Letta AI Agent

The Letta agent provides intelligent search capabilities:

- **Semantic Understanding**: Matches "pet" with "dog" and "cat"
- **Context Awareness**: Understands natural language queries
- **Relevance Ranking**: Returns most relevant photos first
- **Fallback Search**: Graceful degradation if Letta API unavailable

### Agent Features
- Uses Letta's LLM and embedding models
- Maintains conversation context
- Provides explanations for matches
- Continuously learns from interactions

---

## Fetch.ai Agent

The Fetch.ai agent enables decentralized deployment:

- **Network Address**: Unique agent address on Fetch network
- **Message Protocol**: Handles `PhotoSearchRequest` messages
- **Discovery**: Can be found by other agents on the network
- **Scalability**: Multiple instances can run independently

### Agent Communication

**Send a search request:**
```python
from uagents import Model

class PhotoSearchRequest(Model):
    query: str
    user_id: str

# Send to agent
await ctx.send(agent_address, PhotoSearchRequest(
    query="sunset",
    user_id="user123"
))
```

**Receive response:**
```python
class PhotoSearchResponse(Model):
    success: bool
    photos: List[Dict]
    message: str
```

---

## Accessibility Standards

This system follows:
- **WCAG 2.1 AA** standards for web accessibility
- **WAI-ARIA** best practices for dynamic content
- **Semantic HTML5** for screen reader compatibility
- **Keyboard accessibility** for all features
- **Voice interface** for hands-free operation

### Tested With
- macOS VoiceOver
- NVDA (Windows)
- Chrome speech recognition/synthesis
- Safari speech APIs
- Keyboard-only navigation

---

## Configuration

### Environment Variables

The `.env` file contains your API keys:

```bash
LETTA_API_KEY=sk-let-...
FETCH_API_KEY=eyJhbG...
```

These are already configured with your keys!

### Customization

**Add more photos:**
1. Edit `data/photo_database.json`
2. Add new photo entries with URLs
3. Run `python setup_photo_data.py`

**Modify UI:**
- Edit `ui/index.html` for structure
- Edit `ui/style.css` for styling
- Edit `ui/app.js` for behavior

**Adjust Agent:**
- Edit `agents/letta_photo_agent.py` for search logic
- Edit `agents/fetch_agent.py` for network behavior

---

## Troubleshooting

### "Letta agent failed to initialize"
- Check your `LETTA_API_KEY` in `.env`
- System falls back to keyword search automatically
- No impact on functionality

### "Voice input not working"
- Use Chrome or Safari (best support)
- Allow microphone permissions when prompted
- Check browser console for errors

### "Photos not loading"
- Run `python setup_photo_data.py` to download photos
- Check `data/photos/` directory exists
- Verify internet connection

### "Fetch.ai agent errors"
- Ensure `uagents` package is installed
- Check port 8001 is available
- Review agent logs for details

---

## Demo Script for Presentation

1. **Open the web interface** → http://localhost:5000

2. **Show accessibility features:**
   - "Notice the clean, high-contrast design"
   - "Click the microphone and say 'dog'"
   - "See how it finds relevant photos"

3. **Show voice output:**
   - "Click a photo card"
   - "Hear the detailed description"
   - "Perfect for blind users"

4. **Show keyboard navigation:**
   - "Press Tab to navigate"
   - "Press Enter to hear descriptions"
   - "Fully keyboard accessible"

5. **Show different searches:**
   - Try: "pet", "nature", "food", "work"
   - Show relevance of results

6. **Explain the tech:**
   - "Powered by Letta AI for smart search"
   - "Deployed on Fetch.ai network"
   - "Real AI agents working together"

---

## Technologies Used

- **Letta**: AI agent framework for intelligent search
- **Fetch.ai**: Decentralized agent network
- **Flask**: Python web framework
- **Web Speech API**: Voice input/output
- **Unsplash**: High-quality photos
- **HTML/CSS/JS**: Accessible web interface

---

## Future Enhancements

- [ ] Image recognition for automatic tagging
- [ ] Multi-language support
- [ ] User photo uploads
- [ ] Advanced voice commands
- [ ] Agent-to-agent photo sharing
- [ ] Vector similarity search
- [ ] Photo categorization
- [ ] Favorites and collections

---

## License

Built for educational and demonstration purposes.
Photos sourced from Unsplash (free to use).

---

## Support

For issues or questions:
1. Check this README
2. Review code comments
3. Check browser console for errors
4. Verify API keys in `.env`

---

## Acknowledgments

- **Letta** for the AI agent framework
- **Fetch.ai** for the decentralized agent network
- **Unsplash** for beautiful, free photos
- Built with accessibility and inclusion in mind

---

**Ready to search? Run `./launch-full-system.sh` and let's go!** 🚀
