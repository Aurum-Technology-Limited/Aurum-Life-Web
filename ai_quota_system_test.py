#!/usr/bin/env python3
"""
AI Quota and System Integration Test
Tests AI quota functionality, sentiment analysis, HRM, RAG, and overall system integration
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

class AIQuotaSystemTester:
    def __init__(self, base_url="https://journal-analytics-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test user credentials - try different passwords or create unique user
        self.test_email = f"test_user_{int(time.time())}@aurumtechnologyltd.com"
        self.test_password = "TestPassword123!"

    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED - {details}")
        
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data
        })

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            return True, response
        except requests.exceptions.RequestException as e:
            return False, str(e)

    def test_health_check(self):
        """Test basic API health"""
        print("\n🏥 Testing API Health...")
        
        success, response = self.make_request('GET', '')
        if success and response.status_code == 200:
            self.log_result("API Root Health", True, f"Status: {response.status_code}")
        else:
            self.log_result("API Root Health", False, f"Status: {response.status_code if success else response}")

        success, response = self.make_request('GET', 'health')
        if success and response.status_code == 200:
            self.log_result("API Health Endpoint", True, f"Status: {response.status_code}")
        else:
            self.log_result("API Health Endpoint", False, f"Status: {response.status_code if success else response}")

    def test_authentication(self):
        """Test user authentication"""
        print("\n🔐 Testing Authentication...")
        
        # First try to login with test user
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.make_request('POST', 'auth/login', login_data)
        
        if success and response.status_code == 200:
            try:
                data = response.json()
                if 'access_token' in data:
                    self.token = data['access_token']
                    self.user_id = data.get('user', {}).get('id')
                    self.log_result("User Authentication", True, f"Logged in as {self.test_email}")
                    return True
                else:
                    self.log_result("User Authentication", False, "No access token in response")
            except json.JSONDecodeError:
                self.log_result("User Authentication", False, "Invalid JSON response")
        else:
            # If login fails, try to register the user first
            print("   Login failed, attempting to register user...")
            
            register_data = {
                "email": self.test_email,
                "password": self.test_password,
                "first_name": "Marc",
                "last_name": "Alleyne",
                "username": "marc_alleyne",
                "birth_date": "1990-01-01"
            }
            
            success, response = self.make_request('POST', 'auth/register', register_data)
            
            if success and response.status_code in [200, 201]:
                self.log_result("User Registration", True, f"Registered user {self.test_email}")
                
                # Now try to login again
                success, response = self.make_request('POST', 'auth/login', login_data)
                
                if success and response.status_code == 200:
                    try:
                        data = response.json()
                        if 'access_token' in data:
                            self.token = data['access_token']
                            self.user_id = data.get('user', {}).get('id')
                            self.log_result("User Authentication", True, f"Logged in as {self.test_email}")
                            return True
                        else:
                            self.log_result("User Authentication", False, "No access token in response after registration")
                    except json.JSONDecodeError:
                        self.log_result("User Authentication", False, "Invalid JSON response after registration")
                else:
                    self.log_result("User Authentication", False, f"Login failed after registration: {response.status_code if success else 'Request failed'}")
            else:
                error_msg = f"Registration failed: {response.status_code if success else 'Request failed'}"
                if success:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('detail', 'Unknown error')}"
                    except:
                        pass
                self.log_result("User Registration", False, error_msg)
                
                # Still try original login error message
                error_msg = f"Login Status: {response.status_code if success else 'Request failed'}"
                self.log_result("User Authentication", False, error_msg)
        
        return False

    def test_ai_quota_system(self):
        """Test AI quota functionality"""
        print("\n🤖 Testing AI Quota System...")
        
        if not self.token:
            self.log_result("AI Quota Check", False, "No authentication token")
            return
        
        success, response = self.make_request('GET', 'ai/quota')
        
        if success and response.status_code == 200:
            try:
                quota_data = response.json()
                remaining = quota_data.get('remaining', 0)
                total = quota_data.get('total', 0)
                used = quota_data.get('used', 0)
                
                # Check if quota allows interactions (should be 250/month for test user)
                if total >= 250 and remaining > 0:
                    self.log_result("AI Quota Check", True, 
                                  f"Quota: {remaining}/{total} remaining, {used} used")
                else:
                    self.log_result("AI Quota Check", False, 
                                  f"Insufficient quota: {remaining}/{total} remaining")
                
                return quota_data
            except json.JSONDecodeError:
                self.log_result("AI Quota Check", False, "Invalid JSON response")
        else:
            self.log_result("AI Quota Check", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        return None

    def test_ai_features(self):
        """Test AI-powered features"""
        print("\n🧠 Testing AI Features...")
        
        if not self.token:
            self.log_result("AI Features", False, "No authentication token")
            return
        
        # Test AI task why statements
        success, response = self.make_request('GET', 'ai/task-why-statements')
        if success and response.status_code == 200:
            self.log_result("AI Task Why Statements", True, "Endpoint accessible")
        else:
            self.log_result("AI Task Why Statements", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test AI focus suggestions
        success, response = self.make_request('GET', 'ai/suggest-focus', params={'top_n': 5})
        if success and response.status_code == 200:
            self.log_result("AI Focus Suggestions", True, "Endpoint accessible")
        else:
            self.log_result("AI Focus Suggestions", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test AI today priorities
        success, response = self.make_request('GET', 'ai/today-priorities', params={'top_n': 5})
        if success and response.status_code == 200:
            self.log_result("AI Today Priorities", True, "Endpoint accessible")
        else:
            self.log_result("AI Today Priorities", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")

    def test_sentiment_analysis(self):
        """Test sentiment analysis functionality"""
        print("\n💭 Testing Sentiment Analysis...")
        
        if not self.token:
            self.log_result("Sentiment Analysis", False, "No authentication token")
            return
        
        # Test sentiment analysis for text
        test_text = "I feel really excited about my progress today. Everything is going well and I'm motivated to achieve my goals!"
        
        sentiment_data = {
            "text": test_text
        }
        
        success, response = self.make_request('POST', 'sentiment/analyze-text', sentiment_data)
        
        if success and response.status_code == 200:
            try:
                result = response.json()
                sentiment_category = result.get('sentiment_analysis', {}).get('sentiment_category')
                if sentiment_category:
                    self.log_result("Sentiment Analysis - Text", True, 
                                  f"Detected sentiment: {sentiment_category}")
                else:
                    self.log_result("Sentiment Analysis - Text", False, "No sentiment category in response")
            except json.JSONDecodeError:
                self.log_result("Sentiment Analysis - Text", False, "Invalid JSON response")
        else:
            self.log_result("Sentiment Analysis - Text", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test sentiment trends
        success, response = self.make_request('GET', 'sentiment/trends', params={'days': 30})
        if success and response.status_code == 200:
            self.log_result("Sentiment Trends", True, "Endpoint accessible")
        else:
            self.log_result("Sentiment Trends", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test emotional wellness score
        success, response = self.make_request('GET', 'sentiment/wellness-score', params={'days': 30})
        if success and response.status_code == 200:
            self.log_result("Emotional Wellness Score", True, "Endpoint accessible")
        else:
            self.log_result("Emotional Wellness Score", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")

    def test_semantic_search_rag(self):
        """Test semantic search (RAG) functionality"""
        print("\n🔍 Testing Semantic Search (RAG)...")
        
        if not self.token:
            self.log_result("Semantic Search", False, "No authentication token")
            return
        
        # Test semantic search
        search_params = {
            'query': 'productivity and goals',
            'limit': 10,
            'min_similarity': 0.3
        }
        
        success, response = self.make_request('GET', 'semantic/search', params=search_params)
        
        if success and response.status_code == 200:
            try:
                result = response.json()
                results_count = len(result.get('results', []))
                self.log_result("Semantic Search", True, f"Found {results_count} results")
            except json.JSONDecodeError:
                self.log_result("Semantic Search", False, "Invalid JSON response")
        else:
            self.log_result("Semantic Search", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")

    def test_alignment_dashboard(self):
        """Test alignment dashboard functionality"""
        print("\n📊 Testing Alignment Dashboard...")
        
        if not self.token:
            self.log_result("Alignment Dashboard", False, "No authentication token")
            return
        
        # Test alignment dashboard
        success, response = self.make_request('GET', 'alignment/dashboard')
        if success and response.status_code == 200:
            self.log_result("Alignment Dashboard", True, "Endpoint accessible")
        else:
            self.log_result("Alignment Dashboard", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test weekly alignment score
        success, response = self.make_request('GET', 'alignment/weekly-score')
        if success and response.status_code == 200:
            self.log_result("Weekly Alignment Score", True, "Endpoint accessible")
        else:
            self.log_result("Weekly Alignment Score", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test monthly alignment score
        success, response = self.make_request('GET', 'alignment/monthly-score')
        if success and response.status_code == 200:
            self.log_result("Monthly Alignment Score", True, "Endpoint accessible")
        else:
            self.log_result("Monthly Alignment Score", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")

    def test_analytics_dashboard(self):
        """Test analytics dashboard functionality"""
        print("\n📈 Testing Analytics Dashboard...")
        
        if not self.token:
            self.log_result("Analytics Dashboard", False, "No authentication token")
            return
        
        # Test analytics dashboard
        success, response = self.make_request('GET', 'analytics/dashboard', params={'days': 30})
        if success and response.status_code == 200:
            self.log_result("Analytics Dashboard", True, "Endpoint accessible")
        else:
            self.log_result("Analytics Dashboard", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test AI feature usage
        success, response = self.make_request('GET', 'analytics/ai-features', params={'days': 30})
        if success and response.status_code == 200:
            self.log_result("AI Feature Usage Analytics", True, "Endpoint accessible")
        else:
            self.log_result("AI Feature Usage Analytics", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test engagement metrics
        success, response = self.make_request('GET', 'analytics/engagement', params={'days': 30})
        if success and response.status_code == 200:
            self.log_result("User Engagement Metrics", True, "Endpoint accessible")
        else:
            self.log_result("User Engagement Metrics", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")

    def test_core_functionality(self):
        """Test core CRUD functionality"""
        print("\n🏗️ Testing Core Functionality...")
        
        if not self.token:
            self.log_result("Core Functionality", False, "No authentication token")
            return
        
        # Test pillars
        success, response = self.make_request('GET', 'pillars')
        if success and response.status_code == 200:
            self.log_result("Pillars Endpoint", True, "Accessible")
        else:
            self.log_result("Pillars Endpoint", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test areas
        success, response = self.make_request('GET', 'areas')
        if success and response.status_code == 200:
            self.log_result("Areas Endpoint", True, "Accessible")
        else:
            self.log_result("Areas Endpoint", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test projects
        success, response = self.make_request('GET', 'projects')
        if success and response.status_code == 200:
            self.log_result("Projects Endpoint", True, "Accessible")
        else:
            self.log_result("Projects Endpoint", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test tasks
        success, response = self.make_request('GET', 'tasks')
        if success and response.status_code == 200:
            self.log_result("Tasks Endpoint", True, "Accessible")
        else:
            self.log_result("Tasks Endpoint", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test journal
        success, response = self.make_request('GET', 'journal')
        if success and response.status_code == 200:
            self.log_result("Journal Endpoint", True, "Accessible")
        else:
            self.log_result("Journal Endpoint", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")
        
        # Test insights
        success, response = self.make_request('GET', 'insights')
        if success and response.status_code == 200:
            self.log_result("Insights Endpoint", True, "Accessible")
        else:
            self.log_result("Insights Endpoint", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")

    def test_journal_sentiment_integration(self):
        """Test journal entry creation with sentiment analysis"""
        print("\n📝 Testing Journal-Sentiment Integration...")
        
        if not self.token:
            self.log_result("Journal-Sentiment Integration", False, "No authentication token")
            return
        
        # Create a test journal entry
        journal_entry = {
            "title": f"Test Entry - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": "Today was an amazing day! I accomplished so much and feel really positive about my progress. I'm excited about the future and all the opportunities ahead.",
            "mood": "positive",
            "tags": ["test", "sentiment", "positive"]
        }
        
        success, response = self.make_request('POST', 'journal', journal_entry)
        
        if success and response.status_code in [200, 201]:
            try:
                result = response.json()
                entry_id = result.get('id')
                if entry_id:
                    self.log_result("Journal Entry Creation", True, f"Created entry {entry_id}")
                    
                    # Wait a moment for sentiment analysis to process
                    time.sleep(2)
                    
                    # Test sentiment analysis on the created entry
                    success, response = self.make_request('POST', f'sentiment/analyze-entry/{entry_id}')
                    if success and response.status_code == 200:
                        self.log_result("Journal Sentiment Analysis", True, "Sentiment analysis completed")
                    else:
                        self.log_result("Journal Sentiment Analysis", False, 
                                      f"Status: {response.status_code if success else 'Request failed'}")
                else:
                    self.log_result("Journal Entry Creation", False, "No entry ID in response")
            except json.JSONDecodeError:
                self.log_result("Journal Entry Creation", False, "Invalid JSON response")
        else:
            self.log_result("Journal Entry Creation", False, 
                          f"Status: {response.status_code if success else 'Request failed'}")

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting AI Quota and System Integration Tests")
        print(f"📅 Test started at: {datetime.now().isoformat()}")
        print(f"🌐 Testing against: {self.base_url}")
        print(f"👤 Test user: {self.test_email}")
        print("=" * 80)
        
        # Run tests in order
        self.test_health_check()
        
        if self.test_authentication():
            self.test_ai_quota_system()
            self.test_ai_features()
            self.test_sentiment_analysis()
            self.test_semantic_search_rag()
            self.test_alignment_dashboard()
            self.test_analytics_dashboard()
            self.test_core_functionality()
            self.test_journal_sentiment_integration()
        else:
            print("\n❌ Authentication failed - skipping authenticated tests")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Print failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print(f"\n🏁 Test completed at: {datetime.now().isoformat()}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AIQuotaSystemTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())