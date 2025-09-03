#!/usr/bin/env python3
"""
AI Features Verification Test
Tests the recently fixed AI features to ensure they work correctly with quota tracking.

Test Coverage:
1. Sentiment Analysis (/api/sentiment/analyze-text)
2. AI Focus Suggestions (/api/ai/suggest-focus)
3. Goal Breakdown (/api/ai/decompose-project)
4. AI Quota Tracking verification
"""

import requests
import json
import sys
from datetime import datetime
import time

class AIFeaturesVerificationTester:
    def __init__(self, base_url="https://journal-analytics-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.initial_quota = None
        self.current_quota = None

    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}", "PASS")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}", "FAIL")
                try:
                    error_data = response.json()
                    self.log(f"   Error details: {error_data}", "ERROR")
                except:
                    self.log(f"   Response text: {response.text[:200]}", "ERROR")
                return False, {}

        except requests.exceptions.Timeout:
            self.log(f"❌ {name} - Request timed out after 30 seconds", "FAIL")
            return False, {}
        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}", "FAIL")
            return False, {}

    def login(self, email, password):
        """Login and get authentication token"""
        self.log("🔐 Attempting login...")
        success, response = self.run_test(
            "Login",
            "POST",
            "auth/login",
            200,
            data={"email": email, "password": password}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.log("✅ Login successful", "PASS")
            return True
        else:
            self.log("❌ Login failed", "FAIL")
            return False

    def get_ai_quota(self):
        """Get current AI quota information"""
        self.log("📊 Checking AI quota...")
        success, response = self.run_test(
            "Get AI Quota",
            "GET",
            "ai/quota",
            200
        )
        
        if success:
            quota_info = {
                'used': response.get('used', 0),
                'remaining': response.get('remaining', 0),
                'total': response.get('total', 0),
                'tier': response.get('tier', 'unknown')
            }
            self.log(f"   Quota: {quota_info['used']}/{quota_info['total']} used, {quota_info['remaining']} remaining", "INFO")
            return quota_info
        return None

    def test_sentiment_analysis(self):
        """Test sentiment analysis endpoint"""
        self.log("🎭 Testing Sentiment Analysis...")
        
        test_data = {
            "text": "I feel great today! This is an amazing day and I'm so grateful for everything.",
            "title": "Good Day"
        }
        
        success, response = self.run_test(
            "Sentiment Analysis",
            "POST",
            "sentiment/analyze-text",
            200,
            data=test_data
        )
        
        if success:
            # Check if response contains expected sentiment data
            if 'sentiment_category' in response or 'sentiment' in response:
                self.log("   ✅ Sentiment analysis returned valid data", "PASS")
                return True
            else:
                self.log("   ❌ Sentiment analysis response missing expected fields", "FAIL")
                self.log(f"   Response keys: {list(response.keys())}", "INFO")
                return False
        return False

    def test_ai_focus_suggestions(self):
        """Test AI focus suggestions endpoint"""
        self.log("🎯 Testing AI Focus Suggestions...")
        
        success, response = self.run_test(
            "AI Focus Suggestions",
            "GET",
            "ai/suggest-focus",
            200,
            params={"top_n": 3}
        )
        
        if success:
            # Check if response contains task suggestions
            if isinstance(response, dict) and ('tasks' in response or 'priorities' in response or 'suggestions' in response):
                self.log("   ✅ AI focus suggestions returned valid data", "PASS")
                return True
            elif isinstance(response, list):
                self.log("   ✅ AI focus suggestions returned task list", "PASS")
                return True
            else:
                self.log("   ❌ AI focus suggestions response format unexpected", "FAIL")
                self.log(f"   Response type: {type(response)}, keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}", "INFO")
                return False
        return False

    def test_goal_breakdown(self):
        """Test goal breakdown endpoint"""
        self.log("🎯 Testing Goal Breakdown...")
        
        test_data = {
            "project_name": "Get Fit",
            "project_description": "Lose weight and build muscle through consistent exercise and proper nutrition"
        }
        
        success, response = self.run_test(
            "Goal Breakdown",
            "POST",
            "ai/decompose-project",
            200,
            data=test_data
        )
        
        if success:
            # Check if response contains project breakdown data
            if isinstance(response, dict) and ('tasks' in response or 'breakdown' in response or 'project' in response):
                self.log("   ✅ Goal breakdown returned valid data", "PASS")
                return True
            else:
                self.log("   ❌ Goal breakdown response format unexpected", "FAIL")
                self.log(f"   Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}", "INFO")
                return False
        return False

    def verify_quota_consumption(self, initial_quota, final_quota, expected_decrease):
        """Verify that quota was consumed correctly"""
        self.log("📊 Verifying quota consumption...")
        
        if not initial_quota or not final_quota:
            self.log("   ❌ Missing quota data for verification", "FAIL")
            return False
        
        actual_decrease = initial_quota['remaining'] - final_quota['remaining']
        actual_increase = final_quota['used'] - initial_quota['used']
        
        self.log(f"   Initial: {initial_quota['used']}/{initial_quota['total']} used", "INFO")
        self.log(f"   Final: {final_quota['used']}/{final_quota['total']} used", "INFO")
        self.log(f"   Expected decrease: {expected_decrease}, Actual: {actual_increase}", "INFO")
        
        if actual_increase == expected_decrease:
            self.log("   ✅ Quota consumption is correct", "PASS")
            return True
        else:
            self.log(f"   ❌ Quota consumption mismatch. Expected {expected_decrease}, got {actual_increase}", "FAIL")
            return False

def main():
    """Main test execution"""
    print("=" * 60)
    print("🧪 AI FEATURES VERIFICATION TEST")
    print("=" * 60)
    
    tester = AIFeaturesVerificationTester()
    
    # Step 1: Login
    if not tester.login("marc.alleyne@aurumtechnologyltd.com", "password123"):
        print("\n❌ Login failed, cannot proceed with tests")
        return 1
    
    # Step 2: Get initial quota
    tester.log("📊 Getting initial quota...")
    initial_quota = tester.get_ai_quota()
    if not initial_quota:
        print("\n❌ Could not get initial quota, proceeding anyway...")
    
    # Step 3: Test AI Features
    ai_tests_passed = 0
    total_ai_tests = 3
    
    # Test 1: Sentiment Analysis
    if tester.test_sentiment_analysis():
        ai_tests_passed += 1
    
    # Small delay between tests
    time.sleep(1)
    
    # Test 2: AI Focus Suggestions  
    if tester.test_ai_focus_suggestions():
        ai_tests_passed += 1
    
    # Small delay between tests
    time.sleep(1)
    
    # Test 3: Goal Breakdown
    if tester.test_goal_breakdown():
        ai_tests_passed += 1
    
    # Step 4: Get final quota and verify consumption
    tester.log("📊 Getting final quota...")
    final_quota = tester.get_ai_quota()
    
    if initial_quota and final_quota:
        # We expect quota to decrease by the number of successful AI tests
        expected_decrease = ai_tests_passed
        quota_verification_passed = tester.verify_quota_consumption(
            initial_quota, final_quota, expected_decrease
        )
    else:
        tester.log("   ⚠️ Could not verify quota consumption due to missing data", "WARN")
        quota_verification_passed = False
    
    # Final Results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"🔐 Authentication: {'✅ PASS' if tester.token else '❌ FAIL'}")
    print(f"🎭 Sentiment Analysis: {'✅ PASS' if ai_tests_passed >= 1 else '❌ FAIL'}")
    print(f"🎯 AI Focus Suggestions: {'✅ PASS' if ai_tests_passed >= 2 else '❌ FAIL'}")  
    print(f"🎯 Goal Breakdown: {'✅ PASS' if ai_tests_passed == 3 else '❌ FAIL'}")
    print(f"📊 Quota Tracking: {'✅ PASS' if quota_verification_passed else '❌ FAIL'}")
    
    print(f"\n📈 Overall: {tester.tests_passed}/{tester.tests_run} tests passed")
    print(f"🤖 AI Features: {ai_tests_passed}/{total_ai_tests} working correctly")
    
    if initial_quota and final_quota:
        print(f"💰 Quota Usage: {initial_quota['used']} → {final_quota['used']} (used {final_quota['used'] - initial_quota['used']} interactions)")
    
    # Determine exit code
    if ai_tests_passed == total_ai_tests and quota_verification_passed:
        print("\n🎉 ALL AI FEATURES WORKING CORRECTLY!")
        return 0
    else:
        print(f"\n⚠️ {total_ai_tests - ai_tests_passed} AI feature(s) failed or quota tracking issues detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())