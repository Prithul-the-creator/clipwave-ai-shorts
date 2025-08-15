#!/usr/bin/env python3
"""
Create compact YouTube cookies for Railway deployment
Railway has a 32KB limit for environment variables
"""

import base64
from pathlib import Path

def create_compact_cookies():
    """Create a compact cookies file with only essential YouTube cookies"""
    
    # Read the full cookies file
    full_cookies_file = Path("cookies/youtube_cookies.txt")
    if not full_cookies_file.exists():
        print("❌ cookies/youtube_cookies.txt not found")
        return None
    
    print("🔧 Creating compact cookies file...")
    
    # Essential YouTube cookies (these are the most important ones)
    essential_cookies = [
        'VISITOR_INFO1_LIVE',
        'LOGIN_INFO',
        'SID',
        'HSID',
        'SSID',
        'APISID',
        'SAPISID',
        'PREF',
        'YSC',
        'SIDCC',
        'SSIDCC',
        'HSIDCC',
        'APISIDCC',
        'SAPISIDCC',
        '__Secure-1PSID',
        '__Secure-3PSID',
        '__Secure-1PAPISID',
        '__Secure-3PAPISID',
        '__Secure-1PSIDCC',
        '__Secure-3PSIDCC',
        '__Secure-1HSID',
        '__Secure-3HSID',
        '__Secure-1SSID',
        '__Secure-3SSID',
        '__Secure-1APISID',
        '__Secure-3APISID',
        '__Secure-1SAPISID',
        '__Secure-3SAPISID',
    ]
    
    compact_lines = []
    found_cookies = set()
    
    with open(full_cookies_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Keep header lines
    for line in lines:
        if line.startswith('#') or line.strip() == '':
            compact_lines.append(line)
            continue
        
        # Parse cookie line
        parts = line.strip().split('\t')
        if len(parts) >= 6:
            cookie_name = parts[5]
            
            # Keep essential cookies
            if cookie_name in essential_cookies:
                compact_lines.append(line)
                found_cookies.add(cookie_name)
                print(f"✅ Added: {cookie_name}")
    
    # Create compact cookies file
    compact_file = Path("cookies/youtube_cookies_compact.txt")
    with open(compact_file, 'w', encoding='utf-8') as f:
        f.writelines(compact_lines)
    
    print(f"\n✅ Compact cookies file created: {compact_file}")
    print(f"   Original size: {len(lines)} lines")
    print(f"   Compact size: {len(compact_lines)} lines")
    print(f"   Essential cookies found: {len(found_cookies)}")
    print(f"   Missing cookies: {set(essential_cookies) - found_cookies}")
    
    return compact_file

def process_compact_cookies():
    """Process the compact cookies and check if it fits Railway's limit"""
    
    compact_file = Path("cookies/youtube_cookies_compact.txt")
    if not compact_file.exists():
        print("❌ Compact cookies file not found")
        return None
    
    print("\n🔧 Processing compact cookies...")
    
    # Read compact cookies
    with open(compact_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encode to base64
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    print(f"✅ Compact cookies processed")
    print(f"   Original size: {len(content)} characters")
    print(f"   Base64 size: {len(encoded)} characters")
    print(f"   Railway limit: 32768 characters")
    
    if len(encoded) <= 32768:
        print(f"✅ FITS within Railway limit! ({len(encoded)} <= 32768)")
        
        # Save base64 version
        b64_file = compact_file.parent / "youtube_cookies_compact_b64.txt"
        with open(b64_file, 'w', encoding='utf-8') as f:
            f.write(encoded)
        
        # Create environment example
        env_content = f"""# ClipWave AI Shorts Environment Variables

# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# YouTube Cookies (base64 encoded) - COMPACT VERSION
YOUTUBE_COOKIES_B64={encoded}

# Optional: YouTube Cookies File Path (for local development)
YOUTUBE_COOKIES_FILE=cookies/youtube_cookies_compact.txt
"""
        
        env_file = Path(".env.example")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Files created:")
        print(f"   Base64 file: {b64_file}")
        print(f"   Environment example: {env_file}")
        
        return encoded
    else:
        print(f"❌ STILL TOO LARGE for Railway! ({len(encoded)} > 32768)")
        print(f"   Need to reduce by {len(encoded) - 32768} characters")
        
        # Try with even fewer cookies
        return create_minimal_cookies()

def create_minimal_cookies():
    """Create minimal cookies with only the most essential ones"""
    
    print("\n🔧 Creating minimal cookies...")
    
    # Only the most essential cookies
    minimal_cookies = [
        'VISITOR_INFO1_LIVE',
        'LOGIN_INFO',
        'SID',
        'HSID',
        'SSID',
        'APISID',
        'SAPISID',
        'PREF',
    ]
    
    full_cookies_file = Path("cookies/youtube_cookies.txt")
    minimal_lines = []
    found_cookies = set()
    
    with open(full_cookies_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Keep header lines
    for line in lines:
        if line.startswith('#') or line.strip() == '':
            minimal_lines.append(line)
            continue
        
        # Parse cookie line
        parts = line.strip().split('\t')
        if len(parts) >= 6:
            cookie_name = parts[5]
            
            # Keep only minimal cookies
            if cookie_name in minimal_cookies:
                minimal_lines.append(line)
                found_cookies.add(cookie_name)
                print(f"✅ Added: {cookie_name}")
    
    # Create minimal cookies file
    minimal_file = Path("cookies/youtube_cookies_minimal.txt")
    with open(minimal_file, 'w', encoding='utf-8') as f:
        f.writelines(minimal_lines)
    
    print(f"\n✅ Minimal cookies file created: {minimal_file}")
    print(f"   Size: {len(minimal_lines)} lines")
    print(f"   Essential cookies found: {len(found_cookies)}")
    
    # Process minimal cookies
    with open(minimal_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    print(f"   Original size: {len(content)} characters")
    print(f"   Base64 size: {len(encoded)} characters")
    
    if len(encoded) <= 32768:
        print(f"✅ FITS within Railway limit! ({len(encoded)} <= 32768)")
        
        # Save base64 version
        b64_file = minimal_file.parent / "youtube_cookies_minimal_b64.txt"
        with open(b64_file, 'w', encoding='utf-8') as f:
            f.write(encoded)
        
        # Create environment example
        env_content = f"""# ClipWave AI Shorts Environment Variables

# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# YouTube Cookies (base64 encoded) - MINIMAL VERSION
YOUTUBE_COOKIES_B64={encoded}

# Optional: YouTube Cookies File Path (for local development)
YOUTUBE_COOKIES_FILE=cookies/youtube_cookies_minimal.txt
"""
        
        env_file = Path(".env.example")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Files created:")
        print(f"   Base64 file: {b64_file}")
        print(f"   Environment example: {env_file}")
        
        return encoded
    else:
        print(f"❌ STILL TOO LARGE! Need alternative approach")
        return None

def test_compact_cookies():
    """Test the compact cookies"""
    
    print("\n🧪 Testing compact cookies...")
    
    # Try compact first, then minimal
    test_files = [
        "cookies/youtube_cookies_compact.txt",
        "cookies/youtube_cookies_minimal.txt"
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"Testing: {test_file}")
            
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            test_output = "test_video.mp4"
            
            import subprocess
            
            cmd = [
                'yt-dlp',
                '--cookies', test_file,
                '--format', 'best[height<=480]',
                '--output', test_output,
                '--quiet',
                test_url
            ]
            
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
            except Exception as e:
                print(f"❌ Test error: {e}")
    
    return False

def main():
    """Main function"""
    print("🍪 Create Compact YouTube Cookies for Railway")
    print("=" * 50)
    
    # Create compact cookies
    compact_file = create_compact_cookies()
    if not compact_file:
        return
    
    # Process compact cookies
    encoded = process_compact_cookies()
    if not encoded:
        print("\n❌ Could not create cookies small enough for Railway")
        print("\n💡 Alternative solutions:")
        print("1. Use the comprehensive 403 error handling (no cookies needed)")
        print("2. Store cookies in a separate service (like Supabase)")
        print("3. Use Railway's file system (temporary solution)")
        return
    
    print("\n🎉 Compact cookies created successfully!")
    print("\n📋 Next steps:")
    print("1. Copy the YOUTUBE_COOKIES_B64 value from the generated file")
    print("2. Add it to your Railway environment variables")
    print("3. Test your application")
    
    # Ask if user wants to test
    try:
        test_choice = input("\n🧪 Test the compact cookies now? (y/n): ").lower().strip()
        if test_choice in ['y', 'yes']:
            test_compact_cookies()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 