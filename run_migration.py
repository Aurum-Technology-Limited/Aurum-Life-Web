#!/usr/bin/env python3
"""
Execute Supabase Migration
"""

import asyncio
from supabase_migration_manager import SupabaseMigrationManager

async def main():
    """Run the complete migration"""
    print("🚀 Starting Aurum Life Migration to Supabase...")
    print("=" * 60)
    
    manager = SupabaseMigrationManager()
    success = await manager.run_full_migration()
    
    print("=" * 60)
    if success:
        print("✅ Migration completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Update backend to use Supabase client")
        print("2. Update frontend authentication")
        print("3. Configure Google OAuth")
        print("4. Test application functionality")
        exit(0)
    else:
        print("❌ Migration failed! Check migration.log for details")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())