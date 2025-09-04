"""
Image Processing Service
Handles image optimization and WebP conversion
"""

import os
import io
import hashlib
from PIL import Image
from typing import Tuple, Optional, Dict, List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    Service for processing and optimizing images
    Supports WebP conversion and responsive image generation
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.quality_settings = {
            'thumbnail': {'quality': 70, 'max_size': (200, 200)},
            'small': {'quality': 80, 'max_size': (400, 400)},
            'medium': {'quality': 85, 'max_size': (800, 800)},
            'large': {'quality': 90, 'max_size': (1600, 1600)},
            'original': {'quality': 95, 'max_size': None}
        }
        
        # Responsive breakpoints for automatic generation
        self.responsive_widths = [640, 768, 1024, 1280, 1920]
    
    async def process_uploaded_image(
        self,
        file_content: bytes,
        filename: str,
        generate_responsive: bool = True,
        generate_webp: bool = True,
        generate_blur_placeholder: bool = True
    ) -> Dict[str, any]:
        """
        Process an uploaded image with various optimizations
        
        Returns:
            Dict containing paths to processed images and metadata
        """
        try:
            # Run processing in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._process_image_sync,
                file_content,
                filename,
                generate_responsive,
                generate_webp,
                generate_blur_placeholder
            )
            return result
        except Exception as e:
            logger.error(f"Error processing image {filename}: {e}")
            raise
    
    def _process_image_sync(
        self,
        file_content: bytes,
        filename: str,
        generate_responsive: bool,
        generate_webp: bool,
        generate_blur_placeholder: bool
    ) -> Dict[str, any]:
        """Synchronous image processing"""
        
        # Generate unique hash for the image
        image_hash = hashlib.md5(file_content).hexdigest()[:12]
        base_name = os.path.splitext(filename)[0]
        
        # Open image
        img = Image.open(io.BytesIO(file_content))
        
        # Convert RGBA to RGB if necessary (for JPEG output)
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Get original dimensions
        original_width, original_height = img.size
        original_format = img.format or 'JPEG'
        
        results = {
            'original': {
                'width': original_width,
                'height': original_height,
                'format': original_format,
                'hash': image_hash
            },
            'processed': {}
        }
        
        # Generate blur placeholder
        if generate_blur_placeholder:
            blur_data = self._generate_blur_placeholder(img)
            results['blur_placeholder'] = blur_data
        
        # Generate responsive images
        if generate_responsive:
            responsive_images = self._generate_responsive_images(
                img, base_name, image_hash, generate_webp
            )
            results['processed']['responsive'] = responsive_images
        
        # Generate standard sizes
        standard_sizes = self._generate_standard_sizes(
            img, base_name, image_hash, generate_webp
        )
        results['processed']['sizes'] = standard_sizes
        
        return results
    
    def _generate_blur_placeholder(self, img: Image.Image) -> str:
        """Generate a small base64-encoded blur placeholder"""
        # Create tiny version (20px wide)
        aspect_ratio = img.height / img.width
        placeholder_width = 20
        placeholder_height = int(placeholder_width * aspect_ratio)
        
        placeholder = img.resize(
            (placeholder_width, placeholder_height),
            Image.Resampling.LANCZOS
        )
        
        # Convert to base64
        buffer = io.BytesIO()
        placeholder.save(buffer, format='JPEG', quality=40)
        
        import base64
        blur_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{blur_data}"
    
    def _generate_responsive_images(
        self,
        img: Image.Image,
        base_name: str,
        image_hash: str,
        generate_webp: bool
    ) -> List[Dict]:
        """Generate images for responsive breakpoints"""
        responsive_images = []
        
        for width in self.responsive_widths:
            # Skip if image is smaller than breakpoint
            if img.width < width:
                continue
            
            # Calculate height maintaining aspect ratio
            aspect_ratio = img.height / img.width
            height = int(width * aspect_ratio)
            
            # Resize image
            resized = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Generate filenames
            jpeg_filename = f"{base_name}-{width}-{image_hash}.jpg"
            webp_filename = f"{base_name}-{width}-{image_hash}.webp"
            
            image_info = {
                'width': width,
                'height': height,
                'jpeg': jpeg_filename
            }
            
            # Save JPEG
            jpeg_buffer = io.BytesIO()
            resized.save(jpeg_buffer, 'JPEG', quality=85, optimize=True)
            image_info['jpeg_size'] = jpeg_buffer.tell()
            image_info['jpeg_data'] = jpeg_buffer.getvalue()
            
            # Save WebP if requested
            if generate_webp:
                webp_buffer = io.BytesIO()
                resized.save(webp_buffer, 'WEBP', quality=80, method=6)
                image_info['webp'] = webp_filename
                image_info['webp_size'] = webp_buffer.tell()
                image_info['webp_data'] = webp_buffer.getvalue()
                
                # Calculate savings
                image_info['webp_savings'] = round(
                    (1 - image_info['webp_size'] / image_info['jpeg_size']) * 100, 1
                )
            
            responsive_images.append(image_info)
        
        return responsive_images
    
    def _generate_standard_sizes(
        self,
        img: Image.Image,
        base_name: str,
        image_hash: str,
        generate_webp: bool
    ) -> Dict[str, Dict]:
        """Generate standard image sizes (thumbnail, small, medium, large)"""
        sizes = {}
        
        for size_name, settings in self.quality_settings.items():
            if size_name == 'original':
                # Handle original separately
                continue
            
            max_size = settings['max_size']
            quality = settings['quality']
            
            # Create resized version
            if max_size:
                img_copy = img.copy()
                img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
            else:
                img_copy = img
            
            width, height = img_copy.size
            
            # Generate filenames
            jpeg_filename = f"{base_name}-{size_name}-{image_hash}.jpg"
            webp_filename = f"{base_name}-{size_name}-{image_hash}.webp"
            
            size_info = {
                'width': width,
                'height': height,
                'jpeg': jpeg_filename
            }
            
            # Save JPEG
            jpeg_buffer = io.BytesIO()
            img_copy.save(jpeg_buffer, 'JPEG', quality=quality, optimize=True)
            size_info['jpeg_size'] = jpeg_buffer.tell()
            size_info['jpeg_data'] = jpeg_buffer.getvalue()
            
            # Save WebP if requested
            if generate_webp:
                webp_buffer = io.BytesIO()
                img_copy.save(webp_buffer, 'WEBP', quality=quality-5, method=6)
                size_info['webp'] = webp_filename
                size_info['webp_size'] = webp_buffer.tell()
                size_info['webp_data'] = webp_buffer.getvalue()
                
                # Calculate savings
                size_info['webp_savings'] = round(
                    (1 - size_info['webp_size'] / size_info['jpeg_size']) * 100, 1
                )
            
            sizes[size_name] = size_info
        
        return sizes
    
    def optimize_existing_image(self, image_path: str, output_format: str = 'webp') -> Tuple[bytes, Dict]:
        """
        Optimize an existing image file
        
        Args:
            image_path: Path to the image file
            output_format: Target format ('webp', 'jpeg', 'png')
            
        Returns:
            Tuple of (optimized_image_bytes, metadata)
        """
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB for JPEG/WebP
                if output_format in ('jpeg', 'webp') and img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                # Optimize based on format
                buffer = io.BytesIO()
                
                if output_format == 'webp':
                    img.save(buffer, 'WEBP', quality=85, method=6, optimize=True)
                elif output_format == 'jpeg':
                    img.save(buffer, 'JPEG', quality=90, optimize=True, progressive=True)
                elif output_format == 'png':
                    img.save(buffer, 'PNG', optimize=True)
                else:
                    raise ValueError(f"Unsupported format: {output_format}")
                
                optimized_bytes = buffer.getvalue()
                
                # Get file sizes for comparison
                original_size = os.path.getsize(image_path)
                optimized_size = len(optimized_bytes)
                
                metadata = {
                    'original_size': original_size,
                    'optimized_size': optimized_size,
                    'savings_percent': round((1 - optimized_size / original_size) * 100, 1),
                    'format': output_format,
                    'width': img.width,
                    'height': img.height
                }
                
                return optimized_bytes, metadata
                
        except Exception as e:
            logger.error(f"Error optimizing image {image_path}: {e}")
            raise

