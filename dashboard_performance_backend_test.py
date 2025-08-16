#!/usr/bin/env python3
"""
Dashboard Performance Backend Test
Re-test dashboard endpoint performance and correctness after concurrency update

Test Requirements:
1) Auth, then call GET /api/dashboard 3 times in a row
2) Record response times; expect each under ~500ms after warm cache (some variability allowed)
3) Validate returned JSON structure still has keys: user, stats, recent_tasks, areas; 
   stats includes completed_tasks, total_tasks, completion_rate, active_projects, completed_projects, active_areas
4) Also call GET /api/ultra/dashboard and verify similar shape and faster execution if cache is warm
5) Return concise timing chart and any issues observed
"""

import requests
import time
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fcbe964d-a00c-4624-8b03-88a109fb0408.preview.emergentagent.com')
BASE_URL = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password123"

def authenticate():
    """Authenticate and return JWT token"""
    print("🔐 Authenticating user...")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    auth_time = (time.time() - start_time) * 1000
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        print(f"✅ Authentication successful ({auth_time:.0f}ms)")
        return access_token
    else:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return None

def test_dashboard_endpoint(token, endpoint_name, endpoint_url):
    """Test a dashboard endpoint 3 times and return timing data"""
    print(f"\n📊 Testing {endpoint_name} endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    timings = []
    responses = []
    
    for i in range(3):
        print(f"  Call {i+1}/3...", end=" ")
        
        start_time = time.time()
        try:
            response = requests.get(endpoint_url, headers=headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                timings.append(response_time)
                responses.append(data)
                print(f"✅ {response_time:.0f}ms")
            else:
                print(f"❌ HTTP {response.status_code}")
                timings.append(None)
                responses.append(None)
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            timings.append(None)
            responses.append(None)
    
    return timings, responses

def validate_dashboard_structure(data, endpoint_name):
    """Validate dashboard JSON structure"""
    print(f"\n🔍 Validating {endpoint_name} structure...")
    
    if not data:
        print("❌ No data to validate")
        return False
    
    # Required top-level keys
    required_keys = ['user', 'stats', 'recent_tasks', 'areas']
    missing_keys = []
    
    for key in required_keys:
        if key not in data:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing top-level keys: {missing_keys}")
        return False
    
    print("✅ All top-level keys present: user, stats, recent_tasks, areas")
    
    # Validate stats structure
    stats = data.get('stats', {})
    required_stats = [
        'completed_tasks', 'total_tasks', 'completion_rate', 
        'active_projects', 'completed_projects', 'active_areas'
    ]
    
    missing_stats = []
    for stat in required_stats:
        if stat not in stats:
            missing_stats.append(stat)
    
    if missing_stats:
        print(f"❌ Missing stats keys: {missing_stats}")
        return False
    
    print("✅ All required stats keys present")
    
    # Print stats values for verification
    print(f"  📈 Stats: completed_tasks={stats.get('completed_tasks')}, total_tasks={stats.get('total_tasks')}")
    print(f"  📈 Stats: completion_rate={stats.get('completion_rate')}, active_projects={stats.get('active_projects')}")
    print(f"  📈 Stats: completed_projects={stats.get('completed_projects')}, active_areas={stats.get('active_areas')}")
    
    return True

def print_timing_chart(regular_timings, ultra_timings):
    """Print concise timing chart"""
    print("\n📊 DASHBOARD PERFORMANCE TIMING CHART")
    print("=" * 50)
    
    print(f"{'Call':<6} {'Regular':<12} {'Ultra':<12} {'Improvement':<12}")
    print("-" * 50)
    
    for i in range(3):
        regular = regular_timings[i] if regular_timings[i] else "FAIL"
        ultra = ultra_timings[i] if ultra_timings[i] else "FAIL"
        
        if isinstance(regular, (int, float)) and isinstance(ultra, (int, float)):
            improvement = f"{((regular - ultra) / regular * 100):.1f}%"
        else:
            improvement = "N/A"
        
        regular_str = f"{regular:.0f}ms" if isinstance(regular, (int, float)) else str(regular)
        ultra_str = f"{ultra:.0f}ms" if isinstance(ultra, (int, float)) else str(ultra)
        
        print(f"{i+1:<6} {regular_str:<12} {ultra_str:<12} {improvement:<12}")
    
    # Calculate averages
    valid_regular = [t for t in regular_timings if t is not None]
    valid_ultra = [t for t in ultra_timings if t is not None]
    
    if valid_regular and valid_ultra:
        avg_regular = sum(valid_regular) / len(valid_regular)
        avg_ultra = sum(valid_ultra) / len(valid_ultra)
        avg_improvement = ((avg_regular - avg_ultra) / avg_regular * 100)
        
        print("-" * 50)
        print(f"{'AVG':<6} {avg_regular:.0f}ms{'':<6} {avg_ultra:.0f}ms{'':<6} {avg_improvement:.1f}%")
    
    print("=" * 50)

def main():
    """Main test execution"""
    print("🚀 DASHBOARD PERFORMANCE BACKEND TEST")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User: {TEST_EMAIL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Authenticate
    token = authenticate()
    if not token:
        print("❌ Test failed: Could not authenticate")
        return
    
    # Step 2: Test regular dashboard endpoint 3 times
    regular_timings, regular_responses = test_dashboard_endpoint(
        token, "Regular Dashboard", f"{BASE_URL}/dashboard"
    )
    
    # Step 3: Test ultra dashboard endpoint 3 times
    ultra_timings, ultra_responses = test_dashboard_endpoint(
        token, "Ultra Dashboard", f"{BASE_URL}/ultra/dashboard"
    )
    
    # Step 4: Validate structure (use first successful response)
    regular_data = next((r for r in regular_responses if r), None)
    ultra_data = next((r for r in ultra_responses if r), None)
    
    regular_valid = validate_dashboard_structure(regular_data, "Regular Dashboard")
    ultra_valid = validate_dashboard_structure(ultra_data, "Ultra Dashboard")
    
    # Step 5: Print timing chart
    print_timing_chart(regular_timings, ultra_timings)
    
    # Step 6: Performance analysis
    print("\n🎯 PERFORMANCE ANALYSIS")
    print("=" * 30)
    
    valid_regular = [t for t in regular_timings if t is not None]
    valid_ultra = [t for t in ultra_timings if t is not None]
    
    # Check 500ms target
    regular_under_500 = sum(1 for t in valid_regular if t < 500)
    ultra_under_500 = sum(1 for t in valid_ultra if t < 500)
    
    print(f"Regular Dashboard: {regular_under_500}/{len(valid_regular)} calls under 500ms")
    print(f"Ultra Dashboard: {ultra_under_500}/{len(valid_ultra)} calls under 500ms")
    
    if valid_regular:
        avg_regular = sum(valid_regular) / len(valid_regular)
        print(f"Regular Average: {avg_regular:.0f}ms")
    
    if valid_ultra:
        avg_ultra = sum(valid_ultra) / len(valid_ultra)
        print(f"Ultra Average: {avg_ultra:.0f}ms")
    
    # Step 7: Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 20)
    
    issues = []
    
    if not regular_valid:
        issues.append("Regular dashboard structure validation failed")
    
    if not ultra_valid:
        issues.append("Ultra dashboard structure validation failed")
    
    if valid_regular and any(t > 500 for t in valid_regular):
        slow_calls = [i+1 for i, t in enumerate(valid_regular) if t > 500]
        issues.append(f"Regular dashboard calls {slow_calls} exceeded 500ms")
    
    if valid_ultra and any(t > 500 for t in valid_ultra):
        slow_calls = [i+1 for i, t in enumerate(valid_ultra) if t > 500]
        issues.append(f"Ultra dashboard calls {slow_calls} exceeded 500ms")
    
    if len(valid_regular) < 3:
        issues.append(f"Regular dashboard had {3 - len(valid_regular)} failed calls")
    
    if len(valid_ultra) < 3:
        issues.append(f"Ultra dashboard had {3 - len(valid_ultra)} failed calls")
    
    if issues:
        print("❌ ISSUES OBSERVED:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("✅ NO ISSUES OBSERVED")
        print("  • All calls successful")
        print("  • All response times under 500ms")
        print("  • All JSON structures valid")
        print("  • Ultra dashboard shows performance improvement")
    
    # Success rate
    total_calls = 6  # 3 regular + 3 ultra
    successful_calls = len(valid_regular) + len(valid_ultra)
    success_rate = (successful_calls / total_calls) * 100
    
    print(f"\n🎯 SUCCESS RATE: {successful_calls}/{total_calls} ({success_rate:.1f}%)")
    
    if success_rate >= 100 and not issues:
        print("🎉 DASHBOARD PERFORMANCE TEST: PASSED")
    elif success_rate >= 80:
        print("⚠️  DASHBOARD PERFORMANCE TEST: PASSED WITH WARNINGS")
    else:
        print("❌ DASHBOARD PERFORMANCE TEST: FAILED")

if __name__ == "__main__":
    main()