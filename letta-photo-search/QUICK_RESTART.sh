#!/bin/bash

echo "🛑 Stopping all agents..."
pkill -9 -f "perception_agent.py"
pkill -9 -f "emotion_agent.py"
pkill -9 -f "narration_agent.py"
pkill -9 -f "coordinator_agent.py"

sleep 2

echo "✅ Agents stopped"
echo ""
echo "🚀 Starting agents with the fix..."
python3 run_story_agents.py
