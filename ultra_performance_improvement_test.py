#!/usr/bin/env python3
"""
Ultra-Performance Improvement Testing
Tests the improved ultra-performance optimization endpoints after fixes
Focuses on verifying the specific improvements mentioned in the review request
"""

import requests
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://hierarchy-master.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password"

# Previous test results for comparison
PREVIOUS_RESULTS = {
    "Ultra Insights": 165,  # met target
    "Ultra Pillars": 274,   # missed target
    "Ultra Areas": 275,     # missed target  
    "Ultra Projects": 317,  # missed target
    "Ultra Dashboard": None # FAILED
}

class UltraPerformanceImprovementTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.performance_comparison = {}
        
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
    
    def measure_endpoint_performance(self, endpoint: str, method: str = "GET", data: dict = None, warmup: bool = True) -> Dict[str, Any]:
        """Measure endpoint performance with detailed metrics"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            # Warm-up request (not counted) - helps with caching
            if warmup:
                if method.upper() == "GET":
                    self.session.get(url)
                elif method.upper() == "POST":
                    self.session.post(url, json=data)
                time.sleep(0.1)  # Brief pause
            
            # Actual performance measurement - multiple runs for accuracy
            measurements = []
            for i in range(3):
                start_time = time.time()
                
                if method.upper() == "GET":
                    response = self.session.get(url)
                elif method.upper() == "POST":
                    response = self.session.post(url, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                measurements.append(response_time)
            
            # Calculate statistics
            avg_time = sum(measurements) / len(measurements)
            min_time = min(measurements)
            max_time = max(measurements)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "avg_response_time_ms": avg_time,
                "min_response_time_ms": min_time,
                "max_response_time_ms": max_time,
                "measurements": measurements,
                "response_data": response.json() if response.status_code == 200 else None,
                "error": response.text if response.status_code != 200 else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "avg_response_time_ms": None,
                "error": str(e)
            }
    
    def test_fixed_ultra_dashboard(self):
        """Test the fixed Ultra Dashboard endpoint that was previously failing"""
        print("\n🎯 TESTING FIXED ULTRA DASHBOARD (Previously FAILED)")
        print("=" * 60)
        
        result = self.measure_endpoint_performance("/ultra/dashboard")
        
        if result["success"]:
            avg_time = result["avg_response_time_ms"]
            target_met = avg_time < 150
            
            # Check if dashboard fix worked
            dashboard_data = result["response_data"]
            has_user_data = dashboard_data and "user" in dashboard_data
            has_stats = dashboard_data and "stats" in dashboard_data
            
            status = "🎉 FIXED & TARGET MET" if target_met else "✅ FIXED BUT SLOW"
            improvement = "PREVIOUSLY FAILED → NOW WORKING"
            
            self.log_result(
                "Ultra Dashboard Fix Verification",
                True,
                f"{status} - {avg_time:.2f}ms (Target: <150ms) - {improvement}",
                avg_time
            )
            
            # Log data quality
            if has_user_data and has_stats:
                print(f"   📊 Dashboard data quality: EXCELLENT (user + stats)")
            elif has_user_data:
                print(f"   📊 Dashboard data quality: GOOD (user data present)")
            else:
                print(f"   📊 Dashboard data quality: BASIC (response received)")
            
            self.performance_comparison["Ultra Dashboard"] = {
                "previous": "FAILED",
                "current": avg_time,
                "target": 150,
                "target_met": target_met,
                "improvement": "Fixed from complete failure"
            }
            
        else:
            self.log_result(
                "Ultra Dashboard Fix Verification",
                False,
                f"Dashboard still failing: {result['error']}"
            )
            
            self.performance_comparison["Ultra Dashboard"] = {
                "previous": "FAILED",
                "current": "STILL FAILED",
                "target": 150,
                "target_met": False,
                "improvement": "No improvement - still failing"
            }
    
    def test_improved_ultra_endpoints(self):
        """Test all improved ultra-performance endpoints"""
        print("\n🚀 TESTING IMPROVED ULTRA-PERFORMANCE ENDPOINTS")
        print("=" * 60)
        
        # Define endpoints with their targets and previous results
        ultra_endpoints = [
            {
                "endpoint": "/ultra/pillars",
                "name": "Ultra Pillars",
                "target_ms": 150,
                "previous_ms": 274
            },
            {
                "endpoint": "/ultra/areas",
                "name": "Ultra Areas", 
                "target_ms": 120,
                "previous_ms": 275
            },
            {
                "endpoint": "/ultra/projects",
                "name": "Ultra Projects",
                "target_ms": 100,
                "previous_ms": 317
            },
            {
                "endpoint": "/ultra/insights",
                "name": "Ultra Insights",
                "target_ms": 200,
                "previous_ms": 165  # This was already meeting target
            }
        ]
        
        for endpoint_config in ultra_endpoints:
            endpoint = endpoint_config["endpoint"]
            name = endpoint_config["name"]
            target_ms = endpoint_config["target_ms"]
            previous_ms = endpoint_config["previous_ms"]
            
            print(f"\n📊 Testing {name}")
            print(f"   Previous: {previous_ms}ms | Target: <{target_ms}ms")
            
            result = self.measure_endpoint_performance(endpoint)
            
            if result["success"]:
                avg_time = result["avg_response_time_ms"]
                min_time = result["min_response_time_ms"]
                max_time = result["max_response_time_ms"]
                
                # Calculate improvement
                improvement_ms = previous_ms - avg_time
                improvement_percent = (improvement_ms / previous_ms) * 100
                
                # Check target achievement
                target_met = avg_time < target_ms
                previously_met_target = previous_ms < target_ms
                
                # Determine status
                if target_met and not previously_met_target:
                    status = "🎯 NOW MEETS TARGET"
                elif target_met and previously_met_target:
                    status = "✅ STILL MEETS TARGET"
                elif not target_met and improvement_percent > 20:
                    status = "📈 SIGNIFICANT IMPROVEMENT"
                elif not target_met and improvement_percent > 0:
                    status = "📊 SOME IMPROVEMENT"
                else:
                    status = "⚠️ NO IMPROVEMENT"
                
                self.log_result(
                    f"{name} Performance",
                    target_met,
                    f"{status} - {avg_time:.2f}ms (was {previous_ms}ms) - {improvement_percent:+.1f}%",
                    avg_time
                )
                
                # Detailed performance info
                print(f"   📈 Improvement: {improvement_ms:+.2f}ms ({improvement_percent:+.1f}%)")
                print(f"   📊 Range: {min_time:.2f}ms - {max_time:.2f}ms")
                
                self.performance_comparison[name] = {
                    "previous": previous_ms,
                    "current": avg_time,
                    "target": target_ms,
                    "target_met": target_met,
                    "improvement_ms": improvement_ms,
                    "improvement_percent": improvement_percent
                }
                
            else:
                self.log_result(
                    f"{name} Performance",
                    False,
                    f"Endpoint failed: {result['error']}"
                )
                
                self.performance_comparison[name] = {
                    "previous": previous_ms,
                    "current": "FAILED",
                    "target": target_ms,
                    "target_met": False,
                    "improvement": "Endpoint failure"
                }
    
    def test_regular_vs_ultra_comparison(self):
        """Compare regular vs ultra endpoint performance"""
        print("\n⚡ REGULAR VS ULTRA PERFORMANCE COMPARISON")
        print("=" * 60)
        
        comparisons = [
            ("/pillars", "/ultra/pillars", "Pillars"),
            ("/areas", "/ultra/areas", "Areas"),
            ("/projects", "/ultra/projects", "Projects"),
            ("/insights", "/ultra/insights", "Insights"),
            ("/dashboard", "/ultra/dashboard", "Dashboard")
        ]
        
        for regular_endpoint, ultra_endpoint, name in comparisons:
            print(f"\n📊 {name} Comparison")
            
            # Test regular endpoint
            regular_result = self.measure_endpoint_performance(regular_endpoint)
            
            # Test ultra endpoint  
            ultra_result = self.measure_endpoint_performance(ultra_endpoint)
            
            if regular_result["success"] and ultra_result["success"]:
                regular_time = regular_result["avg_response_time_ms"]
                ultra_time = ultra_result["avg_response_time_ms"]
                
                improvement = ((regular_time - ultra_time) / regular_time) * 100
                speed_factor = regular_time / ultra_time
                
                print(f"   Regular: {regular_time:.2f}ms")
                print(f"   Ultra:   {ultra_time:.2f}ms")
                print(f"   Improvement: {improvement:.1f}% faster ({speed_factor:.1f}x speed)")
                
            elif ultra_result["success"]:
                print(f"   Regular: FAILED")
                print(f"   Ultra:   {ultra_result['avg_response_time_ms']:.2f}ms")
                print(f"   Status: Ultra working, Regular failed")
                
            elif regular_result["success"]:
                print(f"   Regular: {regular_result['avg_response_time_ms']:.2f}ms")
                print(f"   Ultra:   FAILED")
                print(f"   Status: Regular working, Ultra failed")
                
            else:
                print(f"   Both endpoints failed")
    
    def test_cache_and_optimization_effectiveness(self):
        """Test cache service and optimization effectiveness"""
        print("\n🔄 TESTING CACHE & OPTIMIZATION EFFECTIVENESS")
        print("=" * 60)
        
        # Test performance stats endpoint
        print("\n📊 Testing Performance Stats")
        stats_result = self.measure_endpoint_performance("/ultra/performance-stats")
        
        if stats_result["success"]:
            stats_data = stats_result["response_data"]
            
            self.log_result(
                "Performance Stats Endpoint",
                True,
                f"Stats retrieved successfully ({stats_result['avg_response_time_ms']:.2f}ms)",
                stats_result["avg_response_time_ms"]
            )
            
            # Log cache statistics if available
            if stats_data and "cache_stats" in stats_data:
                cache_stats = stats_data["cache_stats"]
                print(f"   📈 Cache hit rate: {cache_stats.get('hit_rate', 'N/A')}")
                print(f"   📊 Cache entries: {cache_stats.get('total_entries', 'N/A')}")
                
        else:
            self.log_result(
                "Performance Stats Endpoint",
                False,
                f"Stats endpoint failed: {stats_result['error']}"
            )
        
        # Test cache effectiveness by making repeated calls
        print("\n🔄 Testing Cache Effectiveness")
        
        # First call (cache miss)
        first_call = self.measure_endpoint_performance("/ultra/pillars", warmup=False)
        
        # Second call (should be cache hit)
        second_call = self.measure_endpoint_performance("/ultra/pillars", warmup=False)
        
        if first_call["success"] and second_call["success"]:
            first_time = first_call["avg_response_time_ms"]
            second_time = second_call["avg_response_time_ms"]
            
            cache_improvement = ((first_time - second_time) / first_time) * 100
            
            if cache_improvement > 10:
                print(f"   ✅ Cache working: {cache_improvement:.1f}% faster on second call")
            else:
                print(f"   📊 Cache effect: {cache_improvement:.1f}% difference")
                
            print(f"   First call:  {first_time:.2f}ms")
            print(f"   Second call: {second_time:.2f}ms")
    
    def generate_improvement_report(self):
        """Generate comprehensive improvement report"""
        print("\n📋 ULTRA-PERFORMANCE IMPROVEMENT REPORT")
        print("=" * 80)
        
        # Overall test results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL TEST RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Performance improvement summary
        print(f"\n🚀 PERFORMANCE IMPROVEMENT SUMMARY:")
        
        targets_met = 0
        total_endpoints = 0
        significant_improvements = 0
        
        for name, comparison in self.performance_comparison.items():
            if isinstance(comparison.get("current"), (int, float)):
                total_endpoints += 1
                current = comparison["current"]
                target = comparison["target"]
                target_met = comparison.get("target_met", False)
                
                if target_met:
                    targets_met += 1
                
                # Check for significant improvement
                if "improvement_percent" in comparison and comparison["improvement_percent"] > 20:
                    significant_improvements += 1
                
                status = "✅" if target_met else "❌"
                
                if comparison["previous"] == "FAILED":
                    improvement_text = "FIXED from failure"
                elif "improvement_percent" in comparison:
                    improvement_text = f"{comparison['improvement_percent']:+.1f}%"
                else:
                    improvement_text = "Fixed"
                
                print(f"   {status} {name}: {current:.2f}ms (Target: <{target}ms) - {improvement_text}")
        
        # Success metrics
        if total_endpoints > 0:
            target_success_rate = (targets_met / total_endpoints) * 100
            print(f"\n🎯 PERFORMANCE TARGET SUCCESS RATE: {target_success_rate:.1f}% ({targets_met}/{total_endpoints})")
        
        print(f"📈 SIGNIFICANT IMPROVEMENTS: {significant_improvements} endpoints")
        
        # Key achievements
        print(f"\n🏆 KEY ACHIEVEMENTS:")
        
        dashboard_fixed = self.performance_comparison.get("Ultra Dashboard", {}).get("current") != "STILL FAILED"
        if dashboard_fixed:
            print(f"   ✅ Ultra Dashboard FIXED - was completely failing, now working")
        
        improved_endpoints = [name for name, comp in self.performance_comparison.items() 
                            if comp.get("improvement_percent", 0) > 0]
        if improved_endpoints:
            print(f"   📈 {len(improved_endpoints)} endpoints showed performance improvements")
        
        meeting_targets = [name for name, comp in self.performance_comparison.items() 
                         if comp.get("target_met", False)]
        if meeting_targets:
            print(f"   🎯 {len(meeting_targets)} endpoints now meet performance targets")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        needs_work = [name for name, comp in self.performance_comparison.items() 
                     if not comp.get("target_met", False) and isinstance(comp.get("current"), (int, float))]
        
        if needs_work:
            print(f"   🔧 Continue optimizing: {', '.join(needs_work)}")
        else:
            print(f"   🎉 All endpoints meet performance targets!")
        
        if significant_improvements >= 2:
            print(f"   ✅ Optimization strategy is working - continue current approach")
        else:
            print(f"   🔄 Consider additional optimization techniques")
        
        return {
            "total_tests": total_tests,
            "success_rate": success_rate,
            "targets_met": targets_met,
            "total_endpoints": total_endpoints,
            "significant_improvements": significant_improvements,
            "dashboard_fixed": dashboard_fixed,
            "performance_comparison": self.performance_comparison
        }
    
    def run_comprehensive_improvement_test(self):
        """Run comprehensive ultra-performance improvement testing"""
        print("🎯 ULTRA-PERFORMANCE IMPROVEMENT TESTING SUITE")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Started: {datetime.utcnow().isoformat()}")
        print(f"\nFOCUS: Testing improvements after optimization fixes")
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with testing.")
            return False
        
        # Step 2: Test the fixed Ultra Dashboard (was previously failing)
        self.test_fixed_ultra_dashboard()
        
        # Step 3: Test all improved ultra-performance endpoints
        self.test_improved_ultra_endpoints()
        
        # Step 4: Compare regular vs ultra performance
        self.test_regular_vs_ultra_comparison()
        
        # Step 5: Test cache and optimization effectiveness
        self.test_cache_and_optimization_effectiveness()
        
        # Step 6: Generate comprehensive improvement report
        report = self.generate_improvement_report()
        
        print(f"\n✅ ULTRA-PERFORMANCE IMPROVEMENT TESTING COMPLETED")
        print(f"Completed: {datetime.utcnow().isoformat()}")
        
        return report

def main():
    """Main test execution"""
    tester = UltraPerformanceImprovementTester()
    
    try:
        report = tester.run_comprehensive_improvement_test()
        
        # Determine overall success based on improvements
        success_rate = report.get("success_rate", 0)
        targets_met = report.get("targets_met", 0)
        total_endpoints = report.get("total_endpoints", 0)
        dashboard_fixed = report.get("dashboard_fixed", False)
        significant_improvements = report.get("significant_improvements", 0)
        
        # Success criteria
        dashboard_success = dashboard_fixed  # Critical: Dashboard must be fixed
        target_success = (targets_met / total_endpoints) >= 0.6 if total_endpoints > 0 else False  # 60% targets met
        improvement_success = significant_improvements >= 2  # At least 2 significant improvements
        
        if dashboard_success and target_success and improvement_success:
            print(f"\n🎉 ULTRA-PERFORMANCE IMPROVEMENTS: EXCELLENT SUCCESS!")
            print(f"Dashboard fixed, {targets_met}/{total_endpoints} targets met, {significant_improvements} significant improvements")
            sys.exit(0)
        elif dashboard_success and (target_success or improvement_success):
            print(f"\n✅ ULTRA-PERFORMANCE IMPROVEMENTS: GOOD SUCCESS!")
            print(f"Dashboard fixed with notable performance improvements")
            sys.exit(0)
        elif dashboard_success:
            print(f"\n📈 ULTRA-PERFORMANCE IMPROVEMENTS: PARTIAL SUCCESS")
            print(f"Dashboard fixed but more optimization needed")
            sys.exit(0)
        else:
            print(f"\n❌ ULTRA-PERFORMANCE IMPROVEMENTS: NEEDS MORE WORK")
            print(f"Critical issues remain - dashboard or performance targets not met")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 TESTING ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()