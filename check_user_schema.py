#!/usr/bin/env python3
"""
Check User Schema
"""

import requests
import json

BACKEND_URL = "https://15d7219c-892b-4111-8d96-e95547e179d6.preview.emergentagent.com/api"

def check_schema():
    # Login
    login_data = {
        "email": "marc.alleyne@aurumtechnologyltd.com",
        "password": "password"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Try to update with a simple field to see what fields are available
    update_data = {"first_name": "Marc"}
    response = requests.put(f"{BACKEND_URL}/auth/profile", json=update_data, headers=headers)
    print(f"Simple update response: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    check_schema()