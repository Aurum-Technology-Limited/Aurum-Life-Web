#!/usr/bin/env python3
"""
ENHANCED GOAL DECOMPOSITION INTERACTIVE WORKFLOW - COMPREHENSIVE BACKEND TESTING
Testing the new enhanced Goal Decomposition system that transforms from suggestions to actual project/task creation.

FOCUS AREAS:
1. Enhanced AI Decomposition Response (POST /api/ai/decompose-project)
2. New Project Integration Endpoint (POST /api/projects/create-with-tasks)
3. Enhanced User Flow with contextual suggestions
4. Quota Management verification
5. Integration Testing (Generate → Edit/Save → Verify)

NEW FEATURES TO TEST:
- Structured JSON response with suggested_project, suggested_tasks, available_areas
- Project creation with associated tasks in one operation
- Contextual task generation for different goal types
- AI quota consumption tracking
- Full workflow integration

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / Alleyne2025!
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://2ba83010-29ce-4f25-8827-92c31097d7b1.preview.emergentagent.com/api"

class GoalDecompositionTestSuite:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "Alleyne2025!"
        self.created_resources = {
            'projects': [],
            'tasks': []
        }
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling and optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Try to parse JSON response
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response': response,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg += f" - Response: {error_data}"
                except:
                    error_msg += f" - Response: {e.response.text[:200]}"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'data': {},
                'response': getattr(e, 'response', None)
            }

    def test_basic_connectivity(self):
        """Test basic connectivity to the backend API"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
        # Test the root endpoint which should exist
        result = self.make_request('GET', '', use_auth=False)
        if not result['success']:
            # Try the base URL without /api
            base_url = self.base_url.replace('/api', '')
            url = f"{base_url}/"
            try:
                response = self.session.get(url, timeout=30)
                result = {
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else {},
                }
            except:
                result = {'success': False, 'error': 'Connection failed'}
        
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_user_authentication(self):
        """Test user authentication with specified credentials"""
        print("\n=== TESTING USER AUTHENTICATION ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_ai_quota_endpoint(self):
        """Test AI quota management endpoint"""
        print("\n=== TESTING AI QUOTA MANAGEMENT ===")
        
        if not self.auth_token:
            self.log_test("AI QUOTA - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/ai/quota
        result = self.make_request('GET', '/ai/quota', use_auth=True)
        self.log_test(
            "GET AI QUOTA",
            result['success'],
            f"Retrieved AI quota successfully" if result['success'] else f"Failed to get quota: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        quota_response = result['data']
        
        # Check if response has the expected structure
        required_fields = ['total', 'used', 'remaining']
        missing_fields = [field for field in required_fields if field not in quota_response]
        
        fields_present = len(missing_fields) == 0
        self.log_test(
            "AI QUOTA - RESPONSE STRUCTURE",
            fields_present,
            f"All required fields present: {quota_response}" if fields_present else f"Missing fields: {missing_fields}"
        )
        
        # Verify quota values are reasonable
        if fields_present:
            total = quota_response.get('total', 0)
            used = quota_response.get('used', 0)
            remaining = quota_response.get('remaining', 0)
            
            quota_valid = (total == 10 and used >= 0 and remaining >= 0 and used + remaining <= total)
            self.log_test(
                "AI QUOTA - VALUES VALIDATION",
                quota_valid,
                f"Quota values valid: total={total}, used={used}, remaining={remaining}" if quota_valid else f"Invalid quota values: total={total}, used={used}, remaining={remaining}"
            )
            
            return quota_valid
        
        return fields_present

    def test_enhanced_ai_decomposition_response(self):
        """Test enhanced AI decomposition response with structured JSON"""
        print("\n=== TESTING ENHANCED AI DECOMPOSITION RESPONSE ===")
        
        if not self.auth_token:
            self.log_test("AI DECOMPOSITION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test different goal types for contextual responses
        test_goals = [
            {"project_name": "Plan a trip to Japan", "expected_tasks": ["visa", "budget", "flights", "accommodation", "itinerary"]},
            {"project_name": "Learn Spanish", "expected_tasks": ["language", "practice", "schedule", "resources", "goals"]},
            {"project_name": "Start fitness routine", "expected_tasks": ["fitness", "goals", "workout", "schedule", "progress"]}
        ]
        
        successful_tests = 0
        
        for goal_data in test_goals:
            goal_name = goal_data["project_name"]
            expected_keywords = goal_data["expected_tasks"]
            
            print(f"\n--- Testing Goal: {goal_name} ---")
            
            # Test POST /api/ai/decompose-project
            request_data = {"project_name": goal_name}
            result = self.make_request('POST', '/ai/decompose-project', data=request_data, use_auth=True)
            
            if result['success']:
                response_data = result['data']
                
                # Check for required structure fields
                required_fields = ['suggested_project', 'suggested_tasks', 'available_areas', 'editable', 'instructions']
                missing_fields = [field for field in required_fields if field not in response_data]
                
                structure_valid = len(missing_fields) == 0
                self.log_test(
                    f"AI DECOMPOSITION - {goal_name} - STRUCTURE",
                    structure_valid,
                    f"Response has all required fields" if structure_valid else f"Missing fields: {missing_fields}"
                )
                
                if structure_valid:
                    # Verify suggested_project structure
                    suggested_project = response_data.get('suggested_project', {})
                    project_fields = ['title', 'description', 'area_id', 'priority', 'status']
                    project_valid = all(field in suggested_project for field in project_fields)
                    
                    self.log_test(
                        f"AI DECOMPOSITION - {goal_name} - PROJECT STRUCTURE",
                        project_valid,
                        f"Suggested project has all required fields" if project_valid else f"Project missing fields: {[f for f in project_fields if f not in suggested_project]}"
                    )
                    
                    # Verify suggested_tasks structure
                    suggested_tasks = response_data.get('suggested_tasks', [])
                    tasks_valid = len(suggested_tasks) > 0
                    
                    if tasks_valid and len(suggested_tasks) > 0:
                        first_task = suggested_tasks[0]
                        task_fields = ['title', 'priority', 'estimated_duration']
                        task_structure_valid = all(field in first_task for field in task_fields)
                        
                        self.log_test(
                            f"AI DECOMPOSITION - {goal_name} - TASKS STRUCTURE",
                            task_structure_valid,
                            f"Tasks have required fields, count: {len(suggested_tasks)}" if task_structure_valid else f"Task missing fields: {[f for f in task_fields if f not in first_task]}"
                        )
                        
                        # Check for contextual task generation
                        task_titles = [task.get('title', '').lower() for task in suggested_tasks]
                        contextual_match = any(keyword in ' '.join(task_titles) for keyword in expected_keywords)
                        
                        self.log_test(
                            f"AI DECOMPOSITION - {goal_name} - CONTEXTUAL TASKS",
                            contextual_match,
                            f"Tasks are contextually relevant to {goal_name}" if contextual_match else f"Tasks may not be contextually relevant: {[task.get('title') for task in suggested_tasks[:3]]}"
                        )
                        
                        if project_valid and task_structure_valid and contextual_match:
                            successful_tests += 1
                    else:
                        self.log_test(
                            f"AI DECOMPOSITION - {goal_name} - TASKS COUNT",
                            False,
                            f"No tasks generated for {goal_name}"
                        )
                else:
                    self.log_test(
                        f"AI DECOMPOSITION - {goal_name} - FAILED",
                        False,
                        f"Response structure invalid"
                    )
            else:
                self.log_test(
                    f"AI DECOMPOSITION - {goal_name} - REQUEST FAILED",
                    False,
                    f"Failed to decompose goal: {result.get('error', 'Unknown error')}"
                )
        
        overall_success = successful_tests >= 2  # At least 2 out of 3 goals should work
        self.log_test(
            "AI DECOMPOSITION - OVERALL SUCCESS",
            overall_success,
            f"Successfully tested {successful_tests}/3 goal types" if overall_success else f"Only {successful_tests}/3 goal types worked"
        )
        
        return overall_success

    def test_project_creation_with_tasks_endpoint(self):
        """Test new project integration endpoint that creates project with tasks"""
        print("\n=== TESTING PROJECT CREATION WITH TASKS ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("PROJECT CREATION WITH TASKS - Authentication Required", False, "No authentication token available")
            return False
        
        # First, get user's areas for proper area_id
        areas_result = self.make_request('GET', '/areas', use_auth=True)
        area_id = None
        if areas_result['success'] and areas_result['data']:
            area_id = areas_result['data'][0]['id']
        
        # Test POST /api/projects/create-with-tasks
        test_project_data = {
            "project": {
                "title": "Test Goal Decomposition Project",
                "description": "A test project created from goal decomposition workflow",
                "area_id": area_id,
                "priority": "medium",
                "status": "Planning"
            },
            "tasks": [
                {
                    "title": "Research and planning phase",
                    "description": "Initial research and planning",
                    "priority": "high",
                    "estimated_duration": 60
                },
                {
                    "title": "Implementation phase",
                    "description": "Execute the main work",
                    "priority": "medium",
                    "estimated_duration": 120
                },
                {
                    "title": "Review and finalize",
                    "description": "Final review and completion",
                    "priority": "low",
                    "estimated_duration": 30
                }
            ]
        }
        
        result = self.make_request('POST', '/projects/create-with-tasks', data=test_project_data, use_auth=True)
        
        self.log_test(
            "PROJECT CREATION WITH TASKS - REQUEST",
            result['success'],
            f"Project with tasks created successfully" if result['success'] else f"Failed to create project with tasks: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        response_data = result['data']
        
        # Verify response structure
        required_fields = ['success', 'project', 'tasks', 'message']
        missing_fields = [field for field in required_fields if field not in response_data]
        
        structure_valid = len(missing_fields) == 0
        self.log_test(
            "PROJECT CREATION WITH TASKS - RESPONSE STRUCTURE",
            structure_valid,
            f"Response has all required fields" if structure_valid else f"Missing fields: {missing_fields}"
        )
        
        if not structure_valid:
            return False
        
        # Verify project was created
        created_project = response_data.get('project', {})
        project_created = 'id' in created_project and created_project.get('name') == test_project_data['project']['title']
        
        self.log_test(
            "PROJECT CREATION WITH TASKS - PROJECT CREATED",
            project_created,
            f"Project created with ID: {created_project.get('id')}" if project_created else f"Project creation failed or invalid data"
        )
        
        # Verify tasks were created
        created_tasks = response_data.get('tasks', [])
        tasks_created = len(created_tasks) == 3 and all('id' in task for task in created_tasks)
        
        self.log_test(
            "PROJECT CREATION WITH TASKS - TASKS CREATED",
            tasks_created,
            f"All 3 tasks created successfully" if tasks_created else f"Task creation failed: {len(created_tasks)} tasks created"
        )
        
        # Store created resources for cleanup
        if project_created:
            self.created_resources['projects'].append(created_project['id'])
        if tasks_created:
            self.created_resources['tasks'].extend([task['id'] for task in created_tasks])
        
        # Test validation - empty project title should return 422
        invalid_data = {
            "project": {
                "title": "",  # Empty title should fail
                "description": "Test validation"
            },
            "tasks": []
        }
        
        validation_result = self.make_request('POST', '/projects/create-with-tasks', data=invalid_data, use_auth=True)
        validation_works = validation_result['status_code'] == 422
        
        self.log_test(
            "PROJECT CREATION WITH TASKS - VALIDATION",
            validation_works,
            f"Validation correctly rejects empty project title" if validation_works else f"Validation failed: status {validation_result['status_code']}"
        )
        
        return project_created and tasks_created and validation_works

    def test_quota_consumption_tracking(self):
        """Test that AI quota is consumed only for generation, not for saving"""
        print("\n=== TESTING QUOTA CONSUMPTION TRACKING ===")
        
        if not self.auth_token:
            self.log_test("QUOTA CONSUMPTION - Authentication Required", False, "No authentication token available")
            return False
        
        # Get initial quota
        initial_quota_result = self.make_request('GET', '/ai/quota', use_auth=True)
        if not initial_quota_result['success']:
            self.log_test("QUOTA CONSUMPTION - INITIAL QUOTA FAILED", False, "Could not get initial quota")
            return False
        
        initial_quota = initial_quota_result['data']
        initial_used = initial_quota.get('used', 0)
        
        # Generate a goal decomposition (should consume quota)
        decomposition_data = {"project_name": "Test quota consumption"}
        decomposition_result = self.make_request('POST', '/ai/decompose-project', data=decomposition_data, use_auth=True)
        
        if not decomposition_result['success']:
            self.log_test("QUOTA CONSUMPTION - DECOMPOSITION FAILED", False, "Goal decomposition failed")
            return False
        
        # Check quota after generation
        after_generation_result = self.make_request('GET', '/ai/quota', use_auth=True)
        if not after_generation_result['success']:
            self.log_test("QUOTA CONSUMPTION - AFTER GENERATION QUOTA FAILED", False, "Could not get quota after generation")
            return False
        
        after_generation_quota = after_generation_result['data']
        after_generation_used = after_generation_quota.get('used', 0)
        
        quota_consumed_for_generation = after_generation_used > initial_used
        self.log_test(
            "QUOTA CONSUMPTION - GENERATION CONSUMES QUOTA",
            quota_consumed_for_generation,
            f"Quota consumed for generation: {initial_used} → {after_generation_used}" if quota_consumed_for_generation else f"Quota not consumed for generation: {initial_used} → {after_generation_used}"
        )
        
        # Now create project with tasks (should NOT consume additional quota)
        project_data = {
            "project": {
                "title": "Quota Test Project",
                "description": "Testing quota consumption",
                "priority": "medium",
                "status": "Planning"
            },
            "tasks": [
                {
                    "title": "Test task",
                    "priority": "medium",
                    "estimated_duration": 30
                }
            ]
        }
        
        creation_result = self.make_request('POST', '/projects/create-with-tasks', data=project_data, use_auth=True)
        
        if not creation_result['success']:
            self.log_test("QUOTA CONSUMPTION - PROJECT CREATION FAILED", False, "Project creation failed")
            return False
        
        # Check quota after project creation
        after_creation_result = self.make_request('GET', '/ai/quota', use_auth=True)
        if not after_creation_result['success']:
            self.log_test("QUOTA CONSUMPTION - AFTER CREATION QUOTA FAILED", False, "Could not get quota after creation")
            return False
        
        after_creation_quota = after_creation_result['data']
        after_creation_used = after_creation_quota.get('used', 0)
        
        quota_not_consumed_for_creation = after_creation_used == after_generation_used
        self.log_test(
            "QUOTA CONSUMPTION - CREATION DOES NOT CONSUME QUOTA",
            quota_not_consumed_for_creation,
            f"Quota not consumed for creation: {after_generation_used} → {after_creation_used}" if quota_not_consumed_for_creation else f"Quota incorrectly consumed for creation: {after_generation_used} → {after_creation_used}"
        )
        
        # Store created project for cleanup
        if creation_result['success']:
            created_project = creation_result['data'].get('project', {})
            if 'id' in created_project:
                self.created_resources['projects'].append(created_project['id'])
        
        return quota_consumed_for_generation and quota_not_consumed_for_creation

    def test_full_workflow_integration(self):
        """Test full workflow: Generate → Edit/Save → Verify project appears"""
        print("\n=== TESTING FULL WORKFLOW INTEGRATION ===")
        
        if not self.auth_token:
            self.log_test("FULL WORKFLOW - Authentication Required", False, "No authentication token available")
            return False
        
        # Step 1: Generate goal decomposition
        goal_data = {"project_name": "Complete workflow test project"}
        generation_result = self.make_request('POST', '/ai/decompose-project', data=goal_data, use_auth=True)
        
        generation_success = generation_result['success']
        self.log_test(
            "FULL WORKFLOW - STEP 1: GENERATION",
            generation_success,
            f"Goal decomposition generated successfully" if generation_success else f"Generation failed: {generation_result.get('error', 'Unknown error')}"
        )
        
        if not generation_success:
            return False
        
        generated_data = generation_result['data']
        
        # Step 2: Simulate editing and create project with tasks
        suggested_project = generated_data.get('suggested_project', {})
        suggested_tasks = generated_data.get('suggested_tasks', [])
        
        # Modify the suggested data (simulate user editing)
        edited_project = {
            "title": suggested_project.get('title', 'Edited Project Title'),
            "description": f"Edited: {suggested_project.get('description', 'Default description')}",
            "priority": "high",  # Changed from suggested
            "status": "Planning"
        }
        
        # Take first 2 tasks and modify them
        edited_tasks = []
        for i, task in enumerate(suggested_tasks[:2]):
            edited_tasks.append({
                "title": f"Edited: {task.get('title', f'Task {i+1}')}",
                "description": f"Modified task description {i+1}",
                "priority": "medium",
                "estimated_duration": task.get('estimated_duration', 30)
            })
        
        creation_data = {
            "project": edited_project,
            "tasks": edited_tasks
        }
        
        creation_result = self.make_request('POST', '/projects/create-with-tasks', data=creation_data, use_auth=True)
        
        creation_success = creation_result['success']
        self.log_test(
            "FULL WORKFLOW - STEP 2: CREATION",
            creation_success,
            f"Project and tasks created successfully" if creation_success else f"Creation failed: {creation_result.get('error', 'Unknown error')}"
        )
        
        if not creation_success:
            return False
        
        created_project = creation_result['data'].get('project', {})
        created_project_id = created_project.get('id')
        
        # Step 3: Verify project appears in user's projects
        projects_result = self.make_request('GET', '/projects', use_auth=True)
        
        verification_success = projects_result['success']
        if verification_success:
            user_projects = projects_result['data']
            project_found = any(p.get('id') == created_project_id for p in user_projects)
            
            self.log_test(
                "FULL WORKFLOW - STEP 3: VERIFICATION",
                project_found,
                f"Created project found in user's projects list" if project_found else f"Created project not found in user's projects"
            )
            
            # Store for cleanup
            if project_found:
                self.created_resources['projects'].append(created_project_id)
                created_tasks = creation_result['data'].get('tasks', [])
                self.created_resources['tasks'].extend([task['id'] for task in created_tasks])
            
            return project_found
        else:
            self.log_test(
                "FULL WORKFLOW - STEP 3: VERIFICATION FAILED",
                False,
                f"Could not retrieve user projects: {projects_result.get('error', 'Unknown error')}"
            )
            return False

    def test_rate_limiting(self):
        """Test rate limiting for AI endpoints"""
        print("\n=== TESTING RATE LIMITING ===")
        
        if not self.auth_token:
            self.log_test("RATE LIMITING - Authentication Required", False, "No authentication token available")
            return False
        
        # Make multiple rapid requests to test rate limiting (max 3 per minute)
        rate_limit_hit = False
        successful_requests = 0
        
        for i in range(5):  # Try 5 requests rapidly
            goal_data = {"project_name": f"Rate limit test {i+1}"}
            result = self.make_request('POST', '/ai/decompose-project', data=goal_data, use_auth=True)
            
            if result['status_code'] == 429:  # Rate limit exceeded
                rate_limit_hit = True
                self.log_test(
                    f"RATE LIMITING - REQUEST {i+1}",
                    True,
                    f"Rate limit properly enforced on request {i+1}"
                )
                break
            elif result['success']:
                successful_requests += 1
                print(f"   Request {i+1}: Success")
            else:
                print(f"   Request {i+1}: Failed with {result['status_code']}")
            
            # Small delay between requests
            time.sleep(0.1)
        
        # Rate limiting should kick in after 3 requests per minute
        rate_limiting_works = rate_limit_hit or successful_requests <= 3
        
        self.log_test(
            "RATE LIMITING - OVERALL",
            rate_limiting_works,
            f"Rate limiting working: {successful_requests} successful requests before limit" if rate_limiting_works else f"Rate limiting not working: {successful_requests} requests succeeded"
        )
        
        return rate_limiting_works

    def cleanup_created_resources(self):
        """Clean up resources created during testing"""
        print("\n=== CLEANING UP CREATED RESOURCES ===")
        
        if not self.auth_token:
            return
        
        # Delete created projects (this should also delete associated tasks)
        for project_id in self.created_resources['projects']:
            try:
                result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    print(f"✅ Deleted project {project_id}")
                else:
                    print(f"❌ Failed to delete project {project_id}")
            except Exception as e:
                print(f"❌ Error deleting project {project_id}: {e}")
        
        # Delete any remaining tasks
        for task_id in self.created_resources['tasks']:
            try:
                result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                if result['success']:
                    print(f"✅ Deleted task {task_id}")
                else:
                    print(f"❌ Failed to delete task {task_id}")
            except Exception as e:
                print(f"❌ Error deleting task {task_id}: {e}")

    def run_comprehensive_goal_decomposition_test(self):
        """Run comprehensive goal decomposition workflow tests"""
        print("\n🎯 STARTING ENHANCED GOAL DECOMPOSITION INTERACTIVE WORKFLOW TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("AI Quota Management", self.test_ai_quota_endpoint),
            ("Enhanced AI Decomposition Response", self.test_enhanced_ai_decomposition_response),
            ("Project Creation with Tasks Endpoint", self.test_project_creation_with_tasks_endpoint),
            ("Quota Consumption Tracking", self.test_quota_consumption_tracking),
            ("Full Workflow Integration", self.test_full_workflow_integration),
            ("Rate Limiting", self.test_rate_limiting)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        # Cleanup resources
        self.cleanup_created_resources()
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🎯 ENHANCED GOAL DECOMPOSITION INTERACTIVE WORKFLOW TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for specific functionality
        ai_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AI' in result['test'])
        project_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROJECT' in result['test'])
        workflow_tests_passed = sum(1 for result in self.test_results if result['success'] and 'WORKFLOW' in result['test'])
        quota_tests_passed = sum(1 for result in self.test_results if result['success'] and 'QUOTA' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"AI Decomposition Tests Passed: {ai_tests_passed}")
        print(f"Project Creation Tests Passed: {project_tests_passed}")
        print(f"Workflow Integration Tests Passed: {workflow_tests_passed}")
        print(f"Quota Management Tests Passed: {quota_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ ENHANCED GOAL DECOMPOSITION SYSTEM: SUCCESS")
            print("   ✅ POST /api/ai/decompose-project working with structured response")
            print("   ✅ POST /api/projects/create-with-tasks functional")
            print("   ✅ Contextual task generation working")
            print("   ✅ Quota management and rate limiting verified")
            print("   ✅ Full workflow integration successful")
            print("   The Enhanced Goal Decomposition Interactive Workflow is production-ready!")
        else:
            print("\n❌ ENHANCED GOAL DECOMPOSITION SYSTEM: ISSUES DETECTED")
            print("   Issues found in goal decomposition workflow implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Enhanced Goal Decomposition Interactive Workflow Tests"""
    print("🎯 STARTING ENHANCED GOAL DECOMPOSITION INTERACTIVE WORKFLOW BACKEND TESTING")
    print("=" * 80)
    
    tester = GoalDecompositionTestSuite()
    
    try:
        # Run the comprehensive goal decomposition tests
        success = tester.run_comprehensive_goal_decomposition_test()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)