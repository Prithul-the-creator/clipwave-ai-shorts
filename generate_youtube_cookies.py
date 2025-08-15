#!/usr/bin/env python3
"""
YouTube Cookies Generator for ClipWave AI Shorts

This script helps you generate fresh, properly formatted YouTube cookies
that work reliably with yt-dlp for video downloads.
"""

import os
import sys
import base64
import subprocess
from pathlib import Path

def check_yt_dlp():
    """Check if yt-dlp is installed"""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ yt-dlp found: {result.stdout.strip()}")
            return True
        else:
            print("❌ yt-dlp not found or not working")
            return False
    except FileNotFoundError:
        print("❌ yt-dlp not found. Please install it first:")
        print("   pip install --upgrade yt-dlp")
        return False

def generate_cookies():
    """Generate fresh YouTube cookies using yt-dlp"""
    print("\n🔄 Generating fresh YouTube cookies...")
    
    # Create cookies directory
    cookies_dir = Path("cookies")
    cookies_dir.mkdir(exist_ok=True)
    
    cookies_file = cookies_dir / "youtube_cookies.txt"
    
    # Try different methods to extract cookies
    methods = [
        # Method 1: Extract from Chrome
        ['yt-dlp', '--cookies-from-browser', 'chrome', '--cookies', str(cookies_file), '--print', 'cookies'],
        # Method 2: Extract from Firefox
        ['yt-dlp', '--cookies-from-browser', 'firefox', '--cookies', str(cookies_file), '--print', 'cookies'],
        # Method 3: Extract from Safari
        ['yt-dlp', '--cookies-from-browser', 'safari', '--cookies', str(cookies_file), '--print', 'cookies'],
    ]
    
    for i, cmd in enumerate(methods, 1):
        browser = cmd[2]
        print(f"Trying method {i}: Extract from {browser}...")
        
        try:
            # First, try to extract cookies to file
            extract_cmd = cmd[:-2]  # Remove --print cookies
            result = subprocess.run(extract_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and cookies_file.exists():
                # Check if file has content
                with open(cookies_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.strip():
                    print(f"✅ Cookies extracted from {browser}")
                    print(f"   File: {cookies_file}")
                    print(f"   Size: {len(content)} characters")
                    print(f"   Lines: {len(content.splitlines())}")
                    return cookies_file
                else:
                    print(f"⚠️  {browser} cookies file is empty")
            else:
                print(f"⚠️  {browser} extraction failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⚠️  {browser} extraction timed out")
        except Exception as e:
            print(f"⚠️  {browser} extraction error: {e}")
    
    print("❌ Could not extract cookies from any browser")
    return None

def validate_cookies(cookies_file):
    """Validate the generated cookies file"""
    print("\n🔍 Validating cookies format...")
    
    with open(cookies_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    valid_lines = []
    invalid_lines = []
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            valid_lines.append(line)
            continue
        
        # Check Netscape cookie format: domain, flag, path, secure, expiry, name, value
        parts = line.split('\t')
        if len(parts) == 7:
            # Additional validation
            if '\n' not in parts[6]:  # No newlines in value
                valid_lines.append(line)
            else:
                invalid_lines.append(f"Line {i}: Newline in cookie value")
        else:
            invalid_lines.append(f"Line {i}: Expected 7 fields, got {len(parts)}")
    
    print(f"✅ Valid lines: {len(valid_lines)}")
    if invalid_lines:
        print(f"❌ Invalid lines: {len(invalid_lines)}")
        for error in invalid_lines[:5]:  # Show first 5 errors
            print(f"   {error}")
        if len(invalid_lines) > 5:
            print(f"   ... and {len(invalid_lines) - 5} more")
    
    # Write cleaned cookies
    cleaned_file = cookies_file.parent / "youtube_cookies_cleaned.txt"
    with open(cleaned_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(valid_lines))
    
    print(f"✅ Cleaned cookies saved to: {cleaned_file}")
    return cleaned_file

def encode_cookies(cookies_file):
    """Encode cookies to base64 for environment variable"""
    print("\n🔐 Encoding cookies to base64...")
    
    with open(cookies_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encode to base64
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    print(f"✅ Base64 encoded cookies ({len(encoded)} characters)")
    
    # Save to file
    encoded_file = cookies_file.parent / "youtube_cookies_b64.txt"
    with open(encoded_file, 'w', encoding='utf-8') as f:
        f.write(encoded)
    
    print(f"✅ Base64 cookies saved to: {encoded_file}")
    
    # Show first and last 50 characters
    print(f"   Preview: {encoded[:50]}...{encoded[-50:]}")
    
    return encoded, encoded_file

def create_env_example(encoded_cookies):
    """Create .env.example with the cookies"""
    print("\n📝 Creating .env.example...")
    
    env_content = f"""# ClipWave AI Shorts Environment Variables

# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# YouTube Cookies (base64 encoded)
YOUTUBE_COOKIES_B64={encoded_cookies}

# Optional: YouTube Cookies File Path (for local development)
# YOUTUBE_COOKIES_FILE=cookies/youtube_cookies_cleaned.txt
"""
    
    env_file = Path(".env.example")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ Environment example created: {env_file}")
    return env_file

def test_cookies(cookies_file):
    """Test the cookies with a simple YouTube video"""
    print("\n🧪 Testing cookies with YouTube download...")
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short video
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
            
            # Clean up test file
            Path(test_output).unlink()
            print("✅ Test file cleaned up")
            return True
        else:
            print("❌ Test failed")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main function"""
    print("🍪 YouTube Cookies Generator for ClipWave AI Shorts")
    print("=" * 60)
    
    # Check prerequisites
    if not check_yt_dlp():
        sys.exit(1)
    
    # Generate cookies
    cookies_file = generate_cookies()
    if not cookies_file:
        print("\n❌ Failed to generate cookies")
        print("\n💡 Alternative: Manual cookie extraction")
        print("1. Open YouTube in your browser")
        print("2. Install a cookie export extension (like 'Cookie Editor')")
        print("3. Export cookies for youtube.com")
        print("4. Save as 'cookies/youtube_cookies.txt'")
        sys.exit(1)
    
    # Validate cookies
    cleaned_file = validate_cookies(cookies_file)
    
    # Encode cookies
    encoded_cookies, encoded_file = encode_cookies(cleaned_file)
    
    # Create environment example
    env_file = create_env_example(encoded_cookies)
    
    # Test cookies
    test_success = test_cookies(cleaned_file)
    
    print("\n" + "=" * 60)
    print("🎉 Cookie Generation Complete!")
    print("=" * 60)
    
    print(f"\n📁 Generated files:")
    print(f"   Original: {cookies_file}")
    print(f"   Cleaned: {cleaned_file}")
    print(f"   Base64: {encoded_file}")
    print(f"   Environment: {env_file}")
    
    print(f"\n🔧 Next steps:")
    print(f"1. Copy the YOUTUBE_COOKIES_B64 value from {encoded_file}")
    print(f"2. Add it to your Railway environment variables")
    print(f"3. Or create a .env file locally with the values from {env_file}")
    print(f"4. Test your application")
    
    if test_success:
        print(f"\n✅ Cookies tested successfully!")
    else:
        print(f"\n⚠️  Cookie test failed - you may need to:")
        print(f"   - Log into YouTube in your browser")
        print(f"   - Try a different browser")
        print(f"   - Manually export cookies")
    
    print(f"\n💡 Tips:")
    print(f"   - Keep your cookies updated (they expire)")
    print(f"   - Use incognito/private browsing for clean cookies")
    print(f"   - Test with different YouTube videos")

if __name__ == "__main__":
    main() 