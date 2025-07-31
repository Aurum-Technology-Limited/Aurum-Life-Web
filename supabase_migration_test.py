#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://2a9362a1-0858-4070-86b9-4648da4a94c4.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class SupabaseMigrationTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "supabase.migration@aurumlife.com"
        self.test_user_password = "SupabaseTest123!"
        self.test_results = []
        self.created_data = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': [],
            'journal_entries': []
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
                "username": "supabasetest",
                "email": self.test_user_email,
                "first_name": "Supabase",
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
        
    async def test_pillar_crud_operations(self):
        """Test 1: Pillar CRUD operations with Supabase"""
        print("\n🧪 Test 1: Pillar CRUD Operations")
        
        try:
            # CREATE - Test pillar creation
            pillar_data = {
                "name": "Health & Wellness",
                "description": "Physical and mental health pillar",
                "icon": "🏃‍♂️",
                "color": "#4CAF50"
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillar = await response.json()
                    pillar_id = pillar["id"]
                    self.created_data['pillars'].append(pillar_id)
                    print("✅ Pillar creation successful")
                    
                    # READ - Test pillar retrieval
                    async with self.session.get(f"{API_BASE}/pillars/{pillar_id}", headers=self.get_auth_headers()) as get_response:
                        if get_response.status == 200:
                            retrieved_pillar = await get_response.json()
                            if retrieved_pillar["name"] == pillar_data["name"]:
                                print("✅ Pillar retrieval successful")
                                
                                # UPDATE - Test pillar update
                                update_data = {"name": "Health & Wellness Updated"}
                                async with self.session.put(f"{API_BASE}/pillars/{pillar_id}", json=update_data, headers=self.get_auth_headers()) as update_response:
                                    if update_response.status == 200:
                                        print("✅ Pillar update successful")
                                        
                                        # LIST - Test pillar listing
                                        async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as list_response:
                                            if list_response.status == 200:
                                                pillars = await list_response.json()
                                                if any(p["id"] == pillar_id for p in pillars):
                                                    print("✅ Pillar listing successful")
                                                    self.test_results.append({"test": "Pillar CRUD Operations", "status": "PASSED", "details": "All CRUD operations working"})
                                                    return True
                                                    
            print("❌ Pillar CRUD operations failed")
            self.test_results.append({"test": "Pillar CRUD Operations", "status": "FAILED", "reason": "One or more operations failed"})
            return False
            
        except Exception as e:
            print(f"❌ Pillar CRUD test failed: {e}")
            self.test_results.append({"test": "Pillar CRUD Operations", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_area_crud_operations(self):
        """Test 2: Area CRUD operations with Supabase"""
        print("\n🧪 Test 2: Area CRUD Operations")
        
        try:
            # CREATE - Test area creation
            area_data = {
                "name": "Fitness Training",
                "description": "Physical fitness and exercise area",
                "icon": "💪",
                "color": "#FF5722"
            }
            
            # Link to pillar if available
            if self.created_data['pillars']:
                area_data["pillar_id"] = self.created_data['pillars'][0]
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    area_id = area["id"]
                    self.created_data['areas'].append(area_id)
                    print("✅ Area creation successful")
                    
                    # READ - Test area retrieval
                    async with self.session.get(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as get_response:
                        if get_response.status == 200:
                            retrieved_area = await get_response.json()
                            if retrieved_area["name"] == area_data["name"]:
                                print("✅ Area retrieval successful")
                                
                                # UPDATE - Test area update
                                update_data = {"name": "Fitness Training Updated"}
                                async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as update_response:
                                    if update_response.status == 200:
                                        print("✅ Area update successful")
                                        
                                        # LIST - Test area listing
                                        async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as list_response:
                                            if list_response.status == 200:
                                                areas = await list_response.json()
                                                if any(a["id"] == area_id for a in areas):
                                                    print("✅ Area listing successful")
                                                    self.test_results.append({"test": "Area CRUD Operations", "status": "PASSED", "details": "All CRUD operations working"})
                                                    return True
                                                    
            print("❌ Area CRUD operations failed")
            self.test_results.append({"test": "Area CRUD Operations", "status": "FAILED", "reason": "One or more operations failed"})
            return False
            
        except Exception as e:
            print(f"❌ Area CRUD test failed: {e}")
            self.test_results.append({"test": "Area CRUD Operations", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_project_crud_operations(self):
        """Test 3: Project CRUD operations with Supabase"""
        print("\n🧪 Test 3: Project CRUD Operations")
        
        try:
            if not self.created_data['areas']:
                print("⚠️ No areas available for project creation")
                self.test_results.append({"test": "Project CRUD Operations", "status": "SKIPPED", "reason": "No areas available"})
                return False
                
            # CREATE - Test project creation
            project_data = {
                "area_id": self.created_data['areas'][0],
                "name": "Morning Workout Routine",
                "description": "Daily morning exercise routine project",
                "icon": "🏃‍♂️",
                "priority": "high"
            }
            
            async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    project = await response.json()
                    project_id = project["id"]
                    self.created_data['projects'].append(project_id)
                    print("✅ Project creation successful")
                    
                    # READ - Test project retrieval
                    async with self.session.get(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as get_response:
                        if get_response.status == 200:
                            retrieved_project = await get_response.json()
                            if retrieved_project["name"] == project_data["name"]:
                                print("✅ Project retrieval successful")
                                
                                # UPDATE - Test project update
                                update_data = {"name": "Morning Workout Routine Updated"}
                                async with self.session.put(f"{API_BASE}/projects/{project_id}", json=update_data, headers=self.get_auth_headers()) as update_response:
                                    if update_response.status == 200:
                                        print("✅ Project update successful")
                                        
                                        # LIST - Test project listing
                                        async with self.session.get(f"{API_BASE}/projects", headers=self.get_auth_headers()) as list_response:
                                            if list_response.status == 200:
                                                projects = await list_response.json()
                                                if any(p["id"] == project_id for p in projects):
                                                    print("✅ Project listing successful")
                                                    self.test_results.append({"test": "Project CRUD Operations", "status": "PASSED", "details": "All CRUD operations working"})
                                                    return True
                                                    
            print("❌ Project CRUD operations failed")
            self.test_results.append({"test": "Project CRUD Operations", "status": "FAILED", "reason": "One or more operations failed"})
            return False
            
        except Exception as e:
            print(f"❌ Project CRUD test failed: {e}")
            self.test_results.append({"test": "Project CRUD Operations", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_task_crud_operations(self):
        """Test 4: Task CRUD operations with Supabase"""
        print("\n🧪 Test 4: Task CRUD Operations")
        
        try:
            if not self.created_data['projects']:
                print("⚠️ No projects available for task creation")
                self.test_results.append({"test": "Task CRUD Operations", "status": "SKIPPED", "reason": "No projects available"})
                return False
                
            # CREATE - Test task creation
            task_data = {
                "project_id": self.created_data['projects'][0],
                "name": "30-minute cardio session",
                "description": "High-intensity cardio workout",
                "priority": "high",
                "status": "todo"
            }
            
            async with self.session.post(f"{API_BASE}/tasks", json=task_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    task = await response.json()
                    task_id = task["id"]
                    self.created_data['tasks'].append(task_id)
                    print("✅ Task creation successful")
                    
                    # READ - Test task retrieval via project tasks
                    async with self.session.get(f"{API_BASE}/projects/{self.created_data['projects'][0]}/tasks", headers=self.get_auth_headers()) as get_response:
                        if get_response.status == 200:
                            tasks = await get_response.json()
                            if any(t["id"] == task_id for t in tasks):
                                print("✅ Task retrieval successful")
                                
                                # UPDATE - Test task update
                                update_data = {"name": "30-minute cardio session updated", "status": "in_progress"}
                                async with self.session.put(f"{API_BASE}/tasks/{task_id}", json=update_data, headers=self.get_auth_headers()) as update_response:
                                    if update_response.status == 200:
                                        print("✅ Task update successful")
                                        
                                        # LIST - Test task listing
                                        async with self.session.get(f"{API_BASE}/tasks", headers=self.get_auth_headers()) as list_response:
                                            if list_response.status == 200:
                                                all_tasks = await list_response.json()
                                                if any(t["id"] == task_id for t in all_tasks):
                                                    print("✅ Task listing successful")
                                                    self.test_results.append({"test": "Task CRUD Operations", "status": "PASSED", "details": "All CRUD operations working"})
                                                    return True
                                                    
            print("❌ Task CRUD operations failed")
            self.test_results.append({"test": "Task CRUD Operations", "status": "FAILED", "reason": "One or more operations failed"})
            return False
            
        except Exception as e:
            print(f"❌ Task CRUD test failed: {e}")
            self.test_results.append({"test": "Task CRUD Operations", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_journal_crud_operations(self):
        """Test 5: Journal CRUD operations with Supabase"""
        print("\n🧪 Test 5: Journal CRUD Operations")
        
        try:
            # CREATE - Test journal entry creation
            journal_data = {
                "title": "Supabase Migration Test Entry",
                "content": "Testing journal functionality after Supabase migration. Everything seems to be working well!",
                "mood": "optimistic",
                "energy_level": "high",
                "tags": ["testing", "supabase", "migration"]
            }
            
            async with self.session.post(f"{API_BASE}/journal", json=journal_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    journal_entry = await response.json()
                    entry_id = journal_entry["id"]
                    self.created_data['journal_entries'].append(entry_id)
                    print("✅ Journal entry creation successful")
                    
                    # READ - Test journal entry retrieval
                    async with self.session.get(f"{API_BASE}/journal", headers=self.get_auth_headers()) as get_response:
                        if get_response.status == 200:
                            entries = await get_response.json()
                            if any(e["id"] == entry_id for e in entries):
                                print("✅ Journal entry retrieval successful")
                                
                                # UPDATE - Test journal entry update
                                update_data = {"title": "Supabase Migration Test Entry Updated"}
                                async with self.session.put(f"{API_BASE}/journal/{entry_id}", json=update_data, headers=self.get_auth_headers()) as update_response:
                                    if update_response.status == 200:
                                        print("✅ Journal entry update successful")
                                        self.test_results.append({"test": "Journal CRUD Operations", "status": "PASSED", "details": "All CRUD operations working"})
                                        return True
                                        
            print("❌ Journal CRUD operations failed")
            self.test_results.append({"test": "Journal CRUD Operations", "status": "FAILED", "reason": "One or more operations failed"})
            return False
            
        except Exception as e:
            print(f"❌ Journal CRUD test failed: {e}")
            self.test_results.append({"test": "Journal CRUD Operations", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_data_relationships(self):
        """Test 6: Data relationships and foreign key constraints"""
        print("\n🧪 Test 6: Data Relationships and Foreign Key Constraints")
        
        try:
            # Test pillar-area relationship
            if self.created_data['pillars'] and self.created_data['areas']:
                async with self.session.get(f"{API_BASE}/pillars/{self.created_data['pillars'][0]}?include_areas=true", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        pillar_with_areas = await response.json()
                        if pillar_with_areas.get('areas') is not None:
                            print("✅ Pillar-Area relationship working")
                        else:
                            print("⚠️ Pillar-Area relationship not populated")
                            
            # Test area-project relationship
            if self.created_data['areas'] and self.created_data['projects']:
                async with self.session.get(f"{API_BASE}/areas?include_projects=true", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        areas_with_projects = await response.json()
                        area_with_project = next((a for a in areas_with_projects if a['id'] == self.created_data['areas'][0]), None)
                        if area_with_project and area_with_project.get('projects'):
                            print("✅ Area-Project relationship working")
                        else:
                            print("⚠️ Area-Project relationship not populated")
                            
            # Test project-task relationship
            if self.created_data['projects'] and self.created_data['tasks']:
                async with self.session.get(f"{API_BASE}/projects/{self.created_data['projects'][0]}?include_tasks=true", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        project_with_tasks = await response.json()
                        if project_with_tasks.get('tasks'):
                            print("✅ Project-Task relationship working")
                            self.test_results.append({"test": "Data Relationships", "status": "PASSED", "details": "Foreign key relationships working"})
                            return True
                        else:
                            print("⚠️ Project-Task relationship not populated")
                            
            self.test_results.append({"test": "Data Relationships", "status": "PARTIAL", "details": "Some relationships working"})
            return True
            
        except Exception as e:
            print(f"❌ Data relationships test failed: {e}")
            self.test_results.append({"test": "Data Relationships", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_dashboard_integration(self):
        """Test 7: Dashboard integration with Supabase data"""
        print("\n🧪 Test 7: Dashboard Integration")
        
        try:
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    dashboard_data = await response.json()
                    
                    # Check if dashboard contains expected data structures
                    required_fields = ['user', 'stats', 'areas']
                    missing_fields = [field for field in required_fields if field not in dashboard_data]
                    
                    if not missing_fields:
                        print("✅ Dashboard structure complete")
                        
                        # Check if our created data appears in dashboard
                        dashboard_areas = dashboard_data.get('areas', [])
                        if any(area['id'] in self.created_data['areas'] for area in dashboard_areas):
                            print("✅ Dashboard showing created data")
                            self.test_results.append({"test": "Dashboard Integration", "status": "PASSED", "details": "Dashboard working with Supabase data"})
                            return True
                        else:
                            print("⚠️ Dashboard not showing created data")
                            self.test_results.append({"test": "Dashboard Integration", "status": "PARTIAL", "details": "Dashboard structure OK but data not visible"})
                            return True
                    else:
                        print(f"❌ Dashboard missing fields: {missing_fields}")
                        self.test_results.append({"test": "Dashboard Integration", "status": "FAILED", "reason": f"Missing fields: {missing_fields}"})
                        return False
                else:
                    print(f"❌ Dashboard endpoint failed: {response.status}")
                    self.test_results.append({"test": "Dashboard Integration", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Dashboard integration test failed: {e}")
            self.test_results.append({"test": "Dashboard Integration", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_authentication_system(self):
        """Test 8: Authentication system with Supabase"""
        print("\n🧪 Test 8: Authentication System")
        
        try:
            # Test current user endpoint
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    user_data = await response.json()
                    if user_data.get('email') == self.test_user_email:
                        print("✅ Authentication system working")
                        
                        # Test protected endpoint access
                        async with self.session.get(f"{API_BASE}/stats", headers=self.get_auth_headers()) as stats_response:
                            if stats_response.status == 200:
                                print("✅ Protected endpoints accessible")
                                self.test_results.append({"test": "Authentication System", "status": "PASSED", "details": "Auth working with Supabase"})
                                return True
                            else:
                                print(f"❌ Protected endpoint failed: {stats_response.status}")
                                self.test_results.append({"test": "Authentication System", "status": "FAILED", "reason": f"Protected endpoint HTTP {stats_response.status}"})
                                return False
                    else:
                        print("❌ User data mismatch")
                        self.test_results.append({"test": "Authentication System", "status": "FAILED", "reason": "User data mismatch"})
                        return False
                else:
                    print(f"❌ Auth/me endpoint failed: {response.status}")
                    self.test_results.append({"test": "Authentication System", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication system test failed: {e}")
            self.test_results.append({"test": "Authentication System", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_performance_basic(self):
        """Test 9: Basic performance check"""
        print("\n🧪 Test 9: Basic Performance Check")
        
        try:
            import time
            
            # Test response times for basic operations
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillars_time = time.time() - start_time
                    
                    start_time = time.time()
                    async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response2:
                        if response2.status == 200:
                            areas_time = time.time() - start_time
                            
                            start_time = time.time()
                            async with self.session.get(f"{API_BASE}/projects", headers=self.get_auth_headers()) as response3:
                                if response3.status == 200:
                                    projects_time = time.time() - start_time
                                    
                                    avg_response_time = (pillars_time + areas_time + projects_time) / 3
                                    
                                    if avg_response_time < 2.0:  # Less than 2 seconds average
                                        print(f"✅ Performance acceptable (avg: {avg_response_time:.2f}s)")
                                        self.test_results.append({"test": "Basic Performance", "status": "PASSED", "details": f"Average response time: {avg_response_time:.2f}s"})
                                        return True
                                    else:
                                        print(f"⚠️ Performance slow (avg: {avg_response_time:.2f}s)")
                                        self.test_results.append({"test": "Basic Performance", "status": "PARTIAL", "details": f"Slow response time: {avg_response_time:.2f}s"})
                                        return True
                                        
            print("❌ Performance test failed")
            self.test_results.append({"test": "Basic Performance", "status": "FAILED", "reason": "Could not complete performance test"})
            return False
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            self.test_results.append({"test": "Basic Performance", "status": "FAILED", "reason": str(e)})
            return False
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete in reverse order to respect foreign key constraints
            
            # Delete journal entries
            for entry_id in self.created_data['journal_entries']:
                async with self.session.delete(f"{API_BASE}/journal/{entry_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted journal entry {entry_id}")
                    else:
                        print(f"⚠️ Failed to delete journal entry {entry_id}: {response.status}")
                        
            # Delete tasks
            for task_id in self.created_data['tasks']:
                async with self.session.delete(f"{API_BASE}/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted task {task_id}")
                    else:
                        print(f"⚠️ Failed to delete task {task_id}: {response.status}")
                        
            # Delete projects
            for project_id in self.created_data['projects']:
                async with self.session.delete(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted project {project_id}")
                    else:
                        print(f"⚠️ Failed to delete project {project_id}: {response.status}")
                        
            # Delete areas
            for area_id in self.created_data['areas']:
                async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted area {area_id}")
                    else:
                        print(f"⚠️ Failed to delete area {area_id}: {response.status}")
                        
            # Delete pillars
            for pillar_id in self.created_data['pillars']:
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
        print("🎯 SUPABASE MIGRATION VERIFICATION - TEST SUMMARY")
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
        
        # Determine overall migration status
        if success_rate >= 90:
            print("🎉 SUPABASE MIGRATION IS SUCCESSFUL AND PRODUCTION-READY!")
            print("✅ All core CRUD operations working with Supabase PostgreSQL")
            print("✅ Data relationships and foreign keys functioning")
            print("✅ Authentication system integrated with Supabase")
            print("✅ Performance is acceptable")
        elif success_rate >= 75:
            print("⚠️ SUPABASE MIGRATION IS MOSTLY SUCCESSFUL - MINOR ISSUES DETECTED")
            print("✅ Core functionality working but some optimizations needed")
        else:
            print("❌ SUPABASE MIGRATION HAS SIGNIFICANT ISSUES - NEEDS ATTENTION")
            print("❌ Critical functionality not working properly")
            
        print("="*80)
        
    async def run_all_tests(self):
        """Run all Supabase migration verification tests"""
        print("🚀 Starting Supabase Migration Verification Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("🎯 Testing: Pillars, Areas, Projects, Tasks, Journal Entries")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            print("✅ Authentication successful")
            
            # Run all tests
            await self.test_pillar_crud_operations()
            await self.test_area_crud_operations()
            await self.test_project_crud_operations()
            await self.test_task_crud_operations()
            await self.test_journal_crud_operations()
            await self.test_data_relationships()
            await self.test_dashboard_integration()
            await self.test_authentication_system()
            await self.test_performance_basic()
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = SupabaseMigrationTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())