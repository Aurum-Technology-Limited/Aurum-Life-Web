import { useMemo, useCallback, memo } from 'react';

/**
 * Custom hook for common memoization patterns
 * Provides utilities for optimizing component performance
 */

/**
 * Memoize expensive computations with dependencies
 */
export function useComputedValue(computeFn, deps) {
  return useMemo(computeFn, deps);
}

/**
 * Create stable callbacks that don't cause re-renders
 */
export function useStableCallback(callback, deps) {
  return useCallback(callback, deps);
}

/**
 * Compare props for memo components
 * Handles common cases like ignoring functions
 */
export function arePropsEqual(prevProps, nextProps) {
  const keys = Object.keys(prevProps);
  
  for (let key of keys) {
    // Skip function comparisons (callbacks usually don't need to trigger re-renders)
    if (typeof prevProps[key] === 'function' && typeof nextProps[key] === 'function') {
      continue;
    }
    
    // Deep comparison for objects and arrays
    if (typeof prevProps[key] === 'object' && prevProps[key] !== null) {
      if (JSON.stringify(prevProps[key]) !== JSON.stringify(nextProps[key])) {
        return false;
      }
    } else if (prevProps[key] !== nextProps[key]) {
      return false;
    }
  }
  
  return true;
}

/**
 * Shallow compare props but ignore callback functions
 */
export function arePropsEqualIgnoreFunctions(prevProps, nextProps) {
  const prevKeys = Object.keys(prevProps);
  const nextKeys = Object.keys(nextProps);
  
  if (prevKeys.length !== nextKeys.length) {
    return false;
  }
  
  for (let key of prevKeys) {
    if (typeof prevProps[key] === 'function') {
      continue;
    }
    
    if (prevProps[key] !== nextProps[key]) {
      return false;
    }
  }
  
  return true;
}

/**
 * HOC to add memo with custom comparison
 */
export function withMemo(Component, customAreEqual = arePropsEqual) {
  return memo(Component, customAreEqual);
}

/**
 * Hook to memoize list items efficiently
 */
export function useMemoizedList(items, keyExtractor, deps = []) {
  return useMemo(() => {
    if (!items) return [];
    
    return items.map(item => ({
      ...item,
      key: keyExtractor(item)
    }));
  }, [items, ...deps]);
}

/**
 * Hook to create memoized event handlers for list items
 */
export function useListItemCallbacks(callbacks) {
  const memoizedCallbacks = {};
  
  Object.entries(callbacks).forEach(([name, callback]) => {
    memoizedCallbacks[name] = useCallback(callback, [callback]);
  });
  
  return memoizedCallbacks;
}