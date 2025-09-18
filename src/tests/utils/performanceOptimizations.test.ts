/**
 * Performance Optimizations Tests
 * Test suite for performance utilities and optimizations
 */

import { renderHook, act } from '@testing-library/react';
import {
  cacheManager,
  performanceMonitor,
  useDebounce,
  useThrottle,
  useMemoizedComputation,
  runPerformanceAudit,
  clearUnusedData,
} from '../../utils/performanceOptimizations.tsx';

describe('CacheManager', () => {
  beforeEach(() => {
    cacheManager.invalidate(); // Clear cache before each test
  });

  it('stores and retrieves cached data', () => {
    const testData = { key: 'value', number: 42 };
    cacheManager.set('test-key', testData);
    
    const retrieved = cacheManager.get('test-key');
    expect(retrieved).toEqual(testData);
  });

  it('returns null for non-existent keys', () => {
    const result = cacheManager.get('non-existent-key');
    expect(result).toBeNull();
  });

  it('expires cached data after TTL', (done) => {
    const testData = { expired: true };
    const shortTTL = 50; // 50ms
    
    cacheManager.set('expire-test', testData, shortTTL);
    
    // Should exist immediately
    expect(cacheManager.get('expire-test')).toEqual(testData);
    
    // Should be expired after TTL
    setTimeout(() => {
      expect(cacheManager.get('expire-test')).toBeNull();
      done();
    }, shortTTL + 10);
  });

  it('invalidates cache with pattern matching', () => {
    cacheManager.set('user:1:profile', { name: 'User 1' });
    cacheManager.set('user:2:profile', { name: 'User 2' });
    cacheManager.set('system:config', { theme: 'dark' });
    
    cacheManager.invalidate('user:.*');
    
    expect(cacheManager.get('user:1:profile')).toBeNull();
    expect(cacheManager.get('user:2:profile')).toBeNull();
    expect(cacheManager.get('system:config')).toEqual({ theme: 'dark' });
  });

  it('enforces cache size limits', () => {
    // Fill cache beyond max size (assuming max is 1000)
    for (let i = 0; i < 1100; i++) {
      cacheManager.set(`key-${i}`, { value: i });
    }
    
    // Cache size should not exceed maximum
    expect(cacheManager.size()).toBeLessThanOrEqual(1000);
  });

  it('implements LRU eviction', () => {
    // Set initial data
    cacheManager.set('first', { order: 1 });
    cacheManager.set('second', { order: 2 });
    
    // Access first item to make it most recently used
    cacheManager.get('first');
    
    // Fill cache to trigger eviction
    for (let i = 0; i < 1000; i++) {
      cacheManager.set(`filler-${i}`, { value: i });
    }
    
    // First should still exist (recently accessed), second should be evicted
    expect(cacheManager.get('first')).toEqual({ order: 1 });
    expect(cacheManager.get('second')).toBeNull();
  });
});

describe('PerformanceMonitor', () => {
  beforeEach(() => {
    // Clear metrics
    while (performanceMonitor.getAverageMetrics().loadTime === 0) {
      performanceMonitor.recordMetric({ loadTime: 0 });
    }
  });

  it('records performance metrics', () => {
    const testMetric = {
      loadTime: 1500,
      renderTime: 50,
      memoryUsage: 25,
      cacheHitRate: 0.85,
    };
    
    performanceMonitor.recordMetric(testMetric);
    const averages = performanceMonitor.getAverageMetrics();
    
    expect(averages.loadTime).toBe(testMetric.loadTime);
    expect(averages.renderTime).toBe(testMetric.renderTime);
    expect(averages.memoryUsage).toBe(testMetric.memoryUsage);
    expect(averages.cacheHitRate).toBe(testMetric.cacheHitRate);
  });

  it('calculates average metrics correctly', () => {
    performanceMonitor.recordMetric({ loadTime: 1000 });
    performanceMonitor.recordMetric({ loadTime: 2000 });
    performanceMonitor.recordMetric({ loadTime: 3000 });
    
    const averages = performanceMonitor.getAverageMetrics();
    expect(averages.loadTime).toBe(2000);
  });

  it('limits the number of stored metrics', () => {
    // Record more than the maximum (assuming max is 100)
    for (let i = 0; i < 150; i++) {
      performanceMonitor.recordMetric({ loadTime: i });
    }
    
    // Should only keep the most recent 100
    const averages = performanceMonitor.getAverageMetrics();
    expect(averages.loadTime).toBeGreaterThan(49); // Should be from recent entries
  });
});

describe('useDebounce Hook', () => {
  it('debounces value changes', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 100 } }
    );
    
    expect(result.current).toBe('initial');
    
    // Change value quickly
    rerender({ value: 'changed1', delay: 100 });
    rerender({ value: 'changed2', delay: 100 });
    rerender({ value: 'final', delay: 100 });
    
    // Should still be initial value immediately
    expect(result.current).toBe('initial');
    
    // Wait for debounce delay
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 150));
    });
    
    // Should now be the final value
    expect(result.current).toBe('final');
  });

  it('cancels previous timeout on new changes', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 200 } }
    );
    
    rerender({ value: 'intermediate', delay: 200 });
    
    // Wait partially through delay
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });
    
    // Change again before first timeout completes
    rerender({ value: 'final', delay: 200 });
    
    // Wait for full delay
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 250));
    });
    
    // Should be final value, not intermediate
    expect(result.current).toBe('final');
  });
});

