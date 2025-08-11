#!/usr/bin/env python3
"""
Test successful profile update with valid data
"""

import requests
import json

BACKEND_URL = "https://15d7219c-892b-4111-8d96-e95547e179d6.preview.emergentagent.com/api"

def test_success():
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
    
    # Test successful update with same username (should not trigger rate limiting)
    test_data = {
        "username": "marcalleyne",  # Same username
        "first_name": "Marc",
        "last_name": "Alleyne"
    }
    
    response = requests.put(f"{BACKEND_URL}/auth/profile", json=test_data, headers=headers)
    print(f"Update with same username: Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_success()