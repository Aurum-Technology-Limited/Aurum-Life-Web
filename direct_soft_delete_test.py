#!/usr/bin/env python3
"""
DIRECT SUPABASE SOFT DELETE TEST
This script tests the soft delete functionality directly by creating an entry,
soft deleting it, and checking the database state.
"""

import os
import sys
import requests
import time
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://taskpilot-2.preview.emergentagent.com/api"

def main():
    """Main execution"""
    print("🧪 DIRECT SUPABASE SOFT DELETE TEST")
    print("="*50)
    
    try:
        # Initialize Supabase client
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            print("❌ Supabase credentials not found")
            return False
        
        supabase_client = create_client(url, key)
        print("✅ Supabase client initialized")
        
        # Initialize HTTP session for API calls
        session = requests.Session()
        
        # Step 1: Authenticate
        print("\n🔐 Step 1: Authenticate")
        login_data = {
            "email": "marc.alleyne@aurumtechnologyltd.com",
            "password": "password123"
        }
        
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
        
        auth_data = response.json()
        token = auth_data['access_token']
        session.headers.update({'Authorization': f'Bearer {token}'})
        print("✅ Authentication successful")
        
        # Step 2: Create a test journal entry
        print("\n📝 Step 2: Create test journal entry")
        entry_data = {
            "title": f"Direct Soft Delete Test - {int(time.time())}",
            "content": "This entry will be used to test direct soft delete functionality.",
            "mood": "reflective",
            "tags": ["test", "soft-delete"]
        }
        
        response = session.post(f"{BACKEND_URL}/journal", json=entry_data)
        if response.status_code != 200:
            print(f"❌ Entry creation failed: {response.status_code}")
            return False
        
        entry = response.json()
        entry_id = entry['id']
        print(f"✅ Entry created with ID: {entry_id}")
        
        # Step 3: Check entry in database before deletion
        print("\n🔍 Step 3: Check entry in database (before deletion)")
        result = supabase_client.table('journal_entries').select('*').eq('id', entry_id).execute()
        if not result.data:
            print("❌ Entry not found in database")
            return False
        
        before_entry = result.data[0]
        print(f"✅ Entry found in database")
        print(f"   - Title: {before_entry['title']}")
        print(f"   - Deleted: {before_entry.get('deleted', 'N/A')}")
        print(f"   - Deleted At: {before_entry.get('deleted_at', 'N/A')}")
        
        # Step 4: Soft delete the entry via API
        print("\n🗑️ Step 4: Soft delete entry via API")
        response = session.delete(f"{BACKEND_URL}/journal/{entry_id}")
        if response.status_code != 200:
            print(f"❌ Soft delete failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("✅ Soft delete API call successful")
        
        # Step 5: Check entry in database after deletion
        print("\n🔍 Step 5: Check entry in database (after deletion)")
        result = supabase_client.table('journal_entries').select('*').eq('id', entry_id).execute()
        if not result.data:
            print("❌ Entry completely removed from database (should be soft deleted)")
            return False
        
        after_entry = result.data[0]
        print(f"✅ Entry still exists in database")
        print(f"   - Title: {after_entry['title']}")
        print(f"   - Deleted: {after_entry.get('deleted', 'N/A')}")
        print(f"   - Deleted At: {after_entry.get('deleted_at', 'N/A')}")
        
        # Check if soft delete worked
        is_deleted = after_entry.get('deleted', False)
        has_deleted_at = after_entry.get('deleted_at') is not None
        
        if is_deleted and has_deleted_at:
            print("🎉 Soft delete working correctly!")
        else:
            print("❌ Soft delete not working correctly")
            print(f"   - Expected deleted=True, got: {is_deleted}")
            print(f"   - Expected deleted_at to be set, got: {has_deleted_at}")
        
        # Step 6: Test trash endpoint
        print("\n🗂️ Step 6: Test trash endpoint")
        response = session.get(f"{BACKEND_URL}/journal/trash")
        if response.status_code != 200:
            print(f"❌ Trash endpoint failed: {response.status_code}")
            return False
        
        trash_entries = response.json()
        found_in_trash = any(e.get('id') == entry_id for e in trash_entries)
        
        if found_in_trash:
            print(f"✅ Entry found in trash ({len(trash_entries)} total trash entries)")
            trash_entry = next(e for e in trash_entries if e.get('id') == entry_id)
            print(f"   - Deleted flag in trash: {trash_entry.get('deleted', 'N/A')}")
            print(f"   - Deleted at in trash: {trash_entry.get('deleted_at', 'N/A')}")
        else:
            print(f"❌ Entry not found in trash ({len(trash_entries)} total trash entries)")
        
        # Step 7: Test main journal endpoint (should exclude deleted)
        print("\n📖 Step 7: Test main journal endpoint")
        response = session.get(f"{BACKEND_URL}/journal")
        if response.status_code != 200:
            print(f"❌ Journal endpoint failed: {response.status_code}")
            return False
        
        journal_entries = response.json()
        found_in_journal = any(e.get('id') == entry_id for e in journal_entries)
        
        if not found_in_journal:
            print(f"✅ Entry correctly excluded from main journal ({len(journal_entries)} total entries)")
        else:
            print(f"❌ Entry still appears in main journal (should be excluded)")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   - Entry created: ✅")
        print(f"   - Soft delete API: ✅")
        print(f"   - Database soft delete: {'✅' if is_deleted and has_deleted_at else '❌'}")
        print(f"   - Found in trash: {'✅' if found_in_trash else '❌'}")
        print(f"   - Excluded from journal: {'✅' if not found_in_journal else '❌'}")
        
        success = is_deleted and has_deleted_at and found_in_trash and not found_in_journal
        print(f"\n🏁 OVERALL RESULT: {'✅ SUCCESS' if success else '❌ FAILURE'}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)