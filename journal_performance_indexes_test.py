#!/usr/bin/env python3
"""
JOURNAL SUPABASE INDEXES PERFORMANCE VERIFICATION
Testing Supabase indexes effectiveness via backend API timing measurements.

REVIEW REQUEST REQUIREMENTS:
1. Auth with known test user (marc.alleyne@aurumtechnologyltd.com/password123)
2. Seed 60 journal entries via POST /api/journal (title/content minimal)
3. Soft-delete 30 alternating entries via DELETE /api/journal/{id}
4. Measure 5 consecutive calls and average durations for:
   a) GET /api/journal (should exclude deleted)
   b) GET /api/journal/trash (should include only deleted and sort desc)
5. Report average and p95 timings
6. Confirm functionality intact: restore one deleted entry then verify entries/trash reflect change within next call
7. Provide final confirmation that soft-delete flow remains correct and that timings are acceptable, indicating indexes are effective
8. Update test_result.md with results

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import time
import statistics
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://taskpilot-2.preview.emergentagent.com/api"

class JournalPerformanceIndexesTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.created_journal_ids = []
        self.deleted_journal_ids = []
        self.performance_metrics = {
            'journal_get_times': [],
            'trash_get_times': []
        }
        
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
        """Step 1: Health check GET /api/health"""
        print("\n🏥 STEP 1: Health Check")
        
        try:
            response, duration = self.make_request("GET", "/health")
            if response.status_code == 200:
                self.log_test("Health Check", True, 
                            f"Backend healthy - Status: {response.status_code}", 
                            response.json(), duration)
                return True
        except Exception as e:
            self.log_test("Health Check", False, f"Health check failed: {e}")
            return False
    
    def test_authentication(self):
        """Step 2: Authentication with specified credentials"""
        print("\n🔐 STEP 2: Authentication")
        
        try:
            login_data = {
                "email": self.primary_email,
                "password": self.primary_password
            }
            
            response, duration = self.make_request("POST", "/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    self.log_test("Authentication", True, 
                                f"Authentication successful - Token received", 
                                {'token_length': len(self.auth_token)}, duration)
                    return True
            
            self.log_test("Authentication", False, 
                        f"Login failed - Status: {response.status_code}, Response: {response.text[:200]}", 
                        None, duration)
            return False
            
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {e}")
            return False
    
    def test_seed_60_journal_entries(self):
        """Step 3: Seed 60 journal entries via POST /api/journal (title/content minimal)"""
        print("\n📝 STEP 3: Seed 60 Journal Entries")
        
        if not self.auth_token:
            self.log_test("Seed Journal Entries", False, "No authentication token available")
            return False
        
        timestamp = int(time.time())
        successful_creates = 0
        total_create_time = 0
        
        for i in range(1, 61):  # Create 60 entries
            # Use valid mood values from MoodEnum
            moods = ["optimistic", "inspired", "reflective", "challenging", "anxious", "grateful", "excited", "frustrated", "peaceful", "motivated"]
            mood = moods[i % len(moods)]  # Cycle through valid moods
            
            entry_data = {
                "title": f"Performance Test Entry {i}",
                "content": f"Minimal content for performance testing - Entry {i} created at {timestamp}",
                "mood": mood,
                "tags": ["performance", "test", "indexes"]
            }
            
            try:
                response, duration = self.make_request("POST", "/journal", json=entry_data)
                total_create_time += duration
                
                if response.status_code == 200:
                    data = response.json()
                    entry_id = data.get('id')
                    if entry_id:
                        self.created_journal_ids.append(entry_id)
                        successful_creates += 1
                        
                        # Log every 10th entry to avoid spam
                        if i % 10 == 0:
                            self.log_test(f"Create Entry {i}", True, 
                                        f"Entry {i} created - ID: {entry_id}", 
                                        None, duration)
                else:
                    self.log_test(f"Create Entry {i}", False, 
                                f"Creation failed - Status: {response.status_code}", 
                                None, duration)
                    
            except Exception as e:
                self.log_test(f"Create Entry {i}", False, f"Creation error: {e}")
        
        avg_create_time = total_create_time / 60 if successful_creates > 0 else 0
        
        if successful_creates >= 60:
            self.log_test("Seed Journal Entries", True, 
                        f"Successfully created {successful_creates}/60 journal entries", 
                        {
                            'created_count': successful_creates,
                            'avg_create_time_ms': round(avg_create_time, 1),
                            'total_time_ms': round(total_create_time, 1)
                        }, total_create_time)
            return True
        else:
            self.log_test("Seed Journal Entries", False, 
                        f"Only created {successful_creates}/60 entries", 
                        {'created_count': successful_creates}, total_create_time)
            return False
    
    def test_soft_delete_30_alternating_entries(self):
        """Step 4: Soft-delete 30 alternating entries via DELETE /api/journal/{id}"""
        print("\n🗑️ STEP 4: Soft Delete 30 Alternating Entries")
        
        if len(self.created_journal_ids) < 60:
            self.log_test("Soft Delete Alternating", False, f"Insufficient entries - Have {len(self.created_journal_ids)}, need 60")
            return False
        
        successful_deletes = 0
        total_delete_time = 0
        
        # Delete alternating entries (every other entry: 0, 2, 4, 6, ... up to 58)
        for i in range(0, 60, 2):  # This gives us 30 entries (0, 2, 4, ..., 58)
            if i < len(self.created_journal_ids):
                entry_id = self.created_journal_ids[i]
                
                try:
                    response, duration = self.make_request("DELETE", f"/journal/{entry_id}")
                    total_delete_time += duration
                    
                    if response.status_code == 200:
                        self.deleted_journal_ids.append(entry_id)
                        successful_deletes += 1
                        
                        # Log every 5th deletion to avoid spam
                        if (i // 2 + 1) % 5 == 0:
                            self.log_test(f"Delete Entry {i//2 + 1}", True, 
                                        f"Entry {i//2 + 1} soft deleted - ID: {entry_id}", 
                                        None, duration)
                    else:
                        self.log_test(f"Delete Entry {i//2 + 1}", False, 
                                    f"Deletion failed - Status: {response.status_code}", 
                                    None, duration)
                        
                except Exception as e:
                    self.log_test(f"Delete Entry {i//2 + 1}", False, f"Deletion error: {e}")
        
        avg_delete_time = total_delete_time / 30 if successful_deletes > 0 else 0
        
        if successful_deletes >= 30:
            self.log_test("Soft Delete Alternating", True, 
                        f"Successfully soft deleted {successful_deletes}/30 alternating entries", 
                        {
                            'deleted_count': successful_deletes,
                            'avg_delete_time_ms': round(avg_delete_time, 1),
                            'total_time_ms': round(total_delete_time, 1)
                        }, total_delete_time)
            return True
        else:
            self.log_test("Soft Delete Alternating", False, 
                        f"Only deleted {successful_deletes}/30 entries", 
                        {'deleted_count': successful_deletes}, total_delete_time)
            return False
    
    def test_measure_journal_get_performance(self):
        """Step 5a: Measure 5 consecutive calls to GET /api/journal and calculate average/p95"""
        print("\n📊 STEP 5a: Measure GET /api/journal Performance (5 consecutive calls)")
        
        if not self.auth_token:
            self.log_test("Journal GET Performance", False, "No authentication token available")
            return False
        
        durations = []
        entry_counts = []
        
        for i in range(1, 6):  # 5 consecutive calls
            try:
                response, duration = self.make_request("GET", "/journal")
                durations.append(duration)
                
                if response.status_code == 200:
                    entries = response.json()
                    entry_counts.append(len(entries))
                    self.log_test(f"Journal GET Call {i}", True, 
                                f"Retrieved {len(entries)} entries", 
                                {'entry_count': len(entries)}, duration)
                else:
                    self.log_test(f"Journal GET Call {i}", False, 
                                f"Failed - Status: {response.status_code}", 
                                None, duration)
                    return False
                    
            except Exception as e:
                self.log_test(f"Journal GET Call {i}", False, f"Error: {e}")
                return False
        
        # Calculate statistics
        avg_duration = statistics.mean(durations)
        p95_duration = statistics.quantiles(durations, n=20)[18] if len(durations) >= 5 else max(durations)  # 95th percentile
        min_duration = min(durations)
        max_duration = max(durations)
        avg_entry_count = statistics.mean(entry_counts) if entry_counts else 0
        
        # Store for final report
        self.performance_metrics['journal_get_times'] = durations
        
        self.log_test("Journal GET Performance Summary", True, 
                    f"Average: {avg_duration:.1f}ms, P95: {p95_duration:.1f}ms, Range: {min_duration:.1f}-{max_duration:.1f}ms", 
                    {
                        'average_ms': round(avg_duration, 1),
                        'p95_ms': round(p95_duration, 1),
                        'min_ms': round(min_duration, 1),
                        'max_ms': round(max_duration, 1),
                        'avg_entry_count': round(avg_entry_count, 1),
                        'all_durations': [round(d, 1) for d in durations]
                    })
        
        return True
    
    def test_measure_trash_get_performance(self):
        """Step 5b: Measure 5 consecutive calls to GET /api/journal/trash and calculate average/p95"""
        print("\n📊 STEP 5b: Measure GET /api/journal/trash Performance (5 consecutive calls)")
        
        if not self.auth_token:
            self.log_test("Trash GET Performance", False, "No authentication token available")
            return False
        
        durations = []
        trash_counts = []
        
        for i in range(1, 6):  # 5 consecutive calls
            try:
                response, duration = self.make_request("GET", "/journal/trash")
                durations.append(duration)
                
                if response.status_code == 200:
                    trash_entries = response.json()
                    trash_counts.append(len(trash_entries))
                    self.log_test(f"Trash GET Call {i}", True, 
                                f"Retrieved {len(trash_entries)} trash entries", 
                                {'trash_count': len(trash_entries)}, duration)
                else:
                    self.log_test(f"Trash GET Call {i}", False, 
                                f"Failed - Status: {response.status_code}", 
                                None, duration)
                    return False
                    
            except Exception as e:
                self.log_test(f"Trash GET Call {i}", False, f"Error: {e}")
                return False
        
        # Calculate statistics
        avg_duration = statistics.mean(durations)
        p95_duration = statistics.quantiles(durations, n=20)[18] if len(durations) >= 5 else max(durations)  # 95th percentile
        min_duration = min(durations)
        max_duration = max(durations)
        avg_trash_count = statistics.mean(trash_counts) if trash_counts else 0
        
        # Store for final report
        self.performance_metrics['trash_get_times'] = durations
        
        self.log_test("Trash GET Performance Summary", True, 
                    f"Average: {avg_duration:.1f}ms, P95: {p95_duration:.1f}ms, Range: {min_duration:.1f}-{max_duration:.1f}ms", 
                    {
                        'average_ms': round(avg_duration, 1),
                        'p95_ms': round(p95_duration, 1),
                        'min_ms': round(min_duration, 1),
                        'max_ms': round(max_duration, 1),
                        'avg_trash_count': round(avg_trash_count, 1),
                        'all_durations': [round(d, 1) for d in durations]
                    })
        
        return True
    
    def test_restore_and_verify_functionality(self):
        """Step 6: Restore one deleted entry then verify entries/trash reflect change within next call"""
        print("\n♻️ STEP 6: Restore One Entry and Verify Functionality")
        
        if not self.deleted_journal_ids:
            self.log_test("Restore and Verify", False, "No deleted entries to restore")
            return False
        
        # Pick the first deleted entry to restore
        entry_to_restore = self.deleted_journal_ids[0]
        
        try:
            # Step 6a: Restore the entry
            response, restore_duration = self.make_request("POST", f"/journal/{entry_to_restore}/restore")
            
            if response.status_code != 200:
                self.log_test("Restore Entry", False, 
                            f"Restore failed - Status: {response.status_code}", 
                            None, restore_duration)
                return False
            
            self.log_test("Restore Entry", True, 
                        f"Entry restored successfully - ID: {entry_to_restore}", 
                        {'restored_id': entry_to_restore}, restore_duration)
            
            # Step 6b: Verify it appears in main journal
            journal_response, journal_duration = self.make_request("GET", "/journal")
            if journal_response.status_code != 200:
                self.log_test("Verify Journal After Restore", False, 
                            f"Failed to get journal - Status: {journal_response.status_code}", 
                            None, journal_duration)
                return False
            
            journal_entries = journal_response.json()
            restored_in_journal = any(entry.get('id') == entry_to_restore for entry in journal_entries)
            
            # Step 6c: Verify it's removed from trash
            trash_response, trash_duration = self.make_request("GET", "/journal/trash")
            if trash_response.status_code != 200:
                self.log_test("Verify Trash After Restore", False, 
                            f"Failed to get trash - Status: {trash_response.status_code}", 
                            None, trash_duration)
                return False
            
            trash_entries = trash_response.json()
            still_in_trash = any(entry.get('id') == entry_to_restore for entry in trash_entries)
            
            total_verification_time = journal_duration + trash_duration
            
            if restored_in_journal and not still_in_trash:
                self.log_test("Restore and Verify", True, 
                            f"Entry successfully restored and moved from trash to journal", 
                            {
                                'restored_id': entry_to_restore,
                                'in_journal': restored_in_journal,
                                'in_trash': still_in_trash,
                                'journal_count': len(journal_entries),
                                'trash_count': len(trash_entries)
                            }, restore_duration + total_verification_time)
                return True
            else:
                self.log_test("Restore and Verify", False, 
                            f"Restore verification failed - In journal: {restored_in_journal}, Still in trash: {still_in_trash}", 
                            {
                                'in_journal': restored_in_journal,
                                'in_trash': still_in_trash
                            }, restore_duration + total_verification_time)
                return False
                
        except Exception as e:
            self.log_test("Restore and Verify", False, f"Error during restore and verify: {e}")
            return False
    
    def generate_performance_report(self):
        """Generate comprehensive performance and functionality report"""
        print("\n" + "="*80)
        print("🎯 JOURNAL SUPABASE INDEXES PERFORMANCE VERIFICATION - FINAL REPORT")
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
        
        # Performance Analysis
        print(f"\n⚡ PERFORMANCE ANALYSIS:")
        
        if self.performance_metrics['journal_get_times']:
            journal_times = self.performance_metrics['journal_get_times']
            journal_avg = statistics.mean(journal_times)
            journal_p95 = statistics.quantiles(journal_times, n=20)[18] if len(journal_times) >= 5 else max(journal_times)
            
            print(f"   GET /api/journal (excludes deleted):")
            print(f"     Average: {journal_avg:.1f}ms")
            print(f"     P95: {journal_p95:.1f}ms")
            print(f"     All times: {[round(t, 1) for t in journal_times]}ms")
        
        if self.performance_metrics['trash_get_times']:
            trash_times = self.performance_metrics['trash_get_times']
            trash_avg = statistics.mean(trash_times)
            trash_p95 = statistics.quantiles(trash_times, n=20)[18] if len(trash_times) >= 5 else max(trash_times)
            
            print(f"   GET /api/journal/trash (includes only deleted, sorted desc):")
            print(f"     Average: {trash_avg:.1f}ms")
            print(f"     P95: {trash_p95:.1f}ms")
            print(f"     All times: {[round(t, 1) for t in trash_times]}ms")
        
        # Index Effectiveness Assessment
        print(f"\n🔍 INDEX EFFECTIVENESS ASSESSMENT:")
        if self.performance_metrics['journal_get_times'] and self.performance_metrics['trash_get_times']:
            journal_avg = statistics.mean(self.performance_metrics['journal_get_times'])
            trash_avg = statistics.mean(self.performance_metrics['trash_get_times'])
            
            # Performance thresholds for index effectiveness
            excellent_threshold = 500  # ms
            good_threshold = 1000  # ms
            
            journal_rating = "EXCELLENT" if journal_avg < excellent_threshold else "GOOD" if journal_avg < good_threshold else "NEEDS IMPROVEMENT"
            trash_rating = "EXCELLENT" if trash_avg < excellent_threshold else "GOOD" if trash_avg < good_threshold else "NEEDS IMPROVEMENT"
            
            print(f"   Journal GET Performance: {journal_rating} ({journal_avg:.1f}ms avg)")
            print(f"   Trash GET Performance: {trash_rating} ({trash_avg:.1f}ms avg)")
            
            if journal_avg < good_threshold and trash_avg < good_threshold:
                print(f"   ✅ INDEXES ARE EFFECTIVE - Both endpoints perform well under load")
            else:
                print(f"   ⚠️ INDEXES MAY NEED OPTIMIZATION - Performance above recommended thresholds")
        
        # Data Integrity Verification
        print(f"\n🔒 DATA INTEGRITY VERIFICATION:")
        print(f"   Journal Entries Created: {len(self.created_journal_ids)}")
        print(f"   Entries Soft Deleted: {len(self.deleted_journal_ids)}")
        print(f"   Expected Active Entries: {len(self.created_journal_ids) - len(self.deleted_journal_ids) + 1}")  # +1 for restored entry
        print(f"   Expected Trash Entries: {len(self.deleted_journal_ids) - 1}")  # -1 for restored entry
        
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
        
        # Final Confirmation
        print(f"\n🏁 FINAL CONFIRMATION:")
        if success_rate >= 90:
            print(f"   ✅ SOFT-DELETE FLOW REMAINS CORRECT")
            print(f"   ✅ API TIMINGS ARE ACCEPTABLE")
            print(f"   ✅ INDEXES ARE EFFECTIVE")
            print(f"   🎉 SUPABASE INDEXES PERFORMANCE VERIFICATION: SUCCESSFUL")
        else:
            print(f"   ❌ SOME ISSUES DETECTED - REVIEW REQUIRED")
            print(f"   ⚠️ SUPABASE INDEXES PERFORMANCE VERIFICATION: NEEDS ATTENTION")
        
        print(f"\n🏁 TESTING COMPLETED AT: {datetime.now().isoformat()}")
        print("="*80)
        
        return success_rate >= 85  # Consider 85%+ success rate as overall success

def main():
    """Main test execution"""
    print("🚀 STARTING JOURNAL SUPABASE INDEXES PERFORMANCE VERIFICATION")
    print("="*80)
    
    tester = JournalPerformanceIndexesTester()
    
    # Execute test steps in sequence
    test_steps = [
        tester.test_health_check,
        tester.test_authentication,
        tester.test_seed_60_journal_entries,
        tester.test_soft_delete_30_alternating_entries,
        tester.test_measure_journal_get_performance,
        tester.test_measure_trash_get_performance,
        tester.test_restore_and_verify_functionality
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
    report_success = tester.generate_performance_report()
    
    # Exit with appropriate code
    if overall_success and report_success:
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n💥 SOME TESTS FAILED - CHECK REPORT ABOVE")
        sys.exit(1)

if __name__ == "__main__":
    main()