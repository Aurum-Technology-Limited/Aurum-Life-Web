#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration - Use external URL from frontend/.env
BACKEND_URL = "https://2add7c3c-bc98-404b-af7c-7c73ee7f9c41.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class ForeignKeyConstraintTestSuite:
    """
    🔧 BACKEND CRUD FIXES VERIFICATION - AREAS AND TASKS FOCUS
    Testing foreign key constraint fixes for Areas and Tasks CRUD operations
    """
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword"
        self.test_results = []
        self.created_resources = {
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
        """Authenticate with test credentials"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    print(f"✅ Authentication successful for {self.test_user_email}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}

    async def test_areas_crud_foreign_key_validation(self):
        """Test 1: Areas CRUD with pillar_id foreign key validation"""
        print("\n🧪 Test 1: Areas CRUD - Foreign Key Constraint Validation")
        
        try:
            # First create a pillar for valid testing
            pillar_data = {
                "name": "Test Pillar for Areas",
                "description": "Pillar for testing area foreign key constraints",
                "icon": "🎯",
                "color": "#10B981",
                "time_allocation_percentage": 25.0
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillar = await response.json()
                    valid_pillar_id = pillar['id']
                    self.created_resources['pillars'].append(valid_pillar_id)
                    print(f"✅ Created test pillar: {valid_pillar_id}")
                else:
                    print(f"❌ Failed to create test pillar: {response.status}")
                    return False

            # Test 1a: Create area WITHOUT pillar_id (should work - pillar_id is optional)
            area_data_no_pillar = {
                "name": "Area Without Pillar",
                "description": "Testing area creation without pillar_id",
                "icon": "📝",
                "color": "#F59E0B",
                "importance": 3
            }
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data_no_pillar, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    self.created_resources['areas'].append(area['id'])
                    print("✅ Area created successfully WITHOUT pillar_id (pillar_id is optional)")
                    self.test_results.append({"test": "Area Creation - No Pillar", "status": "PASSED", "details": "Optional pillar_id working correctly"})
                else:
                    error_text = await response.text()
                    print(f"❌ Area creation without pillar_id failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Area Creation - No Pillar", "status": "FAILED", "reason": f"HTTP {response.status}"})

            # Test 1b: Create area WITH valid pillar_id (should work)
            area_data_valid_pillar = {
                "name": "Area With Valid Pillar",
                "description": "Testing area creation with valid pillar_id",
                "pillar_id": valid_pillar_id,
                "icon": "✅",
                "color": "#10B981",
                "importance": 4
            }
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data_valid_pillar, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    self.created_resources['areas'].append(area['id'])
                    if area.get('pillar_id') == valid_pillar_id:
                        print("✅ Area created successfully WITH valid pillar_id")
                        self.test_results.append({"test": "Area Creation - Valid Pillar", "status": "PASSED", "details": "Valid pillar_id linking working"})
                    else:
                        print("❌ Area created but pillar_id not properly linked")
                        self.test_results.append({"test": "Area Creation - Valid Pillar", "status": "FAILED", "reason": "Pillar linking failed"})
                else:
                    error_text = await response.text()
                    print(f"❌ Area creation with valid pillar_id failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Area Creation - Valid Pillar", "status": "FAILED", "reason": f"HTTP {response.status}"})

            # Test 1c: Create area WITH invalid pillar_id (should fail gracefully)
            area_data_invalid_pillar = {
                "name": "Area With Invalid Pillar",
                "description": "Testing area creation with invalid pillar_id",
                "pillar_id": "invalid-pillar-id-12345",
                "icon": "❌",
                "color": "#EF4444",
                "importance": 2
            }
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data_invalid_pillar, headers=self.get_auth_headers()) as response:
                if response.status == 400:
                    error_data = await response.json()
                    print("✅ Area creation with invalid pillar_id correctly rejected with clear error")
                    print(f"   Error message: {error_data.get('detail', 'No detail provided')}")
                    self.test_results.append({"test": "Area Creation - Invalid Pillar", "status": "PASSED", "details": "Invalid pillar_id properly rejected"})
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ Area creation with invalid pillar_id caused server error (should be 400): {error_text}")
                    self.test_results.append({"test": "Area Creation - Invalid Pillar", "status": "FAILED", "reason": "Server error instead of validation error"})
                else:
                    print(f"❌ Area creation with invalid pillar_id should fail but got: {response.status}")
                    self.test_results.append({"test": "Area Creation - Invalid Pillar", "status": "FAILED", "reason": f"Expected 400, got {response.status}"})

            # Test 1d: Update area operations
            if self.created_resources['areas']:
                area_id = self.created_resources['areas'][0]
                update_data = {
                    "name": "Updated Area Name",
                    "importance": 5
                }
                
                async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("✅ Area update operation successful")
                        self.test_results.append({"test": "Area Update", "status": "PASSED", "details": "Area update working correctly"})
                    else:
                        error_text = await response.text()
                        print(f"❌ Area update failed: {response.status} - {error_text}")
                        self.test_results.append({"test": "Area Update", "status": "FAILED", "reason": f"HTTP {response.status}"})

            return True
            
        except Exception as e:
            print(f"❌ Areas CRUD foreign key test failed: {e}")
            self.test_results.append({"test": "Areas CRUD Foreign Key", "status": "FAILED", "reason": str(e)})
            return False

    async def test_tasks_crud_foreign_key_validation(self):
        """Test 2: Tasks CRUD with project_id and parent_task_id foreign key validation"""
        print("\n🧪 Test 2: Tasks CRUD - Foreign Key Constraint Validation")
        
        try:
            # First create the dependency chain: Area -> Project
            area_data = {
                "name": "Test Area for Tasks",
                "description": "Area for testing task foreign key constraints",
                "icon": "🎯",
                "color": "#8B5CF6",
                "importance": 4
            }
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    area_id = area['id']
                    self.created_resources['areas'].append(area_id)
                    print(f"✅ Created test area: {area_id}")
                else:
                    print(f"❌ Failed to create test area: {response.status}")
                    return False

            project_data = {
                "area_id": area_id,
                "name": "Test Project for Tasks",
                "description": "Project for testing task foreign key constraints",
                "icon": "🚀",
                "status": "Not Started",
                "priority": "high"
            }
            
            async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    project = await response.json()
                    valid_project_id = project['id']
                    self.created_resources['projects'].append(valid_project_id)
                    print(f"✅ Created test project: {valid_project_id}")
                else:
                    print(f"❌ Failed to create test project: {response.status}")
                    return False

            # Test 2a: Create task with valid project_id (should work)
            task_data_valid_project = {
                "project_id": valid_project_id,
                "name": "Task With Valid Project",
                "description": "Testing task creation with valid project_id",
                "status": "todo",
                "priority": "medium"
            }
            
            async with self.session.post(f"{API_BASE}/tasks", json=task_data_valid_project, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    task = await response.json()
                    parent_task_id = task['id']  # Save for parent task testing
                    self.created_resources['tasks'].append(parent_task_id)
                    if task.get('project_id') == valid_project_id:
                        print("✅ Task created successfully WITH valid project_id")
                        self.test_results.append({"test": "Task Creation - Valid Project", "status": "PASSED", "details": "Valid project_id linking working"})
                    else:
                        print("❌ Task created but project_id not properly linked")
                        self.test_results.append({"test": "Task Creation - Valid Project", "status": "FAILED", "reason": "Project linking failed"})
                else:
                    error_text = await response.text()
                    print(f"❌ Task creation with valid project_id failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Task Creation - Valid Project", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False

            # Test 2b: Create task with invalid project_id (should fail gracefully)
            task_data_invalid_project = {
                "project_id": "invalid-project-id-12345",
                "name": "Task With Invalid Project",
                "description": "Testing task creation with invalid project_id",
                "status": "todo",
                "priority": "low"
            }
            
            async with self.session.post(f"{API_BASE}/tasks", json=task_data_invalid_project, headers=self.get_auth_headers()) as response:
                if response.status == 400:
                    error_data = await response.json()
                    print("✅ Task creation with invalid project_id correctly rejected with clear error")
                    print(f"   Error message: {error_data.get('detail', 'No detail provided')}")
                    self.test_results.append({"test": "Task Creation - Invalid Project", "status": "PASSED", "details": "Invalid project_id properly rejected"})
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ Task creation with invalid project_id caused server error (should be 400): {error_text}")
                    self.test_results.append({"test": "Task Creation - Invalid Project", "status": "FAILED", "reason": "Server error instead of validation error"})
                else:
                    print(f"❌ Task creation with invalid project_id should fail but got: {response.status}")
                    self.test_results.append({"test": "Task Creation - Invalid Project", "status": "FAILED", "reason": f"Expected 400, got {response.status}"})

            # Test 2c: Create task with valid parent_task_id (should work)
            task_data_valid_parent = {
                "project_id": valid_project_id,
                "parent_task_id": parent_task_id,
                "name": "Subtask With Valid Parent",
                "description": "Testing task creation with valid parent_task_id",
                "status": "todo",
                "priority": "high"
            }
            
            async with self.session.post(f"{API_BASE}/tasks", json=task_data_valid_parent, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    task = await response.json()
                    self.created_resources['tasks'].append(task['id'])
                    if task.get('parent_task_id') == parent_task_id:
                        print("✅ Task created successfully WITH valid parent_task_id")
                        self.test_results.append({"test": "Task Creation - Valid Parent", "status": "PASSED", "details": "Valid parent_task_id linking working"})
                    else:
                        print("❌ Task created but parent_task_id not properly linked")
                        self.test_results.append({"test": "Task Creation - Valid Parent", "status": "FAILED", "reason": "Parent task linking failed"})
                else:
                    error_text = await response.text()
                    print(f"❌ Task creation with valid parent_task_id failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Task Creation - Valid Parent", "status": "FAILED", "reason": f"HTTP {response.status}"})

            # Test 2d: Create task with invalid parent_task_id (should fail gracefully)
            task_data_invalid_parent = {
                "project_id": valid_project_id,
                "parent_task_id": "invalid-parent-task-id-12345",
                "name": "Subtask With Invalid Parent",
                "description": "Testing task creation with invalid parent_task_id",
                "status": "todo",
                "priority": "medium"
            }
            
            async with self.session.post(f"{API_BASE}/tasks", json=task_data_invalid_parent, headers=self.get_auth_headers()) as response:
                if response.status == 400:
                    error_data = await response.json()
                    print("✅ Task creation with invalid parent_task_id correctly rejected with clear error")
                    print(f"   Error message: {error_data.get('detail', 'No detail provided')}")
                    self.test_results.append({"test": "Task Creation - Invalid Parent", "status": "PASSED", "details": "Invalid parent_task_id properly rejected"})
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ Task creation with invalid parent_task_id caused server error (should be 400): {error_text}")
                    self.test_results.append({"test": "Task Creation - Invalid Parent", "status": "FAILED", "reason": "Server error instead of validation error"})
                else:
                    print(f"❌ Task creation with invalid parent_task_id should fail but got: {response.status}")
                    self.test_results.append({"test": "Task Creation - Invalid Parent", "status": "FAILED", "reason": f"Expected 400, got {response.status}"})

            # Test 2e: Update task operations
            if self.created_resources['tasks']:
                task_id = self.created_resources['tasks'][0]
                update_data = {
                    "name": "Updated Task Name",
                    "status": "in_progress"
                }
                
                async with self.session.put(f"{API_BASE}/tasks/{task_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("✅ Task update operation successful")
                        self.test_results.append({"test": "Task Update", "status": "PASSED", "details": "Task update working correctly"})
                    else:
                        error_text = await response.text()
                        print(f"❌ Task update failed: {response.status} - {error_text}")
                        self.test_results.append({"test": "Task Update", "status": "FAILED", "reason": f"HTTP {response.status}"})

            return True
            
        except Exception as e:
            print(f"❌ Tasks CRUD foreign key test failed: {e}")
            self.test_results.append({"test": "Tasks CRUD Foreign Key", "status": "FAILED", "reason": str(e)})
            return False

    async def test_dependency_creation_workflow(self):
        """Test 3: Full dependency creation workflow (Pillar → Area → Project → Task)"""
        print("\n🧪 Test 3: Dependency Creation Workflow Testing")
        
        try:
            # Step 1: Create a Pillar
            pillar_data = {
                "name": "Workflow Test Pillar",
                "description": "Pillar for testing full dependency workflow",
                "icon": "🏗️",
                "color": "#6366F1",
                "time_allocation_percentage": 30.0
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillar = await response.json()
                    workflow_pillar_id = pillar['id']
                    self.created_resources['pillars'].append(workflow_pillar_id)
                    print(f"✅ Step 1: Created Pillar - {workflow_pillar_id}")
                else:
                    print(f"❌ Step 1 failed: Pillar creation - {response.status}")
                    return False

            # Step 2: Create an Area linked to that Pillar
            area_data = {
                "pillar_id": workflow_pillar_id,
                "name": "Workflow Test Area",
                "description": "Area linked to workflow test pillar",
                "icon": "🎯",
                "color": "#10B981",
                "importance": 4
            }
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    workflow_area_id = area['id']
                    self.created_resources['areas'].append(workflow_area_id)
                    if area.get('pillar_id') == workflow_pillar_id:
                        print(f"✅ Step 2: Created Area linked to Pillar - {workflow_area_id}")
                    else:
                        print(f"❌ Step 2: Area created but not properly linked to Pillar")
                        return False
                else:
                    print(f"❌ Step 2 failed: Area creation - {response.status}")
                    return False

            # Step 3: Create a Project linked to that Area
            project_data = {
                "area_id": workflow_area_id,
                "name": "Workflow Test Project",
                "description": "Project linked to workflow test area",
                "icon": "🚀",
                "status": "Not Started",
                "priority": "high"
            }
            
            async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    project = await response.json()
                    workflow_project_id = project['id']
                    self.created_resources['projects'].append(workflow_project_id)
                    if project.get('area_id') == workflow_area_id:
                        print(f"✅ Step 3: Created Project linked to Area - {workflow_project_id}")
                    else:
                        print(f"❌ Step 3: Project created but not properly linked to Area")
                        return False
                else:
                    print(f"❌ Step 3 failed: Project creation - {response.status}")
                    return False

            # Step 4: Create Tasks linked to that Project
            task_data = {
                "project_id": workflow_project_id,
                "name": "Workflow Test Task",
                "description": "Task linked to workflow test project",
                "status": "todo",
                "priority": "medium"
            }
            
            async with self.session.post(f"{API_BASE}/tasks", json=task_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    task = await response.json()
                    workflow_task_id = task['id']
                    self.created_resources['tasks'].append(workflow_task_id)
                    if task.get('project_id') == workflow_project_id:
                        print(f"✅ Step 4: Created Task linked to Project - {workflow_task_id}")
                        print("🎉 Full hierarchy creation workflow SUCCESSFUL!")
                        self.test_results.append({"test": "Dependency Creation Workflow", "status": "PASSED", "details": "Full Pillar→Area→Project→Task chain created successfully"})
                        return True
                    else:
                        print(f"❌ Step 4: Task created but not properly linked to Project")
                        return False
                else:
                    print(f"❌ Step 4 failed: Task creation - {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Dependency creation workflow test failed: {e}")
            self.test_results.append({"test": "Dependency Creation Workflow", "status": "FAILED", "reason": str(e)})
            return False

    async def test_delete_operations(self):
        """Test 4: Delete operations across all entities"""
        print("\n🧪 Test 4: Delete Operations Testing")
        
        try:
            success_count = 0
            total_tests = 0
            
            # Delete Tasks
            for task_id in self.created_resources['tasks'][:2]:  # Test first 2 tasks
                total_tests += 1
                async with self.session.delete(f"{API_BASE}/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Task delete successful: {task_id}")
                        success_count += 1
                    else:
                        print(f"❌ Task delete failed: {task_id} - {response.status}")
                        
            # Delete Projects
            for project_id in self.created_resources['projects'][:2]:  # Test first 2 projects
                total_tests += 1
                async with self.session.delete(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Project delete successful: {project_id}")
                        success_count += 1
                    else:
                        print(f"❌ Project delete failed: {project_id} - {response.status}")
                        
            # Delete Areas
            for area_id in self.created_resources['areas'][:2]:  # Test first 2 areas
                total_tests += 1
                async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Area delete successful: {area_id}")
                        success_count += 1
                    else:
                        print(f"❌ Area delete failed: {area_id} - {response.status}")
                        
            if success_count == total_tests and total_tests > 0:
                self.test_results.append({"test": "Delete Operations", "status": "PASSED", "details": f"All {total_tests} delete operations successful"})
                return True
            elif total_tests > 0:
                self.test_results.append({"test": "Delete Operations", "status": "PARTIAL", "details": f"{success_count}/{total_tests} delete operations successful"})
                return True
            else:
                self.test_results.append({"test": "Delete Operations", "status": "SKIPPED", "details": "No resources to delete"})
                return True
                
        except Exception as e:
            print(f"❌ Delete operations test failed: {e}")
            self.test_results.append({"test": "Delete Operations", "status": "FAILED", "reason": str(e)})
            return False

    async def test_comprehensive_crud_verification(self):
        """Test 5: Quick verification of other CRUD components"""
        print("\n🧪 Test 5: Comprehensive CRUD Re-verification")
        
        try:
            success_count = 0
            total_tests = 4
            
            # Test Dashboard endpoint
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    print("✅ Dashboard endpoint working")
                    success_count += 1
                else:
                    print(f"❌ Dashboard endpoint failed: {response.status}")
                    
            # Test Today view endpoint
            async with self.session.get(f"{API_BASE}/today", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    print("✅ Today view endpoint working")
                    success_count += 1
                else:
                    print(f"❌ Today view endpoint failed: {response.status}")
                    
            # Test Insights endpoint
            async with self.session.get(f"{API_BASE}/insights", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    print("✅ Insights endpoint working")
                    success_count += 1
                else:
                    print(f"❌ Insights endpoint failed: {response.status}")
                    
            # Test Pillars GET endpoint
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    print("✅ Pillars GET endpoint working")
                    success_count += 1
                else:
                    print(f"❌ Pillars GET endpoint failed: {response.status}")
                    
            success_rate = (success_count / total_tests) * 100
            if success_rate >= 75:
                self.test_results.append({"test": "Comprehensive CRUD Re-verification", "status": "PASSED", "details": f"{success_count}/{total_tests} endpoints working ({success_rate:.1f}%)"})
                return True
            else:
                self.test_results.append({"test": "Comprehensive CRUD Re-verification", "status": "FAILED", "details": f"Only {success_count}/{total_tests} endpoints working ({success_rate:.1f}%)"})
                return False
                
        except Exception as e:
            print(f"❌ Comprehensive CRUD re-verification failed: {e}")
            self.test_results.append({"test": "Comprehensive CRUD Re-verification", "status": "FAILED", "reason": str(e)})
            return False

    async def cleanup_remaining_test_data(self):
        """Clean up remaining test data"""
        print("\n🧹 Cleaning up remaining test data...")
        
        try:
            # Delete remaining resources in reverse order
            for task_id in self.created_resources['tasks']:
                try:
                    async with self.session.delete(f"{API_BASE}/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            print(f"✅ Cleaned up task {task_id}")
                        else:
                            print(f"⚠️ Failed to clean up task {task_id}: {response.status}")
                except:
                    pass
                        
            for project_id in self.created_resources['projects']:
                try:
                    async with self.session.delete(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            print(f"✅ Cleaned up project {project_id}")
                        else:
                            print(f"⚠️ Failed to clean up project {project_id}: {response.status}")
                except:
                    pass
                        
            for area_id in self.created_resources['areas']:
                try:
                    async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            print(f"✅ Cleaned up area {area_id}")
                        else:
                            print(f"⚠️ Failed to clean up area {area_id}: {response.status}")
                except:
                    pass
                        
            for pillar_id in self.created_resources['pillars']:
                try:
                    async with self.session.delete(f"{API_BASE}/pillars/{pillar_id}", headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            print(f"✅ Cleaned up pillar {pillar_id}")
                        else:
                            print(f"⚠️ Failed to clean up pillar {pillar_id}: {response.status}")
                except:
                    pass
                        
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🔧 BACKEND CRUD FIXES VERIFICATION - AREAS AND TASKS FOCUS")
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
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️", "SKIPPED": "⏭️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate >= 95:
            print("🎉 FOREIGN KEY CONSTRAINT FIXES ARE WORKING PERFECTLY!")
            print("✅ Areas CRUD now 100% functional with proper error handling")
            print("✅ Tasks CRUD now 100% functional with proper error handling")
            print("✅ Clear error messages for invalid foreign key references")
            print("✅ Overall backend CRUD success rate achieved 95-100%")
        elif success_rate >= 80:
            print("⚠️ FOREIGN KEY CONSTRAINT FIXES ARE MOSTLY WORKING - MINOR ISSUES DETECTED")
            print("✅ Most Areas and Tasks CRUD operations working")
            print("⚠️ Some error handling or edge cases may need attention")
        else:
            print("❌ FOREIGN KEY CONSTRAINT FIXES NEED MORE WORK")
            print("❌ Significant issues remain with Areas and/or Tasks CRUD operations")
            
        print("="*80)
        
    async def run_foreign_key_constraint_tests(self):
        """Run the focused foreign key constraint test suite"""
        print("🔧 Starting Backend CRUD Fixes Verification - Areas and Tasks Focus...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("🎯 Testing foreign key constraint fixes for Areas and Tasks CRUD operations")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run focused tests
            await self.test_areas_crud_foreign_key_validation()
            await self.test_tasks_crud_foreign_key_validation()
            await self.test_dependency_creation_workflow()
            await self.test_delete_operations()
            await self.test_comprehensive_crud_verification()
            
            # Cleanup
            await self.cleanup_remaining_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = ForeignKeyConstraintTestSuite()
    await test_suite.run_foreign_key_constraint_tests()

if __name__ == "__main__":
    asyncio.run(main())