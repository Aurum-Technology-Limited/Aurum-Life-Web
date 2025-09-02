#!/usr/bin/env python3
"""
Journal Endpoints Backend Testing
Tests journal CRUD operations to verify 405 error fix
"""

import requests
import sys
import json
from datetime import datetime
import uuid
import time

class JournalEndpointsTester:
    def __init__(self, base_url="https://emotional-os-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_entry_id = None

    def log_test(self, name, success, details="", response_data=None, response_time=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            time_info = f" ({response_time:.1f}ms)" if response_time else ""
            print(f"✅ {name} - PASSED{time_info}")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'response_time': response_time
        })

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make authenticated API request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}", {}, 0

            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if not success:
                return False, f"Expected {expected_status}, got {response.status_code}: {response.text}", response_data, response_time
            
            return True, "Success", response_data, response_time

        except requests.exceptions.Timeout:
            return False, "Request timeout (30s)", {}, 0
        except requests.exceptions.ConnectionError:
            return False, "Connection error", {}, 0
        except Exception as e:
            return False, f"Request error: {str(e)}", {}, 0

    def test_authentication(self):
        """Test authentication with provided credentials"""
        print("\n🔐 Testing Authentication...")
        
        success, message, response_data, response_time = self.make_request(
            'POST', 
            'auth/login',
            {
                "email": "marc.alleyne@aurumtechnologyltd.com",
                "password": "password123"
            }
        )
        
        if success and 'access_token' in response_data:
            self.token = response_data['access_token']
            self.log_test("Authentication", True, "Login successful", response_data, response_time)
            return True
        else:
            self.log_test("Authentication", False, f"Login failed: {message}", response_data, response_time)
            return False

    def test_get_journal_entries(self):
        """Test GET /api/journal endpoint"""
        print("\n📖 Testing GET Journal Entries...")
        
        success, message, response_data, response_time = self.make_request('GET', 'journal')
        
        if success:
            # Check if response is an array
            if isinstance(response_data, list):
                self.log_test("GET Journal Entries", True, f"Retrieved {len(response_data)} journal entries", response_data, response_time)
                return True
            else:
                self.log_test("GET Journal Entries", False, "Response is not an array", response_data, response_time)
                return False
        else:
            self.log_test("GET Journal Entries", False, message, response_data, response_time)
            return False

    def test_create_journal_entry(self):
        """Test POST /api/journal endpoint to verify 405 error is fixed"""
        print("\n✍️ Testing POST Journal Entry (405 Error Fix)...")
        
        # Create test journal entry data
        entry_data = {
            "title": "Test Entry",
            "content": "This is a test journal entry to verify the 405 error is fixed."
        }
        
        success, message, response_data, response_time = self.make_request(
            'POST', 
            'journal',
            entry_data,
            200  # Expecting 200 for successful creation
        )
        
        if success:
            # Check if response contains the created entry data
            if 'id' in response_data:
                self.created_entry_id = response_data['id']
                self.log_test("POST Journal Entry", True, f"Created journal entry with ID: {self.created_entry_id}", response_data, response_time)
                return True
            else:
                self.log_test("POST Journal Entry", False, "Response missing entry ID", response_data, response_time)
                return False
        else:
            # Check if we got a 405 error (which would indicate the fix didn't work)
            if "405" in message:
                self.log_test("POST Journal Entry", False, "405 Method Not Allowed error still present - fix not working", response_data, response_time)
            else:
                self.log_test("POST Journal Entry", False, message, response_data, response_time)
            return False

    def test_update_journal_entry(self):
        """Test PUT /api/journal/{entry_id} endpoint"""
        print("\n✏️ Testing PUT Journal Entry...")
        
        if not self.created_entry_id:
            self.log_test("PUT Journal Entry", False, "No entry ID available for update test")
            return False
        
        # Update data
        update_data = {
            "title": "Updated Test Entry",
            "content": "This is an updated test journal entry to verify PUT endpoint works."
        }
        
        success, message, response_data, response_time = self.make_request(
            'PUT', 
            f'journal/{self.created_entry_id}',
            update_data
        )
        
        if success:
            # Check if response indicates success
            if response_data.get('success') == True:
                self.log_test("PUT Journal Entry", True, "Journal entry updated successfully", response_data, response_time)
                return True
            else:
                self.log_test("PUT Journal Entry", False, "Update response missing success indicator", response_data, response_time)
                return False
        else:
            self.log_test("PUT Journal Entry", False, message, response_data, response_time)
            return False

    def test_delete_journal_entry(self):
        """Test DELETE /api/journal/{entry_id} endpoint"""
        print("\n🗑️ Testing DELETE Journal Entry...")
        
        if not self.created_entry_id:
            self.log_test("DELETE Journal Entry", False, "No entry ID available for delete test")
            return False
        
        success, message, response_data, response_time = self.make_request(
            'DELETE', 
            f'journal/{self.created_entry_id}'
        )
        
        if success:
            # Check if response indicates success
            if response_data.get('success') == True:
                self.log_test("DELETE Journal Entry", True, "Journal entry deleted successfully", response_data, response_time)
                return True
            else:
                self.log_test("DELETE Journal Entry", False, "Delete response missing success indicator", response_data, response_time)
                return False
        else:
            self.log_test("DELETE Journal Entry", False, message, response_data, response_time)
            return False

    def test_verify_405_fix(self):
        """Comprehensive test to verify 405 error is completely fixed"""
        print("\n🔍 Testing 405 Error Fix Verification...")
        
        # Test all HTTP methods on journal endpoint to ensure proper routing
        methods_to_test = [
            ('GET', 'journal', None, 200),
            ('POST', 'journal', {"title": "405 Fix Test", "content": "Testing 405 fix"}, 200),
        ]
        
        all_methods_working = True
        
        for method, endpoint, data, expected_status in methods_to_test:
            success, message, response_data, response_time = self.make_request(
                method, endpoint, data, expected_status
            )
            
            test_name = f"405 Fix - {method} {endpoint}"
            
            if success:
                self.log_test(test_name, True, f"{method} method working correctly", response_data, response_time)
            else:
                # Check specifically for 405 errors
                if "405" in message:
                    self.log_test(test_name, False, f"405 Method Not Allowed - fix incomplete for {method}", response_data, response_time)
                else:
                    self.log_test(test_name, False, message, response_data, response_time)
                all_methods_working = False
        
        return all_methods_working

    def run_all_tests(self):
        """Run comprehensive journal endpoints tests"""
        print("🚀 Starting Journal Endpoints Backend Testing")
        print("=" * 60)
        print("🎯 OBJECTIVE: Verify 405 error when saving journal entries has been fixed")
        print("=" * 60)
        
        # Test authentication first
        if not self.test_authentication():
            print("\n❌ Authentication failed - stopping tests")
            return False
        
        # Test existing GET endpoint
        self.test_get_journal_entries()
        
        # Test POST endpoint (main focus - 405 error fix)
        self.test_create_journal_entry()
        
        # Test PUT endpoint
        self.test_update_journal_entry()
        
        # Test DELETE endpoint
        self.test_delete_journal_entry()
        
        # Comprehensive 405 fix verification
        self.test_verify_405_fix()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 JOURNAL ENDPOINTS TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['name']}: {test['details']}")
        
        # Show successful tests
        successful_tests = [test for test in self.test_results if test['success']]
        if successful_tests:
            print("\n✅ SUCCESSFUL TESTS:")
            for test in successful_tests:
                time_info = f" ({test['response_time']:.1f}ms)" if test['response_time'] else ""
                print(f"  • {test['name']}{time_info}")
        
        # 405 Error Fix Status
        print("\n" + "=" * 60)
        post_test = next((test for test in self.test_results if 'POST Journal Entry' in test['name']), None)
        if post_test and post_test['success']:
            print("🎉 405 ERROR FIX STATUS: ✅ RESOLVED")
            print("   POST /api/journal endpoint is working correctly")
        else:
            print("🚨 405 ERROR FIX STATUS: ❌ NOT RESOLVED")
            print("   POST /api/journal endpoint still has issues")
        
        print("=" * 60)
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = JournalEndpointsTester()
    
    try:
        success = tester.run_all_tests()
        all_passed = tester.print_summary()
        
        return 0 if all_passed else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        tester.print_summary()
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        tester.print_summary()
        return 1

if __name__ == "__main__":
    sys.exit(main())