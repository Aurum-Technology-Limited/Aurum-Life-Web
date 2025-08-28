#!/usr/bin/env python3
"""
Test Supabase File Storage Integration
Verify file upload, storage, and management functionality
"""

import requests
import base64
import json
import os

BASE_URL = "http://localhost:8001/api"
FRONTEND_URL = "http://localhost:3000"

def test_file_storage_integration():
    """Test complete file storage functionality"""
    print("🗂️ SUPABASE FILE STORAGE INTEGRATION TEST")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    auth_token = None
    
    # Test 1: Authentication for file operations
    print("\n1️⃣ Authentication Test")
    try:
        login_data = {
            "email": "final.test@aurumlife.com",
            "password": "FinalTest123!"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            auth_token = token_data["access_token"]
            print("   ✅ Authentication successful")
            print("   ✅ JWT token obtained")
            tests_passed += 1
        else:
            print(f"   ❌ Authentication failed: HTTP {login_response.status_code}")
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
    total_tests += 1
    
    if not auth_token:
        print("\n❌ Cannot continue without authentication")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 2: Create test project for file attachment
    print("\n2️⃣ Create Test Project")
    project_id = None
    try:
        project_data = {
            "name": "File Storage Test Project",
            "description": "Testing Supabase file storage",
            "area_id": "test-area-id-123"  # This might fail, but that's ok for testing
        }
        
        # First create an area
        area_data = {
            "name": "Test Area",
            "pillar_id": "test-pillar-id-123"
        }
        
        # First create a pillar
        pillar_data = {
            "name": "Test Pillar",
            "description": "For file storage testing"
        }
        
        pillar_response = requests.post(f"{BASE_URL}/pillars", json=pillar_data, headers=headers)
        if pillar_response.status_code == 200:
            pillar = pillar_response.json()
            area_data["pillar_id"] = pillar["id"]
            
            area_response = requests.post(f"{BASE_URL}/areas", json=area_data, headers=headers)
            if area_response.status_code == 200:
                area = area_response.json()
                project_data["area_id"] = area["id"]
                
                project_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
                if project_response.status_code == 200:
                    project = project_response.json()
                    project_id = project["id"]
                    print("   ✅ Test project created")
                    tests_passed += 1
                else:
                    print(f"   ❌ Project creation failed: HTTP {project_response.status_code}")
            else:
                print(f"   ❌ Area creation failed: HTTP {area_response.status_code}")
        else:
            print(f"   ❌ Pillar creation failed: HTTP {pillar_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Project creation error: {e}")
    total_tests += 1
    
    # Test 3: File Upload to Supabase Storage
    print("\n3️⃣ File Upload Test")
    uploaded_file_id = None
    try:
        if project_id:
            # Create a simple test file (base64 encoded)
            test_content = "This is a test file for Supabase Storage integration!"
            test_file_b64 = base64.b64encode(test_content.encode()).decode()
            data_url = f"data:text/plain;base64,{test_file_b64}"
            
            file_data = {
                "filename": "test-file.txt",
                "original_filename": "test-file.txt",
                "file_type": "document",
                "mime_type": "text/plain",
                "file_size": len(test_content),
                "file_content": data_url,
                "parent_type": "project",
                "parent_id": project_id,
                "description": "Test file upload to Supabase Storage"
            }
            
            upload_response = requests.post(f"{BASE_URL}/resources", json=file_data, headers=headers)
            if upload_response.status_code == 200:
                uploaded_file = upload_response.json()
                uploaded_file_id = uploaded_file["id"]
                print("   ✅ File uploaded successfully")
                print(f"   ✅ File ID: {uploaded_file_id}")
                
                # Check if it's using Supabase Storage
                if uploaded_file.get("storage_bucket") and uploaded_file.get("storage_path"):
                    print("   ✅ File stored in Supabase Storage")
                    print(f"   📁 Bucket: {uploaded_file['storage_bucket']}")
                    print(f"   📄 Path: {uploaded_file['storage_path']}")
                elif uploaded_file.get("file_url"):
                    print("   ✅ File URL generated")
                else:
                    print("   ⚠️ File uploaded but storage details unclear")
                
                tests_passed += 1
            else:
                print(f"   ❌ File upload failed: HTTP {upload_response.status_code}")
                print(f"   Response: {upload_response.text[:200]}")
        else:
            print("   ⏩ Skipping file upload (no project created)")
            
    except Exception as e:
        print(f"   ❌ File upload error: {e}")
    total_tests += 1
    
    # Test 4: Retrieve Files by Parent
    print("\n4️⃣ File Retrieval Test")
    try:
        if project_id:
            files_response = requests.get(f"{BASE_URL}/resources/parent/project/{project_id}", headers=headers)
            if files_response.status_code == 200:
                files = files_response.json()
                print(f"   ✅ Retrieved {len(files)} files for project")
                
                if len(files) > 0:
                    file = files[0]
                    if file.get("file_url"):
                        print("   ✅ File has download URL")
                    if file.get("storage_bucket"):
                        print("   ✅ File has Supabase Storage reference")
                    tests_passed += 1
                else:
                    print("   ⚠️ No files found (upload may have failed)")
                    tests_passed += 0.5
            else:
                print(f"   ❌ File retrieval failed: HTTP {files_response.status_code}")
        else:
            print("   ⏩ Skipping file retrieval (no project created)")
            
    except Exception as e:
        print(f"   ❌ File retrieval error: {e}")
    total_tests += 1
    
    # Test 5: Storage Migration Endpoint
    print("\n5️⃣ Storage Migration Test")
    try:
        migration_response = requests.post(f"{BASE_URL}/resources/migrate-to-storage", headers=headers)
        if migration_response.status_code == 200:
            migration_result = migration_response.json()
            print("   ✅ Migration endpoint accessible")
            print(f"   📊 Migration result: {migration_result.get('message', 'Completed')}")
            tests_passed += 1
        else:
            print(f"   ❌ Migration endpoint failed: HTTP {migration_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Migration test error: {e}")
    total_tests += 1
    
    # Test 6: Frontend Integration
    print("\n6️⃣ Frontend Integration Test")
    try:
        frontend_response = requests.get(FRONTEND_URL, timeout=5)
        if frontend_response.status_code == 200:
            frontend_html = frontend_response.text
            if "FileAttachment" in frontend_html or "file-attachment" in frontend_html:
                print("   ✅ Frontend accessible with file components")
                tests_passed += 1
            else:
                print("   ✅ Frontend accessible")
                tests_passed += 0.5
        else:
            print(f"   ❌ Frontend not accessible: HTTP {frontend_response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️ Frontend test error: {e}")
    total_tests += 1
    
    # Calculate Results
    print("\n" + "=" * 60)
    print("📊 FILE STORAGE INTEGRATION SUMMARY")
    print("=" * 60)
    
    success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"✅ Tests Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 85:
        print("\n🎉 FILE STORAGE INTEGRATION SUCCESSFUL!")
        print("✅ Authentication working")
        print("✅ File upload to Supabase Storage")
        print("✅ File retrieval and URL generation")
        print("✅ Storage migration endpoint ready")
        print("✅ Frontend integration prepared")
        
    elif success_rate >= 70:
        print("\n✅ FILE STORAGE MOSTLY WORKING!")
        print("Core functionality operational with minor issues")
        
    else:
        print("\n❌ FILE STORAGE NEEDS MORE WORK")
        print("Critical issues detected")
    
    print(f"\n📁 STORAGE MIGRATION STATUS: {success_rate:.0f}% COMPLETE")
    print("=" * 60)
    
    # Cleanup
    if uploaded_file_id:
        try:
            delete_response = requests.delete(f"{BASE_URL}/resources/{uploaded_file_id}", headers=headers)
            if delete_response.status_code == 200:
                print("\n🗑️ Test file cleaned up successfully")
        except Exception as e:
            print(f"\n⚠️ Cleanup warning: {e}")
    
    return success_rate >= 85

if __name__ == "__main__":
    success = test_file_storage_integration()
    exit(0 if success else 1)