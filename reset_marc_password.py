#!/usr/bin/env python3
"""
Reset Marc's password for testing
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from supabase_client import find_documents, update_document
from auth import get_password_hash

async def reset_marc_password():
    """Reset Marc's password to 'password123'"""
    try:
        # Find Marc's user
        users = await find_documents("users", {"email": "marc.alleyne@aurumtechnologyltd.com"}, limit=1)
        if not users:
            print("Marc user not found")
            return
        
        user = users[0]
        user_id = user['id']
        
        # Hash the new password
        new_password_hash = get_password_hash("password123")
        
        # Update the user
        success = await update_document("users", user_id, {"password_hash": new_password_hash})
        
        if success:
            print(f"✅ Successfully reset password for Marc ({user['email']})")
        else:
            print("❌ Failed to update password")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(reset_marc_password())