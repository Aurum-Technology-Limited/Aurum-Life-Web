#!/usr/bin/env python3
"""
Pre-existing User Password Reset Helper
Since we migrated password hashes but users may not remember their passwords,
this script helps administrators reset passwords for specific users.
"""

import os
import asyncio
from supabase import create_client
from dotenv import load_dotenv
from passlib.context import CryptContext

# Load environment
load_dotenv('/app/backend/.env')

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserPasswordHelper:
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase = create_client(supabase_url, supabase_key)
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def update_user_password(self, email: str, new_password: str) -> bool:
        """Update a user's password hash"""
        try:
            # Hash the new password
            password_hash = self.hash_password(new_password)
            
            # Update in database
            result = self.supabase.table('users').update({
                'password_hash': password_hash
            }).eq('email', email).execute()
            
            if result.data:
                print(f"✅ Password updated for {email}")
                return True
            else:
                print(f"❌ User {email} not found")
                return False
                
        except Exception as e:
            print(f"❌ Error updating password for {email}: {e}")
            return False
    
    def list_users(self):
        """List all migrated users"""
        try:
            result = self.supabase.table('users').select('email, username, created_at').execute()
            print(f"Found {len(result.data)} users:")
            for i, user in enumerate(result.data, 1):
                created = user.get('created_at', '')[:10] if user.get('created_at') else 'unknown'
                print(f"{i:2d}. {user['email']} ({user.get('username', 'no username')}) - {created}")
        except Exception as e:
            print(f"Error listing users: {e}")

def main():
    helper = UserPasswordHelper()
    
    print("🔧 Pre-existing User Password Reset Helper")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. List all users")
        print("2. Reset user password")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            helper.list_users()
        
        elif choice == "2":
            email = input("Enter user email: ").strip()
            new_password = input("Enter new password: ").strip()
            
            if len(new_password) < 6:
                print("❌ Password must be at least 6 characters long")
                continue
            
            if helper.update_user_password(email, new_password):
                print(f"✅ Password reset successful!")
                print(f"📧 User {email} can now login with the new password")
            
        elif choice == "3":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()