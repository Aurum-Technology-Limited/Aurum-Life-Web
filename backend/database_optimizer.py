"""
Database Optimization for Aurum Life MVP v1.1
Adds indexes and optimizations for sub-150ms API response times
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[os.environ.get('DB_NAME', 'aurum_life')]
        logger.info("Connected to MongoDB")
        
    async def create_indexes(self):
        """Create all indexes needed for MVP performance"""
        
        # Pillars indexes
        pillars_indexes = [
            [("user_id", 1), ("sort_order", 1)],
            [("user_id", 1), ("archived", 1), ("sort_order", 1)],
        ]
        
        # Areas indexes
        areas_indexes = [
            [("user_id", 1), ("pillar_id", 1), ("sort_order", 1)],
            [("user_id", 1), ("archived", 1), ("sort_order", 1)],
            [("pillar_id", 1), ("archived", 1)],
        ]
        
        # Projects indexes
        projects_indexes = [
            [("user_id", 1), ("area_id", 1), ("sort_order", 1)],
            [("user_id", 1), ("status", 1), ("sort_order", 1)],
            [("area_id", 1), ("archived", 1), ("status", 1)],
            [("user_id", 1), ("archived", 1), ("deadline", 1)],
        ]
        
        # Tasks indexes - Most critical for performance
        tasks_indexes = [
            [("user_id", 1), ("project_id", 1), ("current_score", -1)],
            [("user_id", 1), ("due_date", 1), ("current_score", -1)],
            [("user_id", 1), ("status", 1), ("current_score", -1)],
            [("project_id", 1), ("completed", 1), ("sort_order", 1)],
            [("user_id", 1), ("completed", 1), ("due_date", 1)],
            # Compound index for Today view
            [("user_id", 1), ("completed", 1), ("due_date", 1), ("current_score", -1)],
        ]
        
        # Users indexes
        users_indexes = [
            [("email", 1)],
            [("username", 1)],
            [("google_id", 1)],
        ]
        
        # Create all indexes
        collections = {
            "pillars": pillars_indexes,
            "areas": areas_indexes,
            "projects": projects_indexes,
            "tasks": tasks_indexes,
            "users": users_indexes,
        }
        
        for collection_name, indexes in collections.items():
            collection = self.db[collection_name]
            for index_spec in indexes:
                try:
                    index_name = await collection.create_index(index_spec)
                    logger.info(f"Created index {index_name} on {collection_name}")
                except Exception as e:
                    logger.error(f"Failed to create index on {collection_name}: {e}")
                    
    async def add_scoring_fields(self):
        """Ensure all tasks have current_score field"""
        tasks_collection = self.db["tasks"]
        
        # Add current_score field to tasks that don't have it
        result = await tasks_collection.update_many(
            {"current_score": {"$exists": False}},
            {"$set": {"current_score": 50.0}}  # Default middle score
        )
        
        logger.info(f"Updated {result.modified_count} tasks with current_score field")
        
    async def optimize_collections(self):
        """Additional collection-level optimizations"""
        
        # Enable collection-level read preference for better performance
        collections = ["pillars", "areas", "projects", "tasks"]
        
        for collection_name in collections:
            try:
                # Compact collections to defragment storage
                result = await self.db.command("compact", collection_name)
                logger.info(f"Compacted {collection_name}: {result}")
            except Exception as e:
                logger.warning(f"Could not compact {collection_name}: {e}")
                
    async def create_materialized_views(self):
        """Create materialized views for complex queries"""
        
        # Create a view for today's tasks (pre-computed)
        today_view_pipeline = [
            {
                "$match": {
                    "completed": False,
                    "$or": [
                        {"due_date": {"$lte": datetime.utcnow()}},
                        {"due_date": None}
                    ]
                }
            },
            {
                "$lookup": {
                    "from": "projects",
                    "localField": "project_id",
                    "foreignField": "id",
                    "as": "project"
                }
            },
            {
                "$unwind": "$project"
            },
            {
                "$lookup": {
                    "from": "areas",
                    "localField": "project.area_id",
                    "foreignField": "id",
                    "as": "area"
                }
            },
            {
                "$unwind": "$area"
            },
            {
                "$project": {
                    "_id": 1,
                    "id": 1,
                    "name": 1,
                    "description": 1,
                    "due_date": 1,
                    "priority": 1,
                    "current_score": 1,
                    "project_name": "$project.name",
                    "area_name": "$area.name",
                    "user_id": 1
                }
            }
        ]
        
        try:
            # Drop existing view if it exists
            await self.db.drop_collection("today_tasks_view")
            
            # Create the view
            await self.db.create_collection(
                "today_tasks_view",
                viewOn="tasks",
                pipeline=today_view_pipeline
            )
            logger.info("Created today_tasks_view materialized view")
        except Exception as e:
            logger.error(f"Failed to create materialized view: {e}")
            
    async def analyze_performance(self):
        """Analyze current query performance"""
        
        # Get index usage stats
        collections = ["pillars", "areas", "projects", "tasks"]
        
        for collection_name in collections:
            collection = self.db[collection_name]
            
            # Get index stats
            index_stats = await collection.aggregate([
                {"$indexStats": {}}
            ]).to_list(None)
            
            logger.info(f"\n{collection_name} Index Usage:")
            for stat in index_stats:
                logger.info(f"  {stat['name']}: {stat.get('accesses', {}).get('ops', 0)} operations")
                
    async def run_optimization(self):
        """Run all optimization tasks"""
        await self.connect()
        
        logger.info("Starting database optimization...")
        
        # Create indexes
        await self.create_indexes()
        
        # Add missing fields
        await self.add_scoring_fields()
        
        # Optimize collections
        await self.optimize_collections()
        
        # Create materialized views
        await self.create_materialized_views()
        
        # Analyze performance
        await self.analyze_performance()
        
        logger.info("Database optimization complete!")
        
        if self.client:
            self.client.close()

# Run optimization
if __name__ == "__main__":
    optimizer = DatabaseOptimizer()
    asyncio.run(optimizer.run_optimization())