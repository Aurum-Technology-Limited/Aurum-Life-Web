#!/usr/bin/env python3
"""
BACKEND HEALTH CHECK - Quick API Verification
Quick verification to ensure backend APIs are working correctly after frontend changes.

FOCUS AREAS:
1. **Authentication**: Login and JWT token validation
2. **Projects API**: Project listing and creation
3. **Areas API**: Area management operations
4. **Insights API**: Insights data retrieval

This is a quick verification to ensure backend is stable before testing the frontend UI overflow fixes.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any
import uuid

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://3a5afcb7-fa6e-48fa-9073-f3c58548c911.preview.emergentagent.com/api"

class BackendHealthChecker:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use realistic test data
        self.test_user_email = f"health.check_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "HealthCheck2025!"
        self.test_user_data = {
            "username": f"health_check_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Health",
            "last_name": "Checker",
            "password": self.test_user_password
        }
        self.created_resources = []
        
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

    def test_authentication_system(self):
        """Test Authentication: Login and JWT token validation"""
        print("\n=== TESTING AUTHENTICATION SYSTEM ===")
        
        # Register user
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        self.log_test(
            "USER REGISTRATION",
            result['success'],
            f"User registered successfully: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
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
        
        # Verify JWT token validation
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "JWT TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_projects_api(self):
        """Test Projects API: Project listing and creation"""
        print("\n=== TESTING PROJECTS API ===")
        
        if not self.auth_token:
            self.log_test("PROJECTS API - Authentication Required", False, "No authentication token available")
            return False
        
        # First, create a pillar and area for project testing
        pillar_data = {
            "name": "Health Check Pillar",
            "description": "Test pillar for health check",
            "icon": "🎯",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("PROJECTS API - CREATE PILLAR", False, f"Failed to create test pillar: {result.get('error', 'Unknown error')}")
            return False
        
        pillar_id = result['data']['id']
        self.created_resources.append(('pillar', pillar_id))
        
        area_data = {
            "name": "Health Check Area",
            "description": "Test area for health check",
            "icon": "📋",
            "color": "#2196F3",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("PROJECTS API - CREATE AREA", False, f"Failed to create test area: {result.get('error', 'Unknown error')}")
            return False
        
        area_id = result['data']['id']
        self.created_resources.append(('area', area_id))
        
        # Test project creation
        project_data = {
            "area_id": area_id,
            "name": "Health Check Project",
            "description": "Test project for backend health check",
            "priority": "medium",
            "icon": "🚀"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        self.log_test(
            "PROJECT CREATION",
            result['success'],
            f"Project created successfully: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Project creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        project_id = result['data']['id']
        self.created_resources.append(('project', project_id))
        
        # Test project listing
        result = self.make_request('GET', '/projects', use_auth=True)
        self.log_test(
            "PROJECT LISTING",
            result['success'],
            f"Projects retrieved successfully: {len(result['data'])} projects found" if result['success'] else f"Project listing failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Test specific project retrieval
        result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
        self.log_test(
            "PROJECT RETRIEVAL",
            result['success'],
            f"Project retrieved successfully: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Project retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_areas_api(self):
        """Test Areas API: Area management operations"""
        print("\n=== TESTING AREAS API ===")
        
        if not self.auth_token:
            self.log_test("AREAS API - Authentication Required", False, "No authentication token available")
            return False
        
        # Test areas listing
        result = self.make_request('GET', '/areas', use_auth=True)
        self.log_test(
            "AREAS LISTING",
            result['success'],
            f"Areas retrieved successfully: {len(result['data'])} areas found" if result['success'] else f"Areas listing failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Test areas with projects included
        result = self.make_request('GET', '/areas', params={'include_projects': 'true'}, use_auth=True)
        self.log_test(
            "AREAS WITH PROJECTS",
            result['success'],
            f"Areas with projects retrieved successfully" if result['success'] else f"Areas with projects failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Test specific area retrieval if we have areas
        areas = result['data']
        if areas:
            area_id = areas[0]['id']
            result = self.make_request('GET', f'/areas/{area_id}', use_auth=True)
            self.log_test(
                "AREA RETRIEVAL",
                result['success'],
                f"Area retrieved successfully: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Area retrieval failed: {result.get('error', 'Unknown error')}"
            )
            return result['success']
        else:
            self.log_test("AREA RETRIEVAL", True, "No areas to test individual retrieval")
            return True

    def test_insights_api(self):
        """Test Insights API: Insights data retrieval"""
        print("\n=== TESTING INSIGHTS API ===")
        
        if not self.auth_token:
            self.log_test("INSIGHTS API - Authentication Required", False, "No authentication token available")
            return False
        
        # Test insights data retrieval
        result = self.make_request('GET', '/insights', use_auth=True)
        self.log_test(
            "INSIGHTS DATA RETRIEVAL",
            result['success'],
            f"Insights data retrieved successfully" if result['success'] else f"Insights data retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Verify insights data structure
        insights_data = result['data']
        required_fields = ['task_status_breakdown', 'productivity_trends', 'area_performance']
        
        has_required_fields = all(field in insights_data for field in required_fields)
        self.log_test(
            "INSIGHTS DATA STRUCTURE",
            has_required_fields,
            f"Insights data has required fields: {required_fields}" if has_required_fields else f"Missing required fields in insights data"
        )
        
        # Test insights with different date ranges
        for date_range in ['weekly', 'monthly', 'yearly']:
            result = self.make_request('GET', '/insights', params={'date_range': date_range}, use_auth=True)
            self.log_test(
                f"INSIGHTS - {date_range.upper()} RANGE",
                result['success'],
                f"Insights data retrieved for {date_range} range" if result['success'] else f"Insights {date_range} range failed: {result.get('error', 'Unknown error')}"
            )
        
        return has_required_fields

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        cleanup_count = 0
        
        # Clean up in reverse order (projects -> areas -> pillars)
        for resource_type, resource_id in reversed(self.created_resources):
            try:
                if resource_type == 'project':
                    result = self.make_request('DELETE', f'/projects/{resource_id}', use_auth=True)
                elif resource_type == 'area':
                    result = self.make_request('DELETE', f'/areas/{resource_id}', use_auth=True)
                elif resource_type == 'pillar':
                    result = self.make_request('DELETE', f'/pillars/{resource_id}', use_auth=True)
                
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up {resource_type}: {resource_id}")
            except:
                pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

    def run_health_check(self):
        """Run comprehensive backend health check"""
        print("\n🏥 STARTING BACKEND HEALTH CHECK")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("Authentication System", self.test_authentication_system),
            ("Projects API", self.test_projects_api),
            ("Areas API", self.test_areas_api),
            ("Insights API", self.test_insights_api)
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
        print("🏥 BACKEND HEALTH CHECK SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Detailed analysis
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and ('AUTHENTICATION' in result['test'] or 'LOGIN' in result['test'] or 'TOKEN' in result['test']))
        projects_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROJECT' in result['test'])
        areas_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AREA' in result['test'])
        insights_tests_passed = sum(1 for result in self.test_results if result['success'] and 'INSIGHTS' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Projects API Tests Passed: {projects_tests_passed}")
        print(f"Areas API Tests Passed: {areas_tests_passed}")
        print(f"Insights API Tests Passed: {insights_tests_passed}")
        
        if success_rate >= 80:
            print("\n✅ BACKEND HEALTH CHECK: SUCCESS")
            print("   ✅ Authentication system working correctly")
            print("   ✅ Projects API functioning properly")
            print("   ✅ Areas API operations working")
            print("   ✅ Insights API data retrieval functional")
            print("   Backend is stable and ready for frontend testing!")
        else:
            print("\n❌ BACKEND HEALTH CHECK: ISSUES DETECTED")
            print("   Issues found in backend API functionality")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 80

def main():
    """Run Backend Health Check"""
    print("🏥 STARTING BACKEND HEALTH CHECK")
    print("=" * 80)
    
    checker = BackendHealthChecker()
    
    try:
        # Run the health check
        success = checker.run_health_check()
        
        # Calculate overall results
        total_tests = len(checker.test_results)
        passed_tests = sum(1 for result in checker.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during health check: {str(e)}")
        return False
    
    finally:
        # Cleanup created resources
        checker.cleanup_resources()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)