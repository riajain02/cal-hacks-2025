#!/usr/bin/env python3
"""
Master script to run all Fetch.ai agents
Launches voice processing, image search, and coordinator agents
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Store process handles
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nShutting down all agents...")
    for p in processes:
        if p is not None:
            try:
                p.terminate()
            except:
                pass
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

def run_agent(agent_file, agent_name, port):
    """Run a single agent in a subprocess"""
    print(f"\n{'='*60}")
    print(f"Starting {agent_name} on port {port}...")
    print(f"{'='*60}")

    try:
        process = subprocess.Popen(
            [sys.executable, agent_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        print(f"  ✓ Process started with PID {process.pid}")
        return process
    except Exception as e:
        print(f"  ✗ Error starting agent: {e}")
        return None

def main():
    """Launch all agents"""
    print(f"\n{'='*70}")
    print("LAUNCHING ALL FETCH.AI AGENTS")
    print(f"{'='*70}\n")
    print("This will start the following agents:")
    print("  1. Voice Processing Agent (port 8002)")
    print("  2. Image Search Agent (port 8003)")
    print("  3. Coordinator Agent (port 8004)")
    print(f"\n{'='*70}\n")

    # Change to agents directory
    agents_dir = Path(__file__).parent / 'agents'

    # Start agents
    agents = [
        ('fetch_voice_agent.py', 'Voice Processing Agent', 8002),
        ('fetch_search_agent.py', 'Image Search Agent', 8003),
        ('fetch_coordinator_agent.py', 'Coordinator Agent', 8004),
    ]

    for agent_file, agent_name, port in agents:
        agent_path = agents_dir / agent_file
        if agent_path.exists():
            proc = run_agent(str(agent_path), agent_name, port)
            processes.append(proc)
            time.sleep(2)  # Give each agent time to start
        else:
            print(f"Warning: {agent_file} not found")

    print(f"\n{'='*70}")
    print("ALL AGENTS RUNNING")
    print(f"{'='*70}\n")
    print("Agent addresses will be displayed above.")
    print("Press Ctrl+C to stop all agents")
    print(f"\n{'='*70}\n")

    # Monitor processes
    try:
        while True:
            for i, proc in enumerate(processes):
                # Skip if process is None
                if proc is None:
                    continue

                # Check if any process has output
                if proc.poll() is None:  # Process still running
                    # Read output without blocking
                    pass
                else:
                    print(f"\nWarning: Agent {i+1} has stopped")
                    processes[i] = None

            time.sleep(1)

    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
