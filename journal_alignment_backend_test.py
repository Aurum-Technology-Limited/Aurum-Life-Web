#!/usr/bin/env python3
"""
Comprehensive Journal and Alignment Endpoints Testing
Tests all journal and alignment API endpoints to verify fixes have been applied
"""

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid
import time

class JournalAlignmentBackendTester:
    def __init__(self, base_url="https://supa-data-explained.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_journal_id = None
        self.created_template_id = None

    def log_test(self, name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details,
            'response_data': response_data
        })

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make authenticated API request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}", {}

            response_time = (time.time() - start_time) * 1000  # Convert to ms
            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if not success:
                return False, f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}", response_data
            
            print(f"   ⏱️  Response time: {response_time:.1f}ms")
            return True, "Success", response_data

        except requests.exceptions.Timeout:
            return False, "Request timeout (30s)", {}
        except requests.exceptions.ConnectionError:
            return False, "Connection error", {}
        except Exception as e:
            return False, f"Request error: {str(e)}", {}

    def test_authentication(self):
        """Test login with provided credentials"""
        print("\n🔐 Testing Authentication...")
        
        success, message, response_data = self.make_request(
            'POST', 
            'auth/login',
            {
                "email": "marc.alleyne@aurumtechnologyltd.com",
                "password": "password123"
            }
        )
        
        if success and 'access_token' in response_data:
            self.token = response_data['access_token']
            self.log_test("Authentication", True, "Login successful with marc.alleyne@aurumtechnologyltd.com")
            return True
        else:
            self.log_test("Authentication", False, f"Login failed: {message}")
            return False

    def test_journal_get(self):
        """Test GET /api/journal - Fetch journal entries"""
        print("\n📖 Testing GET /api/journal...")
        
        success, message, response_data = self.make_request('GET', 'journal')
        
        if success:
            # Check if response is an array
            if isinstance(response_data, list):
                self.log_test("GET /api/journal", True, f"Retrieved {len(response_data)} journal entries")
                return True
            else:
                self.log_test("GET /api/journal", False, "Response is not an array", response_data)
                return False
        else:
            self.log_test("GET /api/journal", False, message, response_data)
            return False

    def test_journal_post(self):
        """Test POST /api/journal - Create journal entry (confirm 405 fix)"""
        print("\n📝 Testing POST /api/journal...")
        
        journal_data = {
            "title": "Test Journal Entry - API Testing",
            "content": "This is a comprehensive test of the journal creation endpoint. Testing that the 405 error has been resolved and POST requests now work correctly.",
            "mood": "optimistic",
            "tags": ["testing", "api", "journal"]
        }
        
        success, message, response_data = self.make_request(
            'POST',
            'journal',
            journal_data,
            200  # Expecting 200 for successful creation
        )
        
        if success:
            # Store the created journal ID for potential cleanup
            if 'id' in response_data:
                self.created_journal_id = response_data['id']
            self.log_test("POST /api/journal", True, "Journal entry created successfully (405 error fixed)")
            return True
        else:
            self.log_test("POST /api/journal", False, f"Journal creation failed: {message}")
            return False

    def test_journal_templates_get(self):
        """Test GET /api/journal/templates - Fetch journal templates (new)"""
        print("\n📋 Testing GET /api/journal/templates...")
        
        success, message, response_data = self.make_request('GET', 'journal/templates')
        
        if success:
            # Check if response is an array
            if isinstance(response_data, list):
                self.log_test("GET /api/journal/templates", True, f"Retrieved {len(response_data)} journal templates")
                return True
            else:
                self.log_test("GET /api/journal/templates", False, "Response is not an array", response_data)
                return False
        else:
            self.log_test("GET /api/journal/templates", False, message, response_data)
            return False

    def test_journal_templates_post(self):
        """Test POST /api/journal/templates - Create journal template (new)"""
        print("\n📝 Testing POST /api/journal/templates...")
        
        template_data = {
            "name": "Daily Reflection Template - API Test",
            "description": "A template for daily reflection and goal tracking",
            "template_type": "daily_reflection",
            "prompts": [
                "What went well today?",
                "What could I improve tomorrow?",
                "What am I grateful for?",
                "How did I progress toward my goals?"
            ],
            "default_tags": ["reflection", "goals"],
            "icon": "📝",
            "color": "#F4B400"
        }
        
        success, message, response_data = self.make_request(
            'POST',
            'journal/templates',
            template_data,
            200  # Expecting 200 for successful creation
        )
        
        if success:
            # Store the created template ID for potential cleanup
            if 'id' in response_data:
                self.created_template_id = response_data['id']
            self.log_test("POST /api/journal/templates", True, "Journal template created successfully")
            return True
        else:
            self.log_test("POST /api/journal/templates", False, f"Template creation failed: {message}")
            return False

    def test_alignment_dashboard(self):
        """Test GET /api/alignment/dashboard - Main alignment dashboard"""
        print("\n📊 Testing GET /api/alignment/dashboard...")
        
        success, message, response_data = self.make_request('GET', 'alignment/dashboard')
        
        if success:
            # Check for expected alignment dashboard fields
            expected_fields = ['rolling_weekly_score', 'monthly_score', 'monthly_goal', 'progress_percentage']
            has_expected_fields = all(field in response_data for field in expected_fields)
            
            if has_expected_fields:
                self.log_test("GET /api/alignment/dashboard", True, "Alignment dashboard data retrieved with all expected fields")
                return True
            else:
                missing_fields = [field for field in expected_fields if field not in response_data]
                self.log_test("GET /api/alignment/dashboard", False, f"Missing expected fields: {missing_fields}", response_data)
                return False
        else:
            self.log_test("GET /api/alignment/dashboard", False, message, response_data)
            return False

    def test_alignment_weekly_score(self):
        """Test GET /api/alignment/weekly-score - Weekly score (new)"""
        print("\n📈 Testing GET /api/alignment/weekly-score...")
        
        success, message, response_data = self.make_request('GET', 'alignment/weekly-score')
        
        if success:
            # Check if response has score data
            has_score_data = isinstance(response_data, dict) and len(response_data) > 0
            
            if has_score_data:
                self.log_test("GET /api/alignment/weekly-score", True, "Weekly alignment score retrieved")
                return True
            else:
                self.log_test("GET /api/alignment/weekly-score", False, "Weekly score response invalid", response_data)
                return False
        else:
            self.log_test("GET /api/alignment/weekly-score", False, message, response_data)
            return False

    def test_alignment_monthly_score(self):
        """Test GET /api/alignment/monthly-score - Monthly score (new)"""
        print("\n📅 Testing GET /api/alignment/monthly-score...")
        
        success, message, response_data = self.make_request('GET', 'alignment/monthly-score')
        
        if success:
            # Check if response has score data
            has_score_data = isinstance(response_data, dict) and len(response_data) > 0
            
            if has_score_data:
                self.log_test("GET /api/alignment/monthly-score", True, "Monthly alignment score retrieved")
                return True
            else:
                self.log_test("GET /api/alignment/monthly-score", False, "Monthly score response invalid", response_data)
                return False
        else:
            self.log_test("GET /api/alignment/monthly-score", False, message, response_data)
            return False

    def test_alignment_score_legacy(self):
        """Test GET /api/alignment-score - Legacy endpoint (new)"""
        print("\n🔄 Testing GET /api/alignment-score (Legacy)...")
        
        success, message, response_data = self.make_request('GET', 'alignment-score')
        
        if success:
            # Check for expected alignment score fields (should match dashboard structure)
            expected_fields = ['rolling_weekly_score', 'monthly_score', 'monthly_goal', 'progress_percentage']
            has_expected_fields = all(field in response_data for field in expected_fields)
            
            if has_expected_fields:
                self.log_test("GET /api/alignment-score", True, "Legacy alignment score endpoint working (404 error resolved)")
                return True
            else:
                missing_fields = [field for field in expected_fields if field not in response_data]
                self.log_test("GET /api/alignment-score", False, f"Missing expected fields: {missing_fields}", response_data)
                return False
        else:
            self.log_test("GET /api/alignment-score", False, message, response_data)
            return False

    def test_network_connectivity(self):
        """Test basic network connectivity and health check"""
        print("\n🌐 Testing Network Connectivity...")
        
        success, message, response_data = self.make_request('GET', 'health')
        
        if success:
            self.log_test("Network Connectivity", True, "Backend health check passed")
            return True
        else:
            self.log_test("Network Connectivity", False, f"Health check failed: {message}")
            return False

    def cleanup_test_data(self):
        """Clean up any test data created during testing"""
        print("\n🧹 Cleaning up test data...")
        
        cleanup_success = True
        
        # Clean up created journal entry
        if self.created_journal_id:
            success, message, response_data = self.make_request(
                'DELETE',
                f'journal/{self.created_journal_id}'
            )
            if success:
                print(f"   ✅ Cleaned up journal entry: {self.created_journal_id}")
            else:
                print(f"   ⚠️  Failed to clean up journal entry: {message}")
                cleanup_success = False
        
        # Clean up created template
        if self.created_template_id:
            success, message, response_data = self.make_request(
                'DELETE',
                f'journal/templates/{self.created_template_id}'
            )
            if success:
                print(f"   ✅ Cleaned up journal template: {self.created_template_id}")
            else:
                print(f"   ⚠️  Failed to clean up journal template: {message}")
                cleanup_success = False
        
        return cleanup_success

    def run_all_tests(self):
        """Run comprehensive journal and alignment backend tests"""
        print("🚀 Starting Comprehensive Journal and Alignment Endpoints Testing")
        print("=" * 70)
        print("📋 Testing Scope:")
        print("   • Journal CRUD endpoints (GET, POST)")
        print("   • Journal Templates endpoints (GET, POST)")
        print("   • Alignment Dashboard and Score endpoints")
        print("   • Network connectivity verification")
        print("=" * 70)
        
        # Test network connectivity first
        if not self.test_network_connectivity():
            print("\n❌ Network connectivity failed - stopping tests")
            return False
        
        # Test authentication
        if not self.test_authentication():
            print("\n❌ Authentication failed - stopping tests")
            return False
        
        # Test Journal Endpoints
        print("\n" + "="*50)
        print("📖 JOURNAL ENDPOINTS TESTING")
        print("="*50)
        
        self.test_journal_get()
        self.test_journal_post()
        self.test_journal_templates_get()
        self.test_journal_templates_post()
        
        # Test Alignment Endpoints
        print("\n" + "="*50)
        print("📊 ALIGNMENT ENDPOINTS TESTING")
        print("="*50)
        
        self.test_alignment_dashboard()
        self.test_alignment_weekly_score()
        self.test_alignment_monthly_score()
        self.test_alignment_score_legacy()
        
        # Cleanup test data
        self.cleanup_test_data()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 JOURNAL & ALIGNMENT ENDPOINTS TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Show test results by category
        journal_tests = [test for test in self.test_results if 'journal' in test['name'].lower()]
        alignment_tests = [test for test in self.test_results if 'alignment' in test['name'].lower()]
        
        print(f"\n📖 Journal Tests: {len([t for t in journal_tests if t['success']])}/{len(journal_tests)} passed")
        print(f"📊 Alignment Tests: {len([t for t in alignment_tests if t['success']])}/{len(alignment_tests)} passed")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['name']}: {test['details']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Journal 405 errors resolved")
            print("✅ Journal templates endpoints working")
            print("✅ Alignment score 404 errors resolved")
            print("✅ Network connectivity stable")
        
        print("\n" + "=" * 70)
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = JournalAlignmentBackendTester()
    
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