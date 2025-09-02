#!/usr/bin/env python3
"""
Enhanced AI System Testing with OpenAI GPT-5 nano
Testing Focus: HRM Reasoning Quality and AI Coach Enhancement

This test verifies:
1. HRM analysis endpoints with GPT-5 nano
2. AI Coach enhancement with better reasoning
3. API response quality and performance
4. Integration verification
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class EnhancedAITester:
    def __init__(self, base_url="https://smart-life-os.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test credentials
        self.test_email = "test@aurumlife.com"
        self.test_password = "password123"

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
                    'error': response.text
                }, response_time
                
        except Exception as e:
            response_time = time.time() - start_time
            return False, {'error': str(e)}, response_time

    def test_authentication(self) -> bool:
        """Test login and get authentication token"""
        print("\n🔐 Testing Authentication...")
        
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
            self.log_test("Authentication", True, {'user_id': self.user_id}, response_time)
            return True
        else:
            self.log_test("Authentication", False, response, response_time)
            return False

    def test_hrm_global_analysis(self) -> bool:
        """Test HRM global analysis with different depths"""
        print("\n🧠 Testing HRM Global Analysis...")
        
        analysis_depths = ['minimal', 'balanced', 'detailed']
        all_passed = True
        
        for depth in analysis_depths:
            success, response, response_time = self.make_request(
                'POST',
                'hrm/analyze',
                data={
                    'entity_type': 'global',
                    'entity_id': None,
                    'analysis_depth': depth,
                    'force_llm': True  # Force GPT-5 nano usage
                }
            )
            
            if success:
                # Verify response structure and quality
                required_fields = ['insight_id', 'confidence_score', 'reasoning_path', 'recommendations']
                has_all_fields = all(field in response for field in required_fields)
                
                # Check confidence score is reasonable (0-100)
                confidence_valid = 0 <= response.get('confidence_score', -1) <= 100
                
                # Check if GPT-5 nano was used
                used_llm = response.get('used_llm', False)
                
                test_passed = has_all_fields and confidence_valid and used_llm
                
                details = {
                    'depth': depth,
                    'confidence_score': response.get('confidence_score'),
                    'used_llm': used_llm,
                    'has_reasoning': bool(response.get('reasoning_path')),
                    'recommendations_count': len(response.get('recommendations', []))
                }
                
                self.log_test(f"HRM Global Analysis ({depth})", test_passed, details, response_time)
                
                if not test_passed:
                    all_passed = False
            else:
                self.log_test(f"HRM Global Analysis ({depth})", False, response, response_time)
                all_passed = False
                
        return all_passed

    def test_task_level_analysis(self) -> bool:
        """Test task-level HRM analysis for reasoning quality"""
        print("\n📋 Testing Task-Level Analysis...")
        
        # First, get user's tasks
        success, tasks_response, _ = self.make_request('GET', 'tasks', params={'limit': 5})
        
        if not success or not tasks_response:
            self.log_test("Get Tasks for Analysis", False, {'error': 'No tasks available'})
            return False
            
        tasks = tasks_response if isinstance(tasks_response, list) else tasks_response.get('tasks', [])
        
        if not tasks:
            self.log_test("Task-Level Analysis", False, {'error': 'No tasks found'})
            return False
            
        # Test analysis on first task
        task = tasks[0]
        task_id = task.get('id')
        
        success, response, response_time = self.make_request(
            'POST',
            'hrm/analyze',
            data={
                'entity_type': 'task',
                'entity_id': task_id,
                'analysis_depth': 'balanced',
                'force_llm': True
            }
        )
        
        if success:
            # Verify enhanced reasoning quality
            reasoning_quality = self._assess_reasoning_quality(response)
            
            details = {
                'task_id': task_id,
                'task_name': task.get('name', 'Unknown'),
                'confidence_score': response.get('confidence_score'),
                'reasoning_quality': reasoning_quality,
                'recommendations_count': len(response.get('recommendations', [])),
                'used_llm': response.get('used_llm', False)
            }
            
            test_passed = reasoning_quality['score'] >= 70  # Expect high quality with GPT-5 nano
            self.log_test("Task-Level Analysis", test_passed, details, response_time)
            return test_passed
        else:
            self.log_test("Task-Level Analysis", False, response, response_time)
            return False

    def test_ai_coach_enhancement(self) -> bool:
        """Test AI Coach with enhanced GPT-5 nano reasoning"""
        print("\n🤖 Testing AI Coach Enhancement...")
        
        # Test today priorities with enhanced coaching
        success, response, response_time = self.make_request(
            'GET',
            'ai/today-priorities',
            params={
                'top_n': 5,
                'include_hrm': True
            }
        )
        
        if success:
            # Verify enhanced coaching quality
            coaching_quality = self._assess_coaching_quality(response)
            
            details = {
                'tasks_count': len(response.get('tasks', [])),
                'has_coaching_messages': bool(response.get('coaching_message')),
                'coaching_quality': coaching_quality,
                'response_structure': list(response.keys())
            }
            
            test_passed = coaching_quality['score'] >= 70
            self.log_test("AI Coach Enhancement", test_passed, details, response_time)
            return test_passed
        else:
            self.log_test("AI Coach Enhancement", False, response, response_time)
            return False

    def test_why_statements_generation(self) -> bool:
        """Test enhanced why-statements with GPT-5 nano"""
        print("\n❓ Testing Why-Statements Generation...")
        
        # Get tasks first
        success, tasks_response, _ = self.make_request('GET', 'tasks', params={'limit': 3})
        
        if not success:
            self.log_test("Why-Statements Generation", False, {'error': 'Could not get tasks'})
            return False
            
        tasks = tasks_response if isinstance(tasks_response, list) else tasks_response.get('tasks', [])
        
        if not tasks:
            self.log_test("Why-Statements Generation", False, {'error': 'No tasks found'})
            return False
            
        task_ids = [task.get('id') for task in tasks[:3] if task.get('id')]
        
        success, response, response_time = self.make_request(
            'GET',
            'ai/task-why-statements',
            params={'task_ids': task_ids}
        )
        
        if success:
            # Verify why-statements quality
            why_quality = self._assess_why_statements_quality(response)
            
            details = {
                'task_ids_requested': len(task_ids),
                'why_statements_received': len(response.get('why_statements', [])),
                'quality_score': why_quality['score'],
                'has_confidence_scores': why_quality['has_confidence'],
                'has_reasoning_paths': why_quality['has_reasoning']
            }
            
            test_passed = why_quality['score'] >= 70
            self.log_test("Why-Statements Generation", test_passed, details, response_time)
            return test_passed
        else:
            self.log_test("Why-Statements Generation", False, response, response_time)
            return False

    def test_ai_intelligence_center(self) -> bool:
        """Test AI Intelligence Center integration"""
        print("\n🧠 Testing AI Intelligence Center...")
        
        # Test insights retrieval
        success, response, response_time = self.make_request(
            'GET',
            'hrm/insights',
            params={
                'limit': 10,
                'is_active': True
            }
        )
        
        if success:
            insights = response.get('insights', [])
            
            details = {
                'insights_count': len(insights),
                'has_confidence_scores': any('confidence_score' in insight for insight in insights),
                'has_reasoning_paths': any('reasoning_path' in insight for insight in insights),
                'insight_types': list(set(insight.get('insight_type') for insight in insights))
            }
            
            test_passed = len(insights) >= 0  # Should work even with no insights
            self.log_test("AI Intelligence Center", test_passed, details, response_time)
            return test_passed
        else:
            self.log_test("AI Intelligence Center", False, response, response_time)
            return False

    def test_performance_comparison(self) -> bool:
        """Test performance with GPT-5 nano"""
        print("\n⚡ Testing Performance...")
        
        # Test multiple concurrent AI operations
        start_time = time.time()
        
        # Run 3 concurrent-like operations
        operations = []
        
        # Operation 1: HRM Analysis
        success1, response1, time1 = self.make_request(
            'POST',
            'hrm/analyze',
            data={
                'entity_type': 'global',
                'analysis_depth': 'minimal',
                'force_llm': True
            }
        )
        operations.append(('HRM Analysis', success1, time1))
        
        # Operation 2: Today Priorities
        success2, response2, time2 = self.make_request(
            'GET',
            'ai/today-priorities',
            params={'top_n': 3, 'include_hrm': True}
        )
        operations.append(('Today Priorities', success2, time2))
        
        # Operation 3: Insights
        success3, response3, time3 = self.make_request(
            'GET',
            'hrm/insights',
            params={'limit': 5}
        )
        operations.append(('Insights', success3, time3))
        
        total_time = time.time() - start_time
        
        # Assess performance
        successful_ops = sum(1 for _, success, _ in operations if success)
        avg_response_time = sum(t for _, _, t in operations) / len(operations)
        
        details = {
            'total_operations': len(operations),
            'successful_operations': successful_ops,
            'total_time': total_time,
            'average_response_time': avg_response_time,
            'operations': [{'name': name, 'success': success, 'time': t} for name, success, t in operations]
        }
        
        # Performance criteria: All operations should succeed and average response time < 10s
        test_passed = successful_ops == len(operations) and avg_response_time < 10.0
        
        self.log_test("Performance Test", test_passed, details, total_time)
        return test_passed

    def _assess_reasoning_quality(self, response: Dict) -> Dict:
        """Assess the quality of reasoning in HRM response"""
        score = 0
        
        # Check confidence score
        confidence = response.get('confidence_score', 0)
        if confidence > 70:
            score += 30
        elif confidence > 50:
            score += 20
        elif confidence > 30:
            score += 10
            
        # Check reasoning path
        reasoning_path = response.get('reasoning_path', [])
        if len(reasoning_path) >= 3:
            score += 25
        elif len(reasoning_path) >= 2:
            score += 15
        elif len(reasoning_path) >= 1:
            score += 10
            
        # Check recommendations
        recommendations = response.get('recommendations', [])
        if len(recommendations) >= 3:
            score += 25
        elif len(recommendations) >= 2:
            score += 15
        elif len(recommendations) >= 1:
            score += 10
            
        # Check summary quality (basic length check)
        summary = response.get('summary', '')
        if len(summary) > 100:
            score += 20
        elif len(summary) > 50:
            score += 10
            
        return {
            'score': score,
            'confidence': confidence,
            'reasoning_steps': len(reasoning_path),
            'recommendations_count': len(recommendations),
            'summary_length': len(summary)
        }

    def _assess_coaching_quality(self, response: Dict) -> Dict:
        """Assess the quality of AI coaching messages"""
        score = 0
        
        # Check if coaching message exists
        coaching_message = response.get('coaching_message', '')
        if coaching_message:
            score += 30
            
            # Check message quality (length and content)
            if len(coaching_message) > 100:
                score += 20
            elif len(coaching_message) > 50:
                score += 10
                
        # Check task prioritization quality
        tasks = response.get('tasks', [])
        if tasks:
            # Check if tasks have scores
            scored_tasks = [t for t in tasks if 'score' in t]
            if len(scored_tasks) == len(tasks):
                score += 25
                
            # Check if tasks have HRM insights
            hrm_tasks = [t for t in tasks if 'hrm_insight' in t]
            if hrm_tasks:
                score += 25
                
        return {
            'score': score,
            'has_coaching_message': bool(coaching_message),
            'coaching_message_length': len(coaching_message),
            'tasks_with_scores': len([t for t in tasks if 'score' in t]),
            'tasks_with_hrm': len([t for t in tasks if 'hrm_insight' in t])
        }

    def _assess_why_statements_quality(self, response: Dict) -> Dict:
        """Assess the quality of why-statements"""
        score = 0
        
        why_statements = response.get('why_statements', [])
        
        if why_statements:
            score += 30
            
            # Check if statements have confidence scores
            with_confidence = [w for w in why_statements if 'confidence_score' in w]
            if len(with_confidence) == len(why_statements):
                score += 25
                
            # Check if statements have reasoning
            with_reasoning = [w for w in why_statements if 'reasoning_path' in w]
            if with_reasoning:
                score += 25
                
            # Check statement quality (length)
            avg_length = sum(len(w.get('why_statement', '')) for w in why_statements) / len(why_statements)
            if avg_length > 100:
                score += 20
            elif avg_length > 50:
                score += 10
                
        return {
            'score': score,
            'statements_count': len(why_statements),
            'has_confidence': len([w for w in why_statements if 'confidence_score' in w]),
            'has_reasoning': len([w for w in why_statements if 'reasoning_path' in w]),
            'avg_statement_length': sum(len(w.get('why_statement', '')) for w in why_statements) / len(why_statements) if why_statements else 0
        }

    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting Enhanced AI System Testing with GPT-5 nano")
        print("=" * 60)
        
        # Authentication is required for all other tests
        if not self.test_authentication():
            print("\n❌ Authentication failed. Cannot proceed with other tests.")
            return False
            
        # Run all AI enhancement tests
        test_methods = [
            self.test_hrm_global_analysis,
            self.test_task_level_analysis,
            self.test_ai_coach_enhancement,
            self.test_why_statements_generation,
            self.test_ai_intelligence_center,
            self.test_performance_comparison
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
        print("📊 TEST SUMMARY")
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
                    print(f"    {test['details']}")
        
        # Print performance insights
        ai_tests = [r for r in self.test_results if 'HRM' in r['test_name'] or 'AI' in r['test_name']]
        if ai_tests:
            avg_ai_time = sum(r['response_time'] for r in ai_tests if r['response_time']) / len(ai_tests)
            print(f"\n⚡ AI PERFORMANCE:")
            print(f"  Average AI Response Time: {avg_ai_time:.2f}s")
            print(f"  AI Tests Passed: {len([t for t in ai_tests if t['success']])}/{len(ai_tests)}")

def main():
    """Main test execution"""
    tester = EnhancedAITester()
    
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