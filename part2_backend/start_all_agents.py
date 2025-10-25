# start_all_agents.py - Start all Fetch.ai agents and collect their addresses
import subprocess
import time
import re
import os

def extract_address(log_output):
    """Extract agent address from startup log"""
    match = re.search(r'Agent started: (agent1[a-z0-9]+)', log_output)
    if match:
        return match.group(1)
    return None

def start_agent(script_name, port):
    """Start an agent and return its address"""
    print(f"🚀 Starting {script_name} on port {port}...")
    env = os.environ.copy()
    env['PYTHONPATH'] = '/Users/amruthasrivatsav/Desktop/CalHacks/part2_backend'

    process = subprocess.Popen(
        ['python', f'agents/{script_name}.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd='/Users/amruthasrivatsav/Desktop/CalHacks/part2_backend',
        env=env
    )

    # Wait for startup and extract address
    address = None
    timeout = 30
    start_time = time.time()

    while time.time() - start_time < timeout and not address:
        if process.poll() is not None:
            # Process ended
            output, _ = process.communicate()
            print(f"❌ {script_name} failed to start:")
            print(output)
            return None

        # Read output
        output = process.stdout.readline()
        if output:
            print(f"[{script_name}] {output.strip()}")
            address = extract_address(output)
            if address:
                print(f"✅ {script_name} address: {address}")
                break

        time.sleep(0.1)

    if not address:
        print(f"❌ Could not extract address for {script_name}")
        process.terminate()
        return None

    return address, process

def main():
    agents = [
        ("perception_agent", 8001),
        ("emotion_agent", 8002),
        ("narration_agent", 8003),
        ("voice_agent", 8004),
        ("audio_mixer_agent", 8005)
    ]

    running_processes = []
    addresses = {}

    print("🎯 Starting all Fetch.ai agents...\n")

    for script_name, port in agents:
        address, process = start_agent(script_name, port)
        if address and process:
            addresses[script_name.replace('_agent', '')] = address
            running_processes.append((script_name, process))
        else:
            print(f"❌ Failed to start {script_name}")
            break

    if len(addresses) == len(agents):
        print("\n🎉 All agents started successfully!")
        print("\n📋 Agent Addresses:")
        for name, addr in addresses.items():
            print(f"  {name}: {addr}")

        print("\n💡 Copy these addresses to AGENT_ADDRESSES in main.py")
        print("\n⚠️  Agents are running in background. Press Ctrl+C to stop all.")

        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all agents...")
            for name, process in running_processes:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait()
            print("✅ All agents stopped.")

    else:
        print("❌ Not all agents started successfully. Stopping...")
        for name, process in running_processes:
            process.terminate()

if __name__ == "__main__":
    main()
