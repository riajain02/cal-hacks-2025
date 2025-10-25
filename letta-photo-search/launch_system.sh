#!/bin/bash

# Launch Script for Complete Voice-to-Image Search System
# This script sets up and launches all components

set -e

echo "=========================================================================="
echo "  VOICE-TO-IMAGE SEARCH SYSTEM FOR BLIND USERS"
echo "  Powered by Letta AI, Fetch.ai, and Fish Audio"
echo "=========================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Python is installed
print_step "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check if pip is installed
print_step "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip."
    exit 1
fi
print_success "pip3 found"

# Install dependencies
print_step "Installing dependencies..."
print_warning "This may take a few minutes (especially for PyTorch and transformers)..."
pip3 install -r requirements.txt -q
print_success "Dependencies installed"

# Create necessary directories
print_step "Creating necessary directories..."
mkdir -p data
mkdir -p storage/audio
print_success "Directories created"

# Check if photo database exists
print_step "Checking photo database..."
if [ ! -f "data/photo_database.json" ]; then
    print_error "Photo database not found at data/photo_database.json"
    print_warning "Please ensure the photo database file exists"
    exit 1
fi
print_success "Photo database found"

# Generate embeddings
print_step "Generating/loading photo embeddings..."
python3 -c "from agents.embedding_search_agent import EmbeddingSearchAgent; EmbeddingSearchAgent()" 2>/dev/null || true
print_success "Embeddings ready"

# Check .env file
print_step "Checking environment variables..."
if [ ! -f ".env" ]; then
    print_error ".env file not found"
    print_warning "Please create a .env file with your API keys"
    exit 1
fi
print_success ".env file found"

echo ""
echo "=========================================================================="
echo "  SYSTEM READY"
echo "=========================================================================="
echo ""
echo "Select launch mode:"
echo ""
echo "  1. Launch web app only (recommended for demos)"
echo "  2. Launch Fetch.ai agents only"
echo "  3. Launch everything (web app + all agents)"
echo "  4. Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        print_step "Launching web application..."
        echo ""
        echo "=========================================================================="
        echo "  WEB APPLICATION STARTING"
        echo "=========================================================================="
        echo ""
        echo "  URL: http://localhost:5000"
        echo ""
        echo "  Features:"
        echo "    ✓ Voice input and output"
        echo "    ✓ Letta AI voice processing"
        echo "    ✓ Embedding-based image search"
        echo "    ✓ Fish Audio text-to-speech"
        echo ""
        echo "  Press Ctrl+C to stop"
        echo ""
        echo "=========================================================================="
        python3 app_enhanced.py
        ;;

    2)
        print_step "Launching Fetch.ai agents..."
        echo ""
        echo "=========================================================================="
        echo "  FETCH.AI AGENTS STARTING"
        echo "=========================================================================="
        echo ""
        echo "  Agents:"
        echo "    ✓ Voice Processing Agent (port 8002)"
        echo "    ✓ Image Search Agent (port 8003)"
        echo "    ✓ Coordinator Agent (port 8004)"
        echo ""
        echo "  Logs will be saved to logs/ directory"
        echo "  Press Ctrl+C to stop all agents"
        echo ""
        echo "=========================================================================="
        python3 run_all_agents_simple.py
        ;;

    3)
        print_step "Launching complete system..."
        echo ""
        echo "=========================================================================="
        echo "  COMPLETE SYSTEM STARTING"
        echo "=========================================================================="
        echo ""
        print_warning "This will launch multiple processes"
        print_warning "Use separate terminals or run in tmux/screen for best results"
        echo ""

        # Start agents in background
        python3 run_all_agents_simple.py &
        AGENTS_PID=$!

        # Give agents time to start
        sleep 5

        # Start web app
        python3 app_enhanced.py &
        WEBAPP_PID=$!

        echo ""
        echo "  System running!"
        echo "    - Web app: http://localhost:5000"
        echo "    - Agents: ports 8002, 8003, 8004"
        echo "    - Agent logs: logs/ directory"
        echo ""
        echo "  Press Ctrl+C to stop everything"
        echo ""

        # Wait for user interrupt
        trap "kill $AGENTS_PID $WEBAPP_PID 2>/dev/null; exit" INT
        wait
        ;;

    4)
        echo "Exiting..."
        exit 0
        ;;

    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac
