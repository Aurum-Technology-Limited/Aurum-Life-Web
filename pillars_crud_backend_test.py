#!/usr/bin/env python3
"""
ULTRA CACHE INVALIDATION VERIFICATION FOR PILLARS
Testing specific flow as requested in review:
1) Login with marc.alleyne@aurumtechnologyltd.com / password123
2) POST /api/pillars with name "E2E Ultra Cache Check <timestamp>"
3) GET /api/pillars → ensure item present
4) GET /api/ultra/pillars → ensure item present (no stale miss)
5) DELETE the created id
6) GET /api/pillars → ensure removed
7) GET /api/ultra/pillars → ensure removed (no stale presence)

Expected output:
- PASS/FAIL and timings for each step
- Verification that ultra cache invalidation works correctly
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://fastapi-react-fix.preview.emergentagent.com/api"

class PillarsCRUDTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        self.created_pillar_id = None
        self.test_results = []
        
    def log_result(self, step: str, success: bool, message: str, response_time: float = None, data: Any = None):
        """Log test results with timing"""
        result = {
            'step': step,
            'success': success,
            'message': message,
            'response_time_ms': round(response_time * 1000) if response_time else None,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        timing = f" ({result['response_time_ms']}ms)" if response_time else ""
        print(f"{status} {step}{timing}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with timing and error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response_time': response_time,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            error_msg = f"Request failed: {str(e)}"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': None,
                'data': {},
                'response_time': response_time
            }

    def step_1_login(self) -> bool:
        """Step 1: Login with marc.alleyne@aurumtechnologyltd.com / password123. Expect 200 and bearer token."""
        print("\n=== STEP 1: LOGIN AUTHENTICATION ===")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success'] and result['status_code'] == 200:
            token_data = result['data']
            self.auth_token = token_data.get('access_token')
            
            if self.auth_token:
                self.log_result(
                    "LOGIN", 
                    True, 
                    f"Successfully authenticated with {self.test_user_email}, received bearer token",
                    result['response_time']
                )
                return True
            else:
                self.log_result(
                    "LOGIN", 
                    False, 
                    "Login returned 200 but no access_token in response",
                    result['response_time'],
                    token_data
                )
                return False
        else:
            self.log_result(
                "LOGIN", 
                False, 
                f"Login failed: {result.get('error', 'Unknown error')}",
                result['response_time']
            )
            return False

    def step_2_create_pillar(self) -> bool:
        """Step 2: Create pillar with specific format. Expect 200 and capture id/uuid."""
        print("\n=== STEP 2: CREATE PILLAR ===")
        
        timestamp = int(time.time())
        pillar_data = {
            "name": f"E2E Ultra Cache Check {timestamp}",
            "description": "Ultra cache invalidation verification",
            "icon": "🎯",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            pillar_response = result['data']
            
            # Look for id field (could be 'id', 'uuid', or other)
            pillar_id = None
            id_field_name = None
            
            for field in ['id', 'uuid', 'pillar_id']:
                if field in pillar_response:
                    pillar_id = pillar_response[field]
                    id_field_name = field
                    break
            
            if pillar_id:
                self.created_pillar_id = pillar_id
                self.log_result(
                    "CREATE PILLAR", 
                    True, 
                    f"Pillar created successfully, {id_field_name}: {pillar_id}",
                    result['response_time'],
                    {id_field_name: pillar_id, "name": pillar_response.get('name')}
                )
                return True
            else:
                self.log_result(
                    "CREATE PILLAR", 
                    False, 
                    "Pillar creation returned 200 but no id/uuid field found",
                    result['response_time'],
                    pillar_response
                )
                return False
        else:
            self.log_result(
                "CREATE PILLAR", 
                False, 
                f"Pillar creation failed: {result.get('error', 'Unknown error')}",
                result['response_time']
            )
            return False

    def step_3_read_standard_pillars(self) -> Dict[str, Any]:
        """Step 3: Read list (standard): GET /api/pillars. Verify created item is present."""
        print("\n=== STEP 3: READ STANDARD PILLARS ===")
        
        params = {
            "include_sub_pillars": "true",
            "include_areas": "true", 
            "include_archived": "false"
        }
        
        result = self.make_request('GET', '/pillars', params=params, use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            pillars = result['data']
            
            # Find created pillar by id and name
            created_pillar = None
            for pillar in pillars:
                if (pillar.get('id') == self.created_pillar_id or 
                    pillar.get('uuid') == self.created_pillar_id or
                    pillar.get('name', '').startswith('E2E Ultra Cache Check')):
                    created_pillar = pillar
                    break
            
            if created_pillar:
                self.log_result(
                    "READ STANDARD PILLARS", 
                    True, 
                    f"Created pillar found in standard list, total pillars: {len(pillars)}",
                    result['response_time'],
                    {"found_pillar": created_pillar.get('name'), "total_count": len(pillars)}
                )
                return {"success": True, "pillars": pillars, "found_pillar": created_pillar}
            else:
                self.log_result(
                    "READ STANDARD PILLARS", 
                    False, 
                    f"Created pillar NOT found in standard list, total pillars: {len(pillars)}",
                    result['response_time'],
                    {"pillar_names": [p.get('name') for p in pillars]}
                )
                return {"success": False, "pillars": pillars, "found_pillar": None}
        else:
            self.log_result(
                "READ STANDARD PILLARS", 
                False, 
                f"Standard pillars retrieval failed: {result.get('error', 'Unknown error')}",
                result['response_time']
            )
            return {"success": False, "pillars": [], "found_pillar": None}

    def step_4_read_ultra_pillars(self) -> Dict[str, Any]:
        """Step 4: Read list (ultra): GET /api/ultra/pillars. Verify created item is present."""
        print("\n=== STEP 4: READ ULTRA PILLARS ===")
        
        params = {
            "include_areas": "true",
            "include_archived": "false"
        }
        
        result = self.make_request('GET', '/ultra/pillars', params=params, use_auth=True)
        
        if result['success'] and result['status_code'] == 200:
            pillars = result['data']
            
            # Find created pillar by id and name
            created_pillar = None
            for pillar in pillars:
                if (pillar.get('id') == self.created_pillar_id or 
                    pillar.get('uuid') == self.created_pillar_id or
                    pillar.get('name', '').startswith('E2E Ultra Cache Check')):
                    created_pillar = pillar
                    break
            
            if created_pillar:
                self.log_result(
                    "READ ULTRA PILLARS", 
                    True, 
                    f"Created pillar found in ultra list, total pillars: {len(pillars)}",
                    result['response_time'],
                    {"found_pillar": created_pillar.get('name'), "total_count": len(pillars)}
                )
                return {"success": True, "pillars": pillars, "found_pillar": created_pillar}
            else:
                self.log_result(
                    "READ ULTRA PILLARS", 
                    False, 
                    f"Created pillar NOT found in ultra list, total pillars: {len(pillars)}",
                    result['response_time'],
                    {"pillar_names": [p.get('name') for p in pillars]}
                )
                return {"success": False, "pillars": pillars, "found_pillar": None}
        else:
            self.log_result(
                "READ ULTRA PILLARS", 
                False, 
                f"Ultra pillars retrieval failed: {result.get('error', 'Unknown error')}",
                result['response_time']
            )
            return {"success": False, "pillars": [], "found_pillar": None}

    def step_5_delete_pillar(self) -> bool:
        """Step 5: Delete created pillar. Expect 200 or 204."""
        print("\n=== STEP 5: DELETE PILLAR ===")
        
        if not self.created_pillar_id:
            self.log_result(
                "DELETE PILLAR", 
                False, 
                "No pillar ID available for deletion",
                None
            )
            return False
        
        result = self.make_request('DELETE', f'/pillars/{self.created_pillar_id}', use_auth=True)
        
        if result['success'] and result['status_code'] in [200, 204]:
            self.log_result(
                "DELETE PILLAR", 
                True, 
                f"Pillar deleted successfully (HTTP {result['status_code']})",
                result['response_time']
            )
            return True
        else:
            self.log_result(
                "DELETE PILLAR", 
                False, 
                f"Pillar deletion failed: {result.get('error', 'Unknown error')}",
                result['response_time']
            )
            return False

    def step_6_confirm_removal(self) -> bool:
        """Step 6: Confirm removal by repeating steps 3 and 4."""
        print("\n=== STEP 6: CONFIRM REMOVAL ===")
        
        # Check standard pillars
        standard_result = self.step_3_read_standard_pillars()
        standard_removed = not standard_result["success"] or standard_result["found_pillar"] is None
        
        # Check ultra pillars  
        ultra_result = self.step_4_read_ultra_pillars()
        ultra_removed = not ultra_result["success"] or ultra_result["found_pillar"] is None
        
        if standard_removed and ultra_removed:
            self.log_result(
                "CONFIRM REMOVAL", 
                True, 
                "Pillar successfully removed from both standard and ultra endpoints",
                None
            )
            return True
        else:
            issues = []
            if not standard_removed:
                issues.append("still present in standard endpoint")
            if not ultra_removed:
                issues.append("still present in ultra endpoint")
            
            self.log_result(
                "CONFIRM REMOVAL", 
                False, 
                f"Pillar removal incomplete: {', '.join(issues)}",
                None
            )
            return False

    def compare_standard_vs_ultra(self, standard_result: Dict, ultra_result: Dict) -> bool:
        """Compare standard and ultra results for consistency"""
        print("\n=== COMPARING STANDARD VS ULTRA CONSISTENCY ===")
        
        if not standard_result["success"] or not ultra_result["success"]:
            print("⚠️ Cannot compare - one or both endpoints failed")
            return False
        
        standard_pillars = standard_result["pillars"]
        ultra_pillars = ultra_result["pillars"]
        
        # Compare counts
        standard_count = len(standard_pillars)
        ultra_count = len(ultra_pillars)
        
        # Compare if created pillar is present in both
        standard_has_pillar = standard_result["found_pillar"] is not None
        ultra_has_pillar = ultra_result["found_pillar"] is not None
        
        consistent = (standard_count == ultra_count and 
                     standard_has_pillar == ultra_has_pillar)
        
        if consistent:
            print(f"✅ CONSISTENCY CHECK: Both endpoints returned {standard_count} pillars, created pillar present in both: {standard_has_pillar}")
        else:
            print(f"❌ CONSISTENCY MISMATCH:")
            print(f"   Standard: {standard_count} pillars, created pillar present: {standard_has_pillar}")
            print(f"   Ultra: {ultra_count} pillars, created pillar present: {ultra_has_pillar}")
        
        return consistent

    def run_ultra_cache_verification(self):
        """Run the complete ultra cache invalidation verification flow"""
        print("🎯 STARTING ULTRA CACHE INVALIDATION VERIFICATION FOR PILLARS")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Execute the 7-step flow as specified in review request
        step_results = []
        
        # Step 1: Login
        step_results.append(self.step_1_login())
        if not step_results[-1]:
            print("\n❌ CRITICAL: Login failed, cannot proceed with verification")
            return False
        
        # Step 2: Create pillar
        step_results.append(self.step_2_create_pillar())
        if not step_results[-1]:
            print("\n❌ CRITICAL: Pillar creation failed, cannot proceed with verification")
            return False
        
        # Step 3: Read standard pillars
        standard_result = self.step_3_read_standard_pillars()
        step_results.append(standard_result["success"])
        
        # Step 4: Read ultra pillars
        ultra_result = self.step_4_read_ultra_pillars()
        step_results.append(ultra_result["success"])
        
        # Compare consistency after creation
        consistency_after_create = self.compare_standard_vs_ultra(standard_result, ultra_result)
        
        # Step 5: Delete pillar
        step_results.append(self.step_5_delete_pillar())
        
        # Step 6 & 7: Confirm removal from both endpoints
        step_results.append(self.step_6_confirm_removal())
        
        # Calculate overall result
        successful_steps = sum(step_results)
        total_steps = len(step_results)
        
        print(f"\n" + "=" * 80)
        print("📊 ULTRA CACHE INVALIDATION VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Steps Completed: {successful_steps}/{total_steps}")
        print(f"Cache Consistency After Create: {'✅ PASS' if consistency_after_create else '❌ FAIL'}")
        
        # Determine final result - all steps must pass AND consistency must be maintained
        cache_invalidation_success = (successful_steps == total_steps and consistency_after_create)
        
        if cache_invalidation_success:
            print("\n🎉 OVERALL RESULT: ✅ PASS")
            print("   ✅ Ultra cache invalidation working correctly")
            print("   ✅ Created item visible in both /api/pillars and /api/ultra/pillars")
            print("   ✅ Item successfully removed from both endpoints after DELETE")
            print("   ✅ No stale cache data detected")
        else:
            print("\n💥 OVERALL RESULT: ❌ FAIL")
            if successful_steps < total_steps:
                failed_steps = total_steps - successful_steps
                print(f"   ❌ {failed_steps} step(s) failed")
            if not consistency_after_create:
                print("   ❌ Ultra cache invalidation not working - inconsistent data between endpoints")
        
        # Show detailed results
        print(f"\n🔍 DETAILED STEP RESULTS:")
        step_names = ["Login", "Create Pillar", "Read Standard", "Read Ultra", "Delete Pillar", "Confirm Removal"]
        for i, (name, success) in enumerate(zip(step_names, step_results)):
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {i+1}. {status} {name}")
        
        # Show timing summary
        timed_results = [r for r in self.test_results if r.get('response_time_ms')]
        if timed_results:
            total_time = sum(r['response_time_ms'] for r in timed_results)
            avg_time = total_time / len(timed_results)
            print(f"\n⏱️ PERFORMANCE SUMMARY:")
            print(f"   Total API time: {total_time}ms")
            print(f"   Average response time: {avg_time:.0f}ms")
            print(f"   API calls made: {len(timed_results)}")
        
        return cache_invalidation_success

def main():
    """Run Focused CRUD Verification"""
    print("🎯 STARTING PILLARS FOCUSED BACKEND CRUD VERIFICATION")
    print("=" * 80)
    
    tester = PillarsCRUDTester()
    
    try:
        success = tester.run_ultra_cache_verification()
        
        print("\n" + "=" * 80)
        print("📋 FINAL VERIFICATION RESULT")
        print("=" * 80)
        
        if success:
            print("🎉 VERIFICATION: ✅ PASS")
            print("The Pillars CRUD verification completed successfully!")
        else:
            print("💥 VERIFICATION: ❌ FAIL") 
            print("Issues detected in Pillars CRUD operations.")
        
        print("=" * 80)
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during verification: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)