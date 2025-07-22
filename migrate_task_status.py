#!/usr/bin/env python3
"""
Task Status Migration Script
Migrates old task status values to new enum values.

Old values -> New values:
- 'not_started' -> 'todo'
- 'on_hold' -> 'todo' (if any exist)

This resolves the Pydantic validation error:
"Input should be 'todo', 'in_progress', 'review' or 'completed'"
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# Database configuration (same as backend)
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = 'test_database'

async def migrate_task_status():
    """Migrate task status values from old enum to new enum values"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    tasks_collection = db.tasks
    
    print("=== Task Status Migration ===")
    print(f"Database: {DB_NAME}")
    print(f"Collection: tasks")
    
    # Check current status distribution
    print("\n1. Current status distribution:")
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    async for result in tasks_collection.aggregate(pipeline):
        print(f"   {result['_id']}: {result['count']} tasks")
    
    # Count records that need migration
    old_status_query = {"status": {"$in": ["not_started", "on_hold"]}}
    old_count = await tasks_collection.count_documents(old_status_query)
    print(f"\n2. Records to migrate: {old_count}")
    
    if old_count == 0:
        print("✅ No migration needed - all tasks have valid status values")
        return
    
    # Migration 1: not_started -> todo
    not_started_count = await tasks_collection.count_documents({"status": "not_started"})
    if not_started_count > 0:
        print(f"\n3. Migrating {not_started_count} tasks: 'not_started' -> 'todo'")
        result = await tasks_collection.update_many(
            {"status": "not_started"},
            {"$set": {"status": "todo", "kanban_column": "to_do"}}
        )
        print(f"   ✅ Updated {result.modified_count} records")
    
    # Migration 2: on_hold -> todo (if any exist)
    on_hold_count = await tasks_collection.count_documents({"status": "on_hold"})
    if on_hold_count > 0:
        print(f"\n4. Migrating {on_hold_count} tasks: 'on_hold' -> 'todo'")
        result = await tasks_collection.update_many(
            {"status": "on_hold"},
            {"$set": {"status": "todo", "kanban_column": "to_do"}}
        )
        print(f"   ✅ Updated {result.modified_count} records")
    
    # Verification: Check final status distribution
    print("\n5. Final status distribution:")
    async for result in tasks_collection.aggregate(pipeline):
        print(f"   {result['_id']}: {result['count']} tasks")
    
    # Final validation check
    remaining_old = await tasks_collection.count_documents(old_status_query)
    if remaining_old == 0:
        print(f"\n✅ Migration completed successfully!")
        print(f"✅ All tasks now have valid status values")
    else:
        print(f"\n❌ Migration incomplete - {remaining_old} tasks still have old status values")
    
    client.close()

def migrate_task_status_sync():
    """Synchronous version using pymongo directly"""
    
    # Connect to MongoDB
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    tasks_collection = db.tasks
    
    print("=== Task Status Migration (Sync) ===")
    print(f"Database: {DB_NAME}")
    print(f"Collection: tasks")
    
    # Check current status distribution
    print("\n1. Current status distribution:")
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    for result in tasks_collection.aggregate(pipeline):
        print(f"   {result['_id']}: {result['count']} tasks")
    
    # Count records that need migration
    old_status_query = {"status": {"$in": ["not_started", "on_hold"]}}
    old_count = tasks_collection.count_documents(old_status_query)
    print(f"\n2. Records to migrate: {old_count}")
    
    if old_count == 0:
        print("✅ No migration needed - all tasks have valid status values")
        return
    
    # Migration 1: not_started -> todo
    not_started_count = tasks_collection.count_documents({"status": "not_started"})
    if not_started_count > 0:
        print(f"\n3. Migrating {not_started_count} tasks: 'not_started' -> 'todo'")
        result = tasks_collection.update_many(
            {"status": "not_started"},
            {"$set": {"status": "todo", "kanban_column": "to_do"}}
        )
        print(f"   ✅ Updated {result.modified_count} records")
    
    # Migration 2: on_hold -> todo (if any exist)
    on_hold_count = tasks_collection.count_documents({"status": "on_hold"})
    if on_hold_count > 0:
        print(f"\n4. Migrating {on_hold_count} tasks: 'on_hold' -> 'todo'")
        result = tasks_collection.update_many(
            {"status": "on_hold"},
            {"$set": {"status": "todo", "kanban_column": "to_do"}}
        )
        print(f"   ✅ Updated {result.modified_count} records")
    
    # Verification: Check final status distribution
    print("\n5. Final status distribution:")
    for result in tasks_collection.aggregate(pipeline):
        print(f"   {result['_id']}: {result['count']} tasks")
    
    # Final validation check
    remaining_old = tasks_collection.count_documents(old_status_query)
    if remaining_old == 0:
        print(f"\n✅ Migration completed successfully!")
        print(f"✅ All tasks now have valid status values")
    else:
        print(f"\n❌ Migration incomplete - {remaining_old} tasks still have old status values")
    
    client.close()

if __name__ == "__main__":
    # Try async first, fallback to sync if needed
    try:
        asyncio.run(migrate_task_status())
    except Exception as e:
        print(f"Async migration failed: {e}")
        print("Falling back to sync migration...")
        migrate_task_status_sync()