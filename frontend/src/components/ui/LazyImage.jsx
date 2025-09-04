import React, { useState, useEffect, useRef } from 'react';
import { cn } from '../../lib/utils';

/**
 * LazyImage Component
 * Provides lazy loading with intersection observer
 * Supports WebP format with fallback
 * Includes blur-up effect for smooth loading
 */
export function LazyImage({
  src,
  alt,
  className,
  width,
  height,
  placeholder = '/images/placeholder.svg',
  blurDataURL,
  sizes,
  priority = false,
  onLoad,
  onError,
  objectFit = 'cover',
  ...props
}) {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [imageRef, setImageRef] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [error, setError] = useState(false);
  const observerRef = useRef(null);

  // Generate WebP source if original is jpg/png
  const getWebPSource = (originalSrc) => {
    if (!originalSrc) return null;
    
    const isExternal = originalSrc.startsWith('http');
    if (isExternal) return null; // Don't convert external images
    
    const supportedFormats = ['.jpg', '.jpeg', '.png'];
    const hasSupported = supportedFormats.some(ext => originalSrc.toLowerCase().includes(ext));
    
    if (hasSupported) {
      return originalSrc.replace(/\.(jpg|jpeg|png)$/i, '.webp');
    }
    
    return null;
  };

  // Set up intersection observer
  useEffect(() => {
    if (!imageRef || priority) {
      if (priority) {
        setIsInView(true);
      }
      return;
    }

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observerRef.current?.disconnect();
          }
        });
      },
      {
        rootMargin: '50px', // Start loading 50px before entering viewport
        threshold: 0.01
      }
    );

    observerRef.current.observe(imageRef);

    return () => {
      observerRef.current?.disconnect();
    };
  }, [imageRef, priority]);

  // Load image when in view
  useEffect(() => {
    if (!isInView || !src) return;

    const img = new Image();
    
    // Try WebP first if available
    const webpSrc = getWebPSource(src);
    const sourcesToTry = webpSrc ? [webpSrc, src] : [src];
    let currentIndex = 0;

    const tryNextSource = () => {
      if (currentIndex >= sourcesToTry.length) {
        setError(true);
        setImageSrc(placeholder);
        onError?.();
        return;
      }

      img.src = sourcesToTry[currentIndex];
      currentIndex++;
    };

    img.onload = () => {
      setImageSrc(img.src);
      setIsLoaded(true);
      onLoad?.();
    };

    img.onerror = () => {
      console.warn(`Failed to load image: ${img.src}`);
      tryNextSource();
    };

    // Set sizes for responsive images
    if (sizes) {
      img.sizes = sizes;
    }

    // Start loading
    tryNextSource();

    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [isInView, src, placeholder, sizes, onLoad, onError]);

  return (
    <div
      className={cn(
        'relative overflow-hidden bg-gray-100',
        className
      )}
      style={{
        width: width || '100%',
        height: height || 'auto',
      }}
    >
      {/* Blur placeholder while loading */}
      {blurDataURL && !isLoaded && (
        <img
          src={blurDataURL}
          alt=""
          className="absolute inset-0 w-full h-full object-cover filter blur-lg scale-110"
          aria-hidden="true"
        />
      )}

      {/* Main image */}
      <img
        ref={setImageRef}
        src={imageSrc}
        alt={alt}
        width={width}
        height={height}
        className={cn(
          'transition-opacity duration-300',
          isLoaded ? 'opacity-100' : 'opacity-0',
          error && 'opacity-50'
        )}
        style={{
          objectFit,
          width: '100%',
          height: '100%'
        }}
        loading={priority ? 'eager' : 'lazy'}
        {...props}
      />

      {/* Loading skeleton */}
      {!isLoaded && !error && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}

      {/* Error state */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="text-center text-gray-400">
            <svg
              className="w-12 h-12 mx-auto mb-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <p className="text-sm">Failed to load image</p>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Picture component with WebP support
 * Automatically generates WebP sources with fallback
 */
export function LazyPicture({
  src,
  alt,
  className,
  width,
  height,
  sizes,
  priority = false,
  ...props
}) {
  const [isInView, setIsInView] = useState(false);
  const pictureRef = useRef(null);

  useEffect(() => {
    if (!pictureRef.current || priority) {
      if (priority) {
        setIsInView(true);
      }
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.01
      }
    );

    observer.observe(pictureRef.current);

    return () => observer.disconnect();
  }, [priority]);

  // Generate responsive image sources
  const generateSources = () => {
    if (!src || !isInView) return null;

    const sources = [];
    const baseUrl = src.replace(/\.(jpg|jpeg|png)$/i, '');
    const extension = src.match(/\.(jpg|jpeg|png)$/i)?.[0] || '.jpg';

    // Define responsive breakpoints
    const breakpoints = [
      { media: '(max-width: 640px)', width: 640 },
      { media: '(max-width: 768px)', width: 768 },
      { media: '(max-width: 1024px)', width: 1024 },
      { media: '(max-width: 1280px)', width: 1280 },
    ];

    // Generate WebP sources
    breakpoints.forEach(({ media, width: bpWidth }) => {
      sources.push(
        <source
          key={`webp-${bpWidth}`}
          media={media}
          srcSet={`${baseUrl}-${bpWidth}.webp`}
          type="image/webp"
        />
      );
    });

    // Generate fallback sources
    breakpoints.forEach(({ media, width: bpWidth }) => {
      sources.push(
        <source
          key={`fallback-${bpWidth}`}
          media={media}
          srcSet={`${baseUrl}-${bpWidth}${extension}`}
        />
      );
    });

    return sources;
  };

  return (
    <picture ref={pictureRef} className={className}>
      {generateSources()}
      <LazyImage
        src={src}
        alt={alt}
        width={width}
        height={height}
        sizes={sizes}
        priority={priority}
        {...props}
      />
    </picture>
  );
}

// Export default as LazyImage
export default LazyImage;