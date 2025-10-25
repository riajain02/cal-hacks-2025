#!/bin/bash
# Launch script for the complete Accessible Photo Search system

echo "=========================================="
echo "ACCESSIBLE PHOTO SEARCH SYSTEM LAUNCHER"
echo "Powered by Letta AI & Fetch.ai"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "=========================================="
echo "SYSTEM COMPONENTS:"
echo "=========================================="
echo ""
echo "1. Web UI Server (Flask) - Port 5000"
echo "   URL: http://localhost:5000"
echo ""
echo "2. Fetch.ai Agent - Port 8001"
echo "   Listens for agent messages on Fetch network"
echo ""
echo "3. Letta AI Agent"
echo "   Provides intelligent photo search"
echo ""
echo "=========================================="
echo ""

# Ask user which component to run
echo "What would you like to launch?"
echo ""
echo "1) Web UI Only (recommended for demo)"
echo "2) Fetch.ai Agent Only"
echo "3) Both (requires multiple terminals)"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Starting Web UI Server..."
        echo "Navigate to http://localhost:5000 in your browser"
        echo ""
        python app.py
        ;;
    2)
        echo ""
        echo "Starting Fetch.ai Agent..."
        python run_agents.py
        ;;
    3)
        echo ""
        echo "To run both components, you need to:"
        echo "1. Open a new terminal and run: python app.py"
        echo "2. Open another terminal and run: python run_agents.py"
        echo ""
        echo "Or use the individual commands above."
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac
