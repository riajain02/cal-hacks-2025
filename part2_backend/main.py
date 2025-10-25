# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import uuid
from fetch_models import VisionAnalysisRequest, ExperienceComplete, ErrorMessage
from uagents import Agent
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Photo-to-Audio Experience API")

# Mount static files
app.mount("/static", StaticFiles(directory="storage/audio"), name="audio")

# Shared request queue for agent communication
import json
import os
REQUEST_FILE = "storage/requests.json"
RESPONSE_DIR = "storage/responses/"

os.makedirs(RESPONSE_DIR, exist_ok=True)

@app.post("/api/experience/create")
async def create_experience(request: Request):
    try:
        data = await request.json()
        photo_url = data.get("photo_url")
        user_id = data.get("user_id", "api_user")

        if not photo_url:
            raise HTTPException(status_code=400, detail="photo_url required")

        session_id = f"{user_id}_{uuid.uuid4().hex[:8]}"

        # Check if agents are running by trying to connect to bureau
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8001))  # Bureau on port 8001
        sock.close()

        if result != 0:
            raise HTTPException(
                status_code=503,
                detail="Agent bureau not running. Please start agents with 'python3 run_agents.py'"
            )

        # Write request to shared file for agents to pick up
        request_data = {
            "session_id": session_id,
            "photo_url": photo_url,
            "timestamp": str(uuid.uuid4())
        }

        # Write to request queue
        with open(REQUEST_FILE, "w") as f:
            json.dump(request_data, f)

        # Wait for response (poll the response file)
        response_file = f"{RESPONSE_DIR}/{session_id}.json"
        import time
        timeout = 300  # 5 minutes timeout for processing
        start_time = time.time()

        while time.time() - start_time < timeout:
            if os.path.exists(response_file):
                with open(response_file, "r") as f:
                    response_data = json.load(f)
                os.remove(response_file)  # Clean up
                return response_data

            time.sleep(2)  # Check every 2 seconds

        # Timeout
        raise HTTPException(
            status_code=504,
            detail="Request timed out after 5 minutes - agents may be processing or there may be an error. Check agent logs."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demo")
async def demo_page():
    return FileResponse("index.html")

@app.get("/")
async def root():
    return {"message": "Photo-to-Audio Experience API", "docs": "/docs"}

if __name__ == "__main__":
    print("🚀 Starting FastAPI server...")
    print("🌐 API: http://localhost:9000")
    print("🎭 Demo: http://localhost:9000/demo")
    print("🤖 IMPORTANT: Start agents first with 'python3 run_agents.py'")
    uvicorn.run(app, host="0.0.0.0", port=9000)
