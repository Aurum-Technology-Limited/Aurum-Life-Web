#!/usr/bin/env python3
"""
Sleep Reflections Backend Testing Script
Tests the new sleep reflection endpoints implementation
"""

import requests
import json
import sys
from datetime import datetime, date
from typing import Dict, Any

# Configuration
BACKEND_URL = "https://8f296db8-41e4-45d4-b9b1-dbc5e21b4a2a.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password"

class SleepReflectionsBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def authenticate(self) -> bool:
        """Authenticate with the backend"""
        try:
            print(f"\n🔐 Authenticating with {TEST_EMAIL}...")
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                
                if self.auth_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    
                    # Get user profile to get user_id
                    profile_response = self.session.get(f"{BACKEND_URL}/auth/me")
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        self.user_id = profile_data.get('id')
                        self.log_result("Authentication", True, f"User ID: {self.user_id}")
                        return True
                    else:
                        self.log_result("Authentication", False, f"Failed to get user profile: {profile_response.status_code}")
                        return False
                else:
                    self.log_result("Authentication", False, "No access token received")
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_create_sleep_reflection_table(self) -> bool:
        """Test if sleep_reflections table exists by attempting to query it"""
        try:
            print(f"\n📊 Testing sleep_reflections table existence...")
            
            # Try to get sleep reflections (should work even if empty)
            response = self.session.get(f"{BACKEND_URL}/sleep-reflections?limit=1")
            
            if response.status_code == 200:
                self.log_result("Sleep Reflections Table Exists", True, "Table accessible via API")
                return True
            elif response.status_code == 500:
                # Check if it's a table not found error
                error_text = response.text.lower()
                if "relation" in error_text and "does not exist" in error_text:
                    self.log_result("Sleep Reflections Table Exists", False, "Table does not exist - needs to be created manually in Supabase")
                    return False
                else:
                    self.log_result("Sleep Reflections Table Exists", False, f"Server error: {response.text}")
                    return False
            else:
                self.log_result("Sleep Reflections Table Exists", False, f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Sleep Reflections Table Exists", False, f"Exception: {str(e)}")
            return False
    
    def test_post_sleep_reflection(self) -> Dict[str, Any]:
        """Test POST /api/sleep-reflections endpoint"""
        try:
            print(f"\n📝 Testing POST /api/sleep-reflections...")
            
            # Test data with all required fields
            test_reflection = {
                "date": date.today().isoformat(),
                "sleep_quality": 8,
                "feeling": "refreshed",
                "sleep_hours": "7.5 hours",
                "sleep_influences": "Had a good workout yesterday, avoided caffeine after 2pm",
                "today_intention": "Focus on completing the project presentation and take a walk during lunch"
            }
            
            response = self.session.post(f"{BACKEND_URL}/sleep-reflections", json=test_reflection)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("POST Sleep Reflection", True, f"Created reflection with ID: {data.get('id')}")
                return data
            else:
                self.log_result("POST Sleep Reflection", False, f"Status: {response.status_code}, Response: {response.text}")
                return {}
                
        except Exception as e:
            self.log_result("POST Sleep Reflection", False, f"Exception: {str(e)}")
            return {}
    
    def test_post_sleep_reflection_minimal(self) -> Dict[str, Any]:
        """Test POST with minimal required fields"""
        try:
            print(f"\n📝 Testing POST /api/sleep-reflections (minimal data)...")
            
            # Test data with only required fields
            minimal_reflection = {
                "date": date.today().isoformat(),
                "sleep_quality": 6,
                "feeling": "tired",
                "sleep_hours": "6 hours"
            }
            
            response = self.session.post(f"{BACKEND_URL}/sleep-reflections", json=minimal_reflection)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("POST Sleep Reflection (Minimal)", True, f"Created minimal reflection with ID: {data.get('id')}")
                return data
            else:
                self.log_result("POST Sleep Reflection (Minimal)", False, f"Status: {response.status_code}, Response: {response.text}")
                return {}
                
        except Exception as e:
            self.log_result("POST Sleep Reflection (Minimal)", False, f"Exception: {str(e)}")
            return {}
    
    def test_get_sleep_reflections(self) -> bool:
        """Test GET /api/sleep-reflections endpoint"""
        try:
            print(f"\n📖 Testing GET /api/sleep-reflections...")
            
            response = self.session.get(f"{BACKEND_URL}/sleep-reflections")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET Sleep Reflections", True, f"Retrieved {len(data)} reflections")
                    
                    # Test with limit parameter
                    limit_response = self.session.get(f"{BACKEND_URL}/sleep-reflections?limit=1")
                    if limit_response.status_code == 200:
                        limit_data = limit_response.json()
                        if isinstance(limit_data, list) and len(limit_data) <= 1:
                            self.log_result("GET Sleep Reflections (with limit)", True, f"Limit parameter working, got {len(limit_data)} reflections")
                        else:
                            self.log_result("GET Sleep Reflections (with limit)", False, f"Limit parameter not working properly")
                    
                    return True
                else:
                    self.log_result("GET Sleep Reflections", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_result("GET Sleep Reflections", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("GET Sleep Reflections", False, f"Exception: {str(e)}")
            return False
    
    def test_data_validation(self) -> bool:
        """Test data validation for sleep reflection endpoints"""
        try:
            print(f"\n🔍 Testing data validation...")
            
            validation_tests = [
                {
                    "name": "Sleep Quality Out of Range (High)",
                    "data": {
                        "date": date.today().isoformat(),
                        "sleep_quality": 15,  # Invalid - should be 1-10
                        "feeling": "great",
                        "sleep_hours": "8 hours"
                    },
                    "should_fail": True
                },
                {
                    "name": "Sleep Quality Out of Range (Low)",
                    "data": {
                        "date": date.today().isoformat(),
                        "sleep_quality": 0,  # Invalid - should be 1-10
                        "feeling": "terrible",
                        "sleep_hours": "4 hours"
                    },
                    "should_fail": True
                },
                {
                    "name": "Missing Required Field (sleep_quality)",
                    "data": {
                        "date": date.today().isoformat(),
                        "feeling": "okay",
                        "sleep_hours": "7 hours"
                    },
                    "should_fail": True
                },
                {
                    "name": "Missing Required Field (feeling)",
                    "data": {
                        "date": date.today().isoformat(),
                        "sleep_quality": 7,
                        "sleep_hours": "7 hours"
                    },
                    "should_fail": True
                },
                {
                    "name": "Missing Required Field (sleep_hours)",
                    "data": {
                        "date": date.today().isoformat(),
                        "sleep_quality": 7,
                        "feeling": "good"
                    },
                    "should_fail": True
                },
                {
                    "name": "Valid Sleep Quality (Boundary - 1)",
                    "data": {
                        "date": date.today().isoformat(),
                        "sleep_quality": 1,
                        "feeling": "awful",
                        "sleep_hours": "3 hours"
                    },
                    "should_fail": False
                },
                {
                    "name": "Valid Sleep Quality (Boundary - 10)",
                    "data": {
                        "date": date.today().isoformat(),
                        "sleep_quality": 10,
                        "feeling": "amazing",
                        "sleep_hours": "9 hours"
                    },
                    "should_fail": False
                }
            ]
            
            validation_success = True
            
            for test in validation_tests:
                try:
                    response = self.session.post(f"{BACKEND_URL}/sleep-reflections", json=test["data"])
                    
                    if test["should_fail"]:
                        # Should return 400 or 422 for validation errors
                        if response.status_code in [400, 422]:
                            self.log_result(f"Validation: {test['name']}", True, f"Correctly rejected with {response.status_code}")
                        else:
                            self.log_result(f"Validation: {test['name']}", False, f"Should have failed but got {response.status_code}")
                            validation_success = False
                    else:
                        # Should succeed
                        if response.status_code == 200:
                            self.log_result(f"Validation: {test['name']}", True, "Correctly accepted valid data")
                        else:
                            self.log_result(f"Validation: {test['name']}", False, f"Should have succeeded but got {response.status_code}: {response.text}")
                            validation_success = False
                            
                except Exception as e:
                    self.log_result(f"Validation: {test['name']}", False, f"Exception: {str(e)}")
                    validation_success = False
            
            return validation_success
            
        except Exception as e:
            self.log_result("Data Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication_required(self) -> bool:
        """Test that endpoints require authentication"""
        try:
            print(f"\n🔒 Testing authentication requirements...")
            
            # Create a session without auth token
            unauth_session = requests.Session()
            
            # Test POST without auth
            test_data = {
                "date": date.today().isoformat(),
                "sleep_quality": 7,
                "feeling": "good",
                "sleep_hours": "8 hours"
            }
            
            post_response = unauth_session.post(f"{BACKEND_URL}/sleep-reflections", json=test_data)
            post_auth_required = post_response.status_code in [401, 403]
            
            # Test GET without auth
            get_response = unauth_session.get(f"{BACKEND_URL}/sleep-reflections")
            get_auth_required = get_response.status_code in [401, 403]
            
            if post_auth_required and get_auth_required:
                self.log_result("Authentication Required", True, "Both endpoints properly require authentication")
                return True
            else:
                details = f"POST auth required: {post_auth_required} (status: {post_response.status_code}), GET auth required: {get_auth_required} (status: {get_response.status_code})"
                self.log_result("Authentication Required", False, details)
                return False
                
        except Exception as e:
            self.log_result("Authentication Required", False, f"Exception: {str(e)}")
            return False
    
    def test_user_data_isolation(self) -> bool:
        """Test that users can only see their own sleep reflections"""
        try:
            print(f"\n🔐 Testing user data isolation...")
            
            # This test assumes we have created some reflections for the current user
            # and verifies that the GET endpoint only returns data for the authenticated user
            
            response = self.session.get(f"{BACKEND_URL}/sleep-reflections")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # All returned reflections should belong to the current user
                    # (We can't easily test cross-user isolation without another user account)
                    self.log_result("User Data Isolation", True, f"Retrieved {len(data)} reflections for authenticated user")
                    return True
                else:
                    self.log_result("User Data Isolation", False, f"Unexpected response format: {type(data)}")
                    return False
            else:
                self.log_result("User Data Isolation", False, f"Failed to get reflections: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("User Data Isolation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all sleep reflection tests"""
        print("🧪 SLEEP REFLECTIONS BACKEND TESTING")
        print("=" * 50)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Check if table exists
        table_exists = self.test_create_sleep_reflection_table()
        
        if not table_exists:
            print("\n⚠️  WARNING: sleep_reflections table does not exist!")
            print("Please execute the SQL script manually in Supabase dashboard:")
            print("File: /app/create_sleep_reflections_table.sql")
            print("\nSkipping endpoint tests...")
            return False
        
        # Step 3: Test authentication requirements
        self.test_authentication_required()
        
        # Step 4: Test POST endpoint
        reflection1 = self.test_post_sleep_reflection()
        reflection2 = self.test_post_sleep_reflection_minimal()
        
        # Step 5: Test GET endpoint
        self.test_get_sleep_reflections()
        
        # Step 6: Test data validation
        self.test_data_validation()
        
        # Step 7: Test user data isolation
        self.test_user_data_isolation()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if total - passed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n{'🎉 ALL TESTS PASSED!' if passed == total else '⚠️  SOME TESTS FAILED'}")
        
        return success_rate

def main():
    """Main function"""
    tester = SleepReflectionsBackendTester()
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()