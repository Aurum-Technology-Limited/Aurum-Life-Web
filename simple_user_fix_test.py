#!/usr/bin/env python3
"""
SIMPLE USER CREATION FIX TEST
Test to verify if the user creation fix is working properly
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://d5525f43-5dcd-48e4-b22b-982ef0b3bb33.preview.emergentagent.com/api"

def test_user_creation_fix():
    """Test the user creation fix by attempting to create a pillar"""
    
    # Login first
    login_data = {
        "email": "marc.alleyne@aurumtechnologyltd.com",
        "password": "password"
    }
    
    session = requests.Session()
    
    # Login
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=30)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False
    
    token_data = response.json()
    auth_token = token_data.get('access_token')
    headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    print(f"✅ Login successful")
    
    # Try to create a pillar - this should trigger the user creation fix
    pillar_data = {
        "name": "Test Pillar for FK Fix",
        "description": "Testing the foreign key constraint fix",
        "icon": "🧪",
        "color": "#10B981",
        "time_allocation_percentage": 25.0
    }
    
    print(f"🧪 Attempting to create pillar...")
    response = session.post(f"{BACKEND_URL}/pillars", json=pillar_data, headers=headers, timeout=30)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("✅ Pillar creation successful - FK fix is working!")
        pillar = response.json()
        
        # Clean up - delete the test pillar
        pillar_id = pillar.get('id')
        if pillar_id:
            delete_response = session.delete(f"{BACKEND_URL}/pillars/{pillar_id}", headers=headers, timeout=30)
            print(f"🧹 Cleanup: {delete_response.status_code}")
        
        return True
    else:
        print(f"❌ Pillar creation failed: {response.status_code}")
        
        # Check if it's a foreign key constraint error
        if 'foreign key' in response.text.lower() or 'constraint' in response.text.lower():
            print("🚨 FOREIGN KEY CONSTRAINT ERROR - The fix is not working!")
        
        return False

if __name__ == "__main__":
    print("🧪 TESTING USER CREATION FIX")
    print("=" * 50)
    
    success = test_user_creation_fix()
    
    if success:
        print("\n✅ USER CREATION FIX IS WORKING")
    else:
        print("\n❌ USER CREATION FIX IS NOT WORKING")
    
    sys.exit(0 if success else 1)