# Global instance
image_processor = ImageProcessor()

# Utility function for FastAPI endpoints
async def process_upload_with_optimization(
    file_content: bytes,
    filename: str,
    user_id: str,
    storage_service
) -> Dict:
    """
    Process uploaded image and store all versions
    
    Args:
        file_content: Raw image bytes
        filename: Original filename
        user_id: User ID for storage path
        storage_service: Storage service instance (e.g., Supabase storage)
        
    Returns:
        Dict with URLs and metadata for all generated images
    """
    # Process image
    result = await image_processor.process_uploaded_image(
        file_content=file_content,
        filename=filename
    )
    
    stored_images = {
        'original': None,
        'responsive': [],
        'sizes': {},
        'blur_placeholder': result.get('blur_placeholder')
    }
    
    # Store original
    original_path = f"users/{user_id}/images/original/{filename}"
    original_url = await storage_service.upload_file(
        bucket='images',
        path=original_path,
        file_content=file_content
    )
    stored_images['original'] = original_url
    
    # Store responsive images
    for img_data in result['processed']['responsive']:
        # Store JPEG version
        jpeg_path = f"users/{user_id}/images/responsive/{img_data['jpeg']}"
        jpeg_url = await storage_service.upload_file(
            bucket='images',
            path=jpeg_path,
            file_content=img_data['jpeg_data']
        )
        
        stored_info = {
            'width': img_data['width'],
            'height': img_data['height'],
            'jpeg': jpeg_url
        }
        
        # Store WebP version if available
        if 'webp_data' in img_data:
            webp_path = f"users/{user_id}/images/responsive/{img_data['webp']}"
            webp_url = await storage_service.upload_file(
                bucket='images',
                path=webp_path,
                file_content=img_data['webp_data']
            )
            stored_info['webp'] = webp_url
            stored_info['webp_savings'] = img_data['webp_savings']
        
        stored_images['responsive'].append(stored_info)
    
    # Store standard sizes
    for size_name, img_data in result['processed']['sizes'].items():
        # Store JPEG version
        jpeg_path = f"users/{user_id}/images/{size_name}/{img_data['jpeg']}"
        jpeg_url = await storage_service.upload_file(
            bucket='images',
            path=jpeg_path,
            file_content=img_data['jpeg_data']
        )
        
        stored_info = {
            'width': img_data['width'],
            'height': img_data['height'],
            'jpeg': jpeg_url
        }
        
        # Store WebP version if available
        if 'webp_data' in img_data:
            webp_path = f"users/{user_id}/images/{size_name}/{img_data['webp']}"
            webp_url = await storage_service.upload_file(
                bucket='images',
                path=webp_path,
                file_content=img_data['webp_data']
            )
            stored_info['webp'] = webp_url
            stored_info['webp_savings'] = img_data['webp_savings']
        
        stored_images['sizes'][size_name] = stored_info
    
    return {
        'images': stored_images,
        'metadata': result['original']
    }