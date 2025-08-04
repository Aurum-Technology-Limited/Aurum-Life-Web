#!/usr/bin/env python3
"""
Quick validation test for empty strings
"""

import requests
import json

BACKEND_URL = "https://51a61c8b-3644-464b-a47b-b402cddf7d0a.preview.emergentagent.com/api"

def test_validation():
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
    
    # Test empty string validation
    test_cases = [
        {"username": "", "first_name": "Test", "last_name": "User"},
        {"username": "test", "first_name": "", "last_name": "User"},
        {"username": "test", "first_name": "Test", "last_name": ""},
        {"username": "   ", "first_name": "Test", "last_name": "User"},  # Whitespace only
    ]
    
    for i, test_data in enumerate(test_cases):
        response = requests.put(f"{BACKEND_URL}/auth/profile", json=test_data, headers=headers)
        print(f"Test {i+1}: {test_data} -> Status: {response.status_code}")
        if response.status_code != 422:
            print(f"  Response: {response.json()}")

if __name__ == "__main__":
    test_validation()