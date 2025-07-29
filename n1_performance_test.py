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

class N1QueryPerformanceTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "performance.test@aurumlife.com"
        self.test_user_password = "TestPass123!"
        self.test_results = []
        self.performance_metrics = {}
        
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
        
    async def measure_endpoint_performance(self, endpoint: str, method: str = "GET", data: dict = None, expected_max_time: float = 1000.0):
        """Measure endpoint performance and detect potential N+1 patterns"""
        print(f"\n🔍 Testing {method} {endpoint}")
        
        start_time = time.time()
        
        try:
            if method == "GET":
                async with self.session.get(f"{API_BASE}{endpoint}", headers=self.get_auth_headers()) as response:
                    end_time = time.time()
                    response_time_ms = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Analyze response for potential N+1 indicators
                        n1_indicators = self.analyze_n1_patterns(response_data, response_time_ms)
                        
                        print(f"⏱️  Response time: {response_time_ms:.2f}ms")
                        
                        if response_time_ms <= expected_max_time:
                            status = "PASSED"
                            print(f"✅ Performance target met (≤{expected_max_time}ms)")
                        else:
                            status = "FAILED"
                            print(f"❌ Performance target exceeded (>{expected_max_time}ms)")
                            
                        self.performance_metrics[endpoint] = {
                            "response_time_ms": response_time_ms,
                            "status_code": response.status,
                            "data_size": len(str(response_data)),
                            "n1_indicators": n1_indicators,
                            "status": status
                        }
                        
                        return {
                            "endpoint": endpoint,
                            "method": method,
                            "response_time_ms": response_time_ms,
                            "status": status,
                            "n1_indicators": n1_indicators,
                            "data": response_data
                        }
                    else:
                        print(f"❌ Request failed with status: {response.status}")
                        error_text = await response.text()
                        print(f"Error: {error_text}")
                        return {
                            "endpoint": endpoint,
                            "method": method,
                            "status": "FAILED",
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            print(f"❌ Request failed with exception: {e}")
            return {
                "endpoint": endpoint,
                "method": method,
                "status": "FAILED",
                "error": str(e),
                "response_time_ms": response_time_ms
            }
            
    def analyze_n1_patterns(self, data: Any, response_time_ms: float) -> Dict[str, Any]:
        """Analyze response data for N+1 query patterns"""
        indicators = {
            "potential_n1": False,
            "reasons": [],
            "data_structure_analysis": {},
            "performance_analysis": {}
        }
        
        # Performance-based indicators
        if response_time_ms > 1000:
            indicators["potential_n1"] = True
            indicators["reasons"].append(f"Slow response time: {response_time_ms:.2f}ms suggests potential N+1 queries")
            
        # Data structure analysis
        if isinstance(data, list):
            indicators["data_structure_analysis"]["is_list"] = True
            indicators["data_structure_analysis"]["item_count"] = len(data)
            
            # Check for nested data that might indicate N+1
            if len(data) > 0 and isinstance(data[0], dict):
                sample_item = data[0]
                nested_fields = []
                
                for key, value in sample_item.items():
                    if isinstance(value, (list, dict)):
                        nested_fields.append(key)
                        
                if nested_fields:
                    indicators["data_structure_analysis"]["nested_fields"] = nested_fields
                    
                    # If we have many items with nested data, it could indicate N+1
                    if len(data) > 5 and len(nested_fields) > 0:
                        indicators["potential_n1"] = True
                        indicators["reasons"].append(f"Large dataset ({len(data)} items) with nested fields {nested_fields} - potential N+1 pattern")
                        
        elif isinstance(data, dict):
            indicators["data_structure_analysis"]["is_dict"] = True
            
            # Check for arrays within the response
            array_fields = []
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    array_fields.append({"field": key, "count": len(value)})
                    
            if array_fields:
                indicators["data_structure_analysis"]["array_fields"] = array_fields
                
        # Performance analysis
        indicators["performance_analysis"]["response_time_ms"] = response_time_ms
        indicators["performance_analysis"]["performance_category"] = (
            "excellent" if response_time_ms < 200 else
            "good" if response_time_ms < 500 else
            "acceptable" if response_time_ms < 1000 else
            "slow" if response_time_ms < 3000 else
            "very_slow"
        )
        
        return indicators
        
    async def test_areas_api_performance(self):
        """Test Areas API performance - the main endpoint mentioned in the issue"""
        print("\n🎯 CRITICAL TEST: Areas API Performance (N+1 Query Regression)")
        
        # Test the specific endpoint mentioned in the issue
        result = await self.measure_endpoint_performance(
            "/areas?include_projects=true&include_archived=false",
            expected_max_time=500.0  # Should be under 500ms based on previous optimization
        )
        
        self.test_results.append({
            "test": "Areas API Performance",
            "endpoint": "/areas?include_projects=true&include_archived=false",
            "result": result,
            "critical": True
        })
        
        # Also test without include_projects to compare
        result_simple = await self.measure_endpoint_performance(
            "/areas?include_archived=false",
            expected_max_time=200.0
        )
        
        self.test_results.append({
            "test": "Areas API Performance (Simple)",
            "endpoint": "/areas?include_archived=false", 
            "result": result_simple,
            "critical": False
        })
        
    async def test_projects_api_performance(self):
        """Test Projects API performance"""
        print("\n🎯 Projects API Performance Test")
        
        result = await self.measure_endpoint_performance(
            "/projects?include_archived=false",
            expected_max_time=300.0  # Should be around 282ms based on previous optimization
        )
        
        self.test_results.append({
            "test": "Projects API Performance",
            "endpoint": "/projects?include_archived=false",
            "result": result,
            "critical": True
        })
        
    async def test_dashboard_api_performance(self):
        """Test Dashboard API performance"""
        print("\n🎯 Dashboard API Performance Test")
        
        result = await self.measure_endpoint_performance(
            "/dashboard",
            expected_max_time=600.0  # Should be around 522ms based on previous optimization
        )
        
        self.test_results.append({
            "test": "Dashboard API Performance",
            "endpoint": "/dashboard",
            "result": result,
            "critical": True
        })
        
    async def test_insights_api_performance(self):
        """Test Insights API performance"""
        print("\n🎯 Insights API Performance Test")
        
        result = await self.measure_endpoint_performance(
            "/insights?date_range=all_time",
            expected_max_time=400.0  # Should be around 378ms based on previous optimization
        )
        
        self.test_results.append({
            "test": "Insights API Performance",
            "endpoint": "/insights?date_range=all_time",
            "result": result,
            "critical": True
        })
        
    async def test_ai_coach_api_performance(self):
        """Test AI Coach/Today API performance"""
        print("\n🎯 AI Coach/Today API Performance Test")
        
        result = await self.measure_endpoint_performance(
            "/today",
            expected_max_time=400.0  # Should be around 386ms based on previous optimization
        )
        
        self.test_results.append({
            "test": "AI Coach/Today API Performance",
            "endpoint": "/today",
            "result": result,
            "critical": True
        })
        
    async def test_pillars_api_performance(self):
        """Test Pillars API performance"""
        print("\n🎯 Pillars API Performance Test")
        
        result = await self.measure_endpoint_performance(
            "/pillars?include_areas=true&include_archived=false",
            expected_max_time=500.0
        )
        
        self.test_results.append({
            "test": "Pillars API Performance",
            "endpoint": "/pillars?include_areas=true&include_archived=false",
            "result": result,
            "critical": False
        })
        
    async def test_tasks_api_performance(self):
        """Test Tasks API performance"""
        print("\n🎯 Tasks API Performance Test")
        
        result = await self.measure_endpoint_performance(
            "/tasks",
            expected_max_time=500.0
        )
        
        self.test_results.append({
            "test": "Tasks API Performance",
            "endpoint": "/tasks",
            "result": result,
            "critical": False
        })
        
    async def run_performance_regression_analysis(self):
        """Analyze performance regression patterns"""
        print("\n🔬 PERFORMANCE REGRESSION ANALYSIS")
        print("="*60)
        
        critical_endpoints = [r for r in self.test_results if r.get("critical", False)]
        
        regression_detected = False
        slow_endpoints = []
        n1_suspects = []
        
        for test in critical_endpoints:
            result = test["result"]
            endpoint = test["endpoint"]
            
            if "response_time_ms" in result:
                response_time = result["response_time_ms"]
                
                # Check for performance regression
                if result["status"] == "FAILED":
                    regression_detected = True
                    slow_endpoints.append({
                        "endpoint": endpoint,
                        "response_time_ms": response_time,
                        "test": test["test"]
                    })
                    
                # Check for N+1 indicators
                if "n1_indicators" in result and result["n1_indicators"]["potential_n1"]:
                    n1_suspects.append({
                        "endpoint": endpoint,
                        "response_time_ms": response_time,
                        "reasons": result["n1_indicators"]["reasons"],
                        "test": test["test"]
                    })
                    
        # Report findings
        if regression_detected:
            print("🚨 PERFORMANCE REGRESSION DETECTED!")
            print(f"📊 {len(slow_endpoints)} critical endpoints are performing below target:")
            
            for endpoint_data in slow_endpoints:
                print(f"  ❌ {endpoint_data['test']}: {endpoint_data['response_time_ms']:.2f}ms")
                print(f"     Endpoint: {endpoint_data['endpoint']}")
                
        if n1_suspects:
            print(f"\n🔍 N+1 QUERY PATTERN SUSPECTS: {len(n1_suspects)} endpoints")
            
            for suspect in n1_suspects:
                print(f"  ⚠️  {suspect['test']}: {suspect['response_time_ms']:.2f}ms")
                print(f"     Endpoint: {suspect['endpoint']}")
                for reason in suspect['reasons']:
                    print(f"     💡 {reason}")
                    
        if not regression_detected and not n1_suspects:
            print("✅ NO PERFORMANCE REGRESSION DETECTED")
            print("✅ NO N+1 QUERY PATTERNS DETECTED")
            
        return {
            "regression_detected": regression_detected,
            "slow_endpoints": slow_endpoints,
            "n1_suspects": n1_suspects
        }
        
    def print_performance_summary(self):
        """Print comprehensive performance test summary"""
        print("\n" + "="*80)
        print("🎯 N+1 QUERY PERFORMANCE REGRESSION TEST SUMMARY")
        print("="*80)
        
        critical_tests = [t for t in self.test_results if t.get("critical", False)]
        all_tests = self.test_results
        
        critical_passed = len([t for t in critical_tests if t["result"].get("status") == "PASSED"])
        critical_failed = len([t for t in critical_tests if t["result"].get("status") == "FAILED"])
        
        all_passed = len([t for t in all_tests if t["result"].get("status") == "PASSED"])
        all_failed = len([t for t in all_tests if t["result"].get("status") == "FAILED"])
        
        print(f"🎯 CRITICAL ENDPOINTS: {critical_passed}/{len(critical_tests)} passed")
        print(f"📊 ALL ENDPOINTS: {all_passed}/{len(all_tests)} passed")
        
        print(f"\n📈 PERFORMANCE METRICS:")
        for test in self.test_results:
            result = test["result"]
            if "response_time_ms" in result:
                status_icon = "✅" if result["status"] == "PASSED" else "❌"
                critical_icon = "🔥" if test.get("critical", False) else "📊"
                
                print(f"{status_icon} {critical_icon} {test['test']}: {result['response_time_ms']:.2f}ms")
                
                # Show N+1 indicators if present
                if "n1_indicators" in result and result["n1_indicators"]["potential_n1"]:
                    print(f"    ⚠️  N+1 PATTERN DETECTED:")
                    for reason in result["n1_indicators"]["reasons"]:
                        print(f"       💡 {reason}")
                        
        # Calculate overall performance score
        if len(critical_tests) > 0:
            critical_success_rate = (critical_passed / len(critical_tests)) * 100
        else:
            critical_success_rate = 0
            
        print(f"\n🎯 CRITICAL ENDPOINT SUCCESS RATE: {critical_success_rate:.1f}%")
        
        print("\n" + "="*80)
        
        # Determine system status
        if critical_success_rate >= 90:
            print("🎉 NO PERFORMANCE REGRESSION DETECTED - OPTIMIZATIONS WORKING!")
        elif critical_success_rate >= 70:
            print("⚠️ MINOR PERFORMANCE ISSUES DETECTED - INVESTIGATION RECOMMENDED")
        else:
            print("🚨 CRITICAL PERFORMANCE REGRESSION DETECTED - IMMEDIATE ACTION REQUIRED!")
            print("💡 N+1 QUERY PATTERNS MAY HAVE RETURNED - CHECK BATCH FETCHING OPTIMIZATIONS")
            
        print("="*80)
        
    async def run_all_tests(self):
        """Run all N+1 performance regression tests"""
        print("🚀 Starting N+1 Query Performance Regression Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("🎯 Focus: Detecting N+1 query patterns and performance regression")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            print("✅ Authentication successful")
            
            # Run performance tests on critical endpoints
            await self.test_areas_api_performance()  # CRITICAL - mentioned in issue
            await self.test_projects_api_performance()  # CRITICAL - previously optimized
            await self.test_dashboard_api_performance()  # CRITICAL - previously optimized
            await self.test_insights_api_performance()  # CRITICAL - previously optimized
            await self.test_ai_coach_api_performance()  # CRITICAL - previously optimized
            
            # Run additional performance tests
            await self.test_pillars_api_performance()
            await self.test_tasks_api_performance()
            
            # Analyze results for regression patterns
            regression_analysis = await self.run_performance_regression_analysis()
            
        finally:
            await self.cleanup_session()
            
        # Print comprehensive summary
        self.print_performance_summary()
        
        return regression_analysis

async def main():
    """Main test execution"""
    test_suite = N1QueryPerformanceTestSuite()
    regression_analysis = await test_suite.run_all_tests()
    
    # Return analysis for further processing
    return regression_analysis

if __name__ == "__main__":
    asyncio.run(main())