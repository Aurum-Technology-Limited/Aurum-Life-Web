/**
 * @fileoverview Password Reset Component
 * 
 * Handles password reset flow including token extraction from URLs,
 * password validation, and backend communication for password updates.
 * Supports both hash and query parameter token formats from Supabase.
 * 
 * @version 1.0.0
 * @author Aurum Life Development Team
 */

import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { getBackendBaseUrl } from '../services/baseUrl';

// Configuration constants
const PASSWORD_RESET_CONFIG = {
  MIN_PASSWORD_LENGTH: 8,
  REDIRECT_DELAY: 1600, // ms
  PASSWORD_REQUIREMENTS: {
    minLength: 8,
    requireUppercase: true,
    requireNumber: true
  }
};

// Password validation messages
const VALIDATION_MESSAGES = {
  TOO_SHORT: `Password must be at least ${PASSWORD_RESET_CONFIG.MIN_PASSWORD_LENGTH} characters long`,
  NO_UPPERCASE: 'Password must include at least one uppercase letter',
  NO_NUMBER: 'Password must include at least one number',
  NO_MATCH: 'Passwords do not match',
  NO_TOKEN: 'Missing or invalid reset token. Please use the password reset link from your email.'
};

// Error types for better error handling
const ERROR_TYPES = {
  OTP_EXPIRED: 'otp_expired',
  ACCESS_DENIED: 'access_denied'
};

/**
 * URL parameter parsing utilities
 */
class URLParameterParser {
  /**
   * Parses URL hash parameters
   * @param {string} hash - URL hash string
   * @returns {Object} Parsed parameters object
   */
  static parseHashParams(hash) {
    const params = {};
    if (!hash) return params;
    
    const cleanHash = hash.startsWith('#') ? hash.slice(1) : hash;
    const pairs = cleanHash.split('&');
    
    for (const pair of pairs) {
      const [key, value] = pair.split('=');
      if (key) {
        params[decodeURIComponent(key)] = decodeURIComponent(value || '');
      }
    }
    
    return params;
  }
  
  /**
   * Parses URL query parameters
   * @param {string} search - URL search string
   * @returns {Object} Parsed parameters object
   */
  static parseQueryParams(search) {
    if (!search) return {};
    
    const params = new URLSearchParams(search);
    const result = {};
    
    for (const [key, value] of params.entries()) {
      result[key] = value;
    }
    
    return result;
  }
  
  /**
   * Extracts all relevant parameters from current URL
   * @returns {Object} Complete parameter extraction result
   */
  static extractURLParameters() {
    const hashParams = this.parseHashParams(window.location.hash);
    const queryParams = this.parseQueryParams(window.location.search);
    
    // Extract error information
    const error = hashParams.error || queryParams.error || '';
    const errorCode = hashParams.error_code || queryParams.error_code || '';
    const errorDescription = hashParams.error_description || queryParams.error_description || '';
    
    // Extract token information (multiple possible parameter names)
    const tokenCandidates = [
      hashParams.access_token,
      queryParams.access_token,
      hashParams.token,
      queryParams.token,
      hashParams.recovery_token,
      queryParams.recovery_token
    ];
    const accessToken = tokenCandidates.find(token => token) || '';
    
    const type = hashParams.type || queryParams.type || '';
    
    return {
      hashParams,
      queryParams,
      error,
      errorCode,
      errorDescription,
      accessToken,
      type
    };
  }
}

/**
 * Password validation utilities
 */
class PasswordValidator {
  /**
   * Validates password according to requirements
   * @param {string} password - Password to validate
   * @returns {string} Error message or empty string if valid
   */
  static validatePassword(password) {
    if (!password || password.length < PASSWORD_RESET_CONFIG.MIN_PASSWORD_LENGTH) {
      return VALIDATION_MESSAGES.TOO_SHORT;
    }
    
    if (PASSWORD_RESET_CONFIG.PASSWORD_REQUIREMENTS.requireUppercase && !/[A-Z]/.test(password)) {
      return VALIDATION_MESSAGES.NO_UPPERCASE;
    }
    
    if (PASSWORD_RESET_CONFIG.PASSWORD_REQUIREMENTS.requireNumber && !/[0-9]/.test(password)) {
      return VALIDATION_MESSAGES.NO_NUMBER;
    }
    
    return '';
  }
  
