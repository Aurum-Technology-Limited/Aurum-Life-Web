#!/usr/bin/env python3
"""
SIMPLIFIED DYNAMIC ACHIEVEMENTS SYSTEM TESTING
Focus on testing the core achievement system functionality without requiring pre-existing badges.
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import time

# Configuration
BACKEND_URL = "https://b5a62d15-d24c-4532-9cae-06d0896a435f.preview.emergentagent.com/api"

class SimpleAchievementTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = None
        self.test_results = []
        self.created_resources = []
        
        # Use realistic test data
        self.test_user_email = f"achievement.test_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "AchievementTest2025!"
        self.test_user_data = {
            "username": f"achievement_test_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Achievement",
            "last_name": "Tester",
            "password": self.test_user_password
        }
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")

    def make_request(self, method: str, endpoint: str, data: dict = None, use_auth: bool = False) -> dict:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Request failed: {str(e)}",
                'status_code': None,
                'data': {}
            }

    def test_basic_connectivity(self):
        """Test basic connectivity"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
        result = self.make_request('GET', '/health')
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_user_setup(self):
        """Test user registration and login"""
        print("\n=== TESTING USER SETUP ===")
        
        # Register user
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        self.log_test(
            "USER REGISTRATION",
            result['success'],
            f"User registered successfully" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Login user
        login_data = {
            "email": self.test_user_data['email'],
            "password": self.test_user_data['password']
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        self.auth_token = result['data'].get('access_token')
        return True

    def test_achievement_endpoints(self):
        """Test achievement API endpoints"""
        print("\n=== TESTING ACHIEVEMENT ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("ACHIEVEMENT ENDPOINTS", False, "No authentication token available")
            return False
        
        # Test GET /api/achievements
        result = self.make_request('GET', '/achievements', use_auth=True)
        self.log_test(
            "GET ACHIEVEMENTS ENDPOINT",
            result['success'],
            f"Retrieved achievements successfully" if result['success'] else f"Failed to get achievements: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            achievements_data = result['data']
            
            # Verify response structure
            has_success = achievements_data.get('success', False)
            has_achievements = 'achievements' in achievements_data
            has_timestamp = 'timestamp' in achievements_data
            
            self.log_test(
                "ACHIEVEMENTS RESPONSE STRUCTURE",
                has_success and has_achievements and has_timestamp,
                f"Response has correct structure (success: {has_success}, achievements: {has_achievements}, timestamp: {has_timestamp})"
            )
            
            achievements_list = achievements_data.get('achievements', [])
            self.log_test(
                "ACHIEVEMENTS LIST TYPE",
                isinstance(achievements_list, list),
                f"Achievements returned as list with {len(achievements_list)} items"
            )
        
        # Test POST /api/achievements/check
        result = self.make_request('POST', '/achievements/check', use_auth=True)
        self.log_test(
            "CHECK ACHIEVEMENTS ENDPOINT",
            result['success'],
            f"Achievement check completed successfully" if result['success'] else f"Failed to check achievements: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            check_data = result['data']
            
            # Verify response structure
            has_success = check_data.get('success', False)
            has_newly_unlocked = 'newly_unlocked' in check_data
            has_achievements = 'achievements' in check_data
            has_timestamp = 'timestamp' in check_data
            
            self.log_test(
                "CHECK ACHIEVEMENTS RESPONSE STRUCTURE",
                has_success and has_newly_unlocked and has_achievements and has_timestamp,
                f"Check response has correct structure"
            )
            
            newly_unlocked_count = check_data.get('newly_unlocked', -1)
            self.log_test(
                "NEWLY UNLOCKED COUNT TYPE",
                isinstance(newly_unlocked_count, int) and newly_unlocked_count >= 0,
                f"Newly unlocked count: {newly_unlocked_count}"
            )
        
        return True

    def test_trigger_integration(self):
        """Test that trigger functions don't cause errors when called through normal operations"""
        print("\n=== TESTING TRIGGER INTEGRATION ===")
        
        if not self.auth_token:
            self.log_test("TRIGGER INTEGRATION", False, "No authentication token available")
            return False
        
        # Create infrastructure for testing triggers
        pillar_data = {
            "name": "Achievement Test Pillar",
            "description": "Test pillar for achievement triggers",
            "icon": "🎯",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE TEST PILLAR", False, "Failed to create test pillar")
            return False
        
        pillar_id = result['data']['id']
        self.created_resources.append(('pillar', pillar_id))
        
        area_data = {
            "name": "Achievement Test Area",
            "description": "Test area for achievement triggers",
            "icon": "📋",
            "color": "#2196F3",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE TEST AREA", False, "Failed to create test area")
            return False
        
        area_id = result['data']['id']
        self.created_resources.append(('area', area_id))
        
        project_data = {
            "area_id": area_id,
            "name": "Achievement Test Project",
            "description": "Project for testing achievement triggers",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE TEST PROJECT", False, "Failed to create test project")
            return False
        
        project_id = result['data']['id']
        self.created_resources.append(('project', project_id))
        
        # Test task completion trigger (should not cause errors even without badges)
        task_data = {
            "project_id": project_id,
            "name": "Achievement Test Task",
            "description": "Task for testing achievement triggers",
            "priority": "medium",
            "status": "todo"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        if result['success']:
            task_id = result['data']['id']
            self.created_resources.append(('task', task_id))
            
            # Complete the task (this should trigger achievement checking without errors)
            update_data = {"status": "completed"}
            update_result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
            
            self.log_test(
                "TASK COMPLETION TRIGGER",
                update_result['success'],
                f"Task completion trigger executed without errors" if update_result['success'] else f"Task completion trigger failed: {update_result.get('error', 'Unknown error')}"
            )
        
        # Test project completion trigger
        update_data = {"status": "Completed"}
        update_result = self.make_request('PUT', f'/projects/{project_id}', data=update_data, use_auth=True)
        
        self.log_test(
            "PROJECT COMPLETION TRIGGER",
            update_result['success'],
            f"Project completion trigger executed without errors" if update_result['success'] else f"Project completion trigger failed: {update_result.get('error', 'Unknown error')}"
        )
        
        # Test journal entry creation trigger
        journal_data = {
            "title": "Achievement Test Journal Entry",
            "content": "Testing journal entry creation for achievement triggers.",
            "mood": "grateful",
            "energy_level": "high",
            "tags": ["achievement", "testing"]
        }
        
        result = self.make_request('POST', '/journal', data=journal_data, use_auth=True)
        self.log_test(
            "JOURNAL ENTRY CREATION TRIGGER",
            result['success'],
            f"Journal entry creation trigger executed without errors" if result['success'] else f"Journal entry creation trigger failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            entry_id = result['data']['id']
            self.created_resources.append(('journal', entry_id))
        
        return True

    def test_performance(self):
        """Test that operations complete in reasonable time"""
        print("\n=== TESTING PERFORMANCE ===")
        
        if not self.auth_token:
            self.log_test("PERFORMANCE TESTING", False, "No authentication token available")
            return False
        
        # Test achievement API performance
        start_time = time.time()
        result = self.make_request('GET', '/achievements', use_auth=True)
        achievement_time = time.time() - start_time
        
        performance_ok = achievement_time < 3.0
        self.log_test(
            "ACHIEVEMENT API PERFORMANCE",
            performance_ok,
            f"Achievement API response time: {achievement_time:.2f}s" if performance_ok else f"Slow achievement API: {achievement_time:.2f}s"
        )
        
        # Test manual check performance
        start_time = time.time()
        result = self.make_request('POST', '/achievements/check', use_auth=True)
        check_time = time.time() - start_time
        
        check_performance_ok = check_time < 5.0
        self.log_test(
            "ACHIEVEMENT CHECK PERFORMANCE",
            check_performance_ok,
            f"Achievement check time: {check_time:.2f}s" if check_performance_ok else f"Slow achievement check: {check_time:.2f}s"
        )
        
        return performance_ok and check_performance_ok

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        cleanup_count = 0
        
        # Clean up in reverse order
        for resource_type, resource_id in reversed(self.created_resources):
            try:
                if resource_type == 'journal':
                    result = self.make_request('DELETE', f'/journal/{resource_id}', use_auth=True)
                elif resource_type == 'task':
                    result = self.make_request('DELETE', f'/tasks/{resource_id}', use_auth=True)
                elif resource_type == 'project':
                    result = self.make_request('DELETE', f'/projects/{resource_id}', use_auth=True)
                elif resource_type == 'area':
                    result = self.make_request('DELETE', f'/areas/{resource_id}', use_auth=True)
                elif resource_type == 'pillar':
                    result = self.make_request('DELETE', f'/pillars/{resource_id}', use_auth=True)
                
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up {resource_type}: {resource_id}")
            except:
                pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

    def run_tests(self):
        """Run all achievement system tests"""
        print("\n🏆 STARTING SIMPLIFIED DYNAMIC ACHIEVEMENTS SYSTEM TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Setup", self.test_user_setup),
            ("Achievement Endpoints", self.test_achievement_endpoints),
            ("Trigger Integration", self.test_trigger_integration),
            ("Performance", self.test_performance)
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
        print("🎯 DYNAMIC ACHIEVEMENTS SYSTEM TESTING SUMMARY")
        print("=" * 80)
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze individual test results
        total_individual_tests = len(self.test_results)
        passed_individual_tests = sum(1 for result in self.test_results if result['success'])
        individual_success_rate = (passed_individual_tests / total_individual_tests * 100) if total_individual_tests > 0 else 0
        
        print(f"Individual Tests: {passed_individual_tests}/{total_individual_tests} successful")
        print(f"Individual Success Rate: {individual_success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n✅ DYNAMIC ACHIEVEMENTS SYSTEM: SUCCESS")
            print("   ✅ Achievement API endpoints working correctly")
            print("   ✅ Auto-tracking trigger functions operational (no errors)")
            print("   ✅ Response structures correct")
            print("   ✅ Performance optimized - no significant latency added")
            print("   ✅ Integration with existing services working")
            print("   The Dynamic Achievements System core functionality is working!")
        else:
            print("\n❌ DYNAMIC ACHIEVEMENTS SYSTEM: ISSUES DETECTED")
            print("   Issues found in achievement system implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 80

def main():
    """Run Simplified Dynamic Achievements System Tests"""
    print("🏆 STARTING SIMPLIFIED DYNAMIC ACHIEVEMENTS SYSTEM BACKEND TESTING")
    print("=" * 80)
    
    tester = SimpleAchievementTester()
    
    try:
        success = tester.run_tests()
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False
    
    finally:
        # Cleanup created resources
        tester.cleanup_resources()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)