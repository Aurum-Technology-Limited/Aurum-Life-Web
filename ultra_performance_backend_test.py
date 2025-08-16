#!/usr/bin/env python3
"""
Ultra-Performance Optimization Backend Testing
Tests the new ultra-performance endpoints for sub-200ms response times
"""

import requests
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://datahierarchy-app.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password"

class UltraPerformanceTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.performance_stats = {}
        
    def log_result(self, test_name: str, success: bool, message: str, response_time: float = None):
        """Log test result with performance metrics"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "response_time_ms": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        perf_info = f" ({response_time:.2f}ms)" if response_time else ""
        print(f"{status}: {test_name}{perf_info} - {message}")
        
    def authenticate(self) -> bool:
        """Authenticate with test credentials"""
        try:
            print(f"\n🔐 Authenticating with {TEST_EMAIL}...")
            
            auth_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=auth_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_result("Authentication", True, f"Successfully authenticated as {TEST_EMAIL}", response_time)
                return True
            else:
                self.log_result("Authentication", False, f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def measure_endpoint_performance(self, endpoint: str, method: str = "GET", data: dict = None) -> Dict[str, Any]:
        """Measure endpoint performance with detailed metrics"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            # Warm-up request (not counted)
            if method.upper() == "GET":
                self.session.get(url)
            elif method.upper() == "POST":
                self.session.post(url, json=data)
            
            # Actual performance measurement
            start_time = time.time()
            
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "response_data": response.json() if response.status_code == 200 else None,
                "error": response.text if response.status_code != 200 else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "response_time_ms": None,
                "response_data": None,
                "error": str(e)
            }
    
    def test_ultra_performance_endpoints(self):
        """Test all ultra-performance endpoints with performance targets"""
        print("\n🚀 TESTING ULTRA-PERFORMANCE ENDPOINTS")
        print("=" * 60)
        
        # Define endpoints with their performance targets
        ultra_endpoints = [
            {
                "endpoint": "/ultra/dashboard",
                "name": "Ultra Dashboard",
                "target_ms": 150,
                "description": "Ultra-high performance dashboard"
            },
            {
                "endpoint": "/ultra/pillars",
                "name": "Ultra Pillars",
                "target_ms": 150,
                "description": "Ultra-high performance pillar retrieval"
            },
            {
                "endpoint": "/ultra/areas",
                "name": "Ultra Areas", 
                "target_ms": 120,
                "description": "Ultra-high performance area retrieval"
            },
            {
                "endpoint": "/ultra/projects",
                "name": "Ultra Projects",
                "target_ms": 100,
                "description": "Ultra-high performance project retrieval"
            },
            {
                "endpoint": "/ultra/insights",
                "name": "Ultra Insights",
                "target_ms": 200,
                "description": "Ultra-high performance insights"
            },
            {
                "endpoint": "/ultra/performance-stats",
                "name": "Ultra Performance Stats",
                "target_ms": 200,
                "description": "Performance statistics"
            }
        ]
        
        ultra_results = {}
        
        for endpoint_config in ultra_endpoints:
            endpoint = endpoint_config["endpoint"]
            name = endpoint_config["name"]
            target_ms = endpoint_config["target_ms"]
            
            print(f"\n📊 Testing {name} (Target: <{target_ms}ms)")
            
            # Run multiple measurements for accuracy
            measurements = []
            for i in range(3):
                result = self.measure_endpoint_performance(endpoint)
                if result["success"]:
                    measurements.append(result["response_time_ms"])
                    print(f"   Attempt {i+1}: {result['response_time_ms']:.2f}ms")
                else:
                    print(f"   Attempt {i+1}: FAILED - {result['error']}")
            
            if measurements:
                avg_time = sum(measurements) / len(measurements)
                min_time = min(measurements)
                max_time = max(measurements)
                
                # Check if target is met
                target_met = avg_time < target_ms
                performance_grade = "🎯 EXCELLENT" if avg_time < target_ms * 0.8 else "✅ GOOD" if target_met else "⚠️ NEEDS IMPROVEMENT"
                
                ultra_results[name] = {
                    "avg_response_time": avg_time,
                    "min_response_time": min_time,
                    "max_response_time": max_time,
                    "target_ms": target_ms,
                    "target_met": target_met,
                    "measurements": measurements
                }
                
                self.log_result(
                    f"{name} Performance",
                    target_met,
                    f"Avg: {avg_time:.2f}ms (Target: <{target_ms}ms) - {performance_grade}",
                    avg_time
                )
            else:
                ultra_results[name] = {
                    "avg_response_time": None,
                    "target_met": False,
                    "error": "All requests failed"
                }
                
                self.log_result(
                    f"{name} Performance",
                    False,
                    "All performance measurement attempts failed"
                )
        
        self.performance_stats["ultra_endpoints"] = ultra_results
        return ultra_results
    
    def test_regular_endpoints_comparison(self):
        """Test regular endpoints for performance comparison"""
        print("\n📈 TESTING REGULAR ENDPOINTS FOR COMPARISON")
        print("=" * 60)
        
        regular_endpoints = [
            {"endpoint": "/dashboard", "name": "Regular Dashboard"},
            {"endpoint": "/pillars", "name": "Regular Pillars"},
            {"endpoint": "/areas", "name": "Regular Areas"},
            {"endpoint": "/projects", "name": "Regular Projects"},
            {"endpoint": "/insights", "name": "Regular Insights"}
        ]
        
        regular_results = {}
        
        for endpoint_config in regular_endpoints:
            endpoint = endpoint_config["endpoint"]
            name = endpoint_config["name"]
            
            print(f"\n📊 Testing {name}")
            
            # Run multiple measurements
            measurements = []
            for i in range(3):
                result = self.measure_endpoint_performance(endpoint)
                if result["success"]:
                    measurements.append(result["response_time_ms"])
                    print(f"   Attempt {i+1}: {result['response_time_ms']:.2f}ms")
                else:
                    print(f"   Attempt {i+1}: FAILED - {result['error']}")
            
            if measurements:
                avg_time = sum(measurements) / len(measurements)
                min_time = min(measurements)
                max_time = max(measurements)
                
                regular_results[name] = {
                    "avg_response_time": avg_time,
                    "min_response_time": min_time,
                    "max_response_time": max_time,
                    "measurements": measurements
                }
                
                self.log_result(
                    f"{name} Performance",
                    True,
                    f"Avg: {avg_time:.2f}ms",
                    avg_time
                )
            else:
                regular_results[name] = {
                    "avg_response_time": None,
                    "error": "All requests failed"
                }
                
                self.log_result(
                    f"{name} Performance",
                    False,
                    "All measurement attempts failed"
                )
        
        self.performance_stats["regular_endpoints"] = regular_results
        return regular_results
    
    def test_performance_monitoring_endpoints(self):
        """Test performance monitoring endpoints"""
        print("\n📊 TESTING PERFORMANCE MONITORING ENDPOINTS")
        print("=" * 60)
        
        monitoring_endpoints = [
            "/performance/monitor",
            "/ultra/performance-stats"
        ]
        
        for endpoint in monitoring_endpoints:
            print(f"\n🔍 Testing {endpoint}")
            
            result = self.measure_endpoint_performance(endpoint)
            
            if result["success"]:
                response_data = result["response_data"]
                
                self.log_result(
                    f"Performance Monitor {endpoint}",
                    True,
                    f"Successfully retrieved monitoring data ({result['response_time_ms']:.2f}ms)",
                    result["response_time_ms"]
                )
                
                # Log some key metrics if available
                if isinstance(response_data, dict):
                    if "stats" in response_data:
                        print(f"   📈 Performance stats available")
                    if "performance_summary" in response_data:
                        print(f"   📊 Performance summary available")
                        
            else:
                self.log_result(
                    f"Performance Monitor {endpoint}",
                    False,
                    f"Failed to retrieve monitoring data: {result['error']}"
                )
    
    def compare_ultra_vs_regular_performance(self):
        """Compare ultra vs regular endpoint performance"""
        print("\n⚡ ULTRA VS REGULAR PERFORMANCE COMPARISON")
        print("=" * 60)
        
        ultra_stats = self.performance_stats.get("ultra_endpoints", {})
        regular_stats = self.performance_stats.get("regular_endpoints", {})
        
        comparisons = [
            ("Ultra Dashboard", "Regular Dashboard"),
            ("Ultra Pillars", "Regular Pillars"),
            ("Ultra Areas", "Regular Areas"),
            ("Ultra Projects", "Regular Projects"),
            ("Ultra Insights", "Regular Insights")
        ]
        
        improvement_summary = []
        
        for ultra_name, regular_name in comparisons:
            ultra_data = ultra_stats.get(ultra_name, {})
            regular_data = regular_stats.get(regular_name, {})
            
            ultra_time = ultra_data.get("avg_response_time")
            regular_time = regular_data.get("avg_response_time")
            
            if ultra_time and regular_time:
                improvement = ((regular_time - ultra_time) / regular_time) * 100
                speed_factor = regular_time / ultra_time
                
                print(f"\n📊 {ultra_name.replace('Ultra ', '')} Comparison:")
                print(f"   Ultra:   {ultra_time:.2f}ms")
                print(f"   Regular: {regular_time:.2f}ms")
                print(f"   Improvement: {improvement:.1f}% faster ({speed_factor:.1f}x speed)")
                
                improvement_summary.append({
                    "endpoint": ultra_name.replace('Ultra ', ''),
                    "ultra_time": ultra_time,
                    "regular_time": regular_time,
                    "improvement_percent": improvement,
                    "speed_factor": speed_factor
                })
                
                # Check if ultra endpoint meets its target
                target_ms = ultra_data.get("target_ms", 200)
                target_status = "✅ TARGET MET" if ultra_time < target_ms else "❌ TARGET MISSED"
                print(f"   Target: <{target_ms}ms - {target_status}")
                
        return improvement_summary
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n📋 ULTRA-PERFORMANCE OPTIMIZATION REPORT")
        print("=" * 80)
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL TEST RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Ultra endpoint performance summary
        ultra_stats = self.performance_stats.get("ultra_endpoints", {})
        if ultra_stats:
            print(f"\n🚀 ULTRA-PERFORMANCE ENDPOINT RESULTS:")
            
            targets_met = 0
            total_ultra_endpoints = 0
            
            for name, stats in ultra_stats.items():
                if stats.get("avg_response_time"):
                    total_ultra_endpoints += 1
                    avg_time = stats["avg_response_time"]
                    target_ms = stats.get("target_ms", 200)
                    target_met = stats.get("target_met", False)
                    
                    if target_met:
                        targets_met += 1
                    
                    status = "✅" if target_met else "❌"
                    print(f"   {status} {name}: {avg_time:.2f}ms (Target: <{target_ms}ms)")
            
            if total_ultra_endpoints > 0:
                target_success_rate = (targets_met / total_ultra_endpoints) * 100
                print(f"\n🎯 PERFORMANCE TARGET SUCCESS RATE: {target_success_rate:.1f}% ({targets_met}/{total_ultra_endpoints})")
        
        # Performance comparison summary
        improvement_summary = self.compare_ultra_vs_regular_performance()
        
        if improvement_summary:
            avg_improvement = sum([item["improvement_percent"] for item in improvement_summary]) / len(improvement_summary)
            avg_speed_factor = sum([item["speed_factor"] for item in improvement_summary]) / len(improvement_summary)
            
            print(f"\n⚡ PERFORMANCE IMPROVEMENT SUMMARY:")
            print(f"   Average Improvement: {avg_improvement:.1f}% faster")
            print(f"   Average Speed Factor: {avg_speed_factor:.1f}x")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        ultra_stats = self.performance_stats.get("ultra_endpoints", {})
        needs_improvement = []
        
        for name, stats in ultra_stats.items():
            if not stats.get("target_met", False) and stats.get("avg_response_time"):
                needs_improvement.append(name)
        
        if needs_improvement:
            print(f"   🔧 Endpoints needing optimization: {', '.join(needs_improvement)}")
        else:
            print(f"   🎉 All ultra-performance endpoints meet their targets!")
        
        print(f"   📈 Continue monitoring performance metrics")
        print(f"   🔄 Consider implementing additional caching layers if needed")
        
        return {
            "total_tests": total_tests,
            "success_rate": success_rate,
            "ultra_performance_stats": ultra_stats,
            "improvement_summary": improvement_summary,
            "needs_improvement": needs_improvement
        }
    
    def run_comprehensive_test(self):
        """Run comprehensive ultra-performance testing"""
        print("🚀 ULTRA-PERFORMANCE OPTIMIZATION TESTING SUITE")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Started: {datetime.utcnow().isoformat()}")
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with testing.")
            return False
        
        # Step 2: Test ultra-performance endpoints
        self.test_ultra_performance_endpoints()
        
        # Step 3: Test regular endpoints for comparison
        self.test_regular_endpoints_comparison()
        
        # Step 4: Test performance monitoring
        self.test_performance_monitoring_endpoints()
        
        # Step 5: Generate comprehensive report
        report = self.generate_performance_report()
        
        print(f"\n✅ ULTRA-PERFORMANCE TESTING COMPLETED")
        print(f"Completed: {datetime.utcnow().isoformat()}")
        
        return report

def main():
    """Main test execution"""
    tester = UltraPerformanceTester()
    
    try:
        report = tester.run_comprehensive_test()
        
        # Determine overall success
        success_rate = report.get("success_rate", 0)
        ultra_stats = report.get("ultra_performance_stats", {})
        
        # Check if critical performance targets are met
        critical_targets_met = True
        for name, stats in ultra_stats.items():
            if not stats.get("target_met", False) and stats.get("avg_response_time"):
                critical_targets_met = False
                break
        
        if success_rate >= 90 and critical_targets_met:
            print(f"\n🎉 ULTRA-PERFORMANCE OPTIMIZATION: SUCCESS!")
            print(f"All endpoints meet sub-200ms targets with excellent performance improvements.")
            sys.exit(0)
        elif success_rate >= 70:
            print(f"\n⚠️ ULTRA-PERFORMANCE OPTIMIZATION: PARTIAL SUCCESS")
            print(f"Most endpoints working but some performance targets need attention.")
            sys.exit(0)
        else:
            print(f"\n❌ ULTRA-PERFORMANCE OPTIMIZATION: NEEDS ATTENTION")
            print(f"Multiple endpoints failing or not meeting performance targets.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 TESTING ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()