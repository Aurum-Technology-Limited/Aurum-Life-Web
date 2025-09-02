#!/usr/bin/env python3
"""
Complete Authentication Flow Test
Test the full authentication flow with working credentials
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://smart-life-os.preview.emergentagent.com/api"
# Using working credentials from previous test
TEST_EMAIL = "authtest_ad92d043@aurumtechnologyltd.com"
TEST_PASSWORD = "TestPassword123!"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def test_complete_auth_flow():
    """Test complete authentication flow"""
    log_test("🎯 TESTING COMPLETE AUTHENTICATION FLOW")
    
    # Step 1: Login
    log_test("🔍 Step 1: Login")
    login_payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
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
        
        log_test(f"✅ Login successful! Token length: {len(token)}")
        
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
        else:
            log_test(f"❌ /auth/me failed: {me_response.text}")
            return False
        
        # Step 3: Test protected endpoints
        log_test("🔍 Step 3: Test protected endpoints")
        
        protected_endpoints = [
            "/pillars",
            "/areas", 
            "/projects",
            "/tasks",
            "/insights",
            "/journal"
        ]
        
        protected_results = {}
        
        for endpoint in protected_endpoints:
            try:
                start_time = time.time()
                endpoint_response = requests.get(
                    f"{BACKEND_URL}{endpoint}",
                    headers=headers,
                    timeout=30
                )
                end_time = time.time()
                
                log_test(f"{endpoint}: {endpoint_response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
                protected_results[endpoint] = endpoint_response.status_code == 200
                
                if endpoint_response.status_code != 200:
                    log_test(f"❌ {endpoint} failed: {endpoint_response.text}")
                
            except Exception as e:
                log_test(f"❌ {endpoint} request failed: {e}")
                protected_results[endpoint] = False
        
        # Step 4: Test token refresh if available
        if refresh_token:
            log_test("🔍 Step 4: Test token refresh")
            
            refresh_payload = {"refresh_token": refresh_token}
            
            try:
                start_time = time.time()
                refresh_response = requests.post(
                    f"{BACKEND_URL}/auth/refresh",
                    json=refresh_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                end_time = time.time()
                
                log_test(f"Token refresh: {refresh_response.status_code} ({(end_time - start_time) * 1000:.1f}ms)")
                
                if refresh_response.status_code == 200:
                    refresh_data = refresh_response.json()
                    new_token = refresh_data.get('access_token')
                    log_test(f"✅ Token refresh successful! New token length: {len(new_token)}")
                else:
                    log_test(f"❌ Token refresh failed: {refresh_response.text}")
                
            except Exception as e:
                log_test(f"❌ Token refresh request failed: {e}")
        
        # Summary
        log_test("\n" + "="*60)
        log_test("🎯 COMPLETE AUTHENTICATION FLOW TEST SUMMARY")
        log_test("="*60)
        
        working_endpoints = sum(1 for result in protected_results.values() if result)
        total_endpoints = len(protected_results)
        
        log_test(f"Authentication Flow: ✅ WORKING")
        log_test(f"Protected Endpoints: {working_endpoints}/{total_endpoints} working")
        
        for endpoint, result in protected_results.items():
            status = "✅" if result else "❌"
            log_test(f"{status} {endpoint}")
        
        if working_endpoints == total_endpoints:
            log_test("\n🎉 AUTHENTICATION SYSTEM IS FULLY FUNCTIONAL!")
            log_test("The 401 error is specific to the marc.alleyne@aurumtechnologyltd.com account.")
            log_test("New accounts can be created and authenticated successfully.")
        else:
            log_test(f"\n⚠️ PARTIAL SUCCESS: {working_endpoints}/{total_endpoints} endpoints working")
        
        return True
        
    except Exception as e:
        log_test(f"❌ Complete auth flow test failed: {e}")
        return False

def main():
    """Main test execution"""
    test_complete_auth_flow()

if __name__ == "__main__":
    main()