#!/usr/bin/env python3
"""
Fix User Auth Migration Issue

This script fixes the issue where users exist in the legacy 'users' table
but not properly in Supabase auth.users, causing foreign key constraint violations
when trying to create pillars, areas, projects, etc.

The issue: User exists in 'users' table with ID ea5d3da8-41d2-4c73-842a-094224cf06c1
but auth.users has a different record for the same email, causing FK violations.
"""

import os
import asyncio
import logging
from supabase_client import get_supabase_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_user_auth_migration():
    """Fix the auth migration issue for the test user"""
    supabase = get_supabase_client()
    
    # The problematic user from our logs
    legacy_user_id = "ea5d3da8-41d2-4c73-842a-094224cf06c1"
    email = "marc.alleyne@aurumtechnologyltd.com"
    
    try:
        logger.info(f"🔍 Checking legacy user: {email} (ID: {legacy_user_id})")
        
        # 1. Get the legacy user data
        legacy_user_result = supabase.table('users').select('*').eq('id', legacy_user_id).execute()
        if not legacy_user_result.data:
            logger.error(f"❌ Legacy user not found in users table")
            return False
            
        legacy_user = legacy_user_result.data[0]
        logger.info(f"✅ Found legacy user: {legacy_user}")
        
        # 2. Check if user exists in auth.users
        try:
            auth_users = supabase.auth.admin.list_users()
            existing_auth_user = None
            
            for user in auth_users:
                if user.email == email:
                    existing_auth_user = user
                    break
                    
            if existing_auth_user:
                logger.info(f"✅ Found existing auth user: {existing_auth_user.id}")
                
                # Check if IDs match
                if existing_auth_user.id == legacy_user_id:
                    logger.info(f"✅ IDs already match - no migration needed")
                    return True
                else:
                    logger.warning(f"⚠️ ID mismatch: auth.users ID = {existing_auth_user.id}, users table ID = {legacy_user_id}")
                    
                    # Option 1: Update all references to use the auth.users ID
                    logger.info(f"🔄 Updating references to use auth.users ID: {existing_auth_user.id}")
                    
                    # Update the users table
                    update_result = supabase.table('users').update({
                        'id': existing_auth_user.id
                    }).eq('id', legacy_user_id).execute()
                    
                    if update_result.data:
                        logger.info(f"✅ Updated users table ID from {legacy_user_id} to {existing_auth_user.id}")
                        
                        # Create user_profiles entry if it doesn't exist
                        try:
                            profile_data = {
                                'id': existing_auth_user.id,
                                'username': legacy_user.get('username', ''),
                                'first_name': legacy_user.get('first_name', ''),
                                'last_name': legacy_user.get('last_name', ''),
                                'is_active': legacy_user.get('is_active', True)
                            }
                            
                            supabase.table('user_profiles').upsert(profile_data).execute()
                            logger.info(f"✅ Created/updated user_profiles entry")
                            
                        except Exception as profile_error:
                            logger.warning(f"⚠️ Could not create user_profiles entry: {profile_error}")
                            
                        return True
                    else:
                        logger.error(f"❌ Failed to update users table")
                        return False
            else:
                logger.info(f"🔧 No auth user found - creating new one")
                
                # Create auth user with the same ID as legacy user
                try:
                    auth_response = supabase.auth.admin.create_user({
                        "email": email,
                        "user_metadata": {
                            "username": legacy_user.get('username', ''),
                            "first_name": legacy_user.get('first_name', ''),
                            "last_name": legacy_user.get('last_name', ''),
                            "migrated_from_legacy": True
                        },
                        "email_confirm": True
                    })
                    
                    if auth_response and auth_response.user:
                        new_auth_id = auth_response.user.id
                        logger.info(f"✅ Created auth user with ID: {new_auth_id}")
                        
                        # Update users table to match the new auth ID
                        update_result = supabase.table('users').update({
                            'id': new_auth_id
                        }).eq('id', legacy_user_id).execute()
                        
                        if update_result.data:
                            logger.info(f"✅ Updated users table ID to match auth ID: {new_auth_id}")
                            
                            # Create user_profiles entry
                            profile_data = {
                                'id': new_auth_id,
                                'username': legacy_user.get('username', ''),
                                'first_name': legacy_user.get('first_name', ''),
                                'last_name': legacy_user.get('last_name', ''),
                                'is_active': legacy_user.get('is_active', True)
                            }
                            
                            supabase.table('user_profiles').upsert(profile_data).execute()
                            logger.info(f"✅ Created user_profiles entry")
                            
                            return True
                        else:
                            logger.error(f"❌ Failed to update users table after auth creation")
                            return False
                    else:
                        logger.error(f"❌ Failed to create auth user")
                        return False
                        
                except Exception as create_error:
                    logger.error(f"❌ Error creating auth user: {create_error}")
                    return False
                    
        except Exception as auth_error:
            logger.error(f"❌ Error checking auth users: {auth_error}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(fix_user_auth_migration())
    if result:
        print("🎉 User auth migration completed successfully!")
    else:
        print("💥 User auth migration failed!")