#!/usr/bin/env python3
"""
Add users table to Supabase programmatically
"""

from backend.supabase_client import supabase_manager
import asyncio

async def add_users_table():
    """Add users table to Supabase"""
    try:
        print("🔧 Adding users table to Supabase...")
        
        supabase = supabase_manager.get_client()
        
        # The SQL for creating users table
        create_users_table_sql = """
        CREATE TABLE IF NOT EXISTS public.users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username TEXT UNIQUE,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT DEFAULT '',
            last_name TEXT DEFAULT '',
            password_hash TEXT,
            google_id TEXT,
            profile_picture TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            level INTEGER DEFAULT 1,
            total_points INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Enable RLS
        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
        
        -- RLS Policy
        DROP POLICY IF EXISTS "Users can manage their own data" ON public.users;
        CREATE POLICY "Users can manage their own data" ON public.users FOR ALL USING (true);
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
        CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
        """
        
        # Use RPC to execute SQL
        try:
            result = supabase.rpc('exec_sql', {'sql': create_users_table_sql}).execute()
            print("✅ Users table created successfully!")
            return True
        except Exception as rpc_error:
            print(f"❌ RPC failed: {rpc_error}")
            print("ℹ️ This is expected - Supabase restricts SQL execution via RPC for security")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_users_table_exists():
    """Test if users table exists"""
    try:
        supabase = supabase_manager.get_client()
        
        # Try to query users table
        result = supabase.table('users').select('id').limit(1).execute()
        print("✅ Users table exists and is accessible!")
        return True
        
    except Exception as e:
        if "relation \"public.users\" does not exist" in str(e):
            print("❌ Users table does not exist")
            return False
        else:
            print(f"❌ Error accessing users table: {e}")
            return False

async def main():
    """Main function"""
    print("🔍 Testing Supabase users table status...")
    print("=" * 50)
    
    # Test if table exists
    exists = await test_users_table_exists()
    
    if not exists:
        print("\n🔧 Attempting to create users table...")
        success = await add_users_table()
        
        if success:
            print("✅ Table creation completed!")
        else:
            print("❌ Programmatic table creation failed")
            print("\n📋 MANUAL STEPS REQUIRED:")
            print("1. Go to Supabase Dashboard → SQL Editor")
            print("2. Execute the SQL from /app/add_users_table.sql")
            print("3. Re-run this test")
    else:
        print("✅ Users table already exists!")
    
    return exists

if __name__ == "__main__":
    asyncio.run(main())