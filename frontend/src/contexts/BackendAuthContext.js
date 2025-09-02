/**
 * @fileoverview Backend Authentication Context
 * 
 * Provides centralized authentication state management with Supabase integration,
 * automatic token refresh, retry mechanisms, and comprehensive error handling.
 * 
 * @version 1.0.0
 * @author Aurum Life Development Team
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getBackendBaseUrl } from '../services/baseUrl';

// Configuration constants
const AUTH_CONFIG = {
  TOKEN_KEY: 'auth_token',
  REFRESH_TOKEN_KEY: 'refresh_token',
  TOKEN_EXPIRY_KEY: 'auth_token_exp',
  PREFILL_EMAIL_KEY: 'auth_prefill_email',
  DUPLICATE_SIGNAL_KEY: 'auth_duplicate_signal',
  
  // Retry configuration
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 400, // ms
  
  // Token refresh configuration
  REFRESH_THRESHOLD: 60000, // Refresh 1 minute before expiry
  HEALTH_CHECK_INTERVAL: 120000, // 2 minutes
  
  // Request timeout
  REQUEST_TIMEOUT: 10000 // 10 seconds
};

// Error messages
const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please try again.',
  LOGIN_FAILED: 'Login failed',
  REGISTRATION_FAILED: 'Registration failed',
  PROFILE_FETCH_FAILED: 'Failed to get user profile',
  LEGACY_ACCOUNT: 'Your old account is no longer supported. Please create a new account.',
  PASSWORD_RESET_FAILED: 'Failed to send password reset email'
};

/**
 * Create authentication context
 */
const AuthContext = createContext();

/**
 * Custom hook to use authentication context
 * @returns {Object} Authentication context value
 * @throws {Error} If used outside AuthProvider
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * Token management utility class
 */
class TokenManager {
  /**
   * Retrieves stored authentication token
   * @returns {string|null} Auth token or null
   */
  static getToken() {
    return localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
  }
  
  /**
   * Retrieves stored refresh token
   * @returns {string|null} Refresh token or null
   */
  static getRefreshToken() {
    return localStorage.getItem(AUTH_CONFIG.REFRESH_TOKEN_KEY);
  }
  
  /**
   * Retrieves token expiry timestamp
   * @returns {number} Expiry timestamp or 0
   */
  static getTokenExpiry() {
    return Number(localStorage.getItem(AUTH_CONFIG.TOKEN_EXPIRY_KEY) || 0);
  }
  
  /**
   * Stores authentication tokens
   * @param {string} accessToken - Access token
   * @param {string} refreshToken - Refresh token
   * @param {number} expiresIn - Token expiry in seconds
   */
  static storeTokens(accessToken, refreshToken = null, expiresIn = null) {
    localStorage.setItem(AUTH_CONFIG.TOKEN_KEY, accessToken);
    
    if (refreshToken) {
      localStorage.setItem(AUTH_CONFIG.REFRESH_TOKEN_KEY, refreshToken);
    }
    
    if (expiresIn) {
      const expiryTime = Date.now() + (expiresIn * 1000);
      localStorage.setItem(AUTH_CONFIG.TOKEN_EXPIRY_KEY, expiryTime.toString());
    }
  }
  
  /**
   * Clears all stored tokens
   */
  static clearTokens() {
    localStorage.removeItem(AUTH_CONFIG.TOKEN_KEY);
    localStorage.removeItem(AUTH_CONFIG.REFRESH_TOKEN_KEY);
    localStorage.removeItem(AUTH_CONFIG.TOKEN_EXPIRY_KEY);
  }
  
  /**
   * Checks if token is expired or near expiry
   * @returns {boolean} True if token needs refresh
   */
  static needsRefresh() {
    const expiry = this.getTokenExpiry();
    if (!expiry) return false;
    
    return Date.now() > (expiry - AUTH_CONFIG.REFRESH_THRESHOLD);
  }
}

/**
 * HTTP request utility with timeout and error handling
 */
class HTTPClient {
  /**
   * Makes HTTP request with timeout and error handling
   * @param {string} url - Request URL
   * @param {Object} options - Fetch options
   * @returns {Promise<Response>} Fetch response
   */
  static async fetchWithTimeout(url, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), AUTH_CONFIG.REQUEST_TIMEOUT);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }
  
  /**
   * Safely parses JSON response
   * @param {Response} response - Fetch response
   * @returns {Promise<Object>} Parsed JSON or empty object
   */
  static async safeJSONParse(response) {
    try {
      return await response.json();
    } catch {
      return {};
    }
  }
}

/**
 * User data fetching service with retry mechanism
 */
