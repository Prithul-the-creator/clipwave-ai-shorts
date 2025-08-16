import os
import json
import uuid
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form, Response
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
        "http://localhost:8080",
        "https://clipwave-ai-shorts-production.up.railway.app",
        # Add your custom domain here when you have it
        # "https://clipwave.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory - try multiple possible locations
static_dirs = ["../static", "./static", "../dist", "./dist"]
for static_dir in static_dirs:
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        print(f"Mounted static files from: {os.path.abspath(static_dir)}")
        break

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

@app.get("/api/test-storage")
async def test_storage():
    """Test storage directory access"""
    try:
        # Test different storage paths
        storage_paths = [
            Path("/app/storage/videos"),
            Path("./storage/videos"),
            Path("storage/videos")
        ]
        
        results = {}
        for path in storage_paths:
            results[str(path)] = {
                "exists": path.exists(),
                "is_dir": path.is_dir() if path.exists() else False,
                "writable": os.access(path, os.W_OK) if path.exists() else False
            }
        
        # Try to create a test file
        test_file = Path("/app/storage/videos/test.txt") if os.path.exists("/app") else Path("./storage/videos/test.txt")
        try:
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("test")
            test_file.unlink()  # Clean up
            results["test_write"] = True
        except Exception as e:
            results["test_write"] = False
            results["write_error"] = str(e)
        
        return {
            "status": "storage_test",
            "current_dir": os.getcwd(),
            "storage_paths": results
        }
    except Exception as e:
        return {
            "status": "storage_test_failed",
            "error": str(e)
        }

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
            "transcript": result["transcript"],
            "video_data": result.get("video_data")  # Store video data for Railway
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
    print(f"get_jobs called with user_id: {user_id}")
    print(f"All jobs: {jobs}")
    user_jobs = [job for job in jobs.values() if job["user_id"] == user_id]
    print(f"User jobs: {user_jobs}")
    return {"jobs": user_jobs}

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
    
    # Add debugging information
    print(f"Requesting video for job {job_id}")
    print(f"Video path: {video_path}")
    print(f"Video path absolute: {video_path.absolute()}")
    print(f"Video path exists: {video_path.exists()}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Storage directory exists: {Path('/app/storage/videos').exists() if os.path.exists('/app') else Path('./storage/videos').exists()}")
    
    # Try multiple possible paths for the video file
    possible_paths = [
        video_path,
        Path(f"/app/storage/videos/{job_id}.mp4"),
        Path(f"./storage/videos/{job_id}.mp4"),
        Path(f"storage/videos/{job_id}.mp4"),
        Path(f"/tmp/{job_id}.mp4"),  # Fallback to temp directory
    ]
    
    found_video_path = None
    for path in possible_paths:
        print(f"Trying path: {path} - exists: {path.exists()}")
        if path.exists() and path.stat().st_size > 0:
            found_video_path = path
            print(f"Found video at: {found_video_path}")
            break
    
    if not found_video_path:
        # If no video file found, check if we can serve from job data
        if "video_data" in job and job["video_data"]:
            # Serve from base64 encoded data
            import base64
            video_data = base64.b64decode(job["video_data"])
            return Response(
                content=video_data,
                media_type="video/mp4",
                headers={"Content-Disposition": f"attachment; filename=clip_{job_id}.mp4"}
            )
        else:
            raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(found_video_path, media_type="video/mp4")

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

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "status": "ok",
        "message": "ClipWave AI Shorts API is working",
        "timestamp": asyncio.get_event_loop().time(),
        "environment": "production" if os.path.exists("/app") else "development"
    }

@app.get("/api/test-download")
async def test_download():
    """Test video download functionality"""
    try:
        from video_processor import VideoProcessor
        
        # Test with a simple, short YouTube video
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short video
        
        processor = VideoProcessor("test-download-api")
        
        # Test download
        await processor._download_youtube_video(test_url, str(processor.video_path))
        
        # Check if file was created
        if processor.video_path.exists():
            file_size = processor.video_path.stat().st_size
            return {
                "status": "success",
                "message": "Video download test successful",
                "file_size": file_size,
                "file_path": str(processor.video_path),
                "temp_dir": str(processor.temp_dir)
            }
        else:
            return {
                "status": "error",
                "message": "Video file was not created",
                "temp_dir": str(processor.temp_dir),
                "files_in_temp": list(processor.temp_dir.glob('*')) if processor.temp_dir.exists() else []
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Video download test failed: {str(e)}",
            "error_type": type(e).__name__
        }

