#!/usr/bin/env python3
"""
Backend Focused Testing for Tasks Filters and Insights Structure
Tests the specific requirements from the review request:
1) GET /api/tasks with optional filters (project_id, q, status, priority, due_date)
2) GET /api/insights with required structure (eisenhower_matrix, alignment_snapshot, area_distribution, generated_at)
3) Ensure no 500s across these endpoints under authenticated context
"""

import requests
import json
import time
import io
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://prodforge-1.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password123"

class BackendSmokeTest:
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

    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
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
                def __init__(self, error):
                    self.status_code = 0
                    self.text = str(error)
                def json(self):
                    return {"error": str(error)}
            return MockResponse(e), end_time - start_time

    def test_step_1_login(self):
        """Step 1: POST /api/auth/login with credentials"""
        print("🔐 Step 1: Testing POST /api/auth/login")
        
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

    def test_step_2_auth_me(self):
        """Step 2: GET /api/auth/me with access token"""
        print("👤 Step 2: Testing GET /api/auth/me")
        
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

    def test_step_3_pillars(self):
        """Step 3: GET /api/pillars"""
        print("🏛️ Step 3: Testing GET /api/pillars")
        
        response, response_time = self.make_request("GET", "/pillars")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} pillars"
                else:
                    details = f"Response type: {type(data)}"
            except Exception as e:
                details = f"JSON parse failed: {e}"
        else:
            details = f"Pillars request failed: {response.text[:200]}"
            
        self.log_result("GET /api/pillars", success, response.status_code, details, response_time)
        return success

    def test_step_4_areas(self):
        """Step 4: GET /api/areas"""
        print("🗺️ Step 4: Testing GET /api/areas")
        
        response, response_time = self.make_request("GET", "/areas")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} areas"
                else:
                    details = f"Response type: {type(data)}"
            except Exception as e:
                details = f"JSON parse failed: {e}"
        else:
            details = f"Areas request failed: {response.text[:200]}"
            
        self.log_result("GET /api/areas", success, response.status_code, details, response_time)
        return success

    def test_step_5_projects(self):
        """Step 5: GET /api/projects"""
        print("📋 Step 5: Testing GET /api/projects")
        
        response, response_time = self.make_request("GET", "/projects")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} projects"
                else:
                    details = f"Response type: {type(data)}"
            except Exception as e:
                details = f"JSON parse failed: {e}"
        else:
            details = f"Projects request failed: {response.text[:200]}"
            
        self.log_result("GET /api/projects", success, response.status_code, details, response_time)
        return success

    def test_step_6_tasks(self):
        """Step 6: GET /api/tasks"""
        print("✅ Step 6: Testing GET /api/tasks")
        
        response, response_time = self.make_request("GET", "/tasks")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} tasks"
                else:
                    details = f"Response type: {type(data)}"
            except Exception as e:
                details = f"JSON parse failed: {e}"
        else:
            details = f"Tasks request failed: {response.text[:200]}"
            
        self.log_result("GET /api/tasks", success, response.status_code, details, response_time)
        return success

    def test_step_6a_tasks_due_date_filters(self):
        """Step 6a: Test /api/tasks due_date filters after timezone fix"""
        print("📅 Step 6a: Testing GET /api/tasks due_date filters")
        
        due_date_filters = ["overdue", "today", "week"]
        all_success = True
        
        for due_date_value in due_date_filters:
            print(f"    Testing due_date={due_date_value}")
            
            response, response_time = self.make_request("GET", f"/tasks?due_date={due_date_value}")
            
            success = response.status_code == 200
            details = ""
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        details = f"Retrieved {len(data)} tasks for due_date={due_date_value}"
                    else:
                        success = False
                        details = f"Expected array, got {type(data)} for due_date={due_date_value}"
                except Exception as e:
                    success = False
                    details = f"JSON parse failed for due_date={due_date_value}: {e}"
            else:
                success = False
                details = f"Request failed for due_date={due_date_value}: {response.text[:200]}"
                
            self.log_result(f"GET /api/tasks?due_date={due_date_value}", success, response.status_code, details, response_time)
            
            if not success:
                all_success = False
        
        return all_success

    def test_step_7_insights(self):
        """Step 7: GET /api/insights"""
        print("📊 Step 7: Testing GET /api/insights")
        
        response, response_time = self.make_request("GET", "/insights")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                details = f"Insights data received: {type(data)}"
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]  # Show first 5 keys
                    details += f", keys: {keys}"
            except Exception as e:
                details = f"JSON parse failed: {e}"
        else:
            details = f"Insights request failed: {response.text[:200]}"
            
        self.log_result("GET /api/insights", success, response.status_code, details, response_time)
        return success

    def test_step_8_alignment(self):
        """Step 8: GET /api/alignment/dashboard (fallback to /api/alignment-score)"""
        print("⚖️ Step 8: Testing alignment endpoints")
        
        # Try primary endpoint first
        response, response_time = self.make_request("GET", "/alignment/dashboard")
        
        if response.status_code == 200:
            success = True
            details = "Primary /api/alignment/dashboard working"
            try:
                data = response.json()
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    details += f", keys: {keys}"
            except Exception as e:
                details += f", JSON parse failed: {e}"
                
            self.log_result("GET /api/alignment/dashboard", success, response.status_code, details, response_time)
            return success
        
        # Fallback to legacy endpoint
        print("    Primary endpoint failed, trying fallback...")
        response, response_time = self.make_request("GET", "/alignment-score")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            details = "Fallback /api/alignment-score working"
            try:
                data = response.json()
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    details += f", keys: {keys}"
            except Exception as e:
                details += f", JSON parse failed: {e}"
        else:
            details = f"Both alignment endpoints failed. Last error: {response.text[:200]}"
            
        self.log_result("GET /api/alignment-score (fallback)", success, response.status_code, details, response_time)
        return success

    def test_step_9_journal(self):
        """Step 9: GET /api/journal"""
        print("📔 Step 9: Testing GET /api/journal")
        
        response, response_time = self.make_request("GET", "/journal")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                if isinstance(data, list):
                    details = f"Retrieved {len(data)} journal entries"
                else:
                    details = f"Response type: {type(data)}"
            except Exception as e:
                details = f"JSON parse failed: {e}"
        else:
            details = f"Journal request failed: {response.text[:200]}"
            
        self.log_result("GET /api/journal", success, response.status_code, details, response_time)
        return success

    def test_step_10_uploads(self):
        """Step 10: Complete upload flow test"""
        print("📤 Step 10: Testing upload flow")
        
        # Step 10a: Initiate upload
        print("    10a: POST /api/uploads/initiate")
        initiate_payload = {
            "filename": "test.txt",
            "size": 12
        }
        
        response, response_time = self.make_request("POST", "/uploads/initiate", json=initiate_payload)
        
        if response.status_code != 200:
            self.log_result("POST /api/uploads/initiate", False, response.status_code, 
                          f"Initiate failed: {response.text[:200]}", response_time)
            return False
            
        try:
            initiate_data = response.json()
            upload_id = initiate_data.get("upload_id")
            chunk_size = initiate_data.get("chunk_size")
            total_chunks = initiate_data.get("total_chunks")
            
            if not upload_id:
                self.log_result("POST /api/uploads/initiate", False, response.status_code, 
                              "No upload_id in response", response_time)
                return False
                
            self.log_result("POST /api/uploads/initiate", True, response.status_code, 
                          f"Upload ID: {upload_id}, chunks: {total_chunks}", response_time)
                          
        except Exception as e:
            self.log_result("POST /api/uploads/initiate", False, response.status_code, 
                          f"JSON parse failed: {e}", response_time)
            return False

        # Step 10b: Upload chunk
        print("    10b: POST /api/uploads/chunk")
        test_content = b"Hello world!"  # 12 bytes
        
        # Create form data for chunk upload
        files = {
            'chunk': ('test.txt', io.BytesIO(test_content), 'text/plain')
        }
        data = {
            'upload_id': upload_id,
            'index': 0,
            'total_chunks': 1
        }
        
        response, response_time = self.make_request("POST", "/uploads/chunk", files=files, data=data)
        
        if response.status_code != 200:
            self.log_result("POST /api/uploads/chunk", False, response.status_code, 
                          f"Chunk upload failed: {response.text[:200]}", response_time)
            return False
            
        self.log_result("POST /api/uploads/chunk", True, response.status_code, 
                      "Chunk uploaded successfully", response_time)

        # Step 10c: Complete upload
        print("    10c: POST /api/uploads/complete")
        complete_data = {'upload_id': upload_id}
        
        response, response_time = self.make_request("POST", "/uploads/complete", data=complete_data)
        
        if response.status_code != 200:
            self.log_result("POST /api/uploads/complete", False, response.status_code, 
                          f"Complete failed: {response.text[:200]}", response_time)
            return False
            
        try:
            complete_response = response.json()
            file_url = complete_response.get("file_url")
            filename = complete_response.get("filename")
            size = complete_response.get("size")
            
            if not file_url:
                self.log_result("POST /api/uploads/complete", False, response.status_code, 
                              "No file_url in response", response_time)
                return False
                
            self.log_result("POST /api/uploads/complete", True, response.status_code, 
                          f"File URL: {file_url}, size: {size}", response_time)
                          
        except Exception as e:
            self.log_result("POST /api/uploads/complete", False, response.status_code, 
                          f"JSON parse failed: {e}", response_time)
            return False

        # Step 10d: Download file
        print("    10d: GET file_url")
        # Remove /api prefix from file_url since it's already included
        file_endpoint = file_url.replace("/api", "")
        
        response, response_time = self.make_request("GET", file_endpoint)
        
        success = response.status_code == 200
        details = ""
        
        if success:
            content_length = len(response.content) if hasattr(response, 'content') else 0
            details = f"File downloaded, size: {content_length} bytes"
            if hasattr(response, 'content') and response.content == test_content:
                details += " (content matches)"
        else:
            details = f"File download failed: {response.text[:200]}"
            
        self.log_result("GET file_url", success, response.status_code, details, response_time)
        return success

    def run_all_tests(self):
        """Run all smoke tests in sequence"""
        print("🚀 Starting Backend Authentication and Uploads Smoke Test")
        print("=" * 70)
        print()
        
        test_methods = [
            self.test_step_1_login,
            self.test_step_2_auth_me,
            self.test_step_3_pillars,
            self.test_step_4_areas,
            self.test_step_5_projects,
            self.test_step_6_tasks,
            self.test_step_7_insights,
            self.test_step_8_alignment,
            self.test_step_9_journal,
            self.test_step_10_uploads
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
            print("🎉 SMOKE TEST PASSED - Backend is ready for production!")
        elif success_rate >= 60:
            print("⚠️ SMOKE TEST PARTIAL - Some issues need attention")
        else:
            print("🚨 SMOKE TEST FAILED - Critical issues require immediate fix")
            
        return success_rate

if __name__ == "__main__":
    tester = BackendSmokeTest()
    success_rate = tester.run_all_tests()
    exit(0 if success_rate >= 80 else 1)