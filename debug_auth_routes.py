#!/usr/bin/env python3
"""
Debug the authentication routing issue
"""

import requests

# Test different auth endpoints
BACKEND_URL = "https://fastapi-react-fix.preview.emergentagent.com"

endpoints_to_test = [
    "/api/auth/register",
    "/api/auth/login", 
    "/api/auth/me",
    "/api/register",
    "/api/login",
    "/api/me"
]

print("🔍 Testing auth endpoint availability...")

for endpoint in endpoints_to_test:
    url = f"{BACKEND_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ {endpoint}: {response.status_code}")
    except Exception as e:
        print(f"❌ {endpoint}: {e}")

# Test with POST for registration endpoints
print("\n🔍 Testing POST endpoints...")

registration_endpoints = [
    "/api/auth/register",
    "/api/register"
]

test_data = {
    "username": "test",
    "email": "test@test.com", 
    "first_name": "Test",
    "last_name": "User",
    "password": "testpass"
}

for endpoint in registration_endpoints:
    url = f"{BACKEND_URL}{endpoint}"
    try:
        response = requests.post(url, json=test_data, timeout=5)
        print(f"✅ POST {endpoint}: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"❌ POST {endpoint}: {e}")