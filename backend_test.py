#!/usr/bin/env python3
"""
Comprehensive E2E Backend Testing for AI Integration System
Tests HRM APIs, AI Coach APIs, Semantic Search, and Authentication
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class AIIntegrationTester:
    def __init__(self, base_url="https://smart-life-os.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data storage
        self.test_pillar_id = None
        self.test_area_id = None
        self.test_project_id = None
        self.test_task_id = None
        self.test_insight_id = None

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED - {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details,
            'response_data': response_data
        })

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple[bool, Dict]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            # Return success status and response data
            return response.status_code < 400, response.json() if response.content else {}
            
        except requests.exceptions.Timeout:
            return False, {"error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError:
            return False, {"error": "Invalid JSON response"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}

    def test_health_check(self):
        """Test basic API health"""
        success, response = self.make_request('GET', 'health')
        self.log_test("API Health Check", success, 
                     "" if success else response.get('error', 'Unknown error'),
                     response)
        return success

    def test_authentication(self):
        """Test authentication system"""
        # Try with a simple test user first
        test_email = "test@aurumlife.com"
        test_password = "password123"
        
        # Try login first
        login_data = {"email": test_email, "password": test_password}
        success, response = self.make_request('POST', 'auth/login', login_data)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            # Get user info from /me endpoint
            me_success, me_response = self.make_request('GET', 'auth/me')
            if me_success:
                self.user_id = me_response.get('id')
            self.log_test("User Login", True, f"User ID: {self.user_id}")
            return True
        else:
            # If login failed, try registration
            test_email = f"test_ai_integration_{int(time.time())}@example.com"
            test_password = "TestPass123!"
            test_username = f"testuser_{int(time.time())}"
            
            # Register user with correct format
            register_data = {
                "username": test_username,
                "email": test_email,
                "password": test_password,
                "first_name": "AI Integration",
                "last_name": "Test User"
            }
            
            success, response = self.make_request('POST', 'auth/register', register_data)
            if success and 'access_token' in response:
                self.token = response['access_token']
                # Get user info from /me endpoint since registration doesn't return user object
                me_success, me_response = self.make_request('GET', 'auth/me')
                if me_success:
                    self.user_id = me_response.get('id')
                self.log_test("User Registration", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Authentication", False, 
                             f"Login failed: {login_data}, Registration failed: {response.get('error', 'Unknown error')}")
                return False

    def test_basic_data_setup(self):
        """Create basic test data (pillar, area, project, task)"""
        if not self.token:
            return False
            
        # Create test pillar
        pillar_data = {
            "name": "AI Test Pillar",
            "description": "Test pillar for AI integration testing",
            "color": "#3B82F6"
        }
        success, response = self.make_request('POST', 'pillars', pillar_data)
        if success and 'id' in response:
            self.test_pillar_id = response['id']
            self.log_test("Create Test Pillar", True, f"Pillar ID: {self.test_pillar_id}")
        else:
            self.log_test("Create Test Pillar", False, response.get('error', 'Unknown error'))
            return False

        # Create test area
        area_data = {
            "name": "AI Test Area",
            "description": "Test area for AI integration testing",
            "pillar_id": self.test_pillar_id,
            "color": "#10B981"
        }
        success, response = self.make_request('POST', 'areas', area_data)
        if success and 'id' in response:
            self.test_area_id = response['id']
            self.log_test("Create Test Area", True, f"Area ID: {self.test_area_id}")
        else:
            self.log_test("Create Test Area", False, response.get('error', 'Unknown error'))
            return False

        # Create test project
        project_data = {
            "name": "AI Test Project",
            "description": "Test project for AI integration testing",
            "area_id": self.test_area_id,
            "status": "active",
            "priority": "medium"
        }
        success, response = self.make_request('POST', 'projects', project_data)
        if success and 'id' in response:
            self.test_project_id = response['id']
            self.log_test("Create Test Project", True, f"Project ID: {self.test_project_id}")
        else:
            self.log_test("Create Test Project", False, f"Error: {response}")
            return False

        # Create test task
        task_data = {
            "name": "AI Test Task",
            "description": "Test task for AI integration testing with semantic content",
            "project_id": self.test_project_id,
            "priority": "high",
            "status": "todo"
        }
        success, response = self.make_request('POST', 'tasks', task_data)
        if success and 'id' in response:
            self.test_task_id = response['id']
            self.log_test("Create Test Task", True, f"Task ID: {self.test_task_id}")
            return True
        else:
            self.log_test("Create Test Task", False, response.get('error', 'Unknown error'))
            return False

    def test_hrm_endpoints(self):
        """Test HRM (Hierarchical Reasoning Model) endpoints"""
        if not self.token or not self.test_task_id:
            self.log_test("HRM Prerequisites", False, "Missing authentication or test data")
            return False

        # Test HRM analyze endpoint
        analyze_data = {
            "entity_type": "task",
            "entity_id": self.test_task_id,
            "analysis_depth": "balanced",
            "force_llm": False
        }
        success, response = self.make_request('POST', 'hrm/analyze', analyze_data)
        if success and 'insight_id' in response:
            self.test_insight_id = response['insight_id']
            self.log_test("HRM Analyze Task", True, 
                         f"Generated insight: {response.get('title', 'N/A')}")
        else:
            self.log_test("HRM Analyze Task", False, 
                         response.get('error', 'Analysis failed'))

        # Test HRM insights endpoint
        success, response = self.make_request('GET', 'hrm/insights', params={'limit': 10})
        if success and 'insights' in response:
            insights_count = len(response['insights'])
            self.log_test("HRM Get Insights", True, f"Retrieved {insights_count} insights")
        else:
            self.log_test("HRM Get Insights", False, 
                         response.get('error', 'Failed to get insights'))

        # Test HRM statistics endpoint
        success, response = self.make_request('GET', 'hrm/statistics', params={'days': 30})
        if success and 'statistics' in response:
            self.log_test("HRM Statistics", True, "Statistics retrieved successfully")
        else:
            self.log_test("HRM Statistics", False, 
                         response.get('error', 'Failed to get statistics'))

        # Test HRM today priorities
        success, response = self.make_request('POST', 'hrm/prioritize-today', 
                                            params={'top_n': 5, 'include_reasoning': True})
        if success and 'tasks' in response:
            tasks_count = len(response['tasks'])
            self.log_test("HRM Today Priorities", True, f"Got {tasks_count} prioritized tasks")
        else:
            self.log_test("HRM Today Priorities", False, 
                         response.get('error', 'Failed to get priorities'))

        # Test HRM preferences
        success, response = self.make_request('GET', 'hrm/preferences')
        if success:
            self.log_test("HRM Get Preferences", True, "Preferences retrieved")
        else:
            self.log_test("HRM Get Preferences", False, 
                         response.get('error', 'Failed to get preferences'))

        return True

    def test_ai_coach_endpoints(self):
        """Test AI Coach endpoints"""
        if not self.token:
            self.log_test("AI Coach Prerequisites", False, "Missing authentication")
            return False

        # Test task why statements
        params = {}
        if self.test_task_id:
            params['task_ids'] = [self.test_task_id]
            
        success, response = self.make_request('GET', 'ai/task-why-statements', params=params)
        if success and 'why_statements' in response:
            statements_count = len(response['why_statements'])
            self.log_test("AI Coach Why Statements", True, 
                         f"Generated {statements_count} why statements")
        else:
            self.log_test("AI Coach Why Statements", False, 
                         response.get('error', 'Failed to generate why statements'))

        # Test suggest focus tasks
        success, response = self.make_request('GET', 'ai/suggest-focus', 
                                            params={'top_n': 5, 'include_reasoning': True})
        if success and 'tasks' in response:
            focus_tasks = len(response['tasks'])
            self.log_test("AI Coach Suggest Focus", True, 
                         f"Got {focus_tasks} focus suggestions")
        else:
            self.log_test("AI Coach Suggest Focus", False, 
                         response.get('error', 'Failed to get focus suggestions'))

        # Test alignment dashboard
        success, response = self.make_request('GET', 'alignment/dashboard')
        if success:
            self.log_test("AI Coach Alignment Dashboard", True, "Dashboard data retrieved")
        else:
            self.log_test("AI Coach Alignment Dashboard", False, 
                         response.get('error', 'Failed to get alignment data'))

        # Test today priorities enhanced
        success, response = self.make_request('GET', 'ai/today-priorities', 
                                            params={'top_n': 5, 'include_hrm': True})
        if success and 'tasks' in response:
            priority_tasks = len(response['tasks'])
            self.log_test("AI Coach Today Priorities Enhanced", True, 
                         f"Got {priority_tasks} enhanced priorities")
        else:
            self.log_test("AI Coach Today Priorities Enhanced", False, 
                         response.get('error', 'Failed to get enhanced priorities'))

        return True

    def test_semantic_search_endpoints(self):
        """Test Semantic Search endpoints"""
        if not self.token:
            self.log_test("Semantic Search Prerequisites", False, "Missing authentication")
            return False

        # Wait a moment for embeddings to be generated
        time.sleep(2)

        # Test semantic search
        search_params = {
            'query': 'AI integration testing task',
            'content_types': ['task', 'project'],
            'limit': 10,
            'min_similarity': 0.3
        }
        success, response = self.make_request('GET', 'semantic/search', params=search_params)
        if success and 'results' in response:
            results_count = len(response['results'])
            self.log_test("Semantic Search", True, 
                         f"Found {results_count} semantic matches")
        else:
            self.log_test("Semantic Search", False, 
                         response.get('error', 'Semantic search failed'))

        # Test find similar content (if we have a task)
        if self.test_task_id:
            success, response = self.make_request('GET', 
                                                f'semantic/similar/task/{self.test_task_id}',
                                                params={'limit': 5, 'min_similarity': 0.4})
            if success and 'similar_content' in response:
                similar_count = len(response['similar_content'])
                self.log_test("Semantic Find Similar", True, 
                             f"Found {similar_count} similar items")
            else:
                self.log_test("Semantic Find Similar", False, 
                             response.get('error', 'Failed to find similar content'))

        return True

    def test_basic_crud_operations(self):
        """Test basic CRUD operations to ensure core functionality"""
        if not self.token:
            return False

        # Test get pillars
        success, response = self.make_request('GET', 'pillars')
        if success and isinstance(response, list):
            self.log_test("Get Pillars", True, f"Retrieved {len(response)} pillars")
        else:
            self.log_test("Get Pillars", False, response.get('error', 'Failed to get pillars'))

        # Test get areas
        success, response = self.make_request('GET', 'areas')
        if success and isinstance(response, list):
            self.log_test("Get Areas", True, f"Retrieved {len(response)} areas")
        else:
            self.log_test("Get Areas", False, response.get('error', 'Failed to get areas'))

        # Test get projects
        success, response = self.make_request('GET', 'projects')
        if success and isinstance(response, list):
            self.log_test("Get Projects", True, f"Retrieved {len(response)} projects")
        else:
            self.log_test("Get Projects", False, response.get('error', 'Failed to get projects'))

        # Test get tasks
        success, response = self.make_request('GET', 'tasks')
        if success and isinstance(response, list):
            self.log_test("Get Tasks", True, f"Retrieved {len(response)} tasks")
        else:
            self.log_test("Get Tasks", False, response.get('error', 'Failed to get tasks'))

        # Test get insights
        success, response = self.make_request('GET', 'insights')
        if success:
            self.log_test("Get Insights", True, "Insights endpoint accessible")
        else:
            self.log_test("Get Insights", False, response.get('error', 'Failed to get insights'))

        return True

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive AI Integration Backend Testing")
        print(f"🎯 Testing against: {self.base_url}")
        print("=" * 80)

        # Core system tests
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False

        if not self.test_authentication():
            print("❌ Authentication failed - stopping tests")
            return False

        # Basic CRUD tests
        self.test_basic_crud_operations()

        # Setup test data
        if not self.test_basic_data_setup():
            print("⚠️ Test data setup failed - some AI tests may not work properly")

        # AI Integration tests
        print("\n🤖 Testing AI Integration Features...")
        self.test_hrm_endpoints()
        self.test_ai_coach_endpoints()
        self.test_semantic_search_endpoints()

        # Print final results
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run} ({success_rate:.1f}%)")
        
        # Group results by category
        categories = {
            'Core System': ['API Health Check', 'User Registration', 'User Login (Fallback)'],
            'Basic CRUD': ['Get Pillars', 'Get Areas', 'Get Projects', 'Get Tasks', 'Get Insights'],
            'Test Data Setup': ['Create Test Pillar', 'Create Test Area', 'Create Test Project', 'Create Test Task'],
            'HRM Integration': [r for r in self.test_results if 'HRM' in r['name']],
            'AI Coach': [r for r in self.test_results if 'AI Coach' in r['name']],
            'Semantic Search': [r for r in self.test_results if 'Semantic' in r['name']]
        }

        failed_tests = []
        for category, test_names in categories.items():
            if isinstance(test_names[0], str):
                # String list - find matching results
                category_results = [r for r in self.test_results if r['name'] in test_names]
            else:
                # Already filtered results
                category_results = test_names
                
            passed = sum(1 for r in category_results if r['success'])
            total = len(category_results)
            
            if total > 0:
                print(f"\n{category}: {passed}/{total} passed")
                for result in category_results:
                    if not result['success']:
                        failed_tests.append(result)
                        print(f"  ❌ {result['name']}: {result['details']}")

        if failed_tests:
            print(f"\n⚠️ FAILED TESTS DETAILS:")
            for test in failed_tests:
                print(f"❌ {test['name']}: {test['details']}")

        # Determine overall success
        critical_failures = [
            'API Health Check', 'Authentication', 'HRM Analyze Task', 
            'AI Coach Why Statements', 'Semantic Search'
        ]
        
        critical_failed = [r for r in self.test_results 
                          if not r['success'] and any(cf in r['name'] for cf in critical_failures)]
        
        if critical_failed:
            print(f"\n🚨 CRITICAL FAILURES DETECTED:")
            for test in critical_failed:
                print(f"❌ {test['name']}: {test['details']}")
            return False
        elif success_rate >= 80:
            print(f"\n🎉 AI INTEGRATION SYSTEM IS READY FOR PRODUCTION!")
            print(f"✅ {success_rate:.1f}% success rate meets requirements")
            return True
        else:
            print(f"\n⚠️ AI INTEGRATION SYSTEM NEEDS ATTENTION")
            print(f"❌ {success_rate:.1f}% success rate below 80% threshold")
            return False

def main():
    """Main test execution"""
    tester = AIIntegrationTester()
    
    try:
        success = tester.run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())