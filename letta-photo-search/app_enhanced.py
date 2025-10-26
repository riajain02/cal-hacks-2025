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
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Import agents and services
from agents.letta_voice_agent import VoiceProcessingAgent
from agents.clip_search_agent import CLIPSearchAgent
from services.fish_audio_service import UnifiedTTSService
from agents.story_agent_client import StoryAgentClient

# Initialize Flask app
app = Flask(__name__, static_folder='ui', static_url_path='')
CORS(app)

# Global agent instances (lazy loading)
voice_agent = None
search_agent = None
tts_service = None
story_agent_client = None

# Storage directories
AUDIO_DIR = Path('storage/audio')
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

PHOTOS_DIR = Path('data/photos/uploaded')
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

# Allowed photo extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


# ----------------------------------------------------------
# Lazy agent getters
# ----------------------------------------------------------
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
            search_agent = CLIPSearchAgent()
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


def get_story_agent_client():
    """Get or create the story agent client"""
    global story_agent_client
    if story_agent_client is None:
        print("Initializing Story Agent Client...")
        try:
            story_agent_client = StoryAgentClient()
        except Exception as e:
            print(f"Error initializing story agent client: {e}")
            story_agent_client = None
    return story_agent_client


# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ----------------------------------------------------------
# Routes
# ----------------------------------------------------------
@app.route('/')
def index():
    """Serve the new futuristic UI"""
    return send_from_directory('ui', 'index_new.html')


@app.route('/classic')
def classic():
    """Serve the classic UI"""
    return send_from_directory('ui', 'index.html')


# Photo upload feature removed - memory generation is done from search results only
# @app.route('/story')
# def story():
#     """Serve the photo story generator UI"""
#     return send_from_directory('ui', 'story.html')


