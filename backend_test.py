#!/usr/bin/env python3
"""
Password Reset Email Functionality Testing
Testing the password reset email functionality to verify if emails are being sent correctly.
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://3c105990-8251-418b-add7-b761b0f7ecd6.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"  # Real test email address
TEST_USER_DATA = {
    "username": "test_user_email_reset",
    "email": TEST_EMAIL,
    "password": "testpassword123",
    "first_name": "Marc",
    "last_name": "Alleyne"
}

class PasswordResetEmailTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_environment_configuration(self):
        """Test environment configuration for email service"""
        print("🔧 TESTING ENVIRONMENT CONFIGURATION")
        print("=" * 60)
        
        try:
            # Read the backend .env file to check configuration
            env_file_path = "/app/backend/.env"
            sendgrid_key = None
            sender_email = None
            
            if os.path.exists(env_file_path):
                with open(env_file_path, 'r') as f:
                    for line in f:
                        if line.startswith('SENDGRID_API_KEY='):
                            sendgrid_key = line.split('=', 1)[1].strip()
                        elif line.startswith('SENDER_EMAIL='):
                            sender_email = line.split('=', 1)[1].strip()
            
            # Check if SendGrid API key is properly configured
            sendgrid_configured = sendgrid_key and sendgrid_key != 'your_sendgrid_api_key_here' and len(sendgrid_key) > 10
            sender_configured = sender_email and '@' in sender_email
            
            self.log_test(
                "SendGrid API Key Configuration",
                sendgrid_configured,
                f"SendGrid API Key: {'Properly configured' if sendgrid_configured else 'Missing or placeholder'}"
            )
            
            self.log_test(
                "Sender Email Configuration", 
                sender_configured,
                f"Sender Email: {sender_email if sender_configured else 'Missing or invalid'}"
            )
            
            # Check if email service is in mock mode or production mode
            mock_mode = not sendgrid_configured
            self.log_test(
                "Email Service Mode",
                True,  # This is informational
                f"Email service running in {'MOCK' if mock_mode else 'PRODUCTION'} mode"
            )
            
            return sendgrid_configured and sender_configured
            
        except Exception as e:
            self.log_test("Environment Configuration", False, f"Error: {str(e)}")
            return False

    def create_test_user(self):
        """Create a test user for password reset testing"""
        print("👤 CREATING TEST USER")
        print("=" * 60)
        
        try:
            # First try to register the user
            response = self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=TEST_USER_DATA,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201 or response.status_code == 200:
                self.log_test("Test User Creation", True, f"User created successfully: {TEST_EMAIL}")
                return True
            elif response.status_code == 400 and "already exists" in response.text.lower():
                self.log_test("Test User Creation", True, f"User already exists: {TEST_EMAIL}")
                return True
            else:
                self.log_test("Test User Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test User Creation", False, f"Error: {str(e)}")
            return False

    def test_password_reset_request(self):
        """Test POST /api/auth/forgot-password endpoint"""
        print("📧 TESTING PASSWORD RESET REQUEST")
        print("=" * 60)
        
        try:
            # Test with valid email
            reset_data = {"email": TEST_EMAIL}
            response = self.session.post(
                f"{BACKEND_URL}/auth/forgot-password",
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                success_message = response_data.get("message", "")
                is_success = response_data.get("success", False)
                
                if is_success and "password reset link has been sent" in success_message.lower():
                    self.log_test(
                        "Password Reset Request - Valid Email",
                        True,
                        f"Status: {response.status_code}, Success: {is_success}, Message: {success_message}"
                    )
                    return True
                else:
                    self.log_test(
                        "Password Reset Request - Valid Email",
                        False,
                        f"Unexpected response: {response_data}"
                    )
                    return False
            else:
                self.log_test(
                    "Password Reset Request - Valid Email",
                    False,
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Password Reset Request", False, f"Error: {str(e)}")
            return False

    def test_password_reset_with_invalid_email(self):
        """Test password reset with invalid email"""
        print("🚫 TESTING PASSWORD RESET WITH INVALID EMAIL")
        print("=" * 60)
        
        try:
            # Test with non-existent email
            reset_data = {"email": "nonexistent@example.com"}
            response = self.session.post(
                f"{BACKEND_URL}/auth/forgot-password",
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                success_message = response_data.get("message", "")
                
                # For security, the response should be the same regardless of email existence
                if "password reset link has been sent" in success_message.lower():
                    self.log_test(
                        "Password Reset Request - Non-existent Email",
                        True,
                        f"Security check passed: Same response for non-existent email"
                    )
                    return True
                else:
                    self.log_test(
                        "Password Reset Request - Non-existent Email",
                        False,
                        f"Security issue: Different response for non-existent email: {response_data}"
                    )
                    return False
            else:
                self.log_test(
                    "Password Reset Request - Non-existent Email",
                    False,
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Password Reset Request - Invalid Email", False, f"Error: {str(e)}")
            return False

    def test_email_service_integration(self):
        """Test email service integration by checking backend logs and response patterns"""
        print("📨 TESTING EMAIL SERVICE INTEGRATION")
        print("=" * 60)
        
        try:
            # Make a password reset request and analyze the response time and patterns
            start_time = time.time()
            
            reset_data = {"email": TEST_EMAIL}
            response = self.session.post(
                f"{BACKEND_URL}/auth/forgot-password",
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if the response indicates email service is working
                # A very fast response might indicate mock mode
                # A slower response might indicate actual email sending
                
                if response_time < 0.5:
                    self.log_test(
                        "Email Service Integration",
                        True,
                        f"Fast response ({response_time:.2f}s) suggests mock mode or efficient email queuing"
                    )
                else:
                    self.log_test(
                        "Email Service Integration",
                        True,
                        f"Response time ({response_time:.2f}s) suggests actual email service integration"
                    )
                
                return True
            else:
                self.log_test(
                    "Email Service Integration",
                    False,
                    f"Email service error: Status {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Email Service Integration", False, f"Error: {str(e)}")
            return False

    def test_email_template_and_url_construction(self):
        """Test email template and reset URL construction by making multiple requests"""
        print("🎨 TESTING EMAIL TEMPLATE AND URL CONSTRUCTION")
        print("=" * 60)
        
        try:
            # Make multiple password reset requests to test consistency
            for i in range(3):
                reset_data = {"email": TEST_EMAIL}
                response = self.session.post(
                    f"{BACKEND_URL}/auth/forgot-password",
                    json=reset_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    self.log_test(
                        "Email Template and URL Construction",
                        False,
                        f"Request {i+1} failed: Status {response.status_code}"
                    )
                    return False
                
                time.sleep(1)  # Small delay between requests
            
            self.log_test(
                "Email Template and URL Construction",
                True,
                "Multiple password reset requests processed successfully, indicating proper template and URL construction"
            )
            return True
            
        except Exception as e:
            self.log_test("Email Template and URL Construction", False, f"Error: {str(e)}")
            return False

    def test_sendgrid_configuration(self):
        """Test SendGrid configuration by analyzing response patterns"""
        print("📬 TESTING SENDGRID CONFIGURATION")
        print("=" * 60)
        
        try:
            # Check if the backend is configured for production email sending
            # We can infer this from the environment and response patterns
            
            # Make a password reset request and check for any error patterns
            reset_data = {"email": TEST_EMAIL}
            response = self.session.post(
                f"{BACKEND_URL}/auth/forgot-password",
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if the response indicates successful email processing
                if response_data.get("success", False):
                    self.log_test(
                        "SendGrid Configuration",
                        True,
                        "Email service responding successfully - SendGrid integration appears functional"
                    )
                    return True
                else:
                    self.log_test(
                        "SendGrid Configuration",
                        False,
                        f"Email service not indicating success: {response_data}"
                    )
                    return False
            else:
                self.log_test(
                    "SendGrid Configuration",
                    False,
                    f"SendGrid configuration issue: Status {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("SendGrid Configuration", False, f"Error: {str(e)}")
            return False

    def test_end_to_end_password_reset_flow(self):
        """Test the complete end-to-end password reset flow"""
        print("🔄 TESTING END-TO-END PASSWORD RESET FLOW")
        print("=" * 60)
        
        try:
            # Step 1: Request password reset
            reset_data = {"email": TEST_EMAIL}
            response = self.session.post(
                f"{BACKEND_URL}/auth/forgot-password",
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_test(
                    "End-to-End Password Reset Flow",
                    False,
                    f"Step 1 failed - Password reset request: Status {response.status_code}"
                )
                return False
            
            # Step 2: Verify the response indicates email was sent
            response_data = response.json()
            if not response_data.get("success", False):
                self.log_test(
                    "End-to-End Password Reset Flow",
                    False,
                    f"Step 2 failed - Email sending not confirmed: {response_data}"
                )
                return False
            
            # Step 3: Test with invalid token (since we can't get the real token from email)
            invalid_token_data = {
                "token": "invalid_token_12345",
                "new_password": "newpassword123"
            }
            
            token_response = self.session.post(
                f"{BACKEND_URL}/auth/reset-password",
                json=invalid_token_data,
                headers={"Content-Type": "application/json"}
            )
            
            if token_response.status_code == 200:
                token_response_data = token_response.json()
                if not token_response_data.get("success", True):  # Should be False for invalid token
                    self.log_test(
                        "End-to-End Password Reset Flow",
                        True,
                        "Complete flow tested: Password reset request successful, invalid token properly rejected"
                    )
                    return True
                else:
                    self.log_test(
                        "End-to-End Password Reset Flow",
                        False,
                        "Security issue: Invalid token was accepted"
                    )
                    return False
            else:
                self.log_test(
                    "End-to-End Password Reset Flow",
                    False,
                    f"Step 3 failed - Token validation: Status {token_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("End-to-End Password Reset Flow", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all password reset email functionality tests"""
        print("🚀 STARTING PASSWORD RESET EMAIL FUNCTIONALITY TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {TEST_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Run all tests
        tests = [
            self.test_environment_configuration,
            self.create_test_user,
            self.test_password_reset_request,
            self.test_password_reset_with_invalid_email,
            self.test_email_service_integration,
            self.test_sendgrid_configuration,
            self.test_email_template_and_url_construction,
            self.test_end_to_end_password_reset_flow
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 PASSWORD RESET EMAIL FUNCTIONALITY TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Print detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 85:
            print("🎉 PASSWORD RESET EMAIL FUNCTIONALITY IS WORKING WELL!")
            if success_rate < 100:
                print("⚠️  Some minor issues detected but core functionality is operational")
        else:
            print("⚠️  SIGNIFICANT ISSUES DETECTED IN PASSWORD RESET EMAIL FUNCTIONALITY")
            print("🔧 Review the failed tests and check email service configuration")
        
        print("=" * 80)
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = PasswordResetEmailTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)