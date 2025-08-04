#!/usr/bin/env python3
"""
Test successful profile update with valid data
"""

import requests
import json

BACKEND_URL = "https://51a61c8b-3644-464b-a47b-b402cddf7d0a.preview.emergentagent.com/api"

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