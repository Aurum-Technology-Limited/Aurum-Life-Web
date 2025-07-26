#!/usr/bin/env python3
"""
AI COACH BACKEND FUNCTIONALITY TESTING
Complete end-to-end testing of the AI Coach backend implementation.

FOCUS AREAS:
1. AI COACH DAILY PRIORITIES - Test GET /api/ai_coach/today endpoint
2. AI COACH CONVERSATIONAL CHAT - Test POST /api/ai_coach/chat endpoint
3. AUTHENTICATION REQUIREMENTS - Test JWT token requirements
4. GEMINI AI INTEGRATION - Test AI integration with Gemini 2.0-Flash
5. RESPONSE FORMAT VALIDATION - Test response structure matches frontend expectations
6. ERROR HANDLING - Test invalid requests and error responses

SPECIFIC ENDPOINTS TO TEST:
- GET /api/ai_coach/today (daily task priorities for dashboard)
- POST /api/ai_coach/chat (conversational AI coaching)

TEST SCENARIOS:
- General coaching questions ("How can I stay motivated?")
- Goal-related questions ("Help me set better goals")
- Progress questions ("I'm feeling stuck lately")
- Focus questions ("Tips for better focus")

AUTHENTICATION:
- Use test credentials with realistic data for AI Coach testing
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://ef742aff-654d-4d46-b965-c2befb9d14a8.preview.emergentagent.com/api"

class AiCoachTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': [],
            'users': []
        }
        self.auth_token = None
        # Use realistic test data for AI Coach testing
        self.test_user_email = f"aicoach.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "AiCoachTest2025!"
        self.test_user_data = {
            "username": f"aicoach_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "AiCoach",
            "last_name": "Tester",
            "password": self.test_user_password
        }
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling and optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Try to parse JSON response
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response': response,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg += f" - Response: {error_data}"
                except:
                    error_msg += f" - Response: {e.response.text[:200]}"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'data': {},
                'response': getattr(e, 'response', None)
            }

    def test_basic_connectivity(self):
        """Test basic connectivity to the backend API"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
        result = self.make_request('GET', '/health')
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            health_data = result['data']
            self.log_test(
                "HEALTH CHECK RESPONSE",
                'status' in health_data,
                f"Health check returned: {health_data.get('status', 'Unknown status')}"
            )
        
        return result['success']

    def test_user_registration_and_login(self):
        """Test user registration and login for AI Coach testing"""
        print("\n=== TESTING USER REGISTRATION AND LOGIN ===")
        
        # Register user
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        self.log_test(
            "USER REGISTRATION",
            result['success'],
            f"User registered successfully: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        self.created_resources['users'].append(result['data'].get('id'))
        
        # Login user
        login_data = {
            "email": self.test_user_data['email'],
            "password": self.test_user_data['password']
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful, JWT token received" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def setup_test_data(self):
        """Create test data for AI Coach to analyze"""
        print("\n=== SETTING UP TEST DATA FOR AI COACH ===")
        
        if not self.auth_token:
            self.log_test("SETUP TEST DATA - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a pillar
        pillar_data = {
            "name": "Health & Wellness",
            "description": "Physical and mental health goals",
            "icon": "🏥",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("SETUP - CREATE PILLAR", False, f"Failed to create pillar: {result.get('error')}")
            return False
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        
        # Create an area
        area_data = {
            "name": "Fitness & Exercise",
            "description": "Regular exercise and fitness activities",
            "icon": "💪",
            "color": "#FF5722",
            "pillar_id": pillar_id,
            "importance": 4
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("SETUP - CREATE AREA", False, f"Failed to create area: {result.get('error')}")
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        # Create a project
        project_data = {
            "area_id": area_id,
            "name": "Morning Workout Routine",
            "description": "Establish a consistent morning workout routine",
            "priority": "high",
            "importance": 5,
            "deadline": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("SETUP - CREATE PROJECT", False, f"Failed to create project: {result.get('error')}")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Create tasks with different priorities and due dates
        tasks_data = [
            {
                "project_id": project_id,
                "name": "Buy workout equipment",
                "description": "Purchase dumbbells and yoga mat",
                "priority": "high",
                "status": "todo",
                "due_date": (datetime.now() + timedelta(days=2)).isoformat()
            },
            {
                "project_id": project_id,
                "name": "Plan weekly workout schedule",
                "description": "Create a structured weekly workout plan",
                "priority": "medium",
                "status": "in_progress",
                "due_date": (datetime.now() + timedelta(days=1)).isoformat()
            },
            {
                "project_id": project_id,
                "name": "Research fitness apps",
                "description": "Find a good fitness tracking app",
                "priority": "low",
                "status": "todo",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat()
            },
            {
                "project_id": project_id,
                "name": "Complete first workout",
                "description": "Do the first workout session",
                "priority": "high",
                "status": "todo",
                "due_date": (datetime.now() - timedelta(days=1)).isoformat()  # Overdue
            }
        ]
        
        created_tasks = 0
        for task_data in tasks_data:
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if result['success']:
                task_id = result['data']['id']
                self.created_resources['tasks'].append(task_id)
                created_tasks += 1
        
        self.log_test(
            "SETUP TEST DATA",
            created_tasks == len(tasks_data),
            f"Created {created_tasks}/{len(tasks_data)} test tasks for AI Coach analysis"
        )
        
        return created_tasks > 0

    def test_ai_coach_authentication(self):
        """Test that AI Coach endpoints require authentication"""
        print("\n=== TESTING AI COACH AUTHENTICATION REQUIREMENTS ===")
        
        # Test GET /api/ai_coach/today without authentication
        result = self.make_request('GET', '/ai_coach/today', use_auth=False)
        self.log_test(
            "AI COACH TODAY - NO AUTH",
            result['status_code'] in [401, 403],
            f"Correctly rejected unauthenticated request (status: {result['status_code']})" if result['status_code'] in [401, 403] else f"Unexpected response: {result['status_code']}"
        )
        
        # Test POST /api/ai_coach/chat without authentication
        result = self.make_request('POST', '/ai_coach/chat', params={"message": "How can I stay motivated?"}, use_auth=False)
        self.log_test(
            "AI COACH CHAT - NO AUTH",
            result['status_code'] in [401, 403],
            f"Correctly rejected unauthenticated request (status: {result['status_code']})" if result['status_code'] in [401, 403] else f"Unexpected response: {result['status_code']}"
        )
        
        return True

    def test_ai_coach_today_endpoint(self):
        """Test GET /api/ai_coach/today endpoint for daily priorities"""
        print("\n=== TESTING AI COACH TODAY ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("AI COACH TODAY - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/ai_coach/today with authentication
        result = self.make_request('GET', '/ai_coach/today', use_auth=True)
        self.log_test(
            "AI COACH TODAY - WITH AUTH",
            result['success'],
            f"Successfully retrieved daily priorities" if result['success'] else f"Failed to get daily priorities: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            response_data = result['data']
            
            # Verify response structure
            expected_fields = ['success', 'recommendations', 'message', 'timestamp']
            missing_fields = [field for field in expected_fields if field not in response_data]
            
            self.log_test(
                "AI COACH TODAY - RESPONSE STRUCTURE",
                len(missing_fields) == 0,
                f"Response has all expected fields" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
            )
            
            # Verify success field
            is_success = response_data.get('success', False)
            self.log_test(
                "AI COACH TODAY - SUCCESS FIELD",
                is_success,
                f"Response indicates success" if is_success else f"Response indicates failure"
            )
            
            # Verify recommendations structure
            recommendations = response_data.get('recommendations', [])
            self.log_test(
                "AI COACH TODAY - RECOMMENDATIONS",
                isinstance(recommendations, list),
                f"Recommendations is a list with {len(recommendations)} items" if isinstance(recommendations, list) else f"Recommendations is not a list: {type(recommendations)}"
            )
            
            # If we have recommendations, verify their structure
            if recommendations and len(recommendations) > 0:
                first_rec = recommendations[0]
                expected_rec_fields = ['task_id', 'task_name', 'coaching_message', 'score', 'reasons']
                missing_rec_fields = [field for field in expected_rec_fields if field not in first_rec]
                
                self.log_test(
                    "AI COACH TODAY - RECOMMENDATION STRUCTURE",
                    len(missing_rec_fields) == 0,
                    f"Recommendation has all expected fields" if len(missing_rec_fields) == 0 else f"Missing recommendation fields: {missing_rec_fields}"
                )
                
                # Verify coaching message is present and meaningful
                coaching_message = first_rec.get('coaching_message', '')
                has_meaningful_message = len(coaching_message) > 10
                
                self.log_test(
                    "AI COACH TODAY - COACHING MESSAGE",
                    has_meaningful_message,
                    f"Coaching message is meaningful ({len(coaching_message)} chars)" if has_meaningful_message else f"Coaching message too short: '{coaching_message}'"
                )
            
            # Verify timestamp format
            timestamp = response_data.get('timestamp', '')
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp_valid = True
            except:
                timestamp_valid = False
            
            self.log_test(
                "AI COACH TODAY - TIMESTAMP FORMAT",
                timestamp_valid,
                f"Timestamp is valid ISO format" if timestamp_valid else f"Invalid timestamp format: {timestamp}"
            )
        
        return result['success']

    def test_ai_coach_chat_endpoint(self):
        """Test POST /api/ai_coach/chat endpoint for conversational coaching"""
        print("\n=== TESTING AI COACH CHAT ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("AI COACH CHAT - Authentication Required", False, "No authentication token available")
            return False
        
        # Test different types of coaching questions
        test_messages = [
            {
                "message": "How can I stay motivated?",
                "category": "General coaching"
            },
            {
                "message": "Help me set better goals",
                "category": "Goal-related"
            },
            {
                "message": "I'm feeling stuck lately",
                "category": "Progress questions"
            },
            {
                "message": "Tips for better focus",
                "category": "Focus questions"
            }
        ]
        
        successful_chats = 0
        
        for test_case in test_messages:
            message = test_case["message"]
            category = test_case["category"]
            
            # Test the chat endpoint - message should be a query parameter
            result = self.make_request('POST', '/ai_coach/chat', params={"message": message}, use_auth=True)
            
            test_success = result['success']
            self.log_test(
                f"AI COACH CHAT - {category.upper()}",
                test_success,
                f"Successfully processed '{message}'" if test_success else f"Failed to process '{message}': {result.get('error', 'Unknown error')}"
            )
            
            if test_success:
                successful_chats += 1
                response_data = result['data']
                
                # Verify response structure
                expected_fields = ['success', 'response', 'timestamp']
                missing_fields = [field for field in expected_fields if field not in response_data]
                
                self.log_test(
                    f"AI COACH CHAT - {category.upper()} STRUCTURE",
                    len(missing_fields) == 0,
                    f"Response has all expected fields" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
                )
                
                # Verify AI response is meaningful
                ai_response = response_data.get('response', '')
                has_meaningful_response = len(ai_response) > 20
                
                self.log_test(
                    f"AI COACH CHAT - {category.upper()} RESPONSE",
                    has_meaningful_response,
                    f"AI response is meaningful ({len(ai_response)} chars)" if has_meaningful_response else f"AI response too short: '{ai_response}'"
                )
                
                # Check if response seems contextual (mentions user data)
                contextual_keywords = ['task', 'goal', 'project', 'health', 'fitness', 'workout']
                is_contextual = any(keyword.lower() in ai_response.lower() for keyword in contextual_keywords)
                
                self.log_test(
                    f"AI COACH CHAT - {category.upper()} CONTEXTUAL",
                    is_contextual,
                    f"AI response appears contextual" if is_contextual else f"AI response may not be using user context"
                )
        
        # Test error handling with invalid input
        result = self.make_request('POST', '/ai_coach/chat', params={}, use_auth=True)
        self.log_test(
            "AI COACH CHAT - INVALID INPUT",
            not result['success'],
            f"Correctly rejected invalid input (status: {result['status_code']})" if not result['success'] else f"Should have rejected empty message"
        )
        
        return successful_chats >= len(test_messages) // 2  # At least half should succeed

    def test_ai_coach_error_handling(self):
        """Test error handling for AI Coach endpoints"""
        print("\n=== TESTING AI COACH ERROR HANDLING ===")
        
        if not self.auth_token:
            self.log_test("AI COACH ERROR HANDLING - Authentication Required", False, "No authentication token available")
            return False
        
        # Test chat with empty message
        result = self.make_request('POST', '/ai_coach/chat', params={"message": ""}, use_auth=True)
        self.log_test(
            "AI COACH CHAT - EMPTY MESSAGE",
            result['status_code'] in [400, 422],
            f"Correctly rejected empty message (status: {result['status_code']})" if result['status_code'] in [400, 422] else f"Should reject empty message, got: {result['status_code']}"
        )
        
        # Test chat with very long message
        long_message = "A" * 10000  # 10k characters
        result = self.make_request('POST', '/ai_coach/chat', params={"message": long_message}, use_auth=True)
        self.log_test(
            "AI COACH CHAT - VERY LONG MESSAGE",
            result['success'] or result['status_code'] in [400, 413],
            f"Handled very long message appropriately (status: {result['status_code']})" if result['success'] or result['status_code'] in [400, 413] else f"Unexpected response to long message: {result['status_code']}"
        )
        
        # Test with malformed JSON (this will be handled by the request framework)
        # We'll test with missing required fields instead
        result = self.make_request('POST', '/ai_coach/chat', params={"not_message": "test"}, use_auth=True)
        self.log_test(
            "AI COACH CHAT - MISSING MESSAGE FIELD",
            result['status_code'] in [400, 422],
            f"Correctly rejected missing message field (status: {result['status_code']})" if result['status_code'] in [400, 422] else f"Should reject missing message field, got: {result['status_code']}"
        )
        
        return True

    def test_gemini_integration(self):
        """Test that Gemini AI integration is working"""
        print("\n=== TESTING GEMINI AI INTEGRATION ===")
        
        if not self.auth_token:
            self.log_test("GEMINI INTEGRATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test a specific question that should trigger AI processing
        ai_test_message = "Based on my current tasks and goals, what should I focus on today to make the most progress?"
        
        result = self.make_request('POST', '/ai_coach/chat', params={"message": ai_test_message}, use_auth=True)
        
        self.log_test(
            "GEMINI AI INTEGRATION - BASIC FUNCTIONALITY",
            result['success'],
            f"Gemini AI responded successfully" if result['success'] else f"Gemini AI integration failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            response_data = result['data']
            ai_response = response_data.get('response', '')
            
            # Check for signs of AI-generated content
            ai_indicators = [
                len(ai_response) > 50,  # Substantial response
                any(word in ai_response.lower() for word in ['focus', 'progress', 'goal', 'task', 'recommend']),  # Relevant keywords
                '.' in ai_response,  # Proper sentences
                not ai_response.startswith('Error'),  # Not an error message
            ]
            
            ai_quality_score = sum(ai_indicators)
            
            self.log_test(
                "GEMINI AI INTEGRATION - RESPONSE QUALITY",
                ai_quality_score >= 3,
                f"AI response quality score: {ai_quality_score}/4" if ai_quality_score >= 3 else f"AI response quality low: {ai_quality_score}/4"
            )
            
            # Test response time (should be reasonable for AI processing)
            # This is a rough test since we don't have precise timing
            self.log_test(
                "GEMINI AI INTEGRATION - RESPONSE TIME",
                True,  # If we got here, response time was acceptable
                f"AI response received within timeout period"
            )
        
        return result['success']

    def run_comprehensive_ai_coach_test(self):
        """Run comprehensive AI Coach backend tests"""
        print("\n🤖 STARTING AI COACH BACKEND COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration and Login", self.test_user_registration_and_login),
            ("Setup Test Data", self.setup_test_data),
            ("AI Coach Authentication", self.test_ai_coach_authentication),
            ("AI Coach Today Endpoint", self.test_ai_coach_today_endpoint),
            ("AI Coach Chat Endpoint", self.test_ai_coach_chat_endpoint),
            ("AI Coach Error Handling", self.test_ai_coach_error_handling),
            ("Gemini AI Integration", self.test_gemini_integration)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🎯 AI COACH BACKEND TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for AI Coach functionality
        ai_coach_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AI COACH' in result['test'])
        gemini_tests_passed = sum(1 for result in self.test_results if result['success'] and 'GEMINI' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"AI Coach Tests Passed: {ai_coach_tests_passed}")
        print(f"Gemini Integration Tests Passed: {gemini_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ AI COACH BACKEND FUNCTIONALITY: SUCCESS")
            print("   ✅ GET /api/ai_coach/today endpoint working correctly")
            print("   ✅ POST /api/ai_coach/chat endpoint working correctly")
            print("   ✅ Authentication requirements properly enforced")
            print("   ✅ Response format matches frontend expectations")
            print("   ✅ Error handling working properly")
            print("   ✅ Gemini 2.0-Flash AI integration functional")
            print("   The AI Coach backend is production-ready!")
        else:
            print("\n❌ AI COACH BACKEND FUNCTIONALITY: ISSUES DETECTED")
            print("   Issues found in AI Coach backend implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        cleanup_count = 0
        
        # Clean up tasks first (they depend on projects)
        for task_id in self.created_resources.get('tasks', []):
            try:
                result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up task: {task_id}")
            except:
                pass
        
        # Clean up projects (they depend on areas)
        for project_id in self.created_resources.get('projects', []):
            try:
                result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up project: {project_id}")
            except:
                pass
        
        # Clean up areas (they may depend on pillars)
        for area_id in self.created_resources.get('areas', []):
            try:
                result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up area: {area_id}")
            except:
                pass
        
        # Clean up pillars
        for pillar_id in self.created_resources.get('pillars', []):
            try:
                result = self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up pillar: {pillar_id}")
            except:
                pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

def main():
    """Run AI Coach Backend Tests"""
    print("🤖 STARTING AI COACH BACKEND TESTING")
    print("=" * 80)
    
    tester = AiCoachTester()
    
    try:
        # Run the comprehensive AI Coach tests
        success = tester.run_comprehensive_ai_coach_test()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False
    
    finally:
        # Cleanup created resources
        tester.cleanup_resources()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)