@app.get("/api/test-403-handling")
async def test_403_handling():
    """Test 403 error handling with different strategies"""
    try:
        from video_processor import VideoProcessor
        
        # Test with a potentially restricted video
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        processor = VideoProcessor("test-403-api")
        
        # Test download with comprehensive 403 handling
        await processor._download_youtube_video(test_url, str(processor.video_path))
        
        # Check if file was created
        if processor.video_path.exists():
            file_size = processor.video_path.stat().st_size
            return {
                "status": "success",
                "message": "403 handling test successful",
                "file_size": file_size,
                "file_path": str(processor.video_path),
                "strategies_used": "Multiple strategies attempted successfully"
            }
        else:
            return {
                "status": "error",
                "message": "403 handling test failed - no file created",
                "temp_dir": str(processor.temp_dir),
                "files_in_temp": list(processor.temp_dir.glob('*')) if processor.temp_dir.exists() else []
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"403 handling test failed: {str(e)}",
            "error_type": type(e).__name__,
            "suggestions": [
                "Try with a different YouTube URL",
                "Check if the video is age-restricted",
                "Verify the video is publicly accessible",
                "Consider using a VPN or different IP"
            ]
        }

@app.get("/api/diagnose")
async def diagnose_issues():
    """Diagnose YouTube download issues"""
    import subprocess
    import base64
    import json
    
    diagnosis = {
        "environment": {},
        "yt_dlp": {},
        "network": {},
        "cookies": {},
        "recommendations": []
    }
    
    # Environment check
    diagnosis["environment"]["openai_key"] = "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Missing"
    diagnosis["environment"]["cookies_b64"] = "✅ Set" if os.getenv("YOUTUBE_COOKIES_B64") else "❌ Missing"
    
    if os.getenv("YOUTUBE_COOKIES_B64"):
        cookies_b64 = os.getenv("YOUTUBE_COOKIES_B64")
        diagnosis["environment"]["cookies_length"] = len(cookies_b64)
        
        try:
            cookies_content = base64.b64decode(cookies_b64).decode('utf-8')
            diagnosis["environment"]["decoded_size"] = len(cookies_content)
            diagnosis["environment"]["cookie_lines"] = len(cookies_content.splitlines())
            diagnosis["environment"]["cookies_valid"] = cookies_content.startswith('# Netscape HTTP Cookie File')
        except Exception as e:
            diagnosis["environment"]["cookies_error"] = str(e)
    
    # yt-dlp check
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            diagnosis["yt_dlp"]["version"] = result.stdout.strip()
            diagnosis["yt_dlp"]["status"] = "✅ Working"
        else:
            diagnosis["yt_dlp"]["status"] = f"❌ Error: {result.stderr}"
    except Exception as e:
        diagnosis["yt_dlp"]["status"] = f"❌ Exception: {str(e)}"
    
    # Network connectivity test
    import urllib.request
    test_urls = ["https://www.youtube.com", "https://www.google.com"]
    
    for url in test_urls:
        try:
            response = urllib.request.urlopen(url, timeout=10)
            diagnosis["network"][url] = f"✅ Status: {response.getcode()}"
        except Exception as e:
            diagnosis["network"][url] = f"❌ Error: {str(e)}"
    
    # Test basic yt-dlp functionality
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        cmd = ['yt-dlp', '--dump-json', '--no-playlist', test_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                info = json.loads(result.stdout)
                diagnosis["yt_dlp"]["info_extraction"] = "✅ Success"
                diagnosis["yt_dlp"]["video_title"] = info.get('title', 'Unknown')
                diagnosis["yt_dlp"]["video_duration"] = info.get('duration', 'Unknown')
            except json.JSONDecodeError:
                diagnosis["yt_dlp"]["info_extraction"] = "⚠️ Success but couldn't parse JSON"
        else:
            diagnosis["yt_dlp"]["info_extraction"] = f"❌ Failed: {result.stderr[:200]}"
    except Exception as e:
        diagnosis["yt_dlp"]["info_extraction"] = f"❌ Exception: {str(e)}"
    
    # Test cookies effectiveness
    if os.getenv("YOUTUBE_COOKIES_B64"):
        try:
            cookies_content = base64.b64decode(os.getenv("YOUTUBE_COOKIES_B64")).decode('utf-8')
            cookies_file = "/tmp/diagnose_cookies.txt"
            with open(cookies_file, 'w') as f:
                f.write(cookies_content)
            
            cmd = [
                'yt-dlp',
                '--cookies', cookies_file,
                '--format', 'best[height<=480]',
                '--output', '/tmp/diagnose_test.mp4',
                '--quiet',
                test_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists('/tmp/diagnose_test.mp4'):
                file_size = os.path.getsize('/tmp/diagnose_test.mp4')
                diagnosis["cookies"]["download_test"] = f"✅ Success ({file_size} bytes)"
                os.remove('/tmp/diagnose_test.mp4')
            else:
                diagnosis["cookies"]["download_test"] = f"❌ Failed: {result.stderr[:200]}"
            
            os.remove(cookies_file)
        except Exception as e:
            diagnosis["cookies"]["download_test"] = f"❌ Exception: {str(e)}"
    else:
        diagnosis["cookies"]["download_test"] = "⚠️ No cookies to test"
    
    # Generate recommendations
    if not diagnosis["environment"]["openai_key"].startswith("✅"):
        diagnosis["recommendations"].append("Set OPENAI_API_KEY environment variable")
    
    if not diagnosis["environment"]["cookies_b64"].startswith("✅"):
        diagnosis["recommendations"].append("Set YOUTUBE_COOKIES_B64 environment variable")
    
    if not diagnosis["yt_dlp"]["status"].startswith("✅"):
        diagnosis["recommendations"].append("Fix yt-dlp installation")
    
    if any("❌" in status for status in diagnosis["network"].values()):
        diagnosis["recommendations"].append("Check network connectivity")
    
    if diagnosis["yt_dlp"].get("info_extraction", "").startswith("❌"):
        diagnosis["recommendations"].append("YouTube may be blocking requests - try different video or wait")
    
    if diagnosis["cookies"].get("download_test", "").startswith("❌"):
        diagnosis["recommendations"].append("Cookies may be invalid or expired - refresh them")
    
    if not diagnosis["recommendations"]:
        diagnosis["recommendations"].append("All systems appear to be working correctly")
    
    return diagnosis

@app.get("/api/test-simple")
async def test_simple_download():
    """Simple test to check if basic yt-dlp works on Railway"""
    import subprocess
    import tempfile
    import os
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    result = {
        "yt_dlp_version": "Unknown",
        "yt_dlp_working": False,
        "info_extraction": False,
        "download_test": False,
        "error": None
    }
    
    # Test 1: Check yt-dlp version
    try:
        version_result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True, timeout=10)
        if version_result.returncode == 0:
            result["yt_dlp_version"] = version_result.stdout.strip()
            result["yt_dlp_working"] = True
        else:
            result["error"] = f"yt-dlp version check failed: {version_result.stderr}"
            return result
    except Exception as e:
        result["error"] = f"yt-dlp not available: {str(e)}"
        return result
    
    # Test 2: Extract video info
    try:
        info_cmd = ['yt-dlp', '--dump-json', '--no-playlist', test_url]
        info_result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=30)
        
        if info_result.returncode == 0:
            import json
            info = json.loads(info_result.stdout)
            result["info_extraction"] = True
            result["video_title"] = info.get('title', 'Unknown')
            result["video_duration"] = info.get('duration', 'Unknown')
        else:
            result["error"] = f"Info extraction failed: {info_result.stderr[:200]}"
            return result
    except Exception as e:
        result["error"] = f"Info extraction error: {str(e)}"
        return result
    
    # Test 3: Try simple download
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            download_cmd = [
                'yt-dlp',
                '--format', 'worst[height<=360]',  # Use worst quality for faster test
                '--output', tmp_file.name,
                '--quiet',
                test_url
            ]
            
            download_result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=60)
            
            if download_result.returncode == 0 and os.path.exists(tmp_file.name):
                file_size = os.path.getsize(tmp_file.name)
                result["download_test"] = True
                result["file_size"] = file_size
                os.unlink(tmp_file.name)  # Clean up
            else:
                result["error"] = f"Download failed: {download_result.stderr[:200]}"
    except Exception as e:
        result["error"] = f"Download error: {str(e)}"
    
    return result

