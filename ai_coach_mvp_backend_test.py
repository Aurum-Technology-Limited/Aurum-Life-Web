#!/usr/bin/env python3
"""
AI Coach MVP Backend Testing Suite
Tests the three core AI Coach MVP features:
1. Contextual Why Statements
2. Project Decomposition 
3. Daily Reflection & Progress Prompt
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

class AiCoachMvpTester:
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
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_feature_1_contextual_why_statements(self):
        """Test Feature 1: Contextual Why Statements"""
        print("\n🎯 TESTING FEATURE 1: CONTEXTUAL WHY STATEMENTS")
        print("=" * 60)
        
        # Test 1.1: Get why statements without specific task IDs (should get recent incomplete tasks)
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.api_base}/ai/task-why-statements",
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["why_statements", "tasks_analyzed", "vertical_alignment"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Why Statements - Response Structure", 
                        False, 
                        f"Missing required fields: {missing_fields}", 
                        response_time
                    )
                else:
                    # Validate why_statements structure
                    why_statements = data.get("why_statements", [])
                    if why_statements:
                        first_statement = why_statements[0]
                        statement_fields = ["task_id", "task_name", "why_statement", "project_connection"]
                        missing_statement_fields = [field for field in statement_fields if field not in first_statement]
                        
                        if missing_statement_fields:
                            self.log_result(
                                "Why Statements - Statement Structure", 
                                False, 
                                f"Missing statement fields: {missing_statement_fields}", 
                                response_time
                            )
                        else:
                            self.log_result(
                                "Why Statements - Basic Request", 
                                True, 
                                f"Retrieved {len(why_statements)} why statements, analyzed {data.get('tasks_analyzed', 0)} tasks", 
                                response_time
                            )
                    else:
                        self.log_result(
                            "Why Statements - Basic Request", 
                            True, 
                            "No incomplete tasks found for why statements (expected if user has no tasks)", 
                            response_time
                        )
            else:
                self.log_result(
                    "Why Statements - Basic Request", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Why Statements - Basic Request", False, f"Exception: {str(e)}")
        
        # Test 1.2: Test with specific task IDs (if we have any tasks)
        try:
            # First get user's tasks to test with specific IDs
            start_time = time.time()
            tasks_response = requests.get(
                f"{self.api_base}/tasks",
                headers=self.get_headers()
            )
            
            if tasks_response.status_code == 200:
                tasks = tasks_response.json()
                if tasks and len(tasks) > 0:
                    # Test with first task ID
                    task_id = tasks[0].get('id')
                    if task_id:
                        response = requests.get(
                            f"{self.api_base}/ai/task-why-statements?task_ids={task_id}",
                            headers=self.get_headers()
                        )
                        response_time = time.time() - start_time
                        
                        if response.status_code == 200:
                            data = response.json()
                            self.log_result(
                                "Why Statements - Specific Task ID", 
                                True, 
                                f"Retrieved why statements for specific task: {task_id}", 
                                response_time
                            )
                        else:
                            self.log_result(
                                "Why Statements - Specific Task ID", 
                                False, 
                                f"Failed with status {response.status_code}: {response.text}", 
                                response_time
                            )
                    else:
                        self.log_result("Why Statements - Specific Task ID", False, "No task ID found in tasks response")
                else:
                    self.log_result("Why Statements - Specific Task ID", True, "No tasks available to test specific task IDs")
            else:
                self.log_result("Why Statements - Specific Task ID", False, f"Could not retrieve tasks: {tasks_response.status_code}")
                
        except Exception as e:
            self.log_result("Why Statements - Specific Task ID", False, f"Exception: {str(e)}")
    
    def test_feature_2_project_decomposition(self):
        """Test Feature 2: Project Decomposition"""
        print("\n🚀 TESTING FEATURE 2: PROJECT DECOMPOSITION")
        print("=" * 60)
        
        # Test different template types
        test_cases = [
            {
                "project_name": "Learn Python Programming",
                "template_type": "learning",
                "project_description": "Master Python programming fundamentals and advanced concepts"
            },
            {
                "project_name": "Career Advancement Plan",
                "template_type": "career",
                "project_description": "Develop skills and network for next career level"
            },
            {
                "project_name": "Home Organization Project",
                "template_type": "general",
                "project_description": "Organize and declutter entire home"
            },
            {
                "project_name": "Fitness Journey",
                "template_type": "health",
                "project_description": "Improve overall health and fitness"
            },
            {
                "project_name": "Website Development",
                "template_type": "work",
                "project_description": "Build a professional portfolio website"
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
                            f"Project Decomposition - {test_case['template_type'].title()} Template", 
                            False, 
                            f"Missing required fields: {missing_fields}", 
                            response_time
                        )
                    else:
                        suggested_tasks = data.get("suggested_tasks", [])
                        if suggested_tasks and len(suggested_tasks) >= 3:
                            # Validate task structure
                            first_task = suggested_tasks[0]
                            task_fields = ["name", "priority", "estimated_duration"]
                            missing_task_fields = [field for field in task_fields if field not in first_task]
                            
                            if missing_task_fields:
                                self.log_result(
                                    f"Project Decomposition - {test_case['template_type'].title()} Template", 
                                    False, 
                                    f"Missing task fields: {missing_task_fields}", 
                                    response_time
                                )
                            else:
                                self.log_result(
                                    f"Project Decomposition - {test_case['template_type'].title()} Template", 
                                    True, 
                                    f"Generated {len(suggested_tasks)} tasks for '{test_case['project_name']}'", 
                                    response_time
                                )
                        else:
                            self.log_result(
                                f"Project Decomposition - {test_case['template_type'].title()} Template", 
                                False, 
                                f"Expected at least 3 suggested tasks, got {len(suggested_tasks)}", 
                                response_time
                            )
                else:
                    self.log_result(
                        f"Project Decomposition - {test_case['template_type'].title()} Template", 
                        False, 
                        f"Failed with status {response.status_code}: {response.text}", 
                        response_time
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Project Decomposition - {test_case['template_type'].title()} Template", 
                    False, 
                    f"Exception: {str(e)}"
                )
        
        # Test invalid template type
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/ai/decompose-project",
                json={
                    "project_name": "Test Project",
                    "template_type": "invalid_type"
                },
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                # Should default to general template
                self.log_result(
                    "Project Decomposition - Invalid Template Type", 
                    True, 
                    f"Handled invalid template type gracefully, defaulted to general template", 
                    response_time
                )
            else:
                self.log_result(
                    "Project Decomposition - Invalid Template Type", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Project Decomposition - Invalid Template Type", False, f"Exception: {str(e)}")
    
    def test_feature_3_daily_reflection(self):
        """Test Feature 3: Daily Reflection & Progress Prompt"""
        print("\n📝 TESTING FEATURE 3: DAILY REFLECTION & PROGRESS PROMPT")
        print("=" * 60)
        
        # Test 3.1: Create daily reflection
        reflection_data = {
            "reflection_text": "Today was a productive day. I completed several important tasks and made good progress on my learning goals.",
            "completion_score": 8,
            "mood": "accomplished",
            "biggest_accomplishment": "Finished the project proposal and got positive feedback",
            "challenges_faced": "Had some difficulty with time management in the afternoon",
            "tomorrow_focus": "Focus on completing the remaining tasks and starting the new project phase"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/ai/daily-reflection",
                json=reflection_data,
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["id", "user_id", "reflection_date", "reflection_text", "created_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Daily Reflection - Create", 
                        False, 
                        f"Missing required fields: {missing_fields}", 
                        response_time
                    )
                else:
                    self.log_result(
                        "Daily Reflection - Create", 
                        True, 
                        f"Created daily reflection with ID: {data.get('id')}", 
                        response_time
                    )
            else:
                self.log_result(
                    "Daily Reflection - Create", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Daily Reflection - Create", False, f"Exception: {str(e)}")
        
        # Test 3.2: Get daily reflections
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.api_base}/ai/daily-reflections?days=30",
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "reflections" in data and "count" in data:
                    reflections = data.get("reflections", [])
                    self.log_result(
                        "Daily Reflection - Get Reflections", 
                        True, 
                        f"Retrieved {len(reflections)} reflections from last 30 days", 
                        response_time
                    )
                else:
                    self.log_result(
                        "Daily Reflection - Get Reflections", 
                        False, 
                        "Missing required fields: reflections or count", 
                        response_time
                    )
            else:
                self.log_result(
                    "Daily Reflection - Get Reflections", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Daily Reflection - Get Reflections", False, f"Exception: {str(e)}")
        
        # Test 3.3: Get daily streak
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.api_base}/ai/daily-streak",
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "daily_streak" in data and "user_id" in data:
                    streak = data.get("daily_streak", 0)
                    self.log_result(
                        "Daily Reflection - Get Streak", 
                        True, 
                        f"Current daily streak: {streak} days", 
                        response_time
                    )
                else:
                    self.log_result(
                        "Daily Reflection - Get Streak", 
                        False, 
                        "Missing required fields: daily_streak or user_id", 
                        response_time
                    )
            else:
                self.log_result(
                    "Daily Reflection - Get Streak", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Daily Reflection - Get Streak", False, f"Exception: {str(e)}")
        
        # Test 3.4: Check if daily prompt should show
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.api_base}/ai/should-show-daily-prompt",
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "should_show_prompt" in data and "user_id" in data:
                    should_show = data.get("should_show_prompt", True)
                    self.log_result(
                        "Daily Reflection - Should Show Prompt", 
                        True, 
                        f"Should show daily prompt: {should_show}", 
                        response_time
                    )
                else:
                    self.log_result(
                        "Daily Reflection - Should Show Prompt", 
                        False, 
                        "Missing required fields: should_show_prompt or user_id", 
                        response_time
                    )
            else:
                self.log_result(
                    "Daily Reflection - Should Show Prompt", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Daily Reflection - Should Show Prompt", False, f"Exception: {str(e)}")
    
    def test_authentication_requirements(self):
        """Test that all endpoints require proper authentication"""
        print("\n🔐 TESTING AUTHENTICATION REQUIREMENTS")
        print("=" * 60)
        
        endpoints_to_test = [
            ("GET", "/ai/task-why-statements"),
            ("POST", "/ai/decompose-project"),
            ("POST", "/ai/daily-reflection"),
            ("GET", "/ai/daily-reflections"),
            ("GET", "/ai/daily-streak"),
            ("GET", "/ai/should-show-daily-prompt")
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
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        print("\n⚠️ TESTING ERROR HANDLING")
        print("=" * 60)
        
        # Test 1: Invalid project decomposition request
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/ai/decompose-project",
                json={},  # Missing required project_name
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code in [400, 422]:
                self.log_result(
                    "Error Handling - Missing Project Name", 
                    True, 
                    f"Properly rejected invalid request with status {response.status_code}", 
                    response_time
                )
            else:
                self.log_result(
                    "Error Handling - Missing Project Name", 
                    False, 
                    f"Should return 400/422 for missing project_name but returned {response.status_code}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Error Handling - Missing Project Name", False, f"Exception: {str(e)}")
        
        # Test 2: Invalid daily reflection request
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/ai/daily-reflection",
                json={},  # Missing required reflection_text
                headers=self.get_headers()
            )
            response_time = time.time() - start_time
            
            if response.status_code in [400, 422]:
                self.log_result(
                    "Error Handling - Missing Reflection Text", 
                    True, 
                    f"Properly rejected invalid request with status {response.status_code}", 
                    response_time
                )
            else:
                self.log_result(
                    "Error Handling - Missing Reflection Text", 
                    False, 
                    f"Should return 400/422 for missing reflection_text but returned {response.status_code}", 
                    response_time
                )
                
        except Exception as e:
            self.log_result("Error Handling - Missing Reflection Text", False, f"Exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run all AI Coach MVP tests"""
        print("🤖 AI COACH MVP COMPREHENSIVE TESTING SUITE")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test all features
        self.test_feature_1_contextual_why_statements()
        self.test_feature_2_project_decomposition()
        self.test_feature_3_daily_reflection()
        self.test_authentication_requirements()
        self.test_error_handling()
        
        # Step 3: Generate summary
        self.generate_summary()
        
        return True
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("🎯 AI COACH MVP TEST SUMMARY")
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
        
        slowest_test = max(self.test_results, key=lambda x: x["response_time_ms"])
        print(f"Slowest Test: {slowest_test['test']} ({slowest_test['response_time_ms']}ms)")
        
        print("\n" + "=" * 80)
        print(f"Testing completed at: {datetime.now().isoformat()}")
        print("=" * 80)

def main():
    """Main test execution"""
    # Use the backend URL from environment or default to localhost
    import os
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8001')
    
    tester = AiCoachMvpTester(backend_url)
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 AI Coach MVP testing completed successfully!")
    else:
        print("\n💥 AI Coach MVP testing failed!")
        exit(1)

if __name__ == "__main__":
    main()