  /**
   * Validates password confirmation
   * @param {string} password - Original password
   * @param {string} confirmPassword - Password confirmation
   * @returns {string} Error message or empty string if valid
   */
  static validatePasswordConfirmation(password, confirmPassword) {
    if (password !== confirmPassword) {
      return VALIDATION_MESSAGES.NO_MATCH;
    }
    return '';
  }
}

/**
 * Password reset API service
 */
class PasswordResetService {
  constructor() {
    this.baseURL = getBackendBaseUrl();
  }
  
  /**
   * Updates user password using recovery token
   * @param {string} token - Recovery token
   * @param {string} newPassword - New password
   * @returns {Promise<Object>} Update result
   */
  async updatePassword(token, newPassword) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/update-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ new_password: newPassword })
      });
      
      if (response.ok) {
        return { success: true };
      }
      
      const errorData = await this.safeJSONParse(response);
      return {
        success: false,
        error: errorData?.detail || 'Failed to update password. Your link may have expired. Try requesting a new reset email.'
      };
      
    } catch (error) {
      return {
        success: false,
        error: 'Network error. Please try again.'
      };
    }
  }
  
  /**
   * Safely parses JSON response
   * @param {Response} response - Fetch response object
   * @returns {Promise<Object>} Parsed JSON or empty object
   */
  async safeJSONParse(response) {
    try {
      return await response.json();
    } catch {
      return {};
    }
  }
}

/**
 * Error display component
 */
const ErrorDisplay = ({ info, error }) => {
  if (info.error) {
    return (
      <div className="mb-4 p-3 bg-red-900 border border-red-700 text-red-300 rounded">
        {info.errorCode === ERROR_TYPES.OTP_EXPIRED ? (
          <ExpiredTokenError />
        ) : (
          <GenericError errorDescription={info.errorDescription} error={info.error} />
        )}
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="mb-4 p-3 bg-red-900 border border-red-700 text-red-300 rounded">
        {error}
      </div>
    );
  }
  
  return null;
};

/**
 * Expired token error component
 */
const ExpiredTokenError = () => (
  <div>
    <div className="font-semibold mb-2">Password reset link has expired</div>
    <div className="text-sm mb-3">
      Password reset links expire after a certain time for security reasons. 
      Please request a new password reset email.
    </div>
    <button
      type="button"
      onClick={() => { window.location.href = '/'; }}
      className="px-3 py-2 bg-yellow-500 text-black rounded hover:bg-yellow-600 text-sm font-medium"
    >
      Request new reset link
    </button>
  </div>
);

/**
 * Generic error component
 */
const GenericError = ({ errorDescription, error }) => (
  <div>
    <div className="font-semibold mb-2">Password reset error</div>
    <div className="text-sm">
      {decodeURIComponent(errorDescription || error || 'An error occurred with your password reset link.')}
    </div>
  </div>
);

/**
 * Missing token display component
 */
const MissingTokenDisplay = ({ info }) => (
  <div className="mb-4 p-3 bg-blue-900 border border-blue-700 text-blue-200 rounded">
    We couldn't find a reset token in your link. Please navigate from the latest password reset email.
    
    <details className="mt-2">
      <summary className="cursor-pointer text-sm">Debug Information</summary>
      <div className="mt-2 text-xs text-blue-300 font-mono">
        <div>Current URL: {window.location.href}</div>
        <div>Hash: {window.location.hash || '(none)'}</div>
        <div>Search: {window.location.search || '(none)'}</div>
        {info.hashParams && Object.keys(info.hashParams).length > 0 && (
          <div>Hash Params: {JSON.stringify(info.hashParams, null, 2)}</div>
        )}
        {info.queryParams && Object.keys(info.queryParams).length > 0 && (
          <div>Query Params: {JSON.stringify(info.queryParams, null, 2)}</div>
        )}
      </div>
    </details>
  </div>
);

