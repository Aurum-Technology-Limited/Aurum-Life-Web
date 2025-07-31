#!/usr/bin/env python3
"""
Backend Integration Test - Verify Core Endpoints After Frontend Integration
Tests core functionality to ensure backend is still working after frontend changes
"""

import requests
import json
import time
from datetime import datetime

class BackendIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str, response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time_ms": round(response_time * 1000, 1),
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details} ({result['response_time_ms']}ms)")
        
    def authenticate(self, email: str = "nav.test@aurumlife.com", password: str = "testpassword123") -> bool:
        """Authenticate with the API"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/auth/login",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log_result("Authentication", True, f"Successfully authenticated as {email}", response_time)
                return True
            else:
                self.log_result("Authentication", False, f"Failed with status {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception during authentication: {str(e)}")
            return False
    
    def get_headers(self) -> dict:
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_core_endpoints(self):
        """Test core CRUD endpoints"""
        print("\n🔧 TESTING CORE ENDPOINTS")
        print("=" * 60)
        
        endpoints = [
            ("GET", "/dashboard", "Dashboard"),
            ("GET", "/pillars", "Pillars List"),
            ("GET", "/areas", "Areas List"),
            ("GET", "/projects", "Projects List"),
            ("GET", "/tasks", "Tasks List"),
            ("GET", "/today", "Today View"),
            ("GET", "/insights", "Insights"),
            ("GET", "/auth/me", "User Profile")
        ]
        
        for method, endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.api_base}{endpoint}",
                    headers=self.get_headers()
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        count = len(data)
                        self.log_result(name, True, f"Retrieved {count} items", response_time)
                    elif isinstance(data, dict):
                        keys = len(data.keys())
                        self.log_result(name, True, f"Retrieved data with {keys} fields", response_time)
                    else:
                        self.log_result(name, True, "Retrieved data successfully", response_time)
                else:
                    self.log_result(name, False, f"Failed with status {response.status_code}", response_time)
                    
            except Exception as e:
                self.log_result(name, False, f"Exception: {str(e)}")
    
    def run_integration_test(self):
        """Run backend integration test"""
        print("🔗 BACKEND INTEGRATION TEST AFTER FRONTEND CHANGES")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test core endpoints
        self.test_core_endpoints()
        
        # Step 3: Generate summary
        self.generate_summary()
        
        return True
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("🎯 BACKEND INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}: {result['details']}")
        
        # Performance summary
        avg_response_time = sum(r["response_time_ms"] for r in self.test_results) / len(self.test_results)
        print(f"\n⚡ PERFORMANCE:")
        print(f"Average Response Time: {avg_response_time:.1f}ms")
        
        print("\n" + "=" * 80)
        print(f"Testing completed at: {datetime.now().isoformat()}")
        print("=" * 80)

def main():
    """Main test execution"""
    tester = BackendIntegrationTester()
    success = tester.run_integration_test()
    
    if success:
        print("\n🎉 Backend integration testing completed!")
    else:
        print("\n💥 Backend integration testing failed!")
        exit(1)

if __name__ == "__main__":
    main()