#!/bin/bash

echo "🛑 Stopping existing agents..."

# Find and kill all agent processes
pkill -f "perception_agent.py"
pkill -f "emotion_agent.py"
pkill -f "narration_agent.py"
pkill -f "coordinator_agent.py"

# Wait a moment for processes to terminate
sleep 2

echo "✅ Agents stopped"
echo ""
echo "🚀 Starting agents..."
echo ""

# Start the agents
python3 run_story_agents.py
