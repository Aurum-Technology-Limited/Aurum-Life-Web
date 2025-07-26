#!/usr/bin/env python3
"""
Add system user to Supabase
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

def add_system_user():
    """Add system user for journal templates"""
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        supabase = create_client(url, key)
        
        # Check if system user exists
        existing = supabase.table('users').select('id').eq('id', '00000000-0000-0000-0000-000000000000').execute()
        
        if existing.data:
            print("✅ System user already exists")
            return True
        
        # Create system user
        system_user = {
            'id': '00000000-0000-0000-0000-000000000000',
            'username': 'system',
            'email': 'system@aurumlife.internal', 
            'first_name': 'System',
            'last_name': 'User',
            'is_active': True,
            'level': 1,
            'total_points': 0,
            'current_streak': 0
        }
        
        result = supabase.table('users').insert(system_user).execute()
        
        if result.data:
            print("✅ System user created successfully")
            return True
        else:
            print("❌ Failed to create system user")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    add_system_user()