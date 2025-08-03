#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://7b39a747-36d6-44f7-9408-a498365475ba.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class AnalyticsTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword123"
        self.test_results = []
        self.created_resources = []
        self.created_projects = []
        self.created_tasks = []
        self.created_areas = []
        self.created_pillars = []
        self.performance_results = []
        
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
                "username": "navtest",
                "email": self.test_user_email,
                "first_name": "Nav",
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
        """Create comprehensive test data for analytics testing"""
        try:
            print("📊 Creating test data for analytics...")
            
            # Create test pillars
            pillar_data = [
                {"name": "Health & Fitness", "description": "Physical and mental wellbeing", "icon": "💪", "color": "#4CAF50"},
                {"name": "Career & Growth", "description": "Professional development", "icon": "🚀", "color": "#2196F3"},
                {"name": "Relationships", "description": "Personal connections", "icon": "❤️", "color": "#E91E63"}
            ]
            
            for pillar in pillar_data:
                async with self.session.post(f"{API_BASE}/pillars", json=pillar, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        pillar_obj = await response.json()
                        self.created_pillars.append(pillar_obj["id"])
                        print(f"✅ Created pillar: {pillar['name']}")
                    else:
                        print(f"❌ Failed to create pillar {pillar['name']}: {response.status}")
            
            # Create test areas linked to pillars
            if len(self.created_pillars) >= 3:
                area_data = [
                    {"name": "Exercise Routine", "description": "Daily workouts", "pillar_id": self.created_pillars[0], "icon": "🏃", "color": "#4CAF50"},
                    {"name": "Skill Development", "description": "Learning new skills", "pillar_id": self.created_pillars[1], "icon": "📚", "color": "#2196F3"},
                    {"name": "Family Time", "description": "Quality time with family", "pillar_id": self.created_pillars[2], "icon": "👨‍👩‍👧‍👦", "color": "#E91E63"},
                    {"name": "Nutrition", "description": "Healthy eating", "pillar_id": self.created_pillars[0], "icon": "🥗", "color": "#4CAF50"}
                ]
                
                for area in area_data:
                    async with self.session.post(f"{API_BASE}/areas", json=area, headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            area_obj = await response.json()
                            self.created_areas.append(area_obj["id"])
                            print(f"✅ Created area: {area['name']}")
                        else:
                            print(f"❌ Failed to create area {area['name']}: {response.status}")
            
            # Create test projects linked to areas
            if len(self.created_areas) >= 4:
                project_data = [
                    {"name": "Morning Workout Plan", "description": "Daily exercise routine", "area_id": self.created_areas[0], "icon": "🏋️"},
                    {"name": "Python Mastery", "description": "Learn advanced Python", "area_id": self.created_areas[1], "icon": "🐍"},
                    {"name": "Weekly Family Dinners", "description": "Regular family meals", "area_id": self.created_areas[2], "icon": "🍽️"},
                    {"name": "Meal Prep Sunday", "description": "Weekly meal preparation", "area_id": self.created_areas[3], "icon": "🥘"},
                    {"name": "Evening Walks", "description": "Daily walks", "area_id": self.created_areas[0], "icon": "🚶"}
                ]
                
                for project in project_data:
                    async with self.session.post(f"{API_BASE}/projects", json=project, headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            project_obj = await response.json()
                            self.created_projects.append(project_obj["id"])
                            print(f"✅ Created project: {project['name']}")
                        else:
                            print(f"❌ Failed to create project {project['name']}: {response.status}")
            
            # Create test tasks (some completed, some not) linked to projects
            if len(self.created_projects) >= 5:
                task_data = [
                    # Health & Fitness tasks (completed)
                    {"name": "30-min cardio", "description": "Morning cardio workout", "project_id": self.created_projects[0], "priority": "high", "completed": True},
                    {"name": "Strength training", "description": "Weight lifting session", "project_id": self.created_projects[0], "priority": "high", "completed": True},
                    {"name": "Evening walk", "description": "30-min walk", "project_id": self.created_projects[4], "priority": "medium", "completed": True},
                    
                    # Career & Growth tasks (completed)
                    {"name": "Python tutorial chapter 1", "description": "Complete first chapter", "project_id": self.created_projects[1], "priority": "high", "completed": True},
                    {"name": "Python tutorial chapter 2", "description": "Complete second chapter", "project_id": self.created_projects[1], "priority": "high", "completed": True},
                    
                    # Relationships tasks (completed)
                    {"name": "Plan family dinner", "description": "Organize Sunday dinner", "project_id": self.created_projects[2], "priority": "medium", "completed": True},
                    {"name": "Call parents", "description": "Weekly check-in call", "project_id": self.created_projects[2], "priority": "medium", "completed": True},
                    
                    # Nutrition tasks (completed)
                    {"name": "Prep healthy lunches", "description": "Prepare 5 healthy lunches", "project_id": self.created_projects[3], "priority": "medium", "completed": True},
                    
                    # Incomplete tasks
                    {"name": "Yoga session", "description": "Morning yoga", "project_id": self.created_projects[0], "priority": "low", "completed": False},
                    {"name": "Python tutorial chapter 3", "description": "Complete third chapter", "project_id": self.created_projects[1], "priority": "high", "completed": False}
                ]
                
                for task in task_data:
                    async with self.session.post(f"{API_BASE}/tasks", json=task, headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            task_obj = await response.json()
                            self.created_tasks.append(task_obj["id"])
                            status = "✅ completed" if task["completed"] else "⏳ pending"
                            print(f"✅ Created task: {task['name']} ({status})")
                        else:
                            print(f"❌ Failed to create task {task['name']}: {response.status}")
            
            # Mark some projects as completed
            if len(self.created_projects) >= 2:
                for i in range(2):  # Mark first 2 projects as completed
                    update_data = {"status": "Completed"}
                    async with self.session.put(f"{API_BASE}/projects/{self.created_projects[i]}", json=update_data, headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            print(f"✅ Marked project as completed")
                        else:
                            print(f"❌ Failed to mark project as completed: {response.status}")
            
            print(f"📊 Test data created: {len(self.created_pillars)} pillars, {len(self.created_areas)} areas, {len(self.created_projects)} projects, {len(self.created_tasks)} tasks")
            return True
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            return False
    
    async def test_lifetime_stats_endpoint(self):
        """Test 1: GET /api/analytics/lifetime-stats endpoint"""
        print("\n🧪 Test 1: Analytics Lifetime Stats Endpoint")
        
        try:
            start_time = time.time()
            
            async with self.session.get(f"{API_BASE}/analytics/lifetime-stats", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                self.performance_results.append({"endpoint": "lifetime-stats", "response_time_ms": response_time})
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if "total_tasks_completed" in data and "total_projects_completed" in data:
                        print(f"✅ Lifetime stats endpoint working - Response time: {response_time:.1f}ms")
                        print(f"   📊 Total tasks completed: {data['total_tasks_completed']}")
                        print(f"   📊 Total projects completed: {data['total_projects_completed']}")
                        
                        # Verify data accuracy (we created 8 completed tasks and 2 completed projects)
                        expected_tasks = 8
                        expected_projects = 2
                        
                        if data['total_tasks_completed'] >= expected_tasks and data['total_projects_completed'] >= expected_projects:
                            print(f"✅ Data accuracy verified - Tasks: {data['total_tasks_completed']}, Projects: {data['total_projects_completed']}")
                            
                            # Check performance requirement (under 200ms)
                            if response_time < 200:
                                print(f"✅ Performance requirement met: {response_time:.1f}ms < 200ms")
                                self.test_results.append({"test": "Lifetime Stats Endpoint", "status": "PASSED", "details": f"Response time: {response_time:.1f}ms, Data accurate"})
                            else:
                                print(f"⚠️ Performance requirement not met: {response_time:.1f}ms >= 200ms")
                                self.test_results.append({"test": "Lifetime Stats Endpoint", "status": "PARTIAL", "details": f"Functional but slow: {response_time:.1f}ms"})
                        else:
                            print(f"❌ Data accuracy issue - Expected tasks: {expected_tasks}, got: {data['total_tasks_completed']}")
                            self.test_results.append({"test": "Lifetime Stats Endpoint", "status": "FAILED", "reason": "Data accuracy issue"})
                    else:
                        print("❌ Invalid response structure - missing required fields")
                        self.test_results.append({"test": "Lifetime Stats Endpoint", "status": "FAILED", "reason": "Invalid response structure"})
                else:
                    print(f"❌ Lifetime stats endpoint failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({"test": "Lifetime Stats Endpoint", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    
        except Exception as e:
            print(f"❌ Lifetime stats test failed: {e}")
            self.test_results.append({"test": "Lifetime Stats Endpoint", "status": "FAILED", "reason": str(e)})
    
    async def test_pillar_alignment_endpoint(self):
        """Test 2: GET /api/analytics/pillar-alignment endpoint"""
        print("\n🧪 Test 2: Analytics Pillar Alignment Endpoint")
        
        try:
            start_time = time.time()
            
            async with self.session.get(f"{API_BASE}/analytics/pillar-alignment", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                self.performance_results.append({"endpoint": "pillar-alignment", "response_time_ms": response_time})
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if isinstance(data, list):
                        print(f"✅ Pillar alignment endpoint working - Response time: {response_time:.1f}ms")
                        print(f"   📊 Found {len(data)} pillars with task distribution")
                        
                        total_percentage = 0
                        for pillar in data:
                            if "pillar_name" in pillar and "task_count" in pillar and "percentage" in pillar:
                                print(f"   📊 {pillar['pillar_name']}: {pillar['task_count']} tasks ({pillar['percentage']}%)")
                                total_percentage += pillar['percentage']
                            else:
                                print("❌ Invalid pillar structure in response")
                                self.test_results.append({"test": "Pillar Alignment Endpoint", "status": "FAILED", "reason": "Invalid pillar structure"})
                                return
                        
                        # Verify percentages add up correctly (should be close to 100% or 0% if no completed tasks)
                        if len(data) > 0 and abs(total_percentage - 100.0) < 0.1:
                            print(f"✅ Percentage calculation verified: {total_percentage}%")
                        elif len(data) == 0:
                            print("✅ No pillar data (expected if no completed tasks linked to pillars)")
                        else:
                            print(f"⚠️ Percentage calculation issue: {total_percentage}% (should be ~100%)")
                        
                        # Check performance requirement (under 200ms)
                        if response_time < 200:
                            print(f"✅ Performance requirement met: {response_time:.1f}ms < 200ms")
                            self.test_results.append({"test": "Pillar Alignment Endpoint", "status": "PASSED", "details": f"Response time: {response_time:.1f}ms, {len(data)} pillars"})
                        else:
                            print(f"⚠️ Performance requirement not met: {response_time:.1f}ms >= 200ms")
                            self.test_results.append({"test": "Pillar Alignment Endpoint", "status": "PARTIAL", "details": f"Functional but slow: {response_time:.1f}ms"})
                    else:
                        print("❌ Invalid response structure - expected array")
                        self.test_results.append({"test": "Pillar Alignment Endpoint", "status": "FAILED", "reason": "Invalid response structure"})
                else:
                    print(f"❌ Pillar alignment endpoint failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({"test": "Pillar Alignment Endpoint", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    
        except Exception as e:
            print(f"❌ Pillar alignment test failed: {e}")
            self.test_results.append({"test": "Pillar Alignment Endpoint", "status": "FAILED", "reason": str(e)})
    
    async def test_alignment_snapshot_endpoint(self):
        """Test 3: GET /api/analytics/alignment-snapshot endpoint"""
        print("\n🧪 Test 3: Analytics Alignment Snapshot Endpoint")
        
        try:
            start_time = time.time()
            
            async with self.session.get(f"{API_BASE}/analytics/alignment-snapshot", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                self.performance_results.append({"endpoint": "alignment-snapshot", "response_time_ms": response_time})
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if "lifetime_stats" in data and "pillar_alignment" in data and "generated_at" in data:
                        print(f"✅ Alignment snapshot endpoint working - Response time: {response_time:.1f}ms")
                        
                        # Verify lifetime_stats structure
                        lifetime_stats = data["lifetime_stats"]
                        if "total_tasks_completed" in lifetime_stats and "total_projects_completed" in lifetime_stats:
                            print(f"   📊 Lifetime stats: {lifetime_stats['total_tasks_completed']} tasks, {lifetime_stats['total_projects_completed']} projects")
                        else:
                            print("❌ Invalid lifetime_stats structure")
                            self.test_results.append({"test": "Alignment Snapshot Endpoint", "status": "FAILED", "reason": "Invalid lifetime_stats structure"})
                            return
                        
                        # Verify pillar_alignment structure
                        pillar_alignment = data["pillar_alignment"]
                        if isinstance(pillar_alignment, list):
                            print(f"   📊 Pillar alignment: {len(pillar_alignment)} pillars")
                        else:
                            print("❌ Invalid pillar_alignment structure")
                            self.test_results.append({"test": "Alignment Snapshot Endpoint", "status": "FAILED", "reason": "Invalid pillar_alignment structure"})
                            return
                        
                        # Verify generated_at timestamp
                        try:
                            datetime.fromisoformat(data["generated_at"].replace('Z', '+00:00'))
                            print(f"   📊 Generated at: {data['generated_at']}")
                        except:
                            print("❌ Invalid generated_at timestamp")
                            self.test_results.append({"test": "Alignment Snapshot Endpoint", "status": "FAILED", "reason": "Invalid timestamp"})
                            return
                        
                        # Check performance requirement (under 200ms)
                        if response_time < 200:
                            print(f"✅ Performance requirement met: {response_time:.1f}ms < 200ms")
                            self.test_results.append({"test": "Alignment Snapshot Endpoint", "status": "PASSED", "details": f"Response time: {response_time:.1f}ms, Complete snapshot"})
                        else:
                            print(f"⚠️ Performance requirement not met: {response_time:.1f}ms >= 200ms")
                            self.test_results.append({"test": "Alignment Snapshot Endpoint", "status": "PARTIAL", "details": f"Functional but slow: {response_time:.1f}ms"})
                    else:
                        print("❌ Invalid response structure - missing required fields")
                        self.test_results.append({"test": "Alignment Snapshot Endpoint", "status": "FAILED", "reason": "Invalid response structure"})
                else:
                    print(f"❌ Alignment snapshot endpoint failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({"test": "Alignment Snapshot Endpoint", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    
        except Exception as e:
            print(f"❌ Alignment snapshot test failed: {e}")
            self.test_results.append({"test": "Alignment Snapshot Endpoint", "status": "FAILED", "reason": str(e)})
    
    async def test_authentication_requirements(self):
        """Test 4: Authentication requirements for analytics endpoints"""
        print("\n🧪 Test 4: Authentication Requirements")
        
        try:
            endpoints = [
                "/analytics/lifetime-stats",
                "/analytics/pillar-alignment", 
                "/analytics/alignment-snapshot"
            ]
            
            # Test without authentication
            for endpoint in endpoints:
                async with self.session.get(f"{API_BASE}{endpoint}") as response:
                    if response.status == 401:
                        print(f"✅ {endpoint} correctly requires authentication")
                    else:
                        print(f"❌ {endpoint} should require authentication but got: {response.status}")
                        self.test_results.append({"test": f"Authentication for {endpoint}", "status": "FAILED", "reason": f"Expected 401, got {response.status}"})
                        return
            
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid-token-12345"}
            for endpoint in endpoints:
                async with self.session.get(f"{API_BASE}{endpoint}", headers=invalid_headers) as response:
                    if response.status == 401:
                        print(f"✅ {endpoint} correctly rejects invalid token")
                    else:
                        print(f"❌ {endpoint} should reject invalid token but got: {response.status}")
                        self.test_results.append({"test": f"Invalid token for {endpoint}", "status": "FAILED", "reason": f"Expected 401, got {response.status}"})
                        return
            
            self.test_results.append({"test": "Authentication Requirements", "status": "PASSED", "details": "All endpoints properly protected"})
            
        except Exception as e:
            print(f"❌ Authentication requirements test failed: {e}")
            self.test_results.append({"test": "Authentication Requirements", "status": "FAILED", "reason": str(e)})
    
    async def test_performance_consistency(self):
        """Test 5: Performance consistency across multiple calls"""
        print("\n🧪 Test 5: Performance Consistency")
        
        try:
            endpoints = [
                "/analytics/lifetime-stats",
                "/analytics/pillar-alignment",
                "/analytics/alignment-snapshot"
            ]
            
            performance_data = {}
            
            for endpoint in endpoints:
                print(f"   Testing {endpoint} performance...")
                response_times = []
                
                # Make 5 calls to each endpoint
                for i in range(5):
                    start_time = time.time()
                    async with self.session.get(f"{API_BASE}{endpoint}", headers=self.get_auth_headers()) as response:
                        response_time = (time.time() - start_time) * 1000
                        response_times.append(response_time)
                        
                        if response.status != 200:
                            print(f"❌ {endpoint} failed on call {i+1}: {response.status}")
                            self.test_results.append({"test": f"Performance consistency {endpoint}", "status": "FAILED", "reason": f"HTTP {response.status}"})
                            return
                
                # Calculate statistics
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                
                performance_data[endpoint] = {
                    "average": avg_time,
                    "max": max_time,
                    "min": min_time,
                    "all_times": response_times
                }
                
                print(f"   📊 {endpoint}: Avg: {avg_time:.1f}ms, Max: {max_time:.1f}ms, Min: {min_time:.1f}ms")
                
                # Check if all calls are under 200ms (P95 requirement)
                calls_under_200ms = sum(1 for t in response_times if t < 200)
                p95_met = calls_under_200ms >= 4  # At least 4 out of 5 calls under 200ms
                
                if p95_met:
                    print(f"   ✅ P95 performance requirement met for {endpoint}")
                else:
                    print(f"   ⚠️ P95 performance requirement not met for {endpoint}")
            
            # Overall performance assessment
            all_endpoints_fast = all(data["average"] < 200 for data in performance_data.values())
            
            if all_endpoints_fast:
                self.test_results.append({"test": "Performance Consistency", "status": "PASSED", "details": "All endpoints consistently fast"})
            else:
                slow_endpoints = [ep for ep, data in performance_data.items() if data["average"] >= 200]
                self.test_results.append({"test": "Performance Consistency", "status": "PARTIAL", "details": f"Slow endpoints: {slow_endpoints}"})
            
        except Exception as e:
            print(f"❌ Performance consistency test failed: {e}")
            self.test_results.append({"test": "Performance Consistency", "status": "FAILED", "reason": str(e)})
    
    async def test_empty_data_scenarios(self):
        """Test 6: Empty data scenarios"""
        print("\n🧪 Test 6: Empty Data Scenarios")
        
        try:
            # Create a new user with no data
            empty_user_email = "empty.test@aurumlife.com"
            empty_user_password = "testpassword123"
            
            # Register new user
            register_data = {
                "username": "emptytest",
                "email": empty_user_email,
                "first_name": "Empty",
                "last_name": "Test",
                "password": empty_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status in [200, 400]:  # 400 if user already exists
                    pass
                    
            # Login as empty user
            login_data = {
                "email": empty_user_email,
                "password": empty_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    empty_user_token = data["access_token"]
                    empty_user_headers = {"Authorization": f"Bearer {empty_user_token}"}
                    
                    # Test lifetime stats with no data
                    async with self.session.get(f"{API_BASE}/analytics/lifetime-stats", headers=empty_user_headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data["total_tasks_completed"] == 0 and data["total_projects_completed"] == 0:
                                print("✅ Lifetime stats handles empty data correctly")
                            else:
                                print(f"❌ Lifetime stats should return 0 for empty user but got: {data}")
                                self.test_results.append({"test": "Empty data - lifetime stats", "status": "FAILED", "reason": "Non-zero values for empty user"})
                                return
                        else:
                            print(f"❌ Lifetime stats failed for empty user: {response.status}")
                            self.test_results.append({"test": "Empty data - lifetime stats", "status": "FAILED", "reason": f"HTTP {response.status}"})
                            return
                    
                    # Test pillar alignment with no data
                    async with self.session.get(f"{API_BASE}/analytics/pillar-alignment", headers=empty_user_headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            if isinstance(data, list) and len(data) == 0:
                                print("✅ Pillar alignment handles empty data correctly")
                            else:
                                print(f"❌ Pillar alignment should return empty array but got: {data}")
                                self.test_results.append({"test": "Empty data - pillar alignment", "status": "FAILED", "reason": "Non-empty data for empty user"})
                                return
                        else:
                            print(f"❌ Pillar alignment failed for empty user: {response.status}")
                            self.test_results.append({"test": "Empty data - pillar alignment", "status": "FAILED", "reason": f"HTTP {response.status}"})
                            return
                    
                    # Test alignment snapshot with no data
                    async with self.session.get(f"{API_BASE}/analytics/alignment-snapshot", headers=empty_user_headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            if (data["lifetime_stats"]["total_tasks_completed"] == 0 and 
                                data["lifetime_stats"]["total_projects_completed"] == 0 and
                                len(data["pillar_alignment"]) == 0):
                                print("✅ Alignment snapshot handles empty data correctly")
                                self.test_results.append({"test": "Empty Data Scenarios", "status": "PASSED", "details": "All endpoints handle empty data gracefully"})
                            else:
                                print(f"❌ Alignment snapshot should return empty data but got: {data}")
                                self.test_results.append({"test": "Empty data - alignment snapshot", "status": "FAILED", "reason": "Non-empty data for empty user"})
                        else:
                            print(f"❌ Alignment snapshot failed for empty user: {response.status}")
                            self.test_results.append({"test": "Empty data - alignment snapshot", "status": "FAILED", "reason": f"HTTP {response.status}"})
                else:
                    print(f"❌ Empty user login failed: {response.status}")
                    self.test_results.append({"test": "Empty Data Scenarios", "status": "FAILED", "reason": "Could not create empty user"})
                    
        except Exception as e:
            print(f"❌ Empty data scenarios test failed: {e}")
            self.test_results.append({"test": "Empty Data Scenarios", "status": "FAILED", "reason": str(e)})
    
    async def test_error_handling(self):
        """Test 7: Error handling scenarios"""
        print("\n🧪 Test 7: Error Handling")
        
        try:
            # Test with malformed requests (if applicable)
            # For now, just verify that endpoints handle errors gracefully
            
            # Test endpoints with valid auth but potential database issues
            endpoints = [
                "/analytics/lifetime-stats",
                "/analytics/pillar-alignment",
                "/analytics/alignment-snapshot"
            ]
            
            error_handling_passed = True
            
            for endpoint in endpoints:
                async with self.session.get(f"{API_BASE}{endpoint}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        # Endpoint should return valid JSON
                        try:
                            data = await response.json()
                            print(f"✅ {endpoint} returns valid JSON")
                        except:
                            print(f"❌ {endpoint} returns invalid JSON")
                            error_handling_passed = False
                    elif response.status == 500:
                        print(f"❌ {endpoint} returns 500 error - poor error handling")
                        error_handling_passed = False
                    else:
                        print(f"✅ {endpoint} handles errors gracefully (status: {response.status})")
            
            if error_handling_passed:
                self.test_results.append({"test": "Error Handling", "status": "PASSED", "details": "All endpoints handle errors gracefully"})
            else:
                self.test_results.append({"test": "Error Handling", "status": "FAILED", "reason": "Some endpoints have poor error handling"})
                
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            self.test_results.append({"test": "Error Handling", "status": "FAILED", "reason": str(e)})
    
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
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
                        
            # Delete created pillars
            for pillar_id in self.created_pillars:
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
        print("🎯 INSIGHTS & ANALYTICS MVP v1.2 - TEST SUMMARY")
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
        
        # Performance summary
        if self.performance_results:
            print(f"\n⚡ PERFORMANCE SUMMARY:")
            for perf in self.performance_results:
                status = "✅" if perf["response_time_ms"] < 200 else "⚠️"
                print(f"   {status} {perf['endpoint']}: {perf['response_time_ms']:.1f}ms")
            
            avg_performance = sum(p["response_time_ms"] for p in self.performance_results) / len(self.performance_results)
            print(f"   📊 Average response time: {avg_performance:.1f}ms")
        
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
            print("🎉 INSIGHTS & ANALYTICS SYSTEM IS PRODUCTION-READY!")
        elif success_rate >= 75:
            print("⚠️ INSIGHTS & ANALYTICS SYSTEM IS MOSTLY FUNCTIONAL - MINOR ISSUES DETECTED")
        else:
            print("❌ INSIGHTS & ANALYTICS SYSTEM HAS SIGNIFICANT ISSUES - NEEDS ATTENTION")
            
        print("="*80)
        
    async def run_all_tests(self):
        """Run all analytics tests"""
        print("🚀 Starting Insights & Analytics MVP v1.2 Testing...")
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
            await self.test_lifetime_stats_endpoint()
            await self.test_pillar_alignment_endpoint()
            await self.test_alignment_snapshot_endpoint()
            await self.test_authentication_requirements()
            await self.test_performance_consistency()
            await self.test_empty_data_scenarios()
            await self.test_error_handling()
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = AnalyticsTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())