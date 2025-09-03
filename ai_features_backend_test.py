#!/usr/bin/env python3
"""
Comprehensive AI Features Backend Test for Aurum Life
Testing all AI endpoints with quota system verification
"""

import requests
import json
import sys
from datetime import datetime
import time

class AIFeaturesBackendTester:
    def __init__(self, base_url="https://journal-analytics-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        
        print(f"🚀 Starting AI Features Backend Test")
        print(f"📍 Base URL: {self.base_url}")
        print(f"👤 Test User: marc.alleyne@aurumtechnologyltd.com")
        print("=" * 60)

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test with detailed logging"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   📡 {method} {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"   ✅ PASSED - Status: {response.status_code}")
                
                # Log response data for AI endpoints
                try:
                    response_data = response.json()
                    if 'quota' in name.lower():
                        print(f"   📊 Quota Info: {response_data.get('used', 'N/A')}/{response_data.get('total', 'N/A')} ({response_data.get('tier', 'N/A')} tier)")
                    elif 'ai' in name.lower():
                        print(f"   🤖 AI Response Keys: {list(response_data.keys())}")
                except:
                    pass
                    
                return True, response.json() if response.content else {}
            else:
                print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📝 Error: {error_data.get('detail', 'No error details')}")
                except:
                    print(f"   📝 Raw Response: {response.text[:200]}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT - Request took longer than 30 seconds")
            return False, {}
        except Exception as e:
            print(f"   💥 EXCEPTION - {str(e)}")
            return False, {}

    def test_authentication(self):
        """Test user authentication"""
        print(f"\n{'='*20} AUTHENTICATION TESTS {'='*20}")
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": "marc.alleyne@aurumtechnologyltd.com",
                "password": "password123"
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response.get('user', {}).get('id')
            print(f"   🔑 Token acquired successfully")
            print(f"   👤 User ID: {self.user_id}")
            return True
        else:
            print(f"   🚫 Authentication failed - cannot proceed with AI tests")
            return False

    def test_ai_quota_system(self):
        """Test AI quota system endpoints"""
        print(f"\n{'='*20} AI QUOTA SYSTEM TESTS {'='*20}")
        
        # Test quota endpoint
        success, quota_data = self.run_test(
            "AI Quota Check",
            "GET",
            "ai/quota",
            200
        )
        
        if success:
            print(f"   📈 Initial Quota: {quota_data.get('used', 'N/A')}/{quota_data.get('total', 'N/A')}")
            print(f"   🎯 Tier: {quota_data.get('tier', 'N/A')}")
            print(f"   ⏰ Resets: {quota_data.get('resets_at', 'N/A')}")
            
            # Verify it's real quota, not hardcoded
            if quota_data.get('total') == 250 and quota_data.get('used') == 250:
                print(f"   ⚠️  WARNING: Quota appears to be hardcoded (250/250)")
                return False
            elif quota_data.get('total') == 50:  # Free tier
                print(f"   ✅ Real quota detected - Free tier (50 interactions)")
                return True
            else:
                print(f"   ✅ Real quota detected - Custom tier")
                return True
        
        return False

    def test_goal_planner_decomposition(self):
        """Test Goal Planner (Goal Decomposition) - Recently Fixed"""
        print(f"\n{'='*20} GOAL PLANNER TESTS {'='*20}")
        
        # Test project decomposition
        test_goal = {
            "project_name": "Learn Spanish",
            "project_description": "I want to become conversational in Spanish within 6 months for travel and career opportunities",
            "template_type": "learning"
        }
        
        success, response = self.run_test(
            "Goal Decomposition (Recently Fixed)",
            "POST",
            "ai/decompose-project",
            200,
            data=test_goal
        )
        
        if success:
            print(f"   🎯 Goal breakdown generated successfully")
            print(f"   📋 Response keys: {list(response.keys())}")
            
            # Check for expected structure
            if 'project_structure' in response or 'breakdown' in response or 'tasks' in response:
                print(f"   ✅ Goal decomposition structure looks correct")
                return True
            else:
                print(f"   ⚠️  Goal decomposition response structure unexpected")
                return False
        
        return False

    def test_ai_quick_actions(self):
        """Test AI Quick Actions (Focus Suggestions, Task Why Statements)"""
        print(f"\n{'='*20} AI QUICK ACTIONS TESTS {'='*20}")
        
        # Test AI Focus Suggestions
        success1, response1 = self.run_test(
            "AI Focus Suggestions",
            "GET",
            "ai/suggest-focus?top_n=5&include_reasoning=true",
            200
        )
        
        if success1:
            print(f"   🎯 Focus suggestions generated")
            print(f"   📊 Response keys: {list(response1.keys())}")
        
        # Test Task Why Statements
        success2, response2 = self.run_test(
            "Task Why Statements",
            "GET",
            "ai/task-why-statements",
            200
        )
        
        if success2:
            print(f"   💭 Why statements generated")
            print(f"   📊 Response keys: {list(response2.keys())}")
        
        return success1 and success2

    def test_sentiment_analysis(self):
        """Test Sentiment Analysis for Journal entries"""
        print(f"\n{'='*20} SENTIMENT ANALYSIS TESTS {'='*20}")
        
        # Test text sentiment analysis
        test_text = {
            "text": "I had an amazing day today! I completed my project and felt really accomplished. The weather was beautiful and I spent time with friends.",
            "title": "Great Day"
        }
        
        success, response = self.run_test(
            "Sentiment Analysis",
            "POST",
            "sentiment/analyze-text",
            200,
            data=test_text
        )
        
        if success:
            print(f"   😊 Sentiment analysis completed")
            print(f"   📊 Response keys: {list(response.keys())}")
            
            # Check for sentiment data
            if 'sentiment' in str(response).lower() or 'emotion' in str(response).lower():
                print(f"   ✅ Sentiment data detected in response")
                return True
            else:
                print(f"   ⚠️  No sentiment data found in response")
                return False
        
        return False

    def test_insights_endpoints(self):
        """Test My AI Insights endpoints"""
        print(f"\n{'='*20} AI INSIGHTS TESTS {'='*20}")
        
        # Test general insights
        success1, response1 = self.run_test(
            "User Insights",
            "GET",
            "insights",
            200
        )
        
        if success1:
            print(f"   💡 Insights retrieved")
            print(f"   📊 Response keys: {list(response1.keys())}")
            
            # Check if insights are personalized (not generic)
            insights_str = str(response1).lower()
            if 'balanced global' in insights_str and 'task completion opportunity' not in insights_str:
                print(f"   ⚠️  WARNING: Insights appear to be generic, not personalized")
                return False
            else:
                print(f"   ✅ Insights appear to be personalized")
                return True
        
        return False

    def test_alignment_dashboard(self):
        """Test Alignment Dashboard with HRM insights"""
        print(f"\n{'='*20} ALIGNMENT DASHBOARD TESTS {'='*20}")
        
        success, response = self.run_test(
            "Alignment Dashboard",
            "GET",
            "alignment/dashboard",
            200
        )
        
        if success:
            print(f"   📊 Alignment dashboard loaded")
            print(f"   📈 Response keys: {list(response.keys())}")
            return True
        
        return False

    def test_semantic_search(self):
        """Test Semantic Search functionality"""
        print(f"\n{'='*20} SEMANTIC SEARCH TESTS {'='*20}")
        
        success, response = self.run_test(
            "Semantic Search",
            "GET",
            "semantic/search?query=productivity&limit=5",
            200
        )
        
        if success:
            print(f"   🔍 Semantic search completed")
            print(f"   📊 Response keys: {list(response.keys())}")
            results = response.get('results', [])
            print(f"   📝 Found {len(results)} results")
            return True
        
        return False

    def test_basic_endpoints(self):
        """Test basic endpoints to ensure user has data"""
        print(f"\n{'='*20} BASIC DATA TESTS {'='*20}")
        
        endpoints = [
            ("Pillars", "pillars"),
            ("Areas", "areas"), 
            ("Projects", "projects"),
            ("Tasks", "tasks"),
            ("Journal", "journal")
        ]
        
        all_success = True
        for name, endpoint in endpoints:
            success, response = self.run_test(
                f"Get {name}",
                "GET",
                endpoint,
                200
            )
            
            if success:
                data_count = len(response) if isinstance(response, list) else len(response.get('data', []))
                print(f"   📊 {name}: {data_count} items")
            else:
                all_success = False
        
        return all_success

    def run_comprehensive_test(self):
        """Run all AI feature tests"""
        start_time = datetime.now()
        print(f"🚀 Starting Comprehensive AI Features Test at {start_time}")
        
        # Step 1: Authentication
        if not self.test_authentication():
            print(f"\n❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Step 2: Basic data check
        self.test_basic_endpoints()
        
        # Step 3: AI Quota System (Critical)
        quota_success = self.test_ai_quota_system()
        
        # Step 4: Goal Planner (Recently Fixed)
        goal_success = self.test_goal_planner_decomposition()
        
        # Step 5: AI Quick Actions
        actions_success = self.test_ai_quick_actions()
        
        # Step 6: Sentiment Analysis
        sentiment_success = self.test_sentiment_analysis()
        
        # Step 7: AI Insights
        insights_success = self.test_insights_endpoints()
        
        # Step 8: Alignment Dashboard
        alignment_success = self.test_alignment_dashboard()
        
        # Step 9: Semantic Search
        search_success = self.test_semantic_search()
        
        # Final Results
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print(f"🏁 AI FEATURES TEST COMPLETE")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"📊 Tests: {self.tests_passed}/{self.tests_run} passed ({(self.tests_passed/self.tests_run*100):.1f}%)")
        print(f"{'='*60}")
        
        # Critical AI Features Summary
        critical_features = {
            "AI Quota System": quota_success,
            "Goal Decomposition (Recently Fixed)": goal_success,
            "AI Quick Actions": actions_success,
            "Sentiment Analysis": sentiment_success,
            "AI Insights": insights_success
        }
        
        print(f"\n🎯 CRITICAL AI FEATURES STATUS:")
        for feature, status in critical_features.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature}")
        
        # Return overall success
        critical_success_count = sum(critical_features.values())
        overall_success = critical_success_count >= 4  # At least 4/5 critical features working
        
        if overall_success:
            print(f"\n🎉 OVERALL: AI Features are working well!")
        else:
            print(f"\n⚠️  OVERALL: Some critical AI features need attention")
        
        return overall_success

def main():
    tester = AIFeaturesBackendTester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())