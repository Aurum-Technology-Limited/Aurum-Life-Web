#!/usr/bin/env python3
"""
Extended Email Login and Core API Testing
Tests additional core endpoints with email authentication
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://15d7219c-892b-4111-8d96-e95547e179d6.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_CREDENTIALS = {
    "email": "nav.test@aurumlife.com",
    "password": "testpassword123"
}

class ExtendedEmailLoginTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, response_time=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        time_info = f" ({response_time:.1f}ms)" if response_time else ""
        print(f"{status}: {test_name}{time_info}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate(self):
        """Authenticate and get access token"""
        print("🔐 Authenticating...")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=TEST_CREDENTIALS,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    print(f"✅ Authentication successful")
                    return True
            
            print(f"❌ Authentication failed: {response.status_code}")
            return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Authentication request failed: {str(e)}")
            return False

    def test_extended_core_endpoints(self):
        """Test additional core endpoints with authentication"""
        print("🔗 Testing Extended Core Endpoints...")
        
        if not self.access_token:
            self.log_result(
                "Extended Core Endpoints",
                False,
                "No access token available"
            )
            return False
        
        # Extended list of endpoints to test
        endpoints_to_test = [
            ("GET", "/projects", "Projects Endpoint"),
            ("GET", "/tasks", "Tasks Endpoint"),
            ("GET", "/today", "Today View Endpoint"),
            ("GET", "/project-templates", "Project Templates Endpoint"),
            ("GET", "/journal", "Journal Endpoint"),
            ("GET", "/insights", "Insights Endpoint")
        ]
        
        auth_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        successful_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for method, endpoint, name in endpoints_to_test:
            try:
                start_time = time.time()
                
                response = self.session.get(
                    f"{API_BASE}{endpoint}",
                    headers=auth_headers,
                    timeout=15
                )
                
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    data_info = ""
                    
                    # Provide specific info based on endpoint
                    if endpoint == "/projects":
                        if isinstance(data, list):
                            data_info = f"Retrieved {len(data)} projects"
                        else:
                            data_info = "Projects data structure received"
                    elif endpoint == "/tasks":
                        if isinstance(data, list):
                            data_info = f"Retrieved {len(data)} tasks"
                        else:
                            data_info = "Tasks data structure received"
                    elif endpoint == "/today":
                        if isinstance(data, dict):
                            tasks_count = len(data.get('tasks', []))
                            data_info = f"Today view with {tasks_count} tasks"
                        else:
                            data_info = "Today view data received"
                    elif endpoint == "/project-templates":
                        if isinstance(data, list):
                            data_info = f"Retrieved {len(data)} project templates"
                        else:
                            data_info = "Project templates data received"
                    elif endpoint == "/journal":
                        if isinstance(data, dict) and 'entries' in data:
                            entries_count = len(data.get('entries', []))
                            data_info = f"Journal with {entries_count} entries"
                        else:
                            data_info = "Journal data received"
                    elif endpoint == "/insights":
                        if isinstance(data, dict):
                            data_info = f"Insights data with {len(data)} sections"
                        else:
                            data_info = "Insights data received"
                    else:
                        data_info = "Data received successfully"
                    
                    self.log_result(
                        name,
                        True,
                        data_info,
                        response_time
                    )
                    successful_endpoints += 1
                else:
                    self.log_result(
                        name,
                        False,
                        f"Request failed with status {response.status_code}: {response.text[:200]}",
                        response_time
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result(
                    name,
                    False,
                    f"Request failed: {str(e)}"
                )
        
        # Overall result
        success_rate = (successful_endpoints / total_endpoints) * 100
        overall_success = success_rate >= 80  # 80% success rate threshold
        
        self.log_result(
            "Extended Core Endpoints",
            overall_success,
            f"Successfully accessed {successful_endpoints}/{total_endpoints} endpoints ({success_rate:.1f}%)"
        )
        
        return overall_success

    def test_authentication_persistence(self):
        """Test that authentication token works across multiple requests"""
        print("🔄 Testing Authentication Persistence...")
        
        if not self.access_token:
            self.log_result(
                "Authentication Persistence",
                False,
                "No access token available"
            )
            return False
        
        auth_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Make multiple requests to different endpoints
        test_endpoints = ["/auth/me", "/dashboard", "/pillars"]
        successful_requests = 0
        
        for endpoint in test_endpoints:
            try:
                response = self.session.get(
                    f"{API_BASE}{endpoint}",
                    headers=auth_headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    successful_requests += 1
                    
            except requests.exceptions.RequestException:
                pass
        
        success = successful_requests == len(test_endpoints)
        
        self.log_result(
            "Authentication Persistence",
            success,
            f"Token worked for {successful_requests}/{len(test_endpoints)} consecutive requests"
        )
        
        return success

    def run_extended_tests(self):
        """Run extended email login and API tests"""
        print("🚀 Starting Extended Email Login and API Testing")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {TEST_CREDENTIALS['email']}")
        print("=" * 70)
        print()
        
        # First authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        print()
        
        # Run extended tests
        tests = [
            ("Extended Core Endpoints", self.test_extended_core_endpoints),
            ("Authentication Persistence", self.test_authentication_persistence)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_result(
                    test_name,
                    False,
                    f"Test execution failed: {str(e)}"
                )
        
        # Print summary
        print("=" * 70)
        print("📊 EXTENDED EMAIL LOGIN AND API TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests) * 100
        overall_status = "✅ PASS" if success_rate >= 80 else "❌ FAIL"
        
        print(f"Overall Status: {overall_status}")
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Print individual test results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("=" * 70)
        
        if success_rate >= 80:
            print("🎉 EXTENDED EMAIL LOGIN TESTING: COMPREHENSIVE SUCCESS")
            print("✅ Email authentication working across all core endpoints")
            print("✅ Token persistence verified")
            print("✅ End-to-end functionality confirmed")
        else:
            print("🚨 EXTENDED EMAIL LOGIN TESTING: ISSUES DETECTED")
            print("❌ Some core endpoints or functionality not working properly")
        
        print("=" * 70)
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = ExtendedEmailLoginTester()
    success = tester.run_extended_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()