@app.get("/api/test-no-cookies")
async def test_without_cookies():
    """Test download without any cookies to see if they're causing issues"""
    import subprocess
    import tempfile
    import os
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    result = {
        "test_type": "Download without cookies",
        "success": False,
        "file_size": 0,
        "error": None,
        "command_used": ""
    }
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            # Create a clean environment without cookies
            env = os.environ.copy()
            env.pop('YOUTUBE_COOKIES_B64', None)  # Remove cookies from environment
            
            download_cmd = [
                'yt-dlp',
                '--format', 'worst[height<=360]',  # Use worst quality for faster test
                '--output', tmp_file.name,
                '--quiet',
                '--no-warnings',
                test_url
            ]
            
            result["command_used"] = ' '.join(download_cmd)
            
            download_result = subprocess.run(
                download_cmd, 
                capture_output=True, 
                text=True, 
                timeout=60,
                env=env  # Use clean environment
            )
            
            if download_result.returncode == 0 and os.path.exists(tmp_file.name):
                file_size = os.path.getsize(tmp_file.name)
                result["success"] = True
                result["file_size"] = file_size
                os.unlink(tmp_file.name)  # Clean up
            else:
                result["error"] = f"Download failed: {download_result.stderr[:300]}"
                
    except Exception as e:
        result["error"] = f"Download error: {str(e)}"
    
    return result

