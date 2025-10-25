#!/usr/bin/env python3
"""
Simple script to run all Fetch.ai agents in the background
Displays their output and allows graceful shutdown
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def main():
    """Launch all agents"""
    print(f"\n{'='*70}")
    print("LAUNCHING ALL FETCH.AI AGENTS")
    print(f"{'='*70}\n")
    print("Starting agents in background...")
    print("Their logs will be saved to the 'logs/' directory")
    print("\nPress Ctrl+C to stop all agents\n")
    print(f"{'='*70}\n")

    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)

    # Change to agents directory
    agents_dir = Path(__file__).parent / 'agents'

    # Start agents
    agents = [
        ('fetch_voice_agent.py', 'Voice Processing Agent', 8002),
        ('fetch_search_agent.py', 'Image Search Agent', 8003),
        ('fetch_coordinator_agent.py', 'Coordinator Agent', 8004),
    ]

    processes = []

    for agent_file, agent_name, port in agents:
        agent_path = agents_dir / agent_file
        log_file = logs_dir / f"{agent_file.replace('.py', '.log')}"

        if agent_path.exists():
            print(f"Starting {agent_name} (port {port})...")
            print(f"  Log file: {log_file}")

            # Open log file
            log_f = open(log_file, 'w')

            # Start process
            proc = subprocess.Popen(
                [sys.executable, str(agent_path)],
                stdout=log_f,
                stderr=subprocess.STDOUT,
                bufsize=1
            )

            processes.append((proc, agent_name, log_f))
            print(f"  ✓ Started (PID {proc.pid})")
            time.sleep(2)  # Give agent time to start
        else:
            print(f"  ✗ Not found: {agent_file}")

    if not processes:
        print("\nNo agents started!")
        return

    print(f"\n{'='*70}")
    print("ALL AGENTS RUNNING")
    print(f"{'='*70}\n")
    print(f"Started {len(processes)} agents:")
    for proc, name, _ in processes:
        print(f"  ✓ {name} (PID {proc.pid})")

    print(f"\nTo view logs in real-time:")
    print(f"  tail -f logs/fetch_voice_agent.log")
    print(f"  tail -f logs/fetch_search_agent.log")
    print(f"  tail -f logs/fetch_coordinator_agent.log")

    print(f"\n{'='*70}")
    print("Press Ctrl+C to stop all agents")
    print(f"{'='*70}\n")

    # Monitor processes
    def cleanup(sig=None, frame=None):
        """Clean up all processes"""
        print("\n\nShutting down all agents...")
        for proc, name, log_f in processes:
            if proc.poll() is None:
                print(f"  Stopping {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except:
                    proc.kill()
            log_f.close()
        print("All agents stopped.")
        sys.exit(0)

    # Register signal handler
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        while True:
            # Check if any process has died
            for i, (proc, name, _) in enumerate(processes):
                if proc.poll() is not None:
                    print(f"\n⚠️  Warning: {name} has stopped (exit code {proc.returncode})")
                    print(f"   Check logs/fetch_{name.lower().replace(' ', '_')}.log for details")

            time.sleep(5)

    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
