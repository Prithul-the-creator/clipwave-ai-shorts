#!/usr/bin/env python3
"""
Simple YouTube Cookie Extractor using yt-dlp
Based on official yt-dlp documentation
"""

import subprocess
import base64
from pathlib import Path

def extract_cookies_from_browser():
    """Extract cookies from browser using yt-dlp's official method"""
    
    # Create cookies directory
    cookies_dir = Path("cookies")
    cookies_dir.mkdir(exist_ok=True)
    
    cookies_file = cookies_dir / "youtube_cookies.txt"
    
    print("🍪 Extracting YouTube cookies using yt-dlp...")
    print("=" * 50)
    
    # Try different browsers
    browsers = ['chrome', 'firefox', 'safari', 'edge', 'brave']
    
    for browser in browsers:
        print(f"\n🔄 Trying {browser}...")
        
        try:
            # Use yt-dlp's official method: --cookies-from-browser
            cmd = [
                'yt-dlp',
                '--cookies-from-browser', browser,
                '--cookies', str(cookies_file)
            ]
            
            print(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and cookies_file.exists():
                # Check if file has content
                with open(cookies_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.strip():
                    print(f"✅ Successfully extracted cookies from {browser}")
                    print(f"   File: {cookies_file}")
                    print(f"   Size: {len(content)} characters")
                    print(f"   Lines: {len(content.splitlines())}")
                    
                    # Process the cookies
                    process_cookies(cookies_file)
                    return True
                else:
                    print(f"⚠️  {browser} cookies file is empty")
            else:
                print(f"⚠️  {browser} extraction failed")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
                    
        except subprocess.TimeoutExpired:
            print(f"⚠️  {browser} extraction timed out")
        except Exception as e:
            print(f"⚠️  {browser} extraction error: {e}")
    
    print("\n❌ Could not extract cookies from any browser")
    print("\n💡 Alternative methods:")
    print("1. Make sure you're logged into YouTube in your browser")
    print("2. Try opening YouTube in a new tab and refreshing")
    print("3. Use a different browser")
    print("4. Check if your browser is supported by yt-dlp")
    
    return False

def process_cookies(cookies_file):
    """Process the extracted cookies and create base64 version"""
    
    print("\n🔧 Processing cookies...")
    
    # Read cookies
    with open(cookies_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encode to base64
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # Save base64 version
    b64_file = cookies_file.parent / "youtube_cookies_b64.txt"
    with open(b64_file, 'w', encoding='utf-8') as f:
        f.write(encoded)
    
    # Create environment example
    env_content = f"""# ClipWave AI Shorts Environment Variables

# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# YouTube Cookies (base64 encoded)
YOUTUBE_COOKIES_B64={encoded}

# Optional: YouTube Cookies File Path (for local development)
YOUTUBE_COOKIES_FILE=cookies/youtube_cookies.txt
"""
    
    env_file = Path(".env.example")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Cookies processed successfully!")
    print(f"   Base64 file: {b64_file}")
    print(f"   Environment example: {env_file}")
    print(f"   Base64 length: {len(encoded)} characters")
    
    return encoded

def test_cookies():
    """Test the cookies with a simple YouTube video"""
    
    print("\n🧪 Testing cookies...")
    
    cookies_file = Path("cookies/youtube_cookies.txt")
    if not cookies_file.exists():
        print("❌ No cookies file to test")
        return False
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    test_output = "test_video.mp4"
    
    cmd = [
        'yt-dlp',
        '--cookies', str(cookies_file),
        '--format', 'best[height<=480]',
        '--output', test_output,
        '--quiet',
        test_url
    ]
    
    print(f"Testing with: {test_url}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and Path(test_output).exists():
            file_size = Path(test_output).stat().st_size
            print(f"✅ Test successful! Downloaded {file_size} bytes")
            
            # Clean up
            Path(test_output).unlink()
            print("✅ Test file cleaned up")
            return True
        else:
            print("❌ Test failed")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main function"""
    print("🍪 YouTube Cookie Extractor (yt-dlp method)")
    print("=" * 50)
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "extract":
            extract_cookies_from_browser()
        elif command == "test":
            test_cookies()
        else:
            print("❌ Unknown command. Use: extract or test")
    else:
        # Default: extract cookies
        if extract_cookies_from_browser():
            print("\n🎉 Cookie extraction completed!")
            print("\n📋 Next steps:")
            print("1. Copy the YOUTUBE_COOKIES_B64 value from cookies/youtube_cookies_b64.txt")
            print("2. Add it to your Railway environment variables")
            print("3. Or create a .env file locally with the values from .env.example")
            print("4. Test your application")
            
            # Ask if user wants to test
            try:
                test_choice = input("\n🧪 Test the cookies now? (y/n): ").lower().strip()
                if test_choice in ['y', 'yes']:
                    test_cookies()
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 