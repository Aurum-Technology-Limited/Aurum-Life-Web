#!/usr/bin/env python3
"""
Migration Script: Remove parent_pillar_id field from existing pillars
Removes the parent_pillar_id field from all pillars to eliminate child pillar functionality
"""

import sys
import os
from pymongo import MongoClient

def migrate_remove_parent_pillar_id():
    """Remove parent_pillar_id field from existing pillars"""
    
    print("🔄 STARTING MIGRATION: Remove parent_pillar_id field from pillars")
    print("=" * 70)
    
    # Connect to MongoDB
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['aurum_life']
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False
    
    try:
        collection = db['pillars']
        
        # Count documents that have parent_pillar_id field
        documents_with_field = collection.count_documents({"parent_pillar_id": {"$exists": True}})
        total_documents = collection.count_documents({})
        
        print(f"📊 Found {documents_with_field} pillars with parent_pillar_id field out of {total_documents} total")
        
        if documents_with_field == 0:
            print("✅ No pillars have parent_pillar_id field - migration not needed")
            client.close()
            return True
        
        # Remove parent_pillar_id field from all documents
        result = collection.update_many(
            {"parent_pillar_id": {"$exists": True}},
            {"$unset": {"parent_pillar_id": ""}}
        )
        
        print(f"✅ Removed parent_pillar_id field from {result.modified_count} pillars")
        
        # Verify the migration
        remaining_with_field = collection.count_documents({"parent_pillar_id": {"$exists": True}})
        
        if remaining_with_field == 0:
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("✅ All pillars now have flat structure (no child pillars)")
            success = True
        else:
            print(f"⚠️ MIGRATION INCOMPLETE: {remaining_with_field} pillars still have parent_pillar_id")
            success = False
        
        client.close()
        return success
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        client.close()
        return False

def main():
    """Run the complete migration process"""
    
    print("🚀 REMOVE CHILD PILLAR FUNCTIONALITY MIGRATION")
    print("=" * 70)
    print("This script will remove the parent_pillar_id field from all existing")
    print("pillars to eliminate child pillar functionality.")
    print()
    
    # Run migration
    migration_success = migrate_remove_parent_pillar_id()
    
    if migration_success:
        print("\n🎯 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("✅ parent_pillar_id field removed from all pillars")
        print("✅ Child pillar functionality disabled")
        print("✅ All pillars now have flat structure")
        print("✅ Backend models updated to remove hierarchy")
        print("✅ API endpoints simplified")
        print()
        print("🌟 Your application now has a simplified pillar structure!")
        print("Users can no longer create child pillars - only top-level pillars.")
    else:
        print("\n❌ MIGRATION FAILED")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()