class UserService {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }
  
  /**
   * Fetches user data with retry mechanism
   * @param {string} authToken - Authentication token
   * @param {number} maxAttempts - Maximum retry attempts
   * @param {number} delayMs - Delay between retries
   * @returns {Promise<Object>} User fetch result
   */
  async fetchUserWithRetry(authToken, maxAttempts = AUTH_CONFIG.MAX_RETRY_ATTEMPTS, delayMs = AUTH_CONFIG.RETRY_DELAY) {
    let lastError = null;
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const response = await HTTPClient.fetchWithTimeout(`${this.baseURL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const userData = await HTTPClient.safeJSONParse(response);
          return { success: true, data: userData };
        } else {
          const errorData = await HTTPClient.safeJSONParse(response);
          lastError = new Error(errorData?.detail || `Request failed with status ${response.status}`);
        }
        
      } catch (error) {
        lastError = error;
      }
      
      // Wait before retry (except on last attempt)
      if (attempt < maxAttempts) {
        await this.sleep(delayMs);
      }
    }
    
    return { success: false, error: lastError };
  }
  
  /**
   * Sleep utility for delays
   * @param {number} ms - Milliseconds to sleep
   * @returns {Promise} Sleep promise
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Authentication service class
 */
class AuthService {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.userService = new UserService(baseURL);
  }
  
  /**
   * Attempts user login
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} Login result
   */
  async login(email, password) {
    try {
      const response = await HTTPClient.fetchWithTimeout(`${this.baseURL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      
      const loginData = await HTTPClient.safeJSONParse(response);
      
      if (response.ok && loginData.access_token) {
        TokenManager.storeTokens(
          loginData.access_token,
          loginData.refresh_token,
          loginData.expires_in || 3600
        );
        
        // Fetch user profile
        const userResult = await this.userService.fetchUserWithRetry(loginData.access_token);
        if (userResult.success) {
          return { success: true, message: 'Login successful!', user: userResult.data };
        } else {
          return { success: false, error: ERROR_MESSAGES.PROFILE_FETCH_FAILED };
        }
      } else {
        let errorMessage = loginData.detail || ERROR_MESSAGES.LOGIN_FAILED;
        if (/legacy/i.test(errorMessage)) {
          errorMessage = ERROR_MESSAGES.LEGACY_ACCOUNT;
        }
        return { success: false, error: errorMessage };
      }
      
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: ERROR_MESSAGES.NETWORK_ERROR };
    }
  }
  
  /**
   * Attempts user registration
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} Registration result
   */
  async register(userData) {
    try {
      const response = await HTTPClient.fetchWithTimeout(`${this.baseURL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      
      const data = await HTTPClient.safeJSONParse(response);
      
      if (response.ok) {
        return { success: true, message: 'Account created successfully!' };
      } else {
        const isDuplicate = response.status === 409 || 
                           (data.detail && data.detail.toLowerCase().includes('already exists'));
        
        return {
          success: false,
          error: data.detail || ERROR_MESSAGES.REGISTRATION_FAILED,
          duplicate: isDuplicate,
          code: response.status
        };
      }
      
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: ERROR_MESSAGES.NETWORK_ERROR };
    }
  }
  
  /**
   * Sends forgot password request
   * @param {string} email - User email
   * @returns {Promise<Object>} Forgot password result
   */
  async forgotPassword(email) {
    try {
      const response = await HTTPClient.fetchWithTimeout(`${this.baseURL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Origin': typeof window !== 'undefined' ? window.location.origin : ''
        },
        body: JSON.stringify({ email })
      });
      
      const data = await HTTPClient.safeJSONParse(response);
      
      if (response.ok) {
        return {
          success: true,
          message: data?.message || 'If an account exists, a password reset email has been sent.',
          recovery_url: data?.recovery_url
        };
      }
      
      return {
        success: false,
        error: data?.detail || ERROR_MESSAGES.PASSWORD_RESET_FAILED
      };
      
    } catch (error) {
      return { success: false, error: ERROR_MESSAGES.NETWORK_ERROR };
    }
  }
  
  /**
   * Refreshes authentication token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} Refresh result
   */
  async refreshToken(refreshToken) {
    try {
      const response = await HTTPClient.fetchWithTimeout(`${this.baseURL}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      
      if (response.ok) {
        const data = await HTTPClient.safeJSONParse(response);
        return { success: true, data };
      }
      
      return { success: false };
      
    } catch (error) {
      console.error('Token refresh error:', error);
      return { success: false };
    }
  }
}

/**
 * Main Authentication Provider Component
 */
export const AuthProvider = ({ children }) => {
  // State management
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(TokenManager.getToken());
  
  // Initialize services
  const baseURL = getBackendBaseUrl();
  const authService = new AuthService(baseURL);
  const userService = new UserService(baseURL);
  
  /**
   * Updates user state with token
   * @param {string} authToken - Authentication token
   * @returns {Promise<boolean>} Success status
   */
  const refreshUserInternal = useCallback(async (authToken) => {
    try {
      const result = await userService.fetchUserWithRetry(authToken);
      if (result.success) {
        setUser(result.data);
        setToken(authToken);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }, [userService]);
  
  /**
   * Refreshes user data from current token
   * @returns {Promise<boolean>} Success status
   */
  const refreshUser = useCallback(async () => {
    const currentToken = TokenManager.getToken();
    if (!currentToken) return false;
    return await refreshUserInternal(currentToken);
  }, [refreshUserInternal]);
  
  /**
   * Handles token refresh
   * @returns {Promise<void>}
   */
  const handleTokenRefresh = useCallback(async () => {
    const refreshToken = TokenManager.getRefreshToken();
    if (!refreshToken) return;
    
    try {
      const result = await authService.refreshToken(refreshToken);
      if (result.success && result.data) {
        const { access_token, refresh_token, expires_in } = result.data;
        
        TokenManager.storeTokens(access_token, refresh_token, expires_in);
        setToken(access_token);
        await refreshUserInternal(access_token);
      } else {
        await logout();
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      await logout();
    }
  }, [authService, refreshUserInternal]);
  
  /**
   * User login handler
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} Login result
   */
  const login = useCallback(async (email, password) => {
    setLoading(true);
    try {
      const result = await authService.login(email, password);
      if (result.success && result.user) {
        setUser(result.user);
        setToken(TokenManager.getToken());
      }
      return result;
    } finally {
      setLoading(false);
    }
  }, [authService]);
  
  /**
   * User registration handler
   * @param {Object} userData - Registration data
   * @returns {Promise<Object>} Registration result
   */
  const register = useCallback(async (userData) => {
    setLoading(true);
    try {
      return await authService.register(userData);
    } finally {
      setLoading(false);
    }
  }, [authService]);
  
  /**
   * Forgot password handler
   * @param {string} email - User email
   * @returns {Promise<Object>} Forgot password result
   */
  const forgotPassword = useCallback(async (email) => {
    return await authService.forgotPassword(email);
  }, [authService]);
  
  /**
   * Google login handler (placeholder for compatibility)
   * @returns {Promise<Object>} Login result
   */
  const loginWithGoogle = useCallback(async () => {
    return { success: false, error: 'Google login not implemented in BackendAuthContext' };
  }, []);
  
  /**
   * User logout handler
   * @returns {Promise<Object>} Logout result
   */
  const logout = useCallback(async () => {
    try {
      TokenManager.clearTokens();
      setToken(null);
      setUser(null);
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      // Always clear state even if error occurs
      TokenManager.clearTokens();
      setToken(null);
      setUser(null);
      return { success: true };
    }
  }, []);
  
  // Initialize authentication on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = TokenManager.getToken();
      const storedRefresh = TokenManager.getRefreshToken();
      
      // Check if token needs refresh
      if (TokenManager.needsRefresh() && storedRefresh) {
        await handleTokenRefresh();
      } else if (storedToken) {
        await refreshUserInternal(storedToken);
      }
      
      setLoading(false);
    };
    
    initializeAuth();
  }, [refreshUserInternal, handleTokenRefresh]);
  
  // Set up periodic token refresh
  useEffect(() => {
    if (!token) return;
    
    const scheduleRefresh = () => {
      const expiry = TokenManager.getTokenExpiry();
      if (!expiry) return null;
      
      const timeUntilRefresh = expiry - Date.now() - AUTH_CONFIG.REFRESH_THRESHOLD;
      if (timeUntilRefresh <= 0) {
        handleTokenRefresh();
        return null;
      }
      
      return setTimeout(handleTokenRefresh, timeUntilRefresh);
    };
    
    const timeoutId = scheduleRefresh();
    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [token, handleTokenRefresh]);
  
  // Set up health check ping
  useEffect(() => {
    if (!token) return;
    
    const controller = new AbortController();
    
    const healthCheck = async () => {
      try {
        await fetch(`${baseURL}/api/health`, {
          headers: { 'Authorization': `Bearer ${token}` },
          signal: controller.signal,
        });
      } catch (error) {
        // Health check failures are logged but don't trigger logout
        console.warn('Health check failed:', error);
      }
    };
    
    const intervalId = setInterval(healthCheck, AUTH_CONFIG.HEALTH_CHECK_INTERVAL);
    
    return () => {
      clearInterval(intervalId);
      controller.abort();
    };
  }, [token, baseURL]);
  
  // Context value
  const value = {
    user,
    loading,
    token,
    login,
    register,
    forgotPassword,
    loginWithGoogle,
    logout,
    refreshUser
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;