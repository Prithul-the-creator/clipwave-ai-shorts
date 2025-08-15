#!/usr/bin/env python3
"""
Process existing YouTube cookies file
"""

import base64
from pathlib import Path

def process_cookies():
    """Process the existing cookies file and create base64 version"""
    
    cookies_file = Path("cookies/youtube_cookies.txt")
    
    if not cookies_file.exists():
        print("❌ cookies/youtube_cookies.txt not found")
        return None
    
    print("🔧 Processing existing cookies...")
    
    # Read cookies
    with open(cookies_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✅ Read {len(content)} characters from cookies file")
    print(f"   Lines: {len(content.splitlines())}")
    
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
    
    # Show first and last 50 characters
    print(f"   Preview: {encoded[:50]}...{encoded[-50:]}")
    
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
    
    import subprocess
    
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
    print("🍪 Process Existing YouTube Cookies")
    print("=" * 40)
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "process":
            process_cookies()
        elif command == "test":
            test_cookies()
        else:
            print("❌ Unknown command. Use: process or test")
    else:
        # Default: process cookies
        encoded = process_cookies()
        
        if encoded:
            print("\n🎉 Cookie processing completed!")
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