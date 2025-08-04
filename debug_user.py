#!/usr/bin/env python3
"""
Debug current user data
"""

import requests
import json

BACKEND_URL = "https://1b0a62f2-f882-476f-afb6-6747b2b238a1.preview.emergentagent.com/api"

def debug_user():
    # Login first
    login_data = {
        "email": "marc.alleyne@aurumtechnologyltd.com",
        "password": "password"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get current user data
    response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
    print(f"Current user data: {response.json()}")

if __name__ == "__main__":
    debug_user()