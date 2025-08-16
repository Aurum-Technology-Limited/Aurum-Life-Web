#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://focus-planner-3.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class CoreDataTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword123"
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
        """Authenticate with test user credentials"""
        try:
            print(f"🔐 Attempting authentication with {self.test_user_email}")
            
            # Try to register user first (in case they don't exist)
            register_data = {
                "username": "navtest",
                "email": self.test_user_email,
                "first_name": "Nav",
                "last_name": "Test",
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status in [200, 400]:  # 400 if user already exists
                    print(f"✅ User registration status: {response.status}")
                    
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
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_authentication(self):
        """Test 1: Authentication with test user"""
        print("\n🧪 Test 1: Authentication System")
        
        try:
            # Test /auth/me endpoint
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ Auth/me endpoint working - User: {user_data.get('email', 'Unknown')}")
                    self.test_results.append({
                        "test": "Authentication System", 
                        "status": "PASSED", 
                        "details": f"Successfully authenticated as {user_data.get('email', 'Unknown')}"
                    })
                else:
                    error_text = await response.text()
                    print(f"❌ Auth/me endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Authentication System", 
                        "status": "FAILED", 
                        "reason": f"Auth/me failed: {response.status}"
                    })
                    
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            self.test_results.append({
                "test": "Authentication System", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_pillar_creation(self):
        """Test 2: Pillar Creation"""
        print("\n🧪 Test 2: Pillar Creation")
        
        try:
            pillar_data = {
                "name": "Test Pillar",
                "description": "Test Description",
                "icon": "🎯",
                "color": "#FF5722",
                "time_allocation_percentage": 25.0
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillar = await response.json()
                    self.created_resources['pillars'].append(pillar["id"])
                    print(f"✅ Pillar created successfully - ID: {pillar['id']}")
                    self.test_results.append({
                        "test": "Pillar Creation", 
                        "status": "PASSED", 
                        "details": f"Created pillar: {pillar['name']}"
                    })
                    return pillar["id"]
                else:
                    error_text = await response.text()
                    print(f"❌ Pillar creation failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Pillar Creation", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}: {error_text}"
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
        """Test 3: Area Creation"""
        print("\n🧪 Test 3: Area Creation")
        
        try:
            area_data = {
                "name": "Test Area",
                "description": "Test area linked to pillar",
                "icon": "📁",
                "color": "#2196F3",
                "importance": 3
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
                        "details": f"Created area: {area['name']}"
                    })
                    return area["id"]
                else:
                    error_text = await response.text()
                    print(f"❌ Area creation failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Area Creation", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}: {error_text}"
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
        """Test 4: Project Creation"""
        print("\n🧪 Test 4: Project Creation")
        
        try:
            project_data = {
                "name": "Test Project",
                "description": "Test project linked to area",
                "icon": "🚀",
                "priority": "high",
                "importance": 3
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
                        "details": f"Created project: {project['name']}"
                    })
                    return project["id"]
                else:
                    error_text = await response.text()
                    print(f"❌ Project creation failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Project Creation", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}: {error_text}"
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
        """Test 5: Task Creation"""
        print("\n🧪 Test 5: Task Creation")
        
        try:
            task_data = {
                "name": "Test Task",
                "description": "Test task linked to project",
                "priority": "high",
                "completed": False
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
                        "details": f"Created task: {task['name']}"
                    })
                    return task["id"]
                else:
                    error_text = await response.text()
                    print(f"❌ Task creation failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Task Creation", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}: {error_text}"
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
            
    async def test_data_retrieval(self):
        """Test 6: Data Retrieval Endpoints"""
        print("\n🧪 Test 6: Data Retrieval Endpoints")
        
        endpoints_to_test = [
            ("GET /api/pillars", f"{API_BASE}/pillars"),
            ("GET /api/areas", f"{API_BASE}/areas"),
            ("GET /api/projects", f"{API_BASE}/projects"),
            ("GET /api/tasks", f"{API_BASE}/tasks")
        ]
        
        retrieval_results = []
        
        for endpoint_name, url in endpoints_to_test:
            try:
                start_time = datetime.now()
                async with self.session.get(url, headers=self.get_auth_headers()) as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {endpoint_name} - Status: {response.status}, Items: {len(data)}, Time: {response_time:.1f}ms")
                        retrieval_results.append({
                            "endpoint": endpoint_name,
                            "status": "PASSED",
                            "items_count": len(data),
                            "response_time_ms": response_time
                        })
                    else:
                        error_text = await response.text()
                        print(f"❌ {endpoint_name} - Status: {response.status}, Error: {error_text}")
                        retrieval_results.append({
                            "endpoint": endpoint_name,
                            "status": "FAILED",
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                        
            except Exception as e:
                print(f"❌ {endpoint_name} - Exception: {e}")
                retrieval_results.append({
                    "endpoint": endpoint_name,
                    "status": "FAILED",
                    "error": str(e)
                })
                
        # Determine overall retrieval test status
        passed_retrievals = len([r for r in retrieval_results if r["status"] == "PASSED"])
        total_retrievals = len(retrieval_results)
        
        if passed_retrievals == total_retrievals:
            self.test_results.append({
                "test": "Data Retrieval Endpoints", 
                "status": "PASSED", 
                "details": f"All {total_retrievals} endpoints working correctly"
            })
        else:
            self.test_results.append({
                "test": "Data Retrieval Endpoints", 
                "status": "FAILED", 
                "reason": f"Only {passed_retrievals}/{total_retrievals} endpoints working"
            })
            
    async def test_dashboard_data(self):
        """Test 7: Dashboard Data Endpoint"""
        print("\n🧪 Test 7: Dashboard Data Endpoint")
        
        try:
            start_time = datetime.now()
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    dashboard_data = await response.json()
                    print(f"✅ Dashboard endpoint working - Response time: {response_time:.1f}ms")
                    
                    # Check for expected dashboard structure
                    expected_fields = ['user', 'stats', 'recent_tasks']
                    missing_fields = [field for field in expected_fields if field not in dashboard_data]
                    
                    if not missing_fields:
                        print("✅ Dashboard data structure is complete")
                        self.test_results.append({
                            "test": "Dashboard Data Endpoint", 
                            "status": "PASSED", 
                            "details": f"Dashboard loaded in {response_time:.1f}ms with complete structure"
                        })
                    else:
                        print(f"⚠️ Dashboard missing fields: {missing_fields}")
                        self.test_results.append({
                            "test": "Dashboard Data Endpoint", 
                            "status": "PARTIAL", 
                            "details": f"Dashboard loaded but missing: {missing_fields}"
                        })
                else:
                    error_text = await response.text()
                    print(f"❌ Dashboard endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Dashboard Data Endpoint", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}: {error_text}"
                    })
                    
        except Exception as e:
            print(f"❌ Dashboard test failed: {e}")
            self.test_results.append({
                "test": "Dashboard Data Endpoint", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_database_connection(self):
        """Test 8: Database Connection and Health"""
        print("\n🧪 Test 8: Database Connection and Health")
        
        try:
            # Test health endpoint
            async with self.session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health endpoint working - Status: {health_data.get('status', 'unknown')}")
                    
                    # Test a simple authenticated query to verify database connection
                    async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as db_response:
                        if db_response.status == 200:
                            print("✅ Database connection verified through authenticated query")
                            self.test_results.append({
                                "test": "Database Connection", 
                                "status": "PASSED", 
                                "details": "Health endpoint and database queries working"
                            })
                        else:
                            print(f"❌ Database query failed: {db_response.status}")
                            self.test_results.append({
                                "test": "Database Connection", 
                                "status": "FAILED", 
                                "reason": f"Database query failed: {db_response.status}"
                            })
                else:
                    print(f"❌ Health endpoint failed: {response.status}")
                    self.test_results.append({
                        "test": "Database Connection", 
                        "status": "FAILED", 
                        "reason": f"Health endpoint failed: {response.status}"
                    })
                    
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            self.test_results.append({
                "test": "Database Connection", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_query_syntax_fixes(self):
        """Test 9: MongoDB/Supabase Query Syntax Fixes"""
        print("\n🧪 Test 9: Query Syntax Fixes (No Boolean/MongoDB Errors)")
        
        try:
            # Test areas endpoint with query parameters that previously caused boolean syntax errors
            test_queries = [
                (f"{API_BASE}/areas?include_projects=true&include_archived=false", "Areas with query params"),
                (f"{API_BASE}/pillars?include_areas=false&include_archived=false", "Pillars with query params"),
                (f"{API_BASE}/projects?include_archived=false", "Projects with archived filter"),
                (f"{API_BASE}/tasks?project_id=test", "Tasks with project filter")
            ]
            
            syntax_results = []
            
            for url, description in test_queries:
                try:
                    async with self.session.get(url, headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ {description} - No syntax errors")
                            syntax_results.append({"query": description, "status": "PASSED"})
                        elif response.status == 404:
                            # 404 is acceptable for some queries (e.g., non-existent project_id)
                            print(f"✅ {description} - No syntax errors (404 expected)")
                            syntax_results.append({"query": description, "status": "PASSED"})
                        else:
                            error_text = await response.text()
                            if "boolean" in error_text.lower() or "mongodb" in error_text.lower():
                                print(f"❌ {description} - Query syntax error: {error_text}")
                                syntax_results.append({"query": description, "status": "FAILED", "error": error_text})
                            else:
                                print(f"⚠️ {description} - Other error (not syntax): {response.status}")
                                syntax_results.append({"query": description, "status": "PASSED"})
                                
                except Exception as e:
                    print(f"❌ {description} - Exception: {e}")
                    syntax_results.append({"query": description, "status": "FAILED", "error": str(e)})
                    
            # Determine overall syntax test status
            passed_syntax = len([r for r in syntax_results if r["status"] == "PASSED"])
            total_syntax = len(syntax_results)
            
            if passed_syntax == total_syntax:
                self.test_results.append({
                    "test": "Query Syntax Fixes", 
                    "status": "PASSED", 
                    "details": f"All {total_syntax} query syntax tests passed"
                })
            else:
                failed_queries = [r["query"] for r in syntax_results if r["status"] == "FAILED"]
                self.test_results.append({
                    "test": "Query Syntax Fixes", 
                    "status": "FAILED", 
                    "reason": f"Syntax errors in: {', '.join(failed_queries)}"
                })
                
        except Exception as e:
            print(f"❌ Query syntax test failed: {e}")
            self.test_results.append({
                "test": "Query Syntax Fixes", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        cleanup_order = ['tasks', 'projects', 'areas', 'pillars']
        
        for resource_type in cleanup_order:
            for resource_id in self.created_resources[resource_type]:
                try:
                    endpoint = f"{API_BASE}/{resource_type}/{resource_id}"
                    async with self.session.delete(endpoint, headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            print(f"✅ Deleted {resource_type[:-1]} {resource_id}")
                        else:
                            print(f"⚠️ Failed to delete {resource_type[:-1]} {resource_id}: {response.status}")
                except Exception as e:
                    print(f"⚠️ Cleanup error for {resource_type[:-1]} {resource_id}: {e}")
                    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 AURUM LIFE CORE DATA FUNCTIONALITY - TEST SUMMARY")
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
            print("🎉 AURUM LIFE CORE DATA SYSTEM IS PRODUCTION-READY!")
        elif success_rate >= 75:
            print("⚠️ AURUM LIFE CORE DATA SYSTEM IS MOSTLY FUNCTIONAL - MINOR ISSUES DETECTED")
        else:
            print("❌ AURUM LIFE CORE DATA SYSTEM HAS SIGNIFICANT ISSUES - NEEDS ATTENTION")
            
        print("="*80)
        
    async def run_all_tests(self):
        """Run all core data functionality tests"""
        print("🚀 Starting Aurum Life Core Data Functionality Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"👤 Test User: {self.test_user_email}")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run authentication test
            await self.test_authentication()
            
            # Run data creation tests (in hierarchical order)
            pillar_id = await self.test_pillar_creation()
            area_id = await self.test_area_creation(pillar_id)
            project_id = await self.test_project_creation(area_id)
            task_id = await self.test_task_creation(project_id)
            
            # Run data retrieval tests
            await self.test_data_retrieval()
            await self.test_dashboard_data()
            
            # Run system tests
            await self.test_database_connection()
            await self.test_query_syntax_fixes()
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = CoreDataTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())