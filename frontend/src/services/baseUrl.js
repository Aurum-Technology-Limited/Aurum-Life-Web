/**
 * @fileoverview Backend URL Resolution Service
 * 
 * Provides centralized, runtime-safe backend URL resolution with multiple fallback strategies.
 * Handles edge cases like misconfigured environment variables and development/production environments.
 * 
 * @version 1.0.0
 * @author Aurum Life Development Team
 */

// Configuration constants
const CONFIG = {
  // Known problematic hosts that should be avoided
  INVALID_HOSTS: /^(none|home|www)\.preview\.emergentagent\.com$/i,
  
  // Production fallback URL
  FALLBACK_URL: 'https://aurum-life-os.preview.emergentagent.com',
  
  // Debug mode flag
  DEBUG_MODE: process.env.NODE_ENV === 'development'
};

/**
 * Logger utility for URL resolution debugging
 */
class URLLogger {
  /**
   * Logs debug information if debug mode is enabled
   * @param {string} level - Log level ('info', 'warn', 'error')
   * @param {string} message - Log message
   * @param {any} data - Optional data to log
   */
  static log(level, message, data = null) {
    if (!CONFIG.DEBUG_MODE) return;
    
    const emoji = {
      info: '🔧',
      warn: '⚠️',
      error: '❌',
      success: '✅',
      fallback: '🚨'
    };
    
    console.log(`${emoji[level] || '📝'} BaseURL ${message}`, data || '');
  }
}

/**
 * Environment variable resolver with multiple access strategies
 */
class EnvironmentResolver {
  /**
   * Attempts to resolve environment variable using multiple strategies
   * @returns {string|null} Environment URL or null if not found
   */
  static resolveEnvironmentURL() {
    // Strategy 1: Standard process.env
    if (process.env.REACT_APP_BACKEND_URL) {
      return process.env.REACT_APP_BACKEND_URL;
    }
    
    // Strategy 2: Window-attached process (for some build systems)
    if (typeof window !== 'undefined' && window.process?.env?.REACT_APP_BACKEND_URL) {
      return window.process.env.REACT_APP_BACKEND_URL;
    }
    
    // Strategy 3: Import.meta (for Vite and modern bundlers)
    if (typeof import.meta !== 'undefined' && import.meta.env?.REACT_APP_BACKEND_URL) {
      return import.meta.env.REACT_APP_BACKEND_URL;
    }
    
    return null;
  }
}

/**
 * URL validator and sanitizer
 */
class URLValidator {
  /**
   * Validates and sanitizes a URL
   * @param {string} url - URL to validate
   * @returns {Object} Validation result with url and isValid properties
   */
  static validateURL(url) {
    if (!url || typeof url !== 'string') {
      return { url: null, isValid: false, reason: 'Empty or invalid URL' };
    }
    
    try {
      const parsedURL = new URL(url);
      
      // Check for known problematic hosts
      if (CONFIG.INVALID_HOSTS.test(parsedURL.host)) {
        return { 
          url: null, 
          isValid: false, 
          reason: `Invalid host: ${parsedURL.host}` 
        };
      }
      
      // Remove trailing slash and return sanitized URL
      const sanitizedURL = url.replace(/\/$/, '');
      return { 
        url: sanitizedURL, 
        isValid: true, 
        host: parsedURL.host 
      };
      
    } catch (error) {
      return { 
        url: null, 
        isValid: false, 
        reason: `URL parse error: ${error.message}` 
      };
    }
  }
}

/**
 * Main backend URL resolution function
 * 
 * Resolution strategy:
 * 1. Try environment variables (multiple access methods)
 * 2. Fallback to window.location.origin (for same-domain deployments)
 * 3. Use hardcoded production fallback as last resort
 * 
 * @returns {string} Resolved backend base URL
 */
export function getBackendBaseUrl() {
  try {
    URLLogger.log('info', 'Starting URL resolution process');
    
    // Step 1: Try environment variable resolution
    const envUrl = EnvironmentResolver.resolveEnvironmentURL();
    URLLogger.log('info', 'Environment URL candidates:', {
      processEnv: process.env.REACT_APP_BACKEND_URL,
      windowEnv: typeof window !== 'undefined' ? window.process?.env?.REACT_APP_BACKEND_URL : 'N/A',
      importMeta: typeof import.meta !== 'undefined' ? import.meta.env?.REACT_APP_BACKEND_URL : 'N/A',
      resolved: envUrl
    });
    
    if (envUrl) {
      const validation = URLValidator.validateURL(envUrl);
      if (validation.isValid) {
        URLLogger.log('success', 'Resolved from environment:', validation.url);
        return validation.url;
      } else {
        URLLogger.log('warn', 'Environment URL invalid:', validation.reason);
      }
    }
    
    // Step 2: Fallback to window.location.origin
    if (typeof window !== 'undefined' && window.location?.origin) {
      const windowOrigin = window.location.origin.replace(/\/$/, '');
      const validation = URLValidator.validateURL(windowOrigin);
      
      if (validation.isValid) {
        URLLogger.log('warn', 'Using window.origin fallback:', validation.url);
        return validation.url;
      } else {
        URLLogger.log('error', 'Window origin invalid:', validation.reason);
      }
    }
    
  } catch (error) {
    URLLogger.log('error', 'URL resolution failed:', error.message);
  }
  
  // Step 3: Last resort fallback
  URLLogger.log('fallback', 'Using hardcoded fallback:', CONFIG.FALLBACK_URL);
  return CONFIG.FALLBACK_URL;
}

/**
 * Development helper to get URL resolution debugging info
 * @returns {Object} Debugging information object
 */
export function getURLResolutionDebugInfo() {
  return {
    environmentURL: EnvironmentResolver.resolveEnvironmentURL(),
    windowOrigin: typeof window !== 'undefined' ? window.location?.origin : 'N/A',
    fallbackURL: CONFIG.FALLBACK_URL,
    resolvedURL: getBackendBaseUrl(),
    timestamp: new Date().toISOString()
  };
}

// Export configuration for testing purposes
export const URLConfig = CONFIG;