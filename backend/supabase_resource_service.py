"""
Enhanced Resource Service with Supabase Storage Support
Handles file uploads, storage, and management with Supabase Storage
"""

import base64
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

# Try to import magic, but don't fail if it's not available
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

from models import Resource, ResourceCreate, ResourceUpdate, ResourceResponse, FileTypeEnum
from supabase_client import create_document, find_document, find_documents, update_document, delete_document
from supabase_storage import storage_service
import logging

logger = logging.getLogger(__name__)

class SupabaseResourceService:
    """Enhanced Resource Service with Supabase Storage integration"""
    
    @staticmethod
    async def create_resource_with_storage(user_id: str, resource_data: ResourceCreate) -> Resource:
        """Create a new file resource using Supabase Storage"""
        try:
            # Validate parent entity if provided
            if resource_data.parent_id and resource_data.parent_type:
                await SupabaseResourceService._validate_parent_entity(user_id, resource_data.parent_id, resource_data.parent_type)
            
            # Ensure storage service buckets exist
            await storage_service.create_buckets_if_not_exist()
            
            # Handle file upload based on whether we have base64 content or storage info
            if resource_data.file_content:
                # Upload from base64 content to Supabase Storage
                upload_result = await storage_service.upload_file_from_base64(
                    user_id=user_id,
                    parent_type=resource_data.parent_type or 'general',
                    parent_id=resource_data.parent_id or 'unassigned', 
                    original_filename=resource_data.original_filename,
                    base64_content=resource_data.file_content,
                    mime_type=resource_data.mime_type,
                    file_type=resource_data.file_type
                )
                
                if not upload_result['success']:
                    raise ValueError(f"File upload failed: {upload_result.get('error', 'Unknown error')}")
                
                # Update resource data with storage information
                resource_data.storage_bucket = upload_result['bucket']
                resource_data.storage_path = upload_result['file_path'] 
                resource_data.file_url = upload_result['file_url']
                resource_data.file_size = upload_result['file_size']
                
                # Clear base64 content after successful upload
                resource_data.file_content = None
                
            elif not (resource_data.storage_bucket and resource_data.storage_path):
                raise ValueError("Either file_content (base64) or storage information (bucket + path) is required")
            
            # Validate file size (limit to 10MB)
            max_file_size = 10 * 1024 * 1024  # 10MB
            if resource_data.file_size > max_file_size:
                raise ValueError(f"File size exceeds maximum limit of {max_file_size // (1024*1024)}MB")
            
            # Determine file type based on MIME type
            detected_file_type = SupabaseResourceService._determine_file_type(resource_data.mime_type)
            if detected_file_type != FileTypeEnum.other:
                resource_data.file_type = detected_file_type
            
            # Create resource in database
            resource = Resource(
                user_id=user_id,
                **resource_data.dict()
            )
            
            await create_document("resources", resource.dict())
            logger.info(f"✅ Created resource with Supabase Storage: {resource.filename}")
            
            return resource
            
        except Exception as e:
            logger.error(f"❌ Error creating resource: {e}")
            raise
    
    @staticmethod
    async def get_resource_with_url(user_id: str, resource_id: str) -> Optional[ResourceResponse]:
        """Get resource with download URL"""
        try:
            resource_doc = await find_document("resources", {"id": resource_id, "user_id": user_id})
            if not resource_doc:
                return None
            
            resource = ResourceResponse(**resource_doc)
            
            # Generate download URL if using Supabase Storage
            if resource_doc.get('storage_bucket') and resource_doc.get('storage_path'):
                download_url = await storage_service.get_file_url(
                    resource_doc['storage_bucket'], 
                    resource_doc['storage_path'],
                    expires_in=3600  # 1 hour
                )
                resource.file_url = download_url
            
            # Update access tracking
            await SupabaseResourceService._track_access(resource_id)
            
            return resource
            
        except Exception as e:
            logger.error(f"❌ Error getting resource: {e}")
            return None
    
    @staticmethod
    async def get_resources_by_parent(user_id: str, parent_type: str, parent_id: str) -> List[ResourceResponse]:
        """Get all resources attached to a parent entity with download URLs"""
        try:
            resources_docs = await find_documents("resources", {
                "user_id": user_id,
                "parent_type": parent_type,
                "parent_id": parent_id
            })
            
            resources = []
            for doc in resources_docs:
                resource = ResourceResponse(**doc)
                
                # Generate download URL if using Supabase Storage  
                if doc.get('storage_bucket') and doc.get('storage_path'):
                    download_url = await storage_service.get_file_url(
                        doc['storage_bucket'],
                        doc['storage_path'], 
                        expires_in=3600
                    )
                    resource.file_url = download_url
                
                resources.append(resource)
            
            return sorted(resources, key=lambda x: x.upload_date, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Error getting resources by parent: {e}")
            return []
    
    @staticmethod
    async def delete_resource(user_id: str, resource_id: str) -> bool:
        """Delete a resource and its file from Supabase Storage"""
        try:
            resource_doc = await find_document("resources", {"id": resource_id, "user_id": user_id})
            if not resource_doc:
                return False
            
            # Delete file from Supabase Storage if it exists there
            if resource_doc.get('storage_bucket') and resource_doc.get('storage_path'):
                delete_success = await storage_service.delete_file(
                    resource_doc['storage_bucket'],
                    resource_doc['storage_path']
                )
                
                if not delete_success:
                    logger.warning(f"⚠️ Failed to delete file from storage, but continuing with database deletion")
            
            # Delete resource from database
            success = await delete_document("resources", {"id": resource_id, "user_id": user_id})
            
            if success:
                logger.info(f"✅ Deleted resource: {resource_doc['filename']}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error deleting resource: {e}")
            return False
    
    @staticmethod
    async def migrate_base64_to_storage(user_id: str = None, batch_size: int = 10) -> Dict[str, Any]:
        """Migrate existing base64-stored files to Supabase Storage"""
        try:
            # Get resources that still have base64 content
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            resources_docs = await find_documents("resources", query, limit=batch_size)
            
            # Filter to only resources with file_content client-side
            resources_docs = [r for r in resources_docs if r.get("file_content") is not None]
            
            if not resources_docs:
                return {"success": True, "message": "No resources to migrate", "migrated": 0}
            
            await storage_service.create_buckets_if_not_exist()
            
            migrated_count = 0
            failed_count = 0
            
            for doc in resources_docs:
                try:
                    # Upload to Supabase Storage
                    upload_result = await storage_service.upload_file_from_base64(
                        user_id=doc['user_id'],
                        parent_type=doc.get('parent_type', 'general'),
                        parent_id=doc.get('parent_id', 'unassigned'),
                        original_filename=doc['original_filename'],
                        base64_content=doc['file_content'],
                        mime_type=doc['mime_type'],
                        file_type=FileTypeEnum(doc['file_type'])
                    )
                    
                    if upload_result['success']:
                        # Update database record
                        update_data = {
                            'storage_bucket': upload_result['bucket'],
                            'storage_path': upload_result['file_path'],
                            'file_url': upload_result['file_url'],
                            'file_content': None,  # Remove base64 content
                            'updated_at': datetime.utcnow()
                        }
                        
                        await update_document("resources", {"id": doc['id']}, update_data)
                        migrated_count += 1
                        logger.info(f"✅ Migrated resource: {doc['filename']}")
                        
                    else:
                        failed_count += 1
                        logger.error(f"❌ Failed to migrate resource: {doc['filename']} - {upload_result.get('error')}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"❌ Error migrating resource {doc.get('filename', 'unknown')}: {e}")
            
            return {
                "success": True,
                "message": f"Migration completed: {migrated_count} succeeded, {failed_count} failed",
                "migrated": migrated_count,
                "failed": failed_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error in migration: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def _validate_parent_entity(user_id: str, parent_id: str, parent_type: str):
        """Validate that parent entity exists and belongs to user"""
        entity_collections = {
            "task": "tasks",
            "project": "projects", 
            "area": "areas",
            "pillar": "pillars",
            "journal_entry": "journal_entries"
        }
        
        if parent_type not in entity_collections:
            raise ValueError(f"Invalid parent type: {parent_type}")
        
        collection = entity_collections[parent_type]
        entity = await find_document(collection, {"id": parent_id, "user_id": user_id})
        if not entity:
            raise ValueError(f"Parent {parent_type} with ID {parent_id} not found or doesn't belong to user")
    
    @staticmethod
    def _determine_file_type(mime_type: str) -> FileTypeEnum:
        """Determine file type enum from MIME type"""
        if mime_type.startswith('image/'):
            return FileTypeEnum.image
        elif mime_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'text/plain', 'text/rtf', 'application/rtf']:
            return FileTypeEnum.document
        elif mime_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                          'text/csv']:
            return FileTypeEnum.spreadsheet
        elif mime_type in ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
            return FileTypeEnum.presentation
        elif mime_type in ['application/zip', 'application/x-rar-compressed', 'application/gzip', 'application/x-tar']:
            return FileTypeEnum.archive
        else:
            return FileTypeEnum.other
    
    @staticmethod 
    async def _track_access(resource_id: str):
        """Track resource access for analytics"""
        try:
            update_data = {
                "last_accessed": datetime.utcnow(),
                "$inc": {"access_count": 1}
            }
            await update_document("resources", {"id": resource_id}, update_data)
        except Exception as e:
            logger.warning(f"⚠️ Failed to track access for resource {resource_id}: {e}")

# Global instance
supabase_resource_service = SupabaseResourceService()