# Serve static assets (CSS, JS files)
@app.get("/assets/{file_path:path}")
async def serve_assets(file_path: str):
    """Serve static assets from static/assets directory"""
    asset_paths = [
        f"static/assets/{file_path}",
        f"../static/assets/{file_path}",
        f"dist/assets/{file_path}",
        f"../dist/assets/{file_path}"
    ]
    
    for asset_path in asset_paths:
        if os.path.exists(asset_path):
            return FileResponse(asset_path)
    
    raise HTTPException(status_code=404, detail="Asset not found")

# SPA routing - serve index.html for all non-API routes
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Serve index.html for all non-API routes to support SPA routing"""
    # Don't serve index.html for API routes
    if full_path.startswith("api/") or full_path.startswith("ws/"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Try multiple locations for index.html
    html_paths = [
        "static/index.html",
        "../static/index.html", 
        "dist/index.html",
        "../dist/index.html"
    ]
    
    for html_path in html_paths:
        if os.path.exists(html_path):
            return FileResponse(html_path)
    
    raise HTTPException(status_code=404, detail="Frontend not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting ClipWave AI Shorts API on port {port}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Environment check:")
    print(f"  - OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"  - YOUTUBE_COOKIES_B64: {'✅ Set' if os.getenv('YOUTUBE_COOKIES_B64') else '❌ Missing'}")
    print(f"Directory structure:")
    print(f"  - ./static exists: {os.path.exists('./static')}")
    print(f"  - ../static exists: {os.path.exists('../static')}")
    print(f"  - ./dist exists: {os.path.exists('./dist')}")
    print(f"  - ../dist exists: {os.path.exists('../dist')}")
    print(f"  - ./storage/videos exists: {os.path.exists('./storage/videos')}")
    print(f"  - /app/storage/videos exists: {os.path.exists('/app/storage/videos')}")
    uvicorn.run(app, host="0.0.0.0", port=port) 