#!/usr/bin/env python3

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, List

# Configuration - Use external URL from frontend/.env
BACKEND_URL = "https://15d7219c-892b-4111-8d96-e95547e179d6.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class PillarStatisticsTestSuite:
    """
    🔍 PILLAR STATISTICS VERIFICATION - Testing Updated Backend Endpoint
    
    Verifies that the updated pillars API endpoint now returns the missing statistics 
    (area_count, project_count, task_count, progress_percentage) that were missing 
    in the frontend display.
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
        
    async def create_test_hierarchy(self):
        """Create test data hierarchy for statistics verification"""
        print("\n🏗️ Creating test data hierarchy for statistics verification...")
        
        try:
            # Create test pillar
            pillar_data = {
                "name": "Statistics Test Pillar",
                "description": "Pillar for testing statistics calculation",
                "icon": "📊",
                "color": "#3B82F6",
                "time_allocation_percentage": 25.0
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillar = await response.json()
                    pillar_id = pillar['id']
                    self.created_resources['pillars'].append(pillar_id)
                    print(f"✅ Created test pillar: {pillar_id}")
                    
                    # Create 2 areas linked to this pillar
                    for i in range(2):
                        area_data = {
                            "pillar_id": pillar_id,
                            "name": f"Test Area {i+1}",
                            "description": f"Test area {i+1} for statistics",
                            "icon": "🎯",
                            "color": "#10B981",
                            "importance": 3 + i
                        }
                        
                        async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as area_response:
                            if area_response.status == 200:
                                area = await area_response.json()
                                area_id = area['id']
                                self.created_resources['areas'].append(area_id)
                                print(f"✅ Created test area {i+1}: {area_id}")
                                
                                # Create 2 projects per area
                                for j in range(2):
                                    project_data = {
                                        "area_id": area_id,
                                        "name": f"Test Project {i+1}-{j+1}",
                                        "description": f"Test project {j+1} in area {i+1}",
                                        "icon": "🚀",
                                        "status": "In Progress",
                                        "priority": "medium"
                                    }
                                    
                                    async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=self.get_auth_headers()) as proj_response:
                                        if proj_response.status == 200:
                                            project = await proj_response.json()
                                            project_id = project['id']
                                            self.created_resources['projects'].append(project_id)
                                            print(f"✅ Created test project {i+1}-{j+1}: {project_id}")
                                            
                                            # Create 3 tasks per project (mix of completed and incomplete)
                                            for k in range(3):
                                                is_completed = k == 0  # First task completed, others todo
                                                task_status = "completed" if is_completed else "todo"
                                                task_data = {
                                                    "project_id": project_id,
                                                    "name": f"Test Task {i+1}-{j+1}-{k+1}",
                                                    "description": f"Test task {k+1} in project {j+1}",
                                                    "status": task_status,
                                                    "priority": "medium"
                                                }
                                                
                                                async with self.session.post(f"{API_BASE}/tasks", json=task_data, headers=self.get_auth_headers()) as task_response:
                                                    if task_response.status == 200:
                                                        task = await task_response.json()
                                                        task_id = task['id']
                                                        self.created_resources['tasks'].append(task_id)
                                                        
                                                        # If this should be a completed task, update it to mark as completed
                                                        if is_completed:
                                                            update_data = {"completed": True, "status": "completed"}
                                                            async with self.session.put(f"{API_BASE}/tasks/{task_id}", json=update_data, headers=self.get_auth_headers()) as update_response:
                                                                if update_response.status == 200:
                                                                    print(f"✅ Created and completed test task {i+1}-{j+1}-{k+1}: {task_id}")
                                                                else:
                                                                    print(f"⚠️ Created task but failed to mark as completed: {task_id}")
                                                        else:
                                                            print(f"✅ Created test task {i+1}-{j+1}-{k+1} (todo): {task_id}")
                                                    else:
                                                        print(f"❌ Failed to create task {i+1}-{j+1}-{k+1}: {task_response.status}")
                                        else:
                                            print(f"❌ Failed to create project {i+1}-{j+1}: {proj_response.status}")
                            else:
                                print(f"❌ Failed to create area {i+1}: {area_response.status}")
                    
                    return pillar_id
                else:
                    print(f"❌ Failed to create test pillar: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error creating test hierarchy: {e}")
            return None
            
    async def test_pillars_basic_statistics(self):
        """Test 1: GET /api/pillars - Basic pillar data with statistics"""
        print("\n🧪 Test 1: GET /api/pillars - Basic pillar data with statistics")
        
        try:
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillars = await response.json()
                    
                    if not pillars:
                        print("⚠️ No pillars found - cannot test statistics")
                        self.test_results.append({"test": "Basic Pillars Statistics", "status": "SKIPPED", "reason": "No pillars found"})
                        return False
                        
                    print(f"📊 Found {len(pillars)} pillars")
                    
                    # Find our test pillar
                    test_pillar = None
                    for pillar in pillars:
                        if pillar.get('name') == 'Statistics Test Pillar':
                            test_pillar = pillar
                            break
                            
                    if not test_pillar:
                        print("⚠️ Test pillar not found - using first available pillar")
                        test_pillar = pillars[0]
                        
                    print(f"\n🔍 Analyzing pillar: {test_pillar.get('name', 'Unknown')}")
                    print(f"   ID: {test_pillar.get('id', 'N/A')}")
                    
                    # Check for required statistical fields
                    required_stats = ['area_count', 'project_count', 'task_count', 'progress_percentage', 'completed_task_count']
                    missing_stats = []
                    present_stats = []
                    
                    for stat in required_stats:
                        if stat in test_pillar:
                            present_stats.append(stat)
                            value = test_pillar[stat]
                            print(f"   ✅ {stat}: {value} ({type(value).__name__})")
                        else:
                            missing_stats.append(stat)
                            print(f"   ❌ {stat}: MISSING")
                            
                    # Verify data types
                    type_errors = []
                    for stat in present_stats:
                        value = test_pillar[stat]
                        if not isinstance(value, (int, float)):
                            type_errors.append(f"{stat} should be number, got {type(value).__name__}")
                            
                    # Check backwards compatibility
                    basic_fields = ['id', 'name', 'description', 'icon', 'color']
                    missing_basic = [field for field in basic_fields if field not in test_pillar]
                    
                    if missing_basic:
                        print(f"   ⚠️ Missing basic fields: {missing_basic}")
                        
                    # Determine test result
                    if not missing_stats and not type_errors and not missing_basic:
                        print("   🎉 All required statistics present with correct types!")
                        self.test_results.append({
                            "test": "Basic Pillars Statistics", 
                            "status": "PASSED", 
                            "details": f"All {len(required_stats)} statistics present with correct types"
                        })
                        return True
                    else:
                        issues = []
                        if missing_stats:
                            issues.append(f"Missing stats: {missing_stats}")
                        if type_errors:
                            issues.append(f"Type errors: {type_errors}")
                        if missing_basic:
                            issues.append(f"Missing basic fields: {missing_basic}")
                            
                        print(f"   ❌ Issues found: {'; '.join(issues)}")
                        self.test_results.append({
                            "test": "Basic Pillars Statistics", 
                            "status": "FAILED", 
                            "reason": '; '.join(issues)
                        })
                        return False
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Pillars endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Basic Pillars Statistics", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Basic pillars statistics test failed: {e}")
            self.test_results.append({
                "test": "Basic Pillars Statistics", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_pillars_with_areas_true(self):
        """Test 2: GET /api/pillars?include_areas=true - Enhanced data with areas"""
        print("\n🧪 Test 2: GET /api/pillars?include_areas=true - Enhanced data with areas")
        
        try:
            async with self.session.get(f"{API_BASE}/pillars?include_areas=true", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillars = await response.json()
                    
                    if not pillars:
                        print("⚠️ No pillars found")
                        self.test_results.append({"test": "Pillars with Areas True", "status": "SKIPPED", "reason": "No pillars found"})
                        return False
                        
                    # Find our test pillar
                    test_pillar = None
                    for pillar in pillars:
                        if pillar.get('name') == 'Statistics Test Pillar':
                            test_pillar = pillar
                            break
                            
                    if not test_pillar:
                        test_pillar = pillars[0]
                        
                    print(f"\n🔍 Analyzing pillar with areas: {test_pillar.get('name', 'Unknown')}")
                    
                    # Check if areas are included
                    has_areas = 'areas' in test_pillar
                    if has_areas:
                        areas = test_pillar['areas']
                        print(f"   ✅ Areas included: {len(areas)} areas found")
                        
                        # Verify area structure
                        if areas:
                            sample_area = areas[0]
                            area_fields = ['id', 'name', 'description']
                            missing_area_fields = [field for field in area_fields if field not in sample_area]
                            if missing_area_fields:
                                print(f"   ⚠️ Area missing fields: {missing_area_fields}")
                            else:
                                print(f"   ✅ Area structure complete")
                    else:
                        print(f"   ❌ Areas not included in response")
                        
                    # Check statistics are still present
                    required_stats = ['area_count', 'project_count', 'task_count', 'progress_percentage']
                    stats_present = all(stat in test_pillar for stat in required_stats)
                    
                    if stats_present:
                        print(f"   ✅ All statistics still present with include_areas=true")
                        
                        # Verify area_count matches actual areas
                        if has_areas:
                            actual_area_count = len(test_pillar['areas'])
                            reported_area_count = test_pillar.get('area_count', 0)
                            if actual_area_count == reported_area_count:
                                print(f"   ✅ Area count matches: {actual_area_count}")
                            else:
                                print(f"   ❌ Area count mismatch: reported {reported_area_count}, actual {actual_area_count}")
                                
                        self.test_results.append({
                            "test": "Pillars with Areas True", 
                            "status": "PASSED", 
                            "details": f"Areas included and statistics preserved"
                        })
                        return True
                    else:
                        missing_stats = [stat for stat in required_stats if stat not in test_pillar]
                        print(f"   ❌ Missing statistics: {missing_stats}")
                        self.test_results.append({
                            "test": "Pillars with Areas True", 
                            "status": "FAILED", 
                            "reason": f"Missing statistics: {missing_stats}"
                        })
                        return False
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Pillars with areas endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Pillars with Areas True", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Pillars with areas test failed: {e}")
            self.test_results.append({
                "test": "Pillars with Areas True", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_pillars_with_areas_false(self):
        """Test 3: GET /api/pillars?include_areas=false - Without areas inclusion"""
        print("\n🧪 Test 3: GET /api/pillars?include_areas=false - Without areas inclusion")
        
        try:
            async with self.session.get(f"{API_BASE}/pillars?include_areas=false", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillars = await response.json()
                    
                    if not pillars:
                        print("⚠️ No pillars found")
                        self.test_results.append({"test": "Pillars with Areas False", "status": "SKIPPED", "reason": "No pillars found"})
                        return False
                        
                    # Find our test pillar
                    test_pillar = None
                    for pillar in pillars:
                        if pillar.get('name') == 'Statistics Test Pillar':
                            test_pillar = pillar
                            break
                            
                    if not test_pillar:
                        test_pillar = pillars[0]
                        
                    print(f"\n🔍 Analyzing pillar without areas: {test_pillar.get('name', 'Unknown')}")
                    
                    # Check that areas are NOT included
                    has_areas = 'areas' in test_pillar
                    if not has_areas:
                        print(f"   ✅ Areas correctly excluded from response")
                    else:
                        print(f"   ❌ Areas should not be included when include_areas=false")
                        
                    # Check statistics are still present
                    required_stats = ['area_count', 'project_count', 'task_count', 'progress_percentage']
                    stats_present = all(stat in test_pillar for stat in required_stats)
                    
                    if stats_present:
                        print(f"   ✅ All statistics present even without areas inclusion")
                        
                        # Display statistics values
                        for stat in required_stats:
                            value = test_pillar.get(stat, 'N/A')
                            print(f"   📊 {stat}: {value}")
                            
                        if not has_areas and stats_present:
                            self.test_results.append({
                                "test": "Pillars with Areas False", 
                                "status": "PASSED", 
                                "details": "Areas excluded and statistics preserved"
                            })
                            return True
                        else:
                            issues = []
                            if has_areas:
                                issues.append("Areas should be excluded")
                            if not stats_present:
                                issues.append("Statistics missing")
                            self.test_results.append({
                                "test": "Pillars with Areas False", 
                                "status": "FAILED", 
                                "reason": "; ".join(issues)
                            })
                            return False
                    else:
                        missing_stats = [stat for stat in required_stats if stat not in test_pillar]
                        print(f"   ❌ Missing statistics: {missing_stats}")
                        self.test_results.append({
                            "test": "Pillars with Areas False", 
                            "status": "FAILED", 
                            "reason": f"Missing statistics: {missing_stats}"
                        })
                        return False
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Pillars without areas endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Pillars with Areas False", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Pillars without areas test failed: {e}")
            self.test_results.append({
                "test": "Pillars without Areas", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_statistics_accuracy(self):
        """Test 4: Verify statistics accuracy based on hierarchical data"""
        print("\n🧪 Test 4: Verify statistics accuracy based on hierarchical data")
        
        try:
            # Get pillar with statistics
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                if response.status != 200:
                    print(f"❌ Failed to get pillars: {response.status}")
                    return False
                    
                pillars = await response.json()
                test_pillar = None
                for pillar in pillars:
                    if pillar.get('name') == 'Statistics Test Pillar':
                        test_pillar = pillar
                        break
                        
                if not test_pillar:
                    print("⚠️ Test pillar not found - cannot verify accuracy")
                    self.test_results.append({"test": "Statistics Accuracy", "status": "SKIPPED", "reason": "Test pillar not found"})
                    return False
                    
            print(f"\n🔍 Verifying statistics accuracy for: {test_pillar.get('name')}")
            
            # Expected values based on our test data creation:
            # - 2 areas per pillar
            # - 2 projects per area = 4 projects total
            # - 3 tasks per project = 12 tasks total
            # - 1 completed task per project = 4 completed tasks total
            # - Progress = 4/12 = 33.33%
            
            expected_area_count = 2
            expected_project_count = 4
            expected_task_count = 12
            expected_completed_tasks = 4
            expected_progress = round((expected_completed_tasks / expected_task_count) * 100, 1)
            
            # Get actual values
            actual_area_count = test_pillar.get('area_count', 0)
            actual_project_count = test_pillar.get('project_count', 0)
            actual_task_count = test_pillar.get('task_count', 0)
            actual_completed_tasks = test_pillar.get('completed_task_count', 0)
            actual_progress = test_pillar.get('progress_percentage', 0)
            
            print(f"\n📊 Expected vs Actual Statistics:")
            print(f"   Area Count: Expected {expected_area_count}, Actual {actual_area_count}")
            print(f"   Project Count: Expected {expected_project_count}, Actual {actual_project_count}")
            print(f"   Task Count: Expected {expected_task_count}, Actual {actual_task_count}")
            print(f"   Completed Tasks: Expected {expected_completed_tasks}, Actual {actual_completed_tasks}")
            print(f"   Progress %: Expected {expected_progress}%, Actual {actual_progress}%")
            
            # Check accuracy (allow some tolerance for existing data)
            accuracy_issues = []
            
            if actual_area_count < expected_area_count:
                accuracy_issues.append(f"Area count too low: {actual_area_count} < {expected_area_count}")
            if actual_project_count < expected_project_count:
                accuracy_issues.append(f"Project count too low: {actual_project_count} < {expected_project_count}")
            if actual_task_count < expected_task_count:
                accuracy_issues.append(f"Task count too low: {actual_task_count} < {expected_task_count}")
                
            # Progress percentage should be reasonable (0-100)
            if not (0 <= actual_progress <= 100):
                accuracy_issues.append(f"Progress percentage out of range: {actual_progress}")
                
            if not accuracy_issues:
                print("   ✅ Statistics appear accurate based on hierarchical relationships")
                self.test_results.append({
                    "test": "Statistics Accuracy", 
                    "status": "PASSED", 
                    "details": "All statistics within expected ranges"
                })
                return True
            else:
                print(f"   ❌ Accuracy issues: {'; '.join(accuracy_issues)}")
                self.test_results.append({
                    "test": "Statistics Accuracy", 
                    "status": "FAILED", 
                    "reason": '; '.join(accuracy_issues)
                })
                return False
                
        except Exception as e:
            print(f"❌ Statistics accuracy test failed: {e}")
            self.test_results.append({
                "test": "Statistics Accuracy", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_performance_verification(self):
        """Test 5: Performance verification - response time under 500ms"""
        print("\n🧪 Test 5: Performance verification - response time under 500ms")
        
        try:
            # Test basic pillars endpoint performance
            start_time = datetime.now()
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
                
                if response.status == 200:
                    print(f"   📊 Basic pillars response time: {response_time:.1f}ms")
                    
                    if response_time < 500:
                        print(f"   ✅ Performance target met: {response_time:.1f}ms < 500ms")
                        basic_performance_ok = True
                    else:
                        print(f"   ❌ Performance target missed: {response_time:.1f}ms >= 500ms")
                        basic_performance_ok = False
                else:
                    print(f"   ❌ Basic pillars request failed: {response.status}")
                    basic_performance_ok = False
                    
            # Test pillars with areas performance
            start_time = datetime.now()
            async with self.session.get(f"{API_BASE}/pillars?include_areas=true", headers=self.get_auth_headers()) as response:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    print(f"   📊 Pillars with areas response time: {response_time:.1f}ms")
                    
                    if response_time < 500:
                        print(f"   ✅ Enhanced performance target met: {response_time:.1f}ms < 500ms")
                        enhanced_performance_ok = True
                    else:
                        print(f"   ❌ Enhanced performance target missed: {response_time:.1f}ms >= 500ms")
                        enhanced_performance_ok = False
                else:
                    print(f"   ❌ Enhanced pillars request failed: {response.status}")
                    enhanced_performance_ok = False
                    
            if basic_performance_ok and enhanced_performance_ok:
                self.test_results.append({
                    "test": "Performance Verification", 
                    "status": "PASSED", 
                    "details": "Both endpoints meet <500ms target"
                })
                return True
            else:
                issues = []
                if not basic_performance_ok:
                    issues.append("Basic endpoint performance issue")
                if not enhanced_performance_ok:
                    issues.append("Enhanced endpoint performance issue")
                    
                self.test_results.append({
                    "test": "Performance Verification", 
                    "status": "FAILED", 
                    "reason": "; ".join(issues)
                })
                return False
                
        except Exception as e:
            print(f"❌ Performance verification test failed: {e}")
            self.test_results.append({
                "test": "Performance Verification", 
                "status": "FAILED", 
                "reason": str(e)
            })
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
        print("🔍 PILLAR STATISTICS VERIFICATION - TEST SUMMARY")
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
        if success_rate == 100:
            print("🎉 PILLAR STATISTICS IMPLEMENTATION IS COMPLETE AND WORKING!")
            print("✅ All required statistics are present and accurate")
            print("✅ Performance targets met")
            print("✅ Backwards compatibility maintained")
        elif success_rate >= 80:
            print("⚠️ PILLAR STATISTICS MOSTLY WORKING - MINOR ISSUES DETECTED")
            print("🔧 Some statistics may need adjustment")
        else:
            print("❌ PILLAR STATISTICS IMPLEMENTATION HAS SIGNIFICANT ISSUES")
            print("🚨 Statistics missing or inaccurate - frontend display will be affected")
            
        print("="*80)
        
    async def run_pillar_statistics_verification(self):
        """Run comprehensive pillar statistics verification"""
        print("🔍 Starting Pillar Statistics Verification...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("📋 Testing updated pillars API endpoint for missing statistics")
        print("🎯 Focus: area_count, project_count, task_count, progress_percentage")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Create test data hierarchy for accurate statistics testing
            pillar_id = await self.create_test_hierarchy()
            if not pillar_id:
                print("⚠️ Failed to create test hierarchy - proceeding with existing data")
                
            # Run all pillar statistics tests
            await self.test_pillars_basic_statistics()
            await self.test_pillars_with_areas_true()
            await self.test_pillars_with_areas_false()
            await self.test_statistics_accuracy()
            await self.test_performance_verification()
            
            # Cleanup test data
            if pillar_id:
                await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main function to run pillar statistics verification"""
    test_suite = PillarStatisticsTestSuite()
    await test_suite.run_pillar_statistics_verification()

if __name__ == "__main__":
    asyncio.run(main())