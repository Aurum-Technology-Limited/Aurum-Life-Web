#!/usr/bin/env python3
"""
ONBOARDING PILLAR CREATION FIX TESTING
Testing the improved onboarding pillar creation fix with robust user existence check.

FOCUS AREAS:
1. Authentication with marc.alleyne@aurumtechnologyltd.com / password
2. Create a single pillar to test the fix
3. Check the logs to see if the user creation/upsert works properly
4. Verify that the foreign key constraint error is resolved

IMPROVEMENTS TESTED:
- Using upsert instead of insert to handle race conditions
- Checking for both user_profiles and legacy users table
- Using select('*') instead of select('id') for more complete validation
- Added better error handling and logging

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://2add7c3c-bc98-404b-af7c-7c73ee7f9c41.preview.emergentagent.com/api"

class OnboardingPillarCreationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        
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

    def test_user_authentication(self):
        """Test user authentication with specified credentials"""
        print("\n=== TESTING USER AUTHENTICATION ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_pillar_creation_with_user_upsert(self):
        """Test pillar creation to verify the user existence check fix"""
        print("\n=== TESTING PILLAR CREATION WITH USER UPSERT FIX ===")
        
        if not self.auth_token:
            self.log_test("PILLAR CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a test pillar to trigger the user existence check
        pillar_data = {
            "name": "Test Pillar - User Upsert Fix",
            "description": "Testing the improved user existence check with upsert functionality",
            "icon": "🧪",
            "color": "#3B82F6",
            "time_allocation_percentage": 25.0
        }
        
        print(f"Creating pillar with data: {json.dumps(pillar_data, indent=2)}")
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        
        if result['success']:
            pillar_response = result['data']
            self.log_test(
                "PILLAR CREATION WITH USER UPSERT",
                True,
                f"Pillar created successfully. ID: {pillar_response.get('id', 'Unknown')}, Name: {pillar_response.get('name', 'Unknown')}"
            )
            
            # Verify the pillar was created with correct data
            if (pillar_response.get('name') == pillar_data['name'] and 
                pillar_response.get('time_allocation_percentage') == pillar_data['time_allocation_percentage']):
                self.log_test(
                    "PILLAR DATA INTEGRITY",
                    True,
                    "Pillar created with correct data mapping and field values"
                )
            else:
                self.log_test(
                    "PILLAR DATA INTEGRITY",
                    False,
                    f"Pillar data mismatch. Expected: {pillar_data}, Got: {pillar_response}"
                )
            
            return pillar_response.get('id')
        else:
            error_details = result.get('error', 'Unknown error')
            status_code = result.get('status_code', 'Unknown')
            
            # Check for specific foreign key constraint errors
            if 'foreign key constraint' in str(error_details).lower():
                self.log_test(
                    "PILLAR CREATION WITH USER UPSERT",
                    False,
                    f"FOREIGN KEY CONSTRAINT ERROR DETECTED - User upsert fix may not be working properly. Status: {status_code}, Error: {error_details}"
                )
            elif 'user' in str(error_details).lower() and ('not found' in str(error_details).lower() or 'does not exist' in str(error_details).lower()):
                self.log_test(
                    "PILLAR CREATION WITH USER UPSERT",
                    False,
                    f"USER EXISTENCE ERROR DETECTED - User upsert fix may not be working properly. Status: {status_code}, Error: {error_details}"
                )
            else:
                self.log_test(
                    "PILLAR CREATION WITH USER UPSERT",
                    False,
                    f"Pillar creation failed with status {status_code}: {error_details}"
                )
            
            return False

    def test_pillar_retrieval(self, pillar_id):
        """Test pillar retrieval to verify the created pillar exists"""
        print("\n=== TESTING PILLAR RETRIEVAL ===")
        
        if not pillar_id:
            self.log_test("PILLAR RETRIEVAL", False, "No pillar ID provided - pillar creation may have failed")
            return False
        
        if not self.auth_token:
            self.log_test("PILLAR RETRIEVAL - Authentication Required", False, "No authentication token available")
            return False
        
        # Get all pillars to verify our created pillar exists
        result = self.make_request('GET', '/pillars', use_auth=True)
        
        if result['success']:
            pillars = result['data']
            created_pillar = None
            
            # Find our created pillar
            for pillar in pillars:
                if pillar.get('id') == pillar_id:
                    created_pillar = pillar
                    break
            
            if created_pillar:
                self.log_test(
                    "PILLAR RETRIEVAL",
                    True,
                    f"Created pillar found in retrieval. Name: {created_pillar.get('name')}, ID: {created_pillar.get('id')}"
                )
                
                # Verify pillar data integrity
                if created_pillar.get('name') == "Test Pillar - User Upsert Fix":
                    self.log_test(
                        "PILLAR PERSISTENCE VERIFICATION",
                        True,
                        "Pillar data persisted correctly in database"
                    )
                else:
                    self.log_test(
                        "PILLAR PERSISTENCE VERIFICATION",
                        False,
                        f"Pillar data may have been corrupted. Expected name: 'Test Pillar - User Upsert Fix', Got: {created_pillar.get('name')}"
                    )
                
                return True
            else:
                self.log_test(
                    "PILLAR RETRIEVAL",
                    False,
                    f"Created pillar with ID {pillar_id} not found in retrieval. Available pillars: {len(pillars)}"
                )
                return False
        else:
            self.log_test(
                "PILLAR RETRIEVAL",
                False,
                f"Failed to retrieve pillars: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_user_profile_verification(self):
        """Test user profile to verify user exists in system"""
        print("\n=== TESTING USER PROFILE VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test("USER PROFILE VERIFICATION", False, "No authentication token available")
            return False
        
        # Get user profile to verify user exists
        result = self.make_request('GET', '/auth/me', use_auth=True)
        
        if result['success']:
            user_data = result['data']
            self.log_test(
                "USER PROFILE VERIFICATION",
                True,
                f"User profile retrieved successfully. Email: {user_data.get('email')}, ID: {user_data.get('id', 'Unknown')}"
            )
            
            # Verify this is the correct user
            if user_data.get('email') == self.test_user_email:
                self.log_test(
                    "USER IDENTITY VERIFICATION",
                    True,
                    f"Correct user authenticated: {self.test_user_email}"
                )
            else:
                self.log_test(
                    "USER IDENTITY VERIFICATION",
                    False,
                    f"User identity mismatch. Expected: {self.test_user_email}, Got: {user_data.get('email')}"
                )
            
            return True
        else:
            self.log_test(
                "USER PROFILE VERIFICATION",
                False,
                f"Failed to retrieve user profile: {result.get('error', 'Unknown error')}"
            )
            return False

    def cleanup_test_pillar(self, pillar_id):
        """Clean up the test pillar"""
        print("\n=== CLEANING UP TEST PILLAR ===")
        
        if not pillar_id or not self.auth_token:
            print("Skipping cleanup - no pillar ID or auth token")
            return
        
        result = self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
        
        if result['success']:
            self.log_test(
                "TEST PILLAR CLEANUP",
                True,
                f"Test pillar {pillar_id} deleted successfully"
            )
        else:
            self.log_test(
                "TEST PILLAR CLEANUP",
                False,
                f"Failed to delete test pillar {pillar_id}: {result.get('error', 'Unknown error')}"
            )

    def run_comprehensive_onboarding_pillar_test(self):
        """Run comprehensive onboarding pillar creation test"""
        print("\n🧪 STARTING ONBOARDING PILLAR CREATION FIX TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Testing improved user existence check with upsert functionality")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("User Profile Verification", self.test_user_profile_verification),
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        pillar_id = None
        
        # Run initial tests
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
                    # If authentication fails, we can't continue
                    if test_name == "User Authentication":
                        print("❌ Cannot continue without authentication")
                        break
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        # Run pillar creation test if authentication succeeded
        if self.auth_token:
            print(f"\n--- Pillar Creation with User Upsert Fix ---")
            try:
                pillar_id = self.test_pillar_creation_with_user_upsert()
                if pillar_id:
                    successful_tests += 1
                    print(f"✅ Pillar Creation with User Upsert Fix completed successfully")
                    
                    # Test pillar retrieval
                    print(f"\n--- Pillar Retrieval Verification ---")
                    if self.test_pillar_retrieval(pillar_id):
                        successful_tests += 1
                        print(f"✅ Pillar Retrieval Verification completed successfully")
                    else:
                        print(f"❌ Pillar Retrieval Verification failed")
                    
                    total_tests += 2  # Add the two additional tests
                else:
                    print(f"❌ Pillar Creation with User Upsert Fix failed")
                    total_tests += 1  # Add only the pillar creation test
            except Exception as e:
                print(f"❌ Pillar Creation with User Upsert Fix raised exception: {e}")
                total_tests += 1
        
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n" + "=" * 80)
        print("🧪 ONBOARDING PILLAR CREATION FIX TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for the specific fix
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        pillar_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PILLAR' in result['test'])
        user_tests_passed = sum(1 for result in self.test_results if result['success'] and 'USER' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"User Verification Tests Passed: {user_tests_passed}")
        print(f"Pillar Creation Tests Passed: {pillar_tests_passed}")
        
        # Check for specific errors that indicate the fix is working
        foreign_key_errors = sum(1 for result in self.test_results if not result['success'] and 'foreign key constraint' in result['message'].lower())
        user_existence_errors = sum(1 for result in self.test_results if not result['success'] and 'user' in result['message'].lower() and ('not found' in result['message'].lower() or 'does not exist' in result['message'].lower()))
        
        print(f"Foreign Key Constraint Errors: {foreign_key_errors}")
        print(f"User Existence Errors: {user_existence_errors}")
        
        if success_rate >= 85 and foreign_key_errors == 0 and user_existence_errors == 0:
            print("\n✅ ONBOARDING PILLAR CREATION FIX: SUCCESS")
            print("   ✅ User authentication working correctly")
            print("   ✅ User existence check with upsert working")
            print("   ✅ Pillar creation successful without foreign key errors")
            print("   ✅ No user existence errors detected")
            print("   The improved user existence check fix is working correctly!")
        elif foreign_key_errors > 0:
            print("\n❌ ONBOARDING PILLAR CREATION FIX: FOREIGN KEY CONSTRAINT ISSUES")
            print("   ❌ Foreign key constraint errors detected")
            print("   The user upsert fix may not be working properly")
        elif user_existence_errors > 0:
            print("\n❌ ONBOARDING PILLAR CREATION FIX: USER EXISTENCE ISSUES")
            print("   ❌ User existence errors detected")
            print("   The user existence check may not be working properly")
        else:
            print("\n⚠️ ONBOARDING PILLAR CREATION FIX: PARTIAL SUCCESS")
            print("   Some tests failed but no specific user/foreign key errors detected")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        # Clean up test pillar
        if pillar_id:
            self.cleanup_test_pillar(pillar_id)
        
        return success_rate >= 85 and foreign_key_errors == 0 and user_existence_errors == 0

def main():
    """Run Onboarding Pillar Creation Fix Tests"""
    print("🧪 STARTING ONBOARDING PILLAR CREATION FIX BACKEND TESTING")
    print("=" * 80)
    
    tester = OnboardingPillarCreationTester()
    
    try:
        # Run the comprehensive onboarding pillar creation tests
        success = tester.run_comprehensive_onboarding_pillar_test()
        
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
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)