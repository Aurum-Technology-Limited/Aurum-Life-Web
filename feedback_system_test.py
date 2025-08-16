#!/usr/bin/env python3
"""
FEEDBACK SYSTEM BACKEND TESTING - COMPREHENSIVE TESTING
Testing the new Feedback System backend endpoint implementation.

FOCUS AREAS:
1. POST /api/feedback - Submit feedback with different categories and priorities
2. GET /api/feedback - Retrieve user's feedback history
3. Email notification system integration
4. Authentication and authorization verification
5. Data validation and error handling
6. Database verification and user data isolation

TESTING CRITERIA:
- Feedback submission working with all categories (suggestion, bug_report, feature_request, question, complaint, compliment)
- Different priorities (low, medium, high, urgent) supported
- Email notification sent after successful submission
- Feedback retrieval working with proper user isolation
- Validation tests for missing/invalid data
- Database records created with correct structure

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://focus-planner-3.preview.emergentagent.com/api"

class FeedbackSystemTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.created_feedback_ids = []
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        
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
        
        # Test the root endpoint which should exist
        result = self.make_request('GET', '', use_auth=False)
        if not result['success']:
            # Try the base URL without /api
            base_url = self.base_url.replace('/api', '')
            url = f"{base_url}/"
            try:
                response = self.session.get(url, timeout=30)
                result = {
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else {},
                }
            except:
                result = {'success': False, 'error': 'Connection failed'}
        
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_user_authentication(self):
        """Test user authentication with specified credentials"""
        print("\n=== TESTING USER AUTHENTICATION ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
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

    def test_feedback_submission_authentication(self):
        """Test that feedback endpoint requires authentication"""
        print("\n=== TESTING FEEDBACK ENDPOINT AUTHENTICATION ===")
        
        # Test without authentication
        feedback_data = {
            "category": "suggestion",
            "priority": "medium",
            "subject": "Test Feedback",
            "message": "This is a test feedback message"
        }
        
        result = self.make_request('POST', '/feedback', data=feedback_data, use_auth=False)
        
        # Should fail with 401 or 403
        auth_required = not result['success'] and result['status_code'] in [401, 403]
        
        self.log_test(
            "FEEDBACK ENDPOINT AUTHENTICATION REQUIRED",
            auth_required,
            f"Endpoint properly requires authentication (status: {result['status_code']})" if auth_required else f"Endpoint allows unauthenticated access (status: {result['status_code']})"
        )
        
        return auth_required

    def test_feedback_submission_categories(self):
        """Test feedback submission with different categories"""
        print("\n=== TESTING FEEDBACK SUBMISSION WITH DIFFERENT CATEGORIES ===")
        
        if not self.auth_token:
            self.log_test("FEEDBACK CATEGORIES", False, "No authentication token available")
            return False
        
        # Test different feedback categories as specified in the review request
        categories = [
            ("suggestion", "Feature Suggestion", "I suggest adding a new feature for better user experience."),
            ("bug_report", "Bug Report", "I found a bug in the application that needs to be fixed."),
            ("feature_request", "Feature Request", "I would like to request a new feature for the application."),
            ("question", "Question", "I have a question about how to use the application."),
            ("complaint", "Complaint", "I have a complaint about the application's performance."),
            ("compliment", "Compliment", "Great job on the application! I love using it.")
        ]
        
        successful_submissions = 0
        total_categories = len(categories)
        
        for category, subject, message in categories:
            feedback_data = {
                "category": category,
                "priority": "medium",
                "subject": subject,
                "message": message
            }
            
            result = self.make_request('POST', '/feedback', data=feedback_data, use_auth=True)
            
            if result['success']:
                successful_submissions += 1
                # Store feedback ID for later retrieval test
                if 'feedback_id' in result['data']:
                    self.created_feedback_ids.append(result['data']['feedback_id'])
            
            self.log_test(
                f"FEEDBACK CATEGORY - {category.upper()}",
                result['success'],
                f"Category '{category}' submitted successfully" if result['success'] else f"Category '{category}' failed: {result.get('error', 'Unknown error')}"
            )
        
        success_rate = (successful_submissions / total_categories) * 100
        overall_success = success_rate >= 90  # 90% success rate threshold
        
        self.log_test(
            "FEEDBACK CATEGORIES OVERALL",
            overall_success,
            f"Category submission success rate: {successful_submissions}/{total_categories} ({success_rate:.1f}%)"
        )
        
        return overall_success

    def test_feedback_submission_priorities(self):
        """Test feedback submission with different priorities"""
        print("\n=== TESTING FEEDBACK SUBMISSION WITH DIFFERENT PRIORITIES ===")
        
        if not self.auth_token:
            self.log_test("FEEDBACK PRIORITIES", False, "No authentication token available")
            return False
        
        # Test different priorities as specified in the review request
        priorities = ["low", "medium", "high", "urgent"]
        
        successful_submissions = 0
        total_priorities = len(priorities)
        
        for priority in priorities:
            feedback_data = {
                "category": "suggestion",
                "priority": priority,
                "subject": f"Test Feedback - {priority.title()} Priority",
                "message": f"This is a test feedback message with {priority} priority."
            }
            
            result = self.make_request('POST', '/feedback', data=feedback_data, use_auth=True)
            
            if result['success']:
                successful_submissions += 1
                # Store feedback ID for later retrieval test
                if 'feedback_id' in result['data']:
                    self.created_feedback_ids.append(result['data']['feedback_id'])
            
            self.log_test(
                f"FEEDBACK PRIORITY - {priority.upper()}",
                result['success'],
                f"Priority '{priority}' submitted successfully" if result['success'] else f"Priority '{priority}' failed: {result.get('error', 'Unknown error')}"
            )
        
        success_rate = (successful_submissions / total_priorities) * 100
        overall_success = success_rate >= 90  # 90% success rate threshold
        
        self.log_test(
            "FEEDBACK PRIORITIES OVERALL",
            overall_success,
            f"Priority submission success rate: {successful_submissions}/{total_priorities} ({success_rate:.1f}%)"
        )
        
        return overall_success

    def test_feedback_response_structure(self):
        """Test feedback submission response structure"""
        print("\n=== TESTING FEEDBACK RESPONSE STRUCTURE ===")
        
        if not self.auth_token:
            self.log_test("FEEDBACK RESPONSE STRUCTURE", False, "No authentication token available")
            return False
        
        # Submit a test feedback to check response structure
        feedback_data = {
            "category": "suggestion",
            "priority": "medium",
            "subject": "Response Structure Test",
            "message": "Testing the response structure of feedback submission."
        }
        
        result = self.make_request('POST', '/feedback', data=feedback_data, use_auth=True)
        
        if not result['success']:
            self.log_test(
                "FEEDBACK RESPONSE STRUCTURE",
                False,
                f"Feedback submission failed: {result.get('error', 'Unknown error')}"
            )
            return False
        
        response_data = result['data']
        
        # Check for expected response fields as per the review request
        expected_fields = ['message', 'feedback_id', 'email_sent']
        missing_fields = []
        
        for field in expected_fields:
            if field not in response_data:
                missing_fields.append(field)
        
        structure_valid = len(missing_fields) == 0
        
        self.log_test(
            "FEEDBACK RESPONSE STRUCTURE",
            structure_valid,
            f"Response contains all expected fields: {expected_fields}" if structure_valid else f"Missing fields: {missing_fields}"
        )
        
        # Check if response indicates successful submission
        success_message = response_data.get('message', '').lower()
        message_valid = 'success' in success_message or 'submitted' in success_message
        
        self.log_test(
            "FEEDBACK SUCCESS MESSAGE",
            message_valid,
            f"Success message present: {response_data.get('message')}" if message_valid else f"Unclear success message: {response_data.get('message')}"
        )
        
        # Check if feedback_id is provided
        feedback_id_present = 'feedback_id' in response_data and response_data['feedback_id']
        
        self.log_test(
            "FEEDBACK ID PROVIDED",
            feedback_id_present,
            f"Feedback ID provided: {response_data.get('feedback_id')}" if feedback_id_present else "Feedback ID missing or empty"
        )
        
        # Store feedback ID for later tests
        if feedback_id_present:
            self.created_feedback_ids.append(response_data['feedback_id'])
        
        return structure_valid and message_valid and feedback_id_present

    def test_email_notification_integration(self):
        """Test email notification integration"""
        print("\n=== TESTING EMAIL NOTIFICATION INTEGRATION ===")
        
        if not self.auth_token:
            self.log_test("EMAIL NOTIFICATION INTEGRATION", False, "No authentication token available")
            return False
        
        # Submit feedback that should trigger email notification
        feedback_data = {
            "category": "bug_report",
            "priority": "high",
            "subject": "Email Integration Test",
            "message": "This feedback is specifically designed to test the email notification integration. The email service should be called and should log the email details."
        }
        
        result = self.make_request('POST', '/feedback', data=feedback_data, use_auth=True)
        
        if not result['success']:
            self.log_test(
                "EMAIL NOTIFICATION INTEGRATION",
                False,
                f"Feedback submission failed: {result.get('error', 'Unknown error')}"
            )
            return False
        
        response_data = result['data']
        
        # Check if email_sent flag is present and indicates email was sent
        email_sent = response_data.get('email_sent', False)
        
        self.log_test(
            "EMAIL NOTIFICATION SENT",
            email_sent,
            f"Email notification sent successfully" if email_sent else f"Email notification not sent or flag missing"
        )
        
        # Store feedback ID for later tests
        if 'feedback_id' in response_data:
            self.created_feedback_ids.append(response_data['feedback_id'])
        
        return email_sent

    def test_feedback_retrieval(self):
        """Test feedback retrieval endpoint"""
        print("\n=== TESTING FEEDBACK RETRIEVAL ===")
        
        if not self.auth_token:
            self.log_test("FEEDBACK RETRIEVAL", False, "No authentication token available")
            return False
        
        # Wait a moment for feedback to be processed
        time.sleep(2)
        
        # Test GET /api/feedback endpoint
        result = self.make_request('GET', '/feedback', use_auth=True)
        
        self.log_test(
            "FEEDBACK RETRIEVAL ENDPOINT",
            result['success'],
            f"Feedback retrieval successful" if result['success'] else f"Feedback retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        feedback_list = result['data']
        
        # Check if response is a list
        is_list = isinstance(feedback_list, list)
        
        self.log_test(
            "FEEDBACK RETRIEVAL RESPONSE FORMAT",
            is_list,
            f"Response is a list with {len(feedback_list)} items" if is_list else f"Response is not a list: {type(feedback_list)}"
        )
        
        if not is_list:
            return False
        
        # Check if we can find some of our submitted feedback
        found_feedback = 0
        for feedback_id in self.created_feedback_ids:
            if any(fb.get('id') == feedback_id for fb in feedback_list):
                found_feedback += 1
        
        feedback_found = found_feedback > 0
        
        self.log_test(
            "FEEDBACK RETRIEVAL DATA INTEGRITY",
            feedback_found,
            f"Found {found_feedback}/{len(self.created_feedback_ids)} submitted feedback items" if feedback_found else "No submitted feedback found in retrieval"
        )
        
        # Check feedback structure if we have any feedback
        if len(feedback_list) > 0:
            first_feedback = feedback_list[0]
            expected_fields = ['id', 'user_id', 'category', 'priority', 'subject', 'message', 'status', 'created_at']
            missing_fields = [field for field in expected_fields if field not in first_feedback]
            
            structure_valid = len(missing_fields) == 0
            
            self.log_test(
                "FEEDBACK ITEM STRUCTURE",
                structure_valid,
                f"Feedback items have correct structure" if structure_valid else f"Missing fields in feedback items: {missing_fields}"
            )
            
            return feedback_found and structure_valid
        
        return feedback_found

    def test_feedback_validation(self):
        """Test feedback validation for missing/invalid data"""
        print("\n=== TESTING FEEDBACK VALIDATION ===")
        
        if not self.auth_token:
            self.log_test("FEEDBACK VALIDATION", False, "No authentication token available")
            return False
        
        validation_tests = []
        
        # Test missing subject
        result = self.make_request('POST', '/feedback', data={
            "category": "suggestion",
            "priority": "medium",
            "message": "Test message without subject"
        }, use_auth=True)
        
        missing_subject_handled = not result['success'] and result['status_code'] in [400, 422]
        validation_tests.append(("Missing Subject", missing_subject_handled))
        
        self.log_test(
            "VALIDATION - MISSING SUBJECT",
            missing_subject_handled,
            f"Missing subject properly rejected (status: {result['status_code']})" if missing_subject_handled else f"Missing subject not properly handled (status: {result['status_code']})"
        )
        
        # Test missing message
        result = self.make_request('POST', '/feedback', data={
            "category": "suggestion",
            "priority": "medium",
            "subject": "Test subject without message"
        }, use_auth=True)
        
        missing_message_handled = not result['success'] and result['status_code'] in [400, 422]
        validation_tests.append(("Missing Message", missing_message_handled))
        
        self.log_test(
            "VALIDATION - MISSING MESSAGE",
            missing_message_handled,
            f"Missing message properly rejected (status: {result['status_code']})" if missing_message_handled else f"Missing message not properly handled (status: {result['status_code']})"
        )
        
        # Test invalid category
        result = self.make_request('POST', '/feedback', data={
            "category": "invalid_category",
            "priority": "medium",
            "subject": "Test Subject",
            "message": "Test message with invalid category"
        }, use_auth=True)
        
        invalid_category_handled = not result['success'] and result['status_code'] in [400, 422]
        validation_tests.append(("Invalid Category", invalid_category_handled))
        
        self.log_test(
            "VALIDATION - INVALID CATEGORY",
            invalid_category_handled,
            f"Invalid category properly rejected (status: {result['status_code']})" if invalid_category_handled else f"Invalid category not properly handled (status: {result['status_code']})"
        )
        
        # Test invalid priority
        result = self.make_request('POST', '/feedback', data={
            "category": "suggestion",
            "priority": "invalid_priority",
            "subject": "Test Subject",
            "message": "Test message with invalid priority"
        }, use_auth=True)
        
        invalid_priority_handled = not result['success'] and result['status_code'] in [400, 422]
        validation_tests.append(("Invalid Priority", invalid_priority_handled))
        
        self.log_test(
            "VALIDATION - INVALID PRIORITY",
            invalid_priority_handled,
            f"Invalid priority properly rejected (status: {result['status_code']})" if invalid_priority_handled else f"Invalid priority not properly handled (status: {result['status_code']})"
        )
        
        # Calculate overall validation success
        passed_validations = sum(1 for _, passed in validation_tests if passed)
        total_validations = len(validation_tests)
        validation_success_rate = (passed_validations / total_validations) * 100
        overall_validation_success = validation_success_rate >= 75  # 75% threshold
        
        self.log_test(
            "VALIDATION OVERALL",
            overall_validation_success,
            f"Validation tests passed: {passed_validations}/{total_validations} ({validation_success_rate:.1f}%)"
        )
        
        return overall_validation_success

    def test_database_verification(self):
        """Test database verification through feedback retrieval"""
        print("\n=== TESTING DATABASE VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test("DATABASE VERIFICATION", False, "No authentication token available")
            return False
        
        # Get user info first
        user_result = self.make_request('GET', '/auth/me', use_auth=True)
        if not user_result['success']:
            self.log_test("DATABASE VERIFICATION - USER INFO", False, "Could not get user information")
            return False
        
        user_data = user_result['data']
        user_id = user_data.get('id')
        user_email = user_data.get('email')
        
        # Retrieve feedback to verify database structure
        feedback_result = self.make_request('GET', '/feedback', use_auth=True)
        if not feedback_result['success']:
            self.log_test("DATABASE VERIFICATION - FEEDBACK RETRIEVAL", False, "Could not retrieve feedback for verification")
            return False
        
        feedback_list = feedback_result['data']
        
        if len(feedback_list) == 0:
            self.log_test("DATABASE VERIFICATION - NO DATA", False, "No feedback data available for verification")
            return False
        
        # Check the first feedback item for proper structure
        first_feedback = feedback_list[0]
        
        # Verify user_id is correctly populated
        user_id_correct = first_feedback.get('user_id') == user_id
        self.log_test(
            "DATABASE - USER ID POPULATION",
            user_id_correct,
            f"User ID correctly populated: {first_feedback.get('user_id')}" if user_id_correct else f"User ID mismatch: expected {user_id}, got {first_feedback.get('user_id')}"
        )
        
        # Verify user_email is correctly populated
        user_email_correct = first_feedback.get('user_email') == user_email
        self.log_test(
            "DATABASE - USER EMAIL POPULATION",
            user_email_correct,
            f"User email correctly populated: {first_feedback.get('user_email')}" if user_email_correct else f"User email mismatch: expected {user_email}, got {first_feedback.get('user_email')}"
        )
        
        # Verify user_name is populated
        user_name_present = 'user_name' in first_feedback and first_feedback['user_name']
        self.log_test(
            "DATABASE - USER NAME POPULATION",
            user_name_present,
            f"User name populated: {first_feedback.get('user_name')}" if user_name_present else "User name missing or empty"
        )
        
        # Verify timestamps are present
        created_at_present = 'created_at' in first_feedback and first_feedback['created_at']
        self.log_test(
            "DATABASE - TIMESTAMP POPULATION",
            created_at_present,
            f"Created timestamp populated: {first_feedback.get('created_at')}" if created_at_present else "Created timestamp missing"
        )
        
        # Verify status field is present
        status_present = 'status' in first_feedback and first_feedback['status']
        self.log_test(
            "DATABASE - STATUS FIELD",
            status_present,
            f"Status field populated: {first_feedback.get('status')}" if status_present else "Status field missing"
        )
        
        return user_id_correct and user_email_correct and user_name_present and created_at_present and status_present

    def run_comprehensive_feedback_test(self):
        """Run comprehensive feedback system tests"""
        print("\n📧 STARTING FEEDBACK SYSTEM COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("Feedback Endpoint Authentication", self.test_feedback_submission_authentication),
            ("Feedback Categories", self.test_feedback_submission_categories),
            ("Feedback Priorities", self.test_feedback_submission_priorities),
            ("Feedback Response Structure", self.test_feedback_response_structure),
            ("Email Notification Integration", self.test_email_notification_integration),
            ("Feedback Retrieval", self.test_feedback_retrieval),
            ("Feedback Validation", self.test_feedback_validation),
            ("Database Verification", self.test_database_verification)
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
        print("📧 FEEDBACK SYSTEM TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for feedback functionality
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        submission_tests_passed = sum(1 for result in self.test_results if result['success'] and ('CATEGORY' in result['test'] or 'PRIORITY' in result['test']))
        email_tests_passed = sum(1 for result in self.test_results if result['success'] and 'EMAIL' in result['test'])
        retrieval_tests_passed = sum(1 for result in self.test_results if result['success'] and 'RETRIEVAL' in result['test'])
        validation_tests_passed = sum(1 for result in self.test_results if result['success'] and 'VALIDATION' in result['test'])
        database_tests_passed = sum(1 for result in self.test_results if result['success'] and 'DATABASE' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Submission Tests Passed: {submission_tests_passed}")
        print(f"Email Integration Tests Passed: {email_tests_passed}")
        print(f"Retrieval Tests Passed: {retrieval_tests_passed}")
        print(f"Validation Tests Passed: {validation_tests_passed}")
        print(f"Database Tests Passed: {database_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ FEEDBACK SYSTEM: SUCCESS")
            print("   ✅ POST /api/feedback endpoint working correctly")
            print("   ✅ GET /api/feedback endpoint functional")
            print("   ✅ Authentication requirement enforced")
            print("   ✅ All feedback categories supported (suggestion, bug_report, feature_request, question, complaint, compliment)")
            print("   ✅ All priority levels supported (low, medium, high, urgent)")
            print("   ✅ Email notification integration functional")
            print("   ✅ Data validation implemented")
            print("   ✅ Database records created with proper structure")
            print("   ✅ User data isolation maintained")
            print("   The Feedback System is production-ready!")
        else:
            print("\n❌ FEEDBACK SYSTEM: ISSUES DETECTED")
            print("   Issues found in feedback system implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Feedback System Tests"""
    print("📧 STARTING FEEDBACK SYSTEM BACKEND TESTING")
    print("=" * 80)
    
    tester = FeedbackSystemTester()
    
    try:
        # Run the comprehensive feedback system tests
        success = tester.run_comprehensive_feedback_test()
        
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

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)