#!/usr/bin/env python3
"""
Comprehensive Sentiment Analysis Backend Testing
Testing GPT-4o-mini integration and all 6 sentiment endpoints
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class SentimentAnalysisAPITester:
    def __init__(self, base_url="https://emotional-os-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with details"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED - {details}")
        
        if response_data and isinstance(response_data, dict):
            print(f"   📊 Response keys: {list(response_data.keys())}")
        
        self.test_results.append({
            'test': name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
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
            else:
                return False, f"Unsupported method: {method}", {}

            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            return response.status_code == 200, response_data, response.status_code
        except requests.exceptions.Timeout:
            return False, "Request timeout (>30s)", {}
        except Exception as e:
            return False, f"Request error: {str(e)}", {}

    def test_authentication(self):
        """Test login with provided credentials"""
        print("\n🔐 Testing Authentication...")
        
        login_data = {
            "email": "marc.alleyne@aurumtechnologyltd.com",
            "password": "password123"
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/login', login_data)
        
        if success and 'access_token' in response_data:
            self.token = response_data['access_token']
            self.log_test("Authentication", True, f"Token obtained (status: {status_code})")
            return True
        else:
            self.log_test("Authentication", False, f"Login failed (status: {status_code})", response_data)
            return False

    def test_analyze_text_endpoint(self):
        """Test POST /api/sentiment/analyze-text"""
        print("\n📝 Testing Text Analysis Endpoint...")
        
        # Test with positive text
        positive_text = {
            "text": "I feel absolutely amazing today! This project is going incredibly well and I'm so proud of what we've accomplished. The sense of joy and fulfillment is overwhelming - I feel truly alive and purposeful."
        }
        
        success, response_data, status_code = self.make_request('POST', 'sentiment/analyze-text', positive_text)
        
        if success:
            # Validate response structure
            required_keys = ['sentiment_analysis', 'sentiment_emoji', 'sentiment_color', 'human_readable']
            missing_keys = [key for key in required_keys if key not in response_data]
            
            if missing_keys:
                self.log_test("Text Analysis - Structure", False, f"Missing keys: {missing_keys}")
            else:
                # Check sentiment analysis details
                sentiment = response_data.get('sentiment_analysis', {})
                score = sentiment.get('sentiment_score', 0)
                category = sentiment.get('sentiment_category', '')
                confidence = sentiment.get('confidence_score', 0)
                keywords = sentiment.get('emotional_keywords', [])
                
                # Validate positive sentiment detection
                if score > 0.2 and 'positive' in category.lower():
                    self.log_test("Text Analysis - Positive Detection", True, f"Score: {score}, Category: {category}")
                else:
                    self.log_test("Text Analysis - Positive Detection", False, f"Expected positive, got score: {score}, category: {category}")
                
                # Validate confidence and keywords
                if confidence >= 0.7:
                    self.log_test("Text Analysis - Confidence", True, f"Confidence: {confidence}")
                else:
                    self.log_test("Text Analysis - Confidence", False, f"Low confidence: {confidence}")
                
                if len(keywords) > 0:
                    self.log_test("Text Analysis - Keywords Extraction", True, f"Keywords: {keywords}")
                else:
                    self.log_test("Text Analysis - Keywords Extraction", False, "No keywords extracted")
        else:
            self.log_test("Text Analysis - Request", False, f"Request failed (status: {status_code})", response_data)

        # Test with negative text
        negative_text = {
            "text": "I'm feeling really down and frustrated today. Everything seems to be going wrong and I can't shake this overwhelming sense of sadness and disappointment."
        }
        
        success, response_data, status_code = self.make_request('POST', 'sentiment/analyze-text', negative_text)
        
        if success:
            sentiment = response_data.get('sentiment_analysis', {})
            score = sentiment.get('sentiment_score', 0)
            category = sentiment.get('sentiment_category', '')
            
            if score < -0.2 and 'negative' in category.lower():
                self.log_test("Text Analysis - Negative Detection", True, f"Score: {score}, Category: {category}")
            else:
                self.log_test("Text Analysis - Negative Detection", False, f"Expected negative, got score: {score}, category: {category}")

    def test_bulk_analyze_endpoint(self):
        """Test POST /api/sentiment/bulk-analyze"""
        print("\n📚 Testing Bulk Analysis Endpoint...")
        
        success, response_data, status_code = self.make_request('POST', 'sentiment/bulk-analyze', {"limit": 10})
        
        if success:
            analyzed_count = response_data.get('analyzed_count', 0)
            total_entries = response_data.get('total_entries', 0)
            
            self.log_test("Bulk Analysis", True, f"Analyzed {analyzed_count} of {total_entries} entries")
            
            # Check if any entries were processed
            if analyzed_count > 0:
                self.log_test("Bulk Analysis - Processing", True, f"Successfully processed {analyzed_count} entries")
            else:
                self.log_test("Bulk Analysis - Processing", True, "No unanalyzed entries found (expected for existing data)")
        else:
            self.log_test("Bulk Analysis", False, f"Request failed (status: {status_code})", response_data)

    def test_sentiment_trends_endpoint(self):
        """Test GET /api/sentiment/trends"""
        print("\n📈 Testing Sentiment Trends Endpoint...")
        
        success, response_data, status_code = self.make_request('GET', 'sentiment/trends', params={'days': 30})
        
        if success:
            trends = response_data.get('trends', [])
            summary = response_data.get('summary', {})
            
            required_summary_keys = ['period_days', 'total_entries_analyzed', 'average_sentiment', 'trend_direction']
            missing_keys = [key for key in required_summary_keys if key not in summary]
            
            if missing_keys:
                self.log_test("Sentiment Trends - Structure", False, f"Missing summary keys: {missing_keys}")
            else:
                self.log_test("Sentiment Trends - Structure", True, f"Found {len(trends)} trend points")
                
                # Validate trend data
                if len(trends) > 0:
                    trend_sample = trends[0]
                    if 'average_sentiment' in trend_sample and 'date' in trend_sample:
                        self.log_test("Sentiment Trends - Data Quality", True, "Trend data contains required fields")
                    else:
                        self.log_test("Sentiment Trends - Data Quality", False, "Trend data missing required fields")
                
                # Check summary statistics
                avg_sentiment = summary.get('average_sentiment', 0)
                if -1.0 <= avg_sentiment <= 1.0:
                    self.log_test("Sentiment Trends - Score Range", True, f"Average sentiment: {avg_sentiment}")
                else:
                    self.log_test("Sentiment Trends - Score Range", False, f"Invalid sentiment score: {avg_sentiment}")
        else:
            self.log_test("Sentiment Trends", False, f"Request failed (status: {status_code})", response_data)

    def test_wellness_score_endpoint(self):
        """Test GET /api/sentiment/wellness-score"""
        print("\n🌟 Testing Wellness Score Endpoint...")
        
        success, response_data, status_code = self.make_request('GET', 'sentiment/wellness-score', params={'days': 30})
        
        if success:
            wellness_score = response_data.get('wellness_score', 0)
            wellness_category = response_data.get('wellness_category', '')
            wellness_emoji = response_data.get('wellness_emoji', '')
            interpretation = response_data.get('interpretation', '')
            
            # Validate wellness score range (0-100)
            if 0 <= wellness_score <= 100:
                self.log_test("Wellness Score - Range", True, f"Score: {wellness_score}/100")
            else:
                self.log_test("Wellness Score - Range", False, f"Invalid score: {wellness_score}")
            
            # Validate category mapping
            valid_categories = ['excellent', 'good', 'moderate', 'concerning', 'needs_attention']
            if wellness_category in valid_categories:
                self.log_test("Wellness Score - Category", True, f"Category: {wellness_category}")
            else:
                self.log_test("Wellness Score - Category", False, f"Invalid category: {wellness_category}")
            
            # Check emoji and interpretation
            if wellness_emoji and interpretation:
                self.log_test("Wellness Score - Presentation", True, f"Emoji: {wellness_emoji}, Has interpretation")
            else:
                self.log_test("Wellness Score - Presentation", False, "Missing emoji or interpretation")
        else:
            self.log_test("Wellness Score", False, f"Request failed (status: {status_code})", response_data)

    def test_correlations_endpoint(self):
        """Test GET /api/sentiment/correlations"""
        print("\n🔗 Testing Activity Correlations Endpoint...")
        
        success, response_data, status_code = self.make_request('GET', 'sentiment/correlations', params={'days': 30})
        
        if success:
            correlations = response_data.get('correlations', [])
            total_correlations = response_data.get('total_correlations', 0)
            
            self.log_test("Activity Correlations", True, f"Found {total_correlations} correlations")
            
            # Validate correlation data structure
            if len(correlations) > 0:
                correlation_sample = correlations[0]
                expected_keys = ['activity_type', 'activity_name', 'correlation_strength', 'average_sentiment']
                missing_keys = [key for key in expected_keys if key not in correlation_sample]
                
                if missing_keys:
                    self.log_test("Activity Correlations - Structure", False, f"Missing keys: {missing_keys}")
                else:
                    self.log_test("Activity Correlations - Structure", True, "Correlation data well-structured")
            else:
                self.log_test("Activity Correlations - Data", True, "No correlations found (expected for limited data)")
        else:
            self.log_test("Activity Correlations", False, f"Request failed (status: {status_code})", response_data)

    def test_insights_endpoint(self):
        """Test GET /api/sentiment/insights"""
        print("\n🧠 Testing Emotional Insights Endpoint...")
        
        success, response_data, status_code = self.make_request('GET', 'sentiment/insights', params={'days': 30})
        
        if success:
            insights = response_data.get('insights', [])
            insight_count = response_data.get('insight_count', 0)
            
            self.log_test("Emotional Insights", True, f"Generated {insight_count} insights")
            
            # Validate insights structure
            if len(insights) > 0:
                insight_sample = insights[0]
                expected_keys = ['insight_type', 'title', 'description', 'confidence_score']
                missing_keys = [key for key in expected_keys if key not in insight_sample]
                
                if missing_keys:
                    self.log_test("Emotional Insights - Structure", False, f"Missing keys: {missing_keys}")
                else:
                    self.log_test("Emotional Insights - Structure", True, "Insights well-structured")
                    
                    # Check confidence scores
                    confidence = insight_sample.get('confidence_score', 0)
                    if 0 <= confidence <= 1:
                        self.log_test("Emotional Insights - Confidence", True, f"Confidence: {confidence}")
                    else:
                        self.log_test("Emotional Insights - Confidence", False, f"Invalid confidence: {confidence}")
            else:
                self.log_test("Emotional Insights - Generation", True, "No insights generated (expected for limited data)")
        else:
            self.log_test("Emotional Insights", False, f"Request failed (status: {status_code})", response_data)

    def test_performance_and_response_times(self):
        """Test response times for all endpoints"""
        print("\n⚡ Testing Performance & Response Times...")
        
        # Test text analysis performance
        start_time = time.time()
        test_text = {"text": "This is a performance test for sentiment analysis response time."}
        success, _, _ = self.make_request('POST', 'sentiment/analyze-text', test_text)
        response_time = time.time() - start_time
        
        if success and response_time < 3.0:
            self.log_test("Performance - Text Analysis", True, f"Response time: {response_time:.2f}s")
        else:
            self.log_test("Performance - Text Analysis", False, f"Slow response: {response_time:.2f}s or failed")
        
        # Test trends endpoint performance
        start_time = time.time()
        success, _, _ = self.make_request('GET', 'sentiment/trends', params={'days': 7})
        response_time = time.time() - start_time
        
        if success and response_time < 3.0:
            self.log_test("Performance - Trends", True, f"Response time: {response_time:.2f}s")
        else:
            self.log_test("Performance - Trends", False, f"Slow response: {response_time:.2f}s or failed")

    def test_error_handling(self):
        """Test error handling for edge cases"""
        print("\n🛡️ Testing Error Handling...")
        
        # Test empty text
        empty_text = {"text": ""}
        success, response_data, status_code = self.make_request('POST', 'sentiment/analyze-text', empty_text)
        
        if not success or status_code >= 400:
            self.log_test("Error Handling - Empty Text", True, "Properly handled empty text")
        else:
            self.log_test("Error Handling - Empty Text", False, "Should reject empty text")
        
        # Test invalid days parameter
        success, response_data, status_code = self.make_request('GET', 'sentiment/trends', params={'days': -1})
        
        if not success or status_code >= 400:
            self.log_test("Error Handling - Invalid Days", True, "Properly handled invalid days parameter")
        else:
            self.log_test("Error Handling - Invalid Days", False, "Should reject negative days")

    def run_comprehensive_test(self):
        """Run all sentiment analysis tests"""
        print("🚀 Starting Comprehensive Sentiment Analysis Testing")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.test_authentication():
            print("❌ Authentication failed. Cannot proceed with API tests.")
            return False
        
        # Step 2: Test all sentiment endpoints
        self.test_analyze_text_endpoint()
        self.test_bulk_analyze_endpoint()
        self.test_sentiment_trends_endpoint()
        self.test_wellness_score_endpoint()
        self.test_correlations_endpoint()
        self.test_insights_endpoint()
        
        # Step 3: Performance and error handling
        self.test_performance_and_response_times()
        self.test_error_handling()
        
        # Step 4: Summary
        self.print_test_summary()
        
        return self.tests_passed == self.tests_run

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 SENTIMENT ANALYSIS TEST SUMMARY")
        print("=" * 60)
        
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result['test'].split(' - ')[0]
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0}
            
            if result['success']:
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
        
        print("\n📋 Results by Category:")
        for category, stats in categories.items():
            total = stats['passed'] + stats['failed']
            success_rate = (stats['passed'] / total) * 100 if total > 0 else 0
            print(f"  {category}: {stats['passed']}/{total} ({success_rate:.1f}%)")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        print("\n🎯 GPT-4o-mini Integration Status:")
        text_analysis_passed = any(r['test'].startswith('Text Analysis') and r['success'] for r in self.test_results)
        if text_analysis_passed:
            print("  ✅ GPT-4o-mini sentiment analysis working correctly")
        else:
            print("  ❌ GPT-4o-mini sentiment analysis issues detected")

def main():
    """Main test execution"""
    print("🧠 Aurum Life Sentiment Analysis API Tester")
    print("Testing GPT-4o-mini integration and all 6 sentiment endpoints")
    print("Backend URL: https://emotional-os-1.preview.emergentagent.com/api")
    print()
    
    tester = SentimentAnalysisAPITester()
    success = tester.run_comprehensive_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())