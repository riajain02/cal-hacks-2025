#!/usr/bin/env python3
"""
Run a single agent for testing/debugging
"""
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_single_agent.py <agent_number>")
        print("\nAvailable agents:")
        print("  1 - Voice Processing Agent (port 8002)")
        print("  2 - Image Search Agent (port 8003)")
        print("  3 - Coordinator Agent (port 8004)")
        sys.exit(1)

    agent_num = sys.argv[1]

    agents = {
        '1': 'fetch_voice_agent.py',
        '2': 'fetch_search_agent.py',
        '3': 'fetch_coordinator_agent.py',
    }

    if agent_num not in agents:
        print(f"Invalid agent number: {agent_num}")
        print("Choose 1, 2, or 3")
        sys.exit(1)

    agent_file = agents[agent_num]
    agent_path = Path(__file__).parent / 'agents' / agent_file

    if not agent_path.exists():
        print(f"Agent file not found: {agent_path}")
        sys.exit(1)

    print(f"Running {agent_file}...")
    print("Press Ctrl+C to stop\n")

    # Run the agent directly (output will show in terminal)
    import subprocess
    subprocess.run([sys.executable, str(agent_path)])

if __name__ == "__main__":
    main()
