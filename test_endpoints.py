#!/usr/bin/env python3
"""
Test the API endpoints that were giving 404 errors
"""

import sys
import os
sys.path.append('backend')

from fastapi.testclient import TestClient
from main import app

def test_endpoints():
    """Test all the endpoints that were giving 404s"""
    client = TestClient(app)
    
    endpoints = [
        "/api/health",
        "/api/diagnose", 
        "/api/test-simple",
        "/api/test-download-strategies"
    ]
    
    print("🧪 Testing API Endpoints")
    print("=" * 40)
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 Testing {endpoint}...")
            response = client.get(endpoint, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - Working (200)")
                # Print first 200 chars of response for verification
                response_text = str(response.json())
                if len(response_text) > 200:
                    response_text = response_text[:200] + "..."
                print(f"   Response: {response_text}")
            else:
                print(f"❌ {endpoint} - Failed ({response.status_code})")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {endpoint} - Exception: {e}")
    
    print(f"\n🎯 All endpoints tested!")

if __name__ == "__main__":
    test_endpoints()