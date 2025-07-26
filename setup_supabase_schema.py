#!/usr/bin/env python3
"""
Setup Supabase Database Schema
Execute the PostgreSQL schema creation for Aurum Life
"""

import os
import psycopg2
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.supabase')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_schema():
    """Execute the schema setup"""
    try:
        # Database connection details
        project_ref = os.getenv('SUPABASE_PROJECT_REF')
        password = os.getenv('SUPABASE_DB_PASSWORD')
        
        # Try different connection formats
        db_urls = [
            f"postgresql://postgres.{project_ref}:{password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
            f"postgresql://postgres:{password}@{project_ref}.supabase.co:5432/postgres",
            f"postgresql://postgres:{password}@db.{project_ref}.supabase.co:5432/postgres"
        ]
        
        conn = None
        for db_url in db_urls:
            try:
                logger.info(f"🔌 Attempting connection: {db_url.replace(password, '***')}")
                conn = psycopg2.connect(db_url)
                logger.info("✅ Connection successful!")
                break
            except Exception as e:
                logger.warning(f"❌ Connection failed: {e}")
                continue
        
        if not conn:
            raise Exception("All connection attempts failed")
        
        # Read and execute schema
        with open('supabase_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        logger.info("🗃️ Executing schema creation...")
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
            conn.commit()
        
        logger.info("✅ Database schema created successfully!")
        
        # Verify tables were created
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name NOT IN ('migrations', 'schema_migrations')
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            
        logger.info("📋 Created tables:")
        for table in tables:
            logger.info(f"   ✓ {table[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema setup failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_schema()
    if success:
        print("✅ Schema setup completed!")
        exit(0)
    else:
        print("❌ Schema setup failed!")
        exit(1)