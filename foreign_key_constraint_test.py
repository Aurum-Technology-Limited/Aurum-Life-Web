#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://8f43b565-3ef8-487e-92ed-bb0b1b3a1936.preview.emergentagent.com')
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
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def create_test_user(self, user_suffix: str) -> Dict[str, Any]:
        """Create a test user and authenticate"""
        try:
            user_email = f"fk.test.{user_suffix}@aurumlife.com"
            user_password = "TestPass123!"
            username = f"fktest{user_suffix}"
            
            # Try to register user first
            register_data = {
                "username": username,
                "email": user_email,
                "first_name": f"FK Test {user_suffix}",
                "last_name": "User",
                "password": user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status in [200, 400]:  # 400 if user already exists
                    pass
                    
            # Login to get token
            login_data = {
                "email": user_email,
                "password": user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    user_info = {
                        'email': user_email,
                        'token': data["access_token"],
                        'headers': {"Authorization": f"Bearer {data['access_token']}"},
                        'user_id': data.get('user', {}).get('id', 'unknown')
                    }
                    self.test_users.append(user_info)
                    return user_info
                else:
                    print(f"❌ Authentication failed for user {user_suffix}: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error creating test user {user_suffix}: {e}")
            return None
            
    async def test_user_authentication_flow(self):
        """Test 1: User Authentication Flow - existing users should authenticate and access data"""
        print("\n🧪 Test 1: User Authentication Flow")
        
        try:
            # Create multiple test users to verify authentication works
            for i in range(3):
                user = await self.create_test_user(f"auth{i}")
                if user:
                    # Test /auth/me endpoint
                    async with self.session.get(f"{API_BASE}/auth/me", headers=user['headers']) as response:
                        if response.status == 200:
                            user_data = await response.json()
                            print(f"✅ User {i+1} authenticated successfully - ID: {user_data.get('id', 'unknown')}")
                        else:
                            print(f"❌ User {i+1} /auth/me failed: {response.status}")
                            self.test_results.append({"test": "User Authentication Flow", "status": "FAILED", "reason": f"User {i+1} /auth/me failed"})
                            return
                else:
                    print(f"❌ Failed to create test user {i+1}")
                    self.test_results.append({"test": "User Authentication Flow", "status": "FAILED", "reason": f"Failed to create test user {i+1}"})
                    return
                    
            self.test_results.append({"test": "User Authentication Flow", "status": "PASSED", "details": f"Successfully authenticated {len(self.test_users)} users"})
            
        except Exception as e:
            print(f"❌ User authentication test failed: {e}")
            self.test_results.append({"test": "User Authentication Flow", "status": "FAILED", "reason": str(e)})
            
    async def test_pillar_creation_no_fk_violations(self):
        """Test 2: Pillar Creation - should work without foreign key constraint violations"""
        print("\n🧪 Test 2: Pillar Creation - No Foreign Key Violations")
        
        try:
            success_count = 0
            
            for i, user in enumerate(self.test_users):
                pillar_data = {
                    "name": f"Test Pillar {i+1}",
                    "description": f"Test pillar for foreign key constraint testing - User {i+1}",
                    "icon": "🏛️",
                    "color": "#2196F3",
                    "time_allocation": 25
                }
                
                async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=user['headers']) as response:
                    if response.status == 200:
                        pillar = await response.json()
                        self.created_resources['pillars'].append({'id': pillar['id'], 'user': user})
                        print(f"✅ Pillar created successfully for user {i+1} - ID: {pillar['id']}")
                        success_count += 1
                    else:
                        error_text = await response.text()
                        print(f"❌ Pillar creation failed for user {i+1}: {response.status}")
                        print(f"   Error details: {error_text}")
                        
                        # Check if it's a foreign key constraint violation
                        if "foreign key" in error_text.lower() or "not present in table" in error_text.lower():
                            print(f"🚨 FOREIGN KEY CONSTRAINT VIOLATION detected for user {i+1}")
                            
            if success_count == len(self.test_users):
                self.test_results.append({"test": "Pillar Creation", "status": "PASSED", "details": f"All {success_count} pillar creations successful"})
            else:
                self.test_results.append({"test": "Pillar Creation", "status": "FAILED", "reason": f"Only {success_count}/{len(self.test_users)} pillar creations successful"})
                
        except Exception as e:
            print(f"❌ Pillar creation test failed: {e}")
            self.test_results.append({"test": "Pillar Creation", "status": "FAILED", "reason": str(e)})
            
    async def test_area_creation_no_fk_violations(self):
        """Test 3: Area Creation - should work without foreign key constraint violations"""
        print("\n🧪 Test 3: Area Creation - No Foreign Key Violations")
        
        try:
            success_count = 0
            
            for i, user in enumerate(self.test_users):
                # Use pillar if available, otherwise create without pillar
                pillar_id = None
                user_pillars = [p for p in self.created_resources['pillars'] if p['user']['user_id'] == user['user_id']]
                if user_pillars:
                    pillar_id = user_pillars[0]['id']
                
                area_data = {
                    "name": f"Test Area {i+1}",
                    "description": f"Test area for foreign key constraint testing - User {i+1}",
                    "icon": "📁",
                    "color": "#4CAF50",
                    "importance": 3
                }
                
                if pillar_id:
                    area_data["pillar_id"] = pillar_id
                
                async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=user['headers']) as response:
                    if response.status == 200:
                        area = await response.json()
                        self.created_resources['areas'].append({'id': area['id'], 'user': user})
                        print(f"✅ Area created successfully for user {i+1} - ID: {area['id']}")
                        success_count += 1
                    else:
                        error_text = await response.text()
                        print(f"❌ Area creation failed for user {i+1}: {response.status}")
                        print(f"   Error details: {error_text}")
                        
                        # Check if it's a foreign key constraint violation
                        if "foreign key" in error_text.lower() or "not present in table" in error_text.lower():
                            print(f"🚨 FOREIGN KEY CONSTRAINT VIOLATION detected for user {i+1}")
                            
            if success_count == len(self.test_users):
                self.test_results.append({"test": "Area Creation", "status": "PASSED", "details": f"All {success_count} area creations successful"})
            else:
                self.test_results.append({"test": "Area Creation", "status": "FAILED", "reason": f"Only {success_count}/{len(self.test_users)} area creations successful"})
                
        except Exception as e:
            print(f"❌ Area creation test failed: {e}")
            self.test_results.append({"test": "Area Creation", "status": "FAILED", "reason": str(e)})
            
    async def test_project_creation_no_fk_violations(self):
        """Test 4: Project Creation - should work without foreign key constraint violations"""
        print("\n🧪 Test 4: Project Creation - No Foreign Key Violations")
        
        try:
            success_count = 0
            
            for i, user in enumerate(self.test_users):
                # Use area if available
                area_id = None
                user_areas = [a for a in self.created_resources['areas'] if a['user']['user_id'] == user['user_id']]
                if user_areas:
                    area_id = user_areas[0]['id']
                
                project_data = {
                    "name": f"Test Project {i+1}",
                    "description": f"Test project for foreign key constraint testing - User {i+1}",
                    "icon": "🚀",
                    "priority": "high",
                    "status": "active"
                }
                
                if area_id:
                    project_data["area_id"] = area_id
                
                async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=user['headers']) as response:
                    if response.status == 200:
                        project = await response.json()
                        self.created_resources['projects'].append({'id': project['id'], 'user': user})
                        print(f"✅ Project created successfully for user {i+1} - ID: {project['id']}")
                        success_count += 1
                    else:
                        error_text = await response.text()
                        print(f"❌ Project creation failed for user {i+1}: {response.status}")
                        print(f"   Error details: {error_text}")
                        
                        # Check if it's a foreign key constraint violation
                        if "foreign key" in error_text.lower() or "not present in table" in error_text.lower():
                            print(f"🚨 FOREIGN KEY CONSTRAINT VIOLATION detected for user {i+1}")
                            
            if success_count == len(self.test_users):
                self.test_results.append({"test": "Project Creation", "status": "PASSED", "details": f"All {success_count} project creations successful"})
            else:
                self.test_results.append({"test": "Project Creation", "status": "FAILED", "reason": f"Only {success_count}/{len(self.test_users)} project creations successful"})
                
        except Exception as e:
            print(f"❌ Project creation test failed: {e}")
            self.test_results.append({"test": "Project Creation", "status": "FAILED", "reason": str(e)})
            
    async def test_task_creation_no_fk_violations(self):
        """Test 5: Task Creation - should work without foreign key constraint violations"""
        print("\n🧪 Test 5: Task Creation - No Foreign Key Violations")
        
        try:
            success_count = 0
            
            for i, user in enumerate(self.test_users):
                # Use project if available
                project_id = None
                user_projects = [p for p in self.created_resources['projects'] if p['user']['user_id'] == user['user_id']]
                if user_projects:
                    project_id = user_projects[0]['id']
                
                task_data = {
                    "name": f"Test Task {i+1}",
                    "description": f"Test task for foreign key constraint testing - User {i+1}",
                    "priority": "high",
                    "status": "todo",
                    "completed": False
                }
                
                if project_id:
                    task_data["project_id"] = project_id
                
                async with self.session.post(f"{API_BASE}/tasks", json=task_data, headers=user['headers']) as response:
                    if response.status == 200:
                        task = await response.json()
                        self.created_resources['tasks'].append({'id': task['id'], 'user': user})
                        print(f"✅ Task created successfully for user {i+1} - ID: {task['id']}")
                        success_count += 1
                    else:
                        error_text = await response.text()
                        print(f"❌ Task creation failed for user {i+1}: {response.status}")
                        print(f"   Error details: {error_text}")
                        
                        # Check if it's a foreign key constraint violation
                        if "foreign key" in error_text.lower() or "not present in table" in error_text.lower():
                            print(f"🚨 FOREIGN KEY CONSTRAINT VIOLATION detected for user {i+1}")
                            
            if success_count == len(self.test_users):
                self.test_results.append({"test": "Task Creation", "status": "PASSED", "details": f"All {success_count} task creations successful"})
            else:
                self.test_results.append({"test": "Task Creation", "status": "FAILED", "reason": f"Only {success_count}/{len(self.test_users)} task creations successful"})
                
        except Exception as e:
            print(f"❌ Task creation test failed: {e}")
            self.test_results.append({"test": "Task Creation", "status": "FAILED", "reason": str(e)})
            
    async def test_data_retrieval_and_integrity(self):
        """Test 6: Data Retrieval and Database Integrity - verify foreign key relationships work correctly"""
        print("\n🧪 Test 6: Data Retrieval and Database Integrity")
        
        try:
            success_count = 0
            
            for i, user in enumerate(self.test_users):
                # Test dashboard endpoint (comprehensive data retrieval)
                async with self.session.get(f"{API_BASE}/dashboard", headers=user['headers']) as response:
                    if response.status == 200:
                        dashboard_data = await response.json()
                        print(f"✅ Dashboard data retrieved successfully for user {i+1}")
                        
                        # Verify data structure integrity
                        if 'user' in dashboard_data and 'stats' in dashboard_data:
                            print(f"   ✅ Dashboard structure valid for user {i+1}")
                        else:
                            print(f"   ⚠️ Dashboard structure incomplete for user {i+1}")
                            
                    else:
                        print(f"❌ Dashboard retrieval failed for user {i+1}: {response.status}")
                        continue
                        
                # Test areas retrieval
                async with self.session.get(f"{API_BASE}/areas", headers=user['headers']) as response:
                    if response.status == 200:
                        areas = await response.json()
                        user_created_areas = [a for a in self.created_resources['areas'] if a['user']['user_id'] == user['user_id']]
                        print(f"✅ Areas retrieved successfully for user {i+1} - Found {len(areas)} areas")
                        
                        # Verify user can only see their own areas
                        if len(user_created_areas) > 0:
                            found_own_area = any(area['id'] == user_created_areas[0]['id'] for area in areas)
                            if found_own_area:
                                print(f"   ✅ User {i+1} can access their own areas")
                            else:
                                print(f"   ⚠️ User {i+1} cannot find their own areas")
                    else:
                        print(f"❌ Areas retrieval failed for user {i+1}: {response.status}")
                        continue
                        
                # Test projects retrieval
                async with self.session.get(f"{API_BASE}/projects", headers=user['headers']) as response:
                    if response.status == 200:
                        projects = await response.json()
                        print(f"✅ Projects retrieved successfully for user {i+1} - Found {len(projects)} projects")
                    else:
                        print(f"❌ Projects retrieval failed for user {i+1}: {response.status}")
                        continue
                        
                # Test tasks retrieval
                async with self.session.get(f"{API_BASE}/tasks", headers=user['headers']) as response:
                    if response.status == 200:
                        tasks = await response.json()
                        print(f"✅ Tasks retrieved successfully for user {i+1} - Found {len(tasks)} tasks")
                        success_count += 1
                    else:
                        print(f"❌ Tasks retrieval failed for user {i+1}: {response.status}")
                        
            if success_count == len(self.test_users):
                self.test_results.append({"test": "Data Retrieval and Integrity", "status": "PASSED", "details": f"All {success_count} users can retrieve their data"})
            else:
                self.test_results.append({"test": "Data Retrieval and Integrity", "status": "FAILED", "reason": f"Only {success_count}/{len(self.test_users)} users can retrieve data"})
                
        except Exception as e:
            print(f"❌ Data retrieval and integrity test failed: {e}")
            self.test_results.append({"test": "Data Retrieval and Integrity", "status": "FAILED", "reason": str(e)})
            
    async def test_new_user_registration_and_immediate_data_creation(self):
        """Test 7: New user registration and immediate data creation - critical for foreign key fix"""
        print("\n🧪 Test 7: New User Registration and Immediate Data Creation")
        
        try:
            # Create a brand new user
            new_user_suffix = f"newuser{int(datetime.now().timestamp())}"
            new_user = await self.create_test_user(new_user_suffix)
            
            if not new_user:
                self.test_results.append({"test": "New User Registration", "status": "FAILED", "reason": "Failed to create new user"})
                return
                
            print(f"✅ New user created: {new_user['email']}")
            
            # Immediately try to create data (this is where foreign key constraints would fail)
            pillar_data = {
                "name": "Immediate Test Pillar",
                "description": "Testing immediate data creation after registration",
                "icon": "⚡",
                "color": "#FF9800",
                "time_allocation": 30
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=new_user['headers']) as response:
                if response.status == 200:
                    pillar = await response.json()
                    print(f"✅ Immediate pillar creation successful for new user - ID: {pillar['id']}")
                    
                    # Try to create an area immediately
                    area_data = {
                        "name": "Immediate Test Area",
                        "description": "Testing immediate area creation",
                        "pillar_id": pillar['id'],
                        "icon": "⚡",
                        "color": "#FF9800",
                        "importance": 4
                    }
                    
                    async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=new_user['headers']) as area_response:
                        if area_response.status == 200:
                            area = await area_response.json()
                            print(f"✅ Immediate area creation successful for new user - ID: {area['id']}")
                            self.test_results.append({"test": "New User Registration", "status": "PASSED", "details": "New user can immediately create data"})
                        else:
                            error_text = await area_response.text()
                            print(f"❌ Immediate area creation failed: {area_response.status}")
                            print(f"   Error details: {error_text}")
                            
                            if "foreign key" in error_text.lower() or "not present in table" in error_text.lower():
                                print("🚨 CRITICAL: FOREIGN KEY CONSTRAINT VIOLATION for new user!")
                                self.test_results.append({"test": "New User Registration", "status": "FAILED", "reason": "Foreign key constraint violation for new user"})
                            else:
                                self.test_results.append({"test": "New User Registration", "status": "FAILED", "reason": f"Area creation failed: {area_response.status}"})
                else:
                    error_text = await response.text()
                    print(f"❌ Immediate pillar creation failed: {response.status}")
                    print(f"   Error details: {error_text}")
                    
                    if "foreign key" in error_text.lower() or "not present in table" in error_text.lower():
                        print("🚨 CRITICAL: FOREIGN KEY CONSTRAINT VIOLATION for new user!")
                        self.test_results.append({"test": "New User Registration", "status": "FAILED", "reason": "Foreign key constraint violation for new user"})
                    else:
                        self.test_results.append({"test": "New User Registration", "status": "FAILED", "reason": f"Pillar creation failed: {response.status}"})
                        
        except Exception as e:
            print(f"❌ New user registration test failed: {e}")
            self.test_results.append({"test": "New User Registration", "status": "FAILED", "reason": str(e)})
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete in reverse order to respect foreign key constraints
            for task in self.created_resources['tasks']:
                try:
                    async with self.session.delete(f"{API_BASE}/tasks/{task['id']}", headers=task['user']['headers']) as response:
                        if response.status == 200:
                            print(f"✅ Deleted task {task['id']}")
                        else:
                            print(f"⚠️ Failed to delete task {task['id']}: {response.status}")
                except:
                    pass
                    
            for project in self.created_resources['projects']:
                try:
                    async with self.session.delete(f"{API_BASE}/projects/{project['id']}", headers=project['user']['headers']) as response:
                        if response.status == 200:
                            print(f"✅ Deleted project {project['id']}")
                        else:
                            print(f"⚠️ Failed to delete project {project['id']}: {response.status}")
                except:
                    pass
                    
            for area in self.created_resources['areas']:
                try:
                    async with self.session.delete(f"{API_BASE}/areas/{area['id']}", headers=area['user']['headers']) as response:
                        if response.status == 200:
                            print(f"✅ Deleted area {area['id']}")
                        else:
                            print(f"⚠️ Failed to delete area {area['id']}: {response.status}")
                except:
                    pass
                    
            for pillar in self.created_resources['pillars']:
                try:
                    async with self.session.delete(f"{API_BASE}/pillars/{pillar['id']}", headers=pillar['user']['headers']) as response:
                        if response.status == 200:
                            print(f"✅ Deleted pillar {pillar['id']}")
                        else:
                            print(f"⚠️ Failed to delete pillar {pillar['id']}: {response.status}")
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 FOREIGN KEY CONSTRAINT RESOLUTION - TEST SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        skipped = len([t for t in self.test_results if t["status"] == "SKIPPED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️ Skipped: {skipped}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print(f"\n👥 Test Users Created: {len(self.test_users)}")
        print(f"🏛️ Pillars Created: {len(self.created_resources['pillars'])}")
        print(f"📁 Areas Created: {len(self.created_resources['areas'])}")
        print(f"🚀 Projects Created: {len(self.created_resources['projects'])}")
        print(f"✅ Tasks Created: {len(self.created_resources['tasks'])}")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        critical_tests = ["User Authentication Flow", "Pillar Creation", "Area Creation", "Project Creation", "Task Creation", "New User Registration"]
        critical_passed = len([t for t in self.test_results if t["test"] in critical_tests and t["status"] == "PASSED"])
        critical_total = len([t for t in self.test_results if t["test"] in critical_tests])
        
        if critical_passed == critical_total and success_rate >= 85:
            print("🎉 FOREIGN KEY CONSTRAINT ISSUE IS COMPLETELY RESOLVED!")
            print("✅ All critical data operations working without foreign key violations")
        elif critical_passed >= critical_total * 0.8:
            print("⚠️ FOREIGN KEY CONSTRAINT ISSUE IS MOSTLY RESOLVED - MINOR ISSUES DETECTED")
        else:
            print("❌ FOREIGN KEY CONSTRAINT ISSUE PERSISTS - CRITICAL FAILURES DETECTED")
            print("🚨 Users cannot create data due to foreign key constraint violations")
            
        print("="*80)
        
        return success_rate
        
    async def run_all_tests(self):
        """Run all foreign key constraint resolution tests"""
        print("🚀 Starting Foreign Key Constraint Resolution Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("📋 Testing Focus: Core data operations should work without foreign key violations")
        
        await self.setup_session()
        
        try:
            # Run all tests in sequence
            await self.test_user_authentication_flow()
            await self.test_pillar_creation_no_fk_violations()
            await self.test_area_creation_no_fk_violations()
            await self.test_project_creation_no_fk_violations()
            await self.test_task_creation_no_fk_violations()
            await self.test_data_retrieval_and_integrity()
            await self.test_new_user_registration_and_immediate_data_creation()
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary and return success rate
        return self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = ForeignKeyConstraintTestSuite()
    success_rate = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    if success_rate >= 85:
        exit(0)  # Success
    else:
        exit(1)  # Failure

if __name__ == "__main__":
    asyncio.run(main())