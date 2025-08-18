#!/usr/bin/env python3
"""
BACKEND JOURNAL SOFT-DELETE WITH SUPABASE STORAGE VERIFICATION
Re-running backend tests for Journal soft-delete now using Supabase storage.

REVIEW REQUEST REQUIREMENTS:
1) Auth (reuse known working flow)
2) Create two journal entries via POST /api/journal
3) GET /api/journal verify both appear (deleted=false)
4) DELETE /api/journal/{id1} verify 200
5) GET /api/journal verify only entry2 appears
6) GET /api/journal/trash verify entry1 appears, has deleted=true and deleted_at set
7) POST /api/journal/{id1}/restore verify it returns to /api/journal and is absent from trash
8) DELETE /api/journal/{id1} then DELETE /api/journal/{id1}/purge verify it disappears from all lists

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import time
import uuid

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://4c39e645-0a34-41d8-8c6a-af773c4a507e.preview.emergentagent.com/api"

class JournalSupabaseBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.created_journal_ids = []
        
        # Test credentials as specified in review request
        self.primary_email = "marc.alleyne@aurumtechnologyltd.com"
        self.primary_password = "password123"
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None, duration_ms: float = 0):
        """Log test results with API duration tracking"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'duration_ms': round(duration_ms, 1),
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        duration_str = f"({duration_ms:.1f}ms)" if duration_ms > 0 else ""
        print(f"{status_icon} {test_name}: {message} {duration_str}")
        
        if data and isinstance(data, dict):
            for key, value in data.items():
                print(f"   {key}: {value}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> tuple:
        """Make HTTP request with timing and error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if we have a token
        if self.auth_token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.auth_token}'
            kwargs['headers'] = headers
        
        start_time = time.time()
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            duration = (time.time() - start_time) * 1000
            return response, duration
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            print(f"❌ Request failed: {method} {endpoint} - {e}")
            raise
    
    def test_health_check(self):
        """Step 1: Health check"""
        print("\n🏥 STEP 1: Health Check")
        
        try:
            response, duration = self.make_request("GET", "/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, 
                            f"Backend accessible - Status: {data.get('status', 'unknown')}", 
                            {'status': data.get('status'), 'timestamp': data.get('timestamp')}, duration)
                return True
            else:
                self.log_test("Health Check", False, 
                            f"Health check failed - Status: {response.status_code}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Health check error: {e}")
            return False
    
    def test_authentication(self):
        """Step 1: Authentication with known working flow"""
        print("\n🔐 STEP 1: Authentication")
        
        login_data = {
            "email": self.primary_email,
            "password": self.primary_password
        }
        
        try:
            response, duration = self.make_request("POST", "/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                
                if self.auth_token:
                    self.log_test("Authentication", True, 
                                f"Login successful - Token type: {data.get('token_type', 'bearer')}", 
                                {'email': self.primary_email, 'token_type': data.get('token_type')}, duration)
                    return True
                else:
                    self.log_test("Authentication", False, "No access token in response", data, duration)
                    return False
            else:
                self.log_test("Authentication", False, 
                            f"Login failed - Status: {response.status_code}, Response: {response.text[:200]}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {e}")
            return False
    
    def test_create_journal_entries(self):
        """Step 2: Create two journal entries via POST /api/journal"""
        print("\n📝 STEP 2: Create Two Journal Entries")
        
        if not self.auth_token:
            self.log_test("Create Journal Entries", False, "No authentication token available")
            return False
        
        # Create unique entries with timestamp
        timestamp = int(time.time())
        
        entry1_data = {
            "title": f"Journal Entry 1 - Supabase Test {timestamp}",
            "content": "This is the first journal entry for testing Supabase soft-delete functionality.",
            "mood": "optimistic",
            "tags": ["test", "supabase", "entry1"]
        }
        
        entry2_data = {
            "title": f"Journal Entry 2 - Supabase Test {timestamp}",
            "content": "This is the second journal entry for testing Supabase soft-delete functionality.",
            "mood": "reflective",
            "tags": ["test", "supabase", "entry2"]
        }
        
        # Create first entry
        success1, id1 = self.create_single_entry(entry1_data, "Entry 1")
        if not success1:
            return False
        
        # Create second entry
        success2, id2 = self.create_single_entry(entry2_data, "Entry 2")
        if not success2:
            return False
        
        self.log_test("Create Journal Entries", True, 
                    f"Both entries created successfully", 
                    {'entry1_id': id1, 'entry2_id': id2, 'total_created': len(self.created_journal_ids)})
        return True
    
    def create_single_entry(self, entry_data: dict, entry_name: str):
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
    
    def test_get_journal_entries_initial(self):
        """Step 3: GET /api/journal verify both appear (deleted=false)"""
        print("\n📖 STEP 3: Get Journal Entries (Verify Both Active)")
        
        if not self.auth_token:
            self.log_test("Get Journal Entries Initial", False, "No authentication token available")
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
                    self.log_test("Get Journal Entries Initial", True, 
                                f"Found {len(active_entries)} active entries out of {len(entries)} total", 
                                {'active_count': len(active_entries), 'total_count': len(entries), 
                                 'found_our_entries': len(found_entries)}, duration)
                    return True
                else:
                    self.log_test("Get Journal Entries Initial", False, 
                                f"Expected 2+ active entries, found {len(active_entries)}", 
                                {'found_entries': len(found_entries), 'active_entries': len(active_entries)}, duration)
                    return False
            else:
                self.log_test("Get Journal Entries Initial", False, 
                            f"Failed to get entries - Status: {response.status_code}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Get Journal Entries Initial", False, f"Error getting entries: {e}")
            return False
    
    def test_soft_delete_entry(self):
        """Step 4: DELETE /api/journal/{id1} verify 200"""
        print("\n🗑️ STEP 4: Soft Delete First Entry")
        
        if not self.created_journal_ids:
            self.log_test("Soft Delete Entry", False, "No journal entries to delete")
            return False
        
        entry_id = self.created_journal_ids[0]
        
        try:
            response, duration = self.make_request("DELETE", f"/journal/{entry_id}")
            
            if response.status_code == 200:
                data = response.json() if response.content else {}
                self.log_test("Soft Delete Entry", True, 
                            f"Entry soft deleted successfully - ID: {entry_id}", 
                            {'deleted_id': entry_id, 'response': data}, duration)
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
        """Step 5: GET /api/journal verify only entry2 appears"""
        print("\n✅ STEP 5: Verify Soft Delete (Only Second Entry Active)")
        
        try:
            response, duration = self.make_request("GET", "/journal")
            
            if response.status_code == 200:
                entries = response.json()
                
                # Find our created entries
                found_entries = []
                for entry in entries:
                    if entry.get('id') in self.created_journal_ids:
                        found_entries.append(entry)
                
                # Verify only second entry is active
                active_entries = [e for e in found_entries if not e.get('deleted', False)]
                
                if len(active_entries) == 1:
                    active_entry = active_entries[0]
                    expected_second_id = self.created_journal_ids[1] if len(self.created_journal_ids) > 1 else None
                    
                    if active_entry.get('id') == expected_second_id:
                        self.log_test("Verify Soft Delete", True, 
                                    f"Only second entry remains active as expected", 
                                    {'active_entry_id': active_entry.get('id'), 
                                     'total_found': len(found_entries)}, duration)
                        return True
                    else:
                        self.log_test("Verify Soft Delete", False, 
                                    f"Wrong entry is active - Expected: {expected_second_id}, Found: {active_entry.get('id')}", 
                                    {'active_entries': [e.get('id') for e in active_entries]}, duration)
                        return False
                else:
                    self.log_test("Verify Soft Delete", False, 
                                f"Expected 1 active entry, found {len(active_entries)}", 
                                {'active_count': len(active_entries), 'found_count': len(found_entries)}, duration)
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
        """Step 6: GET /api/journal/trash verify entry1 appears, has deleted=true and deleted_at set"""
        print("\n🗂️ STEP 6: Get Trash Entries (Verify First Entry in Trash)")
        
        try:
            response, duration = self.make_request("GET", "/journal/trash")
            
            if response.status_code == 200:
                trash_entries = response.json()
                
                # Find our deleted entry
                deleted_entry_id = self.created_journal_ids[0] if self.created_journal_ids else None
                found_deleted_entry = None
                
                for entry in trash_entries:
                    if entry.get('id') == deleted_entry_id:
                        found_deleted_entry = entry
                        break
                
                if found_deleted_entry:
                    # Verify entry has deleted=true and deleted_at set
                    is_deleted = found_deleted_entry.get('deleted', False)
                    deleted_at = found_deleted_entry.get('deleted_at')
                    
                    if is_deleted and deleted_at:
                        self.log_test("Get Trash Entries", True, 
                                    f"Deleted entry found in trash with proper flags", 
                                    {'deleted_entry_id': deleted_entry_id, 
                                     'deleted': is_deleted, 
                                     'deleted_at': deleted_at,
                                     'total_trash_entries': len(trash_entries)}, duration)
                        return True
                    else:
                        self.log_test("Get Trash Entries", False, 
                                    f"Entry found but missing proper deletion flags - deleted: {is_deleted}, deleted_at: {deleted_at}", 
                                    {'entry_data': found_deleted_entry}, duration)
                        return False
                else:
                    self.log_test("Get Trash Entries", False, 
                                f"Deleted entry not found in trash - Expected ID: {deleted_entry_id}", 
                                {'trash_entry_ids': [e.get('id') for e in trash_entries]}, duration)
                    return False
            else:
                self.log_test("Get Trash Entries", False, 
                            f"Failed to get trash entries - Status: {response.status_code}, Response: {response.text[:200]}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Get Trash Entries", False, f"Error getting trash entries: {e}")
            return False
    
    def test_restore_entry(self):
        """Step 7: POST /api/journal/{id1}/restore verify it returns to /api/journal and is absent from trash"""
        print("\n♻️ STEP 7: Restore Entry")
        
        if not self.created_journal_ids:
            self.log_test("Restore Entry", False, "No journal entries to restore")
            return False
        
        entry_id = self.created_journal_ids[0]
        
        try:
            # Restore the entry
            response, duration = self.make_request("POST", f"/journal/{entry_id}/restore")
            
            if response.status_code == 200:
                data = response.json() if response.content else {}
                self.log_test("Restore Entry API", True, 
                            f"Entry restore API successful - ID: {entry_id}", 
                            {'restored_id': entry_id, 'response': data}, duration)
                
                # Verify entry is back in main journal list
                time.sleep(0.5)  # Brief pause for consistency
                journal_response, journal_duration = self.make_request("GET", "/journal")
                
                if journal_response.status_code == 200:
                    entries = journal_response.json()
                    restored_entry = None
                    
                    for entry in entries:
                        if entry.get('id') == entry_id:
                            restored_entry = entry
                            break
                    
                    if restored_entry and not restored_entry.get('deleted', False):
                        # Verify entry is absent from trash
                        trash_response, trash_duration = self.make_request("GET", "/journal/trash")
                        
                        if trash_response.status_code == 200:
                            trash_entries = trash_response.json()
                            in_trash = any(e.get('id') == entry_id for e in trash_entries)
                            
                            if not in_trash:
                                self.log_test("Restore Entry", True, 
                                            f"Entry successfully restored and removed from trash", 
                                            {'restored_id': entry_id, 'in_journal': True, 'in_trash': False}, 
                                            duration + journal_duration + trash_duration)
                                return True
                            else:
                                self.log_test("Restore Entry", False, 
                                            f"Entry restored but still appears in trash", 
                                            {'restored_id': entry_id}, duration)
                                return False
                        else:
                            self.log_test("Restore Entry", False, 
                                        f"Could not verify trash status - Status: {trash_response.status_code}", 
                                        None, duration)
                            return False
                    else:
                        self.log_test("Restore Entry", False, 
                                    f"Entry not found in main journal after restore", 
                                    {'entry_id': entry_id}, duration)
                        return False
                else:
                    self.log_test("Restore Entry", False, 
                                f"Could not verify journal after restore - Status: {journal_response.status_code}", 
                                None, duration)
                    return False
            else:
                self.log_test("Restore Entry", False, 
                            f"Restore failed - Status: {response.status_code}, Response: {response.text[:200]}", 
                            None, duration)
                return False
                
        except Exception as e:
            self.log_test("Restore Entry", False, f"Restore error: {e}")
            return False
    
    def test_permanent_delete(self):
        """Step 8: DELETE /api/journal/{id1} then DELETE /api/journal/{id1}/purge verify it disappears from all lists"""
        print("\n💀 STEP 8: Permanent Delete (Soft Delete + Purge)")
        
        if not self.created_journal_ids:
            self.log_test("Permanent Delete", False, "No journal entries to permanently delete")
            return False
        
        entry_id = self.created_journal_ids[0]
        
        try:
            # First, soft delete the entry again
            soft_delete_response, soft_delete_duration = self.make_request("DELETE", f"/journal/{entry_id}")
            
            if soft_delete_response.status_code == 200:
                self.log_test("Permanent Delete - Soft Delete", True, 
                            f"Entry soft deleted again - ID: {entry_id}", 
                            {'deleted_id': entry_id}, soft_delete_duration)
                
                # Brief pause for consistency
                time.sleep(0.5)
                
                # Now purge the entry permanently
                purge_response, purge_duration = self.make_request("DELETE", f"/journal/{entry_id}/purge")
                
                if purge_response.status_code == 200:
                    data = purge_response.json() if purge_response.content else {}
                    self.log_test("Permanent Delete - Purge", True, 
                                f"Entry purged successfully - ID: {entry_id}", 
                                {'purged_id': entry_id, 'response': data}, purge_duration)
                    
                    # Verify entry is gone from both journal and trash
                    time.sleep(0.5)  # Brief pause for consistency
                    
                    # Check main journal
                    journal_response, journal_duration = self.make_request("GET", "/journal")
                    in_journal = False
                    
                    if journal_response.status_code == 200:
                        entries = journal_response.json()
                        in_journal = any(e.get('id') == entry_id for e in entries)
                    
                    # Check trash
                    trash_response, trash_duration = self.make_request("GET", "/journal/trash")
                    in_trash = False
                    
                    if trash_response.status_code == 200:
                        trash_entries = trash_response.json()
                        in_trash = any(e.get('id') == entry_id for e in trash_entries)
                    
                    if not in_journal and not in_trash:
                        self.log_test("Permanent Delete", True, 
                                    f"Entry completely removed from all lists", 
                                    {'purged_id': entry_id, 'in_journal': False, 'in_trash': False}, 
                                    soft_delete_duration + purge_duration + journal_duration + trash_duration)
                        return True
                    else:
                        self.log_test("Permanent Delete", False, 
                                    f"Entry still found after purge - In journal: {in_journal}, In trash: {in_trash}", 
                                    {'purged_id': entry_id}, soft_delete_duration + purge_duration)
                        return False
                else:
                    self.log_test("Permanent Delete - Purge", False, 
                                f"Purge failed - Status: {purge_response.status_code}, Response: {purge_response.text[:200]}", 
                                None, purge_duration)
                    return False
            else:
                self.log_test("Permanent Delete - Soft Delete", False, 
                            f"Soft delete failed - Status: {soft_delete_response.status_code}", 
                            None, soft_delete_duration)
                return False
                
        except Exception as e:
            self.log_test("Permanent Delete", False, f"Permanent delete error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all journal soft-delete tests in sequence"""
        print("🚀 JOURNAL SUPABASE BACKEND TESTING STARTED")
        print("=" * 60)
        
        test_sequence = [
            ("Health Check", self.test_health_check),
            ("Authentication", self.test_authentication),
            ("Create Journal Entries", self.test_create_journal_entries),
            ("Get Journal Entries Initial", self.test_get_journal_entries_initial),
            ("Soft Delete Entry", self.test_soft_delete_entry),
            ("Verify Soft Delete", self.test_verify_soft_delete),
            ("Get Trash Entries", self.test_get_trash_entries),
            ("Restore Entry", self.test_restore_entry),
            ("Permanent Delete", self.test_permanent_delete)
        ]
        
        passed_tests = 0
        total_tests = len(test_sequence)
        
        for test_name, test_func in test_sequence:
            try:
                success = test_func()
                if success:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 JOURNAL SUPABASE BACKEND TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Print detailed results
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = f"({result['duration_ms']:.1f}ms)" if result['duration_ms'] > 0 else ""
            print(f"{status} {result['test']}: {result['message']} {duration}")
        
        # Calculate average response time
        durations = [r['duration_ms'] for r in self.test_results if r['duration_ms'] > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        print(f"\nPerformance Metrics:")
        print(f"- Average API Response Time: {avg_duration:.1f}ms")
        print(f"- Total Test Duration: {sum(durations):.1f}ms")
        print(f"- Created Journal IDs: {self.created_journal_ids}")
        
        return success_rate >= 80  # Consider 80%+ as success

def main():
    """Main test execution"""
    tester = JournalSupabaseBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 JOURNAL SUPABASE BACKEND TESTS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n🚨 JOURNAL SUPABASE BACKEND TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()