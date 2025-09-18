#!/usr/bin/env python3
"""
AI Features Focused Test - Testing Recently Fixed Issues
Tests the specific AI features that were just fixed to verify they work correctly.
"""

import requests
import json
import time
import sys
from datetime import datetime

class AIFeaturesTester:
    def __init__(self, base_url="https://supa-data-explained.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.quota_before = {}
        self.quota_after = {}

    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test with enhanced error reporting"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        self.log(f"   URL: {url}")
        if data:
            self.log(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            
            duration = time.time() - start_time
            self.log(f"   Response time: {duration:.2f}s")
            self.log(f"   Status code: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                self.log(f"   Response preview: {json.dumps(response_data, indent=2)[:500]}...")
            except:
                response_data = {"raw_response": response.text[:500]}
                self.log(f"   Raw response: {response.text[:200]}...")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - {name}")
            else:
                self.log(f"❌ FAILED - {name} - Expected {expected_status}, got {response.status_code}")
                if response.status_code >= 400:
                    self.log(f"   Error details: {response.text}")

            return success, response_data

        except requests.exceptions.Timeout:
            self.log(f"⏰ TIMEOUT - {name} - Request took longer than {timeout}s")
            return False, {"error": "timeout"}
        except Exception as e:
            self.log(f"❌ ERROR - {name} - {str(e)}")
            return False, {"error": str(e)}

    def login(self):
        """Login with test credentials"""
        self.log("🔐 Attempting login...")
        success, response = self.run_test(
            "Login",
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
            self.log(f"✅ Login successful - Token: {self.token[:20]}...")
            return True
        else:
            self.log(f"❌ Login failed - Response: {response}")
            return False

    def get_quota_info(self, label=""):
        """Get current AI quota information"""
        self.log(f"📊 Getting AI quota info {label}...")
        success, response = self.run_test(
            f"AI Quota Check {label}",
            "GET",
            "ai/quota",
            200
        )
        
        if success:
            quota_info = {
                'total': response.get('total', 0),
                'used': response.get('used', 0),
                'remaining': response.get('remaining', 0),
                'tier': response.get('tier', 'unknown'),
                'usage_breakdown': response.get('usage_breakdown', {})
            }
            self.log(f"   Quota: {quota_info['used']}/{quota_info['total']} (Tier: {quota_info['tier']})")
            return quota_info
        return None

    def test_quota_system(self):
        """Test 1: AI Quota System Verification"""
        self.log("\n" + "="*60)
        self.log("TEST 1: AI QUOTA SYSTEM VERIFICATION")
        self.log("="*60)
        
        quota_info = self.get_quota_info("(Initial)")
        if not quota_info:
            self.log("❌ Failed to get quota information")
            return False
            
        # Verify it shows 50 total (Free tier) not 250
        if quota_info['total'] == 50:
            self.log("✅ Quota total is correct: 50 (Free tier)")
            quota_check_passed = True
        else:
            self.log(f"❌ Quota total is incorrect: {quota_info['total']} (Expected: 50)")
            quota_check_passed = False
            
        # Verify tier is 'free'
        if quota_info['tier'] == 'free':
            self.log("✅ User tier is correct: free")
            tier_check_passed = True
        else:
            self.log(f"❌ User tier is incorrect: {quota_info['tier']} (Expected: free)")
            tier_check_passed = False
            
        self.quota_before = quota_info
        return quota_check_passed and tier_check_passed

    def test_goal_breakdown(self):
        """Test 2: Goal Breakdown (CRITICAL - Just Fixed)"""
        self.log("\n" + "="*60)
        self.log("TEST 2: GOAL BREAKDOWN (PROJECT DECOMPOSITION)")
        self.log("="*60)
        
        quota_before = self.get_quota_info("(Before Goal Breakdown)")
        
        # Test the /api/ai/decompose-project endpoint with 25 second timeout
        success, response = self.run_test(
            "Goal Breakdown - Learn Spanish",
            "POST",
            "ai/decompose-project",
            200,
            data={
                "project_name": "Learn Spanish",
                "project_description": "Become conversational",
                "template_type": "learning"
            },
            timeout=30  # 30 second timeout to test the 25 second backend limit
        )
        
        quota_after = self.get_quota_info("(After Goal Breakdown)")
        
        if success:
            # Verify response structure
            has_breakdown = 'breakdown' in response or 'tasks' in response or 'milestones' in response
            has_ai_content = any(key in response for key in ['ai_insights', 'coaching_message', 'recommendations'])
            
            self.log(f"   Has breakdown structure: {has_breakdown}")
            self.log(f"   Has AI content: {has_ai_content}")
            
            # Verify quota consumption
            if quota_before and quota_after:
                quota_consumed = quota_after['used'] - quota_before['used']
                self.log(f"   Quota consumed: {quota_consumed}")
                if quota_consumed == 1:
                    self.log("✅ Quota consumption is correct (1 interaction)")
                    quota_consumption_ok = True
                else:
                    self.log(f"❌ Quota consumption is incorrect: {quota_consumed} (Expected: 1)")
                    quota_consumption_ok = False
            else:
                quota_consumption_ok = False
                
            return success and has_breakdown and quota_consumption_ok
        
        return False

    def test_sentiment_analysis(self):
        """Test 3: Sentiment Analysis (Just Fixed)"""
        self.log("\n" + "="*60)
        self.log("TEST 3: SENTIMENT ANALYSIS")
        self.log("="*60)
        
        quota_before = self.get_quota_info("(Before Sentiment Analysis)")
        
        # Test with optional title attribute
        success, response = self.run_test(
            "Sentiment Analysis - Good Day",
            "POST",
            "sentiment/analyze-text",
            200,
            data={
                "text": "I feel amazing today!",
                "title": "Good Day"
            }
        )
        
        quota_after = self.get_quota_info("(After Sentiment Analysis)")
        
        if success:
            # Verify response structure
            has_sentiment = 'sentiment' in response or 'sentiment_score' in response
            has_analysis = 'analysis' in response or 'emotional_analysis' in response
            
            self.log(f"   Has sentiment data: {has_sentiment}")
            self.log(f"   Has analysis: {has_analysis}")
            
            # Verify quota consumption
            if quota_before and quota_after:
                quota_consumed = quota_after['used'] - quota_before['used']
                self.log(f"   Quota consumed: {quota_consumed}")
                if quota_consumed == 1:
                    self.log("✅ Quota consumption is correct (1 interaction)")
                    quota_consumption_ok = True
                else:
                    self.log(f"❌ Quota consumption is incorrect: {quota_consumed} (Expected: 1)")
                    quota_consumption_ok = False
            else:
                quota_consumption_ok = False
                
            return success and (has_sentiment or has_analysis) and quota_consumption_ok
        
        return False

    def test_ai_focus_suggestions(self):
        """Test 4: AI Focus Suggestions (Just Fixed)"""
        self.log("\n" + "="*60)
        self.log("TEST 4: AI FOCUS SUGGESTIONS")
        self.log("="*60)
        
        quota_before = self.get_quota_info("(Before Focus Suggestions)")
        
        # Test /api/ai/suggest-focus?top_n=5
        success, response = self.run_test(
            "AI Focus Suggestions",
            "GET",
            "ai/suggest-focus?top_n=5",
            200
        )
        
        quota_after = self.get_quota_info("(After Focus Suggestions)")
        
        if success:
            # Verify response structure
            has_suggestions = 'suggestions' in response or 'priorities' in response or 'tasks' in response
            has_coaching = 'coaching_message' in response or 'ai_insights' in response
            
            self.log(f"   Has suggestions: {has_suggestions}")
            self.log(f"   Has coaching messages: {has_coaching}")
            
            # Verify quota consumption
            if quota_before and quota_after:
                quota_consumed = quota_after['used'] - quota_before['used']
                self.log(f"   Quota consumed: {quota_consumed}")
                if quota_consumed == 1:
                    self.log("✅ Quota consumption is correct (1 interaction)")
                    quota_consumption_ok = True
                else:
                    self.log(f"❌ Quota consumption is incorrect: {quota_consumed} (Expected: 1)")
                    quota_consumption_ok = False
            else:
                quota_consumption_ok = False
                
            return success and has_suggestions and quota_consumption_ok
        
        return False

    def test_quota_consumption_verification(self):
        """Test 5: Overall Quota Consumption Verification"""
        self.log("\n" + "="*60)
        self.log("TEST 5: QUOTA CONSUMPTION VERIFICATION")
        self.log("="*60)
        
        final_quota = self.get_quota_info("(Final)")
        
        if self.quota_before and final_quota:
            total_consumed = final_quota['used'] - self.quota_before['used']
            self.log(f"   Initial quota: {self.quota_before['used']}/{self.quota_before['total']}")
            self.log(f"   Final quota: {final_quota['used']}/{final_quota['total']}")
            self.log(f"   Total consumed: {total_consumed}")
            
            # We ran 3 AI features, so should have consumed 3 quota
            expected_consumption = 3
            if total_consumed == expected_consumption:
                self.log(f"✅ Total quota consumption is correct: {total_consumed}")
                return True
            else:
                self.log(f"❌ Total quota consumption is incorrect: {total_consumed} (Expected: {expected_consumption})")
                return False
        
        return False

    def run_all_tests(self):
        """Run all AI feature tests"""
        self.log("🚀 Starting AI Features Focused Test Suite")
        self.log(f"   Target: {self.base_url}")
        self.log(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Login first
        if not self.login():
            self.log("❌ Login failed, cannot proceed with tests")
            return False
        
        # Run all tests
        test_results = []
        
        test_results.append(self.test_quota_system())
        test_results.append(self.test_goal_breakdown())
        test_results.append(self.test_sentiment_analysis())
        test_results.append(self.test_ai_focus_suggestions())
        test_results.append(self.test_quota_consumption_verification())
        
        # Summary
        self.log("\n" + "="*60)
        self.log("TEST SUMMARY")
        self.log("="*60)
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        self.log(f"📊 Tests passed: {passed_tests}/{total_tests}")
        self.log(f"📊 API calls made: {self.tests_passed}/{self.tests_run}")
        
        if passed_tests == total_tests:
            self.log("🎉 ALL AI FEATURES WORKING CORRECTLY!")
            return True
        else:
            self.log("⚠️  SOME AI FEATURES NEED ATTENTION")
            return False

def main():
    tester = AIFeaturesTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())