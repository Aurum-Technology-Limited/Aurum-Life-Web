#!/usr/bin/env python3
"""
Semantic Search Functionality Testing
Testing Focus: OpenAI embeddings + pgvector RAG search

This test verifies:
1. User authentication with test user (testuser)
2. Basic semantic search endpoint functionality
3. Error scenarios and edge cases
4. SQL error checking (ambiguous column references)
5. OpenAI integration and pgvector search
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class SemanticSearchTester:
    def __init__(self, base_url="https://supa-data-explained.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test credentials - using known working credentials from test_result.md
        self.test_email = "test@aurumlife.com"
        self.test_password = "password123"
        self.test_user_id = "f9ed7066-5954-46e2-8de3-92d38a28832f"

    def log_test(self, name: str, success: bool, details: Dict = None, response_time: float = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            
        result = {
            'test_name': name,
            'success': success,
            'details': details or {},
            'response_time': response_time,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}s)" if response_time else ""
        print(f"{status} {name}{time_info}")
        
        if details and not success:
            print(f"   Details: {details}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, response_time)"""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        start_time = time.time()
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            if response.status_code < 400:
                return True, response.json(), response_time
            else:
                return False, {
                    'status_code': response.status_code,
                    'error': response.text,
                    'headers': dict(response.headers)
                }, response_time
                
        except Exception as e:
            response_time = time.time() - start_time
            return False, {'error': str(e)}, response_time

    def test_authentication(self) -> bool:
        """Test login with test user credentials"""
        print("\n🔐 Testing Authentication with test user...")
        
        success, response, response_time = self.make_request(
            'POST', 
            'auth/login',
            data={
                'email': self.test_email,
                'password': self.test_password
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response.get('user', {}).get('id')
            
            # Verify this is the expected test user
            expected_user_match = self.user_id == self.test_user_id
            
            details = {
                'user_id': self.user_id,
                'expected_user_id': self.test_user_id,
                'user_match': expected_user_match,
                'username': response.get('user', {}).get('username', 'N/A')
            }
            
            self.log_test("Authentication", True, details, response_time)
            return True
        else:
            self.log_test("Authentication", False, response, response_time)
            return False

    def test_basic_semantic_search(self) -> bool:
        """Test basic semantic search endpoint with query parameter"""
        print("\n🔍 Testing Basic Semantic Search...")
        
        success, response, response_time = self.make_request(
            'GET',
            'semantic/search',
            params={'query': 'test'}
        )
        
        if success:
            # Verify response structure
            required_fields = ['query', 'results', 'total_results', 'search_metadata']
            has_all_fields = all(field in response for field in required_fields)
            
            # Check search metadata
            metadata = response.get('search_metadata', {})
            has_embedding_model = 'embedding_model' in metadata
            
            # Check if results have proper structure
            results = response.get('results', [])
            valid_results = True
            if results:
                result_fields = ['id', 'entity_type', 'title', 'content_preview', 'similarity_score']
                valid_results = all(
                    all(field in result for field in result_fields) 
                    for result in results
                )
            
            details = {
                'query': response.get('query'),
                'total_results': response.get('total_results'),
                'results_count': len(results),
                'has_all_fields': has_all_fields,
                'has_embedding_model': has_embedding_model,
                'embedding_model': metadata.get('embedding_model'),
                'valid_results_structure': valid_results,
                'sample_result': results[0] if results else None
            }
            
            test_passed = has_all_fields and has_embedding_model and valid_results
            self.log_test("Basic Semantic Search", test_passed, details, response_time)
            return test_passed
        else:
            self.log_test("Basic Semantic Search", False, response, response_time)
            return False

    def test_semantic_search_with_parameters(self) -> bool:
        """Test semantic search with various parameters"""
        print("\n⚙️ Testing Semantic Search with Parameters...")
        
        test_cases = [
            {
                'name': 'With limit parameter',
                'params': {'query': 'productivity', 'limit': 5}
            },
            {
                'name': 'With min_similarity parameter',
                'params': {'query': 'goals', 'min_similarity': 0.5}
            },
            {
                'name': 'With content_types parameter',
                'params': {'query': 'journal', 'content_types': ['journal_entry']}
            },
            {
                'name': 'With date_range_days parameter',
                'params': {'query': 'tasks', 'date_range_days': 30}
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            success, response, response_time = self.make_request(
                'GET',
                'semantic/search',
                params=test_case['params']
            )
            
            if success:
                # Verify response structure is maintained
                has_required_fields = all(
                    field in response 
                    for field in ['query', 'results', 'total_results', 'search_metadata']
                )
                
                # Check if parameters were applied
                metadata = response.get('search_metadata', {})
                
                details = {
                    'params': test_case['params'],
                    'total_results': response.get('total_results'),
                    'has_required_fields': has_required_fields,
                    'metadata': metadata
                }
                
                test_passed = has_required_fields
                self.log_test(f"Semantic Search - {test_case['name']}", test_passed, details, response_time)
                
                if not test_passed:
                    all_passed = False
            else:
                self.log_test(f"Semantic Search - {test_case['name']}", False, response, response_time)
                all_passed = False
        
        return all_passed

    def test_error_scenarios(self) -> bool:
        """Test error scenarios for semantic search"""
        print("\n🚨 Testing Error Scenarios...")
        
        error_test_cases = [
            {
                'name': 'No query parameter',
                'params': {},
                'expected_status': 422
            },
            {
                'name': 'Empty query',
                'params': {'query': ''},
                'expected_status': 422
            },
            {
                'name': 'Invalid limit (too high)',
                'params': {'query': 'test', 'limit': 100},
                'expected_status': 422
            },
            {
                'name': 'Invalid min_similarity (out of range)',
                'params': {'query': 'test', 'min_similarity': 1.5},
                'expected_status': 422
            }
        ]
        
        all_passed = True
        
        for test_case in error_test_cases:
            success, response, response_time = self.make_request(
                'GET',
                'semantic/search',
                params=test_case['params']
            )
            
            # For error scenarios, we expect success=False
            expected_failure = not success
            actual_status = response.get('status_code', 200) if not success else 200
            status_match = actual_status == test_case['expected_status']
            
            details = {
                'params': test_case['params'],
                'expected_status': test_case['expected_status'],
                'actual_status': actual_status,
                'expected_failure': expected_failure,
                'status_match': status_match,
                'error_response': response if not success else None
            }
            
            test_passed = expected_failure and status_match
            self.log_test(f"Error Scenario - {test_case['name']}", test_passed, details, response_time)
            
            if not test_passed:
                all_passed = False
        
        return all_passed

    def test_sql_error_checking(self) -> bool:
        """Test for SQL errors, particularly ambiguous column references"""
        print("\n🔍 Testing for SQL Errors...")
        
        # Test various queries that might trigger SQL issues
        test_queries = [
            'title',  # This might trigger ambiguous column reference
            'content',
            'name',
            'description',
            'project task journal'  # Complex query
        ]
        
        all_passed = True
        sql_errors_found = []
        
        for query in test_queries:
            success, response, response_time = self.make_request(
                'GET',
                'semantic/search',
                params={'query': query, 'limit': 10}
            )
            
            # Check for SQL-related errors in response
            sql_error_indicators = [
                'ambiguous',
                'column reference',
                'SQL',
                'database error',
                'relation does not exist'
            ]
            
            has_sql_error = False
            if not success:
                error_text = str(response.get('error', '')).lower()
                has_sql_error = any(indicator in error_text for indicator in sql_error_indicators)
                if has_sql_error:
                    sql_errors_found.append({
                        'query': query,
                        'error': response.get('error'),
                        'status_code': response.get('status_code')
                    })
            
            details = {
                'query': query,
                'success': success,
                'has_sql_error': has_sql_error,
                'response_time': response_time,
                'total_results': response.get('total_results', 0) if success else 0
            }
            
            # Test passes if no SQL errors are found
            test_passed = not has_sql_error
            self.log_test(f"SQL Error Check - Query: '{query}'", test_passed, details, response_time)
            
            if not test_passed:
                all_passed = False
        
        # Summary of SQL error checking
        summary_details = {
            'total_queries_tested': len(test_queries),
            'sql_errors_found': len(sql_errors_found),
            'sql_errors': sql_errors_found
        }
        
        overall_passed = len(sql_errors_found) == 0
        self.log_test("Overall SQL Error Check", overall_passed, summary_details)
        
        return overall_passed

    def test_openai_integration(self) -> bool:
        """Test OpenAI integration and configuration"""
        print("\n🤖 Testing OpenAI Integration...")
        
        # Test with a meaningful query that should generate embeddings
        success, response, response_time = self.make_request(
            'GET',
            'semantic/search',
            params={
                'query': 'artificial intelligence machine learning productivity optimization',
                'limit': 5
            }
        )
        
        if success:
            # Check if OpenAI embedding model is being used
            metadata = response.get('search_metadata', {})
            embedding_model = metadata.get('embedding_model')
            
            # Check if we got meaningful results (indicates embeddings worked)
            results = response.get('results', [])
            has_similarity_scores = all(
                'similarity_score' in result and isinstance(result['similarity_score'], (int, float))
                for result in results
            )
            
            details = {
                'embedding_model': embedding_model,
                'results_count': len(results),
                'has_similarity_scores': has_similarity_scores,
                'similarity_scores': [r.get('similarity_score') for r in results[:3]],
                'response_time': response_time
            }
            
            # Test passes if we have the expected embedding model and valid similarity scores
            test_passed = (
                embedding_model == 'text-embedding-3-small' and
                has_similarity_scores
            )
            
            self.log_test("OpenAI Integration", test_passed, details, response_time)
            return test_passed
        else:
            # Check if error is related to OpenAI API key
            error_text = str(response.get('error', '')).lower()
            openai_error = 'openai' in error_text or 'api key' in error_text
            
            details = {
                'error': response.get('error'),
                'status_code': response.get('status_code'),
                'openai_related_error': openai_error
            }
            
            self.log_test("OpenAI Integration", False, details, response_time)
            return False

    def test_rag_search_function(self) -> bool:
        """Test RAG search function specifically"""
        print("\n📚 Testing RAG Search Function...")
        
        # Test with content_types set to "all" to trigger rag_search function
        success, response, response_time = self.make_request(
            'GET',
            'semantic/search',
            params={
                'query': 'productivity goals tasks journal',
                'content_types': ['all'],
                'limit': 10,
                'min_similarity': 0.3
            }
        )
        
        if success:
            # Verify RAG search worked by checking response structure
            results = response.get('results', [])
            metadata = response.get('search_metadata', {})
            
            # Check if we got diverse content types (indicates RAG search worked)
            entity_types = set(result.get('entity_type') for result in results)
            
            # Check if results have proper RAG structure
            valid_rag_results = all(
                all(field in result for field in ['entity_type', 'similarity_score', 'confidence_level'])
                for result in results
            )
            
            details = {
                'results_count': len(results),
                'entity_types_found': list(entity_types),
                'valid_rag_structure': valid_rag_results,
                'content_types_searched': metadata.get('content_types_searched', []),
                'sample_confidences': [r.get('confidence_level') for r in results[:3]]
            }
            
            test_passed = valid_rag_results and len(entity_types) >= 0  # Allow empty results
            self.log_test("RAG Search Function", test_passed, details, response_time)
            return test_passed
        else:
            self.log_test("RAG Search Function", False, response, response_time)
            return False

    def test_authentication_required(self) -> bool:
        """Test that semantic search requires authentication"""
        print("\n🔒 Testing Authentication Requirement...")
        
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        success, response, response_time = self.make_request(
            'GET',
            'semantic/search',
            params={'query': 'test'}
        )
        
        # Restore token
        self.token = original_token
        
        # Should fail without authentication
        expected_failure = not success
        status_code = response.get('status_code', 200) if not success else 200
        is_auth_error = status_code in [401, 403]
        
        details = {
            'expected_failure': expected_failure,
            'status_code': status_code,
            'is_auth_error': is_auth_error,
            'error': response.get('error') if not success else None
        }
        
        test_passed = expected_failure and is_auth_error
        self.log_test("Authentication Required", test_passed, details, response_time)
        return test_passed

    def run_comprehensive_test(self):
        """Run all semantic search tests"""
        print("🚀 Starting Semantic Search Functionality Testing")
        print("=" * 60)
        
        # Authentication is required for all other tests
        if not self.test_authentication():
            print("\n❌ Authentication failed. Cannot proceed with other tests.")
            return False
            
        # Run all semantic search tests
        test_methods = [
            self.test_basic_semantic_search,
            self.test_semantic_search_with_parameters,
            self.test_error_scenarios,
            self.test_sql_error_checking,
            self.test_openai_integration,
            self.test_rag_search_function,
            self.test_authentication_required
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {e}")
                self.log_test(test_method.__name__, False, {'exception': str(e)})
        
        # Print summary
        self.print_summary()
        
        return self.tests_passed == self.tests_run

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 SEMANTIC SEARCH TEST SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Print failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test_name']}")
                if test['details']:
                    error_info = test['details'].get('error', test['details'].get('exception', ''))
                    if error_info:
                        print(f"    Error: {error_info}")
        
        # Print performance insights
        search_tests = [r for r in self.test_results if 'Semantic Search' in r['test_name']]
        if search_tests:
            avg_search_time = sum(r['response_time'] for r in search_tests if r['response_time']) / len(search_tests)
            print(f"\n⚡ SEMANTIC SEARCH PERFORMANCE:")
            print(f"  Average Search Response Time: {avg_search_time:.2f}s")
            print(f"  Search Tests Passed: {len([t for t in search_tests if t['success']])}/{len(search_tests)}")
        
        # Print key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        # Check for SQL errors
        sql_errors = [r for r in self.test_results if 'SQL Error' in r['test_name'] and not r['success']]
        if sql_errors:
            print(f"  ⚠️ SQL errors detected in {len(sql_errors)} queries")
        else:
            print(f"  ✅ No SQL errors detected")
        
        # Check OpenAI integration
        openai_test = next((r for r in self.test_results if 'OpenAI Integration' in r['test_name']), None)
        if openai_test:
            if openai_test['success']:
                print(f"  ✅ OpenAI integration working correctly")
            else:
                print(f"  ❌ OpenAI integration issues detected")
        
        # Check authentication
        auth_test = next((r for r in self.test_results if r['test_name'] == 'Authentication'), None)
        if auth_test and auth_test['success']:
            user_match = auth_test['details'].get('user_match', False)
            if user_match:
                print(f"  ✅ Test user authentication successful (correct user ID)")
            else:
                print(f"  ⚠️ Authentication successful but user ID mismatch")

def main():
    """Main test execution"""
    tester = SemanticSearchTester()
    
    try:
        success = tester.run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())