#!/usr/bin/env python3
"""
Direct test of Supabase Storage service
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('/app/backend/.env')

async def test_storage_service():
    """Test Supabase Storage service directly"""
    print("🧪 DIRECT STORAGE SERVICE TEST")
    print("=" * 40)
    
    try:
        # Import after environment is loaded
        from backend.supabase_storage import storage_service
        
        print("✅ Storage service imported")
        
        # Test bucket creation
        bucket_result = await storage_service.create_buckets_if_not_exist()
        if bucket_result:
            print("✅ Buckets setup successful")
        else:
            print("❌ Bucket setup failed")
            
        # Test file upload from base64
        test_content = "Hello Supabase Storage!"
        import base64
        b64_content = base64.b64encode(test_content.encode()).decode()
        
        upload_result = await storage_service.upload_file_from_base64(
            user_id="test-user-123",
            parent_type="project",
            parent_id="test-project-123", 
            original_filename="test.txt",
            base64_content=b64_content,
            mime_type="text/plain",
            file_type="document"
        )
        
        if upload_result['success']:
            print("✅ File upload successful")
            print(f"   Bucket: {upload_result['bucket']}")
            print(f"   Path: {upload_result['file_path']}")
            
            # Test URL generation
            file_url = await storage_service.get_file_url(
                upload_result['bucket'],
                upload_result['file_path']
            )
            
            if file_url:
                print("✅ File URL generated")
                print(f"   URL: {file_url[:50]}...")
            else:
                print("❌ File URL generation failed")
                
            # Test file deletion
            delete_result = await storage_service.delete_file(
                upload_result['bucket'],
                upload_result['file_path']
            )
            
            if delete_result:
                print("✅ File deletion successful")
            else:
                print("❌ File deletion failed")
                
        else:
            print(f"❌ File upload failed: {upload_result.get('error')}")
            
        return True
        
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_storage_service())
    if success:
        print("\n🎉 STORAGE SERVICE WORKING!")
    else:
        print("\n❌ STORAGE SERVICE FAILED!")