#!/usr/bin/env python3
"""
Comprehensive E2E Backend Testing for Aurum Life Application
Tests all endpoints systematically focusing on known issues from the review request
"""

import requests
import sys
import json
from datetime import datetime
import time

class AurumLifeE2ETester:
    def __init__(self, base_url="https://journal-analytics-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        
        # Test credentials from the review request
        self.test_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_password = "password123"

    def log_test(self, name, success, status_code=None, error_msg=None, response_time=None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            time_info = f" ({response_time:.2f}s)" if response_time else ""
            print(f"✅ {name} - Status: {status_code}{time_info}")
        else:
            self.failed_tests.append({
                'name': name,
                'status_code': status_code,
                'error': error_msg
            })
            print(f"❌ {name} - Status: {status_code}, Error: {error_msg}")

    def make_request(self, method, endpoint, data=None, expected_status=200, timeout=30):
        """Make HTTP request with proper headers and timing"""
        url = f"{self.base_url}/api/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)
            
            response_time = time.time() - start_time
            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:200]}
            
            return success, response.status_code, response_data, response_time
            
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return False, 'TIMEOUT', {'error': f'Request timeout after {timeout}s'}, response_time
        except requests.exceptions.ConnectionError:
            response_time = time.time() - start_time
            return False, 'CONNECTION_ERROR', {'error': 'Connection failed'}, response_time
        except Exception as e:
            response_time = time.time() - start_time
            return False, 'EXCEPTION', {'error': str(e)}, response_time

    def test_authentication(self):
        """Test authentication - critical for all other tests"""
        print("\n🔐 Testing Authentication...")
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, status, data, response_time = self.make_request('POST', 'auth/login', login_data, expected_status=200)
        
        if success and 'access_token' in data:
            self.token = data['access_token']
            self.user_id = data.get('user', {}).get('id')
            print(f"🎯 Login successful - User ID: {self.user_id}")
        
        self.log_test("User Login", success, status, data.get('error') or data.get('detail'), response_time)
        return success

    def test_core_navigation_endpoints(self):
        """Test all core navigation screen endpoints"""
        print("\n📊 Testing Core Navigation Endpoints...")
        
        endpoints = [
            ('pillars', 'Get Pillars'),
            ('areas', 'Get Areas'), 
            ('projects', 'Get Projects'),
            ('tasks', 'Get Tasks'),
            ('insights', 'Get Insights')
        ]
        
        for endpoint, name in endpoints:
            success, status, data, response_time = self.make_request('GET', endpoint)
            error_msg = data.get('error') if isinstance(data, dict) else str(data)[:100]
            self.log_test(name, success, status, error_msg, response_time)

    def test_journal_endpoints_detailed(self):
        """Test journal endpoints - PRIORITY KNOWN ISSUES"""
        print("\n📖 Testing Journal Endpoints (PRIORITY - Known Network Errors)...")
        
        # Test journal entries endpoint
        success, status, data, response_time = self.make_request('GET', 'journal')
        error_msg = data.get('error') if isinstance(data, dict) else str(data)[:100]
        self.log_test("Journal Entries Endpoint", success, status, error_msg, response_time)
        
        # Test journal templates endpoint  
        success, status, data, response_time = self.make_request('GET', 'journal/templates')
        error_msg = data.get('error') if isinstance(data, dict) else str(data)[:100]
        self.log_test("Journal Templates Endpoint", success, status, error_msg, response_time)

    def test_ai_powered_features(self):
        """Test AI-powered features"""
        print("\n🧠 Testing AI-Powered Features...")
        
        ai_endpoints = [
            ('ai/quota', 'AI Quota'),
            ('ai/today-priorities', 'AI Today Priorities'),
            ('ai/suggest-focus', 'AI Suggest Focus'),
            ('ai/task-why-statements', 'AI Task Why Statements')
        ]
        
        for endpoint, name in ai_endpoints:
            success, status, data, response_time = self.make_request('GET', endpoint)
            error_msg = data.get('error') if isinstance(data, dict) else str(data)[:100]
            self.log_test(name, success, status, error_msg, response_time)

    def test_alignment_endpoints_detailed(self):
        """Test alignment endpoints - KNOWN TIMEOUT ISSUES"""
        print("\n🎯 Testing Alignment Endpoints (Known Timeout Issues)...")
        
        # Test with longer timeout for alignment endpoints
        alignment_endpoints = [
            ('alignment/dashboard', 'Alignment Dashboard'),
            ('alignment/weekly-score', 'Weekly Alignment Score'),
            ('alignment/monthly-score', 'Monthly Alignment Score'),
            ('alignment-score', 'Legacy Alignment Score')
        ]
        
        for endpoint, name in alignment_endpoints:
            # Use longer timeout for alignment endpoints due to known issues
            success, status, data, response_time = self.make_request('GET', endpoint, timeout=35)
            error_msg = data.get('error') if isinstance(data, dict) else str(data)[:100]
            self.log_test(name, success, status, error_msg, response_time)

    def test_semantic_search_features(self):
        """Test semantic search features"""
        print("\n🔍 Testing Semantic Search Features...")
        
        # Test basic semantic search
        success, status, data, response_time = self.make_request('GET', 'semantic/search?query=productivity&limit=5')
        error_msg = data.get('error') if isinstance(data, dict) else str(data)[:100]
        self.log_test("Semantic Search", success, status, error_msg, response_time)

    def test_analytics_intelligence(self):
        """Test analytics and intelligence features"""
        print("\n📈 Testing Analytics & Intelligence...")
        
        analytics_endpoints = [
            ('analytics/dashboard', 'Analytics Dashboard'),
            ('analytics/engagement', 'Engagement Metrics'),
            ('analytics/ai-features', 'AI Features Analytics'),
            ('analytics/preferences', 'Analytics Preferences')
        ]
        
        for endpoint, name in analytics_endpoints:
            success, status, data, response_time = self.make_request('GET', endpoint)
            error_msg = data.get('error') if isinstance(data, dict) else str(data)[:100]
            self.log_test(name, success, status, error_msg, response_time)

    def test_sentiment_emotional_os(self):
        """Test sentiment analysis (Emotional OS) features"""
        print("\n😊 Testing Sentiment Analysis (Emotional OS)...")
        
        sentiment_endpoints = [
            ('sentiment/trends', 'Sentiment Trends'),
            ('sentiment/wellness-score', 'Emotional Wellness Score'),
            ('sentiment/correlations', 'Activity Sentiment Correlations'),
            ('sentiment/insights', 'Emotional Insights')
        ]
        
        for endpoint, name in sentiment_endpoints:
            success, status, data, response_time = self.make_request('GET', endpoint)
            error_msg = data.get('error') if isinstance(data, dict) else str(data)[:100]
            self.log_test(name, success, status, error_msg, response_time)

    def test_health_connectivity(self):
        """Test basic health and connectivity"""
        print("\n🏥 Testing Health & Connectivity...")
        
        # Test root endpoint
        success, status, data, response_time = self.make_request('GET', '', expected_status=200)
        error_msg = data.get('error') if isinstance(data, dict) else str(data)[:100]
        self.log_test("Root Endpoint", success, status, error_msg, response_time)
        
        # Test health endpoint
        success, status, data, response_time = self.make_request('GET', 'health', expected_status=200)
        error_msg = data.get('error') if isinstance(data, dict) else str(data)[:100]
        self.log_test("Health Check", success, status, error_msg, response_time)

    def run_comprehensive_tests(self):
        """Run all comprehensive E2E backend tests"""
        print("🚀 Starting Comprehensive E2E Backend Testing for Aurum Life")
        print(f"🎯 Target URL: {self.base_url}")
        print(f"👤 Test User: {self.test_email}")
        print("🔍 Focus: Known issues from review request")
        print("=" * 70)
        
        # Test basic connectivity first
        self.test_health_connectivity()
        
        # Test authentication - critical for other tests
        if not self.test_authentication():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with authenticated tests")
            self.print_summary()
            return 1
        
        # Test all feature areas systematically
        self.test_core_navigation_endpoints()
        self.test_journal_endpoints_detailed()  # PRIORITY - Known issues
        self.test_ai_powered_features()
        self.test_alignment_endpoints_detailed()  # PRIORITY - Known timeout issues
        self.test_semantic_search_features()
        self.test_analytics_intelligence()
        self.test_sentiment_emotional_os()
        
        # Print final summary
        self.print_summary()
        
        return 0 if len(self.failed_tests) == 0 else 1

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE E2E BACKEND TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"❌ Tests Failed: {len(self.failed_tests)}/{self.tests_run}")
        
        if self.tests_run > 0:
            success_rate = (self.tests_passed / self.tests_run) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests:
            print("\n🚨 FAILED TESTS (Priority Issues):")
            priority_issues = []
            other_issues = []
            
            for test in self.failed_tests:
                if any(keyword in test['name'].lower() for keyword in ['journal', 'alignment', 'timeout']):
                    priority_issues.append(test)
                else:
                    other_issues.append(test)
            
            if priority_issues:
                print("\n  🔥 HIGH PRIORITY (Known Issues):")
                for test in priority_issues:
                    print(f"    • {test['name']}: {test['status_code']} - {test['error']}")
            
            if other_issues:
                print("\n  ⚠️  OTHER ISSUES:")
                for test in other_issues:
                    print(f"    • {test['name']}: {test['status_code']} - {test['error']}")
        
        print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

def main():
    tester = AurumLifeE2ETester()
    return tester.run_comprehensive_tests()

if __name__ == "__main__":
    sys.exit(main())