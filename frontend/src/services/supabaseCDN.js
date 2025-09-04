/**
 * Supabase CDN Service
 * Handles CDN URLs and image transformations
 */

import { supabase } from './supabase';

const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL || '';
const STORAGE_URL = `${SUPABASE_URL}/storage/v1/object/public`;

/**
 * Image transformation options for Supabase
 */
export const ImageTransformOptions = {
  // Preset sizes
  thumbnail: { width: 200, height: 200, resize: 'cover' },
  small: { width: 400, height: 400, resize: 'contain' },
  medium: { width: 800, height: 800, resize: 'contain' },
  large: { width: 1600, height: 1600, resize: 'contain' },
  
  // Quality presets
  quality: {
    low: 60,
    medium: 80,
    high: 90,
    original: 100
  }
};

/**
 * Generate CDN URL for Supabase storage
 * @param {string} bucket - Storage bucket name
 * @param {string} path - File path in bucket
 * @param {Object} transform - Transformation options
 * @returns {string} CDN URL with transformations
 */
export function getSupabaseCDNUrl(bucket, path, transform = {}) {
  if (!bucket || !path) return '';
  
  // Base CDN URL
  let url = `${STORAGE_URL}/${bucket}/${path}`;
  
  // Add transformation parameters
  const params = new URLSearchParams();
  
  if (transform.width) params.append('width', transform.width);
  if (transform.height) params.append('height', transform.height);
  if (transform.resize) params.append('resize', transform.resize);
  if (transform.quality) params.append('quality', transform.quality);
  if (transform.format) params.append('format', transform.format);
  
  // Add cache control
  params.append('cache-control', '3600'); // 1 hour cache
  
  if (params.toString()) {
    url += '?' + params.toString();
  }
  
  return url;
}

/**
 * Generate responsive image URLs
 * @param {string} bucket - Storage bucket name
 * @param {string} path - File path in bucket
 * @returns {Object} Responsive image URLs
 */
export function getResponsiveImageUrls(bucket, path) {
  const baseUrl = path.replace(/\.(jpg|jpeg|png)$/i, '');
  const extension = path.match(/\.(jpg|jpeg|png)$/i)?.[0] || '.jpg';
  
  return {
    // Original
    original: getSupabaseCDNUrl(bucket, path),
    
    // WebP versions (if your setup supports it)
    webp: {
      small: getSupabaseCDNUrl(bucket, path, { 
        width: 400, 
        format: 'webp',
        quality: 80 
      }),
      medium: getSupabaseCDNUrl(bucket, path, { 
        width: 800, 
        format: 'webp',
        quality: 85 
      }),
      large: getSupabaseCDNUrl(bucket, path, { 
        width: 1600, 
        format: 'webp',
        quality: 90 
      })
    },
    
    // Standard formats
    sizes: {
      thumbnail: getSupabaseCDNUrl(bucket, path, ImageTransformOptions.thumbnail),
      small: getSupabaseCDNUrl(bucket, path, ImageTransformOptions.small),
      medium: getSupabaseCDNUrl(bucket, path, ImageTransformOptions.medium),
      large: getSupabaseCDNUrl(bucket, path, ImageTransformOptions.large)
    },
    
    // Responsive srcset
    srcset: [
      `${getSupabaseCDNUrl(bucket, path, { width: 400 })} 400w`,
      `${getSupabaseCDNUrl(bucket, path, { width: 800 })} 800w`,
      `${getSupabaseCDNUrl(bucket, path, { width: 1200 })} 1200w`,
      `${getSupabaseCDNUrl(bucket, path, { width: 1600 })} 1600w`
    ].join(', ')
  };
}

/**
 * Upload image with CDN optimization
 * @param {File} file - Image file to upload
 * @param {string} bucket - Storage bucket name
 * @param {string} path - File path in bucket
 * @returns {Promise<Object>} Upload result with CDN URLs
 */
export async function uploadImageWithCDN(file, bucket, path) {
  try {
    // Upload to Supabase storage
    const { data, error } = await supabase.storage
      .from(bucket)
      .upload(path, file, {
        cacheControl: '3600',
        upsert: false
      });
    
    if (error) throw error;
    
    // Generate CDN URLs
    const cdnUrls = getResponsiveImageUrls(bucket, data.path);
    
    return {
      success: true,
      path: data.path,
      urls: cdnUrls
    };
  } catch (error) {
    console.error('Upload error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get public URL with CDN benefits
 * @param {string} bucket - Storage bucket name
 * @param {string} path - File path in bucket
 * @returns {string} Public CDN URL
 */
export function getPublicUrl(bucket, path) {
  const { data } = supabase.storage
    .from(bucket)
    .getPublicUrl(path);
  
  return data.publicUrl;
}

/**
 * Delete image from CDN cache
 * @param {string} bucket - Storage bucket name
 * @param {string} path - File path in bucket
 */
export async function deleteImageFromCDN(bucket, path) {
  try {
    const { error } = await supabase.storage
      .from(bucket)
      .remove([path]);
    
    if (error) throw error;
    
    // Note: CDN cache will expire based on cache-control headers
    return { success: true };
  } catch (error) {
    console.error('Delete error:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Generate blur placeholder data URL
 * @param {string} bucket - Storage bucket name
 * @param {string} path - File path in bucket
 * @returns {Promise<string>} Base64 blur placeholder
 */
export async function generateBlurPlaceholder(bucket, path) {
  try {
    // Get tiny version of image
    const tinyUrl = getSupabaseCDNUrl(bucket, path, {
      width: 20,
      quality: 40,
      format: 'webp'
    });
    
    // Fetch and convert to base64
    const response = await fetch(tinyUrl);
    const blob = await response.blob();
    
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch (error) {
    console.error('Blur placeholder error:', error);
    return null;
  }
}

/**
 * Preload images for better performance
 * @param {Array<string>} urls - URLs to preload
 */
export function preloadImages(urls) {
  urls.forEach(url => {
    const img = new Image();
    img.src = url;
  });
}

/**
 * React hook for Supabase CDN images
 */
export function useSupabaseCDN(bucket, path, options = {}) {
  const [urls, setUrls] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  
  React.useEffect(() => {
    if (!bucket || !path) {
      setLoading(false);
      return;
    }
    
    try {
      const cdnUrls = getResponsiveImageUrls(bucket, path);
      setUrls(cdnUrls);
      
      // Preload if priority
      if (options.priority) {
        preloadImages([
          cdnUrls.sizes.small,
          cdnUrls.sizes.medium
        ]);
      }
      
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }, [bucket, path, options.priority]);
  
  return { urls, loading, error };
}