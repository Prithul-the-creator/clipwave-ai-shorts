import os
import json
import uuid
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import asyncio
from video_processor import VideoProcessor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="ClipWave AI Shorts API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "https://clipwave-ai-shorts-production.up.railway.app",
        # Add your custom domain here when you have it
        # "https://clipwave.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                print(f"Error sending message to {user_id}: {e}")
                self.disconnect(user_id)

manager = ConnectionManager()

# In-memory storage for jobs (in production, use a database)
jobs: Dict[str, Dict[str, Any]] = {}

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    print("Health check endpoint called")
    return {"status": "healthy", "message": "ClipWave AI Shorts API is running"}

@app.get("/api/health")
async def api_health_check():
    """Alternative health check endpoint"""
    print("API health check endpoint called")
    return {"status": "healthy", "message": "ClipWave AI Shorts API is running"}

@app.get("/")
async def read_root():
    """Serve the frontend application"""
    if os.path.exists("dist/index.html"):
        return FileResponse("dist/index.html")
    elif os.path.exists("../dist/index.html"):
        return FileResponse("../dist/index.html")
    return {"message": "ClipWave AI Shorts API"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any incoming WebSocket messages if needed
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.post("/api/jobs")
async def create_job(
    youtube_url: str = Form(...),
    instructions: str = Form(""),
    user_id: str = Form(...)
):
    """Create a new video processing job"""
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "id": job_id,
        "youtube_url": youtube_url,
        "instructions": instructions,
        "user_id": user_id,
        "status": "processing",
        "progress": 0,
        "created_at": asyncio.get_event_loop().time(),
        "video_path": None,
        "clips": [],
        "transcript": ""
    }
    
    # Start processing in background
    asyncio.create_task(process_video_job(job_id, youtube_url, instructions, user_id))
    
    return {"job_id": job_id, "status": "processing"}

async def process_video_job(job_id: str, youtube_url: str, instructions: str, user_id: str):
    """Process video in background"""
    try:
        processor = VideoProcessor(job_id)
        
        def progress_callback(progress: int, step: str):
            jobs[job_id]["progress"] = progress
            asyncio.create_task(
                manager.send_personal_message(
                    json.dumps({
                        "type": "progress",
                        "job_id": job_id,
                        "progress": progress,
                        "step": step
                    }),
                    user_id
                )
            )
        
        # Process the video
        result = await processor.process_video(youtube_url, instructions, progress_callback)
        
        # Update job with results
        jobs[job_id].update({
            "status": "completed",
            "progress": 100,
            "video_path": result["video_path"],
            "clips": result["clips"],
            "transcript": result["transcript"]
        })
        
        # Send completion message
        await manager.send_personal_message(
            json.dumps({
                "type": "completed",
                "job_id": job_id,
                "result": {
                    "video_path": result["video_path"],
                    "clips": result["clips"]
                }
            }),
            user_id
        )
        
    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "error": str(e)
        })
        
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "job_id": job_id,
                "error": str(e)
            }),
            user_id
        )

@app.get("/api/jobs")
async def get_jobs(user_id: str):
    """Get all jobs for a user"""
    user_jobs = [job for job in jobs.values() if job["user_id"] == user_id]
    return user_jobs

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str, user_id: str):
    """Get a specific job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return job

@app.get("/api/videos/{job_id}")
async def get_video(job_id: str, user_id: str):
    """Get video file for a job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if job["status"] != "completed" or not job["video_path"]:
        raise HTTPException(status_code=404, detail="Video not ready")
    
    video_path = Path(job["video_path"])
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(video_path, media_type="video/mp4")

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str, user_id: str):
    """Delete a job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete video file if it exists
    if job["video_path"]:
        try:
            Path(job["video_path"]).unlink(missing_ok=True)
        except Exception:
            pass
    
    del jobs[job_id]
    return {"message": "Job deleted"}

# Mount static files for frontend (after all API routes)
if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")
elif os.path.exists("../dist"):
    app.mount("/", StaticFiles(directory="../dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting ClipWave AI Shorts API on port {port}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Dist directory exists: {os.path.exists('dist')}")
    print(f"../dist directory exists: {os.path.exists('../dist')}")
    uvicorn.run(app, host="0.0.0.0", port=port) 