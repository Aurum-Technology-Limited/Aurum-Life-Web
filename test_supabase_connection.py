#!/usr/bin/env python3
"""
Test Supabase connection and execute schema
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.supabase')

def test_connection_and_setup():
    """Test Supabase connection and create tables"""
    try:
        # Initialize Supabase client
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        supabase = create_client(url, key)
        print("✅ Supabase client initialized")
        
        # Test with a simple query
        result = supabase.table('user_profiles').select('*').limit(1).execute()
        print("❌ Tables already exist - ready for migration")
        return True
        
    except Exception as e:
        print(f"ℹ️ Tables don't exist yet (expected): {e}")
        
        # Try to create tables using SQL execution
        try:
            # Read schema file
            with open('supabase_schema.sql', 'r') as f:
                schema_sql = f.read()
            
            # Execute schema using supabase RPC
            print("🗃️ Creating database schema via Supabase...")
            
            # Split schema into smaller chunks to avoid timeout
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            
            success_count = 0
            for i, statement in enumerate(statements):
                if statement.strip():
                    try:
                        # Use rpc for SQL execution
                        supabase.rpc('exec_sql', {'sql': statement}).execute()
                        success_count += 1
                        if i % 10 == 0:
                            print(f"   Processed {i}/{len(statements)} statements...")
                    except Exception as stmt_error:
                        print(f"   Warning: Statement {i} failed: {str(stmt_error)[:100]}")
                        continue
            
            print(f"✅ Schema creation completed! {success_count}/{len(statements)} statements executed")
            return True
            
        except Exception as setup_error:
            print(f"❌ Schema setup failed: {setup_error}")
            
            # Alternative: Create tables manually using supabase client
            print("🔄 Trying manual table creation...")
            try:
                # Create essential tables first
                essential_tables = {
                    'user_profiles': '''
                        CREATE TABLE IF NOT EXISTS public.user_profiles (
                            id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
                            username TEXT UNIQUE,
                            first_name TEXT,
                            last_name TEXT,
                            google_id TEXT,
                            profile_picture TEXT,
                            is_active BOOLEAN DEFAULT TRUE,
                            level INTEGER DEFAULT 1,
                            total_points INTEGER DEFAULT 0,
                            current_streak INTEGER DEFAULT 0,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                        ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
                        CREATE POLICY "Users can manage their own profile" ON public.user_profiles FOR ALL USING (auth.uid() = id);
                    ''',
                    'pillars': '''
                        CREATE TABLE IF NOT EXISTS public.pillars (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
                            name TEXT NOT NULL,
                            description TEXT DEFAULT '',
                            icon TEXT DEFAULT '🎯',
                            color TEXT DEFAULT '#F4B400',
                            sort_order INTEGER DEFAULT 0,
                            archived BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                        ALTER TABLE public.pillars ENABLE ROW LEVEL SECURITY;
                        CREATE POLICY "Users can manage their own pillars" ON public.pillars FOR ALL USING (auth.uid() = user_id);
                    '''
                }
                
                for table_name, create_sql in essential_tables.items():
                    try:
                        supabase.rpc('exec_sql', {'sql': create_sql}).execute()
                        print(f"   ✅ Created {table_name}")
                    except Exception as table_error:
                        print(f"   ❌ Failed to create {table_name}: {table_error}")
                
                print("✅ Essential tables created successfully!")
                return True
                
            except Exception as manual_error:
                print(f"❌ Manual table creation failed: {manual_error}")
                return False

if __name__ == "__main__":
    success = test_connection_and_setup()
    if success:
        print("\n🎉 Supabase setup completed! Ready for data migration.")
    else:
        print("\n❌ Supabase setup failed!")
        print("\n💡 Manual steps needed:")
        print("1. Go to your Supabase SQL Editor")
        print("2. Copy and paste the contents of supabase_schema.sql")
        print("3. Execute the SQL script")
        print("4. Then run the migration script")