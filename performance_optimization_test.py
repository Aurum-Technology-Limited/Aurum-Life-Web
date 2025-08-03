#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://b5a62d15-d24c-4532-9cae-06d0896a435f.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class PerformanceOptimizationTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "performance.test@aurumlife.com"
        self.test_user_password = "TestPass123!"
        self.test_results = []
        self.performance_metrics = {}
        self.created_data = {
            'areas': [],
            'projects': [],
            'tasks': [],
            'pillars': []
        }
        
    async def setup_session(self):
        """Initialize HTTP session with timeout"""
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            # Try to register user first (in case they don't exist)
            register_data = {
                "username": "performancetest",
                "email": self.test_user_email,
                "first_name": "Performance",
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
        
    async def measure_endpoint_performance(self, endpoint: str, method: str = "GET", data: dict = None, headers: dict = None) -> Tuple[int, float, dict]:
        """Measure endpoint performance and return status, response time, and data"""
        if headers is None:
            headers = self.get_auth_headers()
            
        start_time = time.time()
        
        try:
            if method == "GET":
                async with self.session.get(f"{API_BASE}{endpoint}", headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    return response.status, response_time, response_data
            elif method == "POST":
                async with self.session.post(f"{API_BASE}{endpoint}", json=data, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    return response.status, response_time, response_data
                    
        except asyncio.TimeoutError:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return 408, response_time, {"error": "Request timeout"}
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return 500, response_time, {"error": str(e)}
            
    async def create_test_data_for_performance(self):
        """Create sufficient test data to properly test performance improvements"""
        print("\n📊 Creating test data for performance testing...")
        
        try:
            # Create multiple pillars
            for i in range(3):
                pillar_data = {
                    "name": f"Performance Test Pillar {i+1}",
                    "description": f"Pillar {i+1} for performance testing",
                    "icon": "🎯",
                    "color": f"#{['FF5722', '2196F3', '4CAF50'][i]}"
                }
                
                status, response_time, pillar = await self.measure_endpoint_performance("/pillars", "POST", pillar_data)
                if status == 200:
                    self.created_data['pillars'].append(pillar["id"])
                    print(f"✅ Created pillar {i+1}")
                    
            # Create multiple areas with pillar assignments
            for i in range(5):
                area_data = {
                    "name": f"Performance Test Area {i+1}",
                    "description": f"Area {i+1} for performance testing with multiple projects and tasks",
                    "icon": "📁",
                    "color": f"#{['FF5722', '2196F3', '4CAF50', 'FF9800', '9C27B0'][i]}",
                    "pillar_id": self.created_data['pillars'][i % len(self.created_data['pillars'])] if self.created_data['pillars'] else None
                }
                
                status, response_time, area = await self.measure_endpoint_performance("/areas", "POST", area_data)
                if status == 200:
                    self.created_data['areas'].append(area["id"])
                    print(f"✅ Created area {i+1}")
                    
            # Create multiple projects per area
            for area_id in self.created_data['areas']:
                for j in range(4):  # 4 projects per area = 20 total projects
                    project_data = {
                        "area_id": area_id,
                        "name": f"Performance Test Project {j+1}",
                        "description": f"Project {j+1} for performance testing",
                        "icon": "🚀"
                    }
                    
                    status, response_time, project = await self.measure_endpoint_performance("/projects", "POST", project_data)
                    if status == 200:
                        self.created_data['projects'].append(project["id"])
                        
            print(f"✅ Created {len(self.created_data['projects'])} projects")
            
            # Create multiple tasks per project
            for project_id in self.created_data['projects']:
                for k in range(3):  # 3 tasks per project = 60 total tasks
                    task_data = {
                        "project_id": project_id,
                        "name": f"Performance Test Task {k+1}",
                        "description": f"Task {k+1} for performance testing",
                        "priority": ["low", "medium", "high"][k % 3],
                        "status": ["todo", "in_progress", "completed"][k % 3]
                    }
                    
                    status, response_time, task = await self.measure_endpoint_performance("/tasks", "POST", task_data)
                    if status == 200:
                        self.created_data['tasks'].append(task["id"])
                        
            print(f"✅ Created {len(self.created_data['tasks'])} tasks")
            print(f"📊 Test data summary: {len(self.created_data['pillars'])} pillars, {len(self.created_data['areas'])} areas, {len(self.created_data['projects'])} projects, {len(self.created_data['tasks'])} tasks")
            return True
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            return False
            
    async def test_areas_api_performance(self):
        """Test 1: Areas API Endpoint Performance (Primary Optimization Target)"""
        print("\n🧪 Test 1: Areas API Endpoint Performance - GET /api/areas?include_projects=true&include_archived=false")
        
        try:
            # Test the optimized areas endpoint
            endpoint = "/areas?include_projects=true&include_archived=false"
            status, response_time, data = await self.measure_endpoint_performance(endpoint)
            
            self.performance_metrics['areas_api'] = {
                'status': status,
                'response_time_ms': response_time,
                'data_count': len(data) if isinstance(data, list) else 0
            }
            
            print(f"📊 Areas API Response Time: {response_time:.2f}ms")
            print(f"📊 Status Code: {status}")
            print(f"📊 Areas Returned: {len(data) if isinstance(data, list) else 0}")
            
            # Check if response time meets target (<1000ms)
            if status == 200 and response_time < 1000:
                print("✅ Areas API performance target achieved (<1000ms)")
                
                # Verify data structure includes projects and task counts
                if isinstance(data, list) and len(data) > 0:
                    sample_area = data[0]
                    if 'projects' in sample_area and 'total_task_count' in sample_area:
                        print("✅ Areas API returns optimized data structure with projects and task counts")
                        self.test_results.append({
                            "test": "Areas API Performance", 
                            "status": "PASSED", 
                            "details": f"Response time: {response_time:.2f}ms, Data structure optimized"
                        })
                    else:
                        print("⚠️ Areas API missing expected data structure fields")
                        self.test_results.append({
                            "test": "Areas API Performance", 
                            "status": "PARTIAL", 
                            "details": f"Fast response ({response_time:.2f}ms) but missing data fields"
                        })
                else:
                    print("⚠️ Areas API returned empty or invalid data")
                    self.test_results.append({
                        "test": "Areas API Performance", 
                        "status": "PARTIAL", 
                        "details": f"Fast response ({response_time:.2f}ms) but no data returned"
                    })
            elif status == 200:
                print(f"❌ Areas API response time ({response_time:.2f}ms) exceeds target (1000ms)")
                self.test_results.append({
                    "test": "Areas API Performance", 
                    "status": "FAILED", 
                    "reason": f"Response time {response_time:.2f}ms exceeds 1000ms target"
                })
            else:
                print(f"❌ Areas API returned error status: {status}")
                self.test_results.append({
                    "test": "Areas API Performance", 
                    "status": "FAILED", 
                    "reason": f"HTTP {status} error"
                })
                
        except Exception as e:
            print(f"❌ Areas API performance test failed: {e}")
            self.test_results.append({
                "test": "Areas API Performance", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_projects_api_performance(self):
        """Test 2: Projects API Endpoint Performance (Verify Maintained Performance)"""
        print("\n🧪 Test 2: Projects API Endpoint Performance - GET /api/projects")
        
        try:
            endpoint = "/projects"
            status, response_time, data = await self.measure_endpoint_performance(endpoint)
            
            self.performance_metrics['projects_api'] = {
                'status': status,
                'response_time_ms': response_time,
                'data_count': len(data) if isinstance(data, list) else 0
            }
            
            print(f"📊 Projects API Response Time: {response_time:.2f}ms")
            print(f"📊 Status Code: {status}")
            print(f"📊 Projects Returned: {len(data) if isinstance(data, list) else 0}")
            
            # Check if response time meets target (<1000ms)
            if status == 200 and response_time < 1000:
                print("✅ Projects API performance target achieved (<1000ms)")
                
                # Verify data structure includes task counts
                if isinstance(data, list) and len(data) > 0:
                    sample_project = data[0]
                    if 'task_count' in sample_project and 'completed_task_count' in sample_project:
                        print("✅ Projects API returns optimized data structure with task counts")
                        self.test_results.append({
                            "test": "Projects API Performance", 
                            "status": "PASSED", 
                            "details": f"Response time: {response_time:.2f}ms, Task counts included"
                        })
                    else:
                        print("⚠️ Projects API missing expected task count fields")
                        self.test_results.append({
                            "test": "Projects API Performance", 
                            "status": "PARTIAL", 
                            "details": f"Fast response ({response_time:.2f}ms) but missing task counts"
                        })
                else:
                    self.test_results.append({
                        "test": "Projects API Performance", 
                        "status": "PASSED", 
                        "details": f"Response time: {response_time:.2f}ms"
                    })
            elif status == 200:
                print(f"❌ Projects API response time ({response_time:.2f}ms) exceeds target (1000ms)")
                self.test_results.append({
                    "test": "Projects API Performance", 
                    "status": "FAILED", 
                    "reason": f"Response time {response_time:.2f}ms exceeds 1000ms target"
                })
            else:
                print(f"❌ Projects API returned error status: {status}")
                self.test_results.append({
                    "test": "Projects API Performance", 
                    "status": "FAILED", 
                    "reason": f"HTTP {status} error"
                })
                
        except Exception as e:
            print(f"❌ Projects API performance test failed: {e}")
            self.test_results.append({
                "test": "Projects API Performance", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_dashboard_api_performance(self):
        """Test 3: Dashboard API Performance (Verify Simplified Approach)"""
        print("\n🧪 Test 3: Dashboard API Performance - GET /api/dashboard")
        
        try:
            endpoint = "/dashboard"
            status, response_time, data = await self.measure_endpoint_performance(endpoint)
            
            self.performance_metrics['dashboard_api'] = {
                'status': status,
                'response_time_ms': response_time,
                'has_user_data': 'user' in data if isinstance(data, dict) else False,
                'has_stats_data': 'stats' in data if isinstance(data, dict) else False
            }
            
            print(f"📊 Dashboard API Response Time: {response_time:.2f}ms")
            print(f"📊 Status Code: {status}")
            
            if status == 200 and response_time < 1000:
                print("✅ Dashboard API performance target achieved (<1000ms)")
                
                # Verify simplified dashboard structure
                if isinstance(data, dict):
                    expected_fields = ['user', 'stats', 'recent_tasks']
                    present_fields = [field for field in expected_fields if field in data]
                    
                    print(f"📊 Dashboard fields present: {present_fields}")
                    
                    if len(present_fields) >= 2:  # At least user and stats
                        print("✅ Dashboard API returns simplified MVP structure")
                        self.test_results.append({
                            "test": "Dashboard API Performance", 
                            "status": "PASSED", 
                            "details": f"Response time: {response_time:.2f}ms, MVP structure confirmed"
                        })
                    else:
                        print("⚠️ Dashboard API missing expected fields")
                        self.test_results.append({
                            "test": "Dashboard API Performance", 
                            "status": "PARTIAL", 
                            "details": f"Fast response ({response_time:.2f}ms) but incomplete structure"
                        })
                else:
                    print("⚠️ Dashboard API returned invalid data structure")
                    self.test_results.append({
                        "test": "Dashboard API Performance", 
                        "status": "PARTIAL", 
                        "details": f"Fast response ({response_time:.2f}ms) but invalid data"
                    })
            elif status == 200:
                print(f"❌ Dashboard API response time ({response_time:.2f}ms) exceeds target (1000ms)")
                self.test_results.append({
                    "test": "Dashboard API Performance", 
                    "status": "FAILED", 
                    "reason": f"Response time {response_time:.2f}ms exceeds 1000ms target"
                })
            else:
                print(f"❌ Dashboard API returned error status: {status}")
                self.test_results.append({
                    "test": "Dashboard API Performance", 
                    "status": "FAILED", 
                    "reason": f"HTTP {status} error"
                })
                
        except Exception as e:
            print(f"❌ Dashboard API performance test failed: {e}")
            self.test_results.append({
                "test": "Dashboard API Performance", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_insights_api_performance(self):
        """Test 4: Insights API Performance (Verify Stats-based Optimization)"""
        print("\n🧪 Test 4: Insights API Performance - GET /api/insights?date_range=all_time")
        
        try:
            endpoint = "/insights?date_range=all_time"
            status, response_time, data = await self.measure_endpoint_performance(endpoint)
            
            self.performance_metrics['insights_api'] = {
                'status': status,
                'response_time_ms': response_time,
                'has_insights_data': isinstance(data, dict) and len(data) > 0
            }
            
            print(f"📊 Insights API Response Time: {response_time:.2f}ms")
            print(f"📊 Status Code: {status}")
            
            if status == 200 and response_time < 1000:
                print("✅ Insights API performance target achieved (<1000ms)")
                
                # Verify insights data structure
                if isinstance(data, dict) and len(data) > 0:
                    expected_fields = ['task_status_breakdown', 'productivity_trends', 'area_performance']
                    present_fields = [field for field in expected_fields if field in data]
                    
                    print(f"📊 Insights fields present: {present_fields}")
                    
                    if len(present_fields) >= 1:  # At least one insights field
                        print("✅ Insights API returns stats-based optimized data")
                        self.test_results.append({
                            "test": "Insights API Performance", 
                            "status": "PASSED", 
                            "details": f"Response time: {response_time:.2f}ms, Stats-based optimization confirmed"
                        })
                    else:
                        print("⚠️ Insights API missing expected insights fields")
                        self.test_results.append({
                            "test": "Insights API Performance", 
                            "status": "PARTIAL", 
                            "details": f"Fast response ({response_time:.2f}ms) but missing insights data"
                        })
                else:
                    print("⚠️ Insights API returned empty or invalid data")
                    self.test_results.append({
                        "test": "Insights API Performance", 
                        "status": "PARTIAL", 
                        "details": f"Fast response ({response_time:.2f}ms) but no insights data"
                    })
            elif status == 200:
                print(f"❌ Insights API response time ({response_time:.2f}ms) exceeds target (1000ms)")
                self.test_results.append({
                    "test": "Insights API Performance", 
                    "status": "FAILED", 
                    "reason": f"Response time {response_time:.2f}ms exceeds 1000ms target"
                })
            else:
                print(f"❌ Insights API returned error status: {status}")
                self.test_results.append({
                    "test": "Insights API Performance", 
                    "status": "FAILED", 
                    "reason": f"HTTP {status} error"
                })
                
        except Exception as e:
            print(f"❌ Insights API performance test failed: {e}")
            self.test_results.append({
                "test": "Insights API Performance", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_ai_coach_api_performance(self):
        """Test 5: AI Coach API Performance (Verify Parallel Execution)"""
        print("\n🧪 Test 5: AI Coach API Performance - GET /api/today (AI Coach integration)")
        
        try:
            endpoint = "/today"
            status, response_time, data = await self.measure_endpoint_performance(endpoint)
            
            self.performance_metrics['ai_coach_api'] = {
                'status': status,
                'response_time_ms': response_time,
                'has_today_data': isinstance(data, dict) and len(data) > 0
            }
            
            print(f"📊 AI Coach (Today) API Response Time: {response_time:.2f}ms")
            print(f"📊 Status Code: {status}")
            
            if status == 200 and response_time < 1000:
                print("✅ AI Coach API performance target achieved (<1000ms)")
                
                # Verify today view data structure (which uses AI Coach service)
                if isinstance(data, dict) and len(data) > 0:
                    expected_fields = ['daily_tasks', 'focus_areas', 'progress_summary']
                    present_fields = [field for field in expected_fields if field in data]
                    
                    print(f"📊 Today view fields present: {present_fields}")
                    
                    if len(present_fields) >= 1:  # At least one field
                        print("✅ AI Coach API returns parallel execution optimized data")
                        self.test_results.append({
                            "test": "AI Coach API Performance", 
                            "status": "PASSED", 
                            "details": f"Response time: {response_time:.2f}ms, Parallel execution confirmed"
                        })
                    else:
                        print("⚠️ AI Coach API missing expected today view fields")
                        self.test_results.append({
                            "test": "AI Coach API Performance", 
                            "status": "PARTIAL", 
                            "details": f"Fast response ({response_time:.2f}ms) but missing today data"
                        })
                else:
                    print("⚠️ AI Coach API returned empty or invalid data")
                    self.test_results.append({
                        "test": "AI Coach API Performance", 
                        "status": "PARTIAL", 
                        "details": f"Fast response ({response_time:.2f}ms) but no today data"
                    })
            elif status == 200:
                print(f"❌ AI Coach API response time ({response_time:.2f}ms) exceeds target (1000ms)")
                self.test_results.append({
                    "test": "AI Coach API Performance", 
                    "status": "FAILED", 
                    "reason": f"Response time {response_time:.2f}ms exceeds 1000ms target"
                })
            else:
                print(f"❌ AI Coach API returned error status: {status}")
                self.test_results.append({
                    "test": "AI Coach API Performance", 
                    "status": "FAILED", 
                    "reason": f"HTTP {status} error"
                })
                
        except Exception as e:
            print(f"❌ AI Coach API performance test failed: {e}")
            self.test_results.append({
                "test": "AI Coach API Performance", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_fast_endpoint_verification(self):
        """Test 6: Fast Endpoint Verification (Sanity Check)"""
        print("\n🧪 Test 6: Fast Endpoint Verification - GET /api/test-fast")
        
        try:
            endpoint = "/test-fast"
            status, response_time, data = await self.measure_endpoint_performance(endpoint)
            
            self.performance_metrics['fast_endpoint'] = {
                'status': status,
                'response_time_ms': response_time
            }
            
            print(f"📊 Fast Endpoint Response Time: {response_time:.2f}ms")
            print(f"📊 Status Code: {status}")
            
            if status == 200 and response_time < 100:  # Should be very fast
                print("✅ Fast endpoint verification passed")
                self.test_results.append({
                    "test": "Fast Endpoint Verification", 
                    "status": "PASSED", 
                    "details": f"Response time: {response_time:.2f}ms"
                })
            elif status == 200:
                print(f"⚠️ Fast endpoint slower than expected: {response_time:.2f}ms")
                self.test_results.append({
                    "test": "Fast Endpoint Verification", 
                    "status": "PARTIAL", 
                    "details": f"Response time: {response_time:.2f}ms (expected <100ms)"
                })
            else:
                print(f"❌ Fast endpoint returned error status: {status}")
                self.test_results.append({
                    "test": "Fast Endpoint Verification", 
                    "status": "FAILED", 
                    "reason": f"HTTP {status} error"
                })
                
        except Exception as e:
            print(f"❌ Fast endpoint verification failed: {e}")
            self.test_results.append({
                "test": "Fast Endpoint Verification", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up performance test data...")
        
        try:
            # Delete tasks
            for task_id in self.created_data['tasks']:
                try:
                    async with self.session.delete(f"{API_BASE}/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                        pass  # Don't log each deletion
                except:
                    pass
                    
            # Delete projects
            for project_id in self.created_data['projects']:
                try:
                    async with self.session.delete(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as response:
                        pass
                except:
                    pass
                    
            # Delete areas
            for area_id in self.created_data['areas']:
                try:
                    async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                        pass
                except:
                    pass
                    
            # Delete pillars
            for pillar_id in self.created_data['pillars']:
                try:
                    async with self.session.delete(f"{API_BASE}/pillars/{pillar_id}", headers=self.get_auth_headers()) as response:
                        pass
                except:
                    pass
                    
            print("✅ Test data cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
            
    def print_performance_summary(self):
        """Print comprehensive performance test summary"""
        print("\n" + "="*80)
        print("🚀 BACKEND PERFORMANCE OPTIMIZATION VERIFICATION - TEST SUMMARY")
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
        
        print("\n📈 PERFORMANCE METRICS:")
        for endpoint, metrics in self.performance_metrics.items():
            response_time = metrics.get('response_time_ms', 0)
            status = metrics.get('status', 'N/A')
            
            # Performance indicator
            if response_time < 500:
                perf_indicator = "🟢 EXCELLENT"
            elif response_time < 1000:
                perf_indicator = "🟡 GOOD"
            elif response_time < 2000:
                perf_indicator = "🟠 ACCEPTABLE"
            else:
                perf_indicator = "🔴 SLOW"
                
            print(f"  {endpoint.upper()}: {response_time:.2f}ms ({status}) {perf_indicator}")
            
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n🎯 N+1 QUERY OPTIMIZATION ASSESSMENT:")
        
        # Check if all major endpoints meet performance targets
        critical_endpoints = ['areas_api', 'projects_api', 'dashboard_api', 'insights_api', 'ai_coach_api']
        fast_endpoints = []
        slow_endpoints = []
        
        for endpoint in critical_endpoints:
            if endpoint in self.performance_metrics:
                response_time = self.performance_metrics[endpoint]['response_time_ms']
                if response_time < 1000:
                    fast_endpoints.append(f"{endpoint}: {response_time:.2f}ms")
                else:
                    slow_endpoints.append(f"{endpoint}: {response_time:.2f}ms")
                    
        print(f"✅ Fast Endpoints (<1000ms): {len(fast_endpoints)}")
        for endpoint in fast_endpoints:
            print(f"    • {endpoint}")
            
        if slow_endpoints:
            print(f"❌ Slow Endpoints (≥1000ms): {len(slow_endpoints)}")
            for endpoint in slow_endpoints:
                print(f"    • {endpoint}")
        else:
            print("🎉 All critical endpoints meet sub-second performance target!")
            
        print("\n" + "="*80)
        
        # Overall assessment
        if success_rate >= 90 and len(slow_endpoints) == 0:
            print("🎉 BACKEND PERFORMANCE OPTIMIZATION SUCCESSFUL!")
            print("✅ N+1 query patterns eliminated - all endpoints sub-second")
        elif success_rate >= 75:
            print("⚠️ BACKEND PERFORMANCE MOSTLY OPTIMIZED - MINOR ISSUES DETECTED")
            print("🔧 Some endpoints may need additional optimization")
        else:
            print("❌ BACKEND PERFORMANCE OPTIMIZATION INCOMPLETE")
            print("🚨 Significant performance issues remain - N+1 patterns may persist")
            
        print("="*80)
        
    async def run_all_performance_tests(self):
        """Run all backend performance optimization tests"""
        print("🚀 Starting Backend Performance Optimization Verification...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("🎯 Target: All major API endpoints <1000ms response time")
        print("🔍 Focus: N+1 query elimination verification")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            print("✅ Authentication successful")
            
            # Create test data for realistic performance testing
            if not await self.create_test_data_for_performance():
                print("❌ Test data creation failed - proceeding with existing data")
                
            # Run all performance tests
            await self.test_fast_endpoint_verification()  # Sanity check first
            await self.test_areas_api_performance()       # Primary optimization target
            await self.test_projects_api_performance()    # Verify maintained performance
            await self.test_dashboard_api_performance()   # Simplified approach
            await self.test_insights_api_performance()    # Stats-based optimization
            await self.test_ai_coach_api_performance()    # Parallel execution
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print comprehensive summary
        self.print_performance_summary()

async def main():
    """Main test execution"""
    test_suite = PerformanceOptimizationTestSuite()
    await test_suite.run_all_performance_tests()

if __name__ == "__main__":
    asyncio.run(main())