#!/usr/bin/env python3
"""
TARGETED ONBOARDING ENDPOINT TEST
=================================

Focused test specifically for the complete-onboarding endpoint fix.
Tests the exact requirements from the review request.
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://auth-flow-master.preview.emergentagent.com/api"

def test_onboarding_endpoint_fix():
    """Test the specific onboarding endpoint fix requirements"""
    
    print("🎯 TARGETED ONBOARDING ENDPOINT FIX TEST")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Started at: {datetime.utcnow().isoformat()}")
    print()
    
    # Step 1: Create a test account since original credentials are failing
    print("🔧 STEP 1: Creating test account for authentication...")
    
    test_user_data = {
        "username": f"onboarding_fix_test_{int(time.time())}",
        "email": f"onboarding_fix_test_{int(time.time())}@aurumtechnologyltd.com",
        "first_name": "Onboarding",
        "last_name": "Fix",
        "password": "OnboardingFix123!"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=test_user_data, timeout=30)
    
    if response.status_code == 200:
        print(f"✅ Test account created: {test_user_data['email']}")
    else:
        print(f"❌ Failed to create test account: {response.status_code} - {response.text}")
        return False
    
    # Step 2: Login to get access token
    print("\n🔐 STEP 2: Authenticating to get access token...")
    
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    
    start_time = time.time()
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=30)
    login_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        print(f"✅ Authentication successful ({login_time*1000:.1f}ms)")
        print(f"   Token received: {access_token[:20]}...")
    else:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return False
    
    # Step 3: Test complete-onboarding endpoint (MAIN TEST)
    print("\n🎯 STEP 3: Testing POST /api/auth/complete-onboarding endpoint...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    start_time = time.time()
    response = requests.post(f"{BACKEND_URL}/auth/complete-onboarding", headers=headers, timeout=30)
    onboarding_time = time.time() - start_time
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📊 Response Time: {onboarding_time*1000:.1f}ms")
    
    try:
        response_data = response.json()
        print(f"📊 Response Data: {json.dumps(response_data, indent=2)}")
    except:
        print(f"📊 Response Text: {response.text}")
        response_data = {}
    
    # CRITICAL VALIDATION: Should return 200 with {"success": true}
    if response.status_code == 200 and response_data.get("success") is True:
        print("✅ ONBOARDING ENDPOINT FIX SUCCESSFUL!")
        print("   ✓ Status: 200 OK (not 500)")
        print("   ✓ Response: {\"success\": true}")
        print("   ✓ No internal server errors")
        endpoint_working = True
    elif response.status_code == 500:
        print("❌ ONBOARDING ENDPOINT STILL FAILING!")
        print("   ✗ Status: 500 Internal Server Error")
        print("   ✗ Fix not working - still returning 500")
        endpoint_working = False
    else:
        print(f"⚠️ UNEXPECTED RESPONSE!")
        print(f"   ? Status: {response.status_code}")
        print(f"   ? Response: {response_data}")
        endpoint_working = False
    
    # Step 4: Verify no database connection errors
    print("\n🗄️ STEP 4: Checking for database connection errors...")
    
    # Check if we can still make authenticated requests
    start_time = time.time()
    health_response = requests.get(f"{BACKEND_URL}/health", timeout=30)
    health_time = time.time() - start_time
    
    if health_response.status_code == 200:
        health_data = health_response.json()
        print(f"✅ Backend health check passed ({health_time*1000:.1f}ms)")
        print(f"   Status: {health_data.get('status', 'unknown')}")
        db_connection_ok = True
    else:
        print(f"❌ Backend health check failed: {health_response.status_code}")
        db_connection_ok = False
    
    # Final Assessment
    print("\n" + "=" * 60)
    print("🏁 ONBOARDING ENDPOINT FIX TEST RESULTS")
    print("=" * 60)
    
    print(f"✅ Authentication Flow: {'WORKING' if access_token else 'FAILED'}")
    print(f"{'✅' if endpoint_working else '❌'} Complete Onboarding Endpoint: {'WORKING (200 + success:true)' if endpoint_working else 'FAILING'}")
    print(f"✅ Database Connection: {'WORKING' if db_connection_ok else 'FAILED'}")
    
    if endpoint_working:
        print("\n🎉 CONCLUSION: ONBOARDING ENDPOINT FIX IS SUCCESSFUL!")
        print("   The endpoint now returns 200 with {\"success\": true} instead of 500 error")
        print("   Smart onboarding feature should now work without internal server errors")
    else:
        print("\n🚨 CONCLUSION: ONBOARDING ENDPOINT FIX NEEDS MORE WORK!")
        print("   The endpoint is still returning errors instead of 200 + success:true")
    
    print(f"\nTest completed at: {datetime.utcnow().isoformat()}")
    
    return endpoint_working


if __name__ == "__main__":
    success = test_onboarding_endpoint_fix()
    exit(0 if success else 1)