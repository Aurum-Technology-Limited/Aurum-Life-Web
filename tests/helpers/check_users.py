#!/usr/bin/env python3
"""
Quick script to check users in the database
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from supabase_client import find_documents

async def check_users():
    """Check what users exist"""
    try:
        users = await find_documents("users", {}, limit=10)
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"- {user.get('email', 'No email')} (ID: {user.get('id', 'No ID')})")
        
        # Try to find marc specifically
        marc_user = await find_documents("users", {"email": "marc.alleyne@gmail.com"}, limit=1)
        if marc_user:
            print(f"\nFound Marc: {marc_user[0]}")
        else:
            print("\nMarc user not found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_users())