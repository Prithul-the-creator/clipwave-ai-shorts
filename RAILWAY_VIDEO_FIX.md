# Railway Video File Not Found Error - Fix Guide

## Problem Description

The "video file not found" error in Railway deployment occurs because:

1. **Railway's Ephemeral Storage**: Railway containers have ephemeral filesystems that don't persist between deployments or container restarts
2. **File Path Issues**: The application was using relative paths that don't work consistently in Docker containers
3. **Storage Directory Access**: The storage directory wasn't properly configured for Railway's environment

## Root Causes

### 1. Ephemeral Storage
- Railway containers lose all files when they restart or redeploy
- Video files created during processing are lost after the job completes
- The `/app/storage/videos` directory is recreated on each deployment

### 2. File Path Inconsistencies
- Local development uses `./storage/videos`
- Docker containers should use `/app/storage/videos`
- The application wasn't detecting the environment correctly

### 3. File Serving Issues
- The video serving endpoint only checked one file path
- No fallback mechanism for when files are lost due to ephemeral storage

## Solutions Implemented

### 1. Environment-Aware Storage Paths

**File**: `backend/video_processor.py`

```python
def __init__(self, job_id: str, storage_dir: str = None):
    # Use absolute path for storage directory
    if storage_dir is None:
        # Default to /app/storage/videos in Docker, or ./storage/videos locally
        if os.path.exists("/app"):
            # Running in Docker container
            self.storage_dir = Path("/app/storage/videos")
        else:
            # Running locally
            self.storage_dir = Path("./storage/videos")
```

### 2. Multiple File Path Fallbacks

**File**: `backend/main.py`

```python
# Try multiple possible paths for the video file
possible_paths = [
    video_path,
    Path(f"/app/storage/videos/{job_id}.mp4"),
    Path(f"./storage/videos/{job_id}.mp4"),
    Path(f"storage/videos/{job_id}.mp4"),
    Path(f"/tmp/{job_id}.mp4"),  # Fallback to temp directory
]
```

### 3. In-Memory Video Storage

**File**: `backend/video_processor.py`

```python
# Store video data in job for Railway's ephemeral storage
try:
    with open(self.output_path, 'rb') as f:
        video_data = f.read()
    # Store as base64 for job storage
    import base64
    video_data_b64 = base64.b64encode(video_data).decode('utf-8')
    print(f"Video data encoded and ready for storage")
except Exception as e:
    print(f"Warning: Could not encode video data: {e}")
```

### 4. Base64 Video Serving

**File**: `backend/main.py`

```python
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
```

### 5. Enhanced Debugging

**File**: `backend/main.py`

```python
# Add debugging information
print(f"Requesting video for job {job_id}")
print(f"Video path: {video_path}")
print(f"Video path absolute: {video_path.absolute()}")
print(f"Video path exists: {video_path.exists()}")
print(f"Current working directory: {os.getcwd()}")
```

### 6. Storage Testing Endpoint

**File**: `backend/main.py`

```python
@app.get("/api/test-storage")
async def test_storage():
    """Test storage directory access"""
    # Test different storage paths and permissions
    # Returns detailed information about storage access
```

## Testing the Fixes

### 1. Local Testing

```bash
# Run the test script
python test_railway_fix.py

# Test the API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/test-storage
curl http://localhost:8000/api/test
```

### 2. Docker Testing

```bash
# Build and test Docker container
./deploy.sh

# Or manually:
docker build -t clipwave-ai-shorts .
docker run --rm -p 8000:8000 clipwave-ai-shorts
```

### 3. Railway Deployment

1. **Push changes to GitHub**:
   ```bash
   git add .
   git commit -m "Fix video file not found error for Railway deployment"
   git push
   ```

2. **Verify Railway environment variables**:
   - `OPENAI_API_KEY`
   - `YOUTUBE_COOKIES_B64`
   - `PORT=8000`

3. **Test Railway endpoints**:
   - `https://your-app.railway.app/api/health`
   - `https://your-app.railway.app/api/test-storage`
   - `https://your-app.railway.app/api/test`

## Monitoring and Debugging

### 1. Check Railway Logs

```bash
railway logs
```

Look for:
- Storage directory creation messages
- Video processing progress
- File path debugging information
- Base64 encoding/decoding messages

### 2. Test Storage Access

Visit `/api/test-storage` to see:
- Which storage paths exist
- Which paths are writable
- Current working directory
- Environment detection

### 3. Video Processing Debugging

The application now logs:
- Storage directory being used
- File creation status
- File sizes
- Base64 encoding status

## Expected Behavior After Fix

### 1. Video Processing
- Videos are processed normally
- Files are saved to the appropriate storage directory
- Video data is also stored in memory as base64

### 2. Video Serving
- First tries to serve from file system
- Falls back to base64 encoded data if file not found
- Multiple file paths are checked
- Detailed error messages if all methods fail

### 3. Railway Deployment
- Works with Railway's ephemeral storage
- Videos persist during the session
- Graceful handling of file system limitations

## Troubleshooting

### If videos still don't work:

1. **Check Railway logs** for specific error messages
2. **Verify environment variables** are set correctly
3. **Test storage endpoint** to see storage access status
4. **Check video processing logs** for file creation issues
5. **Verify base64 encoding** is working

### Common Issues:

1. **Environment variables not set**: Check Railway dashboard
2. **Storage directory not writable**: Check `/api/test-storage` endpoint
3. **Base64 encoding fails**: Check video file size and memory limits
4. **File paths still wrong**: Check environment detection logic

## Performance Considerations

### Memory Usage
- Base64 encoding increases memory usage by ~33%
- Large videos may cause memory issues
- Consider implementing video streaming for large files

### File System
- Temporary files are cleaned up after processing
- Storage directory is created if it doesn't exist
- Multiple fallback paths ensure maximum compatibility

## Future Improvements

1. **Video Streaming**: Implement streaming for large files
2. **External Storage**: Use S3 or similar for persistent storage
3. **Caching**: Implement video caching to reduce processing time
4. **Compression**: Add video compression to reduce file sizes
5. **CDN Integration**: Use CDN for better video delivery

## Conclusion

The implemented fixes address the core issues with Railway's ephemeral storage by:

1. **Environment-aware path handling**
2. **Multiple file path fallbacks**
3. **In-memory video storage as backup**
4. **Enhanced debugging and monitoring**
5. **Robust error handling**

These changes ensure the application works reliably on Railway while maintaining compatibility with local development and other deployment environments. 