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

@app.post("/api/experience/create")
async def create_experience(request: Request):
    try:
        data = await request.json()
        photo_url = data.get("photo_url")
        user_id = data.get("user_id", "api_user")

        if not photo_url:
            raise HTTPException(status_code=400, detail="photo_url required")

        session_id = f"{user_id}_{uuid.uuid4().hex[:8]}"

        # Try to communicate with agents - if agents are running, this will work
        try:
            # Check if agents are running by trying to connect to bureau
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()

            if result == 0:
                # Agents are running - try to send request via HTTP to coordinator
                vision_request = VisionAnalysisRequest(
                    photo_url=photo_url,
                    session_id=session_id
                )

                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(
                        "http://localhost:8006/submit",
                        json={
                            "type": "VisionAnalysisRequest",
                            "data": vision_request.__dict__
                        }
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return result
                    else:
                        raise Exception(f"Agent returned error: {response.text}")
            else:
                raise Exception("Agent bureau not running")

        except Exception as agent_error:
            # Agents not available - provide informative error
            raise HTTPException(
                status_code=503,
                detail=f"Agent system not available: {str(agent_error)}. Please start agents with 'python3 run_agents.py'"
            )

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
