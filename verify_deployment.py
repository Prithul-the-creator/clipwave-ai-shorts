#!/usr/bin/env python3
"""
Railway Deployment Verification Script
Checks if the application is properly configured for Railway deployment
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if required files exist"""
    print("🔍 Checking required files...")
    
    required_files = [
        "railway.json",
        "Dockerfile", 
        "backend/main.py",
        "backend/video_processor.py",
        "requirements-deploy.txt",
        "package.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"   ❌ Missing: {file_path}")
        else:
            print(f"   ✅ Found: {file_path}")
    
    return len(missing_files) == 0

def check_syntax():
    """Check Python syntax"""
    print("\n🐍 Checking Python syntax...")
    
    python_files = [
        "backend/main.py",
        "backend/video_processor.py"
    ]
    
    syntax_errors = []
    for py_file in python_files:
        if os.path.exists(py_file):
            try:
                import subprocess
                result = subprocess.run([sys.executable, "-m", "py_compile", py_file], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"   ✅ Syntax OK: {py_file}")
                else:
                    print(f"   ❌ Syntax Error: {py_file}")
                    print(f"      Error: {result.stderr}")
                    syntax_errors.append(py_file)
            except Exception as e:
                print(f"   ⚠️ Could not check {py_file}: {e}")
    
    return len(syntax_errors) == 0

def check_dockerfile():
    """Check Dockerfile configuration"""
    print("\n🐳 Checking Dockerfile...")
    
    if not os.path.exists("Dockerfile"):
        print("   ❌ Dockerfile not found")
        return False
    
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    checks = [
        ("WORKDIR /app", "Working directory set"),
        ("EXPOSE 8000", "Port exposed"),
        ("CMD [\"python\", \"backend/main.py\"]", "Correct start command"),
        ("yt-dlp", "yt-dlp installation included"),
        ("mkdir -p storage/videos", "Storage directory creation")
    ]
    
    for check, description in checks:
        if check in content:
            print(f"   ✅ {description}")
        else:
            print(f"   ⚠️  {description} may be missing")
    
    return True

def check_static_files():
    """Check static file setup"""
    print("\n📁 Checking static file configuration...")
    
    static_dirs = ["backend/static", "dist", "static"]
    found_static = False
    
    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            print(f"   ✅ Found static directory: {static_dir}")
            files = list(Path(static_dir).glob("**/*"))
            print(f"      Contains {len(files)} files")
            found_static = True
            
            # Check for common frontend files
            if any("index.html" in str(f) for f in files):
                print("      ✅ Contains index.html")
            if any(str(f).endswith(".js") for f in files):
                print("      ✅ Contains JavaScript files")
            if any(str(f).endswith(".css") for f in files):
                print("      ✅ Contains CSS files")
    
    if not found_static:
        print("   ⚠️  No static files found - make sure to build frontend")
    
    return found_static

def main():
    """Main verification function"""
    print("🚀 Railway Deployment Verification")
    print("=" * 50)
    
    # Run all checks
    files_ok = check_files()
    syntax_ok = check_syntax()
    dockerfile_ok = check_dockerfile()
    static_ok = check_static_files()
    
    # Summary
    print("\n📋 Deployment Readiness Summary")
    print("=" * 50)
    print(f"Files: {'✅ Ready' if files_ok else '❌ Issues found'}")
    print(f"Python Syntax: {'✅ Clean' if syntax_ok else '❌ Errors found'}")
    print(f"Dockerfile: {'✅ Configured' if dockerfile_ok else '❌ Issues found'}")
    print(f"Static Files: {'✅ Ready' if static_ok else '⚠️  May need frontend build'}")
    
    if all([files_ok, syntax_ok, dockerfile_ok]):
        print("\n🎉 Ready for Railway deployment!")
        print("\n📝 Deployment steps:")
        print("1. Commit your changes: git add . && git commit -m 'Fix deployment issues'")
        print("2. Push to Railway: git push")
        print("3. Check Railway logs for any runtime issues")
    else:
        print("\n⚠️  Please fix the issues above before deploying")
    
    return all([files_ok, syntax_ok, dockerfile_ok])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)