"""
Enhanced Flask Backend for Accessible Photo Search
Integrates Letta voice processing, embedding search, and Fish Audio services
"""
import os
import json
import uuid
import asyncio
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agents and services
from agents.letta_voice_agent import VoiceProcessingAgent
from agents.embedding_search_agent import EmbeddingSearchAgent
from services.fish_audio_service import UnifiedTTSService

# Initialize Flask app
app = Flask(__name__, static_folder='ui', static_url_path='')
CORS(app)

# Global agent instances (lazy loading)
voice_agent = None
search_agent = None
tts_service = None

# Audio storage directory
AUDIO_DIR = Path('storage/audio')
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def get_voice_agent():
    """Get or create the voice processing agent"""
    global voice_agent
    if voice_agent is None:
        print("Initializing Voice Processing Agent...")
        try:
            voice_agent = VoiceProcessingAgent()
        except Exception as e:
            print(f"Error initializing voice agent: {e}")
            voice_agent = None
    return voice_agent

def get_search_agent():
    """Get or create the embedding search agent"""
    global search_agent
    if search_agent is None:
        print("Initializing Embedding Search Agent...")
        try:
            search_agent = EmbeddingSearchAgent()
        except Exception as e:
            print(f"Error initializing search agent: {e}")
            search_agent = None
    return search_agent

def get_tts_service():
    """Get or create the TTS service"""
    global tts_service
    if tts_service is None:
        print("Initializing TTS Service...")
        try:
            tts_service = UnifiedTTSService()
        except Exception as e:
            print(f"Error initializing TTS service: {e}")
            tts_service = None
    return tts_service

# Routes
@app.route('/')
def index():
    """Serve the new futuristic UI"""
    return send_from_directory('ui', 'index_new.html')

@app.route('/classic')
def classic():
    """Serve the classic UI"""
    return send_from_directory('ui', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('ui', path)

@app.route('/api/search', methods=['POST'])
def search():
    """
    Enhanced search endpoint
    Processes voice/text input and returns matching photos
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        use_voice_processing = data.get('use_voice_processing', True)

        if not query:
            return jsonify({
                'success': False,
                'message': 'Query is required',
                'photos': []
            }), 400

        print(f"Received search query: {query}")

        # Step 1: Process voice input if enabled
        processed_query = query
        entities = []
        context = {}

        if use_voice_processing:
            v_agent = get_voice_agent()
            if v_agent:
                print("Processing voice input...")
                voice_result = v_agent.process_voice_input(query)
                processed_query = voice_result['search_query']
                entities = voice_result['entities']
                context = voice_result['context']
                print(f"  Processed query: {processed_query}")
                print(f"  Entities: {entities}")
                print(f"  Context: {context}")

        # Step 2: Search for images
        s_agent = get_search_agent()
        if s_agent:
            print("Searching for images...")
            if entities or context:
                results = s_agent.search_with_context(
                    query=processed_query,
                    entities=entities,
                    context=context,
                    top_k=3
                )
            else:
                results = s_agent.search(processed_query, top_k=3)
        else:
            return jsonify({
                'success': False,
                'message': 'Search agent not available',
                'photos': []
            }), 500

        print(f"Found {len(results)} results")

        return jsonify({
            'success': True,
            'message': f'Found {len(results)} photo(s)',
            'photos': results,
            'query': query,
            'processed_query': processed_query,
            'entities': entities,
            'context': context
        })

    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'photos': []
        }), 500

@app.route('/api/voice/process', methods=['POST'])
def process_voice():
    """
    Process voice input to extract intent and entities
    """
    try:
        data = request.get_json()
        voice_text = data.get('text', '').strip()

        if not voice_text:
            return jsonify({
                'success': False,
                'message': 'Voice text is required'
            }), 400

        v_agent = get_voice_agent()
        if not v_agent:
            return jsonify({
                'success': False,
                'message': 'Voice processing agent not available'
            }), 500

        result = v_agent.process_voice_input(voice_text)

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        print(f"Voice processing error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/tts', methods=['POST'])
async def text_to_speech():
    """
    Convert text to speech using Fish Audio or OpenAI
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({
                'success': False,
                'message': 'Text is required'
            }), 400

        tts = get_tts_service()
        if not tts:
            return jsonify({
                'success': False,
                'message': 'TTS service not available'
            }), 500

        # Generate unique filename
        filename = f"{uuid.uuid4()}.mp3"
        filepath = AUDIO_DIR / filename

        # Generate audio
        await tts.text_to_speech(text, save_to=str(filepath))

        # Return URL to audio file
        audio_url = f"/api/audio/{filename}"

        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'message': 'Audio generated successfully'
        })

    except Exception as e:
        print(f"TTS error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        return send_file(AUDIO_DIR / filename, mimetype='audio/mpeg')
    except Exception as e:
        print(f"Error serving audio: {e}")
        return jsonify({'error': str(e)}), 404

@app.route('/api/photo/<int:photo_id>')
def get_photo(photo_id):
    """Get a specific photo file"""
    try:
        s_agent = get_search_agent()
        if not s_agent:
            return jsonify({'error': 'Search agent not available'}), 500

        photo = s_agent.get_photo_by_id(photo_id)

        if not photo:
            # Return Unsplash URL instead
            return jsonify({
                'url': photo.get('url', '')
            })

        # Serve from Unsplash URL
        return jsonify({
            'url': photo.get('url', '')
        })

    except Exception as e:
        print(f"Error serving photo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/photos')
def list_photos():
    """List all available photos"""
    try:
        s_agent = get_search_agent()
        if not s_agent:
            return jsonify({
                'success': False,
                'message': 'Search agent not available'
            }), 500

        return jsonify({
            'success': True,
            'photos': s_agent.photo_database
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'voice_agent': 'ready' if voice_agent else 'not_initialized',
        'search_agent': 'ready' if search_agent else 'not_initialized',
        'tts_service': 'ready' if tts_service else 'not_initialized'
    })

@app.route('/api/agent-status')
def agent_status():
    """Get status of all agents"""
    return jsonify({
        'voice_agent': {
            'initialized': voice_agent is not None,
            'type': 'Letta Voice Processing'
        },
        'search_agent': {
            'initialized': search_agent is not None,
            'type': 'Embedding-based Search',
            'photos_count': len(search_agent.photo_database) if search_agent else 0
        },
        'tts_service': {
            'initialized': tts_service is not None,
            'type': 'Fish Audio / OpenAI TTS'
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("ENHANCED ACCESSIBLE PHOTO SEARCH - BACKEND SERVER")
    print("=" * 60)
    print("\nStarting server...")
    print("UI will be available at: http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  POST /api/search - Search for photos (with voice processing)")
    print("  POST /api/voice/process - Process voice input")
    print("  POST /api/tts - Generate text-to-speech")
    print("  GET  /api/audio/<filename> - Get audio file")
    print("  GET  /api/photo/<id> - Get specific photo")
    print("  GET  /api/photos - List all photos")
    print("  GET  /api/health - Health check")
    print("  GET  /api/agent-status - Agent status")
    print("\n" + "=" * 60)

    # Pre-initialize agents
    print("\nInitializing agents...")
    try:
        get_voice_agent()
        get_search_agent()
        get_tts_service()
        print("✓ All agents initialized successfully")
    except Exception as e:
        print(f"Warning: Some agents failed to initialize: {e}")

    # Run the app (use asyncio-compatible server for production)
    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    config = Config()
    config.bind = ["0.0.0.0:5000"]

    print("\nStarting server...")
    asyncio.run(serve(app, config))
