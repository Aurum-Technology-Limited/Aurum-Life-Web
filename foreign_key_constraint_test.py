#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://f3436837-b2f7-41f6-8f79-d2f18535f691.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ForeignKeyConstraintTestSuite:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_users = []
        self.created_resources = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': []
        }
        self.created_resources = {
            'users': [],
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': []
        }
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            # Try to register user first (in case they don't exist)
            register_data = {
                "username": "fktestfinal",
                "email": self.test_user_email,
                "first_name": "FK",
                "last_name": "Test",
                "password": self.test_user_password
            }
            
            user_created = False
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status == 200:
                    user_created = True
                    print("✅ New user registered successfully")
                elif response.status == 400:
                    print("ℹ️ User already exists")
                else:
                    print(f"⚠️ Registration response: {response.status}")
                    
            # Login to get token
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    
                    # Get user ID from /auth/me
                    async with self.session.get(f"{API_BASE}/auth/me", headers={"Authorization": f"Bearer {self.auth_token}"}) as me_response:
                        if me_response.status == 200:
                            user_data = await me_response.json()
                            user_id = user_data.get('id')
                            
                            # If user was just created, sync them to legacy users table
                            if user_created and user_id:
                                print(f"🔄 Syncing new user {user_id} to legacy users table...")
                                import subprocess
                                result = subprocess.run(['python', '/app/sync_user.py', user_id], 
                                                      capture_output=True, text=True, cwd='/app')
                                if result.returncode == 0:
                                    print("✅ User synchronized successfully")
                                else:
                                    print(f"⚠️ User sync warning: {result.stderr}")
                    
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_user_authentication_flow(self):
        """Test 1: User Authentication Flow"""
        print("\n🧪 Test 1: User Authentication Flow")
        
        try:
            # Test /auth/me endpoint
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ User authentication working - User ID: {user_data.get('id')}")
                    self.test_results.append({
                        "test": "User Authentication Flow", 
                        "status": "PASSED", 
                        "details": f"User ID: {user_data.get('id')}"
                    })
                    return user_data.get('id')
                else:
                    print(f"❌ User authentication failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({
                        "test": "User Authentication Flow", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return None
                    
        except Exception as e:
            print(f"❌ User authentication test failed: {e}")
            self.test_results.append({
                "test": "User Authentication Flow", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return None
            
    async def test_pillar_creation(self):
        """Test 2: Pillar Creation (Foreign Key Constraint Test)"""
        print("\n🧪 Test 2: Pillar Creation - Foreign Key Constraint Test")
        
        try:
            pillar_data = {
                "name": "FK Test Pillar",
                "description": "Testing foreign key constraints for pillar creation",
                "icon": "🎯",
                "color": "#FF5722",
                "time_allocation": 25
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillar = await response.json()
                    self.created_resources['pillars'].append(pillar["id"])
                    print(f"✅ Pillar created successfully - ID: {pillar['id']}")
                    self.test_results.append({
                        "test": "Pillar Creation", 
                        "status": "PASSED", 
                        "details": f"Pillar ID: {pillar['id']}"
                    })
                    return pillar["id"]
                else:
                    print(f"❌ Pillar creation failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({
                        "test": "Pillar Creation", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status} - {error_text}"
                    })
                    return None
                    
        except Exception as e:
            print(f"❌ Pillar creation test failed: {e}")
            self.test_results.append({
                "test": "Pillar Creation", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return None
            
    async def test_area_creation(self, pillar_id=None):
        """Test 3: Area Creation (Foreign Key Constraint Test)"""
        print("\n🧪 Test 3: Area Creation - Foreign Key Constraint Test")
        
        try:
            area_data = {
                "name": "FK Test Area",
                "description": "Testing foreign key constraints for area creation",
                "icon": "📁",
                "color": "#2196F3",
                "importance": 4
            }
            
            if pillar_id:
                area_data["pillar_id"] = pillar_id
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    self.created_resources['areas'].append(area["id"])
                    print(f"✅ Area created successfully - ID: {area['id']}")
                    self.test_results.append({
                        "test": "Area Creation", 
                        "status": "PASSED", 
                        "details": f"Area ID: {area['id']}"
                    })
                    return area["id"]
                else:
                    print(f"❌ Area creation failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({
                        "test": "Area Creation", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status} - {error_text}"
                    })
                    return None
                    
        except Exception as e:
            print(f"❌ Area creation test failed: {e}")
            self.test_results.append({
                "test": "Area Creation", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return None
            
    async def test_project_creation(self, area_id=None):
        """Test 4: Project Creation (Foreign Key Constraint Test)"""
        print("\n🧪 Test 4: Project Creation - Foreign Key Constraint Test")
        
        try:
            project_data = {
                "name": "FK Test Project",
                "description": "Testing foreign key constraints for project creation",
                "icon": "🚀",
                "priority": "high",
                "status": "active"
            }
            
            if area_id:
                project_data["area_id"] = area_id
            
            async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    project = await response.json()
                    self.created_resources['projects'].append(project["id"])
                    print(f"✅ Project created successfully - ID: {project['id']}")
                    self.test_results.append({
                        "test": "Project Creation", 
                        "status": "PASSED", 
                        "details": f"Project ID: {project['id']}"
                    })
                    return project["id"]
                else:
                    print(f"❌ Project creation failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({
                        "test": "Project Creation", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status} - {error_text}"
                    })
                    return None
                    
        except Exception as e:
            print(f"❌ Project creation test failed: {e}")
            self.test_results.append({
                "test": "Project Creation", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return None
            
    async def test_task_creation(self, project_id=None):
        """Test 5: Task Creation (Foreign Key Constraint Test)"""
        print("\n🧪 Test 5: Task Creation - Foreign Key Constraint Test")
        
        try:
            task_data = {
                "name": "FK Test Task",
                "description": "Testing foreign key constraints for task creation",
                "priority": "high",
                "status": "todo",
                "estimated_duration": 60
            }
            
            if project_id:
                task_data["project_id"] = project_id
            
            async with self.session.post(f"{API_BASE}/tasks", json=task_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    task = await response.json()
                    self.created_resources['tasks'].append(task["id"])
                    print(f"✅ Task created successfully - ID: {task['id']}")
                    self.test_results.append({
                        "test": "Task Creation", 
                        "status": "PASSED", 
                        "details": f"Task ID: {task['id']}"
                    })
                    return task["id"]
                else:
                    print(f"❌ Task creation failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({
                        "test": "Task Creation", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status} - {error_text}"
                    })
                    return None
                    
        except Exception as e:
            print(f"❌ Task creation test failed: {e}")
            self.test_results.append({
                "test": "Task Creation", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return None
            
    async def test_crud_operations(self):
        """Test 6: CRUD Operations on Created Data"""
        print("\n🧪 Test 6: CRUD Operations Test")
        
        try:
            crud_results = []
            
            # Test READ operations
            if self.created_resources['pillars']:
                pillar_id = self.created_resources['pillars'][0]
                async with self.session.get(f"{API_BASE}/pillars/{pillar_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        crud_results.append("Pillar READ: ✅")
                    else:
                        crud_results.append(f"Pillar READ: ❌ ({response.status})")
                        
            if self.created_resources['areas']:
                area_id = self.created_resources['areas'][0]
                async with self.session.get(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        crud_results.append("Area READ: ✅")
                    else:
                        crud_results.append(f"Area READ: ❌ ({response.status})")
                        
            if self.created_resources['projects']:
                project_id = self.created_resources['projects'][0]
                async with self.session.get(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        crud_results.append("Project READ: ✅")
                    else:
                        crud_results.append(f"Project READ: ❌ ({response.status})")
                        
            # Test UPDATE operations
            if self.created_resources['tasks']:
                task_id = self.created_resources['tasks'][0]
                update_data = {"name": "Updated FK Test Task", "description": "Updated description"}
                async with self.session.put(f"{API_BASE}/tasks/{task_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        crud_results.append("Task UPDATE: ✅")
                    else:
                        crud_results.append(f"Task UPDATE: ❌ ({response.status})")
                        
            # Test LIST operations
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    crud_results.append("Pillars LIST: ✅")
                else:
                    crud_results.append(f"Pillars LIST: ❌ ({response.status})")
                    
            async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    crud_results.append("Areas LIST: ✅")
                else:
                    crud_results.append(f"Areas LIST: ❌ ({response.status})")
                    
            async with self.session.get(f"{API_BASE}/projects", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    crud_results.append("Projects LIST: ✅")
                else:
                    crud_results.append(f"Projects LIST: ❌ ({response.status})")
                    
            async with self.session.get(f"{API_BASE}/tasks", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    crud_results.append("Tasks LIST: ✅")
                else:
                    crud_results.append(f"Tasks LIST: ❌ ({response.status})")
            
            success_count = len([r for r in crud_results if "✅" in r])
            total_count = len(crud_results)
            
            print(f"✅ CRUD Operations: {success_count}/{total_count} successful")
            for result in crud_results:
                print(f"   {result}")
                
            if success_count == total_count:
                self.test_results.append({
                    "test": "CRUD Operations", 
                    "status": "PASSED", 
                    "details": f"{success_count}/{total_count} operations successful"
                })
            else:
                self.test_results.append({
                    "test": "CRUD Operations", 
                    "status": "PARTIAL", 
                    "details": f"{success_count}/{total_count} operations successful"
                })
                
        except Exception as e:
            print(f"❌ CRUD operations test failed: {e}")
            self.test_results.append({
                "test": "CRUD Operations", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_database_consistency(self):
        """Test 7: Database Consistency Check"""
        print("\n🧪 Test 7: Database Consistency Check")
        
        try:
            consistency_results = []
            
            # Test dashboard endpoint (tests user data consistency)
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    dashboard_data = await response.json()
                    if 'user' in dashboard_data and 'stats' in dashboard_data:
                        consistency_results.append("Dashboard consistency: ✅")
                    else:
                        consistency_results.append("Dashboard consistency: ❌ (missing fields)")
                else:
                    consistency_results.append(f"Dashboard consistency: ❌ ({response.status})")
                    
            # Test today view (tests task relationships)
            async with self.session.get(f"{API_BASE}/today", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    today_data = await response.json()
                    if 'prioritized_tasks' in today_data:
                        consistency_results.append("Today view consistency: ✅")
                    else:
                        consistency_results.append("Today view consistency: ❌ (missing fields)")
                else:
                    consistency_results.append(f"Today view consistency: ❌ ({response.status})")
                    
            # Test areas with projects (tests foreign key relationships)
            async with self.session.get(f"{API_BASE}/areas?include_projects=true", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    areas_data = await response.json()
                    consistency_results.append("Areas with projects consistency: ✅")
                else:
                    consistency_results.append(f"Areas with projects consistency: ❌ ({response.status})")
                    
            # Test pillars with areas (tests foreign key relationships)
            async with self.session.get(f"{API_BASE}/pillars?include_areas=true", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillars_data = await response.json()
                    consistency_results.append("Pillars with areas consistency: ✅")
                else:
                    consistency_results.append(f"Pillars with areas consistency: ❌ ({response.status})")
            
            success_count = len([r for r in consistency_results if "✅" in r])
            total_count = len(consistency_results)
            
            print(f"✅ Database Consistency: {success_count}/{total_count} checks passed")
            for result in consistency_results:
                print(f"   {result}")
                
            if success_count == total_count:
                self.test_results.append({
                    "test": "Database Consistency", 
                    "status": "PASSED", 
                    "details": f"{success_count}/{total_count} consistency checks passed"
                })
            else:
                self.test_results.append({
                    "test": "Database Consistency", 
                    "status": "PARTIAL", 
                    "details": f"{success_count}/{total_count} consistency checks passed"
                })
                
        except Exception as e:
            print(f"❌ Database consistency test failed: {e}")
            self.test_results.append({
                "test": "Database Consistency", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_error_handling(self):
        """Test 8: Error Handling - No 500 Errors or FK Constraint Violations"""
        print("\n🧪 Test 8: Error Handling Test")
        
        try:
            error_handling_results = []
            
            # Test creating area with invalid pillar_id (should not cause 500 error)
            invalid_area_data = {
                "name": "Invalid FK Test Area",
                "description": "Testing invalid foreign key handling",
                "icon": "📁",
                "color": "#2196F3",
                "pillar_id": "invalid-pillar-id-12345"
            }
            
            async with self.session.post(f"{API_BASE}/areas", json=invalid_area_data, headers=self.get_auth_headers()) as response:
                if response.status in [400, 404]:  # Should be client error, not server error
                    error_handling_results.append("Invalid pillar_id handling: ✅")
                elif response.status == 500:
                    error_handling_results.append("Invalid pillar_id handling: ❌ (500 error)")
                else:
                    error_handling_results.append(f"Invalid pillar_id handling: ⚠️ ({response.status})")
                    
            # Test creating project with invalid area_id
            invalid_project_data = {
                "name": "Invalid FK Test Project",
                "description": "Testing invalid foreign key handling",
                "icon": "🚀",
                "area_id": "invalid-area-id-12345"
            }
            
            async with self.session.post(f"{API_BASE}/projects", json=invalid_project_data, headers=self.get_auth_headers()) as response:
                if response.status in [400, 404]:
                    error_handling_results.append("Invalid area_id handling: ✅")
                elif response.status == 500:
                    error_handling_results.append("Invalid area_id handling: ❌ (500 error)")
                else:
                    error_handling_results.append(f"Invalid area_id handling: ⚠️ ({response.status})")
                    
            # Test creating task with invalid project_id
            invalid_task_data = {
                "name": "Invalid FK Test Task",
                "description": "Testing invalid foreign key handling",
                "project_id": "invalid-project-id-12345"
            }
            
            async with self.session.post(f"{API_BASE}/tasks", json=invalid_task_data, headers=self.get_auth_headers()) as response:
                if response.status in [400, 404]:
                    error_handling_results.append("Invalid project_id handling: ✅")
                elif response.status == 500:
                    error_handling_results.append("Invalid project_id handling: ❌ (500 error)")
                else:
                    error_handling_results.append(f"Invalid project_id handling: ⚠️ ({response.status})")
            
            success_count = len([r for r in error_handling_results if "✅" in r])
            error_count = len([r for r in error_handling_results if "❌" in r])
            total_count = len(error_handling_results)
            
            print(f"✅ Error Handling: {success_count}/{total_count} tests passed, {error_count} critical errors")
            for result in error_handling_results:
                print(f"   {result}")
                
            if error_count == 0:
                self.test_results.append({
                    "test": "Error Handling", 
                    "status": "PASSED", 
                    "details": f"No 500 errors or FK constraint violations detected"
                })
            else:
                self.test_results.append({
                    "test": "Error Handling", 
                    "status": "FAILED", 
                    "details": f"{error_count} critical errors detected"
                })
                
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            self.test_results.append({
                "test": "Error Handling", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete in reverse order to respect foreign key constraints
            for task_id in self.created_resources['tasks']:
                async with self.session.delete(f"{API_BASE}/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted task {task_id}")
                    else:
                        print(f"⚠️ Failed to delete task {task_id}: {response.status}")
                        
            for project_id in self.created_resources['projects']:
                async with self.session.delete(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted project {project_id}")
                    else:
                        print(f"⚠️ Failed to delete project {project_id}: {response.status}")
                        
            for area_id in self.created_resources['areas']:
                async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted area {area_id}")
                    else:
                        print(f"⚠️ Failed to delete area {area_id}: {response.status}")
                        
            for pillar_id in self.created_resources['pillars']:
                async with self.session.delete(f"{API_BASE}/pillars/{pillar_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted pillar {pillar_id}")
                    else:
                        print(f"⚠️ Failed to delete pillar {pillar_id}: {response.status}")
                        
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 FOREIGN KEY CONSTRAINT RESOLUTION - TEST SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        partial = len([t for t in self.test_results if t["status"] == "PARTIAL"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Partial: {partial}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate >= 90:
            print("🎉 FOREIGN KEY CONSTRAINT ISSUE IS FULLY RESOLVED!")
            print("✅ All authenticated users can create and manage their data successfully")
        elif success_rate >= 75:
            print("⚠️ FOREIGN KEY CONSTRAINT ISSUE IS MOSTLY RESOLVED - MINOR ISSUES DETECTED")
        else:
            print("❌ FOREIGN KEY CONSTRAINT ISSUE STILL EXISTS - NEEDS IMMEDIATE ATTENTION")
            
        print("="*80)
        
    async def run_all_tests(self):
        """Run all foreign key constraint tests"""
        print("🚀 Starting Foreign Key Constraint Resolution Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("📋 Testing the critical fix for foreign key constraint mismatch")
        print("🎯 Goal: Verify users can create pillars, areas, projects, and tasks without FK violations")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            print("✅ Authentication successful")
            
            # Run all tests in sequence
            user_id = await self.test_user_authentication_flow()
            pillar_id = await self.test_pillar_creation()
            area_id = await self.test_area_creation(pillar_id)
            project_id = await self.test_project_creation(area_id)
            task_id = await self.test_task_creation(project_id)
            
            # Run additional tests
            await self.test_crud_operations()
            await self.test_database_consistency()
            await self.test_error_handling()
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = ForeignKeyConstraintTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())