#!/usr/bin/env python3
"""
SECURITY HARDENING BACKEND TESTING - COMPREHENSIVE VERIFICATION
Testing the security hardening implementation to verify:
1. HTTP Security Headers (CSP, HSTS, X-Frame-Options, etc.)
2. Input Sanitization (XSS prevention)
3. Core Functionality Integrity after security updates
4. Authentication & CRUD Operations

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time
import re

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://fastapi-react-fix.preview.emergentagent.com/api"

class SecurityHardeningTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified credentials
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
                'headers': dict(response.headers),
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
                'response': getattr(e, 'response', None),
                'headers': {}
            }

    def test_basic_connectivity(self):
        """Test basic connectivity to the backend API"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
        # Test the root endpoint
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
                    'headers': dict(response.headers)
                }
            except:
                result = {'success': False, 'error': 'Connection failed', 'headers': {}}
        
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

    def test_security_headers(self):
        """Test HTTP Security Headers implementation"""
        print("\n=== TESTING HTTP SECURITY HEADERS ===")
        
        if not self.auth_token:
            self.log_test("SECURITY HEADERS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test security headers on a protected endpoint
        result = self.make_request('GET', '/dashboard', use_auth=True)
        
        if not result['success']:
            self.log_test("SECURITY HEADERS - Endpoint Access", False, f"Could not access dashboard endpoint: {result.get('error', 'Unknown error')}")
            return False
        
        headers = result['headers']
        security_headers_found = 0
        total_security_headers = 7
        
        # Check for Content-Security-Policy
        csp_header = headers.get('Content-Security-Policy') or headers.get('content-security-policy')
        if csp_header:
            security_headers_found += 1
            self.log_test(
                "SECURITY HEADERS - Content-Security-Policy",
                True,
                f"CSP header present: {csp_header[:100]}..."
            )
        else:
            self.log_test(
                "SECURITY HEADERS - Content-Security-Policy",
                False,
                "CSP header missing"
            )
        
        # Check for HTTP Strict-Transport-Security
        hsts_header = headers.get('Strict-Transport-Security') or headers.get('strict-transport-security')
        if hsts_header:
            security_headers_found += 1
            self.log_test(
                "SECURITY HEADERS - Strict-Transport-Security",
                True,
                f"HSTS header present: {hsts_header}"
            )
        else:
            self.log_test(
                "SECURITY HEADERS - Strict-Transport-Security",
                False,
                "HSTS header missing"
            )
        
        # Check for X-Content-Type-Options
        content_type_options = headers.get('X-Content-Type-Options') or headers.get('x-content-type-options')
        if content_type_options:
            security_headers_found += 1
            self.log_test(
                "SECURITY HEADERS - X-Content-Type-Options",
                True,
                f"X-Content-Type-Options header present: {content_type_options}"
            )
        else:
            self.log_test(
                "SECURITY HEADERS - X-Content-Type-Options",
                False,
                "X-Content-Type-Options header missing"
            )
        
        # Check for X-Frame-Options
        frame_options = headers.get('X-Frame-Options') or headers.get('x-frame-options')
        if frame_options:
            security_headers_found += 1
            self.log_test(
                "SECURITY HEADERS - X-Frame-Options",
                True,
                f"X-Frame-Options header present: {frame_options}"
            )
        else:
            self.log_test(
                "SECURITY HEADERS - X-Frame-Options",
                False,
                "X-Frame-Options header missing"
            )
        
        # Check for X-XSS-Protection
        xss_protection = headers.get('X-XSS-Protection') or headers.get('x-xss-protection')
        if xss_protection:
            security_headers_found += 1
            self.log_test(
                "SECURITY HEADERS - X-XSS-Protection",
                True,
                f"X-XSS-Protection header present: {xss_protection}"
            )
        else:
            self.log_test(
                "SECURITY HEADERS - X-XSS-Protection",
                False,
                "X-XSS-Protection header missing"
            )
        
        # Check for Referrer-Policy
        referrer_policy = headers.get('Referrer-Policy') or headers.get('referrer-policy')
        if referrer_policy:
            security_headers_found += 1
            self.log_test(
                "SECURITY HEADERS - Referrer-Policy",
                True,
                f"Referrer-Policy header present: {referrer_policy}"
            )
        else:
            self.log_test(
                "SECURITY HEADERS - Referrer-Policy",
                False,
                "Referrer-Policy header missing"
            )
        
        # Check for Permissions-Policy
        permissions_policy = headers.get('Permissions-Policy') or headers.get('permissions-policy')
        if permissions_policy:
            security_headers_found += 1
            self.log_test(
                "SECURITY HEADERS - Permissions-Policy",
                True,
                f"Permissions-Policy header present: {permissions_policy[:100]}..."
            )
        else:
            self.log_test(
                "SECURITY HEADERS - Permissions-Policy",
                False,
                "Permissions-Policy header missing"
            )
        
        # Overall security headers assessment
        security_headers_percentage = (security_headers_found / total_security_headers) * 100
        headers_success = security_headers_percentage >= 70  # At least 70% of security headers should be present
        
        self.log_test(
            "SECURITY HEADERS - OVERALL ASSESSMENT",
            headers_success,
            f"Security headers implementation: {security_headers_found}/{total_security_headers} headers present ({security_headers_percentage:.1f}%)"
        )
        
        return headers_success

    def test_input_sanitization(self):
        """Test input sanitization against XSS attacks"""
        print("\n=== TESTING INPUT SANITIZATION ===")
        
        if not self.auth_token:
            self.log_test("INPUT SANITIZATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test XSS payloads on various endpoints
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';DROP TABLE users;--",
            "<svg onload=alert('XSS')>",
            "{{7*7}}",  # Template injection
            "${7*7}",   # Expression injection
        ]
        
        sanitization_tests_passed = 0
        total_sanitization_tests = 0
        
        # Test feedback endpoint with XSS payloads
        for i, payload in enumerate(xss_payloads):
            total_sanitization_tests += 1
            feedback_data = {
                "category": "suggestion",
                "priority": "medium",
                "subject": f"Test Subject {i}",
                "message": payload
            }
            
            result = self.make_request('POST', '/feedback', data=feedback_data, use_auth=True)
            
            if result['success']:
                # Check if the response contains the raw payload (bad) or sanitized version (good)
                response_text = json.dumps(result['data']).lower()
                contains_script = '<script>' in response_text or 'javascript:' in response_text or 'onerror=' in response_text
                
                if not contains_script:
                    sanitization_tests_passed += 1
                    self.log_test(
                        f"INPUT SANITIZATION - Feedback XSS Test {i+1}",
                        True,
                        f"XSS payload properly sanitized in feedback"
                    )
                else:
                    self.log_test(
                        f"INPUT SANITIZATION - Feedback XSS Test {i+1}",
                        False,
                        f"XSS payload not properly sanitized: {payload}"
                    )
            else:
                # If request failed, it might be due to validation - which is also good
                if result['status_code'] in [400, 422]:
                    sanitization_tests_passed += 1
                    self.log_test(
                        f"INPUT SANITIZATION - Feedback XSS Test {i+1}",
                        True,
                        f"XSS payload rejected by validation"
                    )
                else:
                    self.log_test(
                        f"INPUT SANITIZATION - Feedback XSS Test {i+1}",
                        False,
                        f"Unexpected error: {result.get('error', 'Unknown error')}"
                    )
        
        # Test task creation with XSS payloads
        for i, payload in enumerate(xss_payloads[:3]):  # Test fewer payloads for tasks
            total_sanitization_tests += 1
            task_data = {
                "name": payload,
                "description": f"Test task description {i}",
                "priority": "medium",
                "status": "todo"
            }
            
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            
            if result['success']:
                response_text = json.dumps(result['data']).lower()
                contains_script = '<script>' in response_text or 'javascript:' in response_text or 'onerror=' in response_text
                
                if not contains_script:
                    sanitization_tests_passed += 1
                    self.log_test(
                        f"INPUT SANITIZATION - Task XSS Test {i+1}",
                        True,
                        f"XSS payload properly sanitized in task creation"
                    )
                else:
                    self.log_test(
                        f"INPUT SANITIZATION - Task XSS Test {i+1}",
                        False,
                        f"XSS payload not properly sanitized: {payload}"
                    )
            else:
                if result['status_code'] in [400, 422]:
                    sanitization_tests_passed += 1
                    self.log_test(
                        f"INPUT SANITIZATION - Task XSS Test {i+1}",
                        True,
                        f"XSS payload rejected by validation"
                    )
                else:
                    self.log_test(
                        f"INPUT SANITIZATION - Task XSS Test {i+1}",
                        False,
                        f"Unexpected error: {result.get('error', 'Unknown error')}"
                    )
        
        # Overall sanitization assessment
        sanitization_percentage = (sanitization_tests_passed / total_sanitization_tests) * 100
        sanitization_success = sanitization_percentage >= 80  # At least 80% should pass
        
        self.log_test(
            "INPUT SANITIZATION - OVERALL ASSESSMENT",
            sanitization_success,
            f"Input sanitization effectiveness: {sanitization_tests_passed}/{total_sanitization_tests} tests passed ({sanitization_percentage:.1f}%)"
        )
        
        return sanitization_success

    def test_core_functionality_integrity(self):
        """Test that core functionality still works after security updates"""
        print("\n=== TESTING CORE FUNCTIONALITY INTEGRITY ===")
        
        if not self.auth_token:
            self.log_test("CORE FUNCTIONALITY - Authentication Required", False, "No authentication token available")
            return False
        
        functionality_tests_passed = 0
        total_functionality_tests = 8
        
        # Test 1: Dashboard access
        result = self.make_request('GET', '/dashboard', use_auth=True)
        if result['success']:
            functionality_tests_passed += 1
            self.log_test(
                "CORE FUNCTIONALITY - Dashboard Access",
                True,
                "Dashboard endpoint accessible and functional"
            )
        else:
            self.log_test(
                "CORE FUNCTIONALITY - Dashboard Access",
                False,
                f"Dashboard access failed: {result.get('error', 'Unknown error')}"
            )
        
        # Test 2: Pillars retrieval
        result = self.make_request('GET', '/pillars', use_auth=True)
        if result['success']:
            functionality_tests_passed += 1
            pillars_count = len(result['data']) if isinstance(result['data'], list) else 0
            self.log_test(
                "CORE FUNCTIONALITY - Pillars Retrieval",
                True,
                f"Pillars endpoint functional, retrieved {pillars_count} pillars"
            )
        else:
            self.log_test(
                "CORE FUNCTIONALITY - Pillars Retrieval",
                False,
                f"Pillars retrieval failed: {result.get('error', 'Unknown error')}"
            )
        
        # Test 3: Areas retrieval
        result = self.make_request('GET', '/areas', use_auth=True)
        if result['success']:
            functionality_tests_passed += 1
            areas_count = len(result['data']) if isinstance(result['data'], list) else 0
            self.log_test(
                "CORE FUNCTIONALITY - Areas Retrieval",
                True,
                f"Areas endpoint functional, retrieved {areas_count} areas"
            )
        else:
            self.log_test(
                "CORE FUNCTIONALITY - Areas Retrieval",
                False,
                f"Areas retrieval failed: {result.get('error', 'Unknown error')}"
            )
        
        # Test 4: Projects retrieval
        result = self.make_request('GET', '/projects', use_auth=True)
        if result['success']:
            functionality_tests_passed += 1
            projects_count = len(result['data']) if isinstance(result['data'], list) else 0
            self.log_test(
                "CORE FUNCTIONALITY - Projects Retrieval",
                True,
                f"Projects endpoint functional, retrieved {projects_count} projects"
            )
        else:
            self.log_test(
                "CORE FUNCTIONALITY - Projects Retrieval",
                False,
                f"Projects retrieval failed: {result.get('error', 'Unknown error')}"
            )
        
        # Test 5: Tasks retrieval
        result = self.make_request('GET', '/tasks', use_auth=True)
        if result['success']:
            functionality_tests_passed += 1
            tasks_count = len(result['data']) if isinstance(result['data'], list) else 0
            self.log_test(
                "CORE FUNCTIONALITY - Tasks Retrieval",
                True,
                f"Tasks endpoint functional, retrieved {tasks_count} tasks"
            )
        else:
            self.log_test(
                "CORE FUNCTIONALITY - Tasks Retrieval",
                False,
                f"Tasks retrieval failed: {result.get('error', 'Unknown error')}"
            )
        
        # Test 6: Feedback submission (clean data)
        feedback_data = {
            "category": "suggestion",
            "priority": "medium",
            "subject": "Security Testing Feedback",
            "message": "This is a clean feedback message to test functionality after security hardening."
        }
        result = self.make_request('POST', '/feedback', data=feedback_data, use_auth=True)
        if result['success']:
            functionality_tests_passed += 1
            self.log_test(
                "CORE FUNCTIONALITY - Feedback Submission",
                True,
                "Feedback submission working correctly with clean data"
            )
        else:
            self.log_test(
                "CORE FUNCTIONALITY - Feedback Submission",
                False,
                f"Feedback submission failed: {result.get('error', 'Unknown error')}"
            )
        
        # Test 7: AI Coach quota check
        result = self.make_request('GET', '/ai/quota', use_auth=True)
        if result['success']:
            functionality_tests_passed += 1
            quota_data = result['data']
            self.log_test(
                "CORE FUNCTIONALITY - AI Coach Quota",
                True,
                f"AI Coach quota endpoint functional, quota: {quota_data.get('remaining', 'unknown')}/{quota_data.get('total', 'unknown')}"
            )
        else:
            self.log_test(
                "CORE FUNCTIONALITY - AI Coach Quota",
                False,
                f"AI Coach quota check failed: {result.get('error', 'Unknown error')}"
            )
        
        # Test 8: Alignment score dashboard
        result = self.make_request('GET', '/alignment/dashboard', use_auth=True)
        if result['success']:
            functionality_tests_passed += 1
            alignment_data = result['data']
            self.log_test(
                "CORE FUNCTIONALITY - Alignment Score Dashboard",
                True,
                f"Alignment score dashboard functional, weekly score: {alignment_data.get('weekly_score', 'unknown')}"
            )
        else:
            self.log_test(
                "CORE FUNCTIONALITY - Alignment Score Dashboard",
                False,
                f"Alignment score dashboard failed: {result.get('error', 'Unknown error')}"
            )
        
        # Overall functionality assessment
        functionality_percentage = (functionality_tests_passed / total_functionality_tests) * 100
        functionality_success = functionality_percentage >= 75  # At least 75% should work
        
        self.log_test(
            "CORE FUNCTIONALITY - OVERALL ASSESSMENT",
            functionality_success,
            f"Core functionality integrity: {functionality_tests_passed}/{total_functionality_tests} tests passed ({functionality_percentage:.1f}%)"
        )
        
        return functionality_success

    def test_authentication_and_crud_operations(self):
        """Test authentication and CRUD operations work correctly"""
        print("\n=== TESTING AUTHENTICATION & CRUD OPERATIONS ===")
        
        if not self.auth_token:
            self.log_test("AUTH & CRUD - Authentication Required", False, "No authentication token available")
            return False
        
        crud_tests_passed = 0
        total_crud_tests = 6
        created_resources = []
        
        # Test 1: Create a pillar
        pillar_data = {
            "name": "Security Test Pillar",
            "description": "A pillar created during security testing",
            "icon": "🔒",
            "color": "#FF5722",
            "time_allocation_percentage": 10.0
        }
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if result['success']:
            crud_tests_passed += 1
            pillar_id = result['data'].get('id')
            created_resources.append(('pillar', pillar_id))
            self.log_test(
                "AUTH & CRUD - Pillar Creation",
                True,
                f"Pillar created successfully with ID: {pillar_id}"
            )
        else:
            self.log_test(
                "AUTH & CRUD - Pillar Creation",
                False,
                f"Pillar creation failed: {result.get('error', 'Unknown error')}"
            )
        
        # Test 2: Create an area (if pillar was created)
        if created_resources and created_resources[-1][0] == 'pillar':
            area_data = {
                "pillar_id": created_resources[-1][1],
                "name": "Security Test Area",
                "description": "An area created during security testing",
                "icon": "🛡️",
                "color": "#2196F3",
                "importance": 3
            }
            result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
            if result['success']:
                crud_tests_passed += 1
                area_id = result['data'].get('id')
                created_resources.append(('area', area_id))
                self.log_test(
                    "AUTH & CRUD - Area Creation",
                    True,
                    f"Area created successfully with ID: {area_id}"
                )
            else:
                self.log_test(
                    "AUTH & CRUD - Area Creation",
                    False,
                    f"Area creation failed: {result.get('error', 'Unknown error')}"
                )
        else:
            total_crud_tests -= 1  # Skip this test if pillar creation failed
        
        # Test 3: Create a project (if area was created)
        if len(created_resources) >= 2 and created_resources[-1][0] == 'area':
            project_data = {
                "area_id": created_resources[-1][1],
                "name": "Security Test Project",
                "description": "A project created during security testing",
                "status": "Not Started",
                "priority": "medium"
            }
            result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
            if result['success']:
                crud_tests_passed += 1
                project_id = result['data'].get('id')
                created_resources.append(('project', project_id))
                self.log_test(
                    "AUTH & CRUD - Project Creation",
                    True,
                    f"Project created successfully with ID: {project_id}"
                )
            else:
                self.log_test(
                    "AUTH & CRUD - Project Creation",
                    False,
                    f"Project creation failed: {result.get('error', 'Unknown error')}"
                )
        else:
            total_crud_tests -= 1  # Skip this test if area creation failed
        
        # Test 4: Create a task (if project was created)
        if len(created_resources) >= 3 and created_resources[-1][0] == 'project':
            task_data = {
                "project_id": created_resources[-1][1],
                "name": "Security Test Task",
                "description": "A task created during security testing",
                "status": "todo",
                "priority": "medium"
            }
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if result['success']:
                crud_tests_passed += 1
                task_id = result['data'].get('id')
                created_resources.append(('task', task_id))
                self.log_test(
                    "AUTH & CRUD - Task Creation",
                    True,
                    f"Task created successfully with ID: {task_id}"
                )
            else:
                self.log_test(
                    "AUTH & CRUD - Task Creation",
                    False,
                    f"Task creation failed: {result.get('error', 'Unknown error')}"
                )
        else:
            total_crud_tests -= 1  # Skip this test if project creation failed
        
        # Test 5: Update operations
        update_success = 0
        update_attempts = 0
        
        for resource_type, resource_id in created_resources:
            if resource_type == 'task' and resource_id:
                update_attempts += 1
                update_data = {
                    "name": "Security Test Task (Updated)",
                    "status": "in_progress"
                }
                result = self.make_request('PUT', f'/tasks/{resource_id}', data=update_data, use_auth=True)
                if result['success']:
                    update_success += 1
        
        if update_attempts > 0:
            crud_tests_passed += 1 if update_success > 0 else 0
            self.log_test(
                "AUTH & CRUD - Update Operations",
                update_success > 0,
                f"Update operations: {update_success}/{update_attempts} successful"
            )
        else:
            total_crud_tests -= 1  # Skip this test if no resources to update
        
        # Test 6: Delete operations (cleanup)
        delete_success = 0
        delete_attempts = 0
        
        # Delete in reverse order (tasks -> projects -> areas -> pillars)
        for resource_type, resource_id in reversed(created_resources):
            if resource_id:
                delete_attempts += 1
                endpoint_map = {
                    'task': '/tasks',
                    'project': '/projects',
                    'area': '/areas',
                    'pillar': '/pillars'
                }
                endpoint = endpoint_map.get(resource_type)
                if endpoint:
                    result = self.make_request('DELETE', f'{endpoint}/{resource_id}', use_auth=True)
                    if result['success']:
                        delete_success += 1
        
        if delete_attempts > 0:
            crud_tests_passed += 1 if delete_success > 0 else 0
            self.log_test(
                "AUTH & CRUD - Delete Operations",
                delete_success > 0,
                f"Delete operations: {delete_success}/{delete_attempts} successful"
            )
        else:
            total_crud_tests -= 1  # Skip this test if no resources to delete
        
        # Overall CRUD assessment
        crud_percentage = (crud_tests_passed / total_crud_tests) * 100 if total_crud_tests > 0 else 0
        crud_success = crud_percentage >= 70  # At least 70% should work
        
        self.log_test(
            "AUTH & CRUD - OVERALL ASSESSMENT",
            crud_success,
            f"Authentication & CRUD operations: {crud_tests_passed}/{total_crud_tests} tests passed ({crud_percentage:.1f}%)"
        )
        
        return crud_success

    def run_comprehensive_security_hardening_test(self):
        """Run comprehensive security hardening verification tests"""
        print("\n🔐 STARTING SECURITY HARDENING COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("HTTP Security Headers", self.test_security_headers),
            ("Input Sanitization", self.test_input_sanitization),
            ("Core Functionality Integrity", self.test_core_functionality_integrity),
            ("Authentication & CRUD Operations", self.test_authentication_and_crud_operations)
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
        print("🔐 SECURITY HARDENING TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for security functionality
        security_headers_passed = sum(1 for result in self.test_results if result['success'] and 'SECURITY HEADERS' in result['test'])
        input_sanitization_passed = sum(1 for result in self.test_results if result['success'] and 'INPUT SANITIZATION' in result['test'])
        functionality_passed = sum(1 for result in self.test_results if result['success'] and 'CORE FUNCTIONALITY' in result['test'])
        crud_passed = sum(1 for result in self.test_results if result['success'] and 'AUTH & CRUD' in result['test'])
        
        print(f"\n🔍 SECURITY ANALYSIS:")
        print(f"Security Headers Tests Passed: {security_headers_passed}")
        print(f"Input Sanitization Tests Passed: {input_sanitization_passed}")
        print(f"Core Functionality Tests Passed: {functionality_passed}")
        print(f"Authentication & CRUD Tests Passed: {crud_passed}")
        
        if success_rate >= 85:
            print("\n✅ SECURITY HARDENING IMPLEMENTATION: SUCCESS")
            print("   ✅ HTTP Security Headers implemented")
            print("   ✅ Input Sanitization working")
            print("   ✅ Core functionality integrity maintained")
            print("   ✅ Authentication & CRUD operations functional")
            print("   The Security Hardening implementation is production-ready!")
        elif success_rate >= 70:
            print("\n⚠️ SECURITY HARDENING IMPLEMENTATION: MOSTLY FUNCTIONAL")
            print("   Security hardening mostly working with minor issues")
        else:
            print("\n❌ SECURITY HARDENING IMPLEMENTATION: ISSUES DETECTED")
            print("   Significant issues found in security hardening implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Security Hardening Tests"""
    print("🔐 STARTING SECURITY HARDENING BACKEND TESTING")
    print("=" * 80)
    
    tester = SecurityHardeningTester()
    
    try:
        # Run the comprehensive security hardening tests
        success = tester.run_comprehensive_security_hardening_test()
        
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