#!/usr/bin/env python3
"""
Admin Operations Testing - Migration and Purge Legacy Users
Tests the specific admin operations from the review request:
1) Execute migration (non-dry run) with admin_token
2) Purge legacy users (dry run) with admin_token  
3) Final purge (non-dry run) with admin_token

These endpoints now only require admin_token (no user authentication needed).
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://prodflow-auth.preview.emergentagent.com/api"
ADMIN_TOKEN = "e8wXf6Ymo_mq__rPet2oc8nzE_V6eVZTY8qV8l7vcBwX6PI9fN_xsFN38s2eVkSJ"
LEGACY_EMAIL = "marc.alleyne@aurumtechnologyltd.com"

class AdminOperationsTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, step: str, success: bool, status_code: int = None, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            "step": step,
            "success": success,
            "status_code": status_code,
            "details": details,
            "response_time_ms": round(response_time * 1000, 1)
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_str = f"({result['response_time_ms']}ms)" if response_time > 0 else ""
        print(f"{status} {step} - Status: {status_code} {time_str}")
        if details:
            print(f"    Details: {details}")
        print()

    def make_request(self, method: str, endpoint: str, **kwargs) -> tuple:
        """Make HTTP request with timing"""
        url = f"{BACKEND_URL}{endpoint}"
            
        start_time = time.time()
        try:
            response = self.session.request(method, url, timeout=60, **kwargs)
            end_time = time.time()
            return response, end_time - start_time
        except Exception as e:
            end_time = time.time()
            print(f"Request failed: {e}")
            # Create a mock response for error handling
            class MockResponse:
                def __init__(self, error_msg):
                    self.status_code = 0
                    self.text = str(error_msg)
                    self.error_msg = error_msg
                def json(self):
                    return {"error": str(self.error_msg)}
            return MockResponse(e), end_time - start_time

    def test_step_1_health_check(self):
        """Step 1: Verify backend is accessible"""
        print("🏥 Step 1: Testing GET /api/health")
        
        response, response_time = self.make_request("GET", "/health")
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                details = f"Backend healthy: {data.get('status', 'unknown')}"
            except Exception as e:
                details = f"Health check passed but JSON parse failed: {e}"
        else:
            details = f"Health check failed: {response.text[:200]}"
            
        self.log_result("GET /api/health", success, response.status_code, details, response_time)
        return success

    def test_step_2_migration_non_dry_run(self):
        """Step 2: Execute migration (non-dry run)"""
        print("🔄 Step 2: Testing POST /api/admin/migrate-legacy-to-supabase (non-dry run)")
        
        payload = {
            "admin_token": ADMIN_TOKEN,
            "legacy_email": LEGACY_EMAIL,
            "create_auth_if_missing": True,
            "dry_run": False
        }
        
        response, response_time = self.make_request("POST", "/admin/migrate-legacy-to-supabase", json=payload)
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                legacy_id = data.get("legacy_id", "N/A")
                supa_id = data.get("supa_id", "N/A")
                email = data.get("email", "N/A")
                updated_counts = data.get("updated_counts", {})
                temp_password = data.get("created_temp_password")
                
                details = f"Migration completed - Legacy ID: {legacy_id}, Supabase ID: {supa_id}, Email: {email}"
                if temp_password:
                    details += f", Temp password created: {temp_password[:8]}..."
                if updated_counts:
                    total_updates = sum(count.get("updated", 0) for count in updated_counts.values() if isinstance(count, dict))
                    details += f", Total records updated: {total_updates}"
                    
            except Exception as e:
                details = f"Migration response received but JSON parse failed: {e}"
        else:
            details = f"Migration failed: {response.text[:500]}"
            
        self.log_result("POST /api/admin/migrate-legacy-to-supabase (non-dry run)", success, response.status_code, details, response_time)
        return success

    def test_step_3_purge_dry_run(self):
        """Step 3: Purge legacy users (dry run)"""
        print("🧹 Step 3: Testing POST /api/admin/purge-legacy-users (dry run)")
        
        payload = {
            "admin_token": ADMIN_TOKEN,
            "preserve_email": LEGACY_EMAIL,
            "dry_run": True
        }
        
        response, response_time = self.make_request("POST", "/admin/purge-legacy-users", json=payload)
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                total_users = data.get("total_legacy_users", 0)
                to_delete_count = data.get("to_delete_count", 0)
                preserved = data.get("preserved", "N/A")
                status = data.get("status", "unknown")
                sample_ids = data.get("sample_delete_ids", [])
                
                details = f"Dry run completed - Total legacy users: {total_users}, To delete: {to_delete_count}, Preserved: {preserved}, Status: {status}"
                if sample_ids:
                    details += f", Sample IDs to delete: {len(sample_ids)} shown"
                    
            except Exception as e:
                details = f"Purge dry run response received but JSON parse failed: {e}"
        else:
            details = f"Purge dry run failed: {response.text[:500]}"
            
        self.log_result("POST /api/admin/purge-legacy-users (dry run)", success, response.status_code, details, response_time)
        return success

    def test_step_4_purge_non_dry_run(self):
        """Step 4: Final purge (non-dry run)"""
        print("🗑️ Step 4: Testing POST /api/admin/purge-legacy-users (non-dry run)")
        
        payload = {
            "admin_token": ADMIN_TOKEN,
            "preserve_email": LEGACY_EMAIL,
            "dry_run": False
        }
        
        response, response_time = self.make_request("POST", "/admin/purge-legacy-users", json=payload)
        
        success = response.status_code == 200
        details = ""
        
        if success:
            try:
                data = response.json()
                total_users = data.get("total_legacy_users", 0)
                to_delete_count = data.get("to_delete_count", 0)
                deleted = data.get("deleted", 0)
                preserved = data.get("preserved", "N/A")
                status = data.get("status", "unknown")
                
                details = f"Purge completed - Total legacy users: {total_users}, To delete: {to_delete_count}, Actually deleted: {deleted}, Preserved: {preserved}, Status: {status}"
                    
            except Exception as e:
                details = f"Purge response received but JSON parse failed: {e}"
        else:
            details = f"Purge failed: {response.text[:500]}"
            
        self.log_result("POST /api/admin/purge-legacy-users (non-dry run)", success, response.status_code, details, response_time)
        return success

    def run_all_tests(self):
        """Run all admin operation tests in sequence"""
        print("🔐 Starting Admin Operations Testing")
        print("=" * 70)
        print(f"Admin Token: {ADMIN_TOKEN[:20]}...")
        print(f"Legacy Email: {LEGACY_EMAIL}")
        print("=" * 70)
        print()
        
        test_methods = [
            self.test_step_1_health_check,
            self.test_step_2_migration_non_dry_run,
            self.test_step_3_purge_dry_run,
            self.test_step_4_purge_non_dry_run
        ]
        
        passed = 0
        total = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed += 1
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} crashed: {e}")
                self.log_result(test_method.__name__, False, None, f"Test crashed: {e}")
        
        print("=" * 70)
        print("📊 ADMIN OPERATIONS TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed / total) * 100
        print(f"Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['step']} - {result['status_code']} ({result['response_time_ms']}ms)")
            if result["details"]:
                print(f"    {result['details']}")
        
        print()
        print("=" * 70)
        
        if success_rate >= 80:
            print("🎉 ADMIN OPERATIONS TEST PASSED - All operations working correctly!")
        elif success_rate >= 60:
            print("⚠️ ADMIN OPERATIONS TEST PARTIAL - Some operations need attention")
        else:
            print("🚨 ADMIN OPERATIONS TEST FAILED - Critical issues require immediate fix")
            
        return success_rate

if __name__ == "__main__":
    tester = AdminOperationsTest()
    success_rate = tester.run_all_tests()
    exit(0 if success_rate >= 80 else 1)