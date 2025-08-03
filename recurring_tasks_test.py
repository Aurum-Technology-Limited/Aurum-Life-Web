#!/usr/bin/env python3
"""
Focused test for Epic 2 Phase 3: Smart Recurring Tasks Backend System
Tests the complete recurring tasks functionality with proper setup
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration
BACKEND_URL = "https://0a9c9d0c-2e17-4f34-937d-e8e0fba8eec7.preview.emergentagent.com/api"

class RecurringTasksTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.test_user_email = f"recurringtest_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "RecurringTest123!"
        self.test_area_id = None
        self.test_project_id = None
        
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
        headers = {}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'response': response
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'data': {},
                'response': getattr(e, 'response', None)
            }

    def setup_test_environment(self):
        """Set up test user, area, and project for recurring tasks testing"""
        print("\n=== SETTING UP TEST ENVIRONMENT ===")
        
        # 1. Create test user
        user_data = {
            "username": f"recurringtest_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Recurring",
            "last_name": "Test",
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/register', data=user_data)
        self.log_test(
            "Setup - User Registration",
            result['success'],
            f"Created test user: {self.test_user_email}" if result['success'] else f"Failed to create user: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # 2. Login with test user
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "Setup - User Login",
            result['success'],
            f"Logged in successfully" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        self.auth_token = result['data'].get('access_token')
        
        # 3. Create test area
        area_data = {
            "name": "Recurring Tasks Test Area",
            "description": "Area for testing recurring tasks functionality",
            "icon": "🔄",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        self.log_test(
            "Setup - Area Creation",
            result['success'],
            f"Created test area: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create area: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        self.test_area_id = result['data']['id']
        
        # 4. Create test project
        project_data = {
            "area_id": self.test_area_id,
            "name": "Recurring Tasks Test Project",
            "description": "Project for testing recurring tasks functionality",
            "status": "In Progress",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        self.log_test(
            "Setup - Project Creation",
            result['success'],
            f"Created test project: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create project: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        self.test_project_id = result['data']['id']
        
        print(f"✅ Test environment ready:")
        print(f"   User: {self.test_user_email}")
        print(f"   Area: {self.test_area_id}")
        print(f"   Project: {self.test_project_id}")
        
        return True

    def test_recurring_task_models_and_enums(self):
        """Test Epic 2 Phase 3: Recurring Task Models and Enums"""
        print("\n=== RECURRING TASK MODELS AND ENUMS TESTING ===")
        
        # Test RecurrenceEnum values through API
        test_patterns = [
            {"type": "daily", "interval": 1},
            {"type": "weekly", "interval": 1, "weekdays": ["monday"]},
            {"type": "monthly", "interval": 1, "month_day": 15},
            {"type": "custom", "interval": 3, "weekdays": ["monday", "wednesday", "friday"]}
        ]
        
        for i, pattern in enumerate(test_patterns):
            task_data = {
                "name": f"Model Test Task {i+1}",
                "description": f"Testing {pattern['type']} recurrence pattern",
                "priority": "medium",
                "project_id": self.test_project_id,
                "category": "testing",
                "estimated_duration": 30,
                "recurrence_pattern": pattern
            }
            
            result = self.make_request('POST', '/recurring-tasks', data=task_data, use_auth=True)
            self.log_test(
                f"RecurrenceEnum - {pattern['type'].title()} Pattern",
                result['success'],
                f"Created {pattern['type']} recurring task successfully" if result['success'] else f"Failed to create {pattern['type']} task: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                # Verify pattern was stored correctly
                returned_pattern = result['data'].get('recurrence_pattern', {})
                self.log_test(
                    f"RecurrencePattern - {pattern['type'].title()} Validation",
                    returned_pattern.get('type') == pattern['type'],
                    f"Pattern type matches: {returned_pattern.get('type')} == {pattern['type']}"
                )
        
        # Test WeekdayEnum validation
        weekday_test_data = {
            "name": "Weekday Enum Test",
            "description": "Testing weekday enum validation",
            "priority": "low",
            "project_id": self.test_project_id,
            "category": "testing",
            "estimated_duration": 15,
            "recurrence_pattern": {
                "type": "weekly",
                "interval": 1,
                "weekdays": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            }
        }
        
        result = self.make_request('POST', '/recurring-tasks', data=weekday_test_data, use_auth=True)
        self.log_test(
            "WeekdayEnum - All Days Validation",
            result['success'],
            f"All weekdays accepted successfully" if result['success'] else f"Weekday validation failed: {result.get('error', 'Unknown error')}"
        )

    def test_recurring_tasks_api_endpoints(self):
        """Test Epic 2 Phase 3: Recurring Tasks API Endpoints"""
        print("\n=== RECURRING TASKS API ENDPOINTS TESTING ===")
        
        # Test all 6 API endpoints
        endpoints_test_data = {
            "name": "API Endpoints Test Task",
            "description": "Testing all recurring tasks API endpoints",
            "priority": "high",
            "project_id": self.test_project_id,
            "category": "api_test",
            "estimated_duration": 45,
            "recurrence_pattern": {
                "type": "weekly",
                "interval": 1,
                "weekdays": ["monday", "friday"],
                "month_day": None,
                "end_date": None,
                "max_instances": 8
            }
        }
        
        # 1. GET /api/recurring-tasks (list all user recurring tasks)
        result = self.make_request('GET', '/recurring-tasks', use_auth=True)
        self.log_test(
            "API Endpoint - GET /api/recurring-tasks",
            result['success'],
            f"List endpoint working: {len(result['data']) if result['success'] else 0} tasks" if result['success'] else f"List endpoint failed: {result.get('error', 'Unknown error')}"
        )
        
        # 2. POST /api/recurring-tasks (create new recurring task)
        result = self.make_request('POST', '/recurring-tasks', data=endpoints_test_data, use_auth=True)
        self.log_test(
            "API Endpoint - POST /api/recurring-tasks",
            result['success'],
            f"Create endpoint working: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Create endpoint failed: {result.get('error', 'Unknown error')}"
        )
        
        api_test_template_id = None
        if result['success']:
            api_test_template_id = result['data']['id']
            
            # 3. PUT /api/recurring-tasks/{id} (update recurring task)
            update_data = {
                "name": "Updated API Test Task",
                "description": "Updated via API endpoint test",
                "priority": "low"
            }
            
            result = self.make_request('PUT', f'/recurring-tasks/{api_test_template_id}', data=update_data, use_auth=True)
            self.log_test(
                "API Endpoint - PUT /api/recurring-tasks/{id}",
                result['success'],
                f"Update endpoint working" if result['success'] else f"Update endpoint failed: {result.get('error', 'Unknown error')}"
            )
            
            # 4. DELETE /api/recurring-tasks/{id} (delete recurring task)
            result = self.make_request('DELETE', f'/recurring-tasks/{api_test_template_id}', use_auth=True)
            self.log_test(
                "API Endpoint - DELETE /api/recurring-tasks/{id}",
                result['success'],
                f"Delete endpoint working" if result['success'] else f"Delete endpoint failed: {result.get('error', 'Unknown error')}"
            )
        
        # 5. POST /api/recurring-tasks/generate-instances (generate task instances)
        result = self.make_request('POST', '/recurring-tasks/generate-instances', use_auth=True)
        self.log_test(
            "API Endpoint - POST /api/recurring-tasks/generate-instances",
            result['success'],
            f"Generate instances endpoint working" if result['success'] else f"Generate endpoint failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test authentication protection on all endpoints
        endpoints_to_test = [
            ('GET', '/recurring-tasks'),
            ('POST', '/recurring-tasks'),
            ('POST', '/recurring-tasks/generate-instances')
        ]
        
        for method, endpoint in endpoints_to_test:
            result = self.make_request(method, endpoint, use_auth=False)
            self.log_test(
                f"API Authentication - {method} {endpoint}",
                not result['success'] and result['status_code'] in [401, 403],
                f"Endpoint properly protected (status: {result['status_code']})" if not result['success'] else f"Endpoint not properly protected"
            )

    def test_recurring_task_service_implementation(self):
        """Test Epic 2 Phase 3: RecurringTaskService Implementation"""
        print("\n=== RECURRINGTASKSERVICE IMPLEMENTATION TESTING ===")
        
        # Test create_recurring_task() method
        service_test_task = {
            "name": "Service Test Task",
            "description": "Testing RecurringTaskService methods",
            "priority": "high",
            "project_id": self.test_project_id,
            "category": "service_test",
            "estimated_duration": 60,
            "due_time": "11:00",
            "recurrence_pattern": {
                "type": "daily",
                "interval": 1,
                "weekdays": None,
                "month_day": None,
                "end_date": None,
                "max_instances": 5
            }
        }
        
        result = self.make_request('POST', '/recurring-tasks', data=service_test_task, use_auth=True)
        self.log_test(
            "RecurringTaskService - create_recurring_task()",
            result['success'],
            f"Service create method working: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Service create failed: {result.get('error', 'Unknown error')}"
        )
        
        service_template_id = None
        if result['success']:
            service_template_id = result['data']['id']
            
            # Test get_user_recurring_tasks() method
            result = self.make_request('GET', '/recurring-tasks', use_auth=True)
            self.log_test(
                "RecurringTaskService - get_user_recurring_tasks()",
                result['success'] and len(result['data']) > 0,
                f"Service get_user_recurring_tasks working: retrieved {len(result['data']) if result['success'] else 0} tasks" if result['success'] else f"Service get failed: {result.get('error', 'Unknown error')}"
            )
            
            # Test update_recurring_task() method
            update_data = {
                "name": "Updated Service Test Task",
                "description": "Updated via service method",
                "priority": "medium"
            }
            
            result = self.make_request('PUT', f'/recurring-tasks/{service_template_id}', data=update_data, use_auth=True)
            self.log_test(
                "RecurringTaskService - update_recurring_task()",
                result['success'],
                f"Service update method working" if result['success'] else f"Service update failed: {result.get('error', 'Unknown error')}"
            )
            
            # Test generate_task_instances() method
            result = self.make_request('POST', '/recurring-tasks/generate-instances', use_auth=True)
            self.log_test(
                "RecurringTaskService - generate_task_instances()",
                result['success'],
                f"Service generate_task_instances working" if result['success'] else f"Service generate failed: {result.get('error', 'Unknown error')}"
            )
            
            # Test _should_generate_task_today() logic by checking instances
            result = self.make_request('GET', f'/recurring-tasks/{service_template_id}/instances', use_auth=True)
            self.log_test(
                "RecurringTaskService - _should_generate_task_today() logic",
                result['success'],
                f"Task generation logic working: {len(result['data']) if result['success'] else 0} instances generated" if result['success'] else f"Generation logic test failed: {result.get('error', 'Unknown error')}"
            )
            
            # Test delete_recurring_task() method
            result = self.make_request('DELETE', f'/recurring-tasks/{service_template_id}', use_auth=True)
            self.log_test(
                "RecurringTaskService - delete_recurring_task()",
                result['success'],
                f"Service delete method working" if result['success'] else f"Service delete failed: {result.get('error', 'Unknown error')}"
            )

    def test_task_scheduling_system(self):
        """Test Epic 2 Phase 3: Task Scheduling System"""
        print("\n=== TASK SCHEDULING SYSTEM TESTING ===")
        
        # Test 1: Verify schedule library is available
        try:
            import schedule
            self.log_test(
                "Schedule Library Import",
                True,
                "Schedule library (schedule==1.2.2) successfully imported"
            )
        except ImportError as e:
            self.log_test(
                "Schedule Library Import",
                False,
                f"Schedule library import failed: {e}"
            )
            return
        
        # Test 2: Test scheduler.py file exists and is importable
        try:
            import sys
            import os
            sys.path.append('/app/backend')
            from scheduler import ScheduledJobs, setup_schedule
            self.log_test(
                "Scheduler Module Import",
                True,
                "Scheduler module successfully imported"
            )
        except ImportError as e:
            self.log_test(
                "Scheduler Module Import",
                False,
                f"Scheduler module import failed: {e}"
            )
            return
        
        # Test 3: Test scheduled job functions exist
        try:
            # Check if the scheduled job methods exist
            has_recurring_job = hasattr(ScheduledJobs, 'run_recurring_tasks_job')
            has_cleanup_job = hasattr(ScheduledJobs, 'run_daily_cleanup')
            has_setup_function = callable(setup_schedule)
            
            self.log_test(
                "Scheduler Functions Availability",
                has_recurring_job and has_cleanup_job and has_setup_function,
                f"Scheduler functions available: recurring_job={has_recurring_job}, cleanup_job={has_cleanup_job}, setup={has_setup_function}"
            )
        except Exception as e:
            self.log_test(
                "Scheduler Functions Availability",
                False,
                f"Error checking scheduler functions: {e}"
            )
        
        # Test 4: Test RecurringTaskService integration
        scheduling_test_task = {
            "name": "Scheduling Integration Test",
            "description": "Testing scheduler integration with RecurringTaskService",
            "priority": "medium",
            "project_id": self.test_project_id,
            "category": "scheduling",
            "estimated_duration": 30,
            "recurrence_pattern": {
                "type": "daily",
                "interval": 1,
                "weekdays": None,
                "month_day": None,
                "end_date": None,
                "max_instances": 3
            }
        }
        
        result = self.make_request('POST', '/recurring-tasks', data=scheduling_test_task, use_auth=True)
        self.log_test(
            "Task Scheduling - RecurringTaskService Integration",
            result['success'],
            f"Created recurring task for scheduling test: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create scheduling test task: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            template_id = result['data']['id']
            
            # Test manual trigger of task generation (simulating scheduler)
            generate_result = self.make_request('POST', '/recurring-tasks/generate-instances', use_auth=True)
            self.log_test(
                "Task Scheduling - Manual Generation Trigger",
                generate_result['success'],
                f"Manual task generation successful (simulating scheduler)" if generate_result['success'] else f"Manual generation failed: {generate_result.get('error', 'Unknown error')}"
            )
            
            # Check if instances were created
            instances_result = self.make_request('GET', f'/recurring-tasks/{template_id}/instances', use_auth=True)
            self.log_test(
                "Task Scheduling - Instance Generation Verification",
                instances_result['success'] and len(instances_result['data']) > 0,
                f"Generated {len(instances_result['data']) if instances_result['success'] else 0} task instances" if instances_result['success'] else f"Instance verification failed: {instances_result.get('error', 'Unknown error')}"
            )
        
        # Test 5: Verify requirements.txt includes schedule library
        try:
            with open('/app/backend/requirements.txt', 'r') as f:
                requirements_content = f.read()
                has_schedule = 'schedule==' in requirements_content
                
            self.log_test(
                "Requirements.txt - Schedule Library",
                has_schedule,
                f"Schedule library found in requirements.txt" if has_schedule else "Schedule library missing from requirements.txt"
            )
        except Exception as e:
            self.log_test(
                "Requirements.txt - Schedule Library",
                False,
                f"Error reading requirements.txt: {e}"
            )

    def test_comprehensive_recurring_tasks_system(self):
        """Test the complete Smart Recurring Tasks system"""
        print("\n=== COMPREHENSIVE SMART RECURRING TASKS SYSTEM TESTING ===")
        
        # Test 1: GET /api/recurring-tasks - Get user recurring tasks (initially empty)
        result = self.make_request('GET', '/recurring-tasks', use_auth=True)
        self.log_test(
            "GET Recurring Tasks - Initial State",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} recurring tasks initially" if result['success'] else f"Failed to get recurring tasks: {result.get('error', 'Unknown error')}"
        )
        
        # Test 2: POST /api/recurring-tasks - Create daily recurring task
        daily_recurring_task = {
            "name": "Daily Standup Meeting",
            "description": "Daily team standup meeting",
            "priority": "high",
            "project_id": self.test_project_id,
            "category": "work",
            "estimated_duration": 30,
            "due_time": "09:00",
            "recurrence_pattern": {
                "type": "daily",
                "interval": 1,
                "weekdays": None,
                "month_day": None,
                "end_date": None,
                "max_instances": None
            }
        }
        
        result = self.make_request('POST', '/recurring-tasks', data=daily_recurring_task, use_auth=True)
        self.log_test(
            "POST Create Daily Recurring Task",
            result['success'],
            f"Created daily recurring task: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create daily recurring task: {result.get('error', 'Unknown error')}"
        )
        
        daily_template_id = None
        if result['success']:
            daily_template_id = result['data']['id']
            
            # Verify template structure
            required_fields = ['id', 'name', 'description', 'priority', 'project_id', 'category', 'recurrence_pattern', 'is_active']
            missing_fields = [field for field in required_fields if field not in result['data']]
            
            self.log_test(
                "Daily Recurring Task - Response Structure",
                len(missing_fields) == 0,
                f"All required fields present" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
            )
        
        # Test 3: POST /api/recurring-tasks - Create weekly recurring task
        weekly_recurring_task = {
            "name": "Weekly Team Review",
            "description": "Weekly team performance review",
            "priority": "medium",
            "project_id": self.test_project_id,
            "category": "work",
            "estimated_duration": 60,
            "due_time": "14:00",
            "recurrence_pattern": {
                "type": "weekly",
                "interval": 1,
                "weekdays": ["monday", "wednesday", "friday"],
                "month_day": None,
                "end_date": None,
                "max_instances": 10
            }
        }
        
        result = self.make_request('POST', '/recurring-tasks', data=weekly_recurring_task, use_auth=True)
        self.log_test(
            "POST Create Weekly Recurring Task",
            result['success'],
            f"Created weekly recurring task: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create weekly recurring task: {result.get('error', 'Unknown error')}"
        )
        
        weekly_template_id = None
        if result['success']:
            weekly_template_id = result['data']['id']
            
            # Verify weekdays pattern
            pattern = result['data'].get('recurrence_pattern', {})
            self.log_test(
                "Weekly Recurring Task - Weekdays Pattern",
                pattern.get('weekdays') == ["monday", "wednesday", "friday"],
                f"Weekdays pattern correct: {pattern.get('weekdays')}"
            )
        
        # Test 4: POST /api/recurring-tasks - Create monthly recurring task
        monthly_recurring_task = {
            "name": "Monthly Report",
            "description": "Generate monthly performance report",
            "priority": "high",
            "project_id": self.test_project_id,
            "category": "reporting",
            "estimated_duration": 120,
            "due_time": "10:00",
            "recurrence_pattern": {
                "type": "monthly",
                "interval": 1,
                "weekdays": None,
                "month_day": 1,
                "end_date": None,
                "max_instances": 12
            }
        }
        
        result = self.make_request('POST', '/recurring-tasks', data=monthly_recurring_task, use_auth=True)
        self.log_test(
            "POST Create Monthly Recurring Task",
            result['success'],
            f"Created monthly recurring task: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create monthly recurring task: {result.get('error', 'Unknown error')}"
        )
        
        monthly_template_id = None
        if result['success']:
            monthly_template_id = result['data']['id']
            
            # Verify monthly pattern
            pattern = result['data'].get('recurrence_pattern', {})
            self.log_test(
                "Monthly Recurring Task - Month Day Pattern",
                pattern.get('month_day') == 1,
                f"Month day pattern correct: {pattern.get('month_day')}"
            )
        
        # Test 5: GET /api/recurring-tasks - Get all user recurring tasks (should now have 3)
        result = self.make_request('GET', '/recurring-tasks', use_auth=True)
        self.log_test(
            "GET Recurring Tasks - After Creation",
            result['success'] and len(result['data']) >= 3,
            f"Retrieved {len(result['data']) if result['success'] else 0} recurring tasks (should be at least 3)" if result['success'] else f"Failed to get recurring tasks: {result.get('error', 'Unknown error')}"
        )
        
        # Test 6: PUT /api/recurring-tasks/{id} - Update recurring task
        if daily_template_id:
            update_data = {
                "name": "Updated Daily Standup",
                "description": "Updated daily team standup meeting",
                "due_time": "09:30",
                "recurrence_pattern": {
                    "type": "daily",
                    "interval": 2,  # Every 2 days instead of daily
                    "weekdays": None,
                    "month_day": None,
                    "end_date": None,
                    "max_instances": None
                }
            }
            
            result = self.make_request('PUT', f'/recurring-tasks/{daily_template_id}', data=update_data, use_auth=True)
            self.log_test(
                "PUT Update Recurring Task",
                result['success'],
                f"Updated recurring task successfully" if result['success'] else f"Failed to update recurring task: {result.get('error', 'Unknown error')}"
            )
        
        # Test 7: POST /api/recurring-tasks/generate-instances - Generate task instances
        result = self.make_request('POST', '/recurring-tasks/generate-instances', use_auth=True)
        self.log_test(
            "POST Generate Recurring Task Instances",
            result['success'],
            f"Generated recurring task instances successfully" if result['success'] else f"Failed to generate instances: {result.get('error', 'Unknown error')}"
        )
        
        # Test 8: GET /api/recurring-tasks/{id}/instances - Get instances for a template
        if daily_template_id:
            result = self.make_request('GET', f'/recurring-tasks/{daily_template_id}/instances', use_auth=True)
            self.log_test(
                "GET Recurring Task Instances",
                result['success'],
                f"Retrieved {len(result['data']) if result['success'] else 0} instances for daily template" if result['success'] else f"Failed to get instances: {result.get('error', 'Unknown error')}"
            )
            
            # Test instance completion if instances exist
            if result['success'] and result['data']:
                instance_id = result['data'][0]['id']
                
                # Test 9: PUT /api/recurring-task-instances/{id}/complete - Complete instance
                complete_result = self.make_request('PUT', f'/recurring-task-instances/{instance_id}/complete', use_auth=True)
                self.log_test(
                    "PUT Complete Recurring Task Instance",
                    complete_result['success'],
                    f"Completed recurring task instance successfully" if complete_result['success'] else f"Failed to complete instance: {complete_result.get('error', 'Unknown error')}"
                )
                
                # Test 10: PUT /api/recurring-task-instances/{id}/skip - Skip instance (if we have another)
                if len(result['data']) > 1:
                    skip_instance_id = result['data'][1]['id']
                    skip_result = self.make_request('PUT', f'/recurring-task-instances/{skip_instance_id}/skip', use_auth=True)
                    self.log_test(
                        "PUT Skip Recurring Task Instance",
                        skip_result['success'],
                        f"Skipped recurring task instance successfully" if skip_result['success'] else f"Failed to skip instance: {skip_result.get('error', 'Unknown error')}"
                    )
        
        # Test 11: Test invalid project_id validation
        invalid_recurring_task = {
            "name": "Invalid Task",
            "description": "Task with invalid project",
            "priority": "low",
            "project_id": "invalid-project-id-12345",
            "category": "test",
            "estimated_duration": 15,
            "recurrence_pattern": {
                "type": "daily",
                "interval": 1
            }
        }
        
        result = self.make_request('POST', '/recurring-tasks', data=invalid_recurring_task, use_auth=True)
        self.log_test(
            "POST Create Recurring Task - Invalid Project ID",
            not result['success'] and result['status_code'] == 400,
            f"Invalid project ID properly rejected with status {result['status_code']}" if not result['success'] else "Invalid project ID was incorrectly accepted"
        )
        
        # Test 12: DELETE /api/recurring-tasks/{id} - Delete recurring task
        if monthly_template_id:
            result = self.make_request('DELETE', f'/recurring-tasks/{monthly_template_id}', use_auth=True)
            self.log_test(
                "DELETE Recurring Task",
                result['success'],
                f"Deleted recurring task successfully" if result['success'] else f"Failed to delete recurring task: {result.get('error', 'Unknown error')}"
            )

    def run_all_tests(self):
        """Run all recurring tasks tests"""
        print("🚀 STARTING EPIC 2 PHASE 3: SMART RECURRING TASKS BACKEND TESTING")
        print("=" * 80)
        
        try:
            # Setup test environment
            if not self.setup_test_environment():
                print("❌ Failed to set up test environment. Aborting tests.")
                return False
            
            # Run all recurring tasks tests
            self.test_comprehensive_recurring_tasks_system()
            self.test_recurring_task_models_and_enums()
            self.test_recurring_tasks_api_endpoints()
            self.test_recurring_task_service_implementation()
            self.test_task_scheduling_system()
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        # Print summary
        self.print_test_summary()
        
        return len([t for t in self.test_results if not t['success']]) == 0

    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🏁 EPIC 2 PHASE 3: SMART RECURRING TASKS TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"   • {test['test']}: {test['message']}")
        
        print("\n✅ EPIC 2 PHASE 3 FUNCTIONALITY STATUS:")
        
        # Check critical functionality
        critical_tests = {
            'Recurring Task Models': any('RecurrenceEnum' in t['test'] and t['success'] for t in self.test_results),
            'API Endpoints': any('API Endpoint' in t['test'] and t['success'] for t in self.test_results),
            'Service Implementation': any('RecurringTaskService' in t['test'] and t['success'] for t in self.test_results),
            'Task Scheduling': any('Task Scheduling' in t['test'] and t['success'] for t in self.test_results),
            'Instance Generation': any('Generate Recurring Task Instances' in t['test'] and t['success'] for t in self.test_results),
            'Instance Management': any('Complete Recurring Task Instance' in t['test'] and t['success'] for t in self.test_results)
        }
        
        for feature, status in critical_tests.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = RecurringTasksTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)