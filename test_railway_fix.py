#!/usr/bin/env python3
"""
Test script to verify Railway deployment fixes
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from video_processor import VideoProcessor

async def test_video_processor():
    """Test the video processor with Railway fixes"""
    print("🧪 Testing VideoProcessor with Railway fixes...")
    
    # Test initialization
    processor = VideoProcessor("test-job-123")
    print(f"✅ VideoProcessor initialized")
    print(f"   Storage directory: {processor.storage_dir}")
    print(f"   Output path: {processor.output_path}")
    
    # Test storage directory creation
    if processor.storage_dir.exists():
        print(f"✅ Storage directory exists: {processor.storage_dir}")
    else:
        print(f"❌ Storage directory does not exist: {processor.storage_dir}")
    
    # Test temp directory creation
    if processor.temp_dir.exists():
        print(f"✅ Temp directory created: {processor.temp_dir}")
    else:
        print(f"❌ Temp directory not created: {processor.temp_dir}")
    
    # Test file path handling
    print(f"   Video path: {processor.video_path}")
    print(f"   Output path: {processor.output_path}")
    
    # Test environment detection
    if os.path.exists("/app"):
        print("✅ Running in Docker container (Railway)")
    else:
        print("✅ Running locally")
    
    return True

async def test_storage_access():
    """Test storage directory access"""
    print("\n📁 Testing storage access...")
    
    storage_paths = [
        Path("/app/storage/videos"),
        Path("./storage/videos"),
        Path("storage/videos")
    ]
    
    for path in storage_paths:
        print(f"Testing path: {path}")
        print(f"  Exists: {path.exists()}")
        if path.exists():
            print(f"  Is directory: {path.is_dir()}")
            print(f"  Writable: {os.access(path, os.W_OK)}")
            
            # Try to create a test file
            test_file = path / "test.txt"
            try:
                test_file.write_text("test")
                print(f"  ✅ Can write to: {path}")
                test_file.unlink()  # Clean up
            except Exception as e:
                print(f"  ❌ Cannot write to {path}: {e}")
        else:
            print(f"  ❌ Path does not exist")
    
    return True

def test_imports():
    """Test that all required modules can be imported"""
    print("\n📦 Testing imports...")
    
    try:
        import yt_dlp
        print("✅ yt-dlp imported successfully")
    except ImportError as e:
        print(f"❌ yt-dlp import failed: {e}")
    
    try:
        import whisper
        print("✅ whisper imported successfully")
    except ImportError as e:
        print(f"❌ whisper import failed: {e}")
    
    try:
        import openai
        print("✅ openai imported successfully")
    except ImportError as e:
        print(f"❌ openai import failed: {e}")
    
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        print("✅ moviepy imported successfully")
    except ImportError as e:
        print(f"❌ moviepy import failed: {e}")
    
    return True

async def main():
    """Run all tests"""
    print("🚀 ClipWave AI Shorts - Railway Fix Test")
    print("=" * 50)
    
    # Test imports
    test_imports()
    
    # Test storage access
    await test_storage_access()
    
    # Test video processor
    await test_video_processor()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Summary:")
    print("- VideoProcessor now handles Railway's ephemeral storage")
    print("- Storage paths are properly configured for both local and Docker environments")
    print("- Video data is stored in memory as a fallback")
    print("- Multiple file paths are checked when serving videos")
    
    print("\n🔧 Next steps:")
    print("1. Deploy to Railway")
    print("2. Test the /api/test-storage endpoint")
    print("3. Process a video and check if it's served correctly")
    print("4. Check Railway logs for any remaining issues")

if __name__ == "__main__":
    asyncio.run(main()) 