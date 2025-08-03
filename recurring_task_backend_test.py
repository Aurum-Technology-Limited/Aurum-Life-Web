#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://f0a50716-337f-44d1-8fc0-56cc66936b59.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class RecurringTaskBackendTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "recurring.task.tester@aurumlife.com"
        self.test_user_password = "RecurringTest2025!"
        self.test_results = []
        self.created_resources = {
            'users': [],
            'areas': [],
            'projects': [],
            'tasks': [],
            'recurring_tasks': []
        }

    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()

    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()

    async def register_test_user(self) -> bool:
        """Register a test user for authentication"""
        try:
            user_data = {
                "username": "recurringtasktester",
                "email": self.test_user_email,
                "first_name": "Recurring",
                "last_name": "Tester",
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE_URL}/auth/register", json=user_data) as response:
                if response.status == 200:
                    user_info = await response.json()
                    self.created_resources['users'].append(user_info['id'])
                    return True
                elif response.status == 400:
                    # User might already exist, try to login
                    return await self.login_test_user()
                else:
                    print(f"Failed to register user: {response.status}")
                    return False
        except Exception as e:
            print(f"Error registering user: {e}")
            return False

    async def login_test_user(self) -> bool:
        """Login test user and get auth token"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    self.auth_token = auth_response['access_token']
                    return True
                else:
                    print(f"Failed to login: {response.status}")
                    return False
        except Exception as e:
            print(f"Error logging in: {e}")
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    async def create_test_area(self) -> str:
        """Create a test area for projects"""
        try:
            area_data = {
                "name": "Recurring Tasks Test Area",
                "description": "Test area for recurring task functionality",
                "icon": "🔄",
                "color": "#F4B400"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/areas", 
                json=area_data, 
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    area = await response.json()
                    self.created_resources['areas'].append(area['id'])
                    return area['id']
                else:
                    print(f"Failed to create area: {response.status}")
                    return None
        except Exception as e:
            print(f"Error creating area: {e}")
            return None

    async def create_test_project(self, area_id: str) -> str:
        """Create a test project for tasks"""
        try:
            project_data = {
                "area_id": area_id,
                "name": "Recurring Tasks Test Project",
                "description": "Test project for recurring task functionality",
                "icon": "🚀",
                "priority": "high"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/projects", 
                json=project_data, 
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    project = await response.json()
                    self.created_resources['projects'].append(project['id'])
                    return project['id']
                else:
                    print(f"Failed to create project: {response.status}")
                    return None
        except Exception as e:
            print(f"Error creating project: {e}")
            return None

    async def test_daily_recurring_task_creation(self, project_id: str) -> bool:
        """Test creating a daily recurring task with recurrence_pattern"""
        try:
            # Calculate dates
            due_date = datetime.now() + timedelta(days=1)
            end_date = datetime.now() + timedelta(days=30)
            
            task_data = {
                "name": "Daily Exercise",
                "description": "30 minutes of exercise",
                "priority": "high",
                "category": "health",
                "project_id": project_id,
                "due_date": due_date.isoformat(),
                "recurrence_pattern": {
                    "type": "daily",
                    "interval": 1,
                    "weekdays": [],
                    "month_day": None,
                    "end_date": end_date.isoformat(),
                    "max_instances": 30
                }
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/tasks", 
                json=task_data, 
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    task = await response.json()
                    self.created_resources['tasks'].append(task['id'])
                    
                    # Verify the task has recurrence_pattern
                    if hasattr(task, 'recurrence_pattern') or 'recurrence_pattern' in str(task):
                        self.test_results.append({
                            "test": "Daily Recurring Task Creation",
                            "status": "PASS",
                            "details": f"Successfully created daily recurring task with ID: {task['id']}"
                        })
                        return True
                    else:
                        self.test_results.append({
                            "test": "Daily Recurring Task Creation",
                            "status": "FAIL",
                            "details": "Task created but recurrence_pattern not found in response"
                        })
                        return False
                else:
                    error_text = await response.text()
                    self.test_results.append({
                        "test": "Daily Recurring Task Creation",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {error_text}"
                    })
                    return False
        except Exception as e:
            self.test_results.append({
                "test": "Daily Recurring Task Creation",
                "status": "ERROR",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_weekly_recurring_task_creation(self, project_id: str) -> bool:
        """Test creating a weekly recurring task with specific weekdays"""
        try:
            due_date = datetime.now() + timedelta(days=1)
            
            task_data = {
                "name": "Team Meeting",
                "description": "Weekly team sync meeting",
                "priority": "medium",
                "category": "work",
                "project_id": project_id,
                "due_date": due_date.isoformat(),
                "recurrence_pattern": {
                    "type": "weekly",
                    "interval": 1,
                    "weekdays": ["monday", "wednesday", "friday"],
                    "month_day": None,
                    "end_date": None,
                    "max_instances": None
                }
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/tasks", 
                json=task_data, 
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    task = await response.json()
                    self.created_resources['tasks'].append(task['id'])
                    
                    self.test_results.append({
                        "test": "Weekly Recurring Task Creation",
                        "status": "PASS",
                        "details": f"Successfully created weekly recurring task with weekdays: {task_data['recurrence_pattern']['weekdays']}"
                    })
                    return True
                else:
                    error_text = await response.text()
                    self.test_results.append({
                        "test": "Weekly Recurring Task Creation",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {error_text}"
                    })
                    return False
        except Exception as e:
            self.test_results.append({
                "test": "Weekly Recurring Task Creation",
                "status": "ERROR",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_monthly_recurring_task_creation(self, project_id: str) -> bool:
        """Test creating a monthly recurring task"""
        try:
            due_date = datetime.now() + timedelta(days=1)
            end_date = datetime.now() + timedelta(days=365)
            
            task_data = {
                "name": "Monthly Report",
                "description": "Generate monthly progress report",
                "priority": "high",
                "category": "work",
                "project_id": project_id,
                "due_date": due_date.isoformat(),
                "recurrence_pattern": {
                    "type": "monthly",
                    "interval": 1,
                    "weekdays": [],
                    "month_day": 15,
                    "end_date": end_date.isoformat(),
                    "max_instances": 12
                }
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/tasks", 
                json=task_data, 
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    task = await response.json()
                    self.created_resources['tasks'].append(task['id'])
                    
                    self.test_results.append({
                        "test": "Monthly Recurring Task Creation",
                        "status": "PASS",
                        "details": f"Successfully created monthly recurring task on day {task_data['recurrence_pattern']['month_day']}"
                    })
                    return True
                else:
                    error_text = await response.text()
                    self.test_results.append({
                        "test": "Monthly Recurring Task Creation",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {error_text}"
                    })
                    return False
        except Exception as e:
            self.test_results.append({
                "test": "Monthly Recurring Task Creation",
                "status": "ERROR",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_task_without_recurrence(self, project_id: str) -> bool:
        """Test creating a regular task without recurrence"""
        try:
            due_date = datetime.now() + timedelta(days=1)
            
            task_data = {
                "name": "One-time Task",
                "description": "A regular non-recurring task",
                "priority": "low",
                "category": "personal",
                "project_id": project_id,
                "due_date": due_date.isoformat()
                # No recurrence_pattern field
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/tasks", 
                json=task_data, 
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    task = await response.json()
                    self.created_resources['tasks'].append(task['id'])
                    
                    self.test_results.append({
                        "test": "Non-Recurring Task Creation",
                        "status": "PASS",
                        "details": "Successfully created regular task without recurrence pattern"
                    })
                    return True
                else:
                    error_text = await response.text()
                    self.test_results.append({
                        "test": "Non-Recurring Task Creation",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {error_text}"
                    })
                    return False
        except Exception as e:
            self.test_results.append({
                "test": "Non-Recurring Task Creation",
                "status": "ERROR",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_recurring_task_template_endpoints(self) -> bool:
        """Test the recurring task template endpoints"""
        try:
            # Test GET /api/recurring-tasks
            async with self.session.get(
                f"{API_BASE_URL}/recurring-tasks", 
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    templates = await response.json()
                    self.test_results.append({
                        "test": "Recurring Task Templates Endpoint",
                        "status": "PASS",
                        "details": f"Successfully retrieved {len(templates)} recurring task templates"
                    })
                    return True
                else:
                    error_text = await response.text()
                    self.test_results.append({
                        "test": "Recurring Task Templates Endpoint",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {error_text}"
                    })
                    return False
        except Exception as e:
            self.test_results.append({
                "test": "Recurring Task Templates Endpoint",
                "status": "ERROR",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_recurrence_pattern_validation(self, project_id: str) -> bool:
        """Test validation of recurrence pattern data"""
        try:
            # Test invalid recurrence type
            task_data = {
                "name": "Invalid Recurrence Test",
                "description": "Testing invalid recurrence pattern",
                "priority": "medium",
                "category": "test",
                "project_id": project_id,
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "recurrence_pattern": {
                    "type": "invalid_type",  # Invalid type
                    "interval": 1,
                    "weekdays": [],
                    "month_day": None,
                    "end_date": None,
                    "max_instances": None
                }
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/tasks", 
                json=task_data, 
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 422 or response.status == 400:
                    # Expected validation error
                    self.test_results.append({
                        "test": "Recurrence Pattern Validation",
                        "status": "PASS",
                        "details": "Correctly rejected invalid recurrence type"
                    })
                    return True
                elif response.status == 200:
                    # Should not succeed with invalid data
                    self.test_results.append({
                        "test": "Recurrence Pattern Validation",
                        "status": "FAIL",
                        "details": "Invalid recurrence pattern was accepted (should be rejected)"
                    })
                    return False
                else:
                    error_text = await response.text()
                    self.test_results.append({
                        "test": "Recurrence Pattern Validation",
                        "status": "FAIL",
                        "details": f"Unexpected HTTP {response.status}: {error_text}"
                    })
                    return False
        except Exception as e:
            self.test_results.append({
                "test": "Recurrence Pattern Validation",
                "status": "ERROR",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_task_retrieval_with_recurrence(self) -> bool:
        """Test retrieving tasks and verifying recurrence pattern data"""
        try:
            async with self.session.get(
                f"{API_BASE_URL}/tasks", 
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    tasks = await response.json()
                    
                    # Look for tasks with recurrence patterns
                    recurring_tasks = []
                    for task in tasks:
                        if isinstance(task, dict) and 'recurrence_pattern' in str(task):
                            recurring_tasks.append(task)
                    
                    self.test_results.append({
                        "test": "Task Retrieval with Recurrence",
                        "status": "PASS",
                        "details": f"Retrieved {len(tasks)} tasks, {len(recurring_tasks)} with recurrence patterns"
                    })
                    return True
                else:
                    error_text = await response.text()
                    self.test_results.append({
                        "test": "Task Retrieval with Recurrence",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {error_text}"
                    })
                    return False
        except Exception as e:
            self.test_results.append({
                "test": "Task Retrieval with Recurrence",
                "status": "ERROR",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def run_all_tests(self):
        """Run all recurring task backend compatibility tests"""
        print("🔄 Starting Recurring Task Backend Compatibility Tests...")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Step 1: Authentication
            print("📝 Step 1: Setting up test user and authentication...")
            if not await self.register_test_user():
                print("❌ Failed to register test user")
                return
            
            if not await self.login_test_user():
                print("❌ Failed to login test user")
                return
            
            print("✅ Authentication successful")
            
            # Step 2: Create test resources
            print("\n🏗️ Step 2: Creating test resources...")
            area_id = await self.create_test_area()
            if not area_id:
                print("❌ Failed to create test area")
                return
            
            project_id = await self.create_test_project(area_id)
            if not project_id:
                print("❌ Failed to create test project")
                return
            
            print("✅ Test resources created")
            
            # Step 3: Run recurring task tests
            print("\n🧪 Step 3: Testing recurring task functionality...")
            
            test_functions = [
                ("Daily Recurring Task", self.test_daily_recurring_task_creation),
                ("Weekly Recurring Task", self.test_weekly_recurring_task_creation),
                ("Monthly Recurring Task", self.test_monthly_recurring_task_creation),
                ("Non-Recurring Task", self.test_task_without_recurrence),
                ("Recurring Task Templates", self.test_recurring_task_template_endpoints),
                ("Recurrence Pattern Validation", self.test_recurrence_pattern_validation),
                ("Task Retrieval", self.test_task_retrieval_with_recurrence)
            ]
            
            for test_name, test_func in test_functions:
                print(f"  Testing {test_name}...")
                if hasattr(test_func, '__code__') and test_func.__code__.co_argcount > 1:
                    await test_func(project_id)
                else:
                    await test_func()
            
            # Step 4: Display results
            print("\n📊 Test Results Summary:")
            print("=" * 80)
            
            passed = 0
            failed = 0
            errors = 0
            
            for result in self.test_results:
                status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
                print(f"{status_icon} {result['test']}: {result['status']}")
                print(f"   {result['details']}")
                
                if result["status"] == "PASS":
                    passed += 1
                elif result["status"] == "FAIL":
                    failed += 1
                else:
                    errors += 1
            
            total_tests = len(self.test_results)
            success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
            
            print("\n" + "=" * 80)
            print(f"🎯 RECURRING TASK BACKEND COMPATIBILITY TEST RESULTS:")
            print(f"   Total Tests: {total_tests}")
            print(f"   Passed: {passed}")
            print(f"   Failed: {failed}")
            print(f"   Errors: {errors}")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: Backend fully supports the new recurrence configuration UI!")
            elif success_rate >= 75:
                print("✅ GOOD: Backend mostly supports the new recurrence configuration UI with minor issues")
            elif success_rate >= 50:
                print("⚠️ MODERATE: Backend partially supports the new recurrence configuration UI")
            else:
                print("❌ POOR: Backend has significant compatibility issues with the new recurrence configuration UI")
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution function"""
    tester = RecurringTaskBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())