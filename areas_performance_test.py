#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import statistics
from datetime import datetime
from typing import Dict, Any, List

# Configuration - Use the backend URL from frontend/.env
BACKEND_URL = "https://2a9362a1-0858-4070-86b9-4648da4a94c4.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class AreasPerformanceTestSuite:
    """
    Focused performance testing for Areas API endpoint optimization verification
    Testing specifically for:
    1. Response time improvements from 430ms baseline
    2. Importance field returned as integers (1-5) instead of strings
    3. Multiple API calls to measure consistency
    """
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword123"
        self.test_results = []
        self.response_times = []
        self.baseline_time = 430  # Previous baseline in ms
        
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
            
            print(f"🔐 Authenticating with {self.test_user_email}...")
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    print(f"✅ Authentication successful")
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
        
    async def test_areas_api_performance(self, num_calls: int = 5):
        """Test Areas API performance with multiple calls"""
        print(f"\n🧪 Testing Areas API Performance ({num_calls} calls)")
        print(f"🎯 Target: Improve from {self.baseline_time}ms baseline")
        
        try:
            response_times = []
            importance_field_results = []
            
            for i in range(num_calls):
                print(f"\n📊 Call {i+1}/{num_calls}:")
                
                # Measure response time
                start_time = time.time()
                
                async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                    end_time = time.time()
                    response_time_ms = (end_time - start_time) * 1000
                    response_times.append(response_time_ms)
                    
                    if response.status == 200:
                        areas_data = await response.json()
                        
                        print(f"   ⏱️  Response time: {response_time_ms:.1f}ms")
                        print(f"   📋 Areas returned: {len(areas_data)}")
                        
                        # Check importance field types
                        importance_types = []
                        importance_values = []
                        
                        for area in areas_data:
                            if 'importance' in area:
                                importance_value = area['importance']
                                importance_types.append(type(importance_value).__name__)
                                importance_values.append(importance_value)
                                
                        if importance_types:
                            # Check if all importance values are integers
                            all_integers = all(isinstance(val, int) for val in importance_values)
                            importance_field_results.append({
                                'all_integers': all_integers,
                                'types': set(importance_types),
                                'values': importance_values[:5]  # Sample first 5
                            })
                            
                            print(f"   🔢 Importance field types: {set(importance_types)}")
                            print(f"   📊 Sample importance values: {importance_values[:3]}")
                        else:
                            print(f"   ⚠️  No importance fields found in areas")
                            
                    else:
                        error_text = await response.text()
                        print(f"   ❌ API call failed: {response.status} - {error_text}")
                        return False
                        
                # Small delay between calls
                await asyncio.sleep(0.1)
                
            # Calculate performance statistics
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            median_response_time = statistics.median(response_times)
            
            # Calculate improvement from baseline
            improvement_ms = self.baseline_time - avg_response_time
            improvement_percent = (improvement_ms / self.baseline_time) * 100
            
            print(f"\n📈 PERFORMANCE RESULTS:")
            print(f"   📊 Average response time: {avg_response_time:.1f}ms")
            print(f"   ⚡ Fastest response: {min_response_time:.1f}ms")
            print(f"   🐌 Slowest response: {max_response_time:.1f}ms")
            print(f"   📊 Median response time: {median_response_time:.1f}ms")
            print(f"   📈 Baseline comparison: {self.baseline_time}ms → {avg_response_time:.1f}ms")
            
            if improvement_ms > 0:
                print(f"   🎉 IMPROVEMENT: {improvement_ms:.1f}ms faster ({improvement_percent:.1f}% improvement)")
            else:
                print(f"   ⚠️  REGRESSION: {abs(improvement_ms):.1f}ms slower ({abs(improvement_percent):.1f}% slower)")
                
            # Analyze importance field results
            print(f"\n🔢 IMPORTANCE FIELD ANALYSIS:")
            if importance_field_results:
                all_calls_integer = all(result['all_integers'] for result in importance_field_results)
                
                if all_calls_integer:
                    print(f"   ✅ All importance fields are integers (1-5) as expected")
                    
                    # Check value ranges
                    all_values = []
                    for result in importance_field_results:
                        all_values.extend(result['values'])
                    
                    valid_range = all(1 <= val <= 5 for val in all_values if isinstance(val, int))
                    if valid_range:
                        print(f"   ✅ All importance values are in valid range (1-5)")
                        print(f"   📊 Sample values: {list(set(all_values))}")
                    else:
                        print(f"   ❌ Some importance values are outside valid range (1-5)")
                        print(f"   📊 Found values: {list(set(all_values))}")
                else:
                    print(f"   ❌ Some importance fields are not integers")
                    for i, result in enumerate(importance_field_results):
                        if not result['all_integers']:
                            print(f"      Call {i+1}: Types found: {result['types']}")
            else:
                print(f"   ⚠️  No importance fields found in any API calls")
                
            # Determine test success
            performance_improved = improvement_ms > 0
            importance_correct = importance_field_results and all(result['all_integers'] for result in importance_field_results)
            
            if performance_improved and importance_correct:
                status = "PASSED"
                details = f"Performance improved by {improvement_ms:.1f}ms ({improvement_percent:.1f}%), importance fields are integers"
            elif performance_improved:
                status = "PARTIAL"
                details = f"Performance improved by {improvement_ms:.1f}ms, but importance field issues detected"
            elif importance_correct:
                status = "PARTIAL" 
                details = f"Importance fields correct, but performance regression of {abs(improvement_ms):.1f}ms"
            else:
                status = "FAILED"
                details = f"Performance regression of {abs(improvement_ms):.1f}ms and importance field issues"
                
            self.test_results.append({
                "test": "Areas API Performance",
                "status": status,
                "details": details,
                "avg_response_time": avg_response_time,
                "baseline_time": self.baseline_time,
                "improvement_ms": improvement_ms,
                "improvement_percent": improvement_percent,
                "importance_fields_correct": importance_correct
            })
            
            return status == "PASSED"
            
        except Exception as e:
            print(f"❌ Areas API performance test failed: {e}")
            self.test_results.append({
                "test": "Areas API Performance",
                "status": "FAILED",
                "reason": str(e)
            })
            return False
            
    async def test_areas_api_consistency(self, num_calls: int = 10):
        """Test Areas API consistency over multiple calls"""
        print(f"\n🧪 Testing Areas API Consistency ({num_calls} calls)")
        
        try:
            response_times = []
            data_consistency = []
            
            for i in range(num_calls):
                start_time = time.time()
                
                async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                    end_time = time.time()
                    response_time_ms = (end_time - start_time) * 1000
                    response_times.append(response_time_ms)
                    
                    if response.status == 200:
                        areas_data = await response.json()
                        data_consistency.append({
                            'count': len(areas_data),
                            'has_importance': any('importance' in area for area in areas_data),
                            'response_time': response_time_ms
                        })
                    else:
                        print(f"   ❌ Call {i+1} failed: {response.status}")
                        return False
                        
                if i % 3 == 0:  # Progress indicator
                    print(f"   📊 Completed {i+1}/{num_calls} calls...")
                    
            # Analyze consistency
            avg_time = statistics.mean(response_times)
            std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            coefficient_of_variation = (std_dev / avg_time) * 100 if avg_time > 0 else 0
            
            # Check data consistency
            area_counts = [data['count'] for data in data_consistency]
            consistent_count = len(set(area_counts)) == 1
            
            print(f"\n📊 CONSISTENCY RESULTS:")
            print(f"   ⏱️  Average response time: {avg_time:.1f}ms")
            print(f"   📊 Standard deviation: {std_dev:.1f}ms")
            print(f"   📈 Coefficient of variation: {coefficient_of_variation:.1f}%")
            print(f"   📋 Area counts consistent: {consistent_count}")
            
            if coefficient_of_variation < 20:
                print(f"   ✅ Response times are consistent (CV < 20%)")
            else:
                print(f"   ⚠️  Response times show high variation (CV > 20%)")
                
            consistency_good = coefficient_of_variation < 25 and consistent_count
            
            self.test_results.append({
                "test": "Areas API Consistency",
                "status": "PASSED" if consistency_good else "PARTIAL",
                "details": f"CV: {coefficient_of_variation:.1f}%, Data consistent: {consistent_count}",
                "coefficient_of_variation": coefficient_of_variation,
                "data_consistent": consistent_count
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Areas API consistency test failed: {e}")
            self.test_results.append({
                "test": "Areas API Consistency",
                "status": "FAILED",
                "reason": str(e)
            })
            return False
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 AREAS API PERFORMANCE OPTIMIZATION VERIFICATION")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        partial = len([t for t in self.test_results if t["status"] == "PARTIAL"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Partial: {partial}")
        print(f"❌ Failed: {failed}")
        
        success_rate = ((passed + partial * 0.5) / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icons = {"PASSED": "✅", "PARTIAL": "⚠️", "FAILED": "❌"}
            icon = status_icons.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
            # Special formatting for performance results
            if result['test'] == "Areas API Performance" and "avg_response_time" in result:
                print(f"    ⏱️  Average: {result['avg_response_time']:.1f}ms")
                print(f"    📈 Baseline: {result['baseline_time']}ms")
                if result['improvement_ms'] > 0:
                    print(f"    🎉 Improvement: {result['improvement_ms']:.1f}ms ({result['improvement_percent']:.1f}%)")
                else:
                    print(f"    ⚠️  Regression: {abs(result['improvement_ms']):.1f}ms ({abs(result['improvement_percent']):.1f}%)")
                    
        print("\n" + "="*80)
        
        # Overall assessment
        performance_test = next((t for t in self.test_results if t['test'] == "Areas API Performance"), None)
        
        if performance_test:
            if performance_test['status'] == "PASSED":
                print("🎉 AREAS API OPTIMIZATION SUCCESSFUL!")
                print("✅ Performance improved from baseline")
                print("✅ Importance fields returned as integers (1-5)")
                print("✅ API optimization goals achieved")
            elif performance_test['status'] == "PARTIAL":
                print("⚠️ AREAS API OPTIMIZATION PARTIALLY SUCCESSFUL")
                print("⚠️ Some optimization goals achieved, others need attention")
            else:
                print("❌ AREAS API OPTIMIZATION NEEDS ATTENTION")
                print("❌ Performance and/or data format issues detected")
        else:
            print("❓ AREAS API OPTIMIZATION STATUS UNCLEAR")
            
        print("="*80)
        
    async def run_areas_performance_test(self):
        """Run comprehensive Areas API performance test"""
        print("🚀 Starting Areas API Performance Optimization Verification...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"👤 Test User: {self.test_user_email}")
        print(f"📊 Baseline: {self.baseline_time}ms")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run performance tests
            print("\n" + "="*60)
            await self.test_areas_api_performance(num_calls=5)
            
            print("\n" + "="*60)
            await self.test_areas_api_consistency(num_calls=10)
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = AreasPerformanceTestSuite()
    await test_suite.run_areas_performance_test()

if __name__ == "__main__":
    asyncio.run(main())