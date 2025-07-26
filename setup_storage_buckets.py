#!/usr/bin/env python3
"""
Setup Supabase Storage Buckets for Aurum Life
Creates the necessary buckets for file storage
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

def setup_storage_buckets():
    """Create storage buckets for file management"""
    try:
        # Initialize Supabase client
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            print("❌ Supabase credentials not found")
            return False
        
        supabase = create_client(url, key)
        print("✅ Supabase client connected")
        
        # Define buckets to create
        buckets_config = {
            'aurum-documents': {
                'public': False,
                'description': 'Document files (PDF, Word, etc.)'
            },
            'aurum-images': {
                'public': False, 
                'description': 'Image files (PNG, JPG, etc.)'
            },
            'aurum-archives': {
                'public': False,
                'description': 'Archive files (ZIP, RAR, etc.)'
            },
            'aurum-files': {
                'public': False,
                'description': 'General file storage'
            }
        }
        
        created_buckets = []
        existing_buckets = []
        
        for bucket_name, config in buckets_config.items():
            try:
                # Try to get bucket info to see if it exists
                existing_bucket = supabase.storage.get_bucket(bucket_name)
                if existing_bucket:
                    existing_buckets.append(bucket_name)
                    print(f"✅ Bucket '{bucket_name}' already exists")
                    continue
                    
            except Exception:
                # Bucket doesn't exist, create it
                try:
                    result = supabase.storage.create_bucket(
                        bucket_name,
                        options={
                            "public": config['public'],
                            "allowed_mime_types": None,  # Allow all file types
                            "file_size_limit": 10485760  # 10MB limit
                        }
                    )
                    
                    if hasattr(result, 'error') and result.error:
                        print(f"❌ Error creating bucket '{bucket_name}': {result.error}")
                    else:
                        created_buckets.append(bucket_name)
                        print(f"✅ Created bucket '{bucket_name}' - {config['description']}")
                        
                except Exception as create_error:
                    print(f"❌ Failed to create bucket '{bucket_name}': {create_error}")
        
        print(f"\n📊 Storage Setup Summary:")
        print(f"   ✅ Created: {len(created_buckets)} buckets")
        print(f"   📁 Existing: {len(existing_buckets)} buckets") 
        print(f"   🎯 Total: {len(created_buckets) + len(existing_buckets)}/{len(buckets_config)} buckets")
        
        if created_buckets:
            print(f"   📝 New buckets: {', '.join(created_buckets)}")
        
        # Test bucket access
        print(f"\n🔍 Testing bucket access...")
        for bucket_name in buckets_config.keys():
            try:
                files = supabase.storage.from_(bucket_name).list()
                if hasattr(files, 'error') and files.error:
                    print(f"   ⚠️ {bucket_name}: Access error - {files.error}")
                else:
                    print(f"   ✅ {bucket_name}: Accessible ({len(files) if files else 0} files)")
            except Exception as e:
                print(f"   ❌ {bucket_name}: Access failed - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage setup failed: {e}")
        return False

if __name__ == "__main__":
    print("🗂️ SETTING UP SUPABASE STORAGE BUCKETS")
    print("=" * 50)
    
    success = setup_storage_buckets()
    
    if success:
        print("\n🎉 STORAGE SETUP COMPLETE!")
        print("✅ All storage buckets are ready")
        print("✅ File upload system can now use Supabase Storage")
    else:
        print("\n❌ STORAGE SETUP FAILED!")
        print("Please check Supabase credentials and try again")
    
    print("=" * 50)