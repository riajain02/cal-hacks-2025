"""
Flask Backend for Accessible Photo Search
Serves the UI and provides API endpoints for photo search
"""
import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Letta photo search agent
from agents.letta_photo_agent import PhotoSearchAgent

# Initialize Flask app
app = Flask(__name__, static_folder='ui', static_url_path='')
CORS(app)

# Initialize Letta agent (lazy loading)
photo_agent = None


def get_photo_agent():
    """Get or create the photo search agent"""
    global photo_agent
    if photo_agent is None:
        print("Initializing Letta Photo Search Agent...")
        try:
            photo_agent = PhotoSearchAgent()
            print("Agent initialized successfully!")
        except Exception as e:
            print(f"Error initializing agent: {e}")
            # Create a fallback agent that works without Letta
            photo_agent = FallbackPhotoAgent()
    return photo_agent


class FallbackPhotoAgent:
    """Fallback agent when Letta is not available"""

    def __init__(self):
        with open('data/photo_database.json', 'r') as f:
            data = json.load(f)
        self.photo_database = data['photos']

    def search_photos(self, query):
        """Simple keyword search"""
        query_lower = query.lower()
        matches = []

        for photo in self.photo_database:
            score = 0
            if query_lower in photo['title'].lower():
                score += 10
            if query_lower in photo['description'].lower():
                score += 5
            for tag in photo['tags']:
                if query_lower in tag.lower() or tag.lower() in query_lower:
                    score += 3

            if score > 0:
                matches.append({**photo, 'relevance_score': score})

        matches.sort(key=lambda x: x['relevance_score'], reverse=True)
        return matches[:3]

    def get_photo_by_id(self, photo_id):
        """Get photo by ID"""
        for photo in self.photo_database:
            if photo['id'] == photo_id:
                return photo
        return None


# Routes
@app.route('/')
def index():
    """Serve the main UI"""
    return send_from_directory('ui', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('ui', path)


@app.route('/api/search', methods=['POST'])
def search():
    """Search for photos based on query"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({
                'success': False,
                'message': 'Query is required',
                'photos': []
            }), 400

        print(f"Searching for: {query}")

        # Get agent and perform search
        agent = get_photo_agent()
        results = agent.search_photos(query)

        print(f"Found {len(results)} results")

        return jsonify({
            'success': True,
            'message': f'Found {len(results)} photo(s)',
            'photos': results,
            'query': query
        })

    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'photos': []
        }), 500


@app.route('/api/photo/<int:photo_id>')
def get_photo(photo_id):
    """Get a specific photo file"""
    try:
        agent = get_photo_agent()
        photo = agent.get_photo_by_id(photo_id)

        if not photo:
            return jsonify({'error': 'Photo not found'}), 404

        # Serve the actual photo file
        photo_path = Path('data/photos') / photo['filename']

        if not photo_path.exists():
            return jsonify({'error': 'Photo file not found'}), 404

        return send_file(photo_path, mimetype='image/jpeg')

    except Exception as e:
        print(f"Error serving photo: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/photos')
def list_photos():
    """List all available photos"""
    try:
        agent = get_photo_agent()
        return jsonify({
            'success': True,
            'photos': agent.photo_database
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
        'agent': 'ready' if photo_agent else 'not_initialized'
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Accessible Photo Search - Backend Server")
    print("=" * 60)
    print("\nStarting server...")
    print("UI will be available at: http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  POST /api/search - Search for photos")
    print("  GET  /api/photo/<id> - Get specific photo")
    print("  GET  /api/photos - List all photos")
    print("  GET  /api/health - Health check")
    print("\n" + "=" * 60)

    # Pre-initialize the agent
    try:
        get_photo_agent()
    except Exception as e:
        print(f"Warning: Could not initialize Letta agent: {e}")
        print("Using fallback search mode")

    app.run(host='0.0.0.0', port=5000, debug=True)
