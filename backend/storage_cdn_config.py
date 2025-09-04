"""
Storage CDN Configuration for Supabase
Optimizes storage buckets for CDN delivery
"""

import logging
from typing import Dict, List, Optional
from supabase_client import supabase_manager

logger = logging.getLogger(__name__)

class StorageCDNConfig:
    """
    Configure Supabase storage buckets for optimal CDN performance
    """
    
    # Recommended cache durations for different content types
    CACHE_DURATIONS = {
        'avatars': 86400,        # 24 hours
        'images': 604800,        # 7 days
        'documents': 86400,      # 24 hours
        'temp': 3600,           # 1 hour
        'public': 2592000,      # 30 days
    }
    
    # CORS configuration for CDN
    CORS_CONFIG = {
        'allowedOrigins': ['*'],  # Allow all origins for CDN
        'allowedMethods': ['GET', 'HEAD'],
        'allowedHeaders': ['*'],
        'exposedHeaders': ['Content-Length', 'Content-Type'],
        'maxAge': 3600
    }
    
    async def setup_cdn_buckets(self):
        """
        Setup storage buckets with CDN-optimized configuration
        """
        buckets_config = [
            {
                'name': 'avatars',
                'public': True,
                'file_size_limit': 5 * 1024 * 1024,  # 5MB
                'allowed_mime_types': ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
            },
            {
                'name': 'images',
                'public': True,
                'file_size_limit': 10 * 1024 * 1024,  # 10MB
                'allowed_mime_types': ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/svg+xml']
            },
            {
                'name': 'documents',
                'public': False,  # Private bucket
                'file_size_limit': 50 * 1024 * 1024,  # 50MB
                'allowed_mime_types': ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            }
        ]
        
        for config in buckets_config:
            await self.create_or_update_bucket(config)
    
    async def create_or_update_bucket(self, config: Dict):
        """
        Create or update a storage bucket with CDN configuration
        """
        try:
            bucket_name = config['name']
            
            # Check if bucket exists
            existing_buckets = await supabase_manager.storage.list_buckets()
            bucket_exists = any(b['name'] == bucket_name for b in existing_buckets)
            
            if not bucket_exists:
                # Create bucket
                result = await supabase_manager.storage.create_bucket(
                    bucket_name,
                    options={
                        'public': config['public'],
                        'fileSizeLimit': config['file_size_limit'],
                        'allowedMimeTypes': config['allowed_mime_types']
                    }
                )
                logger.info(f"Created bucket: {bucket_name}")
            else:
                # Update bucket configuration
                result = await supabase_manager.storage.update_bucket(
                    bucket_name,
                    options={
                        'public': config['public'],
                        'fileSizeLimit': config['file_size_limit'],
                        'allowedMimeTypes': config['allowed_mime_types']
                    }
                )
                logger.info(f"Updated bucket: {bucket_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error configuring bucket {config['name']}: {e}")
            raise
    
    def get_cdn_headers(self, bucket_name: str, content_type: str) -> Dict[str, str]:
        """
        Get optimized CDN headers for file uploads
        """
        cache_duration = self.CACHE_DURATIONS.get(bucket_name, 86400)
        
        headers = {
            'Cache-Control': f'public, max-age={cache_duration}, immutable',
            'Content-Type': content_type,
            'X-Content-Type-Options': 'nosniff',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, HEAD',
            'Access-Control-Max-Age': '3600'
        }
        
        # Add image-specific headers
        if content_type.startswith('image/'):
            headers.update({
                'Accept-Ranges': 'bytes',
                'X-Frame-Options': 'ALLOWALL',  # Allow embedding images
                'Content-Disposition': 'inline'  # Display in browser
            })
        
        return headers
    
    async def upload_with_cdn_optimization(
        self,
        bucket_name: str,
        file_path: str,
        file_content: bytes,
        content_type: str
    ) -> Dict:
        """
        Upload file with CDN-optimized headers
        """
        try:
            # Get CDN headers
            headers = self.get_cdn_headers(bucket_name, content_type)
            
            # Upload to Supabase
            result = await supabase_manager.storage.from_(bucket_name).upload(
                file_path,
                file_content,
                file_options={
                    'contentType': content_type,
                    'cacheControl': headers['Cache-Control'],
                    'upsert': False
                }
            )
            
            if result.error:
                raise Exception(result.error.message)
            
            # Get public URL
            public_url = supabase_manager.storage.from_(bucket_name).get_public_url(file_path)
            
            return {
                'success': True,
                'path': file_path,
                'url': public_url,
                'cdn_headers': headers
            }
            
        except Exception as e:
            logger.error(f"CDN upload error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_transformation_url(
        self,
        bucket_name: str,
        file_path: str,
        transformations: Dict
    ) -> str:
        """
        Generate URL with image transformations
        
        Args:
            bucket_name: Storage bucket name
            file_path: Path to file in bucket
            transformations: Dict with transformation options
                - width: Target width
                - height: Target height
                - resize: 'cover' | 'contain' | 'fill'
                - quality: 1-100
                - format: 'webp' | 'jpeg' | 'png'
        """
        base_url = supabase_manager.storage.from_(bucket_name).get_public_url(file_path)
        
        # Add transformation parameters
        params = []
        
        if 'width' in transformations:
            params.append(f"width={transformations['width']}")
        
        if 'height' in transformations:
            params.append(f"height={transformations['height']}")
        
        if 'resize' in transformations:
            params.append(f"resize={transformations['resize']}")
        
        if 'quality' in transformations:
            params.append(f"quality={transformations['quality']}")
        
        if 'format' in transformations:
            params.append(f"format={transformations['format']}")
        
        if params:
            separator = '&' if '?' in base_url else '?'
            return f"{base_url}{separator}{'&'.join(params)}"
        
        return base_url
    
    async def purge_cdn_cache(self, bucket_name: str, file_path: str):
        """
        Note: Supabase doesn't provide direct cache purging.
        Files will expire based on Cache-Control headers.
        This is a placeholder for future implementation.
        """
        logger.info(f"Cache purge requested for {bucket_name}/{file_path}")
        # In production, you might integrate with Cloudflare or another CDN
        # that provides cache purging APIs
        return True

# Global instance
storage_cdn_config = StorageCDNConfig()

# Utility function for FastAPI endpoints
async def setup_cdn_buckets():
    """
    Run this once to setup CDN-optimized buckets
    """
    await storage_cdn_config.setup_cdn_buckets()
    return {"message": "CDN buckets configured successfully"}