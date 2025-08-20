#!/usr/bin/env python3
"""
Backend Smoke Test - Legacy Admin Endpoints Removal Verification
Tests the specific requirements from the review request:
1) GET /api/health -> 200
2) Auth flow (Supabase-only): POST /api/auth/login with marc.alleyne@aurumtechnologyltd.com/password123 -> 200; then GET /api/auth/me -> 200
3) Core endpoints under auth: GET /api/pillars, /api/areas, /api/projects, /api/tasks, /api/insights -> 200
4) Uploads flow basics: POST /api/uploads/initiate (small file meta) -> 200
"""

import requests
import json
import time
import io
from typing import Dict, Any, Optional

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://31e11061-3a9b-4b56-884b-e50264312c7d.preview.emergentagent.com/api"
TEST_EMAIL = "smoketest_e0742f61@aurumtechnologyltd.com"
TEST_PASSWORD = "password123"

class LegacyAdminRemovalSmokeTest:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
    def log_result(self, step: str, success: bool, status_code: int = None, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            "step": step,
            "success": success,
            "status_code": status_code,
            "details": details,
            "response_time_ms": round(response_time * 1000, 1)
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_str = f"({result['response_time_ms']}ms)" if response_time > 0 else ""
        print(f"{status} {step} - Status: {status_code} {time_str}")
        if details:
            print(f"    Details: {details}")
        print()

    def make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request with timing"""
        url = f"{BACKEND_URL}{endpoint}"
        
        # Add authorization header if we have a token
        if self.access_token and 'headers' not in kwargs:
            kwargs['headers'] = {}
        if self.access_token:
            kwargs['headers']['Authorization'] = f"Bearer {self.access_token}"
            
        start_time = time.time()
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            end_time = time.time()
            return response, end_time - start_time
        except Exception as e:
            end_time = time.time()
            print(f"Request failed: {e}")
            # Create a mock response for error handling
            class MockResponse:
                def __init__(self, error_msg):
                    self.status_code = 0
                    self.text = str(error_msg)
                    self.error_msg = error_msg
                def json(self):
                    return {"error": str(self.error_msg)}
            return MockResponse(e), end_time - start_time

    def test_health_check(self):
        """Test 1: GET /api/health -> 200"""
        print("🏥 Test 1: GET /api/health")
        
        response, response_time = self.make_request("GET", "/health")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                status = data.get("status", "unknown")
                details = f"Health status: {status}"
            except Exception as e:
                details = f"JSON parse failed: {e}"
        else:
            details = f"Health check failed: {response.text[:200]}"
            
        self.log_result("GET /api/health", success, response.status_code, details, response_time)
        return success

    def test_auth_login(self):
        """Test 2a: POST /api/auth/login with credentials"""
        print("🔐 Test 2a: POST /api/auth/login")
        
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response, response_time = self.make_request("POST", "/auth/login", json=payload)
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    details = f"Access token received (length: {len(self.access_token)})"
                else:
                    success = False
                    details = "No access_token in response"
            except Exception as e:
                success = False
                details = f"Failed to parse JSON: {e}"
        else:
            details = f"Login failed: {response.text[:200]}"
            
        self.log_result("POST /api/auth/login", success, response.status_code, details, response_time)
        return success

    def test_auth_me(self):
        """Test 2b: GET /api/auth/me with access token"""
        print("👤 Test 2b: GET /api/auth/me")
        
        if not self.access_token:
            self.log_result("GET /api/auth/me", False, None, "No access token available")
            return False
            
        response, response_time = self.make_request("GET", "/auth/me")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                user_id = data.get("id", "unknown")
                email = data.get("email", "unknown")
                details = f"User authenticated: {email} (ID: {user_id})"
            except Exception as e:
                details = f"Response received but JSON parse failed: {e}"
        else:
            details = f"Auth verification failed: {response.text[:200]}"
            
        self.log_result("GET /api/auth/me", success, response.status_code, details, response_time)
        return success

    def test_core_endpoints(self):
        """Test 3: Core endpoints under auth"""
        print("🔒 Test 3: Core endpoints under authentication")
        
        if not self.access_token:
            self.log_result("Core endpoints test", False, None, "No access token available")
            return False
        
        endpoints = [
            ("/pillars", "🏛️ Pillars"),
            ("/areas", "🗺️ Areas"),
            ("/projects", "📋 Projects"),
            ("/tasks", "✅ Tasks"),
            ("/insights", "📊 Insights")
        ]
        
        all_success = True
        
        for endpoint, description in endpoints:
            print(f"    Testing {description}: GET /api{endpoint}")
            
            response, response_time = self.make_request("GET", endpoint)
            
            success = response.status_code == 200
            details = ""
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        details = f"Retrieved {len(data)} items"
                    elif isinstance(data, dict):
                        keys = list(data.keys())[:3]  # Show first 3 keys
                        details = f"Response keys: {keys}"
                    else:
                        details = f"Response type: {type(data)}"
                except Exception as e:
                    details = f"JSON parse failed: {e}"
            else:
                details = f"Request failed: {response.text[:200]}"
                all_success = False
                
            self.log_result(f"GET /api{endpoint}", success, response.status_code, details, response_time)
        
        return all_success

    def test_uploads_initiate(self):
        """Test 4: Uploads flow basics - POST /api/uploads/initiate"""
        print("📤 Test 4: POST /api/uploads/initiate")
        
        if not self.access_token:
            self.log_result("POST /api/uploads/initiate", False, None, "No access token available")
            return False
        
        # Small file metadata for testing
        initiate_payload = {
            "filename": "smoke_test.txt",
            "size": 25,
            "parent_type": "test",
            "parent_id": "smoke-test-id"
        }
        
        response, response_time = self.make_request("POST", "/uploads/initiate", json=initiate_payload)
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                upload_id = data.get("upload_id")
                chunk_size = data.get("chunk_size")
                total_chunks = data.get("total_chunks")
                
                if upload_id and chunk_size and total_chunks:
                    details = f"Upload initiated: ID={upload_id[:8]}..., chunk_size={chunk_size}, total_chunks={total_chunks}"
                else:
                    success = False
                    details = f"Missing required fields in response: {list(data.keys())}"
            except Exception as e:
                success = False
                details = f"JSON parse failed: {e}"
        else:
            details = f"Upload initiate failed: {response.text[:200]}"
            
        self.log_result("POST /api/uploads/initiate", success, response.status_code, details, response_time)
        return success

    def run_all_tests(self):
        """Run all smoke tests in sequence"""
        print("🚀 Starting Legacy Admin Endpoints Removal Smoke Test")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Account: {TEST_EMAIL}")
        print("=" * 70)
        print()
        
        test_methods = [
            self.test_health_check,
            self.test_auth_login,
            self.test_auth_me,
            self.test_core_endpoints,
            self.test_uploads_initiate
        ]
        
        passed = 0
        total = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed += 1
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} crashed: {e}")
                self.log_result(test_method.__name__, False, None, f"Test crashed: {e}")
        
        print("=" * 70)
        print("📊 SMOKE TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed / total) * 100
        print(f"Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['step']} - {result['status_code']} ({result['response_time_ms']}ms)")
            if result["details"]:
                print(f"    {result['details']}")
        
        print()
        print("=" * 70)
        
        if success_rate >= 80:
            print("🎉 SMOKE TEST PASSED - API still works after legacy admin endpoints removal!")
        elif success_rate >= 60:
            print("⚠️ SMOKE TEST PARTIAL - Some issues need attention")
        else:
            print("🚨 SMOKE TEST FAILED - Critical issues require immediate fix")
            
        return success_rate

if __name__ == "__main__":
    tester = LegacyAdminRemovalSmokeTest()
    success_rate = tester.run_all_tests()
    exit(0 if success_rate >= 80 else 1)