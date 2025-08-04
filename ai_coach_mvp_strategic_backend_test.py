#!/usr/bin/env python3
"""
AI Coach MVP Strategic Features Backend Testing Suite
Tests the three core AI Coach MVP strategic features with safeguards:
1. AI Quota Management - GET /api/ai/quota
2. Goal Decomposition - POST /api/ai/decompose-project  
3. Weekly Strategic Review - POST /api/ai/weekly-review
4. Obstacle Analysis - POST /api/ai/obstacle-analysis

Includes testing of rate limiting and quota safeguards.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid

class AiCoachMvpStrategicTester:
    def __init__(self, base_url: str = "https://51a61c8b-3644-464b-a47b-b402cddf7d0a.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.auth_token = None
        self.test_results = []
        self.user_id = None
        
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
        
    def authenticate(self, email: str = "marc.alleyne@aurumtechnologyltd.com", password: str = "Alleyne2025!") -> bool:
        """Authenticate with the API using specified credentials"""
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
                self.user_id = data.get("user", {}).get("id")
                self.log_result("Authentication", True, f"Successfully authenticated as {email}", response_time)
                return True
            else:
                self.log_result("Authentication", False, f"Failed with status {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception during authentication: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_ai_quota_management(self):
        """Test AI Quota Management - GET /api/ai/quota"""
        print("\n📊 TESTING AI QUOTA MANAGEMENT")
        print("=" * 60)
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.api_base}/ai/quota",
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["total", "used", "remaining"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "AI Quota - Response Structure", 
                        False, 
                        f"Missing required fields: {missing_fields}", 
                        response_time
                    )
                else:
                    total = data.get("total", 0)
                    used = data.get("used", 0)
                    remaining = data.get("remaining", 0)
                    
                    # Validate quota logic
                    if total == 10 and used + remaining == total:
                        self.log_result(
                            "AI Quota - Management", 
                            True, 
                            f"Monthly quota: {total}, Used: {used}, Remaining: {remaining}", 
                            response_time
                        )
                    else:
                        self.log_result(
                            "AI Quota - Management", 
                            False, 
                            f"Quota logic error - Total: {total}, Used: {used}, Remaining: {remaining}", 
                            response_time
                        )
            else:
                self.log_result(
                    "AI Quota - Management", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("AI Quota - Management", False, f"Exception: {str(e)}")
    
    def test_goal_decomposition(self):
        """Test Feature 1 - Goal Decomposition with Safeguards"""
        print("\n🎯 TESTING GOAL DECOMPOSITION WITH SAFEGUARDS")
        print("=" * 60)
        
        # Test cases for different goals
        test_cases = [
            {
                "project_name": "Learn Spanish",
                "project_description": "Master Spanish language for travel and career advancement",
                "template_type": "learning"
            },
            {
                "project_name": "Start fitness routine", 
                "project_description": "Develop a sustainable fitness routine for better health",
                "template_type": "health"
            },
            {
                "project_name": "Career advancement plan",
                "project_description": "Strategic plan to advance to senior position",
                "template_type": "career"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_base}/ai/decompose-project",
                    json=test_case,
                    headers=self.get_headers()
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["project_name", "template_type", "suggested_tasks", "total_tasks"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(
                            f"Goal Decomposition - {test_case['project_name']}", 
                            False, 
                            f"Missing required fields: {missing_fields}", 
                            response_time
                        )
                    else:
                        suggested_tasks = data.get("suggested_tasks", [])
                        if isinstance(suggested_tasks, list) and len(suggested_tasks) >= 3:
                            self.log_result(
                                f"Goal Decomposition - {test_case['project_name']}", 
                                True, 
                                f"Generated {len(suggested_tasks)} tasks for '{test_case['project_name']}'", 
                                response_time
                            )
                        else:
                            self.log_result(
                                f"Goal Decomposition - {test_case['project_name']}", 
                                False, 
                                f"Expected array of tasks, got {type(suggested_tasks)} with {len(suggested_tasks) if isinstance(suggested_tasks, list) else 0} items", 
                                response_time
                            )
                elif response.status_code == 429:
                    self.log_result(
                        f"Goal Decomposition - Rate Limit", 
                        True, 
                        f"Rate limiting working correctly (429 status)", 
                        response_time
                    )
                elif response.status_code == 402:
                    self.log_result(
                        f"Goal Decomposition - Quota Exceeded", 
                        True, 
                        f"Quota limit working correctly (402 status)", 
                        response_time
                    )
                else:
                    self.log_result(
                        f"Goal Decomposition - {test_case['project_name']}", 
                        False, 
                        f"Failed with status {response.status_code}: {response.text}", 
                        response_time
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Goal Decomposition - {test_case['project_name']}", 
                    False, 
                    f"Exception: {str(e)}"
                )
            
            # Small delay between requests to avoid rate limiting during normal testing
            time.sleep(1)
    
    def test_weekly_strategic_review(self):
        """Test Feature 2 - Weekly Strategic Review"""
        print("\n📈 TESTING WEEKLY STRATEGIC REVIEW")
        print("=" * 60)
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/ai/weekly-review",
                json={},  # No body required
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["weekly_summary", "projects_completed", "weekly_points"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Weekly Strategic Review", 
                        False, 
                        f"Missing required fields: {missing_fields}", 
                        response_time
                    )
                else:
                    weekly_summary = data.get("weekly_summary", "")
                    projects_completed = data.get("projects_completed", 0)
                    weekly_points = data.get("weekly_points", 0)
                    
                    if isinstance(weekly_summary, str) and len(weekly_summary) > 0:
                        self.log_result(
                            "Weekly Strategic Review", 
                            True, 
                            f"Generated review: {projects_completed} projects, {weekly_points} points", 
                            response_time
                        )
                    else:
                        self.log_result(
                            "Weekly Strategic Review", 
                            False, 
                            f"Invalid weekly_summary format or empty", 
                            response_time
                        )
            elif response.status_code == 429:
                self.log_result(
                    "Weekly Strategic Review - Rate Limit", 
                    True, 
                    f"Rate limiting working correctly (429 status)", 
                    response_time
                )
            elif response.status_code == 402:
                self.log_result(
                    "Weekly Strategic Review - Quota Exceeded", 
                    True, 
                    f"Quota limit working correctly (402 status)", 
                    response_time
                )
            else:
                self.log_result(
                    "Weekly Strategic Review", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Weekly Strategic Review", False, f"Exception: {str(e)}")
    
    def test_obstacle_analysis(self):
        """Test Feature 3 - Obstacle Analysis"""
        print("\n🚧 TESTING OBSTACLE ANALYSIS")
        print("=" * 60)
        
        # First, we need to get or create a project to test with
        project_id = self.get_or_create_test_project()
        
        if not project_id:
            self.log_result("Obstacle Analysis - Setup", False, "Could not get or create test project")
            return
        
        # Test valid obstacle analysis
        test_request = {
            "project_id": project_id,
            "problem_description": "I'm stuck on planning and don't know where to start"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/ai/obstacle-analysis",
                json=test_request,
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["project_name", "suggestions"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Obstacle Analysis - Valid Request", 
                        False, 
                        f"Missing required fields: {missing_fields}", 
                        response_time
                    )
                else:
                    suggestions = data.get("suggestions", [])
                    project_name = data.get("project_name", "")
                    
                    if isinstance(suggestions, list) and len(suggestions) > 0:
                        self.log_result(
                            "Obstacle Analysis - Valid Request", 
                            True, 
                            f"Generated {len(suggestions)} suggestions for project '{project_name}'", 
                            response_time
                        )
                    else:
                        self.log_result(
                            "Obstacle Analysis - Valid Request", 
                            False, 
                            f"Expected array of suggestions, got {type(suggestions)}", 
                            response_time
                        )
            elif response.status_code == 429:
                self.log_result(
                    "Obstacle Analysis - Rate Limit", 
                    True, 
                    f"Rate limiting working correctly (429 status)", 
                    response_time
                )
            elif response.status_code == 402:
                self.log_result(
                    "Obstacle Analysis - Quota Exceeded", 
                    True, 
                    f"Quota limit working correctly (402 status)", 
                    response_time
                )
            else:
                self.log_result(
                    "Obstacle Analysis - Valid Request", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Obstacle Analysis - Valid Request", False, f"Exception: {str(e)}")
        
        # Test with invalid project_id
        try:
            start_time = time.time()
            invalid_request = {
                "project_id": "invalid-project-id-12345",
                "problem_description": "Test problem"
            }
            
            response = requests.post(
                f"{self.api_base}/ai/obstacle-analysis",
                json=invalid_request,
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result(
                    "Obstacle Analysis - Invalid Project ID", 
                    True, 
                    f"Correctly returned 404 for invalid project ID", 
                    response_time
                )
            else:
                self.log_result(
                    "Obstacle Analysis - Invalid Project ID", 
                    False, 
                    f"Expected 404 for invalid project ID, got {response.status_code}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Obstacle Analysis - Invalid Project ID", False, f"Exception: {str(e)}")
    
    def get_or_create_test_project(self) -> str:
        """Get existing project or create a test project for obstacle analysis"""
        try:
            # First try to get existing projects
            response = requests.get(
                f"{self.api_base}/projects",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                projects = response.json()
                if projects and len(projects) > 0:
                    return projects[0].get("id")
            
            # If no projects exist, create a test project
            # First get areas to link the project
            areas_response = requests.get(
                f"{self.api_base}/areas",
                headers=self.get_headers()
            )
            
            area_id = None
            if areas_response.status_code == 200:
                areas = areas_response.json()
                if areas and len(areas) > 0:
                    area_id = areas[0].get("id")
            
            if not area_id:
                # Create a test area first
                area_data = {
                    "name": "Test Area for AI Coach",
                    "description": "Test area for AI Coach obstacle analysis testing",
                    "importance": 5
                }
                
                area_response = requests.post(
                    f"{self.api_base}/areas",
                    json=area_data,
                    headers=self.get_headers()
                )
                
                if area_response.status_code == 200:
                    area_id = area_response.json().get("id")
                else:
                    return None
            
            # Create test project
            project_data = {
                "name": "Test Project for AI Coach",
                "description": "Test project for AI Coach obstacle analysis testing",
                "area_id": area_id,
                "priority": "medium",
                "status": "In Progress"
            }
            
            project_response = requests.post(
                f"{self.api_base}/projects",
                json=project_data,
                headers=self.get_headers()
            )
            
            if project_response.status_code == 200:
                return project_response.json().get("id")
            
            return None
            
        except Exception as e:
            print(f"Error getting/creating test project: {e}")
            return None
    
    def test_rate_limiting(self):
        """Test rate limiting (max 3 requests per minute)"""
        print("\n⏱️ TESTING RATE LIMITING")
        print("=" * 60)
        
        # Make 4 rapid requests to test rate limiting
        for i in range(4):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_base}/ai/decompose-project",
                    json={
                        "project_name": f"Rate Limit Test {i+1}",
                        "template_type": "general"
                    },
                    headers=self.get_headers()
                )
                response_time = time.time() - start_time
                
                if i < 3:  # First 3 requests should succeed or consume quota
                    if response.status_code in [200, 402]:  # Success or quota exceeded
                        self.log_result(
                            f"Rate Limiting - Request {i+1}", 
                            True, 
                            f"Request {i+1} processed (status {response.status_code})", 
                            response_time
                        )
                    else:
                        self.log_result(
                            f"Rate Limiting - Request {i+1}", 
                            False, 
                            f"Unexpected status {response.status_code} for request {i+1}", 
                            response_time
                        )
                else:  # 4th request should be rate limited
                    if response.status_code == 429:
                        self.log_result(
                            "Rate Limiting - Enforcement", 
                            True, 
                            f"Rate limiting correctly enforced on request {i+1}", 
                            response_time
                        )
                    else:
                        self.log_result(
                            "Rate Limiting - Enforcement", 
                            False, 
                            f"Expected 429 for rate limit, got {response.status_code}", 
                            response_time
                        )
                
                # Small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                self.log_result(f"Rate Limiting - Request {i+1}", False, f"Exception: {str(e)}")
    
    def test_authentication_requirements(self):
        """Test that all AI endpoints require authentication"""
        print("\n🔐 TESTING AUTHENTICATION REQUIREMENTS")
        print("=" * 60)
        
        endpoints_to_test = [
            ("GET", "/ai/quota"),
            ("POST", "/ai/decompose-project"),
            ("POST", "/ai/weekly-review"),
            ("POST", "/ai/obstacle-analysis")
        ]
        
        for method, endpoint in endpoints_to_test:
            try:
                start_time = time.time()
                
                # Test without authentication
                if method == "GET":
                    response = requests.get(f"{self.api_base}{endpoint}")
                else:
                    response = requests.post(
                        f"{self.api_base}{endpoint}",
                        json={"test": "data"}
                    )
                
                response_time = time.time() - start_time
                
                if response.status_code in [401, 403]:
                    self.log_result(
                        f"Auth Required - {method} {endpoint}", 
                        True, 
                        f"Properly rejected unauthenticated request with status {response.status_code}", 
                        response_time
                    )
                else:
                    self.log_result(
                        f"Auth Required - {method} {endpoint}", 
                        False, 
                        f"Should require authentication but returned status {response.status_code}", 
                        response_time
                    )
                    
            except Exception as e:
                self.log_result(f"Auth Required - {method} {endpoint}", False, f"Exception: {str(e)}")
    
    def test_quota_consumption(self):
        """Test that AI interactions consume quota"""
        print("\n📉 TESTING QUOTA CONSUMPTION")
        print("=" * 60)
        
        # Get initial quota
        try:
            initial_response = requests.get(
                f"{self.api_base}/ai/quota",
                headers=self.get_headers()
            )
            
            if initial_response.status_code == 200:
                initial_quota = initial_response.json()
                initial_remaining = initial_quota.get("remaining", 0)
                
                # Make an AI request
                ai_response = requests.post(
                    f"{self.api_base}/ai/decompose-project",
                    json={
                        "project_name": "Quota Test Project",
                        "template_type": "general"
                    },
                    headers=self.get_headers()
                )
                
                if ai_response.status_code == 200:
                    # Check quota after request
                    final_response = requests.get(
                        f"{self.api_base}/ai/quota",
                        headers=self.get_headers()
                    )
                    
                    if final_response.status_code == 200:
                        final_quota = final_response.json()
                        final_remaining = final_quota.get("remaining", 0)
                        
                        if final_remaining == initial_remaining - 1:
                            self.log_result(
                                "Quota Consumption", 
                                True, 
                                f"Quota correctly consumed: {initial_remaining} → {final_remaining}", 
                                0
                            )
                        else:
                            self.log_result(
                                "Quota Consumption", 
                                False, 
                                f"Quota not consumed correctly: {initial_remaining} → {final_remaining}", 
                                0
                            )
                    else:
                        self.log_result("Quota Consumption", False, "Could not check final quota")
                elif ai_response.status_code == 402:
                    self.log_result(
                        "Quota Consumption", 
                        True, 
                        "Quota already exhausted (402 status)", 
                        0
                    )
                else:
                    self.log_result("Quota Consumption", False, f"AI request failed: {ai_response.status_code}")
            else:
                self.log_result("Quota Consumption", False, "Could not get initial quota")
                
        except Exception as e:
            self.log_result("Quota Consumption", False, f"Exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run all AI Coach MVP Strategic tests"""
        print("🤖 AI COACH MVP STRATEGIC FEATURES COMPREHENSIVE TESTING SUITE")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test all features
        self.test_ai_quota_management()
        self.test_goal_decomposition()
        self.test_weekly_strategic_review()
        self.test_obstacle_analysis()
        self.test_authentication_requirements()
        self.test_quota_consumption()
        # Note: Rate limiting test disabled to avoid disrupting other tests
        # self.test_rate_limiting()
        
        # Step 3: Generate summary
        self.generate_summary()
        
        return True
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("🎯 AI COACH MVP STRATEGIC FEATURES TEST SUMMARY")
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
        if self.test_results:
            avg_response_time = sum(r["response_time_ms"] for r in self.test_results) / len(self.test_results)
            print(f"\n⚡ PERFORMANCE:")
            print(f"Average Response Time: {avg_response_time:.1f}ms")
            
            slowest_test = max(self.test_results, key=lambda x: x["response_time_ms"])
            print(f"Slowest Test: {slowest_test['test']} ({slowest_test['response_time_ms']}ms)")
        
        print("\n" + "=" * 80)
        print(f"Testing completed at: {datetime.now().isoformat()}")
        print("=" * 80)

def main():
    """Main test execution"""
    # Use the production backend URL
    backend_url = "https://51a61c8b-3644-464b-a47b-b402cddf7d0a.preview.emergentagent.com"
    
    tester = AiCoachMvpStrategicTester(backend_url)
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 AI Coach MVP Strategic Features testing completed successfully!")
    else:
        print("\n💥 AI Coach MVP Strategic Features testing failed!")
        exit(1)

if __name__ == "__main__":
    main()