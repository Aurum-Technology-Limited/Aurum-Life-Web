#!/usr/bin/env python3
"""
Streak Endpoints Testing Script
Tests the new streak endpoints as requested in review:
1) Authenticate with marc.alleyne@aurumtechnologyltd.com/password123
2) POST /api/streaks/login with timezone header
3) GET /api/streaks/stats 
4) GET /api/streaks/month for current year/month
5) Retry POST /api/streaks/login to verify idempotency
"""

import requests
import json
from datetime import datetime
import os
import sys

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://hierarchy-enforcer.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_streak_endpoints():
    """Test streak endpoints flow as specified in review request"""
    print("🧪 STREAK ENDPOINTS TESTING STARTED")
    print("=" * 60)
    
    results = {
        'authentication': False,
        'first_login_streak': False,
        'stats_verification': False,
        'month_verification': False,
        'idempotency_check': False,
        'errors': []
    }
    
    try:
        # Step 1: Authenticate with specified credentials
        print("📋 Step 1: Authentication with marc.alleyne@aurumtechnologyltd.com/password123")
        auth_data = {
            "email": "marc.alleyne@aurumtechnologyltd.com",
            "password": "password123"
        }
        
        auth_response = requests.post(f"{API_BASE}/auth/login", json=auth_data, timeout=10)
        print(f"   Auth Status: {auth_response.status_code}")
        
        if auth_response.status_code != 200:
            results['errors'].append(f"Authentication failed: {auth_response.status_code} - {auth_response.text}")
            return results
            
        auth_json = auth_response.json()
        access_token = auth_json.get('access_token')
        
        if not access_token:
            results['errors'].append("No access_token in auth response")
            return results
            
        print(f"   ✅ Authentication successful, token obtained")
        results['authentication'] = True
        
        # Set up headers with Bearer token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Step 2: POST /api/streaks/login with timezone header
        print("\n📋 Step 2: POST /api/streaks/login with X-Client-Timezone header")
        streak_headers = headers.copy()
        streak_headers['X-Client-Timezone'] = 'America/New_York'
        
        login_streak_response = requests.post(f"{API_BASE}/streaks/login", headers=streak_headers, timeout=10)
        print(f"   Login Streak Status: {login_streak_response.status_code}")
        
        if login_streak_response.status_code != 200:
            results['errors'].append(f"Login streak failed: {login_streak_response.status_code} - {login_streak_response.text}")
            return results
            
        login_streak_json = login_streak_response.json()
        print(f"   Response: {json.dumps(login_streak_json, indent=2)}")
        
        # Verify response has required fields and values >= 1
        current_streak_1 = login_streak_json.get('current_streak', 0)
        best_streak_1 = login_streak_json.get('best_streak', 0)
        
        if current_streak_1 >= 1 and best_streak_1 >= 1:
            print(f"   ✅ Login streak successful: current={current_streak_1}, best={best_streak_1}")
            results['first_login_streak'] = True
        else:
            results['errors'].append(f"Streak values not >= 1: current={current_streak_1}, best={best_streak_1}")
            return results
        
        # Step 3: GET /api/streaks/stats and verify same or higher values
        print("\n📋 Step 3: GET /api/streaks/stats verification")
        stats_response = requests.get(f"{API_BASE}/streaks/stats", headers=headers, timeout=10)
        print(f"   Stats Status: {stats_response.status_code}")
        
        if stats_response.status_code != 200:
            results['errors'].append(f"Stats request failed: {stats_response.status_code} - {stats_response.text}")
            return results
            
        stats_json = stats_response.json()
        print(f"   Stats Response: {json.dumps(stats_json, indent=2)}")
        
        current_streak_stats = stats_json.get('current_streak', 0)
        best_streak_stats = stats_json.get('best_streak', 0)
        
        if current_streak_stats >= current_streak_1 and best_streak_stats >= best_streak_1:
            print(f"   ✅ Stats verification successful: current={current_streak_stats}, best={best_streak_stats}")
            results['stats_verification'] = True
        else:
            results['errors'].append(f"Stats values lower than login: stats current={current_streak_stats} vs login={current_streak_1}, stats best={best_streak_stats} vs login={best_streak_1}")
            return results
        
        # Step 4: GET /api/streaks/month for current year/month
        print("\n📋 Step 4: GET /api/streaks/month for current year/month")
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day
        
        month_response = requests.get(f"{API_BASE}/streaks/month?year={current_year}&month={current_month}", headers=headers, timeout=10)
        print(f"   Month Status: {month_response.status_code}")
        
        if month_response.status_code != 200:
            results['errors'].append(f"Month request failed: {month_response.status_code} - {month_response.text}")
            return results
            
        month_json = month_response.json()
        print(f"   Month Response: {json.dumps(month_json, indent=2)}")
        
        days_list = month_json.get('days', [])
        
        if current_day in days_list:
            print(f"   ✅ Month verification successful: today's day {current_day} found in days list {days_list}")
            results['month_verification'] = True
        else:
            results['errors'].append(f"Today's day {current_day} not found in month days list: {days_list}")
            return results
        
        # Step 5: Retry POST /api/streaks/login to verify idempotency
        print("\n📋 Step 5: Retry POST /api/streaks/login for idempotency check")
        login_streak_response_2 = requests.post(f"{API_BASE}/streaks/login", headers=streak_headers, timeout=10)
        print(f"   Second Login Streak Status: {login_streak_response_2.status_code}")
        
        if login_streak_response_2.status_code != 200:
            results['errors'].append(f"Second login streak failed: {login_streak_response_2.status_code} - {login_streak_response_2.text}")
            return results
            
        login_streak_json_2 = login_streak_response_2.json()
        print(f"   Second Response: {json.dumps(login_streak_json_2, indent=2)}")
        
        current_streak_2 = login_streak_json_2.get('current_streak', 0)
        best_streak_2 = login_streak_json_2.get('best_streak', 0)
        
        # Verify stats remain the same (idempotent)
        if current_streak_2 == current_streak_1 and best_streak_2 == best_streak_1:
            print(f"   ✅ Idempotency check successful: streaks unchanged (current={current_streak_2}, best={best_streak_2})")
            results['idempotency_check'] = True
        else:
            results['errors'].append(f"Idempotency failed: streaks changed from current={current_streak_1}/best={best_streak_1} to current={current_streak_2}/best={best_streak_2}")
            return results
        
        # Final stats verification
        print("\n📋 Final: Verify stats remain consistent")
        final_stats_response = requests.get(f"{API_BASE}/streaks/stats", headers=headers, timeout=10)
        if final_stats_response.status_code == 200:
            final_stats_json = final_stats_response.json()
            final_current = final_stats_json.get('current_streak', 0)
            final_best = final_stats_json.get('best_streak', 0)
            
            if final_current == current_streak_2 and final_best == best_streak_2:
                print(f"   ✅ Final stats consistent: current={final_current}, best={final_best}")
            else:
                results['errors'].append(f"Final stats inconsistent: expected current={current_streak_2}/best={best_streak_2}, got current={final_current}/best={final_best}")
        
    except requests.exceptions.RequestException as e:
        results['errors'].append(f"Network error: {str(e)}")
    except json.JSONDecodeError as e:
        results['errors'].append(f"JSON decode error: {str(e)}")
    except Exception as e:
        results['errors'].append(f"Unexpected error: {str(e)}")
    
    return results

