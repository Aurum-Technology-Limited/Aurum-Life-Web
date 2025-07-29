#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://2cd28277-bdef-4a23-84f3-f1e19960e535.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveTanStackQueryTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "comprehensive.tanstack@aurumlife.com"
        self.test_user_password = "ComprehensiveTest123!"
        self.test_results = []
        self.performance_metrics = {}
        self.created_data = {
            "pillars": [],
            "areas": [],
            "projects": [],
            "tasks": []
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
            # Register test user
            register_data = {
                "username": "comptanstacktest",
                "email": self.test_user_email,
                "first_name": "Comprehensive",
                "last_name": "TanStackTest",
                "password": self.test_user_password
            }
            
            print(f"🔄 Setting up test user: {self.test_user_email}")
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status == 200:
                    print("✅ Test user registered successfully")
                elif response.status == 400:
                    print("ℹ️ Test user already exists")
                else:
                    print(f"⚠️ User registration returned: {response.status}")
                    
            # Login to get token
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            start_time = time.time()
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    self.performance_metrics["auth_login"] = response_time
                    print(f"✅ Authentication successful ({response_time:.2f}ms)")
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def create_sample_data(self):
        """Create sample data for comprehensive testing"""
        print("\n🔧 Creating sample data for testing...")
        
        try:
            # Create sample pillars
            pillar_data = [
                {"name": "Health & Wellness", "description": "Physical and mental health", "icon": "🏃", "color": "#4CAF50"},
                {"name": "Career Growth", "description": "Professional development", "icon": "💼", "color": "#2196F3"},
                {"name": "Personal Development", "description": "Learning and growth", "icon": "📚", "color": "#FF9800"}
            ]
            
            for pillar in pillar_data:
                async with self.session.post(f"{API_BASE}/pillars", json=pillar, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        created_pillar = await response.json()
                        self.created_data["pillars"].append(created_pillar["id"])
                        print(f"   ✅ Created pillar: {pillar['name']}")
                    else:
                        print(f"   ❌ Failed to create pillar: {pillar['name']} ({response.status})")
                        
            # Create sample areas
            if self.created_data["pillars"]:
                area_data = [
                    {"name": "Fitness", "description": "Exercise and physical activity", "icon": "💪", "color": "#4CAF50", "pillar_id": self.created_data["pillars"][0]},
                    {"name": "Work Projects", "description": "Professional tasks", "icon": "🏢", "color": "#2196F3", "pillar_id": self.created_data["pillars"][1]},
                    {"name": "Learning", "description": "Skill development", "icon": "🎓", "color": "#FF9800", "pillar_id": self.created_data["pillars"][2]}
                ]
                
                for area in area_data:
                    async with self.session.post(f"{API_BASE}/areas", json=area, headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            created_area = await response.json()
                            self.created_data["areas"].append(created_area["id"])
                            print(f"   ✅ Created area: {area['name']}")
                        else:
                            print(f"   ❌ Failed to create area: {area['name']} ({response.status})")
                            
            # Create sample projects
            if self.created_data["areas"]:
                project_data = [
                    {"name": "Morning Workout Routine", "description": "Daily exercise plan", "area_id": self.created_data["areas"][0], "icon": "🏃"},
                    {"name": "TanStack Query Implementation", "description": "Frontend optimization project", "area_id": self.created_data["areas"][1], "icon": "⚡"},
                    {"name": "React Advanced Course", "description": "Online learning course", "area_id": self.created_data["areas"][2], "icon": "⚛️"}
                ]
                
                for project in project_data:
                    async with self.session.post(f"{API_BASE}/projects", json=project, headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            created_project = await response.json()
                            self.created_data["projects"].append(created_project["id"])
                            print(f"   ✅ Created project: {project['name']}")
                        else:
                            print(f"   ❌ Failed to create project: {project['name']} ({response.status})")
                            
            # Create sample tasks
            if self.created_data["projects"]:
                task_data = [
                    {"name": "30-minute cardio", "description": "Daily cardio exercise", "project_id": self.created_data["projects"][0], "priority": "high"},
                    {"name": "Implement useQuery hooks", "description": "Add TanStack Query hooks", "project_id": self.created_data["projects"][1], "priority": "high"},
                    {"name": "Complete React hooks module", "description": "Study advanced hooks", "project_id": self.created_data["projects"][2], "priority": "medium"}
                ]
                
                for task in task_data:
                    async with self.session.post(f"{API_BASE}/tasks", json=task, headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            created_task = await response.json()
                            self.created_data["tasks"].append(created_task["id"])
                            print(f"   ✅ Created task: {task['name']}")
                        else:
                            print(f"   ❌ Failed to create task: {task['name']} ({response.status})")
                            
            print(f"📊 Sample data created: {len(self.created_data['pillars'])} pillars, {len(self.created_data['areas'])} areas, {len(self.created_data['projects'])} projects, {len(self.created_data['tasks'])} tasks")
            return True
            
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            return False
            
    async def test_dashboard_with_data(self):
        """Test Dashboard API with actual data"""
        print("\n🧪 Test 1: Dashboard API with Real Data")
        
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                self.performance_metrics["dashboard"] = response_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    required_fields = ["user", "stats", "recent_tasks"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print(f"✅ Dashboard API successful ({response_time:.2f}ms)")
                        print(f"   👤 User: {data['user'].get('email', 'N/A')}")
                        print(f"   📊 Stats: {len(data.get('stats', {}))} stat fields")
                        print(f"   📝 Recent tasks: {len(data.get('recent_tasks', []))}")
                        
                        # Performance assessment
                        if response_time < 1000:
                            performance_status = "EXCELLENT"
                            print(f"   🚀 Performance excellent for caching: {response_time:.2f}ms < 1000ms")
                        elif response_time < 2000:
                            performance_status = "GOOD"
                            print(f"   ⚡ Performance good: {response_time:.2f}ms < 2000ms")
                        else:
                            performance_status = "SLOW"
                            print(f"   ⚠️ Performance slow: {response_time:.2f}ms > 2000ms")
                            
                        self.test_results.append({
                            "test": "Dashboard API with Data",
                            "status": "PASSED",
                            "response_time": f"{response_time:.2f}ms",
                            "performance": performance_status,
                            "details": f"User data, stats, and {len(data.get('recent_tasks', []))} recent tasks"
                        })
                    else:
                        print(f"❌ Dashboard API missing required fields: {missing_fields}")
                        self.test_results.append({
                            "test": "Dashboard API with Data",
                            "status": "FAILED",
                            "reason": f"Missing fields: {missing_fields}"
                        })
                else:
                    print(f"❌ Dashboard API failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({
                        "test": "Dashboard API with Data",
                        "status": "FAILED",
                        "reason": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            print(f"❌ Dashboard API test failed: {e}")
            self.test_results.append({
                "test": "Dashboard API with Data",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_areas_with_relationships(self):
        """Test Areas API with project relationships"""
        print("\n🧪 Test 2: Areas API with Project Relationships")
        
        try:
            # Test the exact endpoint used by TanStack Query
            params = "include_projects=true&include_archived=false"
            
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/areas?{params}", headers=self.get_auth_headers()) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                self.performance_metrics["areas_with_projects"] = response_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"✅ Areas API successful ({response_time:.2f}ms)")
                    print(f"   📊 Retrieved {len(data)} areas")
                    
                    # Verify project relationships
                    areas_with_projects = 0
                    total_projects = 0
                    
                    for area in data:
                        if "projects" in area and area["projects"]:
                            areas_with_projects += 1
                            total_projects += len(area["projects"])
                            print(f"   🔗 Area '{area.get('name', 'N/A')}' has {len(area['projects'])} projects")
                        elif "project_count" in area:
                            if area["project_count"] > 0:
                                areas_with_projects += 1
                                total_projects += area["project_count"]
                            print(f"   📊 Area '{area.get('name', 'N/A')}' has {area['project_count']} projects")
                            
                    print(f"   📈 Total: {areas_with_projects} areas with {total_projects} projects")
                    
                    # Performance assessment for batch loading
                    if response_time < 500:
                        performance_status = "EXCELLENT"
                        print(f"   🚀 Batch loading performance excellent: {response_time:.2f}ms")
                    elif response_time < 1000:
                        performance_status = "GOOD"
                        print(f"   ⚡ Batch loading performance good: {response_time:.2f}ms")
                    else:
                        performance_status = "SLOW"
                        print(f"   ⚠️ Batch loading performance slow: {response_time:.2f}ms")
                        
                    self.test_results.append({
                        "test": "Areas API with Project Relationships",
                        "status": "PASSED",
                        "response_time": f"{response_time:.2f}ms",
                        "performance": performance_status,
                        "details": f"{len(data)} areas, {total_projects} total projects"
                    })
                else:
                    print(f"❌ Areas API failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({
                        "test": "Areas API with Project Relationships",
                        "status": "FAILED",
                        "reason": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            print(f"❌ Areas API test failed: {e}")
            self.test_results.append({
                "test": "Areas API with Project Relationships",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_pillars_for_dropdowns(self):
        """Test Pillars API for dropdown/selection components"""
        print("\n🧪 Test 3: Pillars API for Dropdown Components")
        
        try:
            # Test all pillar query variations
            test_scenarios = [
                ("basic", ""),
                ("with_areas", "include_areas=true"),
                ("with_archived", "include_archived=true"),
                ("full", "include_areas=true&include_archived=true")
            ]
            
            for scenario_name, params in test_scenarios:
                url = f"{API_BASE}/pillars"
                if params:
                    url += f"?{params}"
                    
                start_time = time.time()
                async with self.session.get(url, headers=self.get_auth_headers()) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ {scenario_name}: {len(data)} pillars ({response_time:.2f}ms)")
                        
                        # Verify dropdown-friendly structure
                        if data and len(data) > 0:
                            sample_pillar = data[0]
                            required_fields = ["id", "name"]
                            optional_fields = ["color", "icon", "description"]
                            
                            has_required = all(field in sample_pillar for field in required_fields)
                            has_optional = sum(1 for field in optional_fields if field in sample_pillar)
                            
                            if has_required:
                                print(f"      ✅ Has required fields for dropdowns: {required_fields}")
                            if has_optional > 0:
                                print(f"      ✅ Has {has_optional} optional display fields")
                                
                            # Check for area relationships if requested
                            if "include_areas=true" in params and "areas" in sample_pillar:
                                print(f"      🔗 Includes area relationships")
                                
                    else:
                        print(f"   ❌ {scenario_name}: Failed ({response.status})")
                        
            # Store performance for basic pillars endpoint
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                self.performance_metrics["pillars"] = response_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Performance assessment
                    if response_time < 500:
                        performance_status = "EXCELLENT"
                    elif response_time < 1000:
                        performance_status = "GOOD"
                    else:
                        performance_status = "SLOW"
                        
                    self.test_results.append({
                        "test": "Pillars API for Dropdown Components",
                        "status": "PASSED",
                        "response_time": f"{response_time:.2f}ms",
                        "performance": performance_status,
                        "details": f"{len(data)} pillars with dropdown-friendly structure"
                    })
                else:
                    self.test_results.append({
                        "test": "Pillars API for Dropdown Components",
                        "status": "FAILED",
                        "reason": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            print(f"❌ Pillars API test failed: {e}")
            self.test_results.append({
                "test": "Pillars API for Dropdown Components",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_authentication_robustness(self):
        """Test authentication robustness for TanStack Query"""
        print("\n🧪 Test 4: Authentication Robustness for TanStack Query")
        
        try:
            auth_tests = []
            
            # Test 1: Valid token works
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    user_data = await response.json()
                    auth_tests.append(("Valid token", True))
                    print(f"   ✅ Valid token works: {user_data.get('email', 'N/A')}")
                else:
                    auth_tests.append(("Valid token", False))
                    print(f"   ❌ Valid token failed: {response.status}")
                    
            # Test 2: No token returns proper error
            async with self.session.get(f"{API_BASE}/dashboard") as response:
                if response.status in [401, 403]:  # Either is acceptable
                    auth_tests.append(("No token protection", True))
                    print(f"   ✅ No token properly protected: {response.status}")
                else:
                    auth_tests.append(("No token protection", False))
                    print(f"   ❌ No token should be protected, got: {response.status}")
                    
            # Test 3: Invalid token returns proper error
            invalid_headers = {"Authorization": "Bearer invalid-token-12345"}
            async with self.session.get(f"{API_BASE}/dashboard", headers=invalid_headers) as response:
                if response.status in [401, 403]:
                    auth_tests.append(("Invalid token rejection", True))
                    print(f"   ✅ Invalid token properly rejected: {response.status}")
                else:
                    auth_tests.append(("Invalid token rejection", False))
                    print(f"   ❌ Invalid token should be rejected, got: {response.status}")
                    
            # Test 4: Malformed token returns proper error
            malformed_headers = {"Authorization": "Bearer malformed.token"}
            async with self.session.get(f"{API_BASE}/dashboard", headers=malformed_headers) as response:
                if response.status in [401, 403]:
                    auth_tests.append(("Malformed token rejection", True))
                    print(f"   ✅ Malformed token properly rejected: {response.status}")
                else:
                    auth_tests.append(("Malformed token rejection", False))
                    print(f"   ❌ Malformed token should be rejected, got: {response.status}")
                    
            # Test 5: Token works across multiple endpoints
            endpoints_to_test = ["/dashboard", "/areas", "/pillars", "/auth/me"]
            endpoint_successes = 0
            
            for endpoint in endpoints_to_test:
                async with self.session.get(f"{API_BASE}{endpoint}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        endpoint_successes += 1
                        
            if endpoint_successes == len(endpoints_to_test):
                auth_tests.append(("Token works across endpoints", True))
                print(f"   ✅ Token works across all {len(endpoints_to_test)} endpoints")
            else:
                auth_tests.append(("Token works across endpoints", False))
                print(f"   ❌ Token failed on {len(endpoints_to_test) - endpoint_successes} endpoints")
                
            # Overall assessment
            successful_tests = sum(1 for _, success in auth_tests if success)
            total_tests = len(auth_tests)
            
            if successful_tests == total_tests:
                self.test_results.append({
                    "test": "Authentication Robustness",
                    "status": "PASSED",
                    "details": f"All {total_tests} authentication scenarios working correctly"
                })
            elif successful_tests >= total_tests * 0.8:
                self.test_results.append({
                    "test": "Authentication Robustness",
                    "status": "PARTIAL",
                    "details": f"{successful_tests}/{total_tests} authentication scenarios working"
                })
            else:
                self.test_results.append({
                    "test": "Authentication Robustness",
                    "status": "FAILED",
                    "reason": f"Only {successful_tests}/{total_tests} authentication scenarios working"
                })
                
        except Exception as e:
            print(f"❌ Authentication robustness test failed: {e}")
            self.test_results.append({
                "test": "Authentication Robustness",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_caching_performance_baseline(self):
        """Test performance baseline for TanStack Query caching"""
        print("\n🧪 Test 5: Caching Performance Baseline")
        
        try:
            # Test key endpoints multiple times to establish baseline
            endpoints = {
                "dashboard": f"{API_BASE}/dashboard",
                "areas": f"{API_BASE}/areas?include_projects=true&include_archived=false",
                "pillars": f"{API_BASE}/pillars",
                "insights": f"{API_BASE}/insights",
                "today": f"{API_BASE}/today"
            }
            
            performance_results = {}
            
            for endpoint_name, endpoint_url in endpoints.items():
                response_times = []
                successful_requests = 0
                
                # Test each endpoint 5 times
                for i in range(5):
                    try:
                        start_time = time.time()
                        async with self.session.get(endpoint_url, headers=self.get_auth_headers()) as response:
                            end_time = time.time()
                            response_time = (end_time - start_time) * 1000
                            
                            if response.status == 200:
                                response_times.append(response_time)
                                successful_requests += 1
                            else:
                                print(f"      ⚠️ {endpoint_name} attempt {i+1}: {response.status}")
                                
                    except Exception as e:
                        print(f"      ❌ {endpoint_name} attempt {i+1}: {e}")
                        
                if response_times:
                    avg_time = sum(response_times) / len(response_times)
                    min_time = min(response_times)
                    max_time = max(response_times)
                    consistency = max_time - min_time
                    
                    performance_results[endpoint_name] = {
                        "avg": avg_time,
                        "min": min_time,
                        "max": max_time,
                        "consistency": consistency,
                        "success_rate": (successful_requests / 5) * 100
                    }
                    
                    # Performance assessment
                    if avg_time < 500:
                        perf_status = "🚀 EXCELLENT"
                    elif avg_time < 1000:
                        perf_status = "⚡ GOOD"
                    elif avg_time < 2000:
                        perf_status = "⚠️ ACCEPTABLE"
                    else:
                        perf_status = "❌ SLOW"
                        
                    print(f"   {perf_status} {endpoint_name}:")
                    print(f"      📊 Avg: {avg_time:.2f}ms, Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")
                    print(f"      📈 Consistency: ±{consistency:.2f}ms, Success: {successful_requests}/5")
                    
            # Overall performance assessment
            if performance_results:
                avg_performance = sum(result["avg"] for result in performance_results.values()) / len(performance_results)
                fast_endpoints = sum(1 for result in performance_results.values() if result["avg"] < 1000)
                consistent_endpoints = sum(1 for result in performance_results.values() if result["consistency"] < 500)
                reliable_endpoints = sum(1 for result in performance_results.values() if result["success_rate"] == 100)
                
                total_endpoints = len(performance_results)
                
                print(f"\n   📈 Performance Baseline Summary:")
                print(f"      Average response time: {avg_performance:.2f}ms")
                print(f"      Fast endpoints (<1s): {fast_endpoints}/{total_endpoints}")
                print(f"      Consistent endpoints (<500ms variance): {consistent_endpoints}/{total_endpoints}")
                print(f"      Reliable endpoints (100% success): {reliable_endpoints}/{total_endpoints}")
                
                # Determine caching suitability
                if avg_performance < 1000 and fast_endpoints >= total_endpoints * 0.8:
                    caching_status = "EXCELLENT"
                    print(f"      🚀 Performance excellent for TanStack Query caching")
                elif avg_performance < 2000 and fast_endpoints >= total_endpoints * 0.6:
                    caching_status = "GOOD"
                    print(f"      ⚡ Performance good for TanStack Query caching")
                else:
                    caching_status = "NEEDS_IMPROVEMENT"
                    print(f"      ⚠️ Performance needs improvement for effective caching")
                    
                self.test_results.append({
                    "test": "Caching Performance Baseline",
                    "status": "PASSED",
                    "performance": caching_status,
                    "details": f"Avg: {avg_performance:.2f}ms, {fast_endpoints}/{total_endpoints} fast, {reliable_endpoints}/{total_endpoints} reliable"
                })
            else:
                self.test_results.append({
                    "test": "Caching Performance Baseline",
                    "status": "FAILED",
                    "reason": "No successful performance measurements"
                })
                
        except Exception as e:
            print(f"❌ Caching performance baseline test failed: {e}")
            self.test_results.append({
                "test": "Caching Performance Baseline",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete in reverse order (tasks -> projects -> areas -> pillars)
            for task_id in self.created_data["tasks"]:
                async with self.session.delete(f"{API_BASE}/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"   ✅ Deleted task {task_id}")
                    else:
                        print(f"   ⚠️ Failed to delete task {task_id}: {response.status}")
                        
            for project_id in self.created_data["projects"]:
                async with self.session.delete(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"   ✅ Deleted project {project_id}")
                    else:
                        print(f"   ⚠️ Failed to delete project {project_id}: {response.status}")
                        
            for area_id in self.created_data["areas"]:
                async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"   ✅ Deleted area {area_id}")
                    else:
                        print(f"   ⚠️ Failed to delete area {area_id}: {response.status}")
                        
            for pillar_id in self.created_data["pillars"]:
                async with self.session.delete(f"{API_BASE}/pillars/{pillar_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"   ✅ Deleted pillar {pillar_id}")
                    else:
                        print(f"   ⚠️ Failed to delete pillar {pillar_id}: {response.status}")
                        
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
            
    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*90)
        print("🎯 COMPREHENSIVE TANSTACK QUERY BACKEND INTEGRATION - TEST SUMMARY")
        print("="*90)
        
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
        
        # Performance summary
        if self.performance_metrics:
            print(f"\n⚡ PERFORMANCE METRICS (Key TanStack Query Endpoints):")
            for endpoint, time_ms in self.performance_metrics.items():
                if time_ms < 500:
                    status = "🚀 EXCELLENT"
                elif time_ms < 1000:
                    status = "⚡ GOOD"
                elif time_ms < 2000:
                    status = "⚠️ ACCEPTABLE"
                else:
                    status = "❌ SLOW"
                print(f"   {status} {endpoint}: {time_ms:.2f}ms")
                
            avg_performance = sum(self.performance_metrics.values()) / len(self.performance_metrics)
            print(f"   📈 Average Response Time: {avg_performance:.2f}ms")
            
        print("\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "response_time" in result:
                print(f"    ⏱️ Response Time: {result['response_time']}")
            if "performance" in result:
                perf_icons = {"EXCELLENT": "🚀", "GOOD": "⚡", "ACCEPTABLE": "⚠️", "SLOW": "❌", "NEEDS_IMPROVEMENT": "⚠️"}
                perf_icon = perf_icons.get(result["performance"], "📊")
                print(f"    {perf_icon} Performance: {result['performance']}")
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*90)
        
        # Final assessment for TanStack Query readiness
        if success_rate >= 90:
            print("🎉 TANSTACK QUERY BACKEND INTEGRATION IS PRODUCTION-READY!")
            print("   ✅ All critical API endpoints working correctly")
            print("   ✅ Authentication system robust")
            print("   ✅ Performance suitable for caching optimization")
        elif success_rate >= 75:
            print("⚠️ TANSTACK QUERY BACKEND INTEGRATION IS MOSTLY FUNCTIONAL")
            print("   ✅ Core functionality working")
            print("   ⚠️ Minor issues detected - review failed tests")
        else:
            print("❌ TANSTACK QUERY BACKEND INTEGRATION HAS SIGNIFICANT ISSUES")
            print("   ❌ Major problems detected")
            print("   🔧 Immediate attention required before TanStack Query implementation")
            
        # Caching performance assessment
        if self.performance_metrics:
            avg_perf = sum(self.performance_metrics.values()) / len(self.performance_metrics)
            if avg_perf < 500:
                print("🚀 CACHING PERFORMANCE: Excellent - TanStack Query will provide significant benefits")
            elif avg_perf < 1000:
                print("⚡ CACHING PERFORMANCE: Good - TanStack Query caching will be effective")
            elif avg_perf < 2000:
                print("⚠️ CACHING PERFORMANCE: Acceptable - TanStack Query will help but consider optimization")
            else:
                print("❌ CACHING PERFORMANCE: Poor - Backend optimization needed before TanStack Query")
                
        print("="*90)
        
    async def run_comprehensive_tests(self):
        """Run comprehensive TanStack Query backend integration tests"""
        print("🚀 Starting Comprehensive TanStack Query Backend Integration Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"👤 Test User: {self.test_user_email}")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Create sample data for realistic testing
            if not await self.create_sample_data():
                print("⚠️ Sample data creation failed - proceeding with limited testing")
                
            # Run all comprehensive tests
            await self.test_dashboard_with_data()
            await self.test_areas_with_relationships()
            await self.test_pillars_for_dropdowns()
            await self.test_authentication_robustness()
            await self.test_caching_performance_baseline()
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print comprehensive summary
        self.print_comprehensive_summary()

async def main():
    """Main test execution"""
    test_suite = ComprehensiveTanStackQueryTest()
    await test_suite.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())