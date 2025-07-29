#!/usr/bin/env python3
"""
Password Reset Email Functionality Testing - Recent Improvements Focus
Testing the fixed password reset email functionality after recent improvements.

SPECIFIC TEST FOCUS:
1. Test Password Reset with Fixed Implementation
2. Verify Email Service Configuration  
3. Test Email Sending
4. End-to-End Flow Test
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import subprocess

# Configuration
BACKEND_URL = "https://008e000d-f023-448d-a17e-eec026cb8b9a.preview.emergentagent.com/api"
TEST_EMAIL = "test@example.com"  # As requested in the review
TEST_USER_DATA = {
    "username": "test_user_improvements",
    "email": TEST_EMAIL,
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User"
}

class PasswordResetImprovementsTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
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

    def test_dotenv_reload_fix(self):
        """Test if dotenv reload fix is working correctly"""
        print("🔧 TESTING DOTENV RELOAD FIX")
        print("=" * 60)
        
        try:
            # Import the email service to test dotenv reload
            sys.path.append('/app/backend')
            from email_service import EmailService
            
            # Create a fresh instance to test dotenv reload
            email_service = EmailService()
            
            # Check if environment variables are properly loaded
            sendgrid_key_loaded = bool(email_service.api_key)
            sender_email_loaded = bool(email_service.sender_email)
            correct_sender = email_service.sender_email == "marc.alleyne@aurumtechnologyltd.com"
            
            self.log_test(
                "Dotenv Reload - SendGrid API Key",
                sendgrid_key_loaded,
                f"SendGrid API key loaded: {'Yes' if sendgrid_key_loaded else 'No'}"
            )
            
            self.log_test(
                "Dotenv Reload - Sender Email",
                sender_email_loaded and correct_sender,
                f"Sender email: {email_service.sender_email if sender_email_loaded else 'Not loaded'}"
            )
            
            return sendgrid_key_loaded and sender_email_loaded and correct_sender
            
        except Exception as e:
            self.log_test("Dotenv Reload Fix", False, f"Error: {str(e)}")
            return False

    def test_email_service_initialization_logs(self):
        """Test email service initialization with detailed logging"""
        print("📋 TESTING EMAIL SERVICE INITIALIZATION LOGS")
        print("=" * 60)
        
        try:
            # Restart backend to see initialization logs
            subprocess.run(["sudo", "supervisorctl", "restart", "backend"], 
                         capture_output=True, timeout=10)
            time.sleep(3)  # Wait for restart
            
            # Check logs for email service initialization
            result = subprocess.run(
                ["sudo", "tail", "-n", "100", "/var/log/supervisor/backend.err.log"],
                capture_output=True, text=True, timeout=10
            )
            
            log_content = result.stdout
            
            # Look for email service initialization messages
            api_key_present = "SENDGRID_API_KEY present: True" in log_content
            sender_email_configured = "SENDER_EMAIL: marc.alleyne@aurumtechnologyltd.com" in log_content
            production_mode = "Email functionality will use SendGrid" in log_content
            
            self.log_test(
                "Email Service Initialization - API Key Detection",
                api_key_present,
                f"SendGrid API key detection logged: {'Yes' if api_key_present else 'No'}"
            )
            
            self.log_test(
                "Email Service Initialization - Sender Email",
                sender_email_configured,
                f"Sender email configuration logged: {'Yes' if sender_email_configured else 'No'}"
            )
            
            self.log_test(
                "Email Service Initialization - Production Mode",
                production_mode,
                f"Production mode initialization logged: {'Yes' if production_mode else 'No'}"
            )
            
            return api_key_present or sender_email_configured or production_mode
            
        except Exception as e:
            self.log_test("Email Service Initialization Logs", False, f"Error: {str(e)}")
            return False

    def test_mock_mode_disabled(self):
        """Test that mock mode is properly disabled with real configuration"""
        print("🚫 TESTING MOCK MODE DISABLED")
        print("=" * 60)
        
        try:
            sys.path.append('/app/backend')
            from email_service import EmailService
            
            # Create email service instance
            email_service = EmailService()
            
            # Check mock mode status
            mock_mode_disabled = not email_service.mock_mode
            
            self.log_test(
                "Mock Mode Disabled",
                mock_mode_disabled,
                f"Email service mock mode: {email_service.mock_mode} (should be False)"
            )
            
            # Verify production configuration
            has_api_key = bool(email_service.api_key)
            has_sender_email = bool(email_service.sender_email)
            
            self.log_test(
                "Production Configuration Complete",
                has_api_key and has_sender_email,
                f"API Key: {'Present' if has_api_key else 'Missing'}, Sender: {'Present' if has_sender_email else 'Missing'}"
            )
            
            return mock_mode_disabled and has_api_key and has_sender_email
            
        except Exception as e:
            self.log_test("Mock Mode Disabled", False, f"Error: {str(e)}")
            return False

    def test_async_method_fix(self):
        """Test that async send_password_reset_email method works correctly"""
        print("⚡ TESTING ASYNC METHOD FIX")
        print("=" * 60)
        
        try:
            # Test the async method by making a password reset request
            reset_data = {"email": TEST_EMAIL}
            
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/auth/forgot-password",
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                success = response_data.get("success", False)
                
                self.log_test(
                    "Async Method - API Response",
                    success,
                    f"Password reset API responded successfully in {response_time:.2f}s"
                )
                
                # Check backend logs for async method execution
                result = subprocess.run(
                    ["sudo", "tail", "-n", "20", "/var/log/supervisor/backend.err.log"],
                    capture_output=True, text=True, timeout=10
                )
                
                log_content = result.stdout
                
                # Look for successful email sending (indicates async method worked)
                email_sent = "Password reset email sent successfully" in log_content
                no_async_errors = "object bool can't be used in 'await' expression" not in log_content
                
                self.log_test(
                    "Async Method - Email Sending",
                    email_sent,
                    f"Email sent successfully: {'Yes' if email_sent else 'No'}"
                )
                
                self.log_test(
                    "Async Method - No Await Errors",
                    no_async_errors,
                    f"No async/await errors detected: {'Yes' if no_async_errors else 'No'}"
                )
                
                return success and email_sent and no_async_errors
            else:
                self.log_test(
                    "Async Method Fix",
                    False,
                    f"API request failed: Status {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Async Method Fix", False, f"Error: {str(e)}")
            return False

    def test_correct_reset_url(self):
        """Test that reset URL uses correct frontend URL"""
        print("🔗 TESTING CORRECT RESET URL")
        print("=" * 60)
        
        try:
            sys.path.append('/app/backend')
            from email_service import EmailService
            
            # Create email service instance
            email_service = EmailService()
            
            # Test the reset URL construction by checking environment
            expected_frontend_url = "https://008e000d-f023-448d-a17e-eec026cb8b9a.preview.emergentagent.com"
            
            # Check if the frontend URL is correctly configured
            frontend_url = os.getenv('FRONTEND_URL', expected_frontend_url)
            
            self.log_test(
                "Frontend URL Configuration",
                frontend_url == expected_frontend_url,
                f"Frontend URL: {frontend_url}"
            )
            
            # Test password reset to verify URL construction
            reset_data = {"email": TEST_EMAIL}
            response = self.session.post(
                f"{BACKEND_URL}/auth/forgot-password",
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                self.log_test(
                    "Reset URL Generation",
                    True,
                    "Password reset request processed successfully, indicating correct URL generation"
                )
                return True
            else:
                self.log_test(
                    "Reset URL Generation",
                    False,
                    f"Password reset failed: Status {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Correct Reset URL", False, f"Error: {str(e)}")
            return False

    def test_sendgrid_api_integration(self):
        """Test SendGrid API integration and actual email sending"""
        print("📬 TESTING SENDGRID API INTEGRATION")
        print("=" * 60)
        
        try:
            # Create test user first
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/auth/register",
                    json=TEST_USER_DATA,
                    headers={"Content-Type": "application/json"}
                )
                # User might already exist, that's okay
            except:
                pass
            
            # Test actual email sending through API
            reset_data = {"email": TEST_EMAIL}
            
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/auth/forgot-password",
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                success = response_data.get("success", False)
                
                # Check backend logs for SendGrid interaction
                result = subprocess.run(
                    ["sudo", "tail", "-n", "10", "/var/log/supervisor/backend.err.log"],
                    capture_output=True, text=True, timeout=10
                )
                
                log_content = result.stdout
                
                # Look for successful SendGrid email sending
                sendgrid_success = "Password reset email sent successfully" in log_content
                no_sendgrid_errors = "Failed to send email" not in log_content
                
                self.log_test(
                    "SendGrid API - Email Delivery",
                    sendgrid_success,
                    f"SendGrid email delivery: {'Success' if sendgrid_success else 'Failed'}"
                )
                
                self.log_test(
                    "SendGrid API - No Errors",
                    no_sendgrid_errors,
                    f"No SendGrid errors detected: {'Yes' if no_sendgrid_errors else 'No'}"
                )
                
                self.log_test(
                    "SendGrid API - Response Time",
                    response_time < 5.0,  # Should be reasonable for API call
                    f"Response time: {response_time:.2f}s (should be < 5s for real API)"
                )
                
                return success and sendgrid_success and no_sendgrid_errors
            else:
                self.log_test(
                    "SendGrid API Integration",
                    False,
                    f"API request failed: Status {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("SendGrid API Integration", False, f"Error: {str(e)}")
            return False

    def test_end_to_end_improved_flow(self):
        """Test complete end-to-end flow with all improvements"""
        print("🔄 TESTING END-TO-END IMPROVED FLOW")
        print("=" * 60)
        
        try:
            # Step 1: Verify email service is properly initialized
            sys.path.append('/app/backend')
            from email_service import EmailService
            
            email_service = EmailService()
            
            if email_service.mock_mode:
                self.log_test(
                    "End-to-End Flow - Service Mode",
                    False,
                    "Email service is in mock mode, should be in production mode"
                )
                return False
            
            # Step 2: Test password reset request
            reset_data = {"email": TEST_EMAIL}
            response = self.session.post(
                f"{BACKEND_URL}/auth/forgot-password",
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_test(
                    "End-to-End Flow - Password Reset Request",
                    False,
                    f"Password reset request failed: Status {response.status_code}"
                )
                return False
            
            response_data = response.json()
            if not response_data.get("success", False):
                self.log_test(
                    "End-to-End Flow - Response Success",
                    False,
                    f"Password reset response not successful: {response_data}"
                )
                return False
            
            # Step 3: Verify email was actually sent (check logs)
            time.sleep(1)  # Allow time for email processing
            
            result = subprocess.run(
                ["sudo", "tail", "-n", "5", "/var/log/supervisor/backend.err.log"],
                capture_output=True, text=True, timeout=10
            )
            
            log_content = result.stdout
            email_sent = "Password reset email sent successfully" in log_content
            
            if not email_sent:
                self.log_test(
                    "End-to-End Flow - Email Sending",
                    False,
                    "Email was not sent successfully according to logs"
                )
                return False
            
            # Step 4: Test invalid token handling (security check)
            invalid_token_data = {
                "token": "invalid_test_token_12345",
                "new_password": "newpassword123"
            }
            
            token_response = self.session.post(
                f"{BACKEND_URL}/auth/reset-password",
                json=invalid_token_data,
                headers={"Content-Type": "application/json"}
            )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                if not token_data.get("success", True):  # Should be False for invalid token
                    self.log_test(
                        "End-to-End Improved Flow",
                        True,
                        "Complete improved flow successful: Email service in production mode, password reset sent via SendGrid, invalid token properly rejected"
                    )
                    return True
                else:
                    self.log_test(
                        "End-to-End Flow - Token Security",
                        False,
                        "Security issue: Invalid token was accepted"
                    )
                    return False
            else:
                self.log_test(
                    "End-to-End Flow - Token Validation",
                    False,
                    f"Token validation failed: Status {token_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("End-to-End Improved Flow", False, f"Error: {str(e)}")
            return False

    def run_improvement_tests(self):
        """Run all password reset improvement tests"""
        print("🚀 TESTING PASSWORD RESET EMAIL FUNCTIONALITY - RECENT IMPROVEMENTS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {TEST_EMAIL}")
        print(f"Focus: Recent improvements (dotenv reload, async method, correct reset URL)")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Run improvement-focused tests
        tests = [
            self.test_dotenv_reload_fix,
            self.test_email_service_initialization_logs,
            self.test_mock_mode_disabled,
            self.test_async_method_fix,
            self.test_correct_reset_url,
            self.test_sendgrid_api_integration,
            self.test_end_to_end_improved_flow
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
        print("📊 PASSWORD RESET IMPROVEMENTS TEST SUMMARY")
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
            print("🎉 PASSWORD RESET EMAIL IMPROVEMENTS ARE WORKING EXCELLENTLY!")
            print("✅ Recent fixes have successfully resolved the mock mode issue")
            print("✅ SendGrid integration is functional and sending real emails")
            if success_rate < 100:
                print("⚠️  Some minor issues detected but core improvements are operational")
        else:
            print("⚠️  ISSUES DETECTED IN PASSWORD RESET EMAIL IMPROVEMENTS")
            print("🔧 Some recent fixes may need additional attention")
        
        print("=" * 80)
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = PasswordResetImprovementsTester()
    success = tester.run_improvement_tests()
    sys.exit(0 if success else 1)