def main():
    """Main test execution"""
    print(f"🌐 Testing against: {API_BASE}")
    print(f"🕐 Test started at: {datetime.now().isoformat()}")
    
    results = test_streak_endpoints()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 STREAK ENDPOINTS TEST SUMMARY")
    print("=" * 60)
    
    total_tests = 5
    passed_tests = sum([
        results['authentication'],
        results['first_login_streak'], 
        results['stats_verification'],
        results['month_verification'],
        results['idempotency_check']
    ])
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"✅ Authentication: {'PASS' if results['authentication'] else 'FAIL'}")
    print(f"✅ First Login Streak: {'PASS' if results['first_login_streak'] else 'FAIL'}")
    print(f"✅ Stats Verification: {'PASS' if results['stats_verification'] else 'FAIL'}")
    print(f"✅ Month Verification: {'PASS' if results['month_verification'] else 'FAIL'}")
    print(f"✅ Idempotency Check: {'PASS' if results['idempotency_check'] else 'FAIL'}")
    
    print(f"\n📈 SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if results['errors']:
        print(f"\n❌ ERRORS ENCOUNTERED:")
        for i, error in enumerate(results['errors'], 1):
            print(f"   {i}. {error}")
    
    if success_rate == 100:
        print(f"\n🎉 ALL STREAK ENDPOINT TESTS PASSED!")
        return 0
    else:
        print(f"\n🚨 SOME TESTS FAILED - Review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())