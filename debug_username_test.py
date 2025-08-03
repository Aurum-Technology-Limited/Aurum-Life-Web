#!/usr/bin/env python3
"""
Debug Username Change Test
"""

import requests
import json
import time

BACKEND_URL = "https://2ba83010-29ce-4f25-8827-92c31097d7b1.preview.emergentagent.com/api"

def test_username_change():
    # Login
    login_data = {
        "email": "marc.alleyne@aurumtechnologyltd.com",
        "password": "password"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    print(f"Login response: {response.status_code}")
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get current profile
    response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
    print(f"Profile response: {response.status_code}")
    if response.status_code == 200:
        profile = response.json()
        print(f"Current profile: {json.dumps(profile, indent=2)}")
    else:
        print(f"Profile failed: {response.text}")
        return
    
    # Try username change
    timestamp = int(time.time())
    new_username = f"testuser_{timestamp}"
    
    update_data = {"username": new_username}
    response = requests.put(f"{BACKEND_URL}/auth/profile", json=update_data, headers=headers)
    print(f"Username change response: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_username_change()