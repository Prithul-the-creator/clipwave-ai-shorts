#!/usr/bin/env python3
"""
Test the new YouTube download strategies locally
"""

import os
import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.append('backend')
from video_processor import VideoProcessor

async def test_strategies():
    """Test the new download strategies"""
    print("🧪 Testing New Download Strategies")
    print("=" * 50)
    
    # Test URLs (from simple to potentially problematic)
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - reliable test video
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo - first YouTube video
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🎯 Test {i}: {url}")
        print("-" * 30)
        
        try:
            # Create processor with temporary job ID
            processor = VideoProcessor(f"test-{i}")
            
            # Try to download
            await processor._download_youtube_video(url, str(processor.video_path))
            
            # Check if successful
            if processor.video_path.exists() and processor.video_path.stat().st_size > 0:
                file_size = processor.video_path.stat().st_size
                print(f"✅ Success! Downloaded {file_size} bytes")
                
                # Clean up
                processor.video_path.unlink()
                processor.temp_dir.rmdir()
            else:
                print("❌ Failed - no file created")
                
        except Exception as e:
            print(f"❌ Failed with error: {e}")
        
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_strategies())