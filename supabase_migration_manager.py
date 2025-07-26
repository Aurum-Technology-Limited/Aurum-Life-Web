#!/usr/bin/env python3
"""
Supabase Migration Manager for Aurum Life
Handles complete migration from MongoDB to Supabase PostgreSQL
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

# Supabase and database imports
import asyncpg
from supabase import create_client, Client
from motor.motor_asyncio import AsyncIOMotorClient
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.supabase')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SupabaseMigrationManager:
    """Handles complete migration from MongoDB to Supabase"""
    
    def __init__(self):
        # Supabase configuration
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase_project_ref = os.getenv('SUPABASE_PROJECT_REF')
        self.supabase_db_password = os.getenv('SUPABASE_DB_PASSWORD')
        
        # MongoDB configuration (from existing .env)
        self.mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.mongo_db_name = os.getenv('DB_NAME', 'aurum_life')
        
        # Migration settings
        self.batch_size = int(os.getenv('MIGRATION_BATCH_SIZE', '1000'))
        self.backup_before_migration = os.getenv('BACKUP_BEFORE_MIGRATION', 'true').lower() == 'true'
        
        # Initialize clients
        self.supabase: Client = None
        self.mongo_client: AsyncIOMotorClient = None
        self.pg_conn = None
        
        # Migration statistics
        self.migration_stats = {
            'started_at': None,
            'completed_at': None,
            'total_records': 0,
            'migrated_records': 0,
            'failed_records': 0,
            'collections_migrated': [],
            'errors': []
        }
        
    async def initialize_connections(self):
        """Initialize all database connections"""
        try:
            # Initialize Supabase client
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized")
            
            # Initialize MongoDB client
            self.mongo_client = AsyncIOMotorClient(self.mongo_url)
            await self.mongo_client.admin.command('ping')
            logger.info("✅ MongoDB client connected")
            
            # Initialize PostgreSQL connection for direct SQL operations
            db_url = f"postgresql://postgres:{self.supabase_db_password}@db.{self.supabase_project_ref}.supabase.co:5432/postgres"
            self.pg_conn = psycopg2.connect(db_url)
            logger.info("✅ PostgreSQL connection established")
            
        except Exception as e:
            logger.error(f"❌ Connection initialization failed: {e}")
            raise
    
    async def setup_database_schema(self):
        """Execute the PostgreSQL schema creation"""
        try:
            schema_file = Path('supabase_schema.sql')
            if not schema_file.exists():
                raise FileNotFoundError("Schema file not found")
                
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            with self.pg_conn.cursor() as cursor:
                cursor.execute(schema_sql)
                self.pg_conn.commit()
                
            logger.info("✅ Database schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema creation failed: {e}")
            return False
    
    async def backup_mongodb_data(self):
        """Create backup of MongoDB data"""
        if not self.backup_before_migration:
            logger.info("⏩ Backup skipped (disabled in settings)")
            return True
            
        try:
            backup_dir = Path(f"mongodb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            backup_dir.mkdir(exist_ok=True)
            
            db = self.mongo_client[self.mongo_db_name]
            collections = await db.list_collection_names()
            
            for collection_name in collections:
                collection = db[collection_name]
                documents = []
                
                async for doc in collection.find():
                    # Convert ObjectId and datetime for JSON serialization
                    doc = self._serialize_document(doc)
                    documents.append(doc)
                
                backup_file = backup_dir / f"{collection_name}.json"
                with open(backup_file, 'w') as f:
                    json.dump(documents, f, indent=2, default=str)
                    
                logger.info(f"✅ Backed up {collection_name}: {len(documents)} documents")
            
            logger.info(f"✅ Full backup completed: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
    
    def _serialize_document(self, doc: Dict) -> Dict:
        """Convert MongoDB document to JSON-serializable format"""
        if isinstance(doc, dict):
            result = {}
            for key, value in doc.items():
                if key == '_id':
                    result['id'] = str(value)
                elif isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, dict):
                    result[key] = self._serialize_document(value)
                elif isinstance(value, list):
                    result[key] = [self._serialize_document(item) if isinstance(item, dict) else item for item in value]
                else:
                    result[key] = value
            return result
        return doc
    
    async def migrate_users(self):
        """Migrate users from MongoDB to Supabase Auth + user_profiles"""
        try:
            logger.info("🚀 Starting user migration...")
            
            db = self.mongo_client[self.mongo_db_name]
            users_collection = db['users']
            
            migrated_count = 0
            failed_count = 0
            
            async for user_doc in users_collection.find():
                try:
                    # Create user in Supabase Auth
                    auth_user = None
                    
                    # Check if user has password (not Google OAuth only)
                    if user_doc.get('password_hash'):
                        # Create user with email/password
                        auth_response = self.supabase.auth.admin.create_user({
                            "email": user_doc['email'],
                            "password": "temp_password_123",  # Will be reset
                            "email_confirm": True,
                            "user_metadata": {
                                "first_name": user_doc.get('first_name', ''),
                                "last_name": user_doc.get('last_name', ''),
                                "migrated_from": "mongodb"
                            }
                        })
                        auth_user = auth_response.user
                    else:
                        # Google OAuth user - create without password
                        auth_response = self.supabase.auth.admin.create_user({
                            "email": user_doc['email'],
                            "email_confirm": True,
                            "user_metadata": {
                                "first_name": user_doc.get('first_name', ''),
                                "last_name": user_doc.get('last_name', ''),
                                "google_id": user_doc.get('google_id'),
                                "migrated_from": "mongodb"
                            }
                        })
                        auth_user = auth_response.user
                    
                    if auth_user:
                        # Create user profile
                        profile_data = {
                            "id": auth_user.id,
                            "username": user_doc.get('username'),
                            "first_name": user_doc.get('first_name', ''),
                            "last_name": user_doc.get('last_name', ''),
                            "google_id": user_doc.get('google_id'),
                            "profile_picture": user_doc.get('profile_picture'),
                            "is_active": user_doc.get('is_active', True),
                            "level": user_doc.get('level', 1),
                            "total_points": user_doc.get('total_points', 0),
                            "current_streak": user_doc.get('current_streak', 0),
                            "created_at": user_doc.get('created_at', datetime.now()).isoformat() if isinstance(user_doc.get('created_at'), datetime) else datetime.now().isoformat()
                        }
                        
                        # Insert profile using direct SQL for better control
                        with self.pg_conn.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO public.user_profiles (
                                    id, username, first_name, last_name, google_id, 
                                    profile_picture, is_active, level, total_points, 
                                    current_streak, created_at
                                ) VALUES (
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                )
                            """, (
                                profile_data['id'], profile_data['username'], 
                                profile_data['first_name'], profile_data['last_name'], 
                                profile_data['google_id'], profile_data['profile_picture'], 
                                profile_data['is_active'], profile_data['level'], 
                                profile_data['total_points'], profile_data['current_streak'],
                                profile_data['created_at']
                            ))
                            self.pg_conn.commit()
                        
                        # Store mapping for other collections
                        self._store_user_mapping(user_doc['id'], auth_user.id)
                        
                        migrated_count += 1
                        logger.info(f"✅ Migrated user: {user_doc['email']}")
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"❌ Failed to migrate user {user_doc.get('email', 'unknown')}: {e}")
                    self.migration_stats['errors'].append(f"User migration error: {e}")
            
            logger.info(f"✅ User migration completed: {migrated_count} migrated, {failed_count} failed")
            self.migration_stats['collections_migrated'].append(f"users: {migrated_count}/{migrated_count + failed_count}")
            
            return migrated_count > 0
            
        except Exception as e:
            logger.error(f"❌ User migration failed: {e}")
            return False
    
    def _store_user_mapping(self, old_user_id: str, new_user_id: str):
        """Store user ID mapping for reference during migration"""
        if not hasattr(self, 'user_id_mapping'):
            self.user_id_mapping = {}
        self.user_id_mapping[old_user_id] = new_user_id
    
    async def migrate_collection(self, collection_name: str, table_name: str, transform_func=None):
        """Generic collection migration with transformation function"""
        try:
            logger.info(f"🚀 Migrating {collection_name} to {table_name}...")
            
            db = self.mongo_client[self.mongo_db_name]
            collection = db[collection_name]
            
            migrated_count = 0
            failed_count = 0
            
            async for doc in collection.find():
                try:
                    # Transform document if function provided
                    if transform_func:
                        transformed_doc = transform_func(doc)
                    else:
                        transformed_doc = self._default_transform(doc)
                    
                    if transformed_doc:
                        # Insert into PostgreSQL
                        await self._insert_document(table_name, transformed_doc)
                        migrated_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"❌ Failed to migrate document from {collection_name}: {e}")
                    self.migration_stats['errors'].append(f"{collection_name} migration error: {e}")
            
            logger.info(f"✅ {collection_name} migration completed: {migrated_count} migrated, {failed_count} failed")
            self.migration_stats['collections_migrated'].append(f"{collection_name}: {migrated_count}/{migrated_count + failed_count}")
            
            return migrated_count > 0
            
        except Exception as e:
            logger.error(f"❌ {collection_name} migration failed: {e}")
            return False
    
    def _default_transform(self, doc: Dict) -> Dict:
        """Default document transformation"""
        transformed = {}
        
        for key, value in doc.items():
            if key == '_id':
                transformed['id'] = str(value)
            elif key == 'user_id' and hasattr(self, 'user_id_mapping'):
                # Map old user ID to new Supabase user ID
                transformed['user_id'] = self.user_id_mapping.get(str(value), str(value))
            elif isinstance(value, datetime):
                transformed[key] = value.isoformat()
            elif isinstance(value, list) and key.endswith('_ids'):
                # Handle ID arrays
                transformed[key] = [str(item) for item in value]
            else:
                transformed[key] = value
        
        return transformed
    
    async def _insert_document(self, table_name: str, doc: Dict):
        """Insert document into PostgreSQL table"""
        try:
            columns = list(doc.keys())
            values = list(doc.values())
            placeholders = ', '.join(['%s'] * len(values))
            
            sql = f"INSERT INTO public.{table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            with self.pg_conn.cursor() as cursor:
                cursor.execute(sql, values)
                self.pg_conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Insert failed for table {table_name}: {e}")
            raise
    
    async def run_full_migration(self):
        """Execute complete migration process"""
        try:
            self.migration_stats['started_at'] = datetime.now()
            logger.info("🚀 Starting Aurum Life Migration to Supabase...")
            
            # Step 1: Initialize connections
            await self.initialize_connections()
            
            # Step 2: Setup database schema
            if not await self.setup_database_schema():
                raise Exception("Schema setup failed")
            
            # Step 3: Backup MongoDB data
            if not await self.backup_mongodb_data():
                raise Exception("Backup failed")
            
            # Step 4: Migrate users first (needed for foreign key references)
            if not await self.migrate_users():
                raise Exception("User migration failed")
            
            # Step 5: Migrate core entities in dependency order
            migration_order = [
                ('pillars', 'pillars'),
                ('areas', 'areas'),
                ('projects', 'projects'),
                ('tasks', 'tasks'),
                ('journal_templates', 'journal_templates'),
                ('journal_entries', 'journal_entries'),
                ('resources', 'resources'),
                ('browser_notifications', 'notifications'),
                ('notification_preferences', 'notification_preferences'),
                ('project_templates', 'project_templates'),
                ('user_stats', 'user_stats')
            ]
            
            for mongo_collection, postgres_table in migration_order:
                await self.migrate_collection(mongo_collection, postgres_table)
            
            # Step 6: Migration completed
            self.migration_stats['completed_at'] = datetime.now()
            duration = self.migration_stats['completed_at'] - self.migration_stats['started_at']
            
            logger.info("🎉 Migration completed successfully!")
            logger.info(f"📊 Migration Statistics:")
            logger.info(f"   Duration: {duration}")
            logger.info(f"   Collections: {len(self.migration_stats['collections_migrated'])}")
            logger.info(f"   Errors: {len(self.migration_stats['errors'])}")
            
            # Save migration report
            with open(f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
                json.dump(self.migration_stats, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            self.migration_stats['errors'].append(f"Migration failure: {e}")
            return False
        
        finally:
            # Cleanup connections
            if self.mongo_client:
                self.mongo_client.close()
            if self.pg_conn:
                self.pg_conn.close()

async def main():
    """Main migration entry point"""
    manager = SupabaseMigrationManager()
    success = await manager.run_full_migration()
    
    if success:
        print("✅ Migration completed successfully!")
        exit(0)
    else:
        print("❌ Migration failed!")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())