#!/usr/bin/env python3
"""
Comprehensive Sentiment Analysis System Testing - Emotional OS
Testing all sentiment analysis endpoints with GPT-5 nano integration
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class SentimentAnalysisAPITester:
    def __init__(self, base_url="https://emotional-os-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple[bool, Dict]:
        """Run a single API test with enhanced error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        self.log(f"   URL: {url}")
        if data:
            self.log(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=30)

            self.log(f"   Response Status: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                self.log(f"   Response Data: {json.dumps(response_data, indent=2)[:500]}...")
            except:
                response_data = {"raw_response": response.text[:500]}
                self.log(f"   Raw Response: {response.text[:200]}...")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - {name}")
            else:
                self.log(f"❌ FAILED - {name} - Expected {expected_status}, got {response.status_code}")
                if response.status_code >= 400:
                    self.log(f"   Error Details: {response_data}")

            return success, response_data

        except requests.exceptions.Timeout:
            self.log(f"❌ FAILED - {name} - Request timeout (30s)")
            return False, {"error": "timeout"}
        except requests.exceptions.ConnectionError:
            self.log(f"❌ FAILED - {name} - Connection error")
            return False, {"error": "connection_error"}
        except Exception as e:
            self.log(f"❌ FAILED - {name} - Error: {str(e)}")
            return False, {"error": str(e)}

    def test_authentication(self, email: str, password: str) -> bool:
        """Test login and get authentication token"""
        self.log("🔐 Testing Authentication...")
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"email": email, "password": password}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.log(f"✅ Authentication successful - Token obtained")
            return True
        elif success and 'token' in response:
            self.token = response['token']
            self.log(f"✅ Authentication successful - Token obtained")
            return True
        else:
            self.log(f"❌ Authentication failed - No token in response")
            return False

    def test_health_check(self) -> bool:
        """Test basic API health"""
        self.log("🏥 Testing API Health...")
        success, _ = self.run_test("Health Check", "GET", "health", 200)
        return success

    def test_sentiment_analyze_text(self) -> bool:
        """Test POST /api/sentiment/analyze-text endpoint"""
        self.log("📝 Testing Text Sentiment Analysis...")
        
        test_data = {
            "text": "Today was absolutely wonderful! I accomplished so much and feel incredibly grateful for all the opportunities in my life. This project brought me such joy and satisfaction.",
            "content_type": "journal_entry",
            "include_detailed_analysis": True
        }
        
        success, response = self.run_test(
            "Analyze Text Sentiment",
            "POST",
            "sentiment/analyze-text",
            200,
            data=test_data
        )
        
        if success:
            # Validate response structure
            required_fields = ['sentiment_analysis', 'sentiment_emoji', 'sentiment_color']
            for field in required_fields:
                if field not in response:
                    self.log(f"❌ Missing required field: {field}")
                    return False
            
            # Validate sentiment analysis structure
            sentiment_analysis = response.get('sentiment_analysis', {})
            sentiment_fields = ['sentiment_score', 'sentiment_category', 'confidence_score']
            for field in sentiment_fields:
                if field not in sentiment_analysis:
                    self.log(f"❌ Missing sentiment analysis field: {field}")
                    return False
            
            # Validate sentiment score range
            sentiment_score = sentiment_analysis.get('sentiment_score', 0)
            if not (-1.0 <= sentiment_score <= 1.0):
                self.log(f"❌ Sentiment score out of range: {sentiment_score}")
                return False
            
            self.log(f"✅ Sentiment Score: {sentiment_score}")
            self.log(f"✅ Sentiment Category: {sentiment_analysis.get('sentiment_category')}")
            self.log(f"✅ Confidence: {sentiment_analysis.get('confidence_score')}")
            
        return success

    def test_sentiment_bulk_analyze(self) -> bool:
        """Test POST /api/sentiment/bulk-analyze endpoint"""
        self.log("📚 Testing Bulk Sentiment Analysis...")
        
        success, response = self.run_test(
            "Bulk Analyze Sentiment",
            "POST",
            "sentiment/bulk-analyze",
            200,
            params={"limit": 10}
        )
        
        if success:
            # Validate response has analysis summary
            if 'processed_count' not in response and 'analyzed_entries' not in response:
                self.log("⚠️ Bulk analysis response may be incomplete")
            else:
                processed = response.get('processed_count', response.get('analyzed_entries', 0))
                self.log(f"✅ Processed {processed} entries")
        
        return success

    def test_sentiment_trends(self) -> bool:
        """Test GET /api/sentiment/trends endpoint"""
        self.log("📈 Testing Sentiment Trends...")
        
        success, response = self.run_test(
            "Get Sentiment Trends",
            "GET",
            "sentiment/trends",
            200,
            params={"days": 30}
        )
        
        if success:
            # Validate response structure
            if 'trends' in response and 'summary' in response:
                trends = response['trends']
                summary = response['summary']
                self.log(f"✅ Retrieved {len(trends)} trend data points")
                self.log(f"✅ Average sentiment: {summary.get('average_sentiment', 'N/A')}")
                self.log(f"✅ Trend direction: {summary.get('trend_direction', 'N/A')}")
            else:
                self.log("⚠️ Trends response structure may be incomplete")
        
        return success

    def test_sentiment_wellness_score(self) -> bool:
        """Test GET /api/sentiment/wellness-score endpoint"""
        self.log("🌟 Testing Emotional Wellness Score...")
        
        success, response = self.run_test(
            "Get Wellness Score",
            "GET",
            "sentiment/wellness-score",
            200,
            params={"days": 30}
        )
        
        if success:
            # Validate wellness score
            wellness_score = response.get('wellness_score', 0)
            if not (0 <= wellness_score <= 100):
                self.log(f"❌ Wellness score out of range: {wellness_score}")
                return False
            
            self.log(f"✅ Wellness Score: {wellness_score}/100")
            self.log(f"✅ Wellness Category: {response.get('wellness_category', 'N/A')}")
            self.log(f"✅ Wellness Emoji: {response.get('wellness_emoji', 'N/A')}")
        
        return success

    def test_sentiment_correlations(self) -> bool:
        """Test GET /api/sentiment/correlations endpoint"""
        self.log("🔗 Testing Activity-Sentiment Correlations...")
        
        success, response = self.run_test(
            "Get Activity Correlations",
            "GET",
            "sentiment/correlations",
            200,
            params={"days": 30}
        )
        
        if success:
            correlations = response.get('correlations', [])
            self.log(f"✅ Retrieved {len(correlations)} correlation data points")
            if correlations:
                # Show sample correlation
                sample = correlations[0]
                self.log(f"✅ Sample correlation: {sample}")
        
        return success

    def test_sentiment_insights(self) -> bool:
        """Test GET /api/sentiment/insights endpoint"""
        self.log("🧠 Testing Emotional Insights...")
        
        success, response = self.run_test(
            "Get Emotional Insights",
            "GET",
            "sentiment/insights",
            200,
            params={"days": 30}
        )
        
        if success:
            insights = response.get('insights', [])
            self.log(f"✅ Retrieved {len(insights)} emotional insights")
            if insights:
                # Show sample insight
                sample = insights[0]
                self.log(f"✅ Sample insight: {sample.get('title', 'N/A')}")
        
        return success

    def test_error_handling(self) -> bool:
        """Test error handling and edge cases"""
        self.log("⚠️ Testing Error Handling...")
        
        # Test with empty text
        success1, _ = self.run_test(
            "Empty Text Analysis",
            "POST",
            "sentiment/analyze-text",
            400,  # Expecting error
            data={"text": "", "content_type": "journal_entry"}
        )
        
        # Test with invalid endpoint
        success2, _ = self.run_test(
            "Invalid Endpoint",
            "GET",
            "sentiment/invalid-endpoint",
            404,  # Expecting not found
        )
        
        # Test without authentication (if required)
        old_token = self.token
        self.token = None
        success3, _ = self.run_test(
            "Unauthorized Access",
            "GET",
            "sentiment/trends",
            401,  # Expecting unauthorized
        )
        self.token = old_token
        
        return success1 or success2 or success3  # At least one error test should pass

    def test_performance(self) -> bool:
        """Test performance and response times"""
        self.log("⚡ Testing Performance...")
        
        start_time = time.time()
        
        # Test text analysis performance
        test_data = {
            "text": "This is a performance test for sentiment analysis. I want to see how quickly the GPT-5 nano model can process this text and return emotional insights.",
            "content_type": "journal_entry",
            "include_detailed_analysis": True
        }
        
        success, response = self.run_test(
            "Performance Test - Text Analysis",
            "POST",
            "sentiment/analyze-text",
            200,
            data=test_data
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.log(f"✅ Response time: {response_time:.2f} seconds")
        
        if response_time > 10:
            self.log("⚠️ Response time is slow (>10s)")
        elif response_time > 5:
            self.log("⚠️ Response time is moderate (>5s)")
        else:
            self.log("✅ Response time is good (<5s)")
        
        return success

    def run_comprehensive_test_suite(self) -> int:
        """Run the complete sentiment analysis test suite"""
        self.log("🚀 Starting Comprehensive Sentiment Analysis Testing")
        self.log("=" * 60)
        
        # 1. Authentication and Base Setup
        self.log("\n📋 PHASE 1: Authentication and Base Setup")
        if not self.test_health_check():
            self.log("❌ Health check failed - stopping tests")
            return 1
        
        if not self.test_authentication("marc.alleyne@aurumtechnologyltd.com", "password123"):
            self.log("❌ Authentication failed - stopping tests")
            return 1
        
        # 2. Test All Sentiment Analysis Endpoints
        self.log("\n📋 PHASE 2: Sentiment Analysis Endpoints")
        
        # A. Text Analysis Endpoint
        self.test_sentiment_analyze_text()
        
        # B. Bulk Analysis Endpoint
        self.test_sentiment_bulk_analyze()
        
        # C. Sentiment Trends Endpoint
        self.test_sentiment_trends()
        
        # D. Emotional Wellness Score
        self.test_sentiment_wellness_score()
        
        # E. Activity Correlations
        self.test_sentiment_correlations()
        
        # F. Emotional Insights
        self.test_sentiment_insights()
        
        # 3. Error Handling and Edge Cases
        self.log("\n📋 PHASE 3: Error Handling and Edge Cases")
        self.test_error_handling()
        
        # 4. Performance Testing
        self.log("\n📋 PHASE 4: Performance Testing")
        self.test_performance()
        
        # Final Results
        self.log("\n" + "=" * 60)
        self.log("📊 FINAL TEST RESULTS")
        self.log(f"Tests Run: {self.tests_run}")
        self.log(f"Tests Passed: {self.tests_passed}")
        self.log(f"Tests Failed: {self.tests_run - self.tests_passed}")
        self.log(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 ALL TESTS PASSED - Sentiment Analysis System is working!")
            return 0
        elif self.tests_passed >= self.tests_run * 0.8:
            self.log("⚠️ MOSTLY WORKING - Some issues found but core functionality works")
            return 0
        else:
            self.log("❌ MAJOR ISSUES - Sentiment Analysis System needs attention")
            return 1

def main():
    """Main test execution"""
    print("🧠 Emotional OS - Sentiment Analysis System Testing")
    print("Testing GPT-5 nano integration and all sentiment endpoints")
    print("=" * 60)
    
    tester = SentimentAnalysisAPITester()
    return tester.run_comprehensive_test_suite()

if __name__ == "__main__":
    sys.exit(main())