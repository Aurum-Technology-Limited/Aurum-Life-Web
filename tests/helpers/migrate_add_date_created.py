#!/usr/bin/env python3
"""
Migration Script: Add date_created field to existing documents
Adds date_created field to all pillars, areas, projects, and tasks in the database
"""

import sys
import os
from datetime import datetime
from pymongo import MongoClient

# Add the backend directory to the path
sys.path.append('/app/backend')

def migrate_add_date_created():
    """Add date_created field to existing documents"""
    
    print("🔄 STARTING MIGRATION: Add date_created field")
    print("=" * 60)
    
    # Connect to MongoDB
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['aurum_life']
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False
    
    collections_to_migrate = ['pillars', 'areas', 'projects', 'tasks']
    migration_results = {}
    
    for collection_name in collections_to_migrate:
        print(f"\n📋 Migrating collection: {collection_name}")
        print("-" * 40)
        
        try:
            collection = db[collection_name]
            
            # Count documents that don't have date_created field
            documents_without_field = collection.count_documents({"date_created": {"$exists": False}})
            
            if documents_without_field == 0:
                print(f"✅ All documents in {collection_name} already have date_created field")
                migration_results[collection_name] = {
                    'migrated': 0,
                    'total': collection.count_documents({}),
                    'status': 'up_to_date'
                }
                continue
            
            print(f"📊 Found {documents_without_field} documents without date_created field")
            
            # Use simple update_many approach instead of bulk_write
            # For existing documents, we'll use created_at if available, otherwise current time
            updated_with_created_at = collection.update_many(
                {
                    "date_created": {"$exists": False},
                    "created_at": {"$exists": True}
                },
                [{"$set": {"date_created": "$created_at"}}]
            )
            
            # For documents without created_at, use current time
            updated_with_current_time = collection.update_many(
                {
                    "date_created": {"$exists": False},
                    "created_at": {"$exists": False}
                },
                {"$set": {"date_created": datetime.utcnow()}}
            )
            
            total_updated = updated_with_created_at.modified_count + updated_with_current_time.modified_count
            
            print(f"✅ Updated {total_updated} documents in {collection_name}")
            print(f"   - {updated_with_created_at.modified_count} used existing created_at")
            print(f"   - {updated_with_current_time.modified_count} used current time")
            
            migration_results[collection_name] = {
                'migrated': total_updated,
                'total': collection.count_documents({}),
                'status': 'migrated'
            }
        
        except Exception as e:
            print(f"❌ Error migrating {collection_name}: {e}")
            migration_results[collection_name] = {
                'migrated': 0,
                'total': 0,
                'status': 'error',
                'error': str(e)
            }
    
    # Print migration summary
    print("\n🎉 MIGRATION SUMMARY")
    print("=" * 60)
    
    total_migrated = 0
    total_documents = 0
    
    for collection_name, result in migration_results.items():
        status_icon = {
            'migrated': '✅',
            'up_to_date': '✅',
            'no_updates_needed': 'ℹ️',
            'error': '❌'
        }.get(result['status'], '❓')
        
        print(f"{status_icon} {collection_name:<10}: {result['migrated']:>3} migrated / {result['total']:>3} total")
        total_migrated += result['migrated']
        total_documents += result['total']
    
    print("-" * 60)
    print(f"📊 TOTAL: {total_migrated} documents migrated out of {total_documents} total")
    
    if total_migrated > 0:
        print("\n🎯 MIGRATION COMPLETED SUCCESSFULLY!")
        print("All pillars, areas, projects, and tasks now have date_created field")
    else:
        print("\n✨ DATABASE ALREADY UP TO DATE!")
        print("All documents already had the date_created field")
    
    client.close()
    return True

def verify_migration():
    """Verify that all documents now have the date_created field"""
    
    print("\n🔍 VERIFYING MIGRATION RESULTS")
    print("=" * 60)
    
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['aurum_life']
        
        collections_to_check = ['pillars', 'areas', 'projects', 'tasks']
        all_good = True
        
        for collection_name in collections_to_check:
            collection = db[collection_name]
            
            total_docs = collection.count_documents({})
            docs_with_date = collection.count_documents({"date_created": {"$exists": True}})
            docs_without_date = collection.count_documents({"date_created": {"$exists": False}})
            
            if docs_without_date == 0:
                print(f"✅ {collection_name:<10}: {docs_with_date}/{total_docs} have date_created")
            else:
                print(f"❌ {collection_name:<10}: {docs_without_date} documents still missing date_created")
                all_good = False
        
        if all_good:
            print("\n🎉 VERIFICATION PASSED!")
            print("All documents now have the date_created field")
        else:
            print("\n⚠️ VERIFICATION FAILED!")
            print("Some documents are still missing the date_created field")
        
        client.close()
        return all_good
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    """Run the complete migration process"""
    
    print("🚀 DATE_CREATED FIELD MIGRATION")
    print("=" * 70)
    print("This script will add the date_created field to all existing")
    print("pillars, areas, projects, and tasks in the database.")
    print()
    
    # Run migration
    migration_success = migrate_add_date_created()
    
    if migration_success:
        # Verify migration
        verification_success = verify_migration()
        
        if verification_success:
            print("\n🎯 MIGRATION AND VERIFICATION COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print("✅ All pillars, areas, projects, and tasks now have date_created field")
            print("✅ New documents will automatically include date_created")
            print("✅ Frontend can now display creation dates")
            print("✅ API responses include date_created information")
            print()
            print("🌟 Your application is now ready with enhanced date tracking!")
        else:
            print("\n⚠️ MIGRATION COMPLETED BUT VERIFICATION FAILED")
            print("Please check the database manually")
    else:
        print("\n❌ MIGRATION FAILED")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()