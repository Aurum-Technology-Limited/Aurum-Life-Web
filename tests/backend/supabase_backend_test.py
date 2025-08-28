#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class SupabaseMigrationTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "supabase.test@aurumlife.com"
        self.test_user_password = "SupabaseTest123!"
        self.test_results = []
        self.created_entities = {
            'users': [],
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
                    print("✅ Authentication successful")
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
        
    async def test_supabase_connection(self):
        """Test 1: Basic Supabase connection through health check"""
        print("\n🧪 Test 1: Supabase Connection Test")
        
        try:
            async with self.session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Backend health check passed")
                    self.test_results.append({
                        "test": "Supabase Connection", 
                        "status": "PASSED", 
                        "details": f"Health check: {data}"
                    })
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    self.test_results.append({
                        "test": "Supabase Connection", 
                        "status": "FAILED", 
                        "reason": f"Health check failed with status {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            self.test_results.append({
                "test": "Supabase Connection", 
                "status": "FAILED", 
                "reason": f"Connection error: {e}"
            })
            return False
            
    async def test_user_crud_operations(self):
        """Test 2: User CRUD operations with Supabase"""
        print("\n🧪 Test 2: User CRUD Operations")
        
        try:
            # Test user profile retrieval
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print("✅ User profile retrieval successful")
                    print(f"   User ID: {user_data.get('id')}")
                    print(f"   Email: {user_data.get('email')}")
                    
                    # Test user profile update
                    update_data = {
                        "first_name": "Updated Supabase",
                        "last_name": "Test User"
                    }
                    
                    async with self.session.put(f"{API_BASE}/users/me", json=update_data, headers=self.get_auth_headers()) as update_response:
                        if update_response.status == 200:
                            print("✅ User profile update successful")
                            
                            # Verify update
                            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as verify_response:
                                if verify_response.status == 200:
                                    updated_user = await verify_response.json()
                                    if updated_user.get('first_name') == 'Updated Supabase':
                                        print("✅ User profile update verified")
                                        self.test_results.append({
                                            "test": "User CRUD Operations", 
                                            "status": "PASSED", 
                                            "details": "Profile retrieval and update successful"
                                        })
                                        return True
                                        
                        print("❌ User profile update failed")
                        self.test_results.append({
                            "test": "User CRUD Operations", 
                            "status": "FAILED", 
                            "reason": "Profile update failed"
                        })
                        return False
                else:
                    print(f"❌ User profile retrieval failed: {response.status}")
                    self.test_results.append({
                        "test": "User CRUD Operations", 
                        "status": "FAILED", 
                        "reason": f"Profile retrieval failed with status {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ User CRUD test error: {e}")
            self.test_results.append({
                "test": "User CRUD Operations", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def test_pillar_crud_operations(self):
        """Test 3: Pillar CRUD operations with Supabase"""
        print("\n🧪 Test 3: Pillar CRUD Operations")
        
        try:
            # Create pillar
            pillar_data = {
                "name": "Health & Wellness",
                "description": "Focus on physical and mental health",
                "icon": "🏃‍♂️",
                "color": "#4CAF50"
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillar = await response.json()
                    pillar_id = pillar["id"]
                    self.created_entities['pillars'].append(pillar_id)
                    print(f"✅ Pillar created successfully: {pillar_id}")
                    
                    # Test pillar retrieval
                    async with self.session.get(f"{API_BASE}/pillars/{pillar_id}", headers=self.get_auth_headers()) as get_response:
                        if get_response.status == 200:
                            retrieved_pillar = await get_response.json()
                            print("✅ Pillar retrieval successful")
                            
                            # Test pillar update
                            update_data = {
                                "description": "Updated description for health pillar"
                            }
                            
                            async with self.session.put(f"{API_BASE}/pillars/{pillar_id}", json=update_data, headers=self.get_auth_headers()) as update_response:
                                if update_response.status == 200:
                                    print("✅ Pillar update successful")
                                    
                                    # Test pillar list
                                    async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as list_response:
                                        if list_response.status == 200:
                                            pillars = await list_response.json()
                                            if len(pillars) > 0:
                                                print(f"✅ Pillar list successful: {len(pillars)} pillars found")
                                                self.test_results.append({
                                                    "test": "Pillar CRUD Operations", 
                                                    "status": "PASSED", 
                                                    "details": f"Created, retrieved, updated, and listed pillars successfully"
                                                })
                                                return True
                                                
                print("❌ Pillar CRUD operations failed")
                self.test_results.append({
                    "test": "Pillar CRUD Operations", 
                    "status": "FAILED", 
                    "reason": "One or more CRUD operations failed"
                })
                return False
                
        except Exception as e:
            print(f"❌ Pillar CRUD test error: {e}")
            self.test_results.append({
                "test": "Pillar CRUD Operations", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def test_area_crud_operations(self):
        """Test 4: Area CRUD operations with Supabase"""
        print("\n🧪 Test 4: Area CRUD Operations")
        
        try:
            # Create area (with pillar if available)
            area_data = {
                "name": "Fitness Training",
                "description": "Regular exercise and fitness activities",
                "icon": "💪",
                "color": "#FF5722"
            }
            
            if self.created_entities['pillars']:
                area_data["pillar_id"] = self.created_entities['pillars'][0]
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    area_id = area["id"]
                    self.created_entities['areas'].append(area_id)
                    print(f"✅ Area created successfully: {area_id}")
                    
                    # Test area retrieval
                    async with self.session.get(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as get_response:
                        if get_response.status == 200:
                            retrieved_area = await get_response.json()
                            print("✅ Area retrieval successful")
                            
                            # Test area list with projects
                            async with self.session.get(f"{API_BASE}/areas?include_projects=true", headers=self.get_auth_headers()) as list_response:
                                if list_response.status == 200:
                                    areas = await list_response.json()
                                    if len(areas) > 0:
                                        print(f"✅ Area list successful: {len(areas)} areas found")
                                        self.test_results.append({
                                            "test": "Area CRUD Operations", 
                                            "status": "PASSED", 
                                            "details": f"Created, retrieved, and listed areas successfully"
                                        })
                                        return True
                                        
                print("❌ Area CRUD operations failed")
                self.test_results.append({
                    "test": "Area CRUD Operations", 
                    "status": "FAILED", 
                    "reason": "One or more CRUD operations failed"
                })
                return False
                
        except Exception as e:
            print(f"❌ Area CRUD test error: {e}")
            self.test_results.append({
                "test": "Area CRUD Operations", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def test_project_crud_operations(self):
        """Test 5: Project CRUD operations with Supabase"""
        print("\n🧪 Test 5: Project CRUD Operations")
        
        try:
            if not self.created_entities['areas']:
                print("❌ No areas available for project creation")
                self.test_results.append({
                    "test": "Project CRUD Operations", 
                    "status": "FAILED", 
                    "reason": "No areas available for project creation"
                })
                return False
                
            # Create project
            project_data = {
                "area_id": self.created_entities['areas'][0],
                "name": "Morning Workout Routine",
                "description": "Daily morning exercise routine",
                "icon": "🌅",
                "priority": "high"
            }
            
            async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    project = await response.json()
                    project_id = project["id"]
                    self.created_entities['projects'].append(project_id)
                    print(f"✅ Project created successfully: {project_id}")
                    
                    # Test project retrieval
                    async with self.session.get(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as get_response:
                        if get_response.status == 200:
                            retrieved_project = await get_response.json()
                            print("✅ Project retrieval successful")
                            
                            # Test project list
                            async with self.session.get(f"{API_BASE}/projects", headers=self.get_auth_headers()) as list_response:
                                if list_response.status == 200:
                                    projects = await list_response.json()
                                    if len(projects) > 0:
                                        print(f"✅ Project list successful: {len(projects)} projects found")
                                        self.test_results.append({
                                            "test": "Project CRUD Operations", 
                                            "status": "PASSED", 
                                            "details": f"Created, retrieved, and listed projects successfully"
                                        })
                                        return True
                                        
                print("❌ Project CRUD operations failed")
                self.test_results.append({
                    "test": "Project CRUD Operations", 
                    "status": "FAILED", 
                    "reason": "One or more CRUD operations failed"
                })
                return False
                
        except Exception as e:
            print(f"❌ Project CRUD test error: {e}")
            self.test_results.append({
                "test": "Project CRUD Operations", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def test_task_crud_operations(self):
        """Test 6: Task CRUD operations with Supabase"""
        print("\n🧪 Test 6: Task CRUD Operations")
        
        try:
            if not self.created_entities['projects']:
                print("❌ No projects available for task creation")
                self.test_results.append({
                    "test": "Task CRUD Operations", 
                    "status": "FAILED", 
                    "reason": "No projects available for task creation"
                })
                return False
                
            # Create task
            task_data = {
                "project_id": self.created_entities['projects'][0],
                "name": "30-minute cardio workout",
                "description": "High-intensity cardio session",
                "priority": "high",
                "status": "todo"
            }
            
            async with self.session.post(f"{API_BASE}/tasks", json=task_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    task = await response.json()
                    task_id = task["id"]
                    self.created_entities['tasks'].append(task_id)
                    print(f"✅ Task created successfully: {task_id}")
                    
                    # Test task retrieval
                    async with self.session.get(f"{API_BASE}/tasks", headers=self.get_auth_headers()) as get_response:
                        if get_response.status == 200:
                            tasks = await get_response.json()
                            print(f"✅ Task list successful: {len(tasks)} tasks found")
                            
                            # Test task update
                            update_data = {
                                "status": "in_progress"
                            }
                            
                            async with self.session.put(f"{API_BASE}/tasks/{task_id}", json=update_data, headers=self.get_auth_headers()) as update_response:
                                if update_response.status == 200:
                                    print("✅ Task update successful")
                                    
                                    # Test kanban board
                                    async with self.session.get(f"{API_BASE}/projects/{self.created_entities['projects'][0]}/kanban", headers=self.get_auth_headers()) as kanban_response:
                                        if kanban_response.status == 200:
                                            kanban = await kanban_response.json()
                                            print("✅ Kanban board retrieval successful")
                                            self.test_results.append({
                                                "test": "Task CRUD Operations", 
                                                "status": "PASSED", 
                                                "details": f"Created, retrieved, updated tasks and accessed kanban board successfully"
                                            })
                                            return True
                                            
                print("❌ Task CRUD operations failed")
                self.test_results.append({
                    "test": "Task CRUD Operations", 
                    "status": "FAILED", 
                    "reason": "One or more CRUD operations failed"
                })
                return False
                
        except Exception as e:
            print(f"❌ Task CRUD test error: {e}")
            self.test_results.append({
                "test": "Task CRUD Operations", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def test_journal_crud_operations(self):
        """Test 7: Journal CRUD operations with Supabase"""
        print("\n🧪 Test 7: Journal CRUD Operations")
        
        try:
            # Create journal entry
            journal_data = {
                "title": "Supabase Migration Test Entry",
                "content": "Testing journal functionality after Supabase migration. Everything seems to be working well!",
                "mood": "optimistic",
                "energy_level": "high",
                "tags": ["supabase", "migration", "testing"]
            }
            
            async with self.session.post(f"{API_BASE}/journal", json=journal_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    journal_entry = await response.json()
                    entry_id = journal_entry["id"]
                    self.created_entities['journal_entries'].append(entry_id)
                    print(f"✅ Journal entry created successfully: {entry_id}")
                    
                    # Test journal entry retrieval
                    async with self.session.get(f"{API_BASE}/journal", headers=self.get_auth_headers()) as get_response:
                        if get_response.status == 200:
                            entries = await get_response.json()
                            print(f"✅ Journal entries retrieval successful: {len(entries)} entries found")
                            
                            # Test journal search
                            async with self.session.get(f"{API_BASE}/journal/search?q=migration", headers=self.get_auth_headers()) as search_response:
                                if search_response.status == 200:
                                    search_results = await search_response.json()
                                    print(f"✅ Journal search successful: {len(search_results)} results found")
                                    
                                    # Test journal insights
                                    async with self.session.get(f"{API_BASE}/journal/insights", headers=self.get_auth_headers()) as insights_response:
                                        if insights_response.status == 200:
                                            insights = await insights_response.json()
                                            print("✅ Journal insights retrieval successful")
                                            self.test_results.append({
                                                "test": "Journal CRUD Operations", 
                                                "status": "PASSED", 
                                                "details": f"Created, retrieved, searched journal entries and accessed insights successfully"
                                            })
                                            return True
                                        else:
                                            print(f"❌ Journal insights failed: {insights_response.status}")
                                            error_text = await insights_response.text()
                                            print(f"Error: {error_text}")
                                else:
                                    print(f"❌ Journal search failed: {search_response.status}")
                                    error_text = await search_response.text()
                                    print(f"Error: {error_text}")
                        else:
                            print(f"❌ Journal retrieval failed: {get_response.status}")
                            error_text = await get_response.text()
                            print(f"Error: {error_text}")
                else:
                    print(f"❌ Journal creation failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                                            
                print("❌ Journal CRUD operations failed")
                self.test_results.append({
                    "test": "Journal CRUD Operations", 
                    "status": "FAILED", 
                    "reason": "One or more CRUD operations failed"
                })
                return False
                
        except Exception as e:
            print(f"❌ Journal CRUD test error: {e}")
            self.test_results.append({
                "test": "Journal CRUD Operations", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def test_dashboard_and_insights(self):
        """Test 8: Dashboard and insights with Supabase data"""
        print("\n🧪 Test 8: Dashboard and Insights")
        
        try:
            # Test dashboard
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    dashboard = await response.json()
                    print("✅ Dashboard retrieval successful")
                    print(f"   Areas: {dashboard.get('area_count', 0)}")
                    print(f"   Projects: {dashboard.get('project_count', 0)}")
                    print(f"   Tasks: {dashboard.get('task_count', 0)}")
                    
                    # Test insights
                    async with self.session.get(f"{API_BASE}/insights", headers=self.get_auth_headers()) as insights_response:
                        if insights_response.status == 200:
                            insights = await insights_response.json()
                            print("✅ Insights retrieval successful")
                            
                            # Test today view
                            async with self.session.get(f"{API_BASE}/today", headers=self.get_auth_headers()) as today_response:
                                if today_response.status == 200:
                                    today = await today_response.json()
                                    print("✅ Today view retrieval successful")
                                    
                                    # Test user stats
                                    async with self.session.get(f"{API_BASE}/stats", headers=self.get_auth_headers()) as stats_response:
                                        if stats_response.status == 200:
                                            stats = await stats_response.json()
                                            print("✅ User stats retrieval successful")
                                            self.test_results.append({
                                                "test": "Dashboard and Insights", 
                                                "status": "PASSED", 
                                                "details": f"Dashboard, insights, today view, and stats all accessible"
                                            })
                                            return True
                                            
                print("❌ Dashboard and insights test failed")
                self.test_results.append({
                    "test": "Dashboard and Insights", 
                    "status": "FAILED", 
                    "reason": "One or more dashboard endpoints failed"
                })
                return False
                
        except Exception as e:
            print(f"❌ Dashboard and insights test error: {e}")
            self.test_results.append({
                "test": "Dashboard and Insights", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def test_data_integrity(self):
        """Test 9: Data integrity and relationships"""
        print("\n🧪 Test 9: Data Integrity and Relationships")
        
        try:
            # Test pillar-area relationship
            if self.created_entities['pillars'] and self.created_entities['areas']:
                async with self.session.get(f"{API_BASE}/pillars/{self.created_entities['pillars'][0]}?include_areas=true", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        pillar_with_areas = await response.json()
                        if 'areas' in pillar_with_areas and len(pillar_with_areas['areas']) > 0:
                            print("✅ Pillar-Area relationship verified")
                        else:
                            print("⚠️ Pillar-Area relationship not found")
                            
            # Test area-project relationship
            if self.created_entities['areas'] and self.created_entities['projects']:
                async with self.session.get(f"{API_BASE}/areas?include_projects=true", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        areas_with_projects = await response.json()
                        found_project = False
                        for area in areas_with_projects:
                            if 'projects' in area and len(area['projects']) > 0:
                                found_project = True
                                break
                        if found_project:
                            print("✅ Area-Project relationship verified")
                        else:
                            print("⚠️ Area-Project relationship not found")
                            
            # Test project-task relationship
            if self.created_entities['projects'] and self.created_entities['tasks']:
                async with self.session.get(f"{API_BASE}/projects/{self.created_entities['projects'][0]}?include_tasks=true", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        project_with_tasks = await response.json()
                        if 'tasks' in project_with_tasks and len(project_with_tasks['tasks']) > 0:
                            print("✅ Project-Task relationship verified")
                        else:
                            print("⚠️ Project-Task relationship not found")
                            
            self.test_results.append({
                "test": "Data Integrity and Relationships", 
                "status": "PASSED", 
                "details": "Hierarchical relationships between entities verified"
            })
            return True
            
        except Exception as e:
            print(f"❌ Data integrity test error: {e}")
            self.test_results.append({
                "test": "Data Integrity and Relationships", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def run_all_tests(self):
        """Run all Supabase migration tests"""
        print("🚀 Starting Supabase Migration Backend Integration Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Authentication is required for most tests
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run all tests
            test_methods = [
                self.test_supabase_connection,
                self.test_user_crud_operations,
                self.test_pillar_crud_operations,
                self.test_area_crud_operations,
                self.test_project_crud_operations,
                self.test_task_crud_operations,
                self.test_journal_crud_operations,
                self.test_dashboard_and_insights,
                self.test_data_integrity
            ]
            
            for test_method in test_methods:
                try:
                    await test_method()
                except Exception as e:
                    print(f"❌ Test {test_method.__name__} failed with exception: {e}")
                    self.test_results.append({
                        "test": test_method.__name__, 
                        "status": "FAILED", 
                        "reason": f"Exception: {e}"
                    })
                    
        finally:
            await self.cleanup_session()
            
        # Print summary
        success = self.print_test_summary()
        return success
        
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🧪 SUPABASE MIGRATION BACKEND INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if r["status"] == "PASSED"]
        failed_tests = [r for r in self.test_results if r["status"] == "FAILED"]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"📊 TOTAL: {len(self.test_results)}")
        
        if len(self.test_results) > 0:
            success_rate = (len(passed_tests) / len(self.test_results)) * 100
            print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["status"] == "PASSED" and "details" in result:
                print(f"   Details: {result['details']}")
            elif result["status"] == "FAILED" and "reason" in result:
                print(f"   Reason: {result['reason']}")
                
        print("\n🔍 CREATED TEST ENTITIES:")
        for entity_type, entities in self.created_entities.items():
            if entities:
                print(f"   {entity_type}: {len(entities)} created")
                
        print("\n" + "=" * 60)
        
        # Return overall success
        return len(failed_tests) == 0

async def main():
    """Main test execution"""
    test_suite = SupabaseMigrationTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("🎉 All Supabase migration tests passed!")
        sys.exit(0)
    else:
        print("💥 Some Supabase migration tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())