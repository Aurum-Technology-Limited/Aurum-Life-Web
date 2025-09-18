/**
 * Circuit breaker utility to prevent long-running operations
 */

interface CircuitBreakerOptions {
  timeout: number;
  name?: string;
}

class CircuitBreaker {
  private static breakers = new Map<string, number>();
  
  // For async operations
  static async execute<T>(
    operation: () => Promise<T>,
    options: CircuitBreakerOptions
  ): Promise<T> {
    const { timeout = 5000, name = 'unnamed' } = options; // Default timeout
    
    // Check if this breaker is already tripped
    const tripTime = this.breakers.get(name);
    if (tripTime && Date.now() - tripTime < 10000) { // 10 second cooldown (reduced from 30)
      console.log(`Circuit breaker ${name} is cooling down, allowing retry...`);
      // Allow retry after cooldown instead of blocking
    }
    
    return new Promise<T>((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        console.warn(`Circuit breaker ${name} tripped after ${timeout}ms`);
        this.breakers.set(name, Date.now());
        reject(new Error(`Operation ${name} timed out after ${timeout}ms`));
      }, timeout);
      
      try {
        const result = operation();
        if (result && typeof result.then === 'function') {
          // It's a Promise
          result
            .then((res) => {
              clearTimeout(timeoutId);
              this.breakers.delete(name);
              resolve(res);
            })
            .catch((error) => {
              clearTimeout(timeoutId);
              this.breakers.set(name, Date.now());
              reject(error);
            });
        } else {
          // It's a synchronous result - cast to expected type
          clearTimeout(timeoutId);
          this.breakers.delete(name);
          resolve(result as T);
        }
      } catch (error) {
        clearTimeout(timeoutId);
        this.breakers.set(name, Date.now());
        reject(error);
      }
    });
  }

  // For synchronous operations (like React components)
  static executeSync<T>(
    operation: () => T,
    fallback: T,
    name: string = 'unnamed'
  ): T {
    try {
      // Check if this breaker is tripped
      const tripTime = this.breakers.get(name);
      if (tripTime && Date.now() - tripTime < 5000) { // 5 second cooldown for sync operations
        console.log(`Circuit breaker ${name} is tripped, using fallback`);
        return fallback;
      }
      
      const result = operation();
      // Reset breaker on success
      this.breakers.delete(name);
      return result;
    } catch (error) {
      console.log(`Circuit breaker ${name} caught error:`, error);
      // Trip breaker on failure
      this.breakers.set(name, Date.now());
      return fallback;
    }
  }
  
  static reset(name?: string) {
    try {
      if (name) {
        this.breakers.delete(name);
        console.log(`Circuit breaker ${name} reset`);
      } else {
        this.breakers.clear();
        console.log('All circuit breakers reset');
      }
    } catch (error) {
      console.log('Circuit breaker reset error (non-critical):', error);
    }
  }

  static emergencyReset() {
    try {
      console.log('Emergency circuit breaker reset initiated');
      this.breakers = new Map();
      
      // Clear any potential hanging timeouts
      if (typeof window !== 'undefined') {
        for (let i = 1; i < 1000; i++) {
          try {
            clearTimeout(i);
          } catch (e) {
            // Ignore - some IDs won't exist
          }
        }
      }
      
      console.log('Emergency circuit breaker reset completed');
    } catch (error) {
      console.log('Emergency reset error (non-critical):', error);
    }
  }
  
  static isTripped(name: string): boolean {
    const tripTime = this.breakers.get(name);
    return tripTime ? Date.now() - tripTime < 10000 : false;
  }
}

export default CircuitBreaker;

// Utility function for wrapping operations with timeout
export function withTimeout<T>(
  operation: () => Promise<T>,
  timeoutMs: number,
  name?: string
): Promise<T> {
  return CircuitBreaker.execute(operation, {
    timeout: timeoutMs || 5000, // Ensure timeout is never undefined
    name: name || 'operation'
  });
}

// Quick timeout for critical operations
export function withQuickTimeout<T>(
  operation: () => Promise<T> | T,
  name?: string
): Promise<T> {
  const wrappedOperation = () => {
    const result = operation();
    if (result && typeof result.then === 'function') {
      return result as Promise<T>;
    }
    return Promise.resolve(result as T);
  };
  return withTimeout(wrappedOperation, 3000, name); // Increased from 1000ms
}

// Emergency timeout for app initialization
export function withEmergencyTimeout<T>(
  operation: () => Promise<T> | T,
  name?: string
): Promise<T> {
  const wrappedOperation = () => {
    const result = operation();
    if (result && typeof result.then === 'function') {
      return result as Promise<T>;
    }
    return Promise.resolve(result as T);
  };
  return withTimeout(wrappedOperation, 5000, name); // Increased to 5000ms for better stability
}