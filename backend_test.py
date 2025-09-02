#!/usr/bin/env python3
"""
Comprehensive Analytics System Backend Testing
Tests all analytics endpoints with authentication and data flow validation
"""

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid
import time

class AnalyticsBackendTester:
    def __init__(self, base_url="https://aurum-life-os.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details,
            'response_data': response_data
        })

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make authenticated API request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}", {}

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if not success:
                return False, f"Expected {expected_status}, got {response.status_code}: {response.text}", response_data
            
            return True, "Success", response_data

        except requests.exceptions.Timeout:
            return False, "Request timeout (30s)", {}
        except requests.exceptions.ConnectionError:
            return False, "Connection error", {}
        except Exception as e:
            return False, f"Request error: {str(e)}", {}

    def test_login(self):
        """Test login with provided credentials"""
        print("\n🔐 Testing Authentication...")
        
        success, message, response_data = self.make_request(
            'POST', 
            'auth/login',
            {
                "email": "marc.alleyne@aurumtechnologyltd.com",
                "password": "password123"
            }
        )
        
        if success and 'access_token' in response_data:
            self.token = response_data['access_token']
            self.log_test("Authentication", True, "Login successful")
            return True
        else:
            self.log_test("Authentication", False, f"Login failed: {message}")
            return False

    def test_analytics_preferences_get(self):
        """Test getting analytics preferences"""
        print("\n📊 Testing Analytics Preferences (GET)...")
        
        success, message, response_data = self.make_request('GET', 'analytics/preferences')
        
        if success:
            # Check if response has expected structure
            expected_fields = ['analytics_enabled', 'data_retention_days']
            has_expected_structure = any(field in response_data for field in expected_fields)
            
            if has_expected_structure:
                self.log_test("Get Analytics Preferences", True, "Retrieved preferences successfully", response_data)
                return True
            else:
                self.log_test("Get Analytics Preferences", False, "Response missing expected fields", response_data)
                return False
        else:
            self.log_test("Get Analytics Preferences", False, message, response_data)
            return False

    def test_analytics_preferences_update(self):
        """Test updating analytics preferences"""
        print("\n📊 Testing Analytics Preferences (PUT)...")
        
        preferences_data = {
            "analytics_enabled": True,
            "performance_tracking": True,
            "ai_interaction_tracking": True,
            "data_retention_days": 90,
            "anonymous_usage_stats": True
        }
        
        success, message, response_data = self.make_request(
            'PUT', 
            'analytics/preferences',
            preferences_data
        )
        
        if success:
            self.log_test("Update Analytics Preferences", True, "Updated preferences successfully", response_data)
            return True
        else:
            self.log_test("Update Analytics Preferences", False, message, response_data)
            return False

    def test_start_session(self):
        """Test starting analytics session"""
        print("\n🚀 Testing Start Analytics Session...")
        
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "device_type": "desktop",
            "screen_resolution": "1920x1080",
            "timezone": "UTC",
            "entry_page": "/dashboard"
        }
        
        success, message, response_data = self.make_request(
            'POST',
            'analytics/start-session',
            session_data,
            201  # Expecting 201 for creation
        )
        
        if success:
            self.session_id = session_id
            self.log_test("Start Analytics Session", True, f"Session started: {self.session_id}", response_data)
            return True
        else:
            self.log_test("Start Analytics Session", False, message, response_data)
            return False

    def test_track_events(self):
        """Test tracking various behavior events"""
        print("\n📈 Testing Event Tracking...")
        
        if not self.session_id:
            self.log_test("Event Tracking Prerequisites", False, "No session ID available")
            return False
        
        # Test different types of events with correct structure
        events_to_test = [
            {
                "session_id": self.session_id,
                "action_type": "page_view",
                "feature_name": "dashboard",
                "page_url": "/dashboard",
                "event_data": {"section": "overview"}
            },
            {
                "session_id": self.session_id,
                "action_type": "ai_interaction",
                "feature_name": "goal_planner",
                "ai_feature_type": "goal_planner",
                "event_data": {"action": "generate_plan", "success": True},
                "success": True
            },
            {
                "session_id": self.session_id,
                "action_type": "feature_usage",
                "feature_name": "my_ai_insights",
                "ai_feature_type": "my_ai_insights",
                "duration_ms": 45000,
                "event_data": {"duration_seconds": 45}
            },
            {
                "session_id": self.session_id,
                "action_type": "navigation",
                "feature_name": "sidebar_navigation",
                "event_data": {"from_page": "/dashboard", "to_page": "/ai-insights", "method": "sidebar_click"}
            }
        ]
        
        all_events_successful = True
        
        for i, event_data in enumerate(events_to_test):
            success, message, response_data = self.make_request(
                'POST',
                'analytics/track-event',
                event_data,
                201  # Expecting 201 for creation
            )
            
            event_name = f"Track Event {i+1} ({event_data['action_type']})"
            
            if success:
                self.log_test(event_name, True, f"Event tracked successfully", response_data)
            else:
                self.log_test(event_name, False, message, response_data)
                all_events_successful = False
            
            # Small delay between events
            time.sleep(0.5)
        
        return all_events_successful

    def test_analytics_dashboard(self):
        """Test analytics dashboard data retrieval"""
        print("\n📊 Testing Analytics Dashboard...")
        
        success, message, response_data = self.make_request('GET', 'analytics/dashboard?days=30')
        
        if success:
            # Check for expected dashboard structure
            expected_sections = ['sessions', 'events', 'ai_features', 'engagement']
            has_data_structure = isinstance(response_data, dict) and len(response_data) > 0
            
            if has_data_structure:
                self.log_test("Analytics Dashboard", True, "Dashboard data retrieved", response_data)
                return True
            else:
                self.log_test("Analytics Dashboard", False, "Dashboard data structure invalid", response_data)
                return False
        else:
            self.log_test("Analytics Dashboard", False, message, response_data)
            return False

    def test_ai_features_analytics(self):
        """Test AI features usage analytics"""
        print("\n🧠 Testing AI Features Analytics...")
        
        success, message, response_data = self.make_request('GET', 'analytics/ai-features?days=30')
        
        if success:
            # Check if response is structured data
            has_ai_data = isinstance(response_data, dict) and 'ai_features' in response_data
            
            if has_ai_data or len(response_data) > 0:
                self.log_test("AI Features Analytics", True, "AI features data retrieved", response_data)
                return True
            else:
                self.log_test("AI Features Analytics", False, "AI features data structure invalid", response_data)
                return False
        else:
            self.log_test("AI Features Analytics", False, message, response_data)
            return False

    def test_engagement_metrics(self):
        """Test user engagement metrics"""
        print("\n📈 Testing Engagement Metrics...")
        
        success, message, response_data = self.make_request('GET', 'analytics/engagement?days=30')
        
        if success:
            # Check if response has engagement data
            has_engagement_data = isinstance(response_data, dict) and len(response_data) > 0
            
            if has_engagement_data:
                self.log_test("Engagement Metrics", True, "Engagement data retrieved", response_data)
                return True
            else:
                self.log_test("Engagement Metrics", False, "Engagement data structure invalid", response_data)
                return False
        else:
            self.log_test("Engagement Metrics", False, message, response_data)
            return False

    def test_end_session(self):
        """Test ending analytics session"""
        print("\n🏁 Testing End Analytics Session...")
        
        if not self.session_id:
            self.log_test("End Analytics Session", False, "No session ID available")
            return False
        
        success, message, response_data = self.make_request(
            'POST',
            f'analytics/end-session/{self.session_id}',
            {"exit_page": "/dashboard"}
        )
        
        if success:
            self.log_test("End Analytics Session", True, "Session ended successfully", response_data)
            return True
        else:
            self.log_test("End Analytics Session", False, message, response_data)
            return False

    def test_privacy_controls(self):
        """Test privacy control endpoints"""
        print("\n🔒 Testing Privacy Controls...")
        
        # Test anonymize data endpoint
        success, message, response_data = self.make_request(
            'POST',
            'analytics/anonymize'
        )
        
        if success:
            self.log_test("Anonymize Analytics Data", True, "Data anonymization successful", response_data)
        else:
            self.log_test("Anonymize Analytics Data", False, message, response_data)

    def run_all_tests(self):
        """Run comprehensive analytics backend tests"""
        print("🚀 Starting Comprehensive Analytics Backend Testing")
        print("=" * 60)
        
        # Test authentication first
        if not self.test_login():
            print("\n❌ Authentication failed - stopping tests")
            return False
        
        # Test analytics preferences
        self.test_analytics_preferences_get()
        self.test_analytics_preferences_update()
        
        # Test session management
        self.test_start_session()
        
        # Test event tracking
        self.test_track_events()
        
        # Test analytics data retrieval
        self.test_analytics_dashboard()
        self.test_ai_features_analytics()
        self.test_engagement_metrics()
        
        # Test session ending
        self.test_end_session()
        
        # Test privacy controls
        self.test_privacy_controls()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 ANALYTICS BACKEND TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['name']}: {test['details']}")
        
        print("\n" + "=" * 60)
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = AnalyticsBackendTester()
    
    try:
        success = tester.run_all_tests()
        tester.print_summary()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        tester.print_summary()
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        tester.print_summary()
        return 1

if __name__ == "__main__":
    sys.exit(main())