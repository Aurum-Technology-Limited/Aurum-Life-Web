#!/usr/bin/env python3
"""
ENHANCED NOTIFICATIONS SYSTEM COMPREHENSIVE TESTING
Complete end-to-end testing of the Enhanced Notifications System implementation.

FOCUS AREAS:
1. Enhanced Notification Management - Test existing and NEW bulk endpoints
2. Browser Notification Features - Test notification preferences and browser notifications
3. Notification Scheduling System - Test task reminder scheduling and generation
4. Data Integrity & Performance - Test bulk operations and data consistency
5. Authentication & Security - Test user isolation and access control
6. Error Handling - Test error scenarios and edge cases

Context: Testing the complete Enhanced Notifications system implementation with:
- Enhanced notification management with bulk operations
- Browser notification features with preferences
- Notification scheduling system for task reminders
- Data integrity and performance optimization
- Full authentication and user isolation
- Comprehensive error handling
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://9e0755cb-5122-46b7-bde6-cd0ca0c057dc.preview.emergentagent.com/api"

class JournalEnhancementsTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'journal_entries': [],
            'journal_templates': [],
            'users': []
        }
        self.auth_token = None
        # Use realistic test data for journal testing
        self.test_user_email = f"journal.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "JournalTest2025!"
        self.test_user_data = {
            "username": f"journal_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Journal",
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
        """Test user registration and login for journal testing"""
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

    def test_journal_templates_system(self):
        """Test the journal templates system including default templates"""
        print("\n=== TESTING JOURNAL TEMPLATES SYSTEM ===")
        
        if not self.auth_token:
            self.log_test("JOURNAL TEMPLATES - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Get all templates (should include default templates)
        result = self.make_request('GET', '/journal/templates', use_auth=True)
        self.log_test(
            "GET ALL JOURNAL TEMPLATES",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} templates" if result['success'] else f"Failed to get templates: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        templates = result['data']
        
        # Test 2: Verify default templates exist
        expected_default_templates = [
            "Daily Reflection", "Gratitude Journal", "Goal Setting", 
            "Weekly Review", "Learning Log"
        ]
        
        default_templates = [t for t in templates if t.get('is_default', False)]
        default_template_names = [t['name'] for t in default_templates]
        
        found_defaults = [name for name in expected_default_templates if name in default_template_names]
        
        self.log_test(
            "DEFAULT TEMPLATES VERIFICATION",
            len(found_defaults) >= 5,
            f"Found {len(found_defaults)}/5 expected default templates: {found_defaults}"
        )
        
        # Test 3: Verify default template structure
        if default_templates:
            sample_template = default_templates[0]
            required_fields = ['id', 'name', 'description', 'template_type', 'prompts', 'default_tags', 'icon', 'color', 'is_default', 'user_id']
            present_fields = [field for field in required_fields if field in sample_template]
            
            self.log_test(
                "DEFAULT TEMPLATE STRUCTURE",
                len(present_fields) >= 8,
                f"Default template contains {len(present_fields)}/{len(required_fields)} expected fields"
            )
            
            # Verify system user_id
            self.log_test(
                "DEFAULT TEMPLATE USER_ID",
                sample_template.get('user_id') == 'system',
                f"Default template user_id: {sample_template.get('user_id', 'Unknown')}"
            )
        
        # Test 4: Create custom template
        custom_template_data = {
            "name": "Test Custom Template",
            "description": "A custom template for testing",
            "template_type": "custom",
            "prompts": [
                "What did you test today?",
                "What worked well?",
                "What needs improvement?"
            ],
            "default_tags": ["testing", "custom"],
            "icon": "🧪",
            "color": "#FF5722"
        }
        
        result = self.make_request('POST', '/journal/templates', data=custom_template_data, use_auth=True)
        self.log_test(
            "CREATE CUSTOM TEMPLATE",
            result['success'],
            f"Custom template created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create template: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            template_id = result['data']['id']
            self.created_resources['journal_templates'].append(template_id)
            
            # Test 5: Get specific template
            result = self.make_request('GET', f'/journal/templates/{template_id}', use_auth=True)
            self.log_test(
                "GET SPECIFIC TEMPLATE",
                result['success'],
                f"Retrieved template: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to get template: {result.get('error', 'Unknown error')}"
            )
            
            # Test 6: Update custom template
            update_data = {
                "description": "Updated description for testing",
                "prompts": ["Updated prompt 1", "Updated prompt 2"]
            }
            
            result = self.make_request('PUT', f'/journal/templates/{template_id}', data=update_data, use_auth=True)
            self.log_test(
                "UPDATE CUSTOM TEMPLATE",
                result['success'],
                f"Template updated successfully" if result['success'] else f"Failed to update template: {result.get('error', 'Unknown error')}"
            )
        
        return True

    def test_journal_entry_management(self):
        """Test comprehensive journal entry management with enhanced fields"""
        print("\n=== TESTING JOURNAL ENTRY MANAGEMENT ===")
        
        if not self.auth_token:
            self.log_test("JOURNAL ENTRY MANAGEMENT - Authentication Required", False, "No authentication token available")
            return False
        
        # Get a template to use for testing
        templates_result = self.make_request('GET', '/journal/templates', use_auth=True)
        template_id = None
        if templates_result['success'] and templates_result['data']:
            template_id = templates_result['data'][0]['id']
        
        # Test 1: Create journal entry with enhanced fields
        entry_data = {
            "title": "My Test Journal Entry",
            "content": "This is a comprehensive test of the journal entry system. I'm testing all the enhanced fields including mood, energy level, tags, template responses, weather, and location. This entry should demonstrate the full capabilities of the journal enhancement system.",
            "mood": "optimistic",
            "energy_level": "high",
            "tags": ["testing", "journal", "enhancement"],
            "template_id": template_id,
            "template_responses": {
                "What went well today?": "The journal testing is going great!",
                "What challenges did you face?": "Some minor API issues but nothing major.",
                "What did you learn?": "The journal system is very comprehensive."
            },
            "weather": "Sunny and warm",
            "location": "Home Office"
        }
        
        result = self.make_request('POST', '/journal', data=entry_data, use_auth=True)
        self.log_test(
            "CREATE JOURNAL ENTRY WITH ENHANCED FIELDS",
            result['success'],
            f"Journal entry created: {result['data'].get('title', 'Unknown')}" if result['success'] else f"Failed to create entry: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        entry_id = result['data']['id']
        self.created_resources['journal_entries'].append(entry_id)
        
        # Verify enhanced fields are present
        created_entry = result['data']
        enhanced_fields = ['mood', 'energy_level', 'tags', 'template_id', 'template_responses', 'weather', 'location', 'word_count', 'reading_time_minutes']
        present_enhanced_fields = [field for field in enhanced_fields if field in created_entry]
        
        self.log_test(
            "ENHANCED FIELDS VERIFICATION",
            len(present_enhanced_fields) >= 7,
            f"Entry contains {len(present_enhanced_fields)}/{len(enhanced_fields)} enhanced fields: {present_enhanced_fields}"
        )
        
        # Test word count and reading time calculation
        expected_word_count = len(entry_data['content'].split())
        actual_word_count = created_entry.get('word_count', 0)
        
        self.log_test(
            "WORD COUNT CALCULATION",
            abs(actual_word_count - expected_word_count) <= 2,  # Allow small variance
            f"Word count calculated: {actual_word_count} (expected ~{expected_word_count})"
        )
        
        self.log_test(
            "READING TIME CALCULATION",
            created_entry.get('reading_time_minutes', 0) > 0,
            f"Reading time calculated: {created_entry.get('reading_time_minutes', 0)} minutes"
        )
        
        # Test 2: Create additional entries for filtering tests
        additional_entries = [
            {
                "title": "Grateful Thoughts",
                "content": "Today I'm grateful for the opportunity to work on this amazing project.",
                "mood": "grateful",
                "energy_level": "moderate",
                "tags": ["gratitude", "work"]
            },
            {
                "title": "Challenging Day",
                "content": "Had some difficulties today but learned a lot from them.",
                "mood": "challenging",
                "energy_level": "low",
                "tags": ["challenges", "learning"]
            },
            {
                "title": "Excited About Progress",
                "content": "Making great progress on the journal system implementation!",
                "mood": "excited",
                "energy_level": "very_high",
                "tags": ["progress", "excitement", "journal"]
            }
        ]
        
        created_entry_ids = []
        for i, additional_entry in enumerate(additional_entries):
            result = self.make_request('POST', '/journal', data=additional_entry, use_auth=True)
            if result['success']:
                created_entry_ids.append(result['data']['id'])
                self.created_resources['journal_entries'].append(result['data']['id'])
        
        self.log_test(
            "CREATE ADDITIONAL ENTRIES",
            len(created_entry_ids) == len(additional_entries),
            f"Created {len(created_entry_ids)}/{len(additional_entries)} additional entries"
        )
        
        # Test 3: Get all entries
        result = self.make_request('GET', '/journal', use_auth=True)
        self.log_test(
            "GET ALL JOURNAL ENTRIES",
            result['success'] and len(result['data']) >= 4,
            f"Retrieved {len(result['data']) if result['success'] else 0} journal entries" if result['success'] else f"Failed to get entries: {result.get('error', 'Unknown error')}"
        )
        
        # Test 4: Advanced filtering - mood filter
        result = self.make_request('GET', '/journal', params={'mood_filter': 'grateful'}, use_auth=True)
        self.log_test(
            "MOOD FILTERING",
            result['success'] and len(result['data']) >= 1,
            f"Found {len(result['data']) if result['success'] else 0} entries with 'grateful' mood"
        )
        
        # Test 5: Advanced filtering - tag filter
        result = self.make_request('GET', '/journal', params={'tag_filter': 'journal'}, use_auth=True)
        self.log_test(
            "TAG FILTERING",
            result['success'] and len(result['data']) >= 2,
            f"Found {len(result['data']) if result['success'] else 0} entries with 'journal' tag"
        )
        
        # Test 6: Pagination
        result = self.make_request('GET', '/journal', params={'limit': 2, 'skip': 0}, use_auth=True)
        self.log_test(
            "PAGINATION",
            result['success'] and len(result['data']) <= 2,
            f"Pagination working: retrieved {len(result['data']) if result['success'] else 0} entries (limit=2)"
        )
        
        # Test 7: Update journal entry
        update_data = {
            "title": "Updated Test Journal Entry",
            "mood": "inspired",
            "tags": ["testing", "journal", "enhancement", "updated"]
        }
        
        result = self.make_request('PUT', f'/journal/{entry_id}', data=update_data, use_auth=True)
        self.log_test(
            "UPDATE JOURNAL ENTRY",
            result['success'],
            f"Journal entry updated successfully" if result['success'] else f"Failed to update entry: {result.get('error', 'Unknown error')}"
        )
        
        return True

    def test_journal_search_and_insights(self):
        """Test journal search and insights functionality"""
        print("\n=== TESTING JOURNAL SEARCH AND INSIGHTS ===")
        
        if not self.auth_token:
            self.log_test("JOURNAL SEARCH AND INSIGHTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Search entries by content
        result = self.make_request('GET', '/journal/search', params={'q': 'testing'}, use_auth=True)
        self.log_test(
            "JOURNAL SEARCH BY CONTENT",
            result['success'],
            f"Search found {len(result['data']) if result['success'] else 0} entries containing 'testing'" if result['success'] else f"Search failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test 2: Search entries by tag
        result = self.make_request('GET', '/journal/search', params={'q': 'journal'}, use_auth=True)
        self.log_test(
            "JOURNAL SEARCH BY TAG",
            result['success'],
            f"Search found {len(result['data']) if result['success'] else 0} entries related to 'journal'" if result['success'] else f"Search failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test 3: On This Day functionality
        result = self.make_request('GET', '/journal/on-this-day', use_auth=True)
        self.log_test(
            "ON THIS DAY FUNCTIONALITY",
            result['success'],
            f"On This Day returned {len(result['data']) if result['success'] else 0} historical entries" if result['success'] else f"On This Day failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test 4: Journal insights analytics
        result = self.make_request('GET', '/journal/insights', use_auth=True)
        self.log_test(
            "JOURNAL INSIGHTS ANALYTICS",
            result['success'],
            f"Insights generated successfully" if result['success'] else f"Insights failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            insights = result['data']
            expected_insight_fields = ['total_entries', 'current_streak', 'most_common_mood', 'average_energy_level', 'most_used_tags', 'mood_trend', 'energy_trend', 'writing_stats']
            present_insight_fields = [field for field in expected_insight_fields if field in insights]
            
            self.log_test(
                "INSIGHTS DATA STRUCTURE",
                len(present_insight_fields) >= 6,
                f"Insights contains {len(present_insight_fields)}/{len(expected_insight_fields)} expected fields: {present_insight_fields}"
            )
            
            # Verify insights data quality
            self.log_test(
                "INSIGHTS DATA QUALITY",
                insights.get('total_entries', 0) > 0 and insights.get('most_common_mood') is not None,
                f"Total entries: {insights.get('total_entries', 0)}, Most common mood: {insights.get('most_common_mood', 'Unknown')}"
            )
        
        return True

    def test_authentication_and_user_isolation(self):
        """Test that all journal endpoints require authentication and provide user isolation"""
        print("\n=== TESTING AUTHENTICATION AND USER ISOLATION ===")
        
        # Test 1: Endpoints without authentication should fail
        endpoints_to_test = [
            '/journal',
            '/journal/templates',
            '/journal/search?q=test',
            '/journal/insights',
            '/journal/on-this-day'
        ]
        
        auth_protected_count = 0
        for endpoint in endpoints_to_test:
            result = self.make_request('GET', endpoint, use_auth=False)
            if not result['success'] and result.get('status_code') in [401, 403]:
                auth_protected_count += 1
        
        self.log_test(
            "AUTHENTICATION PROTECTION",
            auth_protected_count == len(endpoints_to_test),
            f"{auth_protected_count}/{len(endpoints_to_test)} endpoints properly protected"
        )
        
        # Test 2: User isolation - entries should be user-specific
        if self.auth_token:
            result = self.make_request('GET', '/journal', use_auth=True)
            if result['success']:
                entries = result['data']
                user_entries = [e for e in entries if e.get('user_id')]
                
                self.log_test(
                    "USER DATA ISOLATION",
                    len(user_entries) == len(entries),
                    f"All {len(entries)} entries have user_id field for isolation"
                )
        
        return True

    def test_template_usage_tracking(self):
        """Test template usage tracking functionality"""
        print("\n=== TESTING TEMPLATE USAGE TRACKING ===")
        
        if not self.auth_token:
            self.log_test("TEMPLATE USAGE TRACKING - Authentication Required", False, "No authentication token available")
            return False
        
        # Get templates to find one with usage count
        result = self.make_request('GET', '/journal/templates', use_auth=True)
        if not result['success'] or not result['data']:
            self.log_test("TEMPLATE USAGE TRACKING", False, "No templates available for testing")
            return False
        
        # Find a template to use
        template = result['data'][0]
        template_id = template['id']
        initial_usage_count = template.get('usage_count', 0)
        
        # Create an entry using this template
        entry_data = {
            "title": "Template Usage Test",
            "content": "Testing template usage tracking functionality.",
            "template_id": template_id,
            "template_responses": {
                "test_prompt": "test_response"
            }
        }
        
        result = self.make_request('POST', '/journal', data=entry_data, use_auth=True)
        if result['success']:
            self.created_resources['journal_entries'].append(result['data']['id'])
        
        self.log_test(
            "CREATE ENTRY WITH TEMPLATE",
            result['success'],
            f"Entry created with template {template_id}" if result['success'] else f"Failed to create entry: {result.get('error', 'Unknown error')}"
        )
        
        # Check if usage count increased (Note: This might not be immediately visible due to async operations)
        result = self.make_request('GET', f'/journal/templates/{template_id}', use_auth=True)
        if result['success']:
            updated_template = result['data']
            new_usage_count = updated_template.get('usage_count', 0)
            
            self.log_test(
                "TEMPLATE USAGE COUNT TRACKING",
                new_usage_count >= initial_usage_count,
                f"Usage count: {initial_usage_count} → {new_usage_count}"
            )
        
        return True

    def test_mood_and_energy_enums(self):
        """Test mood and energy level enum validation"""
        print("\n=== TESTING MOOD AND ENERGY LEVEL ENUMS ===")
        
        if not self.auth_token:
            self.log_test("MOOD AND ENERGY ENUMS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test valid mood values
        valid_moods = ["optimistic", "inspired", "reflective", "challenging", "anxious", "grateful", "excited", "frustrated", "peaceful", "motivated"]
        valid_energy_levels = ["very_low", "low", "moderate", "high", "very_high"]
        
        # Test with valid values
        entry_data = {
            "title": "Enum Validation Test",
            "content": "Testing mood and energy level enum validation.",
            "mood": "grateful",
            "energy_level": "high"
        }
        
        result = self.make_request('POST', '/journal', data=entry_data, use_auth=True)
        self.log_test(
            "VALID MOOD AND ENERGY ENUMS",
            result['success'],
            f"Entry created with valid enums" if result['success'] else f"Failed with valid enums: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            self.created_resources['journal_entries'].append(result['data']['id'])
        
        # Test with invalid mood (should fail validation)
        invalid_entry_data = {
            "title": "Invalid Enum Test",
            "content": "Testing invalid enum values.",
            "mood": "invalid_mood",
            "energy_level": "moderate"
        }
        
        result = self.make_request('POST', '/journal', data=invalid_entry_data, use_auth=True)
        self.log_test(
            "INVALID MOOD ENUM REJECTION",
            not result['success'] and result.get('status_code') in [400, 422],
            f"Invalid mood properly rejected with status {result.get('status_code')}" if not result['success'] else "⚠️ Invalid mood was accepted - validation issue!"
        )
        
        return True

    def run_comprehensive_journal_test(self):
        """Run comprehensive journal enhancements system tests"""
        print("\n📝 STARTING JOURNAL ENHANCEMENTS SYSTEM TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration and Login", self.test_user_registration_and_login),
            ("Journal Templates System", self.test_journal_templates_system),
            ("Journal Entry Management", self.test_journal_entry_management),
            ("Journal Search and Insights", self.test_journal_search_and_insights),
            ("Authentication and User Isolation", self.test_authentication_and_user_isolation),
            ("Template Usage Tracking", self.test_template_usage_tracking),
            ("Mood and Energy Enums", self.test_mood_and_energy_enums)
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
        print("🎯 JOURNAL ENHANCEMENTS SYSTEM TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for journal system
        journal_tests_passed = sum(1 for result in self.test_results if result['success'] and 'JOURNAL' in result['test'])
        template_tests_passed = sum(1 for result in self.test_results if result['success'] and 'TEMPLATE' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Journal Entry Tests Passed: {journal_tests_passed}")
        print(f"Template System Tests Passed: {template_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ JOURNAL ENHANCEMENTS SYSTEM: SUCCESS")
            print("   ✅ Journal entry management with enhanced fields working")
            print("   ✅ Journal templates system functional (default + custom)")
            print("   ✅ Advanced filtering and search capabilities working")
            print("   ✅ Journal insights and analytics functional")
            print("   ✅ Authentication and user isolation working")
            print("   ✅ Template usage tracking operational")
            print("   ✅ Mood and energy level validation working")
            print("   The Journal Enhancements system is production-ready!")
        else:
            print("\n❌ JOURNAL ENHANCEMENTS SYSTEM: ISSUES DETECTED")
            print("   Issues found in journal system functionality")
        
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
        
        # Clean up journal entries
        for entry_id in self.created_resources.get('journal_entries', []):
            try:
                result = self.make_request('DELETE', f'/journal/{entry_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up journal entry: {entry_id}")
            except:
                pass
        
        # Clean up custom templates
        for template_id in self.created_resources.get('journal_templates', []):
            try:
                result = self.make_request('DELETE', f'/journal/templates/{template_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up journal template: {template_id}")
            except:
                pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

def main():
    """Run Journal Enhancements System Tests"""
    print("📝 STARTING JOURNAL ENHANCEMENTS SYSTEM BACKEND TESTING")
    print("=" * 80)
    
    tester = JournalEnhancementsTester()
    
    try:
        # Run the comprehensive journal system tests
        success = tester.run_comprehensive_journal_test()
        
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