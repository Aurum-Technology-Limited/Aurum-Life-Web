import React, { memo, useMemo } from 'react';
import { LazyImage } from './LazyImage';
import { getSupabaseCDNUrl, getResponsiveImageUrls } from '../../services/supabaseCDN';
import { cn } from '../../lib/utils';

/**
 * CDNImage Component
 * Optimized image component that uses Supabase CDN with transformations
 */
export const CDNImage = memo(({
  bucket,
  path,
  alt,
  className,
  width,
  height,
  size = 'medium', // thumbnail, small, medium, large, original
  quality = 'medium', // low, medium, high
  priority = false,
  objectFit = 'cover',
  transform = {}, // Custom transformations
  placeholder,
  onLoad,
  onError,
  ...props
}) => {
  // Generate CDN URL with transformations
  const cdnUrl = useMemo(() => {
    if (!bucket || !path) return '';
    
    // Predefined size transformations
    const sizeTransforms = {
      thumbnail: { width: 200, height: 200, resize: 'cover' },
      small: { width: 400, resize: 'contain' },
      medium: { width: 800, resize: 'contain' },
      large: { width: 1600, resize: 'contain' },
      original: {}
    };
    
    // Quality settings
    const qualityMap = {
      low: 60,
      medium: 80,
      high: 90,
      original: 100
    };
    
    // Merge predefined and custom transformations
    const finalTransform = {
      ...sizeTransforms[size],
      quality: qualityMap[quality],
      ...transform
    };
    
    return getSupabaseCDNUrl(bucket, path, finalTransform);
  }, [bucket, path, size, quality, transform]);
  
  // Generate responsive URLs
  const responsiveUrls = useMemo(() => {
    if (!bucket || !path) return null;
    return getResponsiveImageUrls(bucket, path);
  }, [bucket, path]);
  
  // Use srcset for responsive images
  const srcSet = responsiveUrls?.srcset;
  
  return (
    <LazyImage
      src={cdnUrl}
      alt={alt}
      className={className}
      width={width}
      height={height}
      sizes={props.sizes}
      srcSet={srcSet}
      priority={priority}
      placeholder={placeholder || '/images/placeholder.svg'}
      objectFit={objectFit}
      onLoad={onLoad}
      onError={onError}
      {...props}
    />
  );
}, (prevProps, nextProps) => {
  // Custom comparison - only re-render if important props change
  return prevProps.bucket === nextProps.bucket &&
         prevProps.path === nextProps.path &&
         prevProps.size === nextProps.size &&
         prevProps.quality === nextProps.quality &&
         JSON.stringify(prevProps.transform) === JSON.stringify(nextProps.transform);
});

/**
 * ResponsiveCDNImage Component
 * Automatically handles responsive images with CDN
 */
export const ResponsiveCDNImage = memo(({
  bucket,
  path,
  alt,
  className,
  aspectRatio = '16/9',
  sizes = '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw',
  priority = false,
  quality = 'medium',
  ...props
}) => {
  const responsiveUrls = useMemo(() => {
    if (!bucket || !path) return null;
    return getResponsiveImageUrls(bucket, path);
  }, [bucket, path]);
  
  if (!responsiveUrls) return null;
  
  return (
    <div 
      className={cn("relative overflow-hidden", className)}
      style={{ aspectRatio }}
    >
      <picture>
        {/* WebP sources */}
        <source
          type="image/webp"
          srcSet={`
            ${responsiveUrls.webp.small} 400w,
            ${responsiveUrls.webp.medium} 800w,
            ${responsiveUrls.webp.large} 1600w
          `}
          sizes={sizes}
        />
        
        {/* Fallback sources */}
        <source
          srcSet={responsiveUrls.srcset}
          sizes={sizes}
        />
        
        {/* Fallback image */}
        <LazyImage
          src={responsiveUrls.sizes.medium}
          alt={alt}
          className="w-full h-full object-cover"
          priority={priority}
          {...props}
        />
      </picture>
    </div>
  );
});

/**
 * AvatarCDNImage Component
 * Optimized avatar images with CDN
 */
export const AvatarCDNImage = memo(({
  bucket = 'avatars',
  path,
  alt,
  size = 40,
  className,
  fallback = '/images/default-avatar.png'
}) => {
  const sizeClass = useMemo(() => {
    if (size <= 32) return 'w-8 h-8';
    if (size <= 40) return 'w-10 h-10';
    if (size <= 48) return 'w-12 h-12';
    if (size <= 64) return 'w-16 h-16';
    return 'w-20 h-20';
  }, [size]);
  
  return (
    <CDNImage
      bucket={bucket}
      path={path}
      alt={alt}
      className={cn(
        "rounded-full object-cover",
        sizeClass,
        className
      )}
      size="thumbnail"
      quality="high"
      transform={{
        width: size * 2, // 2x for retina
        height: size * 2,
        resize: 'cover'
      }}
      placeholder={fallback}
      priority={true}
    />
  );
});

/**
 * GalleryCDNImage Component
 * Optimized for image galleries with lightbox support
 */
export const GalleryCDNImage = memo(({
  bucket,
  path,
  alt,
  className,
  onClick,
  showCaption = false,
  caption
}) => {
  const [isLoaded, setIsLoaded] = React.useState(false);
  
  const handleClick = React.useCallback(() => {
    if (onClick) {
      const urls = getResponsiveImageUrls(bucket, path);
      onClick({
        original: urls.original,
        large: urls.sizes.large,
        medium: urls.sizes.medium,
        alt,
        caption
      });
    }
  }, [bucket, path, alt, caption, onClick]);
  
  return (
    <div className={cn("relative group cursor-pointer", className)}>
      <CDNImage
        bucket={bucket}
        path={path}
        alt={alt}
        className="w-full h-full object-cover transition-transform group-hover:scale-105"
        size="medium"
        quality="high"
        onLoad={() => setIsLoaded(true)}
      />
      
      {/* Overlay on hover */}
      <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
        </svg>
      </div>
      
      {/* Caption */}
      {showCaption && caption && isLoaded && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3">
          <p className="text-white text-sm">{caption}</p>
        </div>
      )}
      
      {/* Click handler */}
      <div
        className="absolute inset-0 cursor-pointer"
        onClick={handleClick}
        role="button"
        tabIndex={0}
        aria-label={`View ${alt} in full size`}
      />
    </div>
  );
});

export default CDNImage;