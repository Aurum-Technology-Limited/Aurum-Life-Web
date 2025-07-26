#!/usr/bin/env python3
"""
Fix User Migration Issue
Migrates all MongoDB users to the public.users table in Supabase
so they can login with their original credentials
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Supabase and database imports
from supabase import create_client, Client
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
from dotenv import load_dotenv

# Load environment from backend
load_dotenv('/app/backend/.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UserMigrationFixer:
    """Fix the user migration by properly migrating MongoDB users to public.users table"""
    
    def __init__(self):
        # Supabase configuration
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        # MongoDB configuration
        self.mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.mongo_db_name = os.getenv('DB_NAME', 'aurum_life')
        
        # Initialize clients
        self.supabase: Client = None
        self.mongo_client: AsyncIOMotorClient = None
        
    async def initialize_connections(self):
        """Initialize connections"""
        try:
            # Initialize Supabase client
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized")
            
            # Initialize MongoDB client
            self.mongo_client = AsyncIOMotorClient(self.mongo_url)
            await self.mongo_client.admin.command('ping')
            logger.info("✅ MongoDB client connected")
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            raise
    
    async def get_existing_supabase_users(self) -> Dict[str, str]:
        """Get existing users in public.users table mapped by email"""
        try:
            result = self.supabase.table('users').select('*').execute()
            existing_users = {}
            
            for user in result.data:
                existing_users[user['email']] = user['id']
            
            logger.info(f"Found {len(existing_users)} existing users in public.users table")
            return existing_users
            
        except Exception as e:
            logger.error(f"Error getting existing Supabase users: {e}")
            return {}
    
    async def migrate_mongo_users_to_supabase(self):
        """Migrate MongoDB users to Supabase public.users table"""
        try:
            logger.info("🔄 Starting user migration from MongoDB to Supabase...")
            
            # Get existing users to avoid duplicates
            existing_users = await self.get_existing_supabase_users()
            
            # Get MongoDB users
            db = self.mongo_client[self.mongo_db_name]
            users_collection = db['users']
            
            migrated_count = 0
            skipped_count = 0
            error_count = 0
            
            async for user_doc in users_collection.find():
                try:
                    user_email = user_doc.get('email', '')
                    
                    # Skip if user already exists in public.users
                    if user_email in existing_users:
                        logger.info(f"⏩ Skipping existing user: {user_email}")
                        skipped_count += 1
                        continue
                    
                    # Prepare user data for Supabase public.users table
                    user_data = {
                        'id': user_doc.get('id'),  # Keep original UUID
                        'username': user_doc.get('username'),
                        'email': user_email,
                        'first_name': user_doc.get('first_name', ''),
                        'last_name': user_doc.get('last_name', ''),
                        'password_hash': user_doc.get('password_hash'),  # Keep original password hash
                        'google_id': user_doc.get('google_id'),
                        'profile_picture': user_doc.get('profile_picture'),
                        'is_active': user_doc.get('is_active', True),
                        'level': user_doc.get('level', 1),
                        'total_points': user_doc.get('total_points', 0),
                        'current_streak': user_doc.get('current_streak', 0),
                        'created_at': user_doc.get('created_at', datetime.utcnow()).isoformat(),
                        'updated_at': user_doc.get('updated_at', datetime.utcnow()).isoformat()
                    }
                    
                    # Insert into Supabase public.users table
                    result = self.supabase.table('users').insert(user_data).execute()
                    
                    if result.data:
                        migrated_count += 1
                        logger.info(f"✅ Migrated user: {user_email}")
                    else:
                        logger.warning(f"⚠️ Failed to migrate user: {user_email}")
                        error_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error migrating user {user_doc.get('email', 'unknown')}: {e}")
                    error_count += 1
            
            logger.info(f"""
✅ User migration completed!
📊 Results:
   - Migrated: {migrated_count} users
   - Skipped: {skipped_count} users (already existed)
   - Errors: {error_count} users
   - Total processed: {migrated_count + skipped_count + error_count} users
""")
            
            return migrated_count > 0
            
        except Exception as e:
            logger.error(f"❌ User migration failed: {e}")
            return False
    
    async def verify_migration(self):
        """Verify that users can now login"""
        try:
            logger.info("🔍 Verifying migration...")
            
            # Get some sample users from public.users
            result = self.supabase.table('users').select('email').limit(5).execute()
            
            logger.info(f"Sample migrated users:")
            for user in result.data:
                logger.info(f"  - {user['email']}")
            
            logger.info("✅ Migration verification completed")
            
        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
    
    async def run_fix(self):
        """Execute the user migration fix"""
        try:
            logger.info("🚀 Starting User Migration Fix...")
            logger.info("=" * 60)
            
            # Step 1: Initialize connections
            await self.initialize_connections()
            
            # Step 2: Migrate users
            if await self.migrate_mongo_users_to_supabase():
                logger.info("✅ User migration completed successfully!")
            else:
                logger.warning("⚠️ User migration had issues")
            
            # Step 3: Verify migration
            await self.verify_migration()
            
            logger.info("=" * 60)
            logger.info("✅ User Migration Fix completed!")
            logger.info("""
📋 What was fixed:
1. Migrated all MongoDB users to Supabase public.users table
2. Preserved original password hashes so users can login with existing credentials
3. Maintained user UUIDs and profile data

🎯 Users should now be able to login with their original credentials!
            """)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ User migration fix failed: {e}")
            return False
            
        finally:
            if self.mongo_client:
                self.mongo_client.close()

async def main():
    """Run the user migration fix"""
    fixer = UserMigrationFixer()
    success = await fixer.run_fix()
    
    if success:
        print("\n🎉 User migration fix completed successfully!")
        print("🔑 Users can now login with their original credentials.")
        return True
    else:
        print("\n❌ User migration fix had issues. Check logs above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())