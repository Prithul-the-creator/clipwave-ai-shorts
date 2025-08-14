#!/usr/bin/env python3
"""
Deployment Preparation Script
This script helps prepare your cookies for secure deployment.
"""

import base64
import os
import sys

def encode_cookies_to_base64(cookies_file_path):
    """Encode cookies file to base64 string for environment variable"""
    try:
        with open(cookies_file_path, 'r') as f:
            cookies_content = f.read()
        
        # Encode to base64
        cookies_b64 = base64.b64encode(cookies_content.encode('utf-8')).decode('utf-8')
        
        print("✅ Cookies encoded successfully!")
        print(f"📁 Original file: {cookies_file_path}")
        print(f"📏 Base64 length: {len(cookies_b64)} characters")
        print("\n🔐 Add this to your server's environment variables:")
        print("=" * 60)
        print(f"YOUTUBE_COOKIES_B64={cookies_b64}")
        print("=" * 60)
        
        return cookies_b64
        
    except FileNotFoundError:
        print(f"❌ Error: Cookies file not found at {cookies_file_path}")
        return None
    except Exception as e:
        print(f"❌ Error encoding cookies: {e}")
        return None

def decode_cookies_from_base64(cookies_b64, output_file="cookies_decoded.txt"):
    """Decode base64 cookies back to file (for testing)"""
    try:
        cookies_content = base64.b64decode(cookies_b64).decode('utf-8')
        
        with open(output_file, 'w') as f:
            f.write(cookies_content)
        
        print(f"✅ Cookies decoded to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error decoding cookies: {e}")
        return False

def main():
    print("🍪 YouTube Cookies Deployment Preparation")
    print("=" * 50)
    
    # Check if cookies file exists
    cookies_file = "cookies.txt"
    if not os.path.exists(cookies_file):
        print(f"❌ Cookies file '{cookies_file}' not found!")
        print("Please run: yt-dlp --cookies-from-browser chrome --cookies cookies.txt")
        sys.exit(1)
    
    # Encode cookies
    cookies_b64 = encode_cookies_to_base64(cookies_file)
    
    if cookies_b64:
        print("\n📋 Next steps:")
        print("1. Copy the YOUTUBE_COOKIES_B64 value above")
        print("2. Add it to your server's environment variables")
        print("3. Update your video_processor.py to use the new method")
        print("4. Test the deployment")
        
        # Ask if user wants to test decoding
        response = input("\n🧪 Test decode cookies? (y/n): ").lower().strip()
        if response == 'y':
            decode_cookies_from_base64(cookies_b64)

if __name__ == "__main__":
    main() 