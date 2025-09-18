#!/usr/bin/env python3
"""
Debug Authentication Test
Quick test to debug the authentication header issue
"""

import requests
import json

base_url = "https://supa-data-explained.preview.emergentagent.com"

# Test 1: No auth header
print("Test 1: No Authorization Header")
response = requests.get(f"{base_url}/api/tasks", headers={'Content-Type': 'application/json'})
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")
print()

# Test 2: Login first
print("Test 2: Login to get token")
login_response = requests.post(
    f"{base_url}/api/auth/login",
    json={'email': 'test@aurumlife.com', 'password': 'password123'},
    headers={'Content-Type': 'application/json'}
)
print(f"Login Status: {login_response.status_code}")
if login_response.status_code == 200:
    token = login_response.json().get('access_token')
    print(f"Token received: {token[:20]}..." if token else "No token")
    
    # Test 3: With valid token
    print("\nTest 3: With valid Authorization Header")
    response = requests.get(
        f"{base_url}/api/tasks",
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response type: {type(response.json()) if response.status_code == 200 else 'Error'}")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"Tasks count: {len(data)}")
        else:
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
else:
    print(f"Login failed: {login_response.text}")