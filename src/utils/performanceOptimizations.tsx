/**
 * Performance Optimization Utilities for Aurum Life
 * Comprehensive performance monitoring, optimization, and caching strategies
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

// Performance Metrics Interface
export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  bundleSize: number;
  memoryUsage: number;
  cacheHitRate: number;
  errorRate: number;
  userInteractionDelay: number;
}

// Cache Management System
class CacheManager {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  private maxSize = 1000;
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  set(key: string, data: any, ttl: number = this.defaultTTL): void {
    // Implement LRU eviction if cache is full
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  get(key: string): any | null {
    const item = this.cache.get(key);
    if (!item) return null;

    // Check if expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    // Move to end for LRU
    this.cache.delete(key);
    this.cache.set(key, item);
    
    return item.data;
  }

  invalidate(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    const regex = new RegExp(pattern);
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    }
  }

  size(): number {
    return this.cache.size;
  }

  getHitRate(): number {
    // Implementation would track hits/misses
    return 0.85; // Placeholder
  }
}

export const cacheManager = new CacheManager();

// Performance Monitor
class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private maxMetrics = 100;

  recordMetric(metric: Partial<PerformanceMetrics>): void {
    const fullMetric: PerformanceMetrics = {
      loadTime: 0,
      renderTime: 0,
      bundleSize: 0,
      memoryUsage: this.getMemoryUsage(),
      cacheHitRate: cacheManager.getHitRate(),
      errorRate: 0,
      userInteractionDelay: 0,
      ...metric,
    };

    this.metrics.push(fullMetric);
    
    // Keep only recent metrics
    if (this.metrics.length > this.maxMetrics) {
      this.metrics.shift();
    }
  }

  getAverageMetrics(): PerformanceMetrics {
    if (this.metrics.length === 0) {
      return {
        loadTime: 0,
        renderTime: 0,
        bundleSize: 0,
        memoryUsage: 0,
        cacheHitRate: 0,
        errorRate: 0,
        userInteractionDelay: 0,
      };
    }

    const sum = this.metrics.reduce((acc, metric) => ({
      loadTime: acc.loadTime + metric.loadTime,
      renderTime: acc.renderTime + metric.renderTime,
      bundleSize: acc.bundleSize + metric.bundleSize,
      memoryUsage: acc.memoryUsage + metric.memoryUsage,
      cacheHitRate: acc.cacheHitRate + metric.cacheHitRate,
      errorRate: acc.errorRate + metric.errorRate,
      userInteractionDelay: acc.userInteractionDelay + metric.userInteractionDelay,
    }));

    return {
      loadTime: sum.loadTime / this.metrics.length,
      renderTime: sum.renderTime / this.metrics.length,
      bundleSize: sum.bundleSize / this.metrics.length,
      memoryUsage: sum.memoryUsage / this.metrics.length,
      cacheHitRate: sum.cacheHitRate / this.metrics.length,
      errorRate: sum.errorRate / this.metrics.length,
      userInteractionDelay: sum.userInteractionDelay / this.metrics.length,
    };
  }

  private getMemoryUsage(): number {
    if ('memory' in performance) {
      return (performance as any).memory.usedJSHeapSize / 1024 / 1024; // MB
    }
    return 0;
  }
}

export const performanceMonitor = new PerformanceMonitor();

// React Performance Hooks

/**
 * Hook for debouncing expensive operations
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Hook for throttling function calls
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const lastRun = useRef<number>(0);
  const timeout = useRef<NodeJS.Timeout>();

  return useCallback(
    ((...args: Parameters<T>) => {
      if (timeout.current) {
        clearTimeout(timeout.current);
      }

      const now = Date.now();
      if (now - lastRun.current >= delay) {
        callback(...args);
        lastRun.current = now;
      } else {
        timeout.current = setTimeout(() => {
          callback(...args);
          lastRun.current = Date.now();
        }, delay - (now - lastRun.current));
      }
    }) as T,
    [callback, delay]
  );
}

/**
 * Hook for memoizing expensive computations with cache
 */
export function useMemoizedComputation<T>(
  computeFn: () => T,
  deps: React.DependencyList,
  cacheKey?: string
): T {
  return useMemo(() => {
    if (cacheKey) {
      const cached = cacheManager.get(cacheKey);
      if (cached) return cached;
    }

    const startTime = performance.now();
    const result = computeFn();
    const endTime = performance.now();

    performanceMonitor.recordMetric({
      renderTime: endTime - startTime,
    });

    if (cacheKey) {
      cacheManager.set(cacheKey, result);
    }

    return result;
  }, deps);
}

/**
 * Hook for measuring component render performance
 */
