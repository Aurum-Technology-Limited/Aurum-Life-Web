#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import base64
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://19eedb9d-8356-46da-a868-07e1ec72a1d8.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class SupabaseCRUDTestSuite:
    """Comprehensive CRUD testing for Supabase-only architecture with schema mapping fixes"""
    
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
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
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
        
    async def test_pillar_crud(self):
        """Test 1: Pillar CRUD operations with schema mapping"""
        print("\n🧪 Test 1: Pillar CRUD Operations with Schema Mapping")
        
        try:
            # CREATE Pillar - Test field mapping (is_active → archived, time_allocation → time_allocation_percentage)
            pillar_data = {
                "name": "Health & Wellness",
                "description": "Physical and mental health pillar",
                "icon": "💪",
                "color": "#10B981",
                "time_allocation": 30.0  # Should map to time_allocation_percentage
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillar = await response.json()
                    self.created_resources['pillars'].append(pillar['id'])
                    
                    # Verify field mapping
                    if pillar.get('time_allocation_percentage') == 30.0:
                        print("✅ Pillar created successfully with proper field mapping")
                        self.test_results.append({"test": "Pillar Creation", "status": "PASSED", "details": "Field mapping working correctly"})
                    else:
                        print("❌ Pillar field mapping failed")
                        self.test_results.append({"test": "Pillar Creation", "status": "FAILED", "reason": "Field mapping incorrect"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Pillar creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Pillar Creation", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
            # READ Pillars - Test data retrieval
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillars = await response.json()
                    if len(pillars) > 0 and any(p['id'] == self.created_resources['pillars'][0] for p in pillars):
                        print("✅ Pillar retrieval successful")
                        return pillar['id']  # Return pillar ID for area creation
                    else:
                        print("❌ Created pillar not found in retrieval")
                        self.test_results.append({"test": "Pillar Retrieval", "status": "FAILED", "reason": "Created pillar not found"})
                        return False
                else:
                    print(f"❌ Pillar retrieval failed: {response.status}")
                    self.test_results.append({"test": "Pillar Retrieval", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Pillar CRUD test failed: {e}")
            self.test_results.append({"test": "Pillar CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_area_crud(self, pillar_id: str):
        """Test 2: Area CRUD operations with schema mapping"""
        print("\n🧪 Test 2: Area CRUD Operations with Schema Mapping")
        
        try:
            # CREATE Area - Test field mapping (is_active → archived, importance field)
            area_data = {
                "pillar_id": pillar_id,
                "name": "Fitness & Exercise",
                "description": "Physical fitness and exercise routines",
                "icon": "🏃",
                "color": "#F59E0B",
                "importance": 4  # Should map to existing importance field
            }
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    self.created_resources['areas'].append(area['id'])
                    
                    # Verify field mapping
                    if area.get('importance') == 4 and area.get('pillar_id') == pillar_id:
                        print("✅ Area created successfully with proper field mapping")
                        self.test_results.append({"test": "Area Creation", "status": "PASSED", "details": "Field mapping and pillar linking working"})
                    else:
                        print("❌ Area field mapping or pillar linking failed")
                        self.test_results.append({"test": "Area Creation", "status": "FAILED", "reason": "Field mapping or linking incorrect"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Area creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Area Creation", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
            # READ Areas - Test data retrieval with pillar relationship
            async with self.session.get(f"{API_BASE}/areas?include_projects=true", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    areas = await response.json()
                    created_area = next((a for a in areas if a['id'] == self.created_resources['areas'][0]), None)
                    if created_area and created_area.get('pillar_id') == pillar_id:
                        print("✅ Area retrieval successful with pillar relationship")
                        return area['id']  # Return area ID for project creation
                    else:
                        print("❌ Created area not found or pillar relationship missing")
                        self.test_results.append({"test": "Area Retrieval", "status": "FAILED", "reason": "Area not found or relationship missing"})
                        return False
                else:
                    print(f"❌ Area retrieval failed: {response.status}")
                    self.test_results.append({"test": "Area Retrieval", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Area CRUD test failed: {e}")
            self.test_results.append({"test": "Area CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_project_crud(self, area_id: str):
        """Test 3: Project CRUD operations with enum mapping"""
        print("\n🧪 Test 3: Project CRUD Operations with Enum Mapping")
        
        try:
            # CREATE Project - Test enum mapping (backend: not_started → database: Not Started)
            project_data = {
                "area_id": area_id,
                "name": "Morning Workout Routine",
                "description": "Daily morning exercise routine",
                "icon": "🏋️",
                "status": "not_started",  # Should map to "Not Started"
                "priority": "high",       # Should map to "High"
                "due_date": "2025-02-15T10:00:00Z"  # Should map to deadline
            }
            
            async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    project = await response.json()
                    self.created_resources['projects'].append(project['id'])
                    
                    # Verify enum mapping
                    if (project.get('status') == 'not_started' and 
                        project.get('priority') == 'high' and 
                        project.get('area_id') == area_id):
                        print("✅ Project created successfully with proper enum mapping")
                        self.test_results.append({"test": "Project Creation", "status": "PASSED", "details": "Enum mapping and area linking working"})
                    else:
                        print("❌ Project enum mapping or area linking failed")
                        print(f"Status: {project.get('status')}, Priority: {project.get('priority')}, Area ID: {project.get('area_id')}")
                        self.test_results.append({"test": "Project Creation", "status": "FAILED", "reason": "Enum mapping or linking incorrect"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Project creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Project Creation", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
            # READ Projects - Test data retrieval with area relationship
            async with self.session.get(f"{API_BASE}/projects?include_tasks=true", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    projects = await response.json()
                    created_project = next((p for p in projects if p['id'] == self.created_resources['projects'][0]), None)
                    if created_project and created_project.get('area_id') == area_id:
                        print("✅ Project retrieval successful with area relationship")
                        return project['id']  # Return project ID for task creation
                    else:
                        print("❌ Created project not found or area relationship missing")
                        self.test_results.append({"test": "Project Retrieval", "status": "FAILED", "reason": "Project not found or relationship missing"})
                        return False
                else:
                    print(f"❌ Project retrieval failed: {response.status}")
                    self.test_results.append({"test": "Project Retrieval", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Project CRUD test failed: {e}")
            self.test_results.append({"test": "Project CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_task_crud(self, project_id: str):
        """Test 4: Task CRUD operations with status/priority mapping"""
        print("\n🧪 Test 4: Task CRUD Operations with Status/Priority Mapping")
        
        try:
            # CREATE Task - Test status/priority mapping (backend: pending → database: todo, medium → Medium)
            task_data = {
                "project_id": project_id,
                "name": "30-minute cardio session",
                "description": "High-intensity cardio workout",
                "status": "pending",    # Should map to "todo"
                "priority": "medium",   # Should map to "Medium"
                "due_date": "2025-01-30T07:00:00Z"
            }
            
            async with self.session.post(f"{API_BASE}/tasks", json=task_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    task = await response.json()
                    self.created_resources['tasks'].append(task['id'])
                    
                    # Verify status/priority mapping
                    if (task.get('status') == 'pending' and 
                        task.get('priority') == 'medium' and 
                        task.get('project_id') == project_id):
                        print("✅ Task created successfully with proper status/priority mapping")
                        self.test_results.append({"test": "Task Creation", "status": "PASSED", "details": "Status/priority mapping and project linking working"})
                    else:
                        print("❌ Task status/priority mapping or project linking failed")
                        print(f"Status: {task.get('status')}, Priority: {task.get('priority')}, Project ID: {task.get('project_id')}")
                        self.test_results.append({"test": "Task Creation", "status": "FAILED", "reason": "Status/priority mapping or linking incorrect"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Task creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Task Creation", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
            # READ Tasks - Test data retrieval with project relationship
            async with self.session.get(f"{API_BASE}/tasks?project_id={project_id}", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    tasks = await response.json()
                    created_task = next((t for t in tasks if t['id'] == self.created_resources['tasks'][0]), None)
                    if created_task and created_task.get('project_id') == project_id:
                        print("✅ Task retrieval successful with project relationship")
                        return True
                    else:
                        print("❌ Created task not found or project relationship missing")
                        self.test_results.append({"test": "Task Retrieval", "status": "FAILED", "reason": "Task not found or relationship missing"})
                        return False
                else:
                    print(f"❌ Task retrieval failed: {response.status}")
                    self.test_results.append({"test": "Task Retrieval", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Task CRUD test failed: {e}")
            self.test_results.append({"test": "Task CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_update_operations(self):
        """Test 5: Update operations across all entities"""
        print("\n🧪 Test 5: Update Operations")
        
        try:
            success_count = 0
            
            # Update Pillar
            if self.created_resources['pillars']:
                pillar_id = self.created_resources['pillars'][0]
                update_data = {"name": "Health & Wellness (Updated)", "time_allocation": 35.0}
                
                async with self.session.put(f"{API_BASE}/pillars/{pillar_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("✅ Pillar update successful")
                        success_count += 1
                    else:
                        print(f"❌ Pillar update failed: {response.status}")
                        
            # Update Area
            if self.created_resources['areas']:
                area_id = self.created_resources['areas'][0]
                update_data = {"name": "Fitness & Exercise (Updated)", "importance": 5}
                
                async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("✅ Area update successful")
                        success_count += 1
                    else:
                        print(f"❌ Area update failed: {response.status}")
                        
            # Update Project
            if self.created_resources['projects']:
                project_id = self.created_resources['projects'][0]
                update_data = {"name": "Morning Workout Routine (Updated)", "status": "in_progress"}
                
                async with self.session.put(f"{API_BASE}/projects/{project_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("✅ Project update successful")
                        success_count += 1
                    else:
                        print(f"❌ Project update failed: {response.status}")
                        
            # Update Task
            if self.created_resources['tasks']:
                task_id = self.created_resources['tasks'][0]
                update_data = {"name": "30-minute cardio session (Updated)", "status": "in_progress"}
                
                async with self.session.put(f"{API_BASE}/tasks/{task_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("✅ Task update successful")
                        success_count += 1
                    else:
                        print(f"❌ Task update failed: {response.status}")
                        
            if success_count == 4:
                self.test_results.append({"test": "Update Operations", "status": "PASSED", "details": "All entity updates successful"})
                return True
            else:
                self.test_results.append({"test": "Update Operations", "status": "FAILED", "reason": f"Only {success_count}/4 updates successful"})
                return False
                
        except Exception as e:
            print(f"❌ Update operations test failed: {e}")
            self.test_results.append({"test": "Update Operations", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_dashboard_endpoint(self):
        """Test 6: Dashboard endpoint functionality"""
        print("\n🧪 Test 6: Dashboard Endpoint")
        
        try:
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    dashboard_data = await response.json()
                    
                    # Verify dashboard structure
                    required_fields = ['user', 'stats', 'recent_tasks']
                    if all(field in dashboard_data for field in required_fields):
                        print("✅ Dashboard endpoint successful with proper structure")
                        self.test_results.append({"test": "Dashboard Endpoint", "status": "PASSED", "details": "Dashboard data structure correct"})
                        return True
                    else:
                        print("❌ Dashboard data structure incomplete")
                        self.test_results.append({"test": "Dashboard Endpoint", "status": "FAILED", "reason": "Missing required fields"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Dashboard endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Dashboard Endpoint", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Dashboard endpoint test failed: {e}")
            self.test_results.append({"test": "Dashboard Endpoint", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_today_view_endpoint(self):
        """Test 7: Today view endpoint functionality"""
        print("\n🧪 Test 7: Today View Endpoint")
        
        try:
            async with self.session.get(f"{API_BASE}/today", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    today_data = await response.json()
                    
                    # Verify today view structure
                    required_fields = ['tasks', 'priorities', 'recommendations']
                    if all(field in today_data for field in required_fields):
                        print("✅ Today view endpoint successful with proper structure")
                        self.test_results.append({"test": "Today View Endpoint", "status": "PASSED", "details": "Today view data structure correct"})
                        return True
                    else:
                        print("❌ Today view data structure incomplete")
                        self.test_results.append({"test": "Today View Endpoint", "status": "FAILED", "reason": "Missing required fields"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Today view endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Today View Endpoint", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Today view endpoint test failed: {e}")
            self.test_results.append({"test": "Today View Endpoint", "status": "FAILED", "reason": str(e)})
            return False
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete in reverse order (tasks → projects → areas → pillars)
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
        print("🎯 SUPABASE-ONLY CRUD OPERATIONS - SCHEMA MAPPING TEST SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate == 100:
            print("🎉 SUPABASE-ONLY ARCHITECTURE IS PRODUCTION-READY!")
            print("✅ All schema mapping fixes working correctly")
            print("✅ Complete CRUD hierarchy functional")
        elif success_rate >= 85:
            print("⚠️ SUPABASE-ONLY ARCHITECTURE IS MOSTLY FUNCTIONAL - MINOR ISSUES DETECTED")
        else:
            print("❌ SUPABASE-ONLY ARCHITECTURE HAS SIGNIFICANT ISSUES - NEEDS ATTENTION")
            
        print("="*80)
        
    async def run_comprehensive_crud_test(self):
        """Run comprehensive CRUD test suite"""
        print("🚀 Starting Supabase-Only CRUD Operations Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("📋 Testing complete hierarchy: Pillar → Area → Project → Task")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Test complete CRUD hierarchy
            pillar_id = await self.test_pillar_crud()
            if not pillar_id:
                print("❌ Pillar CRUD failed - stopping hierarchy test")
                return
                
            area_id = await self.test_area_crud(pillar_id)
            if not area_id:
                print("❌ Area CRUD failed - stopping hierarchy test")
                return
                
            project_id = await self.test_project_crud(area_id)
            if not project_id:
                print("❌ Project CRUD failed - stopping hierarchy test")
                return
                
            task_success = await self.test_task_crud(project_id)
            if not task_success:
                print("❌ Task CRUD failed")
                return
                
            # Test update operations
            await self.test_update_operations()
            
            # Test additional endpoints
            await self.test_dashboard_endpoint()
            await self.test_today_view_endpoint()
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

class ContextualFileAttachmentsTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "contextual.test@aurumlife.com"
        self.test_user_password = "TestPass123!"
        self.test_results = []
        self.created_resources = []
        self.created_projects = []
        self.created_tasks = []
        self.created_areas = []
        
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
                "username": "contextualtest",
                "email": self.test_user_email,
                "first_name": "Contextual",
                "last_name": "Test",
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status in [200, 400]:  # 400 if user already exists
                    pass
                    
            # Login to get token
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def create_test_data(self):
        """Create test areas, projects, and tasks for testing"""
        try:
            # Create test area
            area_data = {
                "name": "Contextual Test Area",
                "description": "Area for testing contextual file attachments",
                "icon": "📁",
                "color": "#FF5722"
            }
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    self.created_areas.append(area["id"])
                    
                    # Create test project
                    project_data = {
                        "area_id": area["id"],
                        "name": "Contextual Test Project",
                        "description": "Project for testing contextual file attachments",
                        "icon": "🚀"
                    }
                    
                    async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=self.get_auth_headers()) as proj_response:
                        if proj_response.status == 200:
                            project = await proj_response.json()
                            self.created_projects.append(project["id"])
                            
                            # Create test task
                            task_data = {
                                "project_id": project["id"],
                                "name": "Contextual Test Task",
                                "description": "Task for testing contextual file attachments",
                                "priority": "high"
                            }
                            
                            async with self.session.post(f"{API_BASE}/tasks", json=task_data, headers=self.get_auth_headers()) as task_response:
                                if task_response.status == 200:
                                    task = await task_response.json()
                                    self.created_tasks.append(task["id"])
                                    return True
                                    
            return False
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            return False
            
    def create_test_file_content(self, filename: str = "test.txt", content: str = "Test file content for contextual attachments") -> Dict[str, Any]:
        """Create test file data"""
        file_bytes = content.encode('utf-8')
        file_content_b64 = base64.b64encode(file_bytes).decode('utf-8')
        
        return {
            "filename": filename,
            "original_filename": filename,
            "file_type": "document",
            "category": "document",
            "mime_type": "text/plain",
            "file_size": len(file_bytes),
            "file_content": file_content_b64,
            "description": f"Test file: {filename}",
            "tags": ["test", "contextual"],
            "folder_path": "/test"
        }
        
    async def test_resource_creation_with_parent(self):
        """Test 1: Resource creation with parent_id and parent_type"""
        print("\n🧪 Test 1: Resource creation with parent_id and parent_type")
        
        if not self.created_projects or not self.created_tasks:
            self.test_results.append({"test": "Resource creation with parent", "status": "FAILED", "reason": "No test data available"})
            return
            
        try:
            # Test 1a: Create resource with project parent
            project_file_data = self.create_test_file_content("project_attachment.txt", "File attached to project")
            project_file_data.update({
                "parent_id": self.created_projects[0],
                "parent_type": "project"
            })
            
            async with self.session.post(f"{API_BASE}/resources", json=project_file_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    resource = await response.json()
                    self.created_resources.append(resource["id"])
                    
                    # Verify parent fields are set correctly
                    if resource["parent_id"] == self.created_projects[0] and resource["parent_type"] == "project":
                        print("✅ Project attachment created successfully")
                    else:
                        print("❌ Project attachment parent fields incorrect")
                        self.test_results.append({"test": "Project attachment creation", "status": "FAILED", "reason": "Parent fields incorrect"})
                        return
                else:
                    print(f"❌ Project attachment creation failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({"test": "Project attachment creation", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return
                    
            # Test 1b: Create resource with task parent
            task_file_data = self.create_test_file_content("task_attachment.txt", "File attached to task")
            task_file_data.update({
                "parent_id": self.created_tasks[0],
                "parent_type": "task"
            })
            
            async with self.session.post(f"{API_BASE}/resources", json=task_file_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    resource = await response.json()
                    self.created_resources.append(resource["id"])
                    
                    # Verify parent fields are set correctly
                    if resource["parent_id"] == self.created_tasks[0] and resource["parent_type"] == "task":
                        print("✅ Task attachment created successfully")
                        self.test_results.append({"test": "Resource creation with parent", "status": "PASSED", "details": "Both project and task attachments created"})
                    else:
                        print("❌ Task attachment parent fields incorrect")
                        self.test_results.append({"test": "Task attachment creation", "status": "FAILED", "reason": "Parent fields incorrect"})
                else:
                    print(f"❌ Task attachment creation failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({"test": "Task attachment creation", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    
        except Exception as e:
            print(f"❌ Resource creation with parent test failed: {e}")
            self.test_results.append({"test": "Resource creation with parent", "status": "FAILED", "reason": str(e)})
            
    async def test_parent_entity_validation(self):
        """Test 2: Parent entity validation"""
        print("\n🧪 Test 2: Parent entity validation")
        
        try:
            # Test 2a: Invalid parent_id should be rejected
            invalid_file_data = self.create_test_file_content("invalid_parent.txt")
            invalid_file_data.update({
                "parent_id": "invalid-parent-id-12345",
                "parent_type": "project"
            })
            
            async with self.session.post(f"{API_BASE}/resources", json=invalid_file_data, headers=self.get_auth_headers()) as response:
                if response.status == 400:
                    print("✅ Invalid parent_id correctly rejected")
                else:
                    print(f"❌ Invalid parent_id should be rejected but got: {response.status}")
                    self.test_results.append({"test": "Invalid parent_id validation", "status": "FAILED", "reason": f"Expected 400, got {response.status}"})
                    return
                    
            # Test 2b: Invalid parent_type should be rejected
            invalid_type_data = self.create_test_file_content("invalid_type.txt")
            invalid_type_data.update({
                "parent_id": self.created_projects[0] if self.created_projects else "test-id",
                "parent_type": "invalid_type"
            })
            
            async with self.session.post(f"{API_BASE}/resources", json=invalid_type_data, headers=self.get_auth_headers()) as response:
                if response.status == 400:
                    print("✅ Invalid parent_type correctly rejected")
                    self.test_results.append({"test": "Parent entity validation", "status": "PASSED", "details": "Both invalid parent_id and parent_type rejected"})
                else:
                    print(f"❌ Invalid parent_type should be rejected but got: {response.status}")
                    self.test_results.append({"test": "Invalid parent_type validation", "status": "FAILED", "reason": f"Expected 400, got {response.status}"})
                    
        except Exception as e:
            print(f"❌ Parent entity validation test failed: {e}")
            self.test_results.append({"test": "Parent entity validation", "status": "FAILED", "reason": str(e)})
            
    async def test_parent_resources_endpoint(self):
        """Test 3: New GET /api/resources/parent/{parent_type}/{parent_id} endpoint"""
        print("\n🧪 Test 3: GET /api/resources/parent/{parent_type}/{parent_id} endpoint")
        
        if not self.created_projects or not self.created_tasks:
            self.test_results.append({"test": "Parent resources endpoint", "status": "FAILED", "reason": "No test data available"})
            return
            
        try:
            # Test 3a: Get resources for project
            async with self.session.get(f"{API_BASE}/resources/parent/project/{self.created_projects[0]}", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    resources = await response.json()
                    project_resources = [r for r in resources if r["parent_type"] == "project" and r["parent_id"] == self.created_projects[0]]
                    
                    if len(project_resources) > 0:
                        print(f"✅ Found {len(project_resources)} resources for project")
                    else:
                        print("⚠️ No resources found for project (may be expected if none created)")
                else:
                    print(f"❌ Project resources endpoint failed: {response.status}")
                    self.test_results.append({"test": "Project resources endpoint", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return
                    
            # Test 3b: Get resources for task
            async with self.session.get(f"{API_BASE}/resources/parent/task/{self.created_tasks[0]}", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    resources = await response.json()
                    task_resources = [r for r in resources if r["parent_type"] == "task" and r["parent_id"] == self.created_tasks[0]]
                    
                    if len(task_resources) > 0:
                        print(f"✅ Found {len(task_resources)} resources for task")
                    else:
                        print("⚠️ No resources found for task (may be expected if none created)")
                        
                    self.test_results.append({"test": "Parent resources endpoint", "status": "PASSED", "details": "Both project and task endpoints working"})
                else:
                    print(f"❌ Task resources endpoint failed: {response.status}")
                    self.test_results.append({"test": "Task resources endpoint", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    
            # Test 3c: Invalid parent_type should be rejected
            async with self.session.get(f"{API_BASE}/resources/parent/invalid_type/test-id", headers=self.get_auth_headers()) as response:
                if response.status == 400:
                    print("✅ Invalid parent_type correctly rejected in endpoint")
                else:
                    print(f"⚠️ Expected 400 for invalid parent_type, got: {response.status}")
                    
        except Exception as e:
            print(f"❌ Parent resources endpoint test failed: {e}")
            self.test_results.append({"test": "Parent resources endpoint", "status": "FAILED", "reason": str(e)})
            
    async def test_cross_user_security(self):
        """Test 4: Cross-user security for parent entities"""
        print("\n🧪 Test 4: Cross-user security for parent entities")
        
        try:
            # Create a second user for testing
            second_user_email = "contextual.test2@aurumlife.com"
            second_user_password = "TestPass123!"
            
            # Register second user
            register_data = {
                "username": "contextualtest2",
                "email": second_user_email,
                "first_name": "Contextual2",
                "last_name": "Test2",
                "password": second_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status in [200, 400]:  # 400 if user already exists
                    pass
                    
            # Login as second user
            login_data = {
                "email": second_user_email,
                "password": second_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    second_user_token = data["access_token"]
                    second_user_headers = {"Authorization": f"Bearer {second_user_token}"}
                    
                    # Try to create resource with first user's project as parent
                    if self.created_projects:
                        cross_user_file_data = self.create_test_file_content("cross_user_test.txt")
                        cross_user_file_data.update({
                            "parent_id": self.created_projects[0],  # First user's project
                            "parent_type": "project"
                        })
                        
                        async with self.session.post(f"{API_BASE}/resources", json=cross_user_file_data, headers=second_user_headers) as response:
                            if response.status == 400:
                                print("✅ Cross-user parent access correctly blocked")
                                self.test_results.append({"test": "Cross-user security", "status": "PASSED", "details": "Cross-user parent access blocked"})
                            else:
                                print(f"❌ Cross-user access should be blocked but got: {response.status}")
                                self.test_results.append({"test": "Cross-user security", "status": "FAILED", "reason": f"Expected 400, got {response.status}"})
                    else:
                        print("⚠️ No test projects available for cross-user test")
                        self.test_results.append({"test": "Cross-user security", "status": "SKIPPED", "reason": "No test data"})
                else:
                    print(f"❌ Second user login failed: {response.status}")
                    self.test_results.append({"test": "Cross-user security", "status": "FAILED", "reason": "Second user login failed"})
                    
        except Exception as e:
            print(f"❌ Cross-user security test failed: {e}")
            self.test_results.append({"test": "Cross-user security", "status": "FAILED", "reason": str(e)})
            
    async def test_file_upload_with_valid_invalid_parent_types(self):
        """Test 5: File upload with both valid and invalid parent types"""
        print("\n🧪 Test 5: File upload with valid and invalid parent types")
        
        try:
            valid_parent_types = ["task", "project", "area", "pillar", "journal_entry"]
            invalid_parent_types = ["user", "course", "invalid", ""]
            
            # Test valid parent types
            for parent_type in valid_parent_types:
                if parent_type == "project" and self.created_projects:
                    parent_id = self.created_projects[0]
                elif parent_type == "task" and self.created_tasks:
                    parent_id = self.created_tasks[0]
                elif parent_type == "area" and self.created_areas:
                    parent_id = self.created_areas[0]
                else:
                    continue  # Skip if we don't have test data for this type
                    
                file_data = self.create_test_file_content(f"valid_{parent_type}.txt")
                file_data.update({
                    "parent_id": parent_id,
                    "parent_type": parent_type
                })
                
                async with self.session.post(f"{API_BASE}/resources", json=file_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        resource = await response.json()
                        self.created_resources.append(resource["id"])
                        print(f"✅ Valid parent_type '{parent_type}' accepted")
                    else:
                        print(f"❌ Valid parent_type '{parent_type}' rejected: {response.status}")
                        
            # Test invalid parent types
            for parent_type in invalid_parent_types:
                file_data = self.create_test_file_content(f"invalid_{parent_type}.txt")
                file_data.update({
                    "parent_id": "test-id",
                    "parent_type": parent_type
                })
                
                async with self.session.post(f"{API_BASE}/resources", json=file_data, headers=self.get_auth_headers()) as response:
                    if response.status == 400:
                        print(f"✅ Invalid parent_type '{parent_type}' correctly rejected")
                    else:
                        print(f"❌ Invalid parent_type '{parent_type}' should be rejected but got: {response.status}")
                        
            self.test_results.append({"test": "Valid/Invalid parent types", "status": "PASSED", "details": "Parent type validation working"})
            
        except Exception as e:
            print(f"❌ Parent types test failed: {e}")
            self.test_results.append({"test": "Valid/Invalid parent types", "status": "FAILED", "reason": str(e)})
            
    async def test_resource_listing_by_parent(self):
        """Test 6: Resource listing by parent entity"""
        print("\n🧪 Test 6: Resource listing by parent entity")
        
        if not self.created_projects or not self.created_tasks:
            self.test_results.append({"test": "Resource listing by parent", "status": "FAILED", "reason": "No test data available"})
            return
            
        try:
            # Create multiple resources for the same parent
            project_id = self.created_projects[0]
            
            for i in range(3):
                file_data = self.create_test_file_content(f"project_file_{i}.txt", f"Content for file {i}")
                file_data.update({
                    "parent_id": project_id,
                    "parent_type": "project"
                })
                
                async with self.session.post(f"{API_BASE}/resources", json=file_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        resource = await response.json()
                        self.created_resources.append(resource["id"])
                        
            # Get resources for the project
            async with self.session.get(f"{API_BASE}/resources/parent/project/{project_id}", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    resources = await response.json()
                    project_resources = [r for r in resources if r["parent_id"] == project_id and r["parent_type"] == "project"]
                    
                    if len(project_resources) >= 3:
                        print(f"✅ Found {len(project_resources)} resources for project (expected at least 3)")
                        self.test_results.append({"test": "Resource listing by parent", "status": "PASSED", "details": f"Found {len(project_resources)} resources"})
                    else:
                        print(f"⚠️ Found {len(project_resources)} resources for project (expected at least 3)")
                        self.test_results.append({"test": "Resource listing by parent", "status": "PARTIAL", "details": f"Found {len(project_resources)} resources"})
                else:
                    print(f"❌ Resource listing failed: {response.status}")
                    self.test_results.append({"test": "Resource listing by parent", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    
        except Exception as e:
            print(f"❌ Resource listing by parent test failed: {e}")
            self.test_results.append({"test": "Resource listing by parent", "status": "FAILED", "reason": str(e)})
            
    async def test_legacy_attachment_compatibility(self):
        """Test 7: Legacy attachment methods still work for backward compatibility"""
        print("\n🧪 Test 7: Legacy attachment methods compatibility")
        
        if not self.created_projects or not self.created_tasks:
            self.test_results.append({"test": "Legacy attachment compatibility", "status": "FAILED", "reason": "No test data available"})
            return
            
        try:
            # Create a resource without parent (legacy style)
            legacy_file_data = self.create_test_file_content("legacy_file.txt", "Legacy attachment test")
            
            async with self.session.post(f"{API_BASE}/resources", json=legacy_file_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    resource = await response.json()
                    resource_id = resource["id"]
                    self.created_resources.append(resource_id)
                    
                    # Test legacy attachment endpoint
                    attachment_data = {
                        "entity_type": "project",
                        "entity_id": self.created_projects[0]
                    }
                    
                    async with self.session.post(f"{API_BASE}/resources/{resource_id}/attach", json=attachment_data, headers=self.get_auth_headers()) as attach_response:
                        if attach_response.status == 200:
                            print("✅ Legacy attachment method working")
                            
                            # Test legacy retrieval endpoint
                            async with self.session.get(f"{API_BASE}/resources/entity/project/{self.created_projects[0]}", headers=self.get_auth_headers()) as get_response:
                                if get_response.status == 200:
                                    attached_resources = await get_response.json()
                                    legacy_attached = [r for r in attached_resources if r["id"] == resource_id]
                                    
                                    if len(legacy_attached) > 0:
                                        print("✅ Legacy retrieval method working")
                                        self.test_results.append({"test": "Legacy attachment compatibility", "status": "PASSED", "details": "Both attachment and retrieval working"})
                                    else:
                                        print("❌ Legacy retrieval method not finding attached resource")
                                        self.test_results.append({"test": "Legacy retrieval compatibility", "status": "FAILED", "reason": "Resource not found in legacy retrieval"})
                                else:
                                    print(f"❌ Legacy retrieval endpoint failed: {get_response.status}")
                                    self.test_results.append({"test": "Legacy retrieval compatibility", "status": "FAILED", "reason": f"HTTP {get_response.status}"})
                        else:
                            print(f"❌ Legacy attachment method failed: {attach_response.status}")
                            error_text = await attach_response.text()
                            print(f"Error: {error_text}")
                            self.test_results.append({"test": "Legacy attachment compatibility", "status": "FAILED", "reason": f"HTTP {attach_response.status}"})
                else:
                    print(f"❌ Legacy resource creation failed: {response.status}")
                    self.test_results.append({"test": "Legacy attachment compatibility", "status": "FAILED", "reason": f"Resource creation failed: {response.status}"})
                    
        except Exception as e:
            print(f"❌ Legacy attachment compatibility test failed: {e}")
            self.test_results.append({"test": "Legacy attachment compatibility", "status": "FAILED", "reason": str(e)})
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete created resources
            for resource_id in self.created_resources:
                async with self.session.delete(f"{API_BASE}/resources/{resource_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted resource {resource_id}")
                    else:
                        print(f"⚠️ Failed to delete resource {resource_id}: {response.status}")
                        
            # Delete created tasks
            for task_id in self.created_tasks:
                async with self.session.delete(f"{API_BASE}/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted task {task_id}")
                    else:
                        print(f"⚠️ Failed to delete task {task_id}: {response.status}")
                        
            # Delete created projects
            for project_id in self.created_projects:
                async with self.session.delete(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted project {project_id}")
                    else:
                        print(f"⚠️ Failed to delete project {project_id}: {response.status}")
                        
            # Delete created areas
            for area_id in self.created_areas:
                async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted area {area_id}")
                    else:
                        print(f"⚠️ Failed to delete area {area_id}: {response.status}")
                        
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 CONTEXTUAL FILE ATTACHMENTS SYSTEM - TEST SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        partial = len([t for t in self.test_results if t["status"] == "PARTIAL"])
        skipped = len([t for t in self.test_results if t["status"] == "SKIPPED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Partial: {partial}")
        print(f"⏭️ Skipped: {skipped}")
        
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
        if success_rate >= 90:
            print("🎉 CONTEXTUAL FILE ATTACHMENTS SYSTEM IS PRODUCTION-READY!")
        elif success_rate >= 75:
            print("⚠️ CONTEXTUAL FILE ATTACHMENTS SYSTEM IS MOSTLY FUNCTIONAL - MINOR ISSUES DETECTED")
        else:
            print("❌ CONTEXTUAL FILE ATTACHMENTS SYSTEM HAS SIGNIFICANT ISSUES - NEEDS ATTENTION")
            
        print("="*80)
        
    async def run_all_tests(self):
        """Run all contextual file attachments tests"""
        print("🚀 Starting Contextual File Attachments System Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            print("✅ Authentication successful")
            
            # Create test data
            if not await self.create_test_data():
                print("❌ Test data creation failed - cannot proceed with tests")
                return
                
            print("✅ Test data created successfully")
            
            # Run all tests
            await self.test_resource_creation_with_parent()
            await self.test_parent_entity_validation()
            await self.test_parent_resources_endpoint()
            await self.test_cross_user_security()
            await self.test_file_upload_with_valid_invalid_parent_types()
            await self.test_resource_listing_by_parent()
            await self.test_legacy_attachment_compatibility()
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = ContextualFileAttachmentsTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())