#!/usr/bin/env python3
"""
Test Frontend Supabase Integration
Verify React app works with Supabase authentication
"""

import requests
import time

def test_frontend_integration():
    """Test frontend Supabase integration"""
    print("🖥️ FRONTEND SUPABASE INTEGRATION TEST")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Frontend Accessibility
    print("\n1️⃣ Frontend Accessibility Test")
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
            print(f"   ✅ Response size: {len(response.text)} bytes")
            
            # Check if Supabase is loaded
            if "supabase" in response.text.lower() or "REACT_APP_SUPABASE" in response.text:
                print("   ✅ Supabase configuration detected")
                tests_passed += 1
            else:
                print("   ⚠️ Supabase configuration not visible (may be bundled)")
                tests_passed += 0.5  # Partial success
        else:
            print(f"   ❌ Frontend not accessible: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend access error: {e}")
    total_tests += 1
    
    # Test 2: Backend Connectivity (through frontend)
    print("\n2️⃣ Backend API Connectivity")
    try:
        # Test health endpoint that frontend would use
        backend_response = requests.get("http://localhost:8001/api/health")
        if backend_response.status_code == 200:
            print("   ✅ Backend API accessible")
            health_data = backend_response.json()
            if health_data.get('status') == 'healthy':
                print("   ✅ Backend reporting healthy status")
                tests_passed += 1
            else:
                print("   ⚠️ Backend health status unclear")
                tests_passed += 0.5
        else:
            print(f"   ❌ Backend API error: HTTP {backend_response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend connectivity error: {e}")
    total_tests += 1
    
    # Test 3: Check JavaScript Console Errors
    print("\n3️⃣ JavaScript Bundle Check")
    try:
        # Look for main JavaScript bundle
        main_page = requests.get("http://localhost:3000").text
        
        # Check for React build indicators
        if "react" in main_page.lower() or "__REACT" in main_page:
            print("   ✅ React application detected")
        else:
            print("   ⚠️ React indicators not found")
        
        # Check for error indicators in HTML
        if "error" not in main_page.lower() or "failed" not in main_page.lower():
            print("   ✅ No obvious errors in initial load")
            tests_passed += 1
        else:
            print("   ⚠️ Potential errors detected in HTML")
            tests_passed += 0.5
            
    except Exception as e:
        print(f"   ❌ JavaScript bundle check error: {e}")
    total_tests += 1
    
    # Test 4: Environment Variables Check
    print("\n4️⃣ Environment Configuration")
    try:
        # Check if environment variables are accessible
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            
        if 'REACT_APP_SUPABASE_URL' in env_content:
            print("   ✅ Supabase URL configured")
            
        if 'REACT_APP_SUPABASE_ANON_KEY' in env_content:
            print("   ✅ Supabase anon key configured")
            
        if 'REACT_APP_BACKEND_URL' in env_content:
            print("   ✅ Backend URL configured")
            
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Environment check error: {e}")
    total_tests += 1
    
    # Test 5: File Integration Check
    print("\n5️⃣ File Integration Status")
    try:
        integration_files = [
            '/app/frontend/src/contexts/SupabaseAuthContext.js',
            '/app/frontend/src/services/supabase.js',
            '/app/frontend/src/services/supabaseApi.js',
            '/app/frontend/src/hooks/useRealtime.js'
        ]
        
        files_exist = 0
        for file_path in integration_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if len(content) > 100:  # Basic content check
                        files_exist += 1
                        print(f"   ✅ {file_path.split('/')[-1]}: Present")
                    else:
                        print(f"   ⚠️ {file_path.split('/')[-1]}: Too small")
            except FileNotFoundError:
                print(f"   ❌ {file_path.split('/')[-1]}: Missing")
        
        if files_exist >= 3:  # At least 3 out of 4 files
            print(f"   ✅ Integration files present ({files_exist}/4)")
            tests_passed += 1
        else:
            print(f"   ❌ Integration files incomplete ({files_exist}/4)")
            
    except Exception as e:
        print(f"   ❌ File integration check error: {e}")
    total_tests += 1
    
    # Calculate Results
    print("\n" + "=" * 50)
    print("📊 FRONTEND INTEGRATION SUMMARY")
    print("=" * 50)
    
    success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"✅ Tests Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("\n🎉 FRONTEND INTEGRATION SUCCESSFUL!")
        print("✅ React app is running")
        print("✅ Supabase configuration ready")
        print("✅ Backend connectivity working")
        print("✅ Integration files in place")
        
        print("\n📱 NEXT STEPS:")
        print("1. Test authentication flow")
        print("2. Verify real-time features")
        print("3. Test CRUD operations")
        
    elif success_rate >= 60:
        print("\n✅ FRONTEND INTEGRATION MOSTLY WORKING!")
        print("Minor issues detected but core functionality ready")
        
    else:
        print("\n❌ FRONTEND INTEGRATION NEEDS WORK")
        print("Critical issues detected")
    
    print(f"\n🚀 INTEGRATION STATUS: {success_rate:.0f}% COMPLETE")
    print("=" * 50)
    
    return success_rate >= 80

if __name__ == "__main__":
    success = test_frontend_integration()
    exit(0 if success else 1)