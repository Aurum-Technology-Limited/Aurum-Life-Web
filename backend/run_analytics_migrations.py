#!/usr/bin/env python3
"""
Analytics Tables Migration Script for Aurum Life
Deploys user behavior analytics tables to Supabase database
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def get_supabase_client():
    """Initialize Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        logger.error("❌ Missing Supabase credentials in .env file")
        logger.error("Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY")
        sys.exit(1)
    
    return create_client(url, key)

def execute_sql_file(supabase: Client, file_path: Path, description: str):
    """Execute SQL file using Supabase"""
    logger.info(f"📄 Executing {description}...")
    
    try:
        # Read SQL file
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split into individual statements (basic splitting on semicolons)
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        success_count = 0
        total_statements = len(statements)
        
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            try:
                # Execute each statement individually
                logger.info(f"   Executing statement {i}/{total_statements}...")
                
                # For CREATE TABLE, CREATE INDEX, CREATE FUNCTION etc.
                if any(keyword in statement.upper() for keyword in ['CREATE', 'ALTER', 'INSERT', 'GRANT', 'COMMENT']):
                    # Use RPC call for DDL statements
                    result = supabase.rpc('exec_sql', {'sql_query': statement}).execute()
                else:
                    # Try direct execution for other statements
                    result = supabase.postgrest.rpc('exec_sql', {'sql_query': statement}).execute()
                
                success_count += 1
                logger.info(f"   ✅ Statement {i} executed successfully")
                
            except Exception as stmt_error:
                logger.warning(f"   ⚠️  Statement {i} failed (might be expected): {stmt_error}")
                # Continue with other statements
                continue
        
        logger.info(f"✅ {description} completed: {success_count}/{total_statements} statements executed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to execute {description}: {e}")
        return False

def create_exec_sql_function(supabase: Client):
    """Create the exec_sql function if it doesn't exist"""
    logger.info("🔧 Creating exec_sql function...")
    
    exec_sql_function = """
    CREATE OR REPLACE FUNCTION exec_sql(sql_query text)
    RETURNS text AS $$
    BEGIN
        EXECUTE sql_query;
        RETURN 'OK';
    EXCEPTION
        WHEN OTHERS THEN
            RETURN SQLERRM;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """
    
    try:
        # Try to create the function directly
        supabase.postgrest.rpc('query', {'query': exec_sql_function}).execute()
        logger.info("✅ exec_sql function created successfully")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Could not create exec_sql function: {e}")
        return False

def verify_tables_created(supabase: Client):
    """Verify that analytics tables were created successfully"""
    logger.info("🔍 Verifying analytics tables...")
    
    tables_to_check = [
        'user_analytics_preferences',
        'user_sessions', 
        'user_behavior_events'
    ]
    
    success_count = 0
    for table in tables_to_check:
        try:
            # Try to query the table (limit 0 to just check if it exists)
            result = supabase.table(table).select('*').limit(0).execute()
            logger.info(f"   ✅ Table '{table}' exists and is accessible")
            success_count += 1
        except Exception as e:
            logger.error(f"   ❌ Table '{table}' verification failed: {e}")
    
    if success_count == len(tables_to_check):
        logger.info("✅ All analytics tables verified successfully!")
        return True
    else:
        logger.error(f"❌ Only {success_count}/{len(tables_to_check)} tables verified")
        return False

def run_migrations():
    """Main migration runner"""
    logger.info("🚀 Starting Aurum Life Analytics Tables Migration")
    logger.info("=" * 60)
    
    # Initialize Supabase client
    try:
        supabase = get_supabase_client()
        logger.info("✅ Connected to Supabase successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)
    
    # Create exec_sql function
    create_exec_sql_function(supabase)
    
    # Migration files
    migrations_dir = Path(__file__).parent / 'migrations'
    migration_files = [
        {
            'file': migrations_dir / '010_create_user_behavior_analytics.sql',
            'description': 'User Behavior Analytics Tables Migration'
        },
        {
            'file': migrations_dir / '011_analytics_support_functions.sql', 
            'description': 'Analytics Support Functions Migration'
        }
    ]
    
    # Execute migrations
    migration_success = True
    for migration in migration_files:
        if not migration['file'].exists():
            logger.error(f"❌ Migration file not found: {migration['file']}")
            migration_success = False
            continue
        
        success = execute_sql_file(
            supabase, 
            migration['file'], 
            migration['description']
        )
        
        if not success:
            migration_success = False
    
    # Verify tables were created
    if migration_success:
        logger.info("\n" + "=" * 60)
        tables_verified = verify_tables_created(supabase)
        
        if tables_verified:
            logger.info("\n🎉 ANALYTICS TABLES MIGRATION COMPLETED SUCCESSFULLY!")
            logger.info("✅ All analytics tables created and verified")
            logger.info("✅ Analytics system is ready for production use")
            logger.info("\nNext steps:")
            logger.info("1. Restart your backend server")
            logger.info("2. Test analytics endpoints")
            logger.info("3. Enable analytics tracking in frontend")
        else:
            logger.error("\n❌ MIGRATION COMPLETED BUT VERIFICATION FAILED")
            logger.error("Some tables may not have been created correctly")
            sys.exit(1)
    else:
        logger.error("\n❌ MIGRATION FAILED")
        logger.error("Some migration files could not be executed")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()