@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve image files"""
    return send_from_directory('images', filename)


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('ui', path)


# ----------------------------------------------------------
# Search and Voice APIs
# ----------------------------------------------------------
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
            return jsonify({'success': False, 'message': 'Query is required', 'photos': []}), 400

        print(f"Received search query: {query}")

        processed_query = query
        entities, context = [], {}

        if use_voice_processing:
            v_agent = get_voice_agent()
            if v_agent:
                print("Processing voice input...")
                voice_result = v_agent.process_voice_input(query)
                processed_query = voice_result['search_query']
                entities = voice_result['entities']
                context = voice_result['context']
                print(f"Processed query: {processed_query}")

        s_agent = get_search_agent()
        if not s_agent:
            return jsonify({'success': False, 'message': 'Search agent not available', 'photos': []}), 500

        print("Searching for images...")
        if entities or context:
            results = s_agent.search_with_context(query=processed_query, entities=entities, context=context, top_k=3)
        else:
            results = s_agent.search(processed_query, top_k=3)

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
        return jsonify({'success': False, 'message': f'Error: {str(e)}', 'photos': []}), 500


@app.route('/api/voice/process', methods=['POST'])
def process_voice():
    """Process voice input to extract intent and entities"""
    try:
        data = request.get_json()
        voice_text = data.get('text', '').strip()

        if not voice_text:
            return jsonify({'success': False, 'message': 'Voice text is required'}), 400

        v_agent = get_voice_agent()
        if not v_agent:
            return jsonify({'success': False, 'message': 'Voice processing agent not available'}), 500

        result = v_agent.process_voice_input(voice_text)
        return jsonify({'success': True, 'data': result})

    except Exception as e:
        print(f"Voice processing error: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ----------------------------------------------------------
# Text-to-Speech and Audio
# ----------------------------------------------------------
@app.route('/api/tts', methods=['POST'])
async def text_to_speech():
    """Convert text to speech using Fish Audio or OpenAI"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'success': False, 'message': 'Text is required'}), 400

        tts = get_tts_service()
        if not tts:
            return jsonify({'success': False, 'message': 'TTS service not available'}), 500

        filename = f"{uuid.uuid4()}.mp3"
        filepath = AUDIO_DIR / filename

        await tts.text_to_speech(text, save_to=str(filepath))
        audio_url = f"/api/audio/{filename}"

        return jsonify({'success': True, 'audio_url': audio_url, 'message': 'Audio generated successfully'})

    except Exception as e:
        print(f"TTS error: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        return send_file(AUDIO_DIR / filename, mimetype='audio/mpeg')
    except Exception as e:
        print(f"Error serving audio: {e}")
        return jsonify({'error': str(e)}), 404


# ----------------------------------------------------------
# Story Generation (photo upload feature removed)
# ----------------------------------------------------------
# Photo upload feature removed - memory generation is done from search results only
# @app.route('/api/photos/upload', methods=['POST'])
# def upload_photo():
#     """Upload a photo for story generation"""
#     try:
#         if 'photo' not in request.files:
#             return jsonify({'success': False, 'message': 'No photo file provided'}), 400
#
#         file = request.files['photo']
#         if file.filename == '':
#             return jsonify({'success': False, 'message': 'No file selected'}), 400
#         if not allowed_file(file.filename):
#             return jsonify({'success': False, 'message': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
#
#         filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
#         filepath = PHOTOS_DIR / filename
#         file.save(str(filepath))
#
#         photo_url = f"/api/photos/uploaded/{filename}"
#         return jsonify({
#             'success': True,
#             'message': 'Photo uploaded successfully',
#             'photo_id': str(uuid.uuid4()),
#             'photo_url': photo_url,
#             'filename': filename,
#             'filepath': str(filepath)
#         })
#
#     except Exception as e:
#         print(f"Upload error: {e}")
#         return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/story/generate', methods=['POST'])
async def generate_story():
    """
    Generate a story from a photo using the agent pipeline
    Expects: { "photo_url": "url_or_path", "photo_path": "optional_local_path" }
    """
    try:
        data = request.get_json()
        photo_url = data.get('photo_url')
        photo_path = data.get('photo_path')

        if not photo_url and not photo_path:
            return jsonify({'success': False, 'message': 'photo_url or photo_path is required'}), 400

        # Convert image_url to local path if needed
        if photo_url and photo_url.startswith('/images/'):
            from urllib.parse import unquote
            filename = unquote(photo_url.replace('/images/', ''))
            photo_path = f"images/{filename}"
            print(f"Using local path: {photo_path}")
        
        # Use photo_path if available, otherwise photo_url
        target_path = photo_path or photo_url
        print(f"Generating story for photo: {target_path}")

        story_client = get_story_agent_client()
        if not story_client:
            return jsonify({
                'success': False,
                'message': 'Story agent client not available. Make sure agents are running.'
            }), 500

        result = await story_client.generate_story_from_photo(target_path, timeout=120)
        if not result.get('success', False):
            return jsonify(result), 500

        narration_data = result.get('narration', {})
        narration_text = narration_data.get('main_narration', '')
        if narration_text:
            try:
                tts = get_tts_service()
                if tts:
                    session_id = result.get('session_id', 'unknown')
                    audio_filename = f"story_{session_id}.mp3"
                    audio_filepath = AUDIO_DIR / audio_filename

                    print("Generating audio narration...")
                    await tts.text_to_speech(narration_text, save_to=str(audio_filepath))

                    audio_url = f"/api/audio/{audio_filename}"
                    result['narration']['audio_url'] = audio_url
                    print(f"Audio narration generated: {audio_url}")
                else:
                    print("TTS service not available")
            except Exception as e:
                print(f"Audio generation failed: {e}")

        print(f"Story generated successfully: {result.get('session_id')}")
        return jsonify(result)

    except Exception as e:
        print(f"Story generation error: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ----------------------------------------------------------
# Health and Agent Status
# ----------------------------------------------------------
@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'voice_agent': 'ready' if voice_agent else 'not_initialized',
        'search_agent': 'ready' if search_agent else 'not_initialized',
        'tts_service': 'ready' if tts_service else 'not_initialized',
        'story_agent': 'ready' if story_agent_client else 'not_initialized'
    })


@app.route('/api/agent-status')
def agent_status():
    """Get status of all agents"""
    return jsonify({
        'voice_agent': {'initialized': voice_agent is not None, 'type': 'Letta Voice Processing'},
        'search_agent': {
            'initialized': search_agent is not None,
            'type': 'Embedding-based Search',
            'photos_count': len(search_agent.photo_database) if search_agent else 0
        },
        'tts_service': {'initialized': tts_service is not None, 'type': 'Fish Audio / OpenAI TTS'}
    })


# ----------------------------------------------------------
# Run server
# ----------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("ENHANCED ACCESSIBLE PHOTO SEARCH - BACKEND SERVER")
    print("=" * 60)
    print("Starting server...\nUI at: http://localhost:5000\n")

    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    config = Config()
    config.bind = ["0.0.0.0:5000"]

    # Pre-initialize agents
    print("Initializing agents...")
    try:
        get_voice_agent()
        get_search_agent()
        get_tts_service()
        print("✓ All agents initialized successfully")
    except Exception as e:
        print(f"Warning: Some agents failed to initialize: {e}")

    asyncio.run(serve(app, config))
