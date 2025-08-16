#!/usr/bin/env python3
"""
ALIGNMENT DASHBOARD BACKEND SMOKE TEST
Testing GET /api/alignment/dashboard after authentication as requested in review.

FOCUS:
1. Login and capture token
2. GET /api/alignment/dashboard with Bearer token
3. Expect 200 and JSON with keys: rolling_weekly_score, monthly_score, monthly_goal, progress_percentage, has_goal_set
4. Return concise pass/fail + sample payload

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://focus-planner-3.preview.emergentagent.com/api"

class AlignmentDashboardTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling and optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Try to parse JSON response
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response': response,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg += f" - Response: {error_data}"
                except:
                    error_msg += f" - Response: {e.response.text[:200]}"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'data': {},
                'response': getattr(e, 'response', None)
            }

    def test_login_and_capture_token(self):
        """Step 1: Login and capture token"""
        print("🔐 Step 1: Login and capture token")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success']:
            token_data = result['data']
            self.auth_token = token_data.get('access_token')
            
            if self.auth_token:
                print(f"✅ Login successful - Token captured")
                print(f"   User: {self.test_user_email}")
                print(f"   Token: {self.auth_token[:20]}...")
                return True
            else:
                print(f"❌ Login successful but no access_token in response")
                print(f"   Response keys: {list(token_data.keys())}")
                return False
        else:
            print(f"❌ Login failed: {result.get('error', 'Unknown error')}")
            return False

    def test_alignment_dashboard_endpoint(self):
        """Step 2: GET /api/alignment/dashboard with Bearer token"""
        print("\n📊 Step 2: GET /api/alignment/dashboard with Bearer token")
        
        if not self.auth_token:
            print("❌ No authentication token available")
            return False, None
        
        result = self.make_request('GET', '/alignment/dashboard', use_auth=True)
        
        if result['success']:
            data = result['data']
            print(f"✅ Alignment dashboard request successful (HTTP {result['status_code']})")
            
            # Step 3: Verify expected JSON keys
            expected_keys = [
                'rolling_weekly_score',
                'monthly_score', 
                'monthly_goal',
                'progress_percentage',
                'has_goal_set'
            ]
            
            missing_keys = []
            present_keys = []
            
            for key in expected_keys:
                if key in data:
                    present_keys.append(key)
                else:
                    missing_keys.append(key)
            
            print(f"\n🔍 Step 3: Verify expected JSON keys")
            print(f"   Expected keys: {expected_keys}")
            print(f"   Present keys: {present_keys}")
            
            if missing_keys:
                print(f"   ❌ Missing keys: {missing_keys}")
                return False, data
            else:
                print(f"   ✅ All expected keys present")
                return True, data
                
        else:
            print(f"❌ Alignment dashboard request failed: {result.get('error', 'Unknown error')}")
            print(f"   Status code: {result.get('status_code', 'Unknown')}")
            return False, None

    def run_alignment_dashboard_smoke_test(self):
        """Run the complete alignment dashboard smoke test"""
        print("🚀 ALIGNMENT DASHBOARD BACKEND SMOKE TEST")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 60)
        
        # Step 1: Login and capture token
        login_success = self.test_login_and_capture_token()
        
        if not login_success:
            print("\n❌ SMOKE TEST FAILED - Authentication failed")
            return False, None
        
        # Step 2 & 3: GET alignment dashboard and verify keys
        dashboard_success, sample_payload = self.test_alignment_dashboard_endpoint()
        
        # Final results
        print("\n" + "=" * 60)
        print("📋 SMOKE TEST RESULTS")
        print("=" * 60)
        
        if dashboard_success:
            print("✅ PASS - Alignment Dashboard Smoke Test")
            print("   ✅ Login successful and token captured")
            print("   ✅ GET /api/alignment/dashboard returned HTTP 200")
            print("   ✅ All expected JSON keys present:")
            print("      - rolling_weekly_score")
            print("      - monthly_score")
            print("      - monthly_goal") 
            print("      - progress_percentage")
            print("      - has_goal_set")
            
            print(f"\n📄 SAMPLE PAYLOAD:")
            print(json.dumps(sample_payload, indent=2, default=str))
            
        else:
            print("❌ FAIL - Alignment Dashboard Smoke Test")
            if login_success:
                print("   ✅ Login successful")
                print("   ❌ Alignment dashboard endpoint failed")
            else:
                print("   ❌ Login failed")
            
            if sample_payload:
                print(f"\n📄 RECEIVED PAYLOAD:")
                print(json.dumps(sample_payload, indent=2, default=str))
        
        print("=" * 60)
        return dashboard_success, sample_payload

def main():
    """Run Alignment Dashboard Smoke Test"""
    tester = AlignmentDashboardTester()
    
    try:
        success, payload = tester.run_alignment_dashboard_smoke_test()
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)