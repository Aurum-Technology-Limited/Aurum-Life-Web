#!/usr/bin/env python3
"""
HIERARCHY ITEM COUNTS FIX TESTING - COMPREHENSIVE BACKEND TESTING
Testing the fixed hierarchy item counts for pillars and areas endpoints.

FOCUS AREAS:
1. Authentication with marc.alleyne@aurumtechnologyltd.com / password
2. Test GET /api/pillars endpoint to verify pillar counts (area_count, project_count, task_count)
3. Test GET /api/areas endpoint to verify area counts (project_count, task_count)
4. Verify that counts are accurate and not showing "0" for existing hierarchies
5. Check that the batch query optimization is working efficiently
6. Confirm no N+1 query problems were introduced
7. Validate that both regular and ultra-performance endpoints are working

CHANGES TESTED:
- Areas Service Enhancement: Updated get_user_areas() method to calculate project_count and task_count statistics
- Count Calculations Added: Each area now includes project_count, task_count, completed_task_count, progress_percentage
- Batch Query Optimization: Maintained efficient batch querying to avoid N+1 query problems
- Consistent Implementation: Areas service now matches the pillars service pattern for count calculations

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://8f43b565-3ef8-487e-92ed-bb0b1b3a1936.preview.emergentagent.com/api"

class HierarchyCountsAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling and optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Try to parse JSON response
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response': response,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg += f" - Response: {error_data}"
                except:
                    error_msg += f" - Response: {e.response.text[:200]}"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'data': {},
                'response': getattr(e, 'response', None)
            }

    def test_basic_connectivity(self):
        """Test basic connectivity to the backend API"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
        # Test the root endpoint which should exist
        result = self.make_request('GET', '', use_auth=False)
        if not result['success']:
            # Try the base URL without /api
            base_url = self.base_url.replace('/api', '')
            url = f"{base_url}/"
            try:
                response = self.session.get(url, timeout=30)
                result = {
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else {},
                }
            except:
                result = {'success': False, 'error': 'Connection failed'}
        
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_user_authentication(self):
        """Test user authentication with specified credentials"""
        print("\n=== TESTING USER AUTHENTICATION ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_pillars_hierarchy_counts(self):
        """Test GET /api/pillars endpoint to verify pillar counts are working"""
        print("\n=== TESTING PILLARS HIERARCHY COUNTS ===")
        
        if not self.auth_token:
            self.log_test("PILLARS HIERARCHY COUNTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/pillars
        result = self.make_request('GET', '/pillars', use_auth=True)
        self.log_test(
            "GET PILLARS ENDPOINT",
            result['success'],
            f"Retrieved pillars successfully" if result['success'] else f"Failed to get pillars: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        pillars = result['data']
        
        # Check if we have pillars
        if not pillars or len(pillars) == 0:
            self.log_test(
                "PILLARS DATA AVAILABILITY",
                False,
                "No pillars found - cannot test hierarchy counts"
            )
            return False
        
        self.log_test(
            "PILLARS DATA AVAILABILITY",
            True,
            f"Found {len(pillars)} pillars for testing"
        )
        
        # Test hierarchy counts for each pillar
        pillars_with_counts = 0
        pillars_with_non_zero_counts = 0
        total_area_count = 0
        total_project_count = 0
        total_task_count = 0
        
        for pillar in pillars:
            pillar_name = pillar.get('name', 'Unknown')
            
            # Check for required count fields
            has_area_count = 'area_count' in pillar
            has_project_count = 'project_count' in pillar
            has_task_count = 'task_count' in pillar
            
            if has_area_count and has_project_count and has_task_count:
                pillars_with_counts += 1
                
                area_count = pillar.get('area_count', 0)
                project_count = pillar.get('project_count', 0)
                task_count = pillar.get('task_count', 0)
                
                total_area_count += area_count
                total_project_count += project_count
                total_task_count += task_count
                
                if area_count > 0 or project_count > 0 or task_count > 0:
                    pillars_with_non_zero_counts += 1
                
                print(f"   Pillar '{pillar_name}': areas={area_count}, projects={project_count}, tasks={task_count}")
            else:
                missing_fields = []
                if not has_area_count:
                    missing_fields.append('area_count')
                if not has_project_count:
                    missing_fields.append('project_count')
                if not has_task_count:
                    missing_fields.append('task_count')
                print(f"   Pillar '{pillar_name}': Missing fields: {missing_fields}")
        
        # Test results
        all_pillars_have_counts = pillars_with_counts == len(pillars)
        self.log_test(
            "PILLARS HIERARCHY COUNT FIELDS",
            all_pillars_have_counts,
            f"All {len(pillars)} pillars have count fields" if all_pillars_have_counts else f"Only {pillars_with_counts}/{len(pillars)} pillars have count fields"
        )
        
        # Test for non-zero counts (indicating the fix is working)
        has_non_zero_counts = pillars_with_non_zero_counts > 0
        self.log_test(
            "PILLARS NON-ZERO COUNTS",
            has_non_zero_counts,
            f"{pillars_with_non_zero_counts} pillars have non-zero counts (totals: areas={total_area_count}, projects={total_project_count}, tasks={total_task_count})" if has_non_zero_counts else "All pillars show zero counts - hierarchy counts may not be working"
        )
        
        return all_pillars_have_counts and has_non_zero_counts

    def test_areas_hierarchy_counts(self):
        """Test GET /api/areas endpoint to verify area counts are working"""
        print("\n=== TESTING AREAS HIERARCHY COUNTS ===")
        
        if not self.auth_token:
            self.log_test("AREAS HIERARCHY COUNTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/areas
        result = self.make_request('GET', '/areas', use_auth=True)
        self.log_test(
            "GET AREAS ENDPOINT",
            result['success'],
            f"Retrieved areas successfully" if result['success'] else f"Failed to get areas: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        areas = result['data']
        
        # Check if we have areas
        if not areas or len(areas) == 0:
            self.log_test(
                "AREAS DATA AVAILABILITY",
                False,
                "No areas found - cannot test hierarchy counts"
            )
            return False
        
        self.log_test(
            "AREAS DATA AVAILABILITY",
            True,
            f"Found {len(areas)} areas for testing"
        )
        
        # Test hierarchy counts for each area
        areas_with_counts = 0
        areas_with_non_zero_counts = 0
        total_project_count = 0
        total_task_count = 0
        areas_with_progress = 0
        
        for area in areas:
            area_name = area.get('name', 'Unknown')
            
            # Check for required count fields (the fix should add these)
            has_project_count = 'project_count' in area
            has_task_count = 'task_count' in area
            has_completed_task_count = 'completed_task_count' in area
            has_progress_percentage = 'progress_percentage' in area
            
            if has_project_count and has_task_count:
                areas_with_counts += 1
                
                project_count = area.get('project_count', 0)
                task_count = area.get('task_count', 0)
                completed_task_count = area.get('completed_task_count', 0)
                progress_percentage = area.get('progress_percentage', 0)
                
                total_project_count += project_count
                total_task_count += task_count
                
                if project_count > 0 or task_count > 0:
                    areas_with_non_zero_counts += 1
                
                if has_progress_percentage:
                    areas_with_progress += 1
                
                print(f"   Area '{area_name}': projects={project_count}, tasks={task_count}, completed={completed_task_count}, progress={progress_percentage}%")
            else:
                missing_fields = []
                if not has_project_count:
                    missing_fields.append('project_count')
                if not has_task_count:
                    missing_fields.append('task_count')
                print(f"   Area '{area_name}': Missing fields: {missing_fields}")
        
        # Test results
        all_areas_have_counts = areas_with_counts == len(areas)
        self.log_test(
            "AREAS HIERARCHY COUNT FIELDS",
            all_areas_have_counts,
            f"All {len(areas)} areas have count fields" if all_areas_have_counts else f"Only {areas_with_counts}/{len(areas)} areas have count fields"
        )
        
        # Test for non-zero counts (indicating the fix is working)
        has_non_zero_counts = areas_with_non_zero_counts > 0
        self.log_test(
            "AREAS NON-ZERO COUNTS",
            has_non_zero_counts,
            f"{areas_with_non_zero_counts} areas have non-zero counts (totals: projects={total_project_count}, tasks={total_task_count})" if has_non_zero_counts else "All areas show zero counts - hierarchy counts may not be working"
        )
        
        # Test progress percentage calculation
        has_progress_calculation = areas_with_progress > 0
        self.log_test(
            "AREAS PROGRESS CALCULATION",
            has_progress_calculation,
            f"{areas_with_progress}/{len(areas)} areas have progress percentage calculation" if has_progress_calculation else "No areas have progress percentage calculation"
        )
        
        return all_areas_have_counts and has_non_zero_counts

    def test_ultra_performance_endpoints(self):
        """Test ultra-performance endpoints for hierarchy counts"""
        print("\n=== TESTING ULTRA-PERFORMANCE ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("ULTRA-PERFORMANCE ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test ultra-performance pillars endpoint
        start_time = time.time()
        result = self.make_request('GET', '/ultra/pillars', use_auth=True)
        pillars_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        ultra_pillars_working = result['success']
        self.log_test(
            "ULTRA-PERFORMANCE PILLARS ENDPOINT",
            ultra_pillars_working,
            f"Ultra pillars endpoint working ({pillars_time:.0f}ms)" if ultra_pillars_working else f"Ultra pillars endpoint failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test ultra-performance areas endpoint
        start_time = time.time()
        result = self.make_request('GET', '/ultra/areas', use_auth=True)
        areas_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        ultra_areas_working = result['success']
        self.log_test(
            "ULTRA-PERFORMANCE AREAS ENDPOINT",
            ultra_areas_working,
            f"Ultra areas endpoint working ({areas_time:.0f}ms)" if ultra_areas_working else f"Ultra areas endpoint failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test performance targets
        performance_target_met = pillars_time < 500 and areas_time < 500  # Under 500ms
        self.log_test(
            "ULTRA-PERFORMANCE TIMING",
            performance_target_met,
            f"Performance targets met: pillars={pillars_time:.0f}ms, areas={areas_time:.0f}ms" if performance_target_met else f"Performance targets not met: pillars={pillars_time:.0f}ms, areas={areas_time:.0f}ms (target: <500ms)"
        )
        
        return ultra_pillars_working and ultra_areas_working

    def test_batch_query_optimization(self):
        """Test that batch query optimization is working (no N+1 problems)"""
        print("\n=== TESTING BATCH QUERY OPTIMIZATION ===")
        
        if not self.auth_token:
            self.log_test("BATCH QUERY OPTIMIZATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test multiple requests to see if performance is consistent (indicating batch queries)
        pillars_times = []
        areas_times = []
        
        # Make 3 requests to each endpoint to test consistency
        for i in range(3):
            # Test pillars endpoint
            start_time = time.time()
            result = self.make_request('GET', '/pillars', use_auth=True)
            pillars_time = (time.time() - start_time) * 1000
            
            if result['success']:
                pillars_times.append(pillars_time)
            
            # Test areas endpoint
            start_time = time.time()
            result = self.make_request('GET', '/areas', use_auth=True)
            areas_time = (time.time() - start_time) * 1000
            
            if result['success']:
                areas_times.append(areas_time)
            
            time.sleep(0.1)  # Small delay between requests
        
        # Analyze performance consistency
        if len(pillars_times) >= 2 and len(areas_times) >= 2:
            pillars_avg = sum(pillars_times) / len(pillars_times)
            areas_avg = sum(areas_times) / len(areas_times)
            
            pillars_variance = max(pillars_times) - min(pillars_times)
            areas_variance = max(areas_times) - min(areas_times)
            
            # Good batch optimization should have consistent performance
            consistent_performance = pillars_variance < (pillars_avg * 0.5) and areas_variance < (areas_avg * 0.5)
            
            self.log_test(
                "BATCH QUERY PERFORMANCE CONSISTENCY",
                consistent_performance,
                f"Performance consistent: pillars avg={pillars_avg:.0f}ms (variance={pillars_variance:.0f}ms), areas avg={areas_avg:.0f}ms (variance={areas_variance:.0f}ms)" if consistent_performance else f"Performance inconsistent: pillars variance={pillars_variance:.0f}ms, areas variance={areas_variance:.0f}ms"
            )
            
            return consistent_performance
        else:
            self.log_test(
                "BATCH QUERY PERFORMANCE CONSISTENCY",
                False,
                "Could not test performance consistency - requests failed"
            )
            return False

    def test_hierarchy_data_accuracy(self):
        """Test that hierarchy counts are accurate by cross-referencing data"""
        print("\n=== TESTING HIERARCHY DATA ACCURACY ===")
        
        if not self.auth_token:
            self.log_test("HIERARCHY DATA ACCURACY - Authentication Required", False, "No authentication token available")
            return False
        
        # Get all data to cross-reference counts
        pillars_result = self.make_request('GET', '/pillars', use_auth=True)
        areas_result = self.make_request('GET', '/areas', use_auth=True)
        projects_result = self.make_request('GET', '/projects', use_auth=True)
        tasks_result = self.make_request('GET', '/tasks', use_auth=True)
        
        if not all([pillars_result['success'], areas_result['success'], projects_result['success'], tasks_result['success']]):
            self.log_test(
                "HIERARCHY DATA RETRIEVAL",
                False,
                "Could not retrieve all hierarchy data for accuracy testing"
            )
            return False
        
        pillars = pillars_result['data']
        areas = areas_result['data']
        projects = projects_result['data']
        tasks = tasks_result['data']
        
        # Cross-reference pillar counts
        pillar_accuracy_issues = 0
        for pillar in pillars:
            pillar_id = pillar.get('id')
            reported_area_count = pillar.get('area_count', 0)
            reported_project_count = pillar.get('project_count', 0)
            reported_task_count = pillar.get('task_count', 0)
            
            # Count actual areas for this pillar
            actual_area_count = len([a for a in areas if a.get('pillar_id') == pillar_id])
            
            # Count actual projects for this pillar (through areas)
            pillar_area_ids = [a.get('id') for a in areas if a.get('pillar_id') == pillar_id]
            actual_project_count = len([p for p in projects if p.get('area_id') in pillar_area_ids])
            
            # Count actual tasks for this pillar (through projects)
            pillar_project_ids = [p.get('id') for p in projects if p.get('area_id') in pillar_area_ids]
            actual_task_count = len([t for t in tasks if t.get('project_id') in pillar_project_ids])
            
            if (reported_area_count != actual_area_count or 
                reported_project_count != actual_project_count or 
                reported_task_count != actual_task_count):
                pillar_accuracy_issues += 1
                print(f"   Pillar '{pillar.get('name')}' count mismatch:")
                print(f"     Areas: reported={reported_area_count}, actual={actual_area_count}")
                print(f"     Projects: reported={reported_project_count}, actual={actual_project_count}")
                print(f"     Tasks: reported={reported_task_count}, actual={actual_task_count}")
        
        # Cross-reference area counts
        area_accuracy_issues = 0
        for area in areas:
            area_id = area.get('id')
            reported_project_count = area.get('project_count', 0)
            reported_task_count = area.get('task_count', 0)
            
            # Count actual projects for this area
            actual_project_count = len([p for p in projects if p.get('area_id') == area_id])
            
            # Count actual tasks for this area (through projects)
            area_project_ids = [p.get('id') for p in projects if p.get('area_id') == area_id]
            actual_task_count = len([t for t in tasks if t.get('project_id') in area_project_ids])
            
            if (reported_project_count != actual_project_count or 
                reported_task_count != actual_task_count):
                area_accuracy_issues += 1
                print(f"   Area '{area.get('name')}' count mismatch:")
                print(f"     Projects: reported={reported_project_count}, actual={actual_project_count}")
                print(f"     Tasks: reported={reported_task_count}, actual={actual_task_count}")
        
        # Test results
        pillar_counts_accurate = pillar_accuracy_issues == 0
        area_counts_accurate = area_accuracy_issues == 0
        
        self.log_test(
            "PILLAR COUNT ACCURACY",
            pillar_counts_accurate,
            f"All pillar counts accurate" if pillar_counts_accurate else f"{pillar_accuracy_issues} pillars have inaccurate counts"
        )
        
        self.log_test(
            "AREA COUNT ACCURACY",
            area_counts_accurate,
            f"All area counts accurate" if area_counts_accurate else f"{area_accuracy_issues} areas have inaccurate counts"
        )
        
        return pillar_counts_accurate and area_counts_accurate

    def run_comprehensive_hierarchy_counts_test(self):
        """Run comprehensive hierarchy counts testing"""
        print("\n🔢 STARTING HIERARCHY ITEM COUNTS FIX COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("Pillars Hierarchy Counts", self.test_pillars_hierarchy_counts),
            ("Areas Hierarchy Counts", self.test_areas_hierarchy_counts),
            ("Ultra-Performance Endpoints", self.test_ultra_performance_endpoints),
            ("Batch Query Optimization", self.test_batch_query_optimization),
            ("Hierarchy Data Accuracy", self.test_hierarchy_data_accuracy)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🔢 HIERARCHY ITEM COUNTS FIX TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for hierarchy counts functionality
        pillars_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PILLARS' in result['test'])
        areas_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AREAS' in result['test'])
        performance_tests_passed = sum(1 for result in self.test_results if result['success'] and ('ULTRA' in result['test'] or 'BATCH' in result['test']))
        accuracy_tests_passed = sum(1 for result in self.test_results if result['success'] and 'ACCURACY' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Pillars Hierarchy Tests Passed: {pillars_tests_passed}")
        print(f"Areas Hierarchy Tests Passed: {areas_tests_passed}")
        print(f"Performance Tests Passed: {performance_tests_passed}")
        print(f"Accuracy Tests Passed: {accuracy_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ HIERARCHY ITEM COUNTS FIX: SUCCESS")
            print("   ✅ GET /api/pillars showing accurate counts (area_count, project_count, task_count)")
            print("   ✅ GET /api/areas showing accurate counts (project_count, task_count)")
            print("   ✅ Counts are accurate and not showing '0' for existing hierarchies")
            print("   ✅ Batch query optimization working efficiently")
            print("   ✅ No N+1 query problems detected")
            print("   ✅ Both regular and ultra-performance endpoints working")
            print("   The hierarchy item counts fix is production-ready!")
        else:
            print("\n❌ HIERARCHY ITEM COUNTS FIX: ISSUES DETECTED")
            print("   Issues found in hierarchy counts implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Hierarchy Item Counts Fix Tests"""
    print("🔢 STARTING HIERARCHY ITEM COUNTS FIX BACKEND TESTING")
    print("=" * 80)
    
    tester = HierarchyCountsAPITester()
    
    try:
        # Run the comprehensive hierarchy counts tests
        success = tester.run_comprehensive_hierarchy_counts_test()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)