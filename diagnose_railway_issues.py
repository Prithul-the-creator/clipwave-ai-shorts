#!/usr/bin/env python3
"""
Railway YouTube Download Diagnostic Tool
Helps identify why all download strategies are failing
"""

import os
import sys
import base64
import subprocess
import asyncio
from pathlib import Path

def check_environment():
    """Check environment variables and system setup"""
    print("🔍 Environment Diagnostics")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    print(f"   OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"   YOUTUBE_COOKIES_B64: {'✅ Set' if os.getenv('YOUTUBE_COOKIES_B64') else '❌ Missing'}")
    
    if os.getenv('YOUTUBE_COOKIES_B64'):
        cookies_b64 = os.getenv('YOUTUBE_COOKIES_B64')
        print(f"   Cookies B64 length: {len(cookies_b64)} characters")
        
        # Try to decode cookies
        try:
            cookies_content = base64.b64decode(cookies_b64).decode('utf-8')
            print(f"   Decoded cookies size: {len(cookies_content)} characters")
            print(f"   Cookie lines: {len(cookies_content.splitlines())}")
            
            # Check if cookies look valid
            if cookies_content.startswith('# Netscape HTTP Cookie File'):
                print("   ✅ Cookies format looks valid")
            else:
                print("   ❌ Cookies format may be invalid")
                
        except Exception as e:
            print(f"   ❌ Failed to decode cookies: {e}")
    
    # Check system info
    print(f"\n💻 System Info:")
    print(f"   Python version: {sys.version}")
    print(f"   Platform: {sys.platform}")
    print(f"   Working directory: {os.getcwd()}")
    
    # Check if we're in Docker/Railway
    if os.path.exists('/app'):
        print("   ✅ Running in Docker container")
    else:
        print("   ℹ️  Running locally")
    
    return True

def check_yt_dlp():
    """Check yt-dlp installation and version"""
    print("\n📦 yt-dlp Diagnostics")
    print("=" * 50)
    
    try:
        # Check yt-dlp version
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ yt-dlp version: {version}")
            
            # Check if version is recent
            if '2025' in version or '2024' in version:
                print("   ✅ yt-dlp version is recent")
            else:
                print("   ⚠️  yt-dlp version may be outdated")
        else:
            print(f"   ❌ yt-dlp not working: {result.stderr}")
            return False
    except FileNotFoundError:
        print("   ❌ yt-dlp not found")
        return False
    except Exception as e:
        print(f"   ❌ yt-dlp error: {e}")
        return False
    
    return True

def test_network_connectivity():
    """Test network connectivity to YouTube"""
    print("\n🌐 Network Connectivity Test")
    print("=" * 50)
    
    test_urls = [
        "https://www.youtube.com",
        "https://www.google.com",
        "https://httpbin.org/get"
    ]
    
    import urllib.request
    import urllib.error
    
    for url in test_urls:
        try:
            print(f"   Testing {url}...")
            response = urllib.request.urlopen(url, timeout=10)
            print(f"   ✅ {url} - Status: {response.getcode()}")
        except urllib.error.URLError as e:
            print(f"   ❌ {url} - Error: {e}")
        except Exception as e:
            print(f"   ❌ {url} - Unexpected error: {e}")

def test_basic_yt_dlp():
    """Test basic yt-dlp functionality"""
    print("\n🧪 Basic yt-dlp Test")
    print("=" * 50)
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Test 1: Just extract info (no download)
    print("   Testing info extraction...")
    try:
        cmd = ['yt-dlp', '--dump-json', '--no-playlist', test_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Info extraction successful")
            # Parse JSON to get basic info
            import json
            try:
                info = json.loads(result.stdout)
                print(f"   📹 Title: {info.get('title', 'Unknown')}")
                print(f"   ⏱️  Duration: {info.get('duration', 'Unknown')} seconds")
                print(f"   👁️  View count: {info.get('view_count', 'Unknown')}")
            except json.JSONDecodeError:
                print("   ⚠️  Could not parse video info")
        else:
            print(f"   ❌ Info extraction failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ Info extraction timed out")
        return False
    except Exception as e:
        print(f"   ❌ Info extraction error: {e}")
        return False
    
    return True

def test_cookies_effectiveness():
    """Test if cookies are actually helping"""
    print("\n🍪 Cookies Effectiveness Test")
    print("=" * 50)
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Test without cookies first
    print("   Testing WITHOUT cookies...")
    try:
        cmd = [
            'yt-dlp',
            '--format', 'best[height<=480]',
            '--output', '/tmp/test_no_cookies.mp4',
            '--quiet',
            test_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists('/tmp/test_no_cookies.mp4'):
            file_size = os.path.getsize('/tmp/test_no_cookies.mp4')
            print(f"   ✅ Download without cookies successful ({file_size} bytes)")
            os.remove('/tmp/test_no_cookies.mp4')
            no_cookies_work = True
        else:
            print(f"   ❌ Download without cookies failed: {result.stderr}")
            no_cookies_work = False
    except Exception as e:
        print(f"   ❌ Download without cookies error: {e}")
        no_cookies_work = False
    
    # Test with cookies
    print("   Testing WITH cookies...")
    cookies_file = None
    cookies_work = False
    
    # Create temporary cookies file
    if os.getenv('YOUTUBE_COOKIES_B64'):
        try:
            cookies_content = base64.b64decode(os.getenv('YOUTUBE_COOKIES_B64')).decode('utf-8')
            cookies_file = '/tmp/test_cookies.txt'
            with open(cookies_file, 'w') as f:
                f.write(cookies_content)
            print(f"   ✅ Created temporary cookies file: {cookies_file}")
        except Exception as e:
            print(f"   ❌ Failed to create cookies file: {e}")
            return False
    
    if cookies_file and os.path.exists(cookies_file):
        try:
            cmd = [
                'yt-dlp',
                '--cookies', cookies_file,
                '--format', 'best[height<=480]',
                '--output', '/tmp/test_with_cookies.mp4',
                '--quiet',
                test_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists('/tmp/test_with_cookies.mp4'):
                file_size = os.path.getsize('/tmp/test_with_cookies.mp4')
                print(f"   ✅ Download with cookies successful ({file_size} bytes)")
                os.remove('/tmp/test_with_cookies.mp4')
                cookies_work = True
            else:
                print(f"   ❌ Download with cookies failed: {result.stderr}")
                cookies_work = False
        except Exception as e:
            print(f"   ❌ Download with cookies error: {e}")
            cookies_work = False
        
        # Clean up
        try:
            os.remove(cookies_file)
        except:
            pass
    else:
        print("   ⚠️  No cookies available to test")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Without cookies: {'✅ Works' if no_cookies_work else '❌ Fails'}")
    print(f"   With cookies: {'✅ Works' if cookies_work else '❌ Fails'}")
    
    if no_cookies_work and not cookies_work:
        print("   ⚠️  Cookies are actually making things worse!")
    elif not no_cookies_work and cookies_work:
        print("   ✅ Cookies are helping!")
    elif no_cookies_work and cookies_work:
        print("   ✅ Both work - cookies are optional")
    else:
        print("   ❌ Neither approach works - deeper issue")
    
    return True

def test_different_formats():
    """Test different video formats and qualities"""
    print("\n🎬 Format Testing")
    print("=" * 50)
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    formats = [
        'worst',
        'worst[height<=360]',
        'best[height<=480]',
        'best[height<=720]',
        'best'
    ]
    
    for format_spec in formats:
        print(f"   Testing format: {format_spec}")
        try:
            cmd = [
                'yt-dlp',
                '--format', format_spec,
                '--output', f'/tmp/test_{format_spec.replace("[", "_").replace("]", "_").replace("=", "_")}.mp4',
                '--quiet',
                test_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"   ✅ {format_spec} - Success")
            else:
                print(f"   ❌ {format_spec} - Failed: {result.stderr[:100]}...")
        except Exception as e:
            print(f"   ❌ {format_spec} - Error: {e}")

def generate_report():
    """Generate a comprehensive diagnostic report"""
    print("\n📋 Diagnostic Report")
    print("=" * 50)
    
    print("\n🔧 Recommendations:")
    print("1. If cookies are making things worse, try without them")
    print("2. If network connectivity fails, check Railway's network settings")
    print("3. If yt-dlp is outdated, update it in your Dockerfile")
    print("4. If basic tests fail, the issue is with yt-dlp or YouTube's anti-bot measures")
    print("5. Consider using a different video source for testing")
    
    print("\n🛠️  Next Steps:")
    print("1. Check Railway logs for specific error messages")
    print("2. Try a different YouTube video URL")
    print("3. Test with a VPN or different IP if possible")
    print("4. Consider implementing a fallback video processing method")

async def main():
    """Main diagnostic function"""
    print("🔍 Railway YouTube Download Diagnostic Tool")
    print("=" * 60)
    
    # Run all diagnostics
    check_environment()
    check_yt_dlp()
    test_network_connectivity()
    test_basic_yt_dlp()
    test_cookies_effectiveness()
    test_different_formats()
    generate_report()
    
    print("\n🎉 Diagnostic complete!")
    print("Check the results above to identify the issue.")

if __name__ == "__main__":
    asyncio.run(main()) 