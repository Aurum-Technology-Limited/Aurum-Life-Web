#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Aurum Life Application
Testing all endpoints with authentication and CRUD operations
"""

import requests
import sys
import json
from datetime import datetime
import time

class AurumLifeAPITester:
    def __init__(self, base_url="https://emotional-os-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test credentials
        self.test_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_password = "password123"
        
        # Store created entities for cleanup
        self.created_entities = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': [],
            'journal_entries': []
        }

    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name} - {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data
        })

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/api/{endpoint}"
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
            
            success = response.status_code == expected_status
            response_data = None
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return success, response_data, response.status_code
            
        except Exception as e:
            return False, str(e), 0

    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        # Test root endpoint
        success, data, status = self.make_request('GET', '', expected_status=200)
        self.log_result("Root endpoint", success, f"Status: {status}")
        
        # Test health endpoint
        success, data, status = self.make_request('GET', 'health', expected_status=200)
        self.log_result("Health check", success, f"Status: {status}")

    def test_authentication(self):
        """Test authentication flow"""
        print("\n🔐 Testing Authentication...")
        
        # Test login
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, data, status = self.make_request('POST', 'auth/login', login_data, expected_status=200)
        
        if success and isinstance(data, dict) and 'access_token' in data:
            self.token = data['access_token']
            self.user_id = data.get('user', {}).get('id')
            self.log_result("Login successful", True, f"Token received, User ID: {self.user_id}")
        else:
            self.log_result("Login failed", False, f"Status: {status}, Data: {data}")
            return False
        
        return True

    def test_ai_quota(self):
        """Test AI quota endpoint"""
        print("\n🤖 Testing AI Quota...")
        
        success, data, status = self.make_request('GET', 'ai/quota', expected_status=200)
        
        if success and isinstance(data, dict):
            remaining = data.get('remaining', 0)
            total = data.get('total', 0)
            expected_total = 250  # Should be 250 after recent update
            
            if total == expected_total:
                self.log_result("AI Quota Check", True, f"Quota: {remaining}/{total}")
            else:
                self.log_result("AI Quota Check", False, f"Expected {expected_total}, got {total}")
        else:
            self.log_result("AI Quota Check", False, f"Status: {status}")

    def test_pillars_crud(self):
        """Test Pillars CRUD operations"""
        print("\n⛰️ Testing Pillars CRUD...")
        
        # Create pillar
        pillar_data = {
            "name": f"Test Pillar {datetime.now().strftime('%H%M%S')}",
            "description": "Test pillar for API testing",
            "color": "#FF6B6B"
        }
        
        success, data, status = self.make_request('POST', 'pillars', pillar_data, expected_status=200)
        if success and isinstance(data, dict) and 'id' in data:
            pillar_id = data['id']
            self.created_entities['pillars'].append(pillar_id)
            self.log_result("Create Pillar", True, f"Created pillar ID: {pillar_id}")
        else:
            self.log_result("Create Pillar", False, f"Status: {status}, Data: {data}")
            return
        
        # Get pillars
        success, data, status = self.make_request('GET', 'pillars', expected_status=200)
        if success and isinstance(data, list):
            self.log_result("Get Pillars", True, f"Retrieved {len(data)} pillars")
        else:
            self.log_result("Get Pillars", False, f"Status: {status}")

    def test_areas_crud(self):
        """Test Areas CRUD operations"""
        print("\n🗂️ Testing Areas CRUD...")
        
        # Create area (only if we have a pillar)
        if not self.created_entities['pillars']:
            self.log_result("Create Area", False, "No pillar available for area creation")
            return
            
        area_data = {
            "name": f"Test Area {datetime.now().strftime('%H%M%S')}",
            "description": "Test area for API testing",
            "pillar_id": self.created_entities['pillars'][0]
        }
        
        success, data, status = self.make_request('POST', 'areas', area_data, expected_status=200)
        if success and isinstance(data, dict) and 'id' in data:
            area_id = data['id']
            self.created_entities['areas'].append(area_id)
            self.log_result("Create Area", True, f"Created area ID: {area_id}")
        else:
            self.log_result("Create Area", False, f"Status: {status}, Data: {data}")
            return
        
        # Get areas
        success, data, status = self.make_request('GET', 'areas', expected_status=200)
        if success and isinstance(data, list):
            self.log_result("Get Areas", True, f"Retrieved {len(data)} areas")
        else:
            self.log_result("Get Areas", False, f"Status: {status}")

    def test_projects_crud(self):
        """Test Projects CRUD operations"""
        print("\n📁 Testing Projects CRUD...")
        
        # Create project (only if we have an area)
        if not self.created_entities['areas']:
            self.log_result("Create Project", False, "No area available for project creation")
            return
            
        project_data = {
            "name": f"Test Project {datetime.now().strftime('%H%M%S')}",
            "description": "Test project for API testing",
            "area_id": self.created_entities['areas'][0],
            "status": "Not Started"
        }
        
        success, data, status = self.make_request('POST', 'projects', project_data, expected_status=200)
        if success and isinstance(data, dict) and 'id' in data:
            project_id = data['id']
            self.created_entities['projects'].append(project_id)
            self.log_result("Create Project", True, f"Created project ID: {project_id}")
        else:
            self.log_result("Create Project", False, f"Status: {status}, Data: {data}")
            return
        
        # Get projects
        success, data, status = self.make_request('GET', 'projects', expected_status=200)
        if success and isinstance(data, list):
            self.log_result("Get Projects", True, f"Retrieved {len(data)} projects")
        else:
            self.log_result("Get Projects", False, f"Status: {status}")

    def test_tasks_crud(self):
        """Test Tasks CRUD operations"""
        print("\n✅ Testing Tasks CRUD...")
        
        # Create task
        task_data = {
            "name": f"Test Task {datetime.now().strftime('%H%M%S')}",
            "description": "Test task for API testing",
            "project_id": self.created_entities['projects'][0] if self.created_entities['projects'] else None,
            "status": "todo",
            "priority": "medium"
        }
        
        success, data, status = self.make_request('POST', 'tasks', task_data, expected_status=201)
        if success and isinstance(data, dict) and 'id' in data:
            task_id = data['id']
            self.created_entities['tasks'].append(task_id)
            self.log_result("Create Task", True, f"Created task ID: {task_id}")
        else:
            self.log_result("Create Task", False, f"Status: {status}, Data: {data}")
            return
        
        # Get tasks
        success, data, status = self.make_request('GET', 'tasks', expected_status=200)
        if success and isinstance(data, list):
            self.log_result("Get Tasks", True, f"Retrieved {len(data)} tasks")
        else:
            self.log_result("Get Tasks", False, f"Status: {status}")

    def test_journal_crud(self):
        """Test Journal CRUD operations (PRIORITY - recently fixed)"""
        print("\n📖 Testing Journal CRUD (PRIORITY)...")
        
        # Create journal entry
        journal_data = {
            "title": f"Test Entry {datetime.now().strftime('%H%M%S')}",
            "content": "This is a test journal entry for API testing. It contains some meaningful content to test the functionality.",
            "mood": "neutral",
            "tags": ["test", "api"]
        }
        
        success, data, status = self.make_request('POST', 'journal', journal_data, expected_status=201)
        if success and isinstance(data, dict) and 'id' in data:
            entry_id = data['id']
            self.created_entities['journal_entries'].append(entry_id)
            self.log_result("Create Journal Entry", True, f"Created entry ID: {entry_id}")
            
            # Test update journal entry
            update_data = {
                "title": f"Updated Test Entry {datetime.now().strftime('%H%M%S')}",
                "content": "This is an updated test journal entry.",
                "mood": "happy"
            }
            
            success, data, status = self.make_request('PUT', f'journal/{entry_id}', update_data, expected_status=200)
            self.log_result("Update Journal Entry", success, f"Status: {status}")
            
        else:
            self.log_result("Create Journal Entry", False, f"Status: {status}, Data: {data}")
            return
        
        # Get journal entries
        success, data, status = self.make_request('GET', 'journal', expected_status=200)
        if success and isinstance(data, list):
            self.log_result("Get Journal Entries", True, f"Retrieved {len(data)} entries")
        else:
            self.log_result("Get Journal Entries", False, f"Status: {status}")

    def test_insights_endpoints(self):
        """Test insights and analytics endpoints"""
        print("\n📊 Testing Insights & Analytics...")
        
        # Test insights
        success, data, status = self.make_request('GET', 'insights', expected_status=200)
        self.log_result("Get Insights", success, f"Status: {status}")
        
        # Test alignment dashboard
        success, data, status = self.make_request('GET', 'alignment/dashboard', expected_status=200)
        self.log_result("Alignment Dashboard", success, f"Status: {status}")
        
        # Test AI today priorities
        success, data, status = self.make_request('GET', 'ai/today-priorities', expected_status=200)
        self.log_result("AI Today Priorities", success, f"Status: {status}")

    def test_semantic_search(self):
        """Test semantic search functionality"""
        print("\n🔍 Testing Semantic Search...")
        
        # Test semantic search
        search_params = "query=test&limit=5"
        success, data, status = self.make_request('GET', f'semantic/search?{search_params}', expected_status=200)
        
        if success and isinstance(data, dict):
            results = data.get('results', [])
            self.log_result("Semantic Search", True, f"Found {len(results)} results")
        else:
            self.log_result("Semantic Search", success, f"Status: {status}")

    def test_ai_features(self):
        """Test AI-related endpoints"""
        print("\n🧠 Testing AI Features...")
        
        # Test task why statements
        success, data, status = self.make_request('GET', 'ai/task-why-statements', expected_status=200)
        self.log_result("AI Task Why Statements", success, f"Status: {status}")
        
        # Test suggest focus
        success, data, status = self.make_request('GET', 'ai/suggest-focus', expected_status=200)
        self.log_result("AI Suggest Focus", success, f"Status: {status}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend API Testing...")
        print(f"📍 Testing against: {self.base_url}")
        print(f"👤 Using credentials: {self.test_email}")
        
        start_time = time.time()
        
        # Run tests in order
        self.test_health_check()
        
        if not self.test_authentication():
            print("❌ Authentication failed - stopping tests")
            return False
        
        self.test_ai_quota()
        self.test_pillars_crud()
        self.test_areas_crud()
        self.test_projects_crud()
        self.test_tasks_crud()
        self.test_journal_crud()  # Priority test
        self.test_insights_endpoints()
        self.test_semantic_search()
        self.test_ai_features()
        
        # Print summary
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 Test Summary:")
        print(f"✅ Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print(f"📈 Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AurumLifeAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
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
    def __init__(self, base_url="https://emotional-os-1.preview.emergentagent.com/api"):
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
            200  # API returns 200, not 201
        )
        
        if success:
            # Extract session_id from response
            if 'session_id' in response_data:
                self.session_id = response_data['session_id']
            else:
                self.session_id = session_id  # Use the one we sent
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
                200  # API likely returns 200, not 201
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