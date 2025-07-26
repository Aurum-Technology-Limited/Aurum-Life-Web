#!/usr/bin/env python3
"""
Simplified Supabase Migration
Focus on Supabase client-only approach
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

# Supabase and database imports
from supabase import create_client, Client
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.supabase')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleMigration:
    """Simplified migration using Supabase client only"""
    
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
        
        # User ID mapping for migration
        self.user_id_mapping = {}
        
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
    
    def _transform_document(self, doc: Dict, collection_name: str) -> Dict:
        """Transform MongoDB document for Supabase"""
        transformed = {}
        
        for key, value in doc.items():
            if key == '_id':
                transformed['id'] = str(value)
            elif key == 'user_id' and collection_name != 'users':
                # Map old user ID to new Supabase user ID
                old_user_id = str(value)
                if old_user_id in self.user_id_mapping:
                    transformed['user_id'] = self.user_id_mapping[old_user_id]
                else:
                    # Skip documents with unmapped user IDs
                    logger.warning(f"Skipping document with unmapped user_id: {old_user_id}")
                    return None
            elif isinstance(value, datetime):
                transformed[key] = value.isoformat()
            elif isinstance(value, list) and key.endswith('_ids'):
                # Handle UUID arrays
                transformed[key] = [str(item) for item in value]
            elif isinstance(value, dict):
                # Convert nested objects to JSON
                transformed[key] = value
            else:
                transformed[key] = value
        
        return transformed
    
    async def migrate_users(self):
        """Migrate users to Supabase Auth"""
        try:
            logger.info("🔄 Migrating users...")
            
            db = self.mongo_client[self.mongo_db_name]
            users_collection = db['users']
            
            migrated_count = 0
            
            async for user_doc in users_collection.find():
                try:
                    # Create a demo user in Supabase Auth for testing
                    # In real migration, you'd handle actual user creation
                    user_email = user_doc.get('email', 'demo@aurumlife.com')
                    
                    # For demo purposes, create a test user
                    try:
                        auth_response = self.supabase.auth.admin.create_user({
                            "email": user_email,
                            "password": "temp_password_123",
                            "email_confirm": True,
                            "user_metadata": {
                                "first_name": user_doc.get('first_name', ''),
                                "last_name": user_doc.get('last_name', ''),
                                "migrated_from": "mongodb"
                            }
                        })
                        
                        if auth_response.user:
                            # Store mapping
                            self.user_id_mapping[user_doc['id']] = auth_response.user.id
                            
                            # Create user profile
                            profile_data = {
                                "id": auth_response.user.id,
                                "username": user_doc.get('username'),
                                "first_name": user_doc.get('first_name', ''),
                                "last_name": user_doc.get('last_name', ''),
                                "google_id": user_doc.get('google_id'),
                                "is_active": user_doc.get('is_active', True),
                                "level": user_doc.get('level', 1),
                                "total_points": user_doc.get('total_points', 0),
                                "current_streak": user_doc.get('current_streak', 0)
                            }
                            
                            self.supabase.table('user_profiles').insert(profile_data).execute()
                            migrated_count += 1
                            logger.info(f"✅ Migrated user: {user_email}")
                        
                    except Exception as auth_error:
                        logger.warning(f"Auth creation failed for {user_email}: {auth_error}")
                        # Continue with next user
                        continue
                    
                except Exception as e:
                    logger.error(f"❌ User migration error: {e}")
            
            logger.info(f"✅ Users migrated: {migrated_count}")
            return migrated_count > 0
            
        except Exception as e:
            logger.error(f"❌ User migration failed: {e}")
            return False
    
    async def migrate_collection(self, collection_name: str, table_name: str = None):
        """Migrate a MongoDB collection to Supabase table"""
        if not table_name:
            table_name = collection_name
            
        try:
            logger.info(f"🔄 Migrating {collection_name} to {table_name}...")
            
            db = self.mongo_client[self.mongo_db_name]
            collection = db[collection_name]
            
            migrated_count = 0
            skipped_count = 0
            
            async for doc in collection.find():
                try:
                    transformed = self._transform_document(doc, collection_name)
                    
                    if transformed:
                        # Insert into Supabase
                        self.supabase.table(table_name).insert(transformed).execute()
                        migrated_count += 1
                        
                        if migrated_count % 10 == 0:
                            logger.info(f"   Migrated {migrated_count} {collection_name} records...")
                    else:
                        skipped_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate document: {e}")
                    skipped_count += 1
            
            logger.info(f"✅ {collection_name}: {migrated_count} migrated, {skipped_count} skipped")
            return True
            
        except Exception as e:
            logger.error(f"❌ {collection_name} migration failed: {e}")
            return False
    
    async def run_migration(self):
        """Execute the migration"""
        try:
            logger.info("🚀 Starting Simplified Supabase Migration...")
            
            # Step 1: Initialize connections
            await self.initialize_connections()
            
            # Step 2: Migrate users first
            if not await self.migrate_users():
                logger.warning("⚠️ User migration had issues, but continuing...")
            
            # Step 3: Migrate collections in order
            collections_to_migrate = [
                ('pillars', 'pillars'),
                ('areas', 'areas'),
                ('projects', 'projects'),
                ('tasks', 'tasks'),
                ('journal_templates', 'journal_templates'),
                ('journal_entries', 'journal_entries')
            ]
            
            for mongo_collection, supabase_table in collections_to_migrate:
                # Check if collection exists
                db = self.mongo_client[self.mongo_db_name]
                if mongo_collection in await db.list_collection_names():
                    await self.migrate_collection(mongo_collection, supabase_table)
                else:
                    logger.info(f"⏩ Skipping {mongo_collection} (collection not found)")
            
            logger.info("✅ Migration completed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
            
        finally:
            if self.mongo_client:
                self.mongo_client.close()

async def main():
    """Run the migration"""
    migration = SimpleMigration()
    success = await migration.run_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Verify data in Supabase Table Editor")
        print("2. Update backend to use Supabase")
        print("3. Configure authentication")
        return True
    else:
        print("\n❌ Migration had issues. Check logs above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())