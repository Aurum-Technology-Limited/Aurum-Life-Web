/**
 * Timeout utilities to prevent infinite loops and hanging operations
 */

export interface TimeoutConfig {
  timeout: number;
  onTimeout?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Wraps a promise with a timeout to prevent hanging
 */
export function withTimeout<T>(
  promise: Promise<T>,
  config: TimeoutConfig
): Promise<T> {
  const { timeout, onTimeout, onError } = config;
  
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      const timeoutError = new Error(`Operation timed out after ${timeout}ms`);
      onTimeout?.();
      onError?.(timeoutError);
      reject(timeoutError);
    }, timeout);

    promise
      .then((result) => {
        clearTimeout(timeoutId);
        resolve(result);
      })
      .catch((error) => {
        clearTimeout(timeoutId);
        onError?.(error);
        reject(error);
      });
  });
}

/**
 * Creates a safe async function that won't hang indefinitely
 */
export function makeSafeAsync<T extends any[], R>(
  fn: (...args: T) => Promise<R>,
  config: TimeoutConfig
) {
  return async (...args: T): Promise<R> => {
    try {
      return await withTimeout(fn(...args), config);
    } catch (error) {
      console.log('Safe async function failed:', error);
      throw error;
    }
  };
}

/**
 * Debounced function with timeout protection
 */
export function debounceWithTimeout<T extends any[]>(
  fn: (...args: T) => void,
  delay: number,
  maxWait: number = 5000
) {
  let timeoutId: NodeJS.Timeout;
  let maxTimeoutId: NodeJS.Timeout;
  
  return (...args: T) => {
    // Clear existing timeouts
    clearTimeout(timeoutId);
    clearTimeout(maxTimeoutId);
    
    // Set debounce timeout
    timeoutId = setTimeout(() => {
      try {
        fn(...args);
      } catch (error) {
        console.log('Debounced function error (non-critical):', error);
      }
    }, delay);
    
    // Set maximum wait timeout
    maxTimeoutId = setTimeout(() => {
      clearTimeout(timeoutId);
      try {
        fn(...args);
      } catch (error) {
        console.log('Max wait function error (non-critical):', error);
      }
    }, maxWait);
  };
}

/**
 * Race condition resolver - takes first resolved promise
 */
export function raceWithTimeout<T>(
  promises: Promise<T>[],
  timeout: number,
  fallback?: T
): Promise<T> {
  const timeoutPromise = new Promise<T>((_, reject) => {
    setTimeout(() => {
      reject(new Error(`Race condition timeout after ${timeout}ms`));
    }, timeout);
  });

  return Promise.race([...promises, timeoutPromise]).catch((error) => {
    console.log('Race condition failed:', error);
    if (fallback !== undefined) {
      return fallback;
    }
    throw error;
  });
}

/**
 * Safe interval that automatically clears on timeout
 */
export function createSafeInterval(
  callback: () => void,
  interval: number,
  maxDuration: number = 30000
): () => void {
  const intervalId = setInterval(() => {
    try {
      callback();
    } catch (error) {
      console.log('Safe interval callback error (non-critical):', error);
    }
  }, interval);

  const timeoutId = setTimeout(() => {
    clearInterval(intervalId);
    console.log('Safe interval auto-cleared after max duration');
  }, maxDuration);

  // Return cleanup function
  return () => {
    clearInterval(intervalId);
    clearTimeout(timeoutId);
  };
}

/**
 * Emergency circuit breaker for critical operations
 */
export class EmergencyCircuitBreaker {
  private static failures = new Map<string, number>();
  private static lastReset = Date.now();
  
  static async execute<T>(
    key: string,
    operation: () => Promise<T>,
    maxFailures: number = 3,
    resetTimeout: number = 60000
  ): Promise<T> {
    // Auto-reset failures after timeout
    if (Date.now() - this.lastReset > resetTimeout) {
      this.failures.clear();
      this.lastReset = Date.now();
    }
    
    const currentFailures = this.failures.get(key) || 0;
    
    if (currentFailures >= maxFailures) {
      throw new Error(`Circuit breaker open for ${key} (${currentFailures} failures)`);
    }
    
    try {
      const result = await withTimeout(operation(), {
        timeout: 5000,
        onTimeout: () => console.log(`Circuit breaker timeout for ${key}`),
        onError: (error) => console.log(`Circuit breaker error for ${key}:`, error)
      });
      
      // Reset failures on success
      this.failures.delete(key);
      return result;
    } catch (error) {
      // Increment failures
      this.failures.set(key, currentFailures + 1);
      throw error;
    }
  }
  
  static reset(): void {
    this.failures.clear();
    this.lastReset = Date.now();
  }
  
  static getStatus(key: string): { failures: number; isOpen: boolean } {
    const failures = this.failures.get(key) || 0;
    return {
      failures,
      isOpen: failures >= 3
    };
  }
}