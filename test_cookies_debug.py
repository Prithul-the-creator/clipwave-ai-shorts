#!/usr/bin/env python3
"""
Debug script to test cookies and download functionality step by step
"""

import os
import base64
import subprocess
import json
import tempfile
from pathlib import Path

def test_environment():
    """Test environment variables"""
    print("🔍 Environment Test")
    print("=" * 50)
    
    cookies_b64 = os.getenv("YOUTUBE_COOKIES_B64")
    print(f"YOUTUBE_COOKIES_B64: {'✅ Set' if cookies_b64 else '❌ Missing'}")
    
    if cookies_b64:
        print(f"Length: {len(cookies_b64)} characters")
        try:
            decoded = base64.b64decode(cookies_b64).decode('utf-8')
            print(f"Decoded length: {len(decoded)} characters")
            print(f"Lines: {len(decoded.splitlines())}")
            print(f"Starts with Netscape format: {decoded.startswith('# Netscape HTTP Cookie File')}")
            
            # Check for common YouTube domains
            youtube_domains = ['.youtube.com', '.google.com', '.googlevideo.com']
            has_youtube = any(domain in decoded for domain in youtube_domains)
            print(f"Contains YouTube domains: {has_youtube}")
            
        except Exception as e:
            print(f"❌ Failed to decode: {e}")
    
    print()

def test_yt_dlp_basic():
    """Test basic yt-dlp functionality"""
    print("📦 yt-dlp Basic Test")
    print("=" * 50)
    
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        print(f"Version: {result.stdout.strip()}")
        print(f"Status: {'✅ Working' if result.returncode == 0 else '❌ Failed'}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

def test_video_info():
    """Test video info extraction"""
    print("📹 Video Info Test")
    print("=" * 50)
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        cmd = ['yt-dlp', '--dump-json', '--no-playlist', test_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            print(f"✅ Title: {info.get('title', 'Unknown')}")
            print(f"✅ Duration: {info.get('duration', 'Unknown')} seconds")
            print(f"✅ Available formats: {len(info.get('formats', []))}")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_download_without_cookies():
    """Test download without cookies"""
    print("⬜ Download WITHOUT Cookies")
    print("=" * 50)
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    output_file = "/tmp/test_no_cookies.mp4"
    
    try:
        cmd = [
            'yt-dlp',
            '--format', 'best[height<=480]',
            '--output', output_file,
            '--quiet',
            test_url
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"✅ Success! File size: {size} bytes")
            os.remove(output_file)
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_download_with_cookies():
    """Test download with cookies"""
    print("🍪 Download WITH Cookies")
    print("=" * 50)
    
    cookies_b64 = os.getenv("YOUTUBE_COOKIES_B64")
    if not cookies_b64:
        print("❌ No cookies available")
        return False
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    output_file = "/tmp/test_with_cookies.mp4"
    
    try:
        # Create temporary cookies file
        cookies_content = base64.b64decode(cookies_b64).decode('utf-8')
        cookies_file = "/tmp/test_cookies.txt"
        
        with open(cookies_file, 'w') as f:
            f.write(cookies_content)
        
        print(f"✅ Created cookies file: {cookies_file}")
        print(f"Cookies file size: {os.path.getsize(cookies_file)} bytes")
        
        cmd = [
            'yt-dlp',
            '--cookies', cookies_file,
            '--format', 'best[height<=480]',
            '--output', output_file,
            '--quiet',
            test_url
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"✅ Success! File size: {size} bytes")
            os.remove(output_file)
            success = True
        else:
            print(f"❌ Failed: {result.stderr}")
            success = False
        
        # Clean up
        os.remove(cookies_file)
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cookies_content():
    """Analyze cookies content"""
    print("🔍 Cookies Content Analysis")
    print("=" * 50)
    
    cookies_b64 = os.getenv("YOUTUBE_COOKIES_B64")
    if not cookies_b64:
        print("❌ No cookies available")
        return
    
    try:
        cookies_content = base64.b64decode(cookies_b64).decode('utf-8')
        lines = cookies_content.splitlines()
        
        print(f"Total lines: {len(lines)}")
        
        # Count valid cookie lines
        valid_cookies = 0
        youtube_cookies = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('\t')
            if len(parts) == 7:
                valid_cookies += 1
                domain = parts[0]
                if '.youtube.com' in domain or '.google.com' in domain:
                    youtube_cookies += 1
        
        print(f"Valid cookies: {valid_cookies}")
        print(f"YouTube/Google cookies: {youtube_cookies}")
        
        # Show first few YouTube cookies
        print("\nFirst 5 YouTube cookies:")
        count = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('\t')
            if len(parts) == 7 and ('.youtube.com' in parts[0] or '.google.com' in parts[0]):
                print(f"  {parts[0]} - {parts[5]}")
                count += 1
                if count >= 5:
                    break
        
    except Exception as e:
        print(f"❌ Error analyzing cookies: {e}")

def main():
    """Run all tests"""
    print("🧪 Comprehensive Cookie & Download Test")
    print("=" * 60)
    
    test_environment()
    test_yt_dlp_basic()
    
    if not test_video_info():
        print("❌ Cannot extract video info - basic yt-dlp issue")
        return
    
    print("\n" + "="*60)
    print("DOWNLOAD TESTS")
    print("="*60)
    
    success_no_cookies = test_download_without_cookies()
    print()
    success_with_cookies = test_download_with_cookies()
    print()
    
    test_cookies_content()
    print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"Without cookies: {'✅ Works' if success_no_cookies else '❌ Fails'}")
    print(f"With cookies: {'✅ Works' if success_with_cookies else '❌ Fails'}")
    
    if success_no_cookies and not success_with_cookies:
        print("\n🚨 COOKIES ARE MAKING THINGS WORSE!")
        print("Recommendation: Remove cookies from environment variables")
    elif not success_no_cookies and success_with_cookies:
        print("\n✅ COOKIES ARE HELPING!")
    elif success_no_cookies and success_with_cookies:
        print("\n✅ BOTH WORK - cookies are optional")
    else:
        print("\n❌ NEITHER WORKS - deeper issue")

if __name__ == "__main__":
    main() 