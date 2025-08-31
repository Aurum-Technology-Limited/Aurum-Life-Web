#!/usr/bin/env python3
"""
Comprehensive HRM and AI Intelligence Center Backend Testing
Tests all HRM endpoints, authentication, and AI functionality
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class HRMBackendTester:
    def __init__(self, base_url: str = "https://aurum-codebase.preview.emergentagent.com"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test credentials
        self.test_email = "test@aurumlife.com"
        self.test_password = "password123"
        
        print(f"🚀 Starting HRM Backend Testing")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🔑 Test Account: {self.test_email}")
        print("=" * 60)

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            print(f"   {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details,
            'response_data': response_data
        })

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request with authentication"""
        url = f"{self.api_base}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response.status_code, response.json() if response.content else {}
            
        except requests.exceptions.Timeout:
            return 408, {"error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            return 500, {"error": str(e)}
        except json.JSONDecodeError:
            return response.status_code, {"error": "Invalid JSON response"}

    def test_authentication(self) -> bool:
        """Test authentication flow"""
        print("\n🔐 Testing Authentication...")
        
        # Test login
        status, response = self.make_request('POST', '/auth/login', {
            'email': self.test_email,
            'password': self.test_password
        })
        
        if status == 200 and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response.get('user', {}).get('id')
            self.log_test("User Login", True, f"Token received, User ID: {self.user_id}")
            return True
        else:
            self.log_test("User Login", False, f"Status: {status}, Response: {response}")
            return False

    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n🏥 Testing Basic Endpoints...")
        
        # Health check
        status, response = self.make_request('GET', '/health')
        self.log_test("Health Check", status == 200, f"Status: {status}")
        
        # Root endpoint
        status, response = self.make_request('GET', '/')
        self.log_test("Root Endpoint", status == 200, f"Status: {status}")

    def test_hrm_analyze_endpoint(self):
        """Test HRM analyze endpoint"""
        print("\n🧠 Testing HRM Analysis Endpoints...")
        
        # Test global analysis
        status, response = self.make_request('POST', '/hrm/analyze', {
            'entity_type': 'global',
            'entity_id': None,
            'analysis_depth': 'balanced',
            'force_llm': False
        })
        
        if status == 200:
            insight_id = response.get('insight_id')
            self.log_test("Global Analysis", True, f"Insight ID: {insight_id}, Confidence: {response.get('confidence_score', 0):.2f}")
            return insight_id
        else:
            self.log_test("Global Analysis", False, f"Status: {status}, Error: {response.get('detail', 'Unknown error')}")
            return None

    def test_hrm_insights_endpoint(self):
        """Test HRM insights retrieval"""
        print("\n📊 Testing HRM Insights Endpoints...")
        
        # Get all insights
        status, response = self.make_request('GET', '/hrm/insights')
        
        if status == 200:
            insights = response.get('insights', [])
            total = response.get('total', 0)
            self.log_test("Get All Insights", True, f"Retrieved {total} insights")
            
            # Test with filters
            status, response = self.make_request('GET', '/hrm/insights', params={
                'entity_type': 'global',
                'is_active': True,
                'limit': 10
            })
            
            if status == 200:
                filtered_insights = response.get('insights', [])
                self.log_test("Get Filtered Insights", True, f"Retrieved {len(filtered_insights)} filtered insights")
                return filtered_insights[0]['id'] if filtered_insights else None
            else:
                self.log_test("Get Filtered Insights", False, f"Status: {status}")
                return None
        else:
            self.log_test("Get All Insights", False, f"Status: {status}, Error: {response.get('detail', 'Unknown error')}")
            return None

    def test_hrm_statistics_endpoint(self):
        """Test HRM statistics endpoint"""
        print("\n📈 Testing HRM Statistics...")
        
        status, response = self.make_request('GET', '/hrm/statistics', params={'days': 30})
        
        if status == 200:
            stats = response.get('statistics', {})
            self.log_test("Get Statistics", True, f"Stats: {json.dumps(stats, indent=2)}")
        else:
            self.log_test("Get Statistics", False, f"Status: {status}, Error: {response.get('detail', 'Unknown error')}")

    def test_hrm_prioritize_today_endpoint(self):
        """Test HRM today prioritization"""
        print("\n🎯 Testing Today Prioritization...")
        
        status, response = self.make_request('POST', '/hrm/prioritize-today', params={
            'top_n': 5,
            'include_reasoning': True
        })
        
        if status == 200:
            tasks = response.get('tasks', [])
            coaching_message = response.get('coaching_message', '')
            self.log_test("Today Prioritization", True, f"Retrieved {len(tasks)} priority tasks")
            if coaching_message:
                print(f"   💬 Coaching: {coaching_message[:100]}...")
        else:
            self.log_test("Today Prioritization", False, f"Status: {status}, Error: {response.get('detail', 'Unknown error')}")

    def test_hrm_preferences_endpoints(self):
        """Test HRM preferences endpoints"""
        print("\n⚙️ Testing HRM Preferences...")
        
        # Get preferences
        status, response = self.make_request('GET', '/hrm/preferences')
        
        if status == 200:
            preferences = response
            self.log_test("Get Preferences", True, f"Retrieved preferences")
            
            # Update preferences
            update_data = {
                'explanation_detail_level': 'detailed',
                'show_confidence_scores': True,
                'ai_personality': 'coach'
            }
            
            status, response = self.make_request('PUT', '/hrm/preferences', update_data)
            
            if status == 200:
                self.log_test("Update Preferences", True, "Preferences updated successfully")
            else:
                self.log_test("Update Preferences", False, f"Status: {status}")
        else:
            self.log_test("Get Preferences", False, f"Status: {status}")

    def test_insight_interactions(self, insight_id: str):
        """Test insight interaction endpoints"""
        if not insight_id:
            print("\n⚠️ Skipping insight interactions - no insight ID available")
            return
            
        print("\n🔄 Testing Insight Interactions...")
        
        # Test feedback
        status, response = self.make_request('POST', f'/hrm/insights/{insight_id}/feedback', {
            'feedback': 'accepted',
            'feedback_details': {'test': True}
        })
        
        self.log_test("Provide Feedback", status == 200, f"Status: {status}")
        
        # Test pinning
        status, response = self.make_request('POST', f'/hrm/insights/{insight_id}/pin', params={'pinned': True})
        self.log_test("Pin Insight", status == 200, f"Status: {status}")
        
        # Test unpinning
        status, response = self.make_request('POST', f'/hrm/insights/{insight_id}/pin', params={'pinned': False})
        self.log_test("Unpin Insight", status == 200, f"Status: {status}")

    def test_batch_analysis(self):
        """Test batch analysis endpoint"""
        print("\n🔄 Testing Batch Analysis...")
        
        status, response = self.make_request('POST', '/hrm/batch-analyze', params={
            'entity_types': 'pillar,area,project',
            'analysis_depth': 'balanced'
        })
        
        if status == 200:
            self.log_test("Batch Analysis", True, "Batch analysis started successfully")
        else:
            self.log_test("Batch Analysis", False, f"Status: {status}, Error: {response.get('detail', 'Unknown error')}")

    def test_core_data_endpoints(self):
        """Test core data endpoints (pillars, areas, projects, tasks)"""
        print("\n📋 Testing Core Data Endpoints...")
        
        endpoints = [
            ('/pillars', 'Pillars'),
            ('/areas', 'Areas'), 
            ('/projects', 'Projects'),
            ('/tasks', 'Tasks'),
            ('/insights', 'Insights')
        ]
        
        for endpoint, name in endpoints:
            status, response = self.make_request('GET', endpoint)
            self.log_test(f"Get {name}", status == 200, f"Status: {status}")

    def test_ai_integration(self):
        """Test AI integration and LLM functionality"""
        print("\n🤖 Testing AI Integration...")
        
        # Test detailed analysis with LLM
        status, response = self.make_request('POST', '/hrm/analyze', {
            'entity_type': 'global',
            'entity_id': None,
            'analysis_depth': 'detailed',
            'force_llm': True
        })
        
        if status == 200:
            used_llm = response.get('used_llm', False)
            confidence = response.get('confidence_score', 0)
            self.log_test("AI LLM Analysis", True, f"LLM Used: {used_llm}, Confidence: {confidence:.2f}")
            
            # Check for AI-generated content
            reasoning_path = response.get('reasoning_path', [])
            recommendations = response.get('recommendations', [])
            
            if reasoning_path:
                self.log_test("AI Reasoning Path", True, f"Generated {len(reasoning_path)} reasoning steps")
            
            if recommendations:
                self.log_test("AI Recommendations", True, f"Generated {len(recommendations)} recommendations")
                print(f"   📝 Sample recommendation: {recommendations[0][:100]}...")
        else:
            self.log_test("AI LLM Analysis", False, f"Status: {status}, Error: {response.get('detail', 'Unknown error')}")

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🚨 Testing Error Handling...")
        
        # Test invalid entity type
        status, response = self.make_request('POST', '/hrm/analyze', {
            'entity_type': 'invalid_type',
            'analysis_depth': 'balanced'
        })
        
        self.log_test("Invalid Entity Type", status >= 400, f"Status: {status} (should be 4xx)")
        
        # Test invalid insight ID
        status, response = self.make_request('GET', '/hrm/insights/invalid-id')
        self.log_test("Invalid Insight ID", status == 404, f"Status: {status} (should be 404)")
        
        # Test unauthorized access (without token)
        old_token = self.token
        self.token = None
        status, response = self.make_request('GET', '/hrm/insights')
        self.log_test("Unauthorized Access", status == 401, f"Status: {status} (should be 401)")
        self.token = old_token

    def run_performance_tests(self):
        """Test performance and response times"""
        print("\n⚡ Testing Performance...")
        
        start_time = time.time()
        status, response = self.make_request('POST', '/hrm/analyze', {
            'entity_type': 'global',
            'analysis_depth': 'minimal'
        })
        end_time = time.time()
        
        response_time = end_time - start_time
        self.log_test("Analysis Response Time", response_time < 10.0, f"{response_time:.2f}s (should be < 10s)")
        
        # Test concurrent requests simulation
        start_time = time.time()
        for i in range(3):
            status, response = self.make_request('GET', '/hrm/insights', params={'limit': 5})
        end_time = time.time()
        
        total_time = end_time - start_time
        self.log_test("Multiple Requests", total_time < 15.0, f"{total_time:.2f}s for 3 requests")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 Starting Comprehensive HRM Backend Testing\n")
        
        # Authentication is required for all other tests
        if not self.test_authentication():
            print("❌ Authentication failed - cannot continue with other tests")
            return self.print_summary()
        
        # Run all test suites
        self.test_basic_endpoints()
        
        # Core HRM functionality
        insight_id = self.test_hrm_analyze_endpoint()
        insight_id_from_list = self.test_hrm_insights_endpoint()
        self.test_hrm_statistics_endpoint()
        self.test_hrm_prioritize_today_endpoint()
        self.test_hrm_preferences_endpoints()
        
        # Use insight ID from analysis or list
        test_insight_id = insight_id or insight_id_from_list
        self.test_insight_interactions(test_insight_id)
        
        # Additional tests
        self.test_batch_analysis()
        self.test_core_data_endpoints()
        self.test_ai_integration()
        self.test_error_handling()
        self.run_performance_tests()
        
        return self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Tests: {self.tests_run}")
        
        # Print failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['name']}: {test['details']}")
        
        # Print critical issues
        critical_failures = [
            test for test in failed_tests 
            if any(keyword in test['name'].lower() for keyword in ['login', 'auth', 'analyze', 'insights'])
        ]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES ({len(critical_failures)}):")
            for test in critical_failures:
                print(f"   • {test['name']}: {test['details']}")
        
        print("\n" + "=" * 60)
        
        return success_rate >= 70  # Consider 70%+ success rate as acceptable

def main():
    """Main test execution"""
    tester = HRMBackendTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())