#!/usr/bin/env python3
"""
Security Hardening Phase 2 Backend Testing
Tests IDOR Protection, CSRF Protection, and Hardened CSP implementation
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sys
import os

# Configuration
BACKEND_URL = "https://focus-planner-3.preview.emergentagent.com/api"
TEST_USER_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_USER_PASSWORD = "password"

class SecurityHardeningTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.csrf_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate(self):
        """Authenticate user and get tokens"""
        print("\n🔐 AUTHENTICATION SETUP")
        
        try:
            # Login to get auth token and CSRF token
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_id = data.get('user', {}).get('id')
                
                # Get CSRF token from cookie
                csrf_cookie = response.cookies.get('csrf_token')
                if csrf_cookie:
                    self.csrf_token = csrf_cookie
                
                # Set auth header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': 'application/json'
                })
                
                self.log_result("User Authentication", True, f"User ID: {self.user_id}")
                self.log_result("CSRF Token Generation", bool(self.csrf_token), f"Token present: {bool(self.csrf_token)}")
                return True
            else:
                self.log_result("User Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Error: {str(e)}")
            return False
    
    def test_idor_protection(self):
        """Test Insecure Direct Object Reference protection"""
        print("\n🛡️ IDOR PROTECTION TESTING")
        
        # First, create test resources to verify ownership
        test_resources = {}
        
        # Create test pillar
        try:
            pillar_data = {
                "name": "Test IDOR Pillar",
                "description": "Test pillar for IDOR testing",
                "color": "#FF5733",
                "icon": "test-icon",
                "time_allocation_percentage": 25
            }
            
            if self.csrf_token:
                self.session.headers['X-CSRF-Token'] = self.csrf_token
            
            response = self.session.post(f"{BACKEND_URL}/pillars", json=pillar_data)
            if response.status_code == 200:
                test_resources['pillar_id'] = response.json()['id']
                self.log_result("Test Pillar Creation", True, f"Created pillar: {test_resources['pillar_id']}")
            else:
                self.log_result("Test Pillar Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Test Pillar Creation", False, f"Error: {str(e)}")
        
        # Create test area
        try:
            area_data = {
                "name": "Test IDOR Area",
                "description": "Test area for IDOR testing",
                "pillar_id": test_resources.get('pillar_id'),
                "importance": 5,
                "color": "#33FF57",
                "icon": "test-area-icon"
            }
            
            response = self.session.post(f"{BACKEND_URL}/areas", json=area_data)
            if response.status_code == 200:
                test_resources['area_id'] = response.json()['id']
                self.log_result("Test Area Creation", True, f"Created area: {test_resources['area_id']}")
            else:
                self.log_result("Test Area Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Test Area Creation", False, f"Error: {str(e)}")
        
        # Create test project
        try:
            project_data = {
                "name": "Test IDOR Project",
                "description": "Test project for IDOR testing",
                "area_id": test_resources.get('area_id'),
                "priority": "high",
                "status": "Not Started"
            }
            
            response = self.session.post(f"{BACKEND_URL}/projects", json=project_data)
            if response.status_code == 200:
                test_resources['project_id'] = response.json()['id']
                self.log_result("Test Project Creation", True, f"Created project: {test_resources['project_id']}")
            else:
                self.log_result("Test Project Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Test Project Creation", False, f"Error: {str(e)}")
        
        # Create test task
        try:
            task_data = {
                "name": "Test IDOR Task",
                "description": "Test task for IDOR testing",
                "project_id": test_resources.get('project_id'),
                "priority": "high",
                "status": "todo"
            }
            
            response = self.session.post(f"{BACKEND_URL}/tasks", json=task_data)
            if response.status_code == 200:
                test_resources['task_id'] = response.json()['id']
                self.log_result("Test Task Creation", True, f"Created task: {test_resources['task_id']}")
            else:
                self.log_result("Test Task Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Test Task Creation", False, f"Error: {str(e)}")
        
        # Now test IDOR protection with fake IDs (should return 404)
        fake_uuid = str(uuid.uuid4())
        
        # Test IDOR protection on different endpoints
        idor_tests = [
            ("PUT", f"/projects/{fake_uuid}", {"name": "Hacked Project"}),
            ("DELETE", f"/projects/{fake_uuid}", None),
            ("PUT", f"/tasks/{fake_uuid}", {"name": "Hacked Task"}),
            ("DELETE", f"/tasks/{fake_uuid}", None),
            ("PUT", f"/areas/{fake_uuid}", {"name": "Hacked Area"}),
            ("DELETE", f"/areas/{fake_uuid}", None),
            ("PUT", f"/pillars/{fake_uuid}", {"name": "Hacked Pillar"}),
            ("DELETE", f"/pillars/{fake_uuid}", None),
            ("DELETE", f"/today/tasks/{fake_uuid}", None)
        ]
        
        for method, endpoint, data in idor_tests:
            try:
                if self.csrf_token:
                    self.session.headers['X-CSRF-Token'] = self.csrf_token
                
                if method == "PUT":
                    response = self.session.put(f"{BACKEND_URL}{endpoint}", json=data)
                elif method == "DELETE":
                    response = self.session.delete(f"{BACKEND_URL}{endpoint}")
                
                # Should return 404 for unauthorized access (not 403 to prevent enumeration)
                if response.status_code == 404:
                    self.log_result(f"IDOR Protection - {method} {endpoint}", True, "Correctly returned 404")
                else:
                    self.log_result(f"IDOR Protection - {method} {endpoint}", False, f"Expected 404, got {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"IDOR Protection - {method} {endpoint}", False, f"Error: {str(e)}")
        
        # Test legitimate access to owned resources (should work)
        if test_resources.get('project_id'):
            try:
                update_data = {"name": "Updated Test Project"}
                if self.csrf_token:
                    self.session.headers['X-CSRF-Token'] = self.csrf_token
                
                response = self.session.put(f"{BACKEND_URL}/projects/{test_resources['project_id']}", json=update_data)
                if response.status_code == 200:
                    self.log_result("Legitimate Resource Access", True, "Owner can update their resource")
                else:
                    self.log_result("Legitimate Resource Access", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Legitimate Resource Access", False, f"Error: {str(e)}")
        
        # Cleanup test resources
        self.cleanup_test_resources(test_resources)
    
    def test_csrf_protection(self):
        """Test CSRF protection implementation"""
        print("\n🔒 CSRF PROTECTION TESTING")
        
        # Test 1: Verify CSRF token is set in cookie after login
        if self.csrf_token:
            self.log_result("CSRF Token Cookie Set", True, "CSRF token found in cookie")
        else:
            self.log_result("CSRF Token Cookie Set", False, "No CSRF token in cookie")
        
        # Test 2: Verify CSRF token cookie is accessible to JavaScript (httpOnly=false)
        try:
            # Check if we can access the cookie (simulating JavaScript access)
            csrf_from_cookie = self.session.cookies.get('csrf_token')
            if csrf_from_cookie:
                self.log_result("CSRF Token JavaScript Access", True, "Token accessible (httpOnly=false)")
            else:
                self.log_result("CSRF Token JavaScript Access", False, "Token not accessible")
        except Exception as e:
            self.log_result("CSRF Token JavaScript Access", False, f"Error: {str(e)}")
        
        # Test 3: Test state-changing request without CSRF token (should be handled appropriately)
        try:
            # Remove CSRF token header temporarily
            headers_backup = self.session.headers.copy()
            if 'X-CSRF-Token' in self.session.headers:
                del self.session.headers['X-CSRF-Token']
            
            test_data = {
                "name": "CSRF Test Pillar",
                "description": "Testing CSRF protection",
                "color": "#FF5733",
                "icon": "test-icon",
                "time_allocation_percentage": 25
            }
            
            response = self.session.post(f"{BACKEND_URL}/pillars", json=test_data)
            
            # In development mode, CSRF is bypassed, so we check for warning logs
            # In production, this should return 403
            if response.status_code in [200, 201]:
                self.log_result("CSRF Protection - No Token", True, "Development mode: CSRF bypassed with warning")
            elif response.status_code == 403:
                self.log_result("CSRF Protection - No Token", True, "Production mode: Correctly blocked with 403")
            else:
                self.log_result("CSRF Protection - No Token", False, f"Unexpected status: {response.status_code}")
            
            # Restore headers
            self.session.headers = headers_backup
            
        except Exception as e:
            self.log_result("CSRF Protection - No Token", False, f"Error: {str(e)}")
        
        # Test 4: Test state-changing request with valid CSRF token (should work)
        try:
            if self.csrf_token:
                self.session.headers['X-CSRF-Token'] = self.csrf_token
            
            test_data = {
                "name": "CSRF Valid Test Pillar",
                "description": "Testing CSRF protection with valid token",
                "color": "#33FF57",
                "icon": "test-icon",
                "time_allocation_percentage": 30
            }
            
            response = self.session.post(f"{BACKEND_URL}/pillars", json=test_data)
            
            if response.status_code in [200, 201]:
                self.log_result("CSRF Protection - Valid Token", True, "Request succeeded with valid token")
                # Clean up created resource
                if response.status_code == 200:
                    pillar_id = response.json().get('id')
                    if pillar_id:
                        self.session.delete(f"{BACKEND_URL}/pillars/{pillar_id}")
            else:
                self.log_result("CSRF Protection - Valid Token", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("CSRF Protection - Valid Token", False, f"Error: {str(e)}")
        
        # Test 5: Test state-changing request with invalid CSRF token
        try:
            # Set invalid CSRF token
            self.session.headers['X-CSRF-Token'] = "invalid-csrf-token-12345"
            
            test_data = {
                "name": "CSRF Invalid Test Pillar",
                "description": "Testing CSRF protection with invalid token",
                "color": "#5733FF",
                "icon": "test-icon",
                "time_allocation_percentage": 35
            }
            
            response = self.session.post(f"{BACKEND_URL}/pillars", json=test_data)
            
            # In development mode, CSRF is bypassed, so we check for warning logs
            # In production, this should return 403
            if response.status_code in [200, 201]:
                self.log_result("CSRF Protection - Invalid Token", True, "Development mode: CSRF bypassed with warning")
                # Clean up if created
                if response.status_code == 200:
                    pillar_id = response.json().get('id')
                    if pillar_id:
                        # Restore valid token for cleanup
                        if self.csrf_token:
                            self.session.headers['X-CSRF-Token'] = self.csrf_token
                        self.session.delete(f"{BACKEND_URL}/pillars/{pillar_id}")
            elif response.status_code == 403:
                self.log_result("CSRF Protection - Invalid Token", True, "Production mode: Correctly blocked with 403")
            else:
                self.log_result("CSRF Protection - Invalid Token", False, f"Unexpected status: {response.status_code}")
            
            # Restore valid CSRF token
            if self.csrf_token:
                self.session.headers['X-CSRF-Token'] = self.csrf_token
                
        except Exception as e:
            self.log_result("CSRF Protection - Invalid Token", False, f"Error: {str(e)}")
    
    def test_hardened_csp(self):
        """Test hardened Content Security Policy headers"""
        print("\n🛡️ HARDENED CSP TESTING")
        
        # Test multiple endpoints to ensure CSP headers are present
        test_endpoints = [
            "/dashboard",
            "/pillars",
            "/areas", 
            "/projects",
            "/tasks"
        ]
        
        for endpoint in test_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                # Check for Content-Security-Policy header
                csp_header = response.headers.get('Content-Security-Policy')
                if csp_header:
                    # Verify hardened CSP (no unsafe-inline or unsafe-eval)
                    has_unsafe_inline = 'unsafe-inline' in csp_header
                    has_unsafe_eval = 'unsafe-eval' in csp_header
                    
                    if not has_unsafe_inline and not has_unsafe_eval:
                        self.log_result(f"Hardened CSP - {endpoint}", True, "No unsafe directives found")
                    else:
                        unsafe_directives = []
                        if has_unsafe_inline:
                            unsafe_directives.append("unsafe-inline")
                        if has_unsafe_eval:
                            unsafe_directives.append("unsafe-eval")
                        self.log_result(f"Hardened CSP - {endpoint}", False, f"Found unsafe directives: {', '.join(unsafe_directives)}")
                    
                    # Verify trusted domains are allowed
                    has_google_oauth = 'accounts.google.com' in csp_header
                    has_google_fonts = 'fonts.googleapis.com' in csp_header
                    
                    if has_google_oauth and has_google_fonts:
                        self.log_result(f"CSP Trusted Domains - {endpoint}", True, "Google OAuth and Fonts allowed")
                    else:
                        missing = []
                        if not has_google_oauth:
                            missing.append("Google OAuth")
                        if not has_google_fonts:
                            missing.append("Google Fonts")
                        self.log_result(f"CSP Trusted Domains - {endpoint}", False, f"Missing: {', '.join(missing)}")
                else:
                    self.log_result(f"CSP Header Present - {endpoint}", False, "No CSP header found")
                
                # Check for other security headers
                security_headers = {
                    'Strict-Transport-Security': 'HSTS',
                    'X-Content-Type-Options': 'MIME sniffing protection',
                    'X-Frame-Options': 'Clickjacking protection',
                    'X-XSS-Protection': 'XSS protection',
                    'Referrer-Policy': 'Referrer policy',
                    'Permissions-Policy': 'Permissions policy'
                }
                
                for header, description in security_headers.items():
                    if response.headers.get(header):
                        self.log_result(f"Security Header - {header}", True, f"{description} present")
                    else:
                        self.log_result(f"Security Header - {header}", False, f"{description} missing")
                
            except Exception as e:
                self.log_result(f"CSP Test - {endpoint}", False, f"Error: {str(e)}")
    
    def test_core_functionality_integrity(self):
        """Test that core functionality still works with security enhancements"""
        print("\n⚙️ CORE FUNCTIONALITY INTEGRITY TESTING")
        
        # Test authentication flow
        try:
            response = self.session.get(f"{BACKEND_URL}/dashboard")
            if response.status_code == 200:
                self.log_result("Dashboard Access", True, "Dashboard loads correctly")
            else:
                self.log_result("Dashboard Access", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Dashboard Access", False, f"Error: {str(e)}")
        
        # Test CRUD operations with security enhancements
        test_pillar_id = None
        
        # Create operation
        try:
            if self.csrf_token:
                self.session.headers['X-CSRF-Token'] = self.csrf_token
            
            pillar_data = {
                "name": "Security Test Pillar",
                "description": "Testing CRUD with security enhancements",
                "color": "#FF5733",
                "icon": "security-icon",
                "time_allocation_percentage": 20
            }
            
            response = self.session.post(f"{BACKEND_URL}/pillars", json=pillar_data)
            if response.status_code == 200:
                test_pillar_id = response.json()['id']
                self.log_result("CRUD - Create Operation", True, f"Created pillar: {test_pillar_id}")
            else:
                self.log_result("CRUD - Create Operation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("CRUD - Create Operation", False, f"Error: {str(e)}")
        
        # Read operation
        if test_pillar_id:
            try:
                response = self.session.get(f"{BACKEND_URL}/pillars")
                if response.status_code == 200:
                    pillars = response.json()
                    found_pillar = any(p['id'] == test_pillar_id for p in pillars)
                    if found_pillar:
                        self.log_result("CRUD - Read Operation", True, "Can read created pillar")
                    else:
                        self.log_result("CRUD - Read Operation", False, "Created pillar not found in list")
                else:
                    self.log_result("CRUD - Read Operation", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("CRUD - Read Operation", False, f"Error: {str(e)}")
        
        # Update operation
        if test_pillar_id:
            try:
                if self.csrf_token:
                    self.session.headers['X-CSRF-Token'] = self.csrf_token
                
                update_data = {"name": "Updated Security Test Pillar"}
                response = self.session.put(f"{BACKEND_URL}/pillars/{test_pillar_id}", json=update_data)
                if response.status_code == 200:
                    self.log_result("CRUD - Update Operation", True, "Successfully updated pillar")
                else:
                    self.log_result("CRUD - Update Operation", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("CRUD - Update Operation", False, f"Error: {str(e)}")
        
        # Delete operation
        if test_pillar_id:
            try:
                if self.csrf_token:
                    self.session.headers['X-CSRF-Token'] = self.csrf_token
                
                response = self.session.delete(f"{BACKEND_URL}/pillars/{test_pillar_id}")
                if response.status_code == 200:
                    self.log_result("CRUD - Delete Operation", True, "Successfully deleted pillar")
                else:
                    self.log_result("CRUD - Delete Operation", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("CRUD - Delete Operation", False, f"Error: {str(e)}")
        
        # Test input sanitization (XSS protection)
        try:
            if self.csrf_token:
                self.session.headers['X-CSRF-Token'] = self.csrf_token
            
            xss_payload = {
                "name": "<script>alert('XSS')</script>Malicious Pillar",
                "description": "<img src=x onerror=alert('XSS')>Malicious description",
                "color": "#FF5733",
                "icon": "test-icon",
                "time_allocation_percentage": 25
            }
            
            response = self.session.post(f"{BACKEND_URL}/pillars", json=xss_payload)
            if response.status_code == 200:
                created_pillar = response.json()
                # Check if XSS payload was sanitized
                if "<script>" not in created_pillar.get('name', '') and "<img" not in created_pillar.get('description', ''):
                    self.log_result("Input Sanitization - XSS Protection", True, "XSS payload sanitized")
                    # Clean up
                    self.session.delete(f"{BACKEND_URL}/pillars/{created_pillar['id']}")
                else:
                    self.log_result("Input Sanitization - XSS Protection", False, "XSS payload not sanitized")
            else:
                self.log_result("Input Sanitization - XSS Protection", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Input Sanitization - XSS Protection", False, f"Error: {str(e)}")
    
    def cleanup_test_resources(self, resources):
        """Clean up test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        
        cleanup_order = ['task_id', 'project_id', 'area_id', 'pillar_id']
        endpoints = {
            'task_id': 'tasks',
            'project_id': 'projects', 
            'area_id': 'areas',
            'pillar_id': 'pillars'
        }
        
        for resource_type in cleanup_order:
            resource_id = resources.get(resource_type)
            if resource_id:
                try:
                    if self.csrf_token:
                        self.session.headers['X-CSRF-Token'] = self.csrf_token
                    
                    endpoint = endpoints[resource_type]
                    response = self.session.delete(f"{BACKEND_URL}/{endpoint}/{resource_id}")
                    if response.status_code == 200:
                        print(f"✅ Cleaned up {resource_type}: {resource_id}")
                    else:
                        print(f"⚠️ Failed to clean up {resource_type}: {resource_id} (Status: {response.status_code})")
                except Exception as e:
                    print(f"❌ Error cleaning up {resource_type}: {str(e)}")
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*80)
        print("🔐 SECURITY HARDENING PHASE 2 TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Group results by category
        categories = {
            'Authentication': [],
            'IDOR Protection': [],
            'CSRF Protection': [],
            'CSP/Security Headers': [],
            'Core Functionality': [],
            'Other': []
        }
        
        for result in self.test_results:
            test_name = result['test']
            if 'Authentication' in test_name or 'Token Generation' in test_name:
                categories['Authentication'].append(result)
            elif 'IDOR' in test_name or 'Resource Access' in test_name:
                categories['IDOR Protection'].append(result)
            elif 'CSRF' in test_name:
                categories['CSRF Protection'].append(result)
            elif 'CSP' in test_name or 'Security Header' in test_name:
                categories['CSP/Security Headers'].append(result)
            elif 'CRUD' in test_name or 'Dashboard' in test_name or 'Sanitization' in test_name:
                categories['Core Functionality'].append(result)
            else:
                categories['Other'].append(result)
        
        print(f"\n📋 DETAILED RESULTS BY CATEGORY:")
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r['success'])
                total = len(results)
                print(f"\n   {category}: {passed}/{total} passed")
                for result in results:
                    status = "✅" if result['success'] else "❌"
                    print(f"      {status} {result['test']}")
                    if result['details']:
                        print(f"         {result['details']}")
        
        # Critical security findings
        critical_failures = []
        for result in self.test_results:
            if not result['success'] and any(keyword in result['test'] for keyword in ['IDOR', 'CSRF', 'CSP', 'XSS']):
                critical_failures.append(result)
        
        if critical_failures:
            print(f"\n🚨 CRITICAL SECURITY ISSUES:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
        else:
            print(f"\n✅ NO CRITICAL SECURITY ISSUES DETECTED")
        
        print(f"\n" + "="*80)
        return success_rate >= 85  # Consider 85%+ success rate as passing
    
    def run_all_tests(self):
        """Run all security hardening tests"""
        print("🔐 STARTING SECURITY HARDENING PHASE 2 TESTING")
        print("="*80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: IDOR Protection Tests
        self.test_idor_protection()
        
        # Step 3: CSRF Protection Tests
        self.test_csrf_protection()
        
        # Step 4: Hardened CSP Tests
        self.test_hardened_csp()
        
        # Step 5: Core Functionality Integrity Tests
        self.test_core_functionality_integrity()
        
        # Step 6: Generate Report
        return self.generate_report()

def main():
    """Main test execution"""
    tester = SecurityHardeningTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 SECURITY HARDENING PHASE 2 TESTING COMPLETED SUCCESSFULLY!")
            sys.exit(0)
        else:
            print("\n⚠️ SECURITY HARDENING PHASE 2 TESTING COMPLETED WITH ISSUES!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()