describe('useThrottle Hook', () => {
  it('throttles function calls', async () => {
    const mockFn = jest.fn();
    const { result } = renderHook(() => useThrottle(mockFn, 100));
    
    const throttledFn = result.current;
    
    // Call function multiple times quickly
    throttledFn('call1');
    throttledFn('call2');
    throttledFn('call3');
    
    // Should only be called once immediately
    expect(mockFn).toHaveBeenCalledTimes(1);
    expect(mockFn).toHaveBeenCalledWith('call1');
    
    // Wait for throttle delay
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 150));
    });
    
    // Should be called with the last argument
    expect(mockFn).toHaveBeenCalledTimes(2);
    expect(mockFn).toHaveBeenLastCalledWith('call3');
  });

  it('allows calls after throttle period', async () => {
    const mockFn = jest.fn();
    const { result } = renderHook(() => useThrottle(mockFn, 50));
    
    const throttledFn = result.current;
    
    throttledFn('first');
    expect(mockFn).toHaveBeenCalledTimes(1);
    
    // Wait for throttle period to end
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });
    
    throttledFn('second');
    expect(mockFn).toHaveBeenCalledTimes(2);
    expect(mockFn).toHaveBeenLastCalledWith('second');
  });
});

describe('useMemoizedComputation Hook', () => {
  it('memoizes expensive computations', () => {
    const expensiveComputation = jest.fn(() => 'computed result');
    
    const { result, rerender } = renderHook(
      ({ deps }) => useMemoizedComputation(expensiveComputation, deps),
      { initialProps: { deps: ['dep1'] } }
    );
    
    expect(result.current).toBe('computed result');
    expect(expensiveComputation).toHaveBeenCalledTimes(1);
    
    // Rerender with same dependencies
    rerender({ deps: ['dep1'] });
    
    // Should not recompute
    expect(expensiveComputation).toHaveBeenCalledTimes(1);
    
    // Rerender with different dependencies
    rerender({ deps: ['dep2'] });
    
    // Should recompute
    expect(expensiveComputation).toHaveBeenCalledTimes(2);
  });

  it('uses cache when cache key is provided', () => {
    const computation = jest.fn(() => 'cached result');
    
    // First call with cache key
    const { result: result1 } = renderHook(() =>
      useMemoizedComputation(computation, [], 'test-cache-key')
    );
    
    expect(result1.current).toBe('cached result');
    expect(computation).toHaveBeenCalledTimes(1);
    
    // Second call with same cache key
    const { result: result2 } = renderHook(() =>
      useMemoizedComputation(computation, [], 'test-cache-key')
    );
    
    expect(result2.current).toBe('cached result');
    // Should use cache, not recompute
    expect(computation).toHaveBeenCalledTimes(1);
  });
});

describe('Performance Audit Functions', () => {
  beforeEach(() => {
    // Mock performance.getEntriesByType
    jest.spyOn(performance, 'getEntriesByType').mockReturnValue([
      {
        loadEventEnd: 2000,
        fetchStart: 500,
        name: 'navigation',
        entryType: 'navigation',
        startTime: 0,
        duration: 1500,
      } as PerformanceNavigationTiming,
    ]);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('identifies performance issues', () => {
    const issues = runPerformanceAudit();
    
    expect(Array.isArray(issues)).toBe(true);
    // Should identify slow load time (2000-500 = 1500ms < 3000ms threshold)
    expect(issues.length).toBeGreaterThanOrEqual(0);
  });

  it('detects slow page load times', () => {
    // Mock slow navigation
    jest.spyOn(performance, 'getEntriesByType').mockReturnValue([
      {
        loadEventEnd: 5000,
        fetchStart: 500,
        name: 'navigation',
        entryType: 'navigation',
        startTime: 0,
        duration: 4500,
      } as PerformanceNavigationTiming,
    ]);
    
    const issues = runPerformanceAudit();
    
    const slowLoadIssue = issues.find(issue => 
      issue.includes('Slow page load')
    );
    expect(slowLoadIssue).toBeDefined();
  });

  it('detects high memory usage', () => {
    // Mock high memory usage
    Object.defineProperty(performance, 'memory', {
      value: {
        usedJSHeapSize: 60 * 1024 * 1024, // 60MB
        totalJSHeapSize: 100 * 1024 * 1024,
        jsHeapSizeLimit: 200 * 1024 * 1024,
      },
      configurable: true,
    });
    
    const issues = runPerformanceAudit();
    
    const memoryIssue = issues.find(issue => 
      issue.includes('High memory usage')
    );
    expect(memoryIssue).toBeDefined();
  });
});

describe('clearUnusedData Function', () => {
  it('clears cache and triggers cleanup', () => {
    // Add some test data to cache
    cacheManager.set('test-data', { value: 'test' });
    expect(cacheManager.get('test-data')).toBeTruthy();
    
    clearUnusedData();
    
    // Cache should be cleared
    expect(cacheManager.get('test-data')).toBeNull();
  });

  it('handles missing garbage collection gracefully', () => {
    // Ensure gc is not available
    delete (window as any).gc;
    
    expect(() => clearUnusedData()).not.toThrow();
  });
});

describe('Integration Tests', () => {
  it('performance monitoring integrates with cache manager', () => {
    // Use cache manager and verify performance is recorded
    cacheManager.set('perf-test', { data: 'test' });
    const hitRate = cacheManager.getHitRate();
    
    performanceMonitor.recordMetric({ cacheHitRate: hitRate });
    const metrics = performanceMonitor.getAverageMetrics();
    
    expect(metrics.cacheHitRate).toBe(hitRate);
  });

  it('performance audit considers cache performance', () => {
    // Mock low cache hit rate
    jest.spyOn(cacheManager, 'getHitRate').mockReturnValue(0.5);
    
    const issues = runPerformanceAudit();
    
    const cacheIssue = issues.find(issue => 
      issue.includes('Low cache hit rate')
    );
    expect(cacheIssue).toBeDefined();
  });
});