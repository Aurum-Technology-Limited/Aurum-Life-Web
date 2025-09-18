"""
Supabase Storage Service for Aurum Life
Handles file uploads, downloads, and management using Supabase Storage
"""

import os
import uuid
from typing import Optional, List, Dict, Any, BinaryIO
from datetime import datetime
import mimetypes
from pathlib import Path
import base64
import logging

from supabase_client import supabase_manager
from models import FileTypeEnum, ResourceCategoryEnum

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    """Manages file operations with Supabase Storage"""
    
    # Storage buckets configuration
    BUCKETS = {
        'documents': 'aurum-documents',
        'images': 'aurum-images', 
        'archives': 'aurum-archives',
        'other': 'aurum-files'
    }
    
    def __init__(self):
        self.supabase = supabase_manager.get_client()
    
    @classmethod
    def get_bucket_for_file_type(cls, file_type: FileTypeEnum, mime_type: str) -> str:
        """Determine the appropriate storage bucket for a file"""
        if file_type == FileTypeEnum.image or mime_type.startswith('image/'):
            return cls.BUCKETS['images']
        elif file_type in [FileTypeEnum.document, FileTypeEnum.spreadsheet, FileTypeEnum.presentation]:
            return cls.BUCKETS['documents']
        elif file_type == FileTypeEnum.archive or mime_type.startswith('application/zip'):
            return cls.BUCKETS['archives']
        else:
            return cls.BUCKETS['other']
    
    async def create_buckets_if_not_exist(self):
        """Create storage buckets if they don't exist"""
        try:
            for bucket_purpose, bucket_name in self.BUCKETS.items():
                try:
                    # Check if bucket exists by trying to get its info
                    bucket_info = self.supabase.storage.get_bucket(bucket_name)
                    logger.info(f"✅ Bucket '{bucket_name}' already exists")
                except Exception:
                    # Bucket doesn't exist, create it
                    try:
                        self.supabase.storage.create_bucket(
                            bucket_name, 
                            options={"public": False}  # Private by default
                        )
                        logger.info(f"✅ Created bucket '{bucket_name}'")
                    except Exception as create_error:
                        logger.error(f"❌ Failed to create bucket '{bucket_name}': {create_error}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up buckets: {e}")
            return False
    
    def generate_file_path(self, user_id: str, parent_type: str, parent_id: str, 
                          original_filename: str) -> str:
        """Generate a unique file path for storage"""
        # Create path structure: user_id/parent_type/parent_id/unique_filename
        file_extension = Path(original_filename).suffix
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        return f"{user_id}/{parent_type}/{parent_id}/{unique_filename}"
    
    async def upload_file_from_base64(self, user_id: str, parent_type: str, parent_id: str,
                                    original_filename: str, base64_content: str, 
                                    mime_type: str, file_type: FileTypeEnum) -> Dict[str, Any]:
        """Upload a file from base64 content to Supabase Storage"""
        try:
            # Decode base64 content
            if ',' in base64_content:  # Handle data URL format (data:image/png;base64,...)
                base64_content = base64_content.split(',')[1]
            
            file_bytes = base64.b64decode(base64_content)
            
            # Determine bucket and file path
            bucket_name = self.get_bucket_for_file_type(file_type, mime_type)
            file_path = self.generate_file_path(user_id, parent_type, parent_id, original_filename)
            
            # Upload to Supabase Storage
            result = self.supabase.storage.from_(bucket_name).upload(
                file_path,
                file_bytes,
                {
                    'content-type': mime_type,
                    'cache-control': '3600'
                }
            )
            
            if hasattr(result, 'error') and result.error:
                raise Exception(f"Upload failed: {result.error}")
            
            # Get public URL (if bucket is public) or signed URL
            try:
                public_url = self.supabase.storage.from_(bucket_name).get_public_url(file_path)
                file_url = public_url
            except:
                # If public URL fails, we'll generate signed URLs on demand
                file_url = None
            
            return {
                'success': True,
                'bucket': bucket_name,
                'file_path': file_path,
                'file_url': file_url,
                'file_size': len(file_bytes)
            }
            
        except Exception as e:
            logger.error(f"❌ File upload error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def upload_file_from_bytes(self, user_id: str, parent_type: str, parent_id: str,
                                   original_filename: str, file_bytes: bytes, 
                                   mime_type: str, file_type: FileTypeEnum) -> Dict[str, Any]:
        """Upload a file from bytes to Supabase Storage"""
        try:
            # Determine bucket and file path
            bucket_name = self.get_bucket_for_file_type(file_type, mime_type)
            file_path = self.generate_file_path(user_id, parent_type, parent_id, original_filename)
            
            # Upload to Supabase Storage
            result = self.supabase.storage.from_(bucket_name).upload(
                file_path,
                file_bytes,
                {
                    'content-type': mime_type,
                    'cache-control': '3600'
                }
            )
            
            if hasattr(result, 'error') and result.error:
                raise Exception(f"Upload failed: {result.error}")
            
            # Get public URL
            try:
                public_url = self.supabase.storage.from_(bucket_name).get_public_url(file_path)
                file_url = public_url
            except:
                file_url = None
            
            return {
                'success': True,
                'bucket': bucket_name,
                'file_path': file_path,
                'file_url': file_url,
                'file_size': len(file_bytes)
            }
            
        except Exception as e:
            logger.error(f"❌ File upload error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_file_url(self, bucket_name: str, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get a signed URL for accessing a file"""
        try:
            # Try public URL first
            try:
                public_url = self.supabase.storage.from_(bucket_name).get_public_url(file_path)
                return public_url
            except:
                pass
            
            # Generate signed URL if public access fails
            signed_url = self.supabase.storage.from_(bucket_name).create_signed_url(file_path, expires_in)
            
            if hasattr(signed_url, 'error') and signed_url.error:
                logger.error(f"Failed to create signed URL: {signed_url.error}")
                return None
                
            return signed_url.get('signedURL')
            
        except Exception as e:
            logger.error(f"❌ Error getting file URL: {e}")
            return None
    
    async def delete_file(self, bucket_name: str, file_path: str) -> bool:
        """Delete a file from Supabase Storage"""
        try:
            result = self.supabase.storage.from_(bucket_name).remove([file_path])
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Failed to delete file: {result.error}")
                return False
                
            logger.info(f"✅ Deleted file: {bucket_name}/{file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting file: {e}")
            return False
    
    async def get_file_info(self, bucket_name: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information from Supabase Storage"""
        try:
            # List files to get file info (Supabase doesn't have direct file info API)
            folder_path = '/'.join(file_path.split('/')[:-1])
            filename = file_path.split('/')[-1]
            
            files = self.supabase.storage.from_(bucket_name).list(folder_path)
            
            if hasattr(files, 'error') and files.error:
                return None
            
            # Find our file
            for file_info in files:
                if file_info.get('name') == filename:
                    return {
                        'name': file_info.get('name'),
                        'size': file_info.get('metadata', {}).get('size'),
                        'mime_type': file_info.get('metadata', {}).get('mimetype'),
                        'last_modified': file_info.get('updated_at'),
                        'created_at': file_info.get('created_at')
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting file info: {e}")
            return None

# Global instance
storage_service = SupabaseStorageService()