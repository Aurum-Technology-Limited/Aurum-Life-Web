#!/usr/bin/env python3
"""
FOCUSED BACKEND SMOKE TEST - ALIGNMENT ROUTES
Re-run backend smoke tests focused on the new alignment routes as requested in review.

SPECIFIC TESTING REQUIREMENTS:
1) GET /api/alignment/dashboard → expect 200 JSON with keys: rolling_weekly_score, monthly_score, monthly_goal, progress_percentage, has_goal_set
2) GET /api/alignment-score → expect same 200 and shape

Return pass/fail and the JSON snippet for each.

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://c7dc63d9-3764-48cb-a7be-e97dc0b89cd2.preview.emergentagent.com/api"

class AlignmentRoutesBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data:
            print(f"   JSON Response: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling and optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = (time.time() - start_time) * 1000
            
            # Try to parse JSON response
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response_time_ms': round(response_time, 1),
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
                'response_time_ms': 0
            }

    def test_user_authentication(self):
        """Test user authentication with specified credentials"""
        print("\n=== TESTING USER AUTHENTICATION ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success'] and 'access_token' in result['data']:
            self.auth_token = result['data']['access_token']
            self.log_test(
                "USER AUTHENTICATION",
                True,
                f"Successfully authenticated user {self.test_user_email} ({result['response_time_ms']}ms)"
            )
            return True
        else:
            self.log_test(
                "USER AUTHENTICATION",
                False,
                f"Failed to authenticate user {self.test_user_email}",
                result
            )
            return False

    def test_alignment_dashboard_endpoint(self):
        """Test GET /api/alignment/dashboard endpoint - REQUIREMENT 1"""
        print("\n=== TESTING GET /api/alignment/dashboard ===")
        
        result = self.make_request('GET', '/alignment/dashboard', use_auth=True)
        
        if result['success']:
            data = result['data']
            required_fields = ['rolling_weekly_score', 'monthly_score', 'monthly_goal', 'progress_percentage', 'has_goal_set']
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test(
                    "GET /api/alignment/dashboard",
                    False,
                    f"Missing required fields: {missing_fields} ({result['response_time_ms']}ms)",
                    data
                )
                return False, data
            
            self.log_test(
                "GET /api/alignment/dashboard",
                True,
                f"200 OK with all required keys ({result['response_time_ms']}ms)",
                data
            )
            return True, data
        else:
            self.log_test(
                "GET /api/alignment/dashboard",
                False,
                f"HTTP {result['status_code']} - Failed to retrieve dashboard data ({result['response_time_ms']}ms)",
                result.get('data', {})
            )
            return False, result.get('data', {})

    def test_alignment_score_legacy_endpoint(self):
        """Test GET /api/alignment-score endpoint - REQUIREMENT 2"""
        print("\n=== TESTING GET /api/alignment-score ===")
        
        result = self.make_request('GET', '/alignment-score', use_auth=True)
        
        if result['success']:
            data = result['data']
            required_fields = ['rolling_weekly_score', 'monthly_score', 'monthly_goal', 'progress_percentage', 'has_goal_set']
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test(
                    "GET /api/alignment-score",
                    False,
                    f"Missing required fields: {missing_fields} ({result['response_time_ms']}ms)",
                    data
                )
                return False, data
            
            self.log_test(
                "GET /api/alignment-score",
                True,
                f"200 OK with all required keys ({result['response_time_ms']}ms)",
                data
            )
            return True, data
        else:
            self.log_test(
                "GET /api/alignment-score",
                False,
                f"HTTP {result['status_code']} - Failed to retrieve alignment score data ({result['response_time_ms']}ms)",
                result.get('data', {})
            )
            return False, result.get('data', {})

    def run_focused_alignment_tests(self):
        """Run focused alignment routes backend tests as requested in review"""
        print("🎯 FOCUSED BACKEND SMOKE TEST - ALIGNMENT ROUTES")
        print("=" * 60)
        print("Testing the new alignment routes with valid Bearer token for test user")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 60)
        
        # Test authentication first
        if not self.test_user_authentication():
            print("❌ Cannot proceed - Authentication failed")
            return False
        
        print(f"\n✅ Authentication successful - Bearer token obtained")
        
        # Test both alignment endpoints as requested
        dashboard_pass, dashboard_data = self.test_alignment_dashboard_endpoint()
        score_pass, score_data = self.test_alignment_score_legacy_endpoint()
        
        # Summary as requested in review
        print("\n" + "=" * 60)
        print("🎯 FOCUSED ALIGNMENT ROUTES TEST RESULTS")
        print("=" * 60)
        
        print("\n1) GET /api/alignment/dashboard:")
        if dashboard_pass:
            print("   ✅ PASS - 200 JSON with required keys")
            print(f"   JSON snippet: {json.dumps(dashboard_data, indent=4, default=str)}")
        else:
            print("   ❌ FAIL - Did not return 200 with required keys")
            print(f"   JSON snippet: {json.dumps(dashboard_data, indent=4, default=str)}")
        
        print("\n2) GET /api/alignment-score:")
        if score_pass:
            print("   ✅ PASS - 200 JSON with required keys")
            print(f"   JSON snippet: {json.dumps(score_data, indent=4, default=str)}")
        else:
            print("   ❌ FAIL - Did not return 200 with required keys")
            print(f"   JSON snippet: {json.dumps(score_data, indent=4, default=str)}")
        
        # Overall result
        overall_success = dashboard_pass and score_pass
        print(f"\n📊 OVERALL RESULT: {'✅ PASS' if overall_success else '❌ FAIL'}")
        print(f"Tests Passed: {sum([dashboard_pass, score_pass])}/2")
        
        if overall_success:
            print("🎉 Both alignment routes are working correctly with valid Bearer token!")
        else:
            print("⚠️  One or more alignment routes failed - requires attention")
        
        return overall_success

if __name__ == "__main__":
    tester = AlignmentRoutesBackendTester()
    success = tester.run_focused_alignment_tests()
    sys.exit(0 if success else 1)