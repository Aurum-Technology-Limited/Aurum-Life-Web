#!/usr/bin/env python3
"""
Quick test to verify the onboarding issue by checking both database tables
"""

import requests
import json

# Configuration
BACKEND_URL = "https://7b39a747-36d6-44f7-9408-a498365475ba.preview.emergentagent.com/api"
TEST_USER_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_USER_PASSWORD = "password"

def test_onboarding_issue():
    session = requests.Session()
    
    # Login
    login_data = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    login_response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing onboarding issue...")
    
    # Get initial status
    me_response = session.get(f"{BACKEND_URL}/auth/me", headers=headers)
    if me_response.status_code == 200:
        initial_status = me_response.json().get("has_completed_onboarding")
        print(f"Initial onboarding status: {initial_status}")
    
    # Complete onboarding
    complete_response = session.post(f"{BACKEND_URL}/auth/complete-onboarding", headers=headers)
    if complete_response.status_code == 200:
        complete_data = complete_response.json()
        print(f"Complete onboarding response: {complete_data.get('has_completed_onboarding')}")
    
    # Check status after completion
    me_response_after = session.get(f"{BACKEND_URL}/auth/me", headers=headers)
    if me_response_after.status_code == 200:
        final_status = me_response_after.json().get("has_completed_onboarding")
        print(f"Final onboarding status: {final_status}")
        
        if final_status is True:
            print("✅ Onboarding status correctly updated!")
        else:
            print("❌ Onboarding status NOT updated - this is the bug!")
    else:
        print(f"❌ Failed to get user data after onboarding: {me_response_after.status_code}")

if __name__ == "__main__":
    test_onboarding_issue()