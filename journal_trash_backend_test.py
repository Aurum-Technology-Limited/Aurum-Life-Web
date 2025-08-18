#!/usr/bin/env python3
"""
BACKEND JOURNAL CRUD WITH TRASH FLOW VERIFICATION
Testing comprehensive Journal CRUD operations with soft delete, restore, and purge functionality.

REVIEW REQUEST REQUIREMENTS:
1. Health check GET /api/health or root
2. Authentication with marc.alleyne@aurumtechnologyltd.com/password123 (or fallback methods)
3. Create two journal entries via POST /api/journal
4. GET /api/journal and assert both appear with deleted=false
5. DELETE /api/journal/{id1} to soft delete first entry
6. GET /api/journal and confirm only second entry remains
7. GET /api/journal/trash and verify first entry appears with deleted=true
8. POST /api/journal/{id1}/restore and verify restoration
9. DELETE /api/journal/{id1} then DELETE /api/journal/{id1}/purge for permanent deletion
10. Report all API durations, statuses, and errors

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://productivity-hub-23.preview.emergentagent.com/api"

class JournalTrashFlowTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.created_journal_ids = []
        
        # Test credentials as specified in review request
        self.primary_email = "marc.alleyne@aurumtechnologyltd.com"
        self.primary_password = "password123"
        self.fallback_password = "password"
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None, duration_ms: float = 0):
        """Log test results with API duration tracking"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'duration_ms': round(duration_ms, 1),
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        duration_info = f" ({duration_ms:.1f}ms)" if duration_ms > 0 else ""
        print(f"{status} {test_name}{duration_info}: {message}")
        
    def make_request(self, method: str, endpoint: str, **kwargs) -> tuple[requests.Response, float]:
        """Make HTTP request and track duration"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            return response, duration_ms
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            print(f"Request error for {method} {endpoint}: {e}")
            raise
    
    def test_health_check(self):
        """Step 1: Health check GET /api/health or root"""
        print("\n🏥 STEP 1: Health Check")
        
        # Try /api/health first
        try:
            response, duration = self.make_request("GET", "/health")
            if response.status_code == 200:
                self.log_test("Health Check (/api/health)", True, 
                            f"Backend healthy - Status: {response.status_code}", 
                            response.json(), duration)
                return True
        except Exception as e:
            print(f"Health check failed: {e}")
        
        # Fallback to root endpoint
        try:
            response, duration = self.make_request("GET", "/")
            if response.status_code == 200:
                self.log_test("Health Check (root)", True, 
                            f"Backend accessible - Status: {response.status_code}", 
                            response.json(), duration)
                return True
        except Exception as e:
            self.log_test("Health Check", False, f"Both health endpoints failed: {e}")
            return False
    
    def test_authentication(self):
        """Step 2: Authentication with hybrid approach"""
        print("\n🔐 STEP 2: Authentication")
        
        # Try primary credentials first
        success = self._try_login(self.primary_email, self.primary_password)
        if success:
            return True
            
        # Try fallback password
        success = self._try_login(self.primary_email, self.fallback_password)
        if success:
            return True
            
        # Try Google OAuth initiate (if available)
        try:
            response, duration = self.make_request("GET", "/auth/google/initiate")
            if response.status_code in [200, 302]:
                self.log_test("Google OAuth Initiate", True, 
                            f"Google OAuth available - Status: {response.status_code}", 
                            None, duration)
                # For testing purposes, we'll skip actual Google OAuth
                print("⚠️  Google OAuth available but skipping for automated testing")
        except Exception:
            pass
            
        self.log_test("Authentication", False, "All authentication methods failed")
        return False
    
    def _try_login(self, email: str, password: str) -> bool:
        """Try login with specific credentials"""
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            response, duration = self.make_request("POST", "/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    self.log_test(f"Login ({email})", True, 
                                f"Authentication successful - Token received", 
                                {'token_length': len(self.auth_token)}, duration)
                    return True
            
            self.log_test(f"Login ({email})", False, 
                        f"Login failed - Status: {response.status_code}, Response: {response.text[:200]}", 
                        None, duration)
            return False
            
        except Exception as e:
            self.log_test(f"Login ({email})", False, f"Login error: {e}")
            return False
    
    def test_create_journal_entries(self):
        """Step 3: Create two journal entries via POST /api/journal"""
        print("\n📝 STEP 3: Create Journal Entries")
        
        if not self.auth_token:
            self.log_test("Create Journal Entries", False, "No authentication token available")
            return False
        
        # Create first journal entry
        entry1_data = {
            "title": f"E2E Journal Entry 1 - {int(time.time())}",
            "content": "This is the first test journal entry for E2E testing of trash flow functionality.",
            "mood": "reflective",
            "tags": ["test", "e2e"]
        }
        
        success1, id1 = self._create_journal_entry(entry1_data, "Entry 1")
        
        # Create second journal entry
        entry2_data = {
            "title": f"E2E Journal Entry 2 - {int(time.time())}",
            "content": "This is the second test journal entry for E2E testing of trash flow functionality.",
            "mood": "reflective", 
            "tags": ["test", "e2e"]
        }
        
        success2, id2 = self._create_journal_entry(entry2_data, "Entry 2")
        
        if success1 and success2:
            self.log_test("Create Journal Entries", True, 
                        f"Both journal entries created successfully - IDs: {id1}, {id2}")
            return True
        else:
            self.log_test("Create Journal Entries", False, 
                        f"Failed to create entries - Success: {success1}, {success2}")
            return False
    
    def _create_journal_entry(self, entry_data: dict, entry_name: str) -> tuple[bool, Optional[str]]:
        """Create a single journal entry"""
        try:
            response, duration = self.make_request("POST", "/journal", json=entry_data)
            
            if response.status_code == 200:
                data = response.json()
                entry_id = data.get('id')
                if entry_id:
                    self.created_journal_ids.append(entry_id)
                    self.log_test(f"Create Journal {entry_name}", True, 
                                f"Entry created - ID: {entry_id}", 
                                {'title': entry_data['title']}, duration)
                    return True, entry_id
            
            self.log_test(f"Create Journal {entry_name}", False, 
                        f"Creation failed - Status: {response.status_code}, Response: {response.text[:200]}", 
                        None, duration)
            return False, None
            
        except Exception as e:
            self.log_test(f"Create Journal {entry_name}", False, f"Creation error: {e}")
            return False, None
    
    def test_get_journal_entries(self):
        """Step 4: GET /api/journal and assert both appear with deleted=false"""
        print("\n📖 STEP 4: Get Journal Entries (Both Active)")
        
        if not self.auth_token:
            self.log_test("Get Journal Entries", False, "No authentication token available")
            return False
        
        try:
            response, duration = self.make_request("GET", "/journal")
            
            if response.status_code == 200:
                entries = response.json()
                
                # Find our created entries
                found_entries = []
                for entry in entries:
                    if entry.get('id') in self.created_journal_ids:
                        found_entries.append(entry)
                
                # Verify both entries are present and not deleted
                active_entries = [e for e in found_entries if not e.get('deleted', False)]
                
                if len(active_entries) >= 2:
                    self.log_test("Get Journal Entries", True, 
                                f"Found {len(active_entries)} active entries out of {len(entries)} total", 
                                {'active_count': len(active_entries), 'total_count': len(entries)}, duration)
                    return True
                else:
                    self.log_test("Get Journal Entries", False, 
                                f"Expected 2+ active entries, found {len(active_entries)}", 
                                {'found_entries': len(found_entries)}, duration)
                    return False
            else:
                self.log_test("Get Journal Entries", False, 
                            f"Failed to get entries - Status: {response.status_code}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Get Journal Entries", False, f"Error getting entries: {e}")
            return False
    
    def test_soft_delete_entry(self):
        """Step 5: DELETE /api/journal/{id1} to soft delete first entry"""
        print("\n🗑️ STEP 5: Soft Delete First Entry")
        
        if not self.created_journal_ids:
            self.log_test("Soft Delete Entry", False, "No journal entries to delete")
            return False
        
        entry_id = self.created_journal_ids[0]
        
        try:
            response, duration = self.make_request("DELETE", f"/journal/{entry_id}")
            
            if response.status_code == 200:
                self.log_test("Soft Delete Entry", True, 
                            f"Entry soft deleted successfully - ID: {entry_id}", 
                            {'deleted_id': entry_id}, duration)
                return True
            else:
                self.log_test("Soft Delete Entry", False, 
                            f"Soft delete failed - Status: {response.status_code}, Response: {response.text[:200]}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Soft Delete Entry", False, f"Soft delete error: {e}")
            return False
    
    def test_verify_soft_delete(self):
        """Step 6: GET /api/journal and confirm only second entry remains"""
        print("\n✅ STEP 6: Verify Soft Delete (Only Second Entry Active)")
        
        try:
            response, duration = self.make_request("GET", "/journal")
            
            if response.status_code == 200:
                entries = response.json()
                
                # Find our created entries that are still active
                active_created_entries = []
                for entry in entries:
                    if entry.get('id') in self.created_journal_ids and not entry.get('deleted', False):
                        active_created_entries.append(entry)
                
                if len(active_created_entries) == 1:
                    remaining_id = active_created_entries[0]['id']
                    expected_remaining = self.created_journal_ids[1] if len(self.created_journal_ids) > 1 else None
                    
                    if remaining_id == expected_remaining:
                        self.log_test("Verify Soft Delete", True, 
                                    f"Correct entry remains active - ID: {remaining_id}", 
                                    {'remaining_id': remaining_id}, duration)
                        return True
                    else:
                        self.log_test("Verify Soft Delete", False, 
                                    f"Wrong entry remains - Expected: {expected_remaining}, Found: {remaining_id}", 
                                    None, duration)
                        return False
                else:
                    self.log_test("Verify Soft Delete", False, 
                                f"Expected 1 active entry, found {len(active_created_entries)}", 
                                {'active_count': len(active_created_entries)}, duration)
                    return False
            else:
                self.log_test("Verify Soft Delete", False, 
                            f"Failed to get entries - Status: {response.status_code}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Verify Soft Delete", False, f"Error verifying soft delete: {e}")
            return False
    
    def test_get_trash_entries(self):
        """Step 7: GET /api/journal/trash and verify first entry appears with deleted=true"""
        print("\n🗂️ STEP 7: Get Trash Entries")
        
        try:
            response, duration = self.make_request("GET", "/journal/trash")
            
            if response.status_code == 200:
                trash_entries = response.json()
                
                # Find our deleted entry in trash
                deleted_entry = None
                for entry in trash_entries:
                    if entry.get('id') == self.created_journal_ids[0]:
                        deleted_entry = entry
                        break
                
                if deleted_entry:
                    # Verify it's marked as deleted and has deleted_at timestamp
                    is_deleted = deleted_entry.get('deleted', False)
                    has_deleted_at = 'deleted_at' in deleted_entry and deleted_entry['deleted_at'] is not None
                    
                    if is_deleted and has_deleted_at:
                        self.log_test("Get Trash Entries", True, 
                                    f"Deleted entry found in trash with proper metadata - ID: {deleted_entry['id']}", 
                                    {
                                        'deleted': is_deleted, 
                                        'deleted_at': deleted_entry.get('deleted_at'),
                                        'trash_count': len(trash_entries)
                                    }, duration)
                        return True
                    else:
                        self.log_test("Get Trash Entries", False, 
                                    f"Entry found but missing deletion metadata - deleted: {is_deleted}, deleted_at: {has_deleted_at}", 
                                    None, duration)
                        return False
                else:
                    self.log_test("Get Trash Entries", False, 
                                f"Deleted entry not found in trash - Expected ID: {self.created_journal_ids[0]}", 
                                {'trash_entries': len(trash_entries)}, duration)
                    return False
            else:
                self.log_test("Get Trash Entries", False, 
                            f"Failed to get trash - Status: {response.status_code}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Get Trash Entries", False, f"Error getting trash: {e}")
            return False
    
    def test_restore_entry(self):
        """Step 8: POST /api/journal/{id1}/restore and verify restoration"""
        print("\n♻️ STEP 8: Restore Deleted Entry")
        
        if not self.created_journal_ids:
            self.log_test("Restore Entry", False, "No journal entries to restore")
            return False
        
        entry_id = self.created_journal_ids[0]
        
        try:
            response, duration = self.make_request("POST", f"/journal/{entry_id}/restore")
            
            if response.status_code == 200:
                self.log_test("Restore Entry", True, 
                            f"Entry restored successfully - ID: {entry_id}", 
                            {'restored_id': entry_id}, duration)
                
                # Verify restoration by checking it appears in main journal list
                return self._verify_restoration(entry_id)
            else:
                self.log_test("Restore Entry", False, 
                            f"Restore failed - Status: {response.status_code}, Response: {response.text[:200]}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Restore Entry", False, f"Restore error: {e}")
            return False
    
    def _verify_restoration(self, entry_id: str) -> bool:
        """Verify entry appears in main journal and is absent from trash"""
        try:
            # Check main journal
            response, duration = self.make_request("GET", "/journal")
            if response.status_code == 200:
                entries = response.json()
                restored_entry = next((e for e in entries if e.get('id') == entry_id), None)
                
                if restored_entry and not restored_entry.get('deleted', False):
                    # Check trash to ensure it's no longer there
                    trash_response, trash_duration = self.make_request("GET", "/journal/trash")
                    if trash_response.status_code == 200:
                        trash_entries = trash_response.json()
                        in_trash = any(e.get('id') == entry_id for e in trash_entries)
                        
                        if not in_trash:
                            self.log_test("Verify Restoration", True, 
                                        f"Entry successfully restored and removed from trash", 
                                        {'restored_id': entry_id}, duration + trash_duration)
                            return True
                        else:
                            self.log_test("Verify Restoration", False, 
                                        f"Entry restored but still in trash", 
                                        None, duration + trash_duration)
                            return False
                else:
                    self.log_test("Verify Restoration", False, 
                                f"Entry not found in main journal after restore", 
                                None, duration)
                    return False
            else:
                self.log_test("Verify Restoration", False, 
                            f"Failed to verify restoration - Status: {response.status_code}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Verify Restoration", False, f"Error verifying restoration: {e}")
            return False
    
    def test_permanent_deletion(self):
        """Step 9: DELETE /api/journal/{id1} then DELETE /api/journal/{id1}/purge"""
        print("\n💀 STEP 9: Permanent Deletion")
        
        if not self.created_journal_ids:
            self.log_test("Permanent Deletion", False, "No journal entries for permanent deletion")
            return False
        
        entry_id = self.created_journal_ids[0]
        
        # First soft delete again
        try:
            response, duration1 = self.make_request("DELETE", f"/journal/{entry_id}")
            if response.status_code != 200:
                self.log_test("Permanent Deletion (Soft Delete)", False, 
                            f"Soft delete failed - Status: {response.status_code}", 
                            None, duration1)
                return False
            
            self.log_test("Permanent Deletion (Soft Delete)", True, 
                        f"Entry soft deleted again - ID: {entry_id}", 
                        None, duration1)
            
            # Now purge permanently
            response, duration2 = self.make_request("DELETE", f"/journal/{entry_id}/purge")
            
            if response.status_code == 200:
                self.log_test("Permanent Deletion (Purge)", True, 
                            f"Entry permanently deleted - ID: {entry_id}", 
                            {'purged_id': entry_id}, duration2)
                
                # Verify it's not in journal or trash
                return self._verify_permanent_deletion(entry_id, duration1 + duration2)
            else:
                self.log_test("Permanent Deletion (Purge)", False, 
                            f"Purge failed - Status: {response.status_code}, Response: {response.text[:200]}", 
                            None, duration2)
                return False
                
        except Exception as e:
            self.log_test("Permanent Deletion", False, f"Permanent deletion error: {e}")
            return False
    
    def _verify_permanent_deletion(self, entry_id: str, previous_duration: float) -> bool:
        """Verify entry is not present in journal nor trash"""
        try:
            # Check main journal
            response, duration1 = self.make_request("GET", "/journal")
            in_journal = False
            if response.status_code == 200:
                entries = response.json()
                in_journal = any(e.get('id') == entry_id for e in entries)
            
            # Check trash
            trash_response, duration2 = self.make_request("GET", "/journal/trash")
            in_trash = False
            if trash_response.status_code == 200:
                trash_entries = trash_response.json()
                in_trash = any(e.get('id') == entry_id for e in trash_entries)
            
            total_duration = previous_duration + duration1 + duration2
            
            if not in_journal and not in_trash:
                self.log_test("Verify Permanent Deletion", True, 
                            f"Entry completely removed from journal and trash", 
                            {'purged_id': entry_id}, total_duration)
                return True
            else:
                self.log_test("Verify Permanent Deletion", False, 
                            f"Entry still exists - In journal: {in_journal}, In trash: {in_trash}", 
                            None, total_duration)
                return False
                
        except Exception as e:
            self.log_test("Verify Permanent Deletion", False, f"Error verifying permanent deletion: {e}")
            return False
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("🎯 BACKEND JOURNAL CRUD WITH TRASH FLOW VERIFICATION - FINAL REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # API Performance Summary
        durations = [r['duration_ms'] for r in self.test_results if r['duration_ms'] > 0]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            print(f"\n⚡ API PERFORMANCE:")
            print(f"   Average Response Time: {avg_duration:.1f}ms")
            print(f"   Fastest Response: {min_duration:.1f}ms")
            print(f"   Slowest Response: {max_duration:.1f}ms")
        
        # Detailed Results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration_info = f" ({result['duration_ms']:.1f}ms)" if result['duration_ms'] > 0 else ""
            print(f"   {i:2d}. {status} {result['test']}{duration_info}")
            if result['message']:
                print(f"       {result['message']}")
        
        # Critical Issues
        critical_failures = [r for r in self.test_results if not r['success']]
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES:")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['message']}")
        
        # Journal IDs Created
        if self.created_journal_ids:
            print(f"\n📝 JOURNAL ENTRIES CREATED:")
            for i, entry_id in enumerate(self.created_journal_ids, 1):
                print(f"   {i}. {entry_id}")
        
        print(f"\n🏁 TESTING COMPLETED AT: {datetime.now().isoformat()}")
        print("="*80)
        
        return success_rate >= 80  # Consider 80%+ success rate as overall success

def main():
    """Main test execution"""
    print("🚀 STARTING BACKEND JOURNAL CRUD WITH TRASH FLOW VERIFICATION")
    print("="*80)
    
    tester = JournalTrashFlowTester()
    
    # Execute test steps in sequence
    test_steps = [
        tester.test_health_check,
        tester.test_authentication,
        tester.test_create_journal_entries,
        tester.test_get_journal_entries,
        tester.test_soft_delete_entry,
        tester.test_verify_soft_delete,
        tester.test_get_trash_entries,
        tester.test_restore_entry,
        tester.test_permanent_deletion
    ]
    
    overall_success = True
    for step in test_steps:
        try:
            success = step()
            if not success:
                overall_success = False
                # Continue with remaining tests even if one fails
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {step.__name__}: {e}")
            overall_success = False
    
    # Generate final report
    report_success = tester.generate_report()
    
    # Exit with appropriate code
    if overall_success and report_success:
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n💥 SOME TESTS FAILED - CHECK REPORT ABOVE")
        sys.exit(1)

if __name__ == "__main__":
    main()