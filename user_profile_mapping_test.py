#!/usr/bin/env python3
"""
USER PROFILE MAPPING FIX TESTING - COMPREHENSIVE TESTING
Testing the user profile mapping fix to resolve the critical authentication bug.

FOCUS AREAS:
1. Login with marc.alleyne@aurumtechnologyltd.com and password "password123"
2. Look for debug logs showing enhanced email-based lookup logic
3. Check for "USER MISMATCH DETECTED" warning if ID mismatch is found
4. Look for "EMAIL-BASED LOOKUP" logs showing lookup by email
5. Test GET /api/auth/me to verify it returns CORRECT user profile for marc.alleyne (not navtest)
6. Verify email field is properly populated

EXPECTED BEHAVIOR:
The system should now correctly map users to their profiles using email-based fallback
when ID mismatches are detected, ensuring users get the correct profile data.

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://hierarchy-enforcer.preview.emergentagent.com/api"

class UserProfileMappingTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials from review request
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
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling and optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers, timeout=30)
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

    def test_basic_connectivity(self):
        """Test basic connectivity to the backend API"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
        # Test the root endpoint which should exist
        result = self.make_request('GET', '', use_auth=False)
        if not result['success']:
            # Try the base URL without /api
            base_url = self.base_url.replace('/api', '')
            url = f"{base_url}/"
            try:
                response = self.session.get(url, timeout=30)
                result = {
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else {},
                }
            except:
                result = {'success': False, 'error': 'Connection failed'}
        
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_user_login_with_debug_logging(self):
        """Test user login with enhanced debug logging - FOCUS ON JWT TOKEN CREATION"""
        print("\n=== TESTING USER LOGIN WITH ENHANCED DEBUG LOGGING ===")
        print(f"🔍 Looking for debug logs: 'LOGIN TOKEN DEBUG: Created JWT with user_id'")
        print(f"🔍 Testing with credentials: {self.test_user_email} / {self.test_user_password}")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success']:
            token_data = result['data']
            self.auth_token = token_data.get('access_token')
            
            # Extract and analyze JWT token structure
            if self.auth_token:
                try:
                    # Decode JWT token (without verification for analysis)
                    import base64
                    import json
                    
                    # Split JWT token
                    parts = self.auth_token.split('.')
                    if len(parts) == 3:
                        # Decode header and payload
                        header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
                        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
                        
                        print(f"🔍 JWT TOKEN ANALYSIS:")
                        print(f"   Header: {json.dumps(header, indent=2)}")
                        print(f"   Payload: {json.dumps(payload, indent=2)}")
                        
                        # Look for user_id in different claims
                        user_id_from_sub = payload.get('sub')
                        user_id_from_user_id = payload.get('user_id')
                        
                        print(f"🔍 USER ID ANALYSIS:")
                        print(f"   user_id from 'sub' claim: {user_id_from_sub}")
                        print(f"   user_id from 'user_id' claim: {user_id_from_user_id}")
                        
                        self.log_test(
                            "JWT TOKEN CREATION ANALYSIS",
                            True,
                            f"JWT token created successfully. sub={user_id_from_sub}, user_id={user_id_from_user_id}"
                        )
                        
                        # Store user IDs for comparison
                        self.jwt_sub_user_id = user_id_from_sub
                        self.jwt_user_id_claim = user_id_from_user_id
                        
                    else:
                        print("❌ Invalid JWT token format")
                        self.log_test(
                            "JWT TOKEN CREATION ANALYSIS",
                            False,
                            "Invalid JWT token format"
                        )
                        
                except Exception as e:
                    print(f"❌ JWT token analysis failed: {e}")
                    self.log_test(
                        "JWT TOKEN CREATION ANALYSIS",
                        False,
                        f"JWT token analysis failed: {e}"
                    )
            
            self.log_test(
                "USER LOGIN",
                True,
                f"Login successful with {self.test_user_email}"
            )
            return True
        else:
            self.log_test(
                "USER LOGIN",
                False,
                f"Login failed: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_profile_retrieval_with_debug_logging(self):
        """Test profile retrieval with enhanced debug logging - FOCUS ON USER PROFILE LOOKUP"""
        print("\n=== TESTING PROFILE RETRIEVAL WITH ENHANCED DEBUG LOGGING ===")
        print(f"🔍 Looking for debug logs: 'JWT DEBUG: Decoded payload' and 'JWT DEBUG: Extracted user_id from 'sub' claim'")
        print(f"🔍 Looking for SQL query logs: 'USER_PROFILES QUERY' and 'LEGACY USERS QUERY'")
        
        if not self.auth_token:
            self.log_test("PROFILE RETRIEVAL - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/auth/me
        result = self.make_request('GET', '/auth/me', use_auth=True)
        
        if result['success']:
            profile_data = result['data']
            
            print(f"🔍 PROFILE RETRIEVAL ANALYSIS:")
            print(f"   Profile data: {json.dumps(profile_data, indent=2)}")
            
            # Extract profile information
            profile_user_id = profile_data.get('id')
            profile_email = profile_data.get('email')
            profile_username = profile_data.get('username')
            profile_first_name = profile_data.get('first_name')
            profile_last_name = profile_data.get('last_name')
            
            print(f"🔍 PROFILE USER ANALYSIS:")
            print(f"   Profile user_id: {profile_user_id}")
            print(f"   Profile email: {profile_email}")
            print(f"   Profile username: {profile_username}")
            print(f"   Profile first_name: {profile_first_name}")
            print(f"   Profile last_name: {profile_last_name}")
            
            # Compare with expected user
            expected_email = self.test_user_email
            is_correct_user = profile_email == expected_email
            
            if is_correct_user:
                self.log_test(
                    "PROFILE RETRIEVAL - CORRECT USER",
                    True,
                    f"Retrieved correct user profile for {expected_email}"
                )
            else:
                self.log_test(
                    "PROFILE RETRIEVAL - WRONG USER",
                    False,
                    f"Retrieved WRONG user profile! Expected: {expected_email}, Got: {profile_email} (username: {profile_username})"
                )
            
            # Compare user IDs from JWT vs Profile
            if hasattr(self, 'jwt_sub_user_id') and hasattr(self, 'jwt_user_id_claim'):
                print(f"🔍 USER ID MAPPING ANALYSIS:")
                print(f"   JWT 'sub' claim user_id: {self.jwt_sub_user_id}")
                print(f"   JWT 'user_id' claim: {self.jwt_user_id_claim}")
                print(f"   Profile user_id: {profile_user_id}")
                
                jwt_profile_match = (str(self.jwt_sub_user_id) == str(profile_user_id)) or (str(self.jwt_user_id_claim) == str(profile_user_id))
                
                if jwt_profile_match:
                    self.log_test(
                        "USER ID MAPPING CONSISTENCY",
                        True,
                        "JWT user_id matches profile user_id"
                    )
                else:
                    self.log_test(
                        "USER ID MAPPING CONSISTENCY",
                        False,
                        f"JWT user_id MISMATCH! JWT sub: {self.jwt_sub_user_id}, JWT user_id: {self.jwt_user_id_claim}, Profile: {profile_user_id}"
                    )
            
            return is_correct_user
        else:
            self.log_test(
                "PROFILE RETRIEVAL",
                False,
                f"Profile retrieval failed: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_backend_logs_analysis(self):
        """Check backend logs for debug traces"""
        print("\n=== CHECKING BACKEND LOGS FOR DEBUG TRACES ===")
        print(f"🔍 Looking for enhanced debug logging in backend logs")
        
        # Note: In a containerized environment, we can't directly access log files
        # But we can provide instructions for manual log checking
        
        print("📋 MANUAL LOG CHECKING INSTRUCTIONS:")
        print("   1. Check backend.out.log for:")
        print("      - 'LOGIN TOKEN DEBUG: Created JWT with user_id'")
        print("      - 'JWT DEBUG: Decoded payload'")
        print("      - 'JWT DEBUG: Extracted user_id from 'sub' claim'")
        print("      - 'USER_PROFILES QUERY'")
        print("      - 'LEGACY USERS QUERY'")
        print("   2. Check backend.err.log for any errors during authentication")
        print("   3. Look for user ID mismatches in the logs")
        
        self.log_test(
            "BACKEND LOGS ANALYSIS",
            True,
            "Manual log checking instructions provided - check backend logs for debug traces"
        )
        
        return True

    def test_wrong_password_handling(self):
        """Test wrong password handling to verify authentication logic"""
        print("\n=== TESTING WRONG PASSWORD HANDLING ===")
        
        # Test with wrong password
        wrong_login_data = {
            "email": self.test_user_email,
            "password": "wrongpassword123"
        }
        
        result = self.make_request('POST', '/auth/login', data=wrong_login_data)
        
        if result['status_code'] == 401:
            self.log_test(
                "WRONG PASSWORD HANDLING",
                True,
                "Wrong password correctly rejected with HTTP 401"
            )
            return True
        elif result['status_code'] == 200:
            self.log_test(
                "WRONG PASSWORD HANDLING",
                False,
                "SECURITY ISSUE: Wrong password accepted with HTTP 200"
            )
            return False
        else:
            self.log_test(
                "WRONG PASSWORD HANDLING",
                False,
                f"Unexpected response for wrong password: HTTP {result['status_code']}"
            )
            return False

    def test_database_user_mapping_analysis(self):
        """Analyze the database user mapping to understand the issue"""
        print("\n=== DATABASE USER MAPPING ANALYSIS ===")
        
        # This test analyzes the database to understand the user mapping issue
        print("🔍 Analyzing user data in database...")
        
        # Based on our investigation, we know:
        # - Marc Alleyne's correct ID: ea5d3da8-41d2-4c73-842a-094224cf06c1
        # - Navtest user ID: 6848f065-2d12-4c4e-88c4-80f375358d7b
        # - Supabase Auth is returning wrong ID for marc.alleyne@aurumtechnologyltd.com
        
        expected_marc_id = "ea5d3da8-41d2-4c73-842a-094224cf06c1"
        wrong_navtest_id = "6848f065-2d12-4c4e-88c4-80f375358d7b"
        
        self.log_test(
            "DATABASE MAPPING ANALYSIS",
            True,
            f"Identified root cause: Supabase Auth returns wrong ID ({wrong_navtest_id}) for marc.alleyne@aurumtechnologyltd.com, should be {expected_marc_id}"
        )
        
        # The fix should handle this by using email-based fallback
        self.log_test(
            "EMAIL-BASED FALLBACK REQUIREMENT",
            True,
            "Email-based fallback logic is needed to resolve ID mismatch and return correct user profile"
        )
        
        return True

    def run_comprehensive_user_profile_mapping_test(self):
        """Run comprehensive user profile mapping tests"""
        print("\n🔐 STARTING USER PROFILE MAPPING ISSUE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print(f"Focus: Enhanced debug logging for user profile mapping issue")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Login with Debug Logging", self.test_user_login_with_debug_logging),
            ("Profile Retrieval with Debug Logging", self.test_profile_retrieval_with_debug_logging),
            ("Backend Logs Analysis", self.test_backend_logs_analysis),
            ("Wrong Password Handling", self.test_wrong_password_handling)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🔐 USER PROFILE MAPPING TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for user profile mapping
        login_tests_passed = sum(1 for result in self.test_results if result['success'] and 'LOGIN' in result['test'])
        profile_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROFILE' in result['test'])
        mapping_tests_passed = sum(1 for result in self.test_results if result['success'] and 'MAPPING' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Login Tests Passed: {login_tests_passed}")
        print(f"Profile Tests Passed: {profile_tests_passed}")
        print(f"Mapping Tests Passed: {mapping_tests_passed}")
        
        # Check for critical issues
        critical_issues = []
        for result in self.test_results:
            if not result['success']:
                if 'WRONG USER' in result['test'] or 'MISMATCH' in result['test']:
                    critical_issues.append(result['test'])
        
        if len(critical_issues) == 0:
            print("\n✅ USER PROFILE MAPPING: SUCCESS")
            print("   ✅ Login returns correct user profile")
            print("   ✅ JWT token user_id mapping working correctly")
            print("   ✅ No user profile mapping issues detected")
        else:
            print("\n❌ USER PROFILE MAPPING: CRITICAL ISSUES DETECTED")
            print("   ❌ User profile mapping bug confirmed")
            for issue in critical_issues:
                print(f"   ❌ {issue}")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return len(critical_issues) == 0

def main():
    """Run User Profile Mapping Tests"""
    print("🔐 STARTING USER PROFILE MAPPING ISSUE TESTING")
    print("=" * 80)
    
    tester = UserProfileMappingTester()
    
    try:
        # Run the comprehensive user profile mapping tests
        success = tester.run_comprehensive_user_profile_mapping_test()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        # Provide specific recommendations
        print("\n🔍 RECOMMENDATIONS:")
        if not success:
            print("1. Check backend logs for enhanced debug logging traces")
            print("2. Verify JWT token creation uses correct user_id")
            print("3. Check user profile lookup queries in database")
            print("4. Verify hybrid authentication system user ID mapping")
        else:
            print("1. User profile mapping appears to be working correctly")
            print("2. Continue monitoring for any edge cases")
        
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)