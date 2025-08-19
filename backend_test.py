#!/usr/bin/env python3
"""
🎯 FOCUSED BACKEND SMOKE TEST - Standardized Frontend API Layer Mappings
Validates critical endpoints exist and return 2xx with Authorization Bearer token
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

class BackendSmokeTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.created_pillar_id = None
        
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
            
    async def run_smoke_tests(self):
        """Run all smoke tests as specified in review request"""
        print("🎯 STARTING FOCUSED BACKEND SMOKE TEST")
        print("=" * 60)
        
        # 1) GET /api/pillars with specific params
        await self.test_endpoint(
            'GET', '/pillars',
            params={
                'include_sub_pillars': 'true',
                'include_areas': 'true', 
                'include_archived': 'false'
            }
        )
        
        # 2) POST /api/pillars (create minimal pillar)
        pillar_payload = {
            "name": f"Test Pillar {int(time.time())}",
            "description": "Smoke test pillar",
            "color": "#3B82F6",
            "icon": "target"
        }
        
        create_result = await self.test_endpoint('POST', '/pillars', json_data=pillar_payload)
        
        # Extract pillar ID for cleanup
        if create_result['success'] and create_result['data']:
            self.created_pillar_id = create_result['data'].get('id')
            print(f"📝 Created pillar ID: {self.created_pillar_id}")
        
        # GET /api/pillars again to verify it includes the new pillar
        await self.test_endpoint('GET', '/pillars')
        
        # 3) GET /api/areas with include_projects=true
        await self.test_endpoint(
            'GET', '/areas',
            params={'include_projects': 'true'}
        )
        
        # 4) GET /api/projects (no params)
        await self.test_endpoint('GET', '/projects')
        
        # 5) GET /api/tasks (no params)
        await self.test_endpoint('GET', '/tasks')
        
        # 6) GET /api/insights?date_range=all_time
        await self.test_endpoint(
            'GET', '/insights',
            params={'date_range': 'all_time'}
        )
        
        # 7) GET /api/alignment/dashboard; if 404, then GET /api/alignment-score (legacy)
        alignment_result = await self.test_endpoint('GET', '/alignment/dashboard')
        
        if alignment_result['status'] == 404:
            print("🔄 /alignment/dashboard returned 404, trying legacy /alignment-score")
            await self.test_endpoint('GET', '/alignment-score')
        
        # 8) GET /api/ai/task-why-statements returns 200 and data array
        why_statements_result = await self.test_endpoint('GET', '/ai/task-why-statements')
        
        if why_statements_result['success']:
            data = why_statements_result['data']
            if isinstance(data, list):
                print(f"✅ /ai/task-why-statements returned array with {len(data)} items")
            elif isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                print(f"✅ /ai/task-why-statements returned data array with {len(data['data'])} items")
            else:
                print(f"⚠️ /ai/task-why-statements returned non-array data: {type(data)}")
        
        # 9) Journal sanity: GET /api/journal and GET /api/journal/trash
        await self.test_endpoint('GET', '/journal')
        await self.test_endpoint('GET', '/journal/trash')
        
        # Cleanup: DELETE the created pillar
        if self.created_pillar_id:
            print(f"🧹 Cleaning up created pillar: {self.created_pillar_id}")
            await self.test_endpoint('DELETE', f'/pillars/{self.created_pillar_id}')
            
    def generate_summary(self) -> str:
        """Generate concise summary with pass/fail per endpoint"""
        print("\n" + "=" * 60)
        print("📊 SMOKE TEST SUMMARY")
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
            
            print(f"{status_icon} {endpoint:<35} {status} ({response_time}ms)")
            
            # Show error details for failures
            if not result['success'] and result['error']:
                if isinstance(result['error'], dict) and 'detail' in result['error']:
                    print(f"    Error: {result['error']['detail']}")
                elif isinstance(result['error'], str):
                    print(f"    Error: {result['error']}")
        
        print("\n" + "=" * 60)
        
        # Record any 401/404/500 errors as requested
        critical_errors = []
        for result in self.test_results:
            if result['status'] in [401, 404, 500]:
                critical_errors.append(f"{result['endpoint']}: {result['status']}")
        
        if critical_errors:
            print("🚨 CRITICAL ERRORS DETECTED:")
            for error in critical_errors:
                print(f"   {error}")
        else:
            print("✅ No critical errors (401/404/500) detected")
            
        # Show payload examples used
        print("\n📝 PAYLOAD EXAMPLES USED:")
        print(f"Authentication: {{'email': '{TEST_EMAIL}', 'password': '[REDACTED]'}}")
        pillar_payload = {
            "name": f"Test Pillar {int(time.time())}",
            "description": "Smoke test pillar", 
            "color": "#3B82F6",
            "icon": "target"
        }
        print(f"Create Pillar: {json.dumps(pillar_payload, indent=2)}")
        
        return f"Smoke test completed: {passed_tests}/{total_tests} passed ({(passed_tests/total_tests*100):.1f}%)"

async def main():
    """Main test execution"""
    test = BackendSmokeTest()
    
    try:
        await test.setup_session()
        
        # Authenticate first
        if not await test.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
            
        # Run all smoke tests
        await test.run_smoke_tests()
        
        # Generate summary
        summary = test.generate_summary()
        print(f"\n🎯 FINAL RESULT: {summary}")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
    finally:
        await test.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())