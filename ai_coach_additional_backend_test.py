#!/usr/bin/env python3
"""
🎯 AI COACH ADDITIONAL ENDPOINTS & JOURNAL TEMPLATES BACKEND SMOKE TEST
Tests the specific endpoints requested in review:
1) GET /api/ai/quota → expect 200 JSON with daily_limit, used, reset_at
2) POST /api/ai/decompose-project {project_name: 'Test', template_type:'general'} → expect 200 with suggested_tasks array (may be empty), total_tasks number
3) POST /api/ai/create-tasks-from-suggestions {project_id:'dummy', suggested_tasks:[{name:'T1'}]} → expect 200 with created (array) and count (number); may be empty
4) GET /api/journal/templates → expect 200 with array (even if empty)

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

class AiCoachAdditionalTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        
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
            
    async def run_ai_coach_tests(self):
        """Run AI Coach additional endpoint tests"""
        print("🎯 STARTING AI COACH ADDITIONAL ENDPOINTS TEST")
        print("=" * 60)
        
        # 1) GET /api/ai/quota → expect 200 JSON with daily_limit, used, reset_at
        print("\n1️⃣ Testing AI Quota endpoint...")
        quota_result = await self.test_endpoint('GET', '/ai/quota')
        
        if quota_result['success'] and quota_result['data']:
            data = quota_result['data']
            required_fields = ['daily_limit', 'used', 'reset_at']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️ Missing required fields in quota response: {missing_fields}")
            else:
                print(f"✅ Quota response has all required fields: daily_limit={data.get('daily_limit')}, used={data.get('used')}, reset_at={data.get('reset_at')}")
        
        # 2) POST /api/ai/decompose-project → expect 200 with suggested_tasks array, total_tasks number
        print("\n2️⃣ Testing AI Decompose Project endpoint...")
        decompose_payload = {
            "project_name": "Test Project for AI Decomposition",
            "template_type": "general"
        }
        
        decompose_result = await self.test_endpoint('POST', '/ai/decompose-project', json_data=decompose_payload)
        
        if decompose_result['success'] and decompose_result['data']:
            data = decompose_result['data']
            
            # Check for required fields
            if 'suggested_tasks' in data and 'total_tasks' in data:
                suggested_tasks = data['suggested_tasks']
                total_tasks = data['total_tasks']
                
                if isinstance(suggested_tasks, list):
                    print(f"✅ Decompose project returned suggested_tasks array with {len(suggested_tasks)} items")
                else:
                    print(f"⚠️ suggested_tasks is not an array: {type(suggested_tasks)}")
                
                if isinstance(total_tasks, (int, float)):
                    print(f"✅ Decompose project returned total_tasks number: {total_tasks}")
                else:
                    print(f"⚠️ total_tasks is not a number: {type(total_tasks)}")
                    
                # Show sample of suggested tasks if any
                if suggested_tasks and len(suggested_tasks) > 0:
                    print(f"📝 Sample suggested task: {suggested_tasks[0]}")
            else:
                missing = []
                if 'suggested_tasks' not in data:
                    missing.append('suggested_tasks')
                if 'total_tasks' not in data:
                    missing.append('total_tasks')
                print(f"⚠️ Missing required fields in decompose response: {missing}")
        
        # 3) POST /api/ai/create-tasks-from-suggestions → expect 200 with created array, count number
        print("\n3️⃣ Testing AI Create Tasks from Suggestions endpoint...")
        create_tasks_payload = {
            "project_id": "dummy-project-id-for-testing",
            "suggested_tasks": [
                {"name": "Test Task 1", "description": "First test task"},
                {"name": "Test Task 2", "description": "Second test task"}
            ]
        }
        
        create_tasks_result = await self.test_endpoint('POST', '/ai/create-tasks-from-suggestions', json_data=create_tasks_payload)
        
        if create_tasks_result['success'] and create_tasks_result['data']:
            data = create_tasks_result['data']
            
            # Check for required fields
            if 'created' in data and 'count' in data:
                created = data['created']
                count = data['count']
                
                if isinstance(created, list):
                    print(f"✅ Create tasks returned created array with {len(created)} items")
                else:
                    print(f"⚠️ created is not an array: {type(created)}")
                
                if isinstance(count, (int, float)):
                    print(f"✅ Create tasks returned count number: {count}")
                else:
                    print(f"⚠️ count is not a number: {type(count)}")
                    
                # Show sample of created tasks if any
                if created and len(created) > 0:
                    print(f"📝 Sample created task: {created[0]}")
            else:
                missing = []
                if 'created' not in data:
                    missing.append('created')
                if 'count' not in data:
                    missing.append('count')
                print(f"⚠️ Missing required fields in create tasks response: {missing}")
        
        # 4) GET /api/journal/templates → expect 200 with array (even if empty)
        print("\n4️⃣ Testing Journal Templates endpoint...")
        templates_result = await self.test_endpoint('GET', '/journal/templates')
        
        if templates_result['success'] and templates_result['data'] is not None:
            data = templates_result['data']
            
            if isinstance(data, list):
                print(f"✅ Journal templates returned array with {len(data)} items")
                
                # Show sample template if any
                if data and len(data) > 0:
                    template = data[0]
                    if isinstance(template, dict):
                        template_keys = list(template.keys())
                        print(f"📝 Sample template keys: {template_keys}")
                    else:
                        print(f"📝 Sample template: {template}")
            else:
                print(f"⚠️ Journal templates response is not an array: {type(data)}")
        
    def generate_summary(self) -> str:
        """Generate concise summary with pass/fail per endpoint"""
        print("\n" + "=" * 60)
        print("📊 AI COACH ADDITIONAL ENDPOINTS TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            endpoint = result['endpoint']
            status = result['status']
            response_time = result['response_time_ms']
            
            print(f"{status_icon} {endpoint:<45} {status} ({response_time}ms)")
            
            # Show error details for failures
            if not result['success'] and result['error']:
                if isinstance(result['error'], dict) and 'detail' in result['error']:
                    print(f"    Error: {result['error']['detail']}")
                elif isinstance(result['error'], str):
                    print(f"    Error: {result['error']}")
        
        print("\n" + "=" * 60)
        
        # Show payload examples used
        print("\n📝 SAMPLE PAYLOADS USED:")
        print("Authentication:")
        print(f"  {{'email': '{TEST_EMAIL}', 'password': '[REDACTED]'}}")
        
        print("\nDecompose Project:")
        decompose_payload = {
            "project_name": "Test Project for AI Decomposition",
            "template_type": "general"
        }
        print(f"  {json.dumps(decompose_payload, indent=2)}")
        
        print("\nCreate Tasks from Suggestions:")
        create_tasks_payload = {
            "project_id": "dummy-project-id-for-testing",
            "suggested_tasks": [
                {"name": "Test Task 1", "description": "First test task"},
                {"name": "Test Task 2", "description": "Second test task"}
            ]
        }
        print(f"  {json.dumps(create_tasks_payload, indent=2)}")
        
        return f"AI Coach additional endpoints test completed: {passed_tests}/{total_tests} passed ({(passed_tests/total_tests*100):.1f}%)"

async def main():
    """Main test execution"""
    test = AiCoachAdditionalTest()
    
    try:
        await test.setup_session()
        
        # Authenticate first
        if not await test.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
            
        # Run AI Coach additional tests
        await test.run_ai_coach_tests()
        
        # Generate summary
        summary = test.generate_summary()
        print(f"\n🎯 FINAL RESULT: {summary}")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
    finally:
        await test.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())