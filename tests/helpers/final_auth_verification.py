#!/usr/bin/env python3
"""
Final Authentication Verification Test
Test complete authentication flow with correct credentials
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://supa-data-explained.preview.emergentagent.com/api"
CORRECT_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
CORRECT_PASSWORD = "Test$1920"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def test_complete_authentication_flow():
    """Test the complete authentication flow with correct credentials"""
    log_test("🎯 TESTING COMPLETE AUTHENTICATION FLOW WITH CORRECT CREDENTIALS")
    
    # Step 1: Login
    log_test("🔍 Step 1: Login with correct credentials")
    login_payload = {
        "email": CORRECT_EMAIL,
        "password": CORRECT_PASSWORD
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        end_time = time.time()
        
        log_test(f"Login: {response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
        
        if response.status_code != 200:
            log_test(f"❌ Login failed: {response.text}")
            return False
        
        data = response.json()
        token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        
        log_test(f"✅ Login successful!")
        log_test(f"Access token length: {len(token)}")
        log_test(f"Refresh token: {'Present' if refresh_token else 'Not present'}")
        
        # Step 2: Test /auth/me
        log_test("🔍 Step 2: Test /auth/me")
        headers = {"Authorization": f"Bearer {token}"}
        
        start_time = time.time()
        me_response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=headers,
            timeout=30
        )
        end_time = time.time()
        
        log_test(f"/auth/me: {me_response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            log_test(f"✅ User profile: {me_data.get('email')} - {me_data.get('first_name')} {me_data.get('last_name')}")
            log_test(f"User ID: {me_data.get('id')}")
            log_test(f"Onboarding completed: {me_data.get('has_completed_onboarding')}")
        else:
            log_test(f"❌ /auth/me failed: {me_response.text}")
            return False
        
        # Step 3: Test key protected endpoints
        log_test("🔍 Step 3: Test key protected endpoints")
        
        key_endpoints = [
            "/pillars",
            "/areas", 
            "/projects",
            "/tasks",
            "/journal"
        ]
        
        endpoint_results = {}
        
        for endpoint in key_endpoints:
            try:
                start_time = time.time()
                endpoint_response = requests.get(
                    f"{BACKEND_URL}{endpoint}",
                    headers=headers,
                    timeout=30
                )
                end_time = time.time()
                
                log_test(f"{endpoint}: {endpoint_response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
                endpoint_results[endpoint] = endpoint_response.status_code == 200
                
                if endpoint_response.status_code == 200:
                    data = endpoint_response.json()
                    if isinstance(data, list):
                        log_test(f"  ✅ Returned {len(data)} items")
                    else:
                        log_test(f"  ✅ Returned data structure")
                else:
                    log_test(f"  ❌ Failed: {endpoint_response.text}")
                
            except Exception as e:
                log_test(f"  ❌ {endpoint} request failed: {e}")
                endpoint_results[endpoint] = False
        
        # Summary
        log_test("\n" + "="*60)
        log_test("🎯 FINAL AUTHENTICATION VERIFICATION SUMMARY")
        log_test("="*60)
        
        working_endpoints = sum(1 for result in endpoint_results.values() if result)
        total_endpoints = len(endpoint_results)
        
        log_test(f"✅ Login: WORKING with {CORRECT_EMAIL}")
        log_test(f"✅ User Profile: WORKING")
        log_test(f"✅ Protected Endpoints: {working_endpoints}/{total_endpoints} working")
        
        for endpoint, result in endpoint_results.items():
            status = "✅" if result else "❌"
            log_test(f"  {status} {endpoint}")
        
        if working_endpoints == total_endpoints:
            log_test("\n🎉 AUTHENTICATION SYSTEM FULLY FUNCTIONAL!")
            log_test(f"✅ Correct credentials: {CORRECT_EMAIL} / {CORRECT_PASSWORD}")
            log_test("✅ All protected endpoints accessible")
            log_test("✅ User profile data available")
            log_test("\n📋 SOLUTION FOR USER:")
            log_test(f"Use password: {CORRECT_PASSWORD} (not password123)")
        
        return True
        
    except Exception as e:
        log_test(f"❌ Complete auth flow test failed: {e}")
        return False

def main():
    """Main test execution"""
    test_complete_authentication_flow()

if __name__ == "__main__":
    main()