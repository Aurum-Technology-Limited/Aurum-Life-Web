#!/usr/bin/env python3
"""
Targeted User Data Migration
Migrates all data for a specific user from MongoDB to Supabase
"""

import os
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any

# MongoDB and Supabase imports
from motor.motor_asyncio import AsyncIOMotorClient
from supabase import create_client, Client

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

class UserDataMigrator:
    """Migrate all data for a specific user from MongoDB to Supabase"""
    
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
    
    def convert_mongo_doc(self, doc: Dict) -> Dict:
        """Convert MongoDB document to Supabase format"""
        if not doc:
            return doc
            
        # Convert ObjectId and datetime fields
        for key, value in doc.items():
            if key == '_id':
                continue  # Skip MongoDB _id
            elif isinstance(value, datetime):
                doc[key] = value.isoformat()
        
        return doc
    
    async def migrate_user_pillars(self, user_id: str, user_email: str) -> int:
        """Migrate user's pillars"""
        try:
            logger.info(f"🏛️ Migrating pillars for {user_email}...")
            
            db = self.mongo_client[self.mongo_db_name]
            pillars = await db.pillars.find({"user_id": user_id}).to_list(length=None)
            
            migrated_count = 0
            for pillar in pillars:
                try:
                    pillar_data = self.convert_mongo_doc(pillar)
                    # Remove MongoDB _id
                    if '_id' in pillar_data:
                        del pillar_data['_id']
                    
                    # Ensure required fields
                    if 'created_at' not in pillar_data:
                        pillar_data['created_at'] = datetime.utcnow().isoformat()
                    if 'updated_at' not in pillar_data:
                        pillar_data['updated_at'] = datetime.utcnow().isoformat()
                    
                    result = self.supabase.table('pillars').insert(pillar_data).execute()
                    if result.data:
                        migrated_count += 1
                        logger.info(f"  ✅ Pillar: {pillar_data.get('name', 'Unknown')}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Failed to migrate pillar {pillar.get('name', 'Unknown')}: {e}")
            
            logger.info(f"✅ Migrated {migrated_count} pillars")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Pillar migration failed: {e}")
            return 0
    
    async def migrate_user_areas(self, user_id: str, user_email: str) -> int:
        """Migrate user's areas"""
        try:
            logger.info(f"🏗️ Migrating areas for {user_email}...")
            
            db = self.mongo_client[self.mongo_db_name]
            areas = await db.areas.find({"user_id": user_id}).to_list(length=None)
            
            migrated_count = 0
            for area in areas:
                try:
                    area_data = self.convert_mongo_doc(area)
                    # Remove MongoDB _id
                    if '_id' in area_data:
                        del area_data['_id']
                    
                    # Ensure required fields
                    if 'created_at' not in area_data:
                        area_data['created_at'] = datetime.utcnow().isoformat()
                    if 'updated_at' not in area_data:
                        area_data['updated_at'] = datetime.utcnow().isoformat()
                    
                    result = self.supabase.table('areas').insert(area_data).execute()
                    if result.data:
                        migrated_count += 1
                        logger.info(f"  ✅ Area: {area_data.get('name', 'Unknown')}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Failed to migrate area {area.get('name', 'Unknown')}: {e}")
            
            logger.info(f"✅ Migrated {migrated_count} areas")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Area migration failed: {e}")
            return 0
    
    async def migrate_user_projects(self, user_id: str, user_email: str) -> int:
        """Migrate user's projects"""
        try:
            logger.info(f"📂 Migrating projects for {user_email}...")
            
            db = self.mongo_client[self.mongo_db_name]
            projects = await db.projects.find({"user_id": user_id}).to_list(length=None)
            
            migrated_count = 0
            for project in projects:
                try:
                    project_data = self.convert_mongo_doc(project)
                    # Remove MongoDB _id
                    if '_id' in project_data:
                        del project_data['_id']
                    
                    # Ensure required fields
                    if 'created_at' not in project_data:
                        project_data['created_at'] = datetime.utcnow().isoformat()
                    if 'updated_at' not in project_data:
                        project_data['updated_at'] = datetime.utcnow().isoformat()
                    
                    result = self.supabase.table('projects').insert(project_data).execute()
                    if result.data:
                        migrated_count += 1
                        logger.info(f"  ✅ Project: {project_data.get('name', 'Unknown')}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Failed to migrate project {project.get('name', 'Unknown')}: {e}")
            
            logger.info(f"✅ Migrated {migrated_count} projects")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Project migration failed: {e}")
            return 0
    
    async def migrate_user_tasks(self, user_id: str, user_email: str) -> int:
        """Migrate user's tasks"""
        try:
            logger.info(f"📝 Migrating tasks for {user_email}...")
            
            db = self.mongo_client[self.mongo_db_name]
            tasks = await db.tasks.find({"user_id": user_id}).to_list(length=None)
            
            migrated_count = 0
            for task in tasks:
                try:
                    task_data = self.convert_mongo_doc(task)
                    # Remove MongoDB _id
                    if '_id' in task_data:
                        del task_data['_id']
                    
                    # Ensure required fields
                    if 'created_at' not in task_data:
                        task_data['created_at'] = datetime.utcnow().isoformat()
                    if 'updated_at' not in task_data:
                        task_data['updated_at'] = datetime.utcnow().isoformat()
                    
                    result = self.supabase.table('tasks').insert(task_data).execute()
                    if result.data:
                        migrated_count += 1
                        logger.info(f"  ✅ Task: {task_data.get('title', 'Unknown')}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Failed to migrate task {task.get('title', 'Unknown')}: {e}")
            
            logger.info(f"✅ Migrated {migrated_count} tasks")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Task migration failed: {e}")
            return 0
    
    async def migrate_user_data(self, user_email: str):
        """Migrate all data for a specific user"""
        try:
            logger.info(f"🚀 Starting migration for user: {user_email}")
            logger.info("=" * 60)
            
            # Step 1: Initialize connections
            await self.initialize_connections()
            
            # Step 2: Get user ID from MongoDB
            db = self.mongo_client[self.mongo_db_name]
            user_doc = await db.users.find_one({"email": user_email})
            
            if not user_doc:
                logger.error(f"❌ User {user_email} not found in MongoDB")
                return False
            
            user_id = user_doc.get('id')
            logger.info(f"👤 Found user: {user_email} (ID: {user_id})")
            
            # Step 3: Migrate data in order (pillars -> areas -> projects -> tasks)
            pillar_count = await self.migrate_user_pillars(user_id, user_email)
            area_count = await self.migrate_user_areas(user_id, user_email)
            project_count = await self.migrate_user_projects(user_id, user_email)
            task_count = await self.migrate_user_tasks(user_id, user_email)
            
            # Step 4: Summary
            total_items = pillar_count + area_count + project_count + task_count
            
            logger.info("=" * 60)
            logger.info(f"✅ Migration completed for {user_email}!")
            logger.info(f"""
📊 Migration Summary:
   - Pillars: {pillar_count}
   - Areas: {area_count}  
   - Projects: {project_count}
   - Tasks: {task_count}
   - Total: {total_items} items migrated
            """)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ User migration failed: {e}")
            return False
            
        finally:
            if self.mongo_client:
                self.mongo_client.close()

async def main():
    """Run the targeted user migration"""
    user_email = "marc.alleyne@gmail.com"
    
    migrator = UserDataMigrator()
    success = await migrator.migrate_user_data(user_email)
    
    if success:
        print(f"\n🎉 Successfully migrated all data for {user_email}!")
        print("🔑 User can now see their pillars, areas, projects, and tasks in the application.")
        return True
    else:
        print(f"\n❌ Migration failed for {user_email}. Check logs above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())