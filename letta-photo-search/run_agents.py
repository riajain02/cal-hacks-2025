#!/usr/bin/env python3
"""
Script to run the Fetch.ai agent
This deploys the photo search agent on the Fetch.ai network
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Fetch agent
from agents.fetch_agent import fetch_agent

if __name__ == "__main__":
    print("=" * 70)
    print("FETCH.AI PHOTO SEARCH AGENT")
    print("=" * 70)
    print("\nThis agent is now running on the Fetch.ai network!")
    print(f"\nAgent Address: {fetch_agent.address}")
    print("\nThe agent will:")
    print("  ✓ Listen for PhotoSearchRequest messages")
    print("  ✓ Use Letta AI to intelligently search photos")
    print("  ✓ Return matching photos with descriptions")
    print("\n" + "=" * 70)
    print("\nPress Ctrl+C to stop the agent\n")

    try:
        fetch_agent.run()
    except KeyboardInterrupt:
        print("\n\nAgent stopped by user")
        sys.exit(0)
