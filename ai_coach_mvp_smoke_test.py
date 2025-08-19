#!/usr/bin/env python3
"""
🎯 AI COACH MVP SMOKE TEST - New AI Coach MVP Routes Testing
Tests the new AI Coach MVP routes as requested in review:
1) GET /api/ai/task-why-statements (no params) → expect 200 and JSON with keys: why_statements (array), tasks_analyzed (number), vertical_alignment (object)
2) GET /api/ai/task-why-statements?task_ids=<comma separated some existing task ids> → expect same 200 shape
3) GET /api/ai/suggest-focus?top_n=3 → expect 200 and JSON with keys: date (string), tasks (array). Each task item should include id, title/name, project_name, area_name, score, breakdown, optional coaching_message

Using known test account: marc.alleyne@aurumtechnologyltd.com/password123
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

# Backend URL from frontend/.env
BACKEND_URL = "https://c7dc63d9-3764-48cb-a7be-e97dc0b89cd2.preview.emergentagent.com/api"

# Test credentials
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password123"

class AiCoachMvpSmokeTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.existing_task_ids = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self) -> bool:
        """Authenticate with test credentials and get Bearer token"""
        try:
            print(f"🔐 Authenticating with {TEST_EMAIL}...")
            start_time = time.time()
            
            auth_payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=auth_payload) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get('access_token')
                    if self.auth_token:
                        print(f"✅ Authentication successful ({response_time:.1f}ms)")
                        return True
                    else:
                        print(f"❌ Authentication failed: No access_token in response")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
        
    async def test_endpoint(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                          json_data: Optional[Dict] = None, expected_status: int = 200) -> Dict[str, Any]:
        """Test a single endpoint and record results"""
        try:
            print(f"🧪 Testing {method} {endpoint}")
            start_time = time.time()
            
            url = f"{BACKEND_URL}{endpoint}"
            headers = self.get_auth_headers()
            
            async with self.session.request(
                method, url, 
                headers=headers, 
                params=params, 
                json=json_data
            ) as response:
                response_time = (time.time() - start_time) * 1000
                status = response.status
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                result = {
                    'endpoint': f"{method} {endpoint}",
                    'status': status,
                    'response_time_ms': round(response_time, 1),
                    'success': 200 <= status < 300,
                    'data': response_data if status < 400 else None,
                    'error': response_data if status >= 400 else None
                }
                
                if result['success']:
                    print(f"✅ {method} {endpoint} - {status} ({response_time:.1f}ms)")
                else:
                    print(f"❌ {method} {endpoint} - {status} ({response_time:.1f}ms)")
                    if isinstance(response_data, dict) and 'detail' in response_data:
                        print(f"   Error: {response_data['detail']}")
                
                self.test_results.append(result)
                return result
                
        except Exception as e:
            print(f"❌ {method} {endpoint} - Exception: {e}")
            result = {
                'endpoint': f"{method} {endpoint}",
                'status': 0,
                'response_time_ms': 0,
                'success': False,
                'data': None,
                'error': str(e)
            }
            self.test_results.append(result)
            return result
    
    async def get_existing_task_ids(self) -> List[str]:
        """Get some existing task IDs for testing"""
        try:
            print("📋 Fetching existing task IDs...")
            result = await self.test_endpoint('GET', '/tasks')
            
            if result['success'] and result['data']:
                tasks = result['data']
                if isinstance(tasks, list) and len(tasks) > 0:
                    # Get up to 3 task IDs for testing
                    task_ids = [task.get('id') for task in tasks[:3] if task.get('id')]
                    self.existing_task_ids = task_ids
                    print(f"✅ Found {len(task_ids)} existing task IDs: {task_ids}")
                    return task_ids
                else:
                    print("⚠️ No tasks found in response")
                    return []
            else:
                print("⚠️ Failed to fetch tasks")
                # Try to get task IDs from the why statements response
                why_result = await self.test_endpoint('GET', '/ai/task-why-statements')
                if why_result['success'] and why_result['data']:
                    why_statements = why_result['data'].get('why_statements', [])
                    if why_statements:
                        task_ids = [stmt.get('task_id') for stmt in why_statements[:2] if stmt.get('task_id')]
                        self.existing_task_ids = task_ids
                        print(f"✅ Extracted {len(task_ids)} task IDs from why statements: {task_ids}")
                        return task_ids
                return []
                
        except Exception as e:
            print(f"❌ Error fetching task IDs: {e}")
            return []
            
    def validate_task_why_statements_response(self, data: Any) -> bool:
        """Validate the structure of task-why-statements response"""
        if not isinstance(data, dict):
            print(f"❌ Response is not a dict: {type(data)}")
            return False
            
        required_keys = ['why_statements', 'tasks_analyzed', 'vertical_alignment']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            print(f"❌ Missing required keys: {missing_keys}")
            return False
            
        # Validate why_statements is an array
        if not isinstance(data.get('why_statements'), list):
            print(f"❌ why_statements is not an array: {type(data.get('why_statements'))}")
            return False
            
        # Validate tasks_analyzed is a number
        if not isinstance(data.get('tasks_analyzed'), (int, float)):
            print(f"❌ tasks_analyzed is not a number: {type(data.get('tasks_analyzed'))}")
            return False
            
        # Validate vertical_alignment is an object
        if not isinstance(data.get('vertical_alignment'), dict):
            print(f"❌ vertical_alignment is not an object: {type(data.get('vertical_alignment'))}")
            return False
            
        print("✅ Task why statements response structure is valid")
        return True
        
    def validate_suggest_focus_response(self, data: Any) -> bool:
        """Validate the structure of suggest-focus response"""
        if not isinstance(data, dict):
            print(f"❌ Response is not a dict: {type(data)}")
            return False
            
        required_keys = ['date', 'tasks']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            print(f"❌ Missing required keys: {missing_keys}")
            return False
            
        # Validate date is a string
        if not isinstance(data.get('date'), str):
            print(f"❌ date is not a string: {type(data.get('date'))}")
            return False
            
        # Validate tasks is an array
        if not isinstance(data.get('tasks'), list):
            print(f"❌ tasks is not an array: {type(data.get('tasks'))}")
            return False
            
        # Validate task items structure
        tasks = data.get('tasks', [])
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                print(f"❌ Task {i} is not an object: {type(task)}")
                return False
                
            # Check for required task fields
            task_required_fields = ['id', 'score', 'breakdown']
            # title/name is flexible - could be either
            has_title_or_name = 'title' in task or 'name' in task
            if not has_title_or_name:
                print(f"❌ Task {i} missing title or name field")
                return False
                
            missing_task_fields = [field for field in task_required_fields if field not in task]
            if missing_task_fields:
                print(f"❌ Task {i} missing required fields: {missing_task_fields}")
                return False
                
        print("✅ Suggest focus response structure is valid")
        return True
            
    async def run_ai_coach_mvp_tests(self):
        """Run all AI Coach MVP smoke tests as specified in review request"""
        print("🎯 STARTING AI COACH MVP SMOKE TEST")
        print("=" * 60)
        
        # First, get some existing task IDs for testing
        await self.get_existing_task_ids()
        
        # Test 1: GET /api/ai/task-why-statements (no params)
        print("\n📝 Test 1: GET /api/ai/task-why-statements (no params)")
        result1 = await self.test_endpoint('GET', '/ai/task-why-statements')
        
        if result1['success']:
            if self.validate_task_why_statements_response(result1['data']):
                print("✅ Test 1 PASSED: Response structure is valid")
                print(f"   Sample response: {json.dumps(result1['data'], indent=2)[:200]}...")
            else:
                print("❌ Test 1 FAILED: Invalid response structure")
        else:
            print("❌ Test 1 FAILED: Request failed")
            
        # Test 2: GET /api/ai/task-why-statements?task_ids=<comma separated task ids>
        print("\n📝 Test 2: GET /api/ai/task-why-statements with task_ids parameter")
        if self.existing_task_ids:
            task_ids_param = ','.join(self.existing_task_ids)
            result2 = await self.test_endpoint(
                'GET', '/ai/task-why-statements',
                params={'task_ids': task_ids_param}
            )
            
            if result2['success']:
                if self.validate_task_why_statements_response(result2['data']):
                    print("✅ Test 2 PASSED: Response structure is valid")
                    print(f"   Sample response: {json.dumps(result2['data'], indent=2)[:200]}...")
                else:
                    print("❌ Test 2 FAILED: Invalid response structure")
            else:
                print("❌ Test 2 FAILED: Request failed")
        else:
            print("⚠️ Test 2 SKIPPED: No existing task IDs found")
            result2 = {'success': False, 'error': 'No task IDs available'}
            
        # Test 3: GET /api/ai/suggest-focus?top_n=3
        print("\n📝 Test 3: GET /api/ai/suggest-focus?top_n=3")
        result3 = await self.test_endpoint(
            'GET', '/ai/suggest-focus',
            params={'top_n': 3}
        )
        
        if result3['success']:
            if self.validate_suggest_focus_response(result3['data']):
                print("✅ Test 3 PASSED: Response structure is valid")
                print(f"   Sample response: {json.dumps(result3['data'], indent=2)[:200]}...")
            else:
                print("❌ Test 3 FAILED: Invalid response structure")
        else:
            print("❌ Test 3 FAILED: Request failed")
            
        return [result1, result2, result3]
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 AI COACH MVP SMOKE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {result['endpoint']} - {result['status']} ({result['response_time_ms']}ms)")
            if not result['success'] and result['error']:
                print(f"   Error: {result['error']}")
                
        print("\n🎯 AI COACH MVP ENDPOINTS TEST COMPLETED!")

async def main():
    """Main test execution"""
    test = AiCoachMvpSmokeTest()
    
    try:
        await test.setup_session()
        
        # Authenticate first
        if not await test.authenticate():
            print("❌ Authentication failed, cannot proceed with tests")
            return
            
        # Run AI Coach MVP tests
        await test.run_ai_coach_mvp_tests()
        
        # Print summary
        test.print_summary()
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
    finally:
        await test.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())