/**
 * Main Password Reset Component
 */
const PasswordReset = () => {
  // State management
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Initialize password reset service
  const passwordResetService = useMemo(() => new PasswordResetService(), []);
  
  // Extract URL parameters and debug information
  const urlInfo = useMemo(() => {
    const extracted = URLParameterParser.extractURLParameters();
    
    // Debug logging for development
    if (process.env.NODE_ENV === 'development') {
      console.log('Password Reset URL Debug:', {
        hash: window.location.hash,
        search: window.location.search,
        extracted
      });
    }
    
    return extracted;
  }, []);
  
  // Handle component mount and token extraction
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🔍 PasswordReset component mounted');
      console.log('Current URL:', window.location.href);
      console.log('Extracted info:', urlInfo);
    }
    
    if (urlInfo.accessToken) {
      setToken(urlInfo.accessToken);
      if (process.env.NODE_ENV === 'development') {
        console.log('✅ Token found:', urlInfo.accessToken);
      }
    } else if (urlInfo.error) {
      if (process.env.NODE_ENV === 'development') {
        console.log('❌ Error found:', urlInfo.error, urlInfo.errorCode, urlInfo.errorDescription);
      }
    } else {
      if (process.env.NODE_ENV === 'development') {
        console.log('❓ No token or error found');
      }
    }
  }, [urlInfo]);
  
  // Handle form submission
  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    
    // Validate token
    if (!token) {
      setError(VALIDATION_MESSAGES.NO_TOKEN);
      return;
    }
    
    // Validate password
    const passwordError = PasswordValidator.validatePassword(newPassword);
    if (passwordError) {
      setError(passwordError);
      return;
    }
    
    // Validate password confirmation
    const confirmationError = PasswordValidator.validatePasswordConfirmation(newPassword, confirmPassword);
    if (confirmationError) {
      setError(confirmationError);
      return;
    }
    
    // Submit password update
    setIsSubmitting(true);
    try {
      const result = await passwordResetService.updatePassword(token, newPassword);
      
      if (result.success) {
        setMessage('Password updated successfully. Redirecting to login...');
        setTimeout(() => {
          window.location.href = '/';
        }, PASSWORD_RESET_CONFIG.REDIRECT_DELAY);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [token, newPassword, confirmPassword, passwordResetService]);
  
  // Handle input changes
  const handlePasswordChange = useCallback((e) => setNewPassword(e.target.value), []);
  const handleConfirmPasswordChange = useCallback((e) => setConfirmPassword(e.target.value), []);
  
  // Render success message
  const SuccessMessage = () => message && (
    <div className="mb-4 p-3 bg-green-900 border border-green-700 text-green-300 rounded">
      {message}
    </div>
  );
  
  return (
    <div className="min-h-screen bg-[#0B0D14] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center mb-6">
          <div className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold text-xl">
            AL
          </div>
        </div>
        <h2 className="text-center text-3xl font-extrabold text-white">
          Reset your password
        </h2>
        <p className="mt-2 text-center text-sm text-gray-400">
          Enter a new password for your account
        </p>
      </div>

      {/* Main Form */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-gray-800 py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <SuccessMessage />
          <ErrorDisplay info={urlInfo} error={error} />
          
          {!urlInfo.error && !token && (
            <MissingTokenDisplay info={urlInfo} />
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* New Password Field */}
            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-gray-300">
                New Password
              </label>
              <input
                id="newPassword"
                name="newPassword"
                type="password"
                autoComplete="new-password"
                required
                disabled={!!urlInfo.error}
                value={newPassword}
                onChange={handlePasswordChange}
                className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="Enter new password"
              />
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                disabled={!!urlInfo.error}
                value={confirmPassword}
                onChange={handleConfirmPasswordChange}
                className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="Re-enter new password"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => { window.location.href = '/'; }}
                className="text-sm text-gray-300 hover:text-gray-200"
              >
                Back to login
              </button>

              <button
                type="submit"
                disabled={isSubmitting || !token || !!urlInfo.error}
                className="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-black bg-yellow-500 hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Updating...' : 'Update password'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PasswordReset;