export const useRenderPerformance = (componentName: string) => {
  const renderStart = useRef<number>(0);

  useEffect(() => {
    renderStart.current = performance.now();
  });

  useEffect(() => {
    const renderTime = performance.now() - renderStart.current;
    performanceMonitor.recordMetric({
      renderTime,
    });
    
    if (renderTime > 16) { // Slower than 60fps
      console.warn(`Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`);
    }
  });
};

/**
 * Hook for optimized async data fetching with caching
 */
export function useOptimizedFetch<T>(
  url: string,
  options?: RequestInit
): { data: T | null; loading: boolean; error: string | null } {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const cacheKey = `fetch_${url}_${JSON.stringify(options)}`;
    
    // Check cache first
    const cached = cacheManager.get(cacheKey);
    if (cached) {
      setData(cached);
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const startTime = performance.now();
        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        const endTime = performance.now();
        
        performanceMonitor.recordMetric({
          loadTime: endTime - startTime,
        });
        
        // Cache the result
        cacheManager.set(cacheKey, result);
        
        setData(result);
      } catch (err) {
        if (err instanceof Error && err.name !== 'AbortError') {
          setError(err.message);
          performanceMonitor.recordMetric({
            errorRate: 1,
          });
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    return () => controller.abort();
  }, [url, JSON.stringify(options)]);

  return { data, loading, error };
}

/**
 * Hook for intersection observer optimization
 */
export const useIntersectionObserver = (
  elementRef: React.RefObject<Element>,
  options?: IntersectionObserverInit
): boolean => {
  const [isIntersecting, setIsIntersecting] = useState(false);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
      },
      options
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [elementRef, options]);

  return isIntersecting;
};

// Bundle Optimization Utilities
export const preloadComponent = (importFn: () => Promise<any>) => {
  // Preload component when idle
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      importFn();
    });
  } else {
    setTimeout(() => {
      importFn();
    }, 0);
  }
};

export const prefetchRoute = (route: string) => {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = route;
  document.head.appendChild(link);
};

// Memory Management
export const clearUnusedData = () => {
  // Clear old cache entries
  cacheManager.invalidate();
  
  // Force garbage collection if available
  if ('gc' in window) {
    (window as any).gc();
  }
};

// Service Worker Optimization
export const registerOptimizedServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
        updateViaCache: 'imports',
      });
      
      console.log('Service Worker registered:', registration);
      
      // Listen for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New version available
              console.log('New version available');
            }
          });
        }
      });
      
      return registration;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
    }
  }
};

// Image Optimization
export const optimizeImage = (
  src: string,
  width?: number,
  height?: number,
  quality: number = 80
): string => {
  // If using a service like Cloudinary or similar
  const params = new URLSearchParams();
  if (width) params.set('w', width.toString());
  if (height) params.set('h', height.toString());
  params.set('q', quality.toString());
  params.set('f', 'auto'); // Auto format
  
  return `${src}?${params.toString()}`;
};

// Performance Reporting
export const reportPerformanceMetrics = () => {
  const metrics = performanceMonitor.getAverageMetrics();
  
  // Report to analytics service
  console.log('Performance Metrics:', metrics);
  
  // You could send to an analytics service here
  // analytics.track('performance_metrics', metrics);
  
  return metrics;
};

// Critical Performance Checks
export const runPerformanceAudit = () => {
  const issues: string[] = [];
  
  // Check bundle size
  if (performance.getEntriesByType('navigation').length > 0) {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const loadTime = navigation.loadEventEnd - navigation.fetchStart;
    
    if (loadTime > 3000) {
      issues.push(`Slow page load: ${loadTime.toFixed(0)}ms`);
    }
  }
  
  // Check memory usage
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    const usedMB = memory.usedJSHeapSize / 1024 / 1024;
    
    if (usedMB > 50) {
      issues.push(`High memory usage: ${usedMB.toFixed(1)}MB`);
    }
  }
  
  // Check cache hit rate
  const cacheHitRate = cacheManager.getHitRate();
  if (cacheHitRate < 0.7) {
    issues.push(`Low cache hit rate: ${(cacheHitRate * 100).toFixed(1)}%`);
  }
  
  return issues;
};

export default {
  cacheManager,
  performanceMonitor,
  useDebounce,
  useThrottle,
  useMemoizedComputation,
  useRenderPerformance,
  useOptimizedFetch,
  useIntersectionObserver,
  preloadComponent,
  prefetchRoute,
  clearUnusedData,
  registerOptimizedServiceWorker,
  optimizeImage,
  reportPerformanceMetrics,
  runPerformanceAudit,
};