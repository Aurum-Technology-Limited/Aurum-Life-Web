/**
 * @fileoverview Login Component
 * 
 * Provides unified authentication interface supporting login, registration,
 * password reset, and Google OAuth. Features automatic duplicate email handling,
 * robust form validation, and enhanced user experience.
 * 
 * @version 1.0.0
 * @author Aurum Life Development Team
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import { useAuth } from '../contexts/BackendAuthContext';
import { EyeIcon, EyeOffIcon } from '@heroicons/react/outline';

// Configuration constants
const LOGIN_CONFIG = {
  MIN_PASSWORD_LENGTH: 6,
  AUTO_SWITCH_DELAY: 1200, // ms
  FOCUS_RETRY_ATTEMPTS: 6,
  FOCUS_RETRY_DELAY: 16, // ms (one animation frame)
  NOTIFICATION_TIMEOUT: 1500, // ms
  
  // Form field names
  FORM_FIELDS: {
    EMAIL: 'email',
    PASSWORD: 'password',
    CONFIRM_PASSWORD: 'confirmPassword',
    FIRST_NAME: 'firstName',
    LAST_NAME: 'lastName',
    USERNAME: 'username'
  },
  
  // Local storage keys
  STORAGE_KEYS: {
    PREFILL_EMAIL: 'auth_prefill_email',
    DUPLICATE_SIGNAL: 'auth_duplicate_signal'
  }
};

// Validation messages
const VALIDATION_MESSAGES = {
  PASSWORD_MISMATCH: 'Passwords do not match',
  PASSWORD_TOO_SHORT: `Password must be at least ${LOGIN_CONFIG.MIN_PASSWORD_LENGTH} characters long`,
  EMAIL_REQUIRED: 'Please enter your email address',
  UNEXPECTED_ERROR: 'An unexpected error occurred',
  GOOGLE_AUTH_FAILED: 'Google authentication failed. Please try again.',
  NETWORK_ERROR: 'Network error. Please try again.'
};

/**
 * Form data management utility
 */
class FormDataManager {
  /**
   * Creates initial form state
   * @returns {Object} Initial form data
   */
  static createInitialState() {
    return {
      [LOGIN_CONFIG.FORM_FIELDS.EMAIL]: '',
      [LOGIN_CONFIG.FORM_FIELDS.PASSWORD]: '',
      [LOGIN_CONFIG.FORM_FIELDS.CONFIRM_PASSWORD]: '',
      [LOGIN_CONFIG.FORM_FIELDS.FIRST_NAME]: '',
      [LOGIN_CONFIG.FORM_FIELDS.LAST_NAME]: '',
      [LOGIN_CONFIG.FORM_FIELDS.USERNAME]: ''
    };
  }
  
  /**
   * Clears password fields
   * @param {Object} currentData - Current form data
   * @returns {Object} Form data with cleared passwords
   */
  static clearPasswords(currentData) {
    return {
      ...currentData,
      [LOGIN_CONFIG.FORM_FIELDS.PASSWORD]: '',
      [LOGIN_CONFIG.FORM_FIELDS.CONFIRM_PASSWORD]: ''
    };
  }
  
  /**
   * Clears registration-specific fields
   * @param {Object} currentData - Current form data
   * @returns {Object} Form data with cleared registration fields
   */
  static clearRegistrationFields(currentData) {
    return {
      ...currentData,
      [LOGIN_CONFIG.FORM_FIELDS.PASSWORD]: '',
      [LOGIN_CONFIG.FORM_FIELDS.CONFIRM_PASSWORD]: '',
      [LOGIN_CONFIG.FORM_FIELDS.FIRST_NAME]: '',
      [LOGIN_CONFIG.FORM_FIELDS.LAST_NAME]: '',
      [LOGIN_CONFIG.FORM_FIELDS.USERNAME]: ''
    };
  }
}

/**
 * Form validation utility
 */
class FormValidator {
  /**
   * Validates password requirements
   * @param {string} password - Password to validate
   * @returns {string} Error message or empty string if valid
   */
  static validatePassword(password) {
    if (!password || password.length < LOGIN_CONFIG.MIN_PASSWORD_LENGTH) {
      return VALIDATION_MESSAGES.PASSWORD_TOO_SHORT;
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
      return VALIDATION_MESSAGES.PASSWORD_MISMATCH;
    }
    return '';
  }
  
  /**
   * Validates email requirement
   * @param {string} email - Email to validate
   * @returns {string} Error message or empty string if valid
   */
  static validateEmailRequired(email) {
    if (!email || !email.trim()) {
      return VALIDATION_MESSAGES.EMAIL_REQUIRED;
    }
    return '';
  }
}

/**
 * Local storage utility for auth state persistence
 */
class AuthStorageManager {
  /**
   * Stores email for auto-fill
   * @param {string} email - Email to store
   */
  static storeEmailForAutoFill(email) {
    try {
      localStorage.setItem(LOGIN_CONFIG.STORAGE_KEYS.PREFILL_EMAIL, email || '');
    } catch (error) {
      console.warn('Failed to store email for auto-fill:', error);
    }
  }
  
  /**
   * Retrieves stored email for auto-fill
   * @returns {string} Stored email or empty string
   */
  static getStoredEmail() {
    try {
      return localStorage.getItem(LOGIN_CONFIG.STORAGE_KEYS.PREFILL_EMAIL) || '';
    } catch {
      return '';
    }
  }
  
  /**
   * Sets duplicate email signal
   */
  static setDuplicateSignal() {
    try {
      localStorage.setItem(LOGIN_CONFIG.STORAGE_KEYS.DUPLICATE_SIGNAL, '1');
    } catch (error) {
      console.warn('Failed to set duplicate signal:', error);
    }
  }
  
  /**
   * Gets and clears duplicate email signal
   * @returns {boolean} True if signal was present
   */
  static consumeDuplicateSignal() {
    try {
      const signal = localStorage.getItem(LOGIN_CONFIG.STORAGE_KEYS.DUPLICATE_SIGNAL);
      if (signal === '1') {
        localStorage.removeItem(LOGIN_CONFIG.STORAGE_KEYS.DUPLICATE_SIGNAL);
        return true;
      }
    } catch (error) {
      console.warn('Failed to check duplicate signal:', error);
    }
    return false;
  }
}

/**
 * Notification utility
 */
class NotificationManager {
  /**
   * Shows browser notification if supported
   * @param {string} title - Notification title
   * @param {string} body - Notification body
   */
  static async showNotification(title, body) {
    try {
      if (window?.Notification && Notification.permission !== 'denied') {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          new Notification(title, { body });
        }
      }
    } catch (error) {
      console.warn('Notification failed:', error);
    }
  }
}

/**
 * Focus management utility
 */
class FocusManager {
  /**
   * Attempts to focus password field with retry mechanism
   * @param {React.RefObject} passwordRef - Password input ref
   * @param {number} maxAttempts - Maximum focus attempts
   */
  static focusPasswordField(passwordRef, maxAttempts = LOGIN_CONFIG.FOCUS_RETRY_ATTEMPTS) {
    let attempts = 0;
    
    const attemptFocus = () => {
      attempts += 1;
      
      try {
        passwordRef?.current?.focus();
      } catch (error) {
        console.warn('Focus attempt failed:', error);
      }
      
      // Check if focus was successful
      const focused = typeof document !== 'undefined' && 
                    document.activeElement && 
                    document.activeElement.id === 'password';
      
      if (!focused && attempts < maxAttempts) {
        requestAnimationFrame(attemptFocus);
      }
    };
    
    Promise.resolve().then(() => requestAnimationFrame(attemptFocus));
  }
}

/**
 * Main Login Component
 */
const Login = () => {
  // Authentication context
  const { login, register, forgotPassword, loginWithGoogle, loading } = useAuth();
  
  // Component state
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState(FormDataManager.createInitialState());
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  // Auto-switch state management
  const [justAutoSwitched, setJustAutoSwitched] = useState(false);
  const [pendingAutoSwitchDuplicate, setPendingAutoSwitchDuplicate] = useState(false);
  const [autoSwitchedDuplicate, setAutoSwitchedDuplicate] = useState(false);
  
  // Recovery URL state (legacy support)
  const [recoveryUrl, setRecoveryUrl] = useState('');
  const [copied, setCopied] = useState(false);
  
  // Refs
  const lastRegEmailRef = useRef('');
  const passwordInputRef = useRef(null);
  
  // Memoized focus function
  const focusPasswordStable = useCallback(() => {
    FocusManager.focusPasswordField(passwordInputRef);
  }, []);
  
  /**
   * Handles form input changes
   */
  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear feedback when user starts typing
    setError('');
    setMessage('');
    setRecoveryUrl('');
    setCopied(false);
  }, []);
  
  /**
   * Handles tab switching between login and registration
   */
  const switchToLogin = useCallback(() => {
    setIsLogin(true);
    setError('');
    setMessage('');
    setJustAutoSwitched(false);
    setTimeout(focusPasswordStable, 0);
  }, [focusPasswordStable]);
  
  const switchToRegistration = useCallback(() => {
    setIsLogin(false);
    setError('');
    setMessage('');
    setAutoSwitchedDuplicate(false);
  }, []);
  
  /**
   * Handles duplicate email auto-switch logic
   */
  useEffect(() => {
    if (isLogin && pendingAutoSwitchDuplicate) {
      setJustAutoSwitched(true);
      setAutoSwitchedDuplicate(true);
      
      const emailToFill = lastRegEmailRef.current || AuthStorageManager.getStoredEmail();
      if (emailToFill) {
        setFormData(prev => ({ ...prev, email: emailToFill, password: '', confirmPassword: '' }));
      } else {
        setFormData(prev => FormDataManager.clearPasswords(prev));
      }
      
      focusPasswordStable();
      setPendingAutoSwitchDuplicate(false);
    }
  }, [isLogin, pendingAutoSwitchDuplicate, focusPasswordStable]);
  
  /**
   * Handles localStorage duplicate signal
   */
  useEffect(() => {
    if (isLogin && AuthStorageManager.consumeDuplicateSignal()) {
      const savedEmail = AuthStorageManager.getStoredEmail();
      setFormData(prev => ({ ...prev, email: savedEmail, password: '', confirmPassword: '' }));
      setAutoSwitchedDuplicate(true);
      setJustAutoSwitched(true);
      
      setTimeout(() => {
        focusPasswordStable();
      }, 150);
    }
  }, [isLogin, focusPasswordStable]);
  
  /**
   * Handles main form submission
   */
  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    try {
      if (isLogin) {
        await handleLoginSubmission();
      } else {
        await handleRegistrationSubmission();
      }
    } catch (error) {
      setError(VALIDATION_MESSAGES.UNEXPECTED_ERROR);
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  }, [isLogin, formData]);
  
  /**
   * Handles login form submission
   */
  const handleLoginSubmission = async () => {
    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      setMessage('Login successful!');
      await NotificationManager.showNotification('Welcome back!', 'Login successful');
      // Navigation handled by ProtectedRoute
    } else {
      setError(result.error || VALIDATION_MESSAGES.UNEXPECTED_ERROR);
    }
  };
  
  /**
   * Handles registration form submission
   */
  const handleRegistrationSubmission = async () => {
    // Validate passwords
    const passwordError = FormValidator.validatePassword(formData.password);
    if (passwordError) {
      setError(passwordError);
      return;
    }
    
    const confirmationError = FormValidator.validatePasswordConfirmation(
      formData.password, 
      formData.confirmPassword
    );
    if (confirmationError) {
      setError(confirmationError);
      return;
    }
    
    // Prepare user data
    const userData = {
      email: formData.email,
      password: formData.password,
      first_name: formData.firstName,
      last_name: formData.lastName,
      username: formData.username || formData.email.split('@')[0]
    };
    
    const result = await register(userData);
    
    if (result.success) {
      await handleSuccessfulRegistration();
    } else {
      await handleRegistrationError(result);
    }
  };
  
  /**
   * Handles successful registration
   */
  const handleSuccessfulRegistration = async () => {
    setError('');
    setFormData({
      ...formData,
      ...FormDataManager.clearRegistrationFields(formData)
    });
    
    setMessage('Your account has been created successfully. You can now sign in.');
    await NotificationManager.showNotification(
      'Account Created',
      'Your account has been created successfully. You can now sign in.'
    );
    
    // Auto-switch to login
    setTimeout(() => {
      setJustAutoSwitched(true);
      focusPasswordStable();
      lastRegEmailRef.current = formData.email;
      setIsLogin(true);
    }, LOGIN_CONFIG.AUTO_SWITCH_DELAY);
  };
  
  /**
   * Handles registration errors including duplicate emails
   */
  const handleRegistrationError = async (result) => {
    if (result.duplicate || result.code === 409) {
      setError(result.error || 'An account with this email already exists. Please sign in instead.');
      
      // Set up auto-switch to login
      lastRegEmailRef.current = formData.email;
      AuthStorageManager.storeEmailForAutoFill(formData.email);
      AuthStorageManager.setDuplicateSignal();
      setPendingAutoSwitchDuplicate(true);
      
      setTimeout(() => {
        setIsLogin(true);
        setTimeout(focusPasswordStable, 0);
      }, LOGIN_CONFIG.AUTO_SWITCH_DELAY);
    } else {
      setError(result.error || VALIDATION_MESSAGES.UNEXPECTED_ERROR);
    }
  };
  
  /**
   * Handles forgot password functionality
   */
  const handleForgotPassword = useCallback(async () => {
    const emailError = FormValidator.validateEmailRequired(formData.email);
    if (emailError) {
      setError(emailError);
      return;
    }
    
    setIsSubmitting(true);
    const result = await forgotPassword(formData.email);
    
    if (result.success) {
      setMessage(result.message);
      if (result.recovery_url) {
        setRecoveryUrl(result.recovery_url);
      }
    } else {
      setError(result.error);
    }
    
    setIsSubmitting(false);
  }, [formData.email, forgotPassword]);
  
  /**
   * Handles copy to clipboard functionality
   */
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(recoveryUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), LOGIN_CONFIG.NOTIFICATION_TIMEOUT);
    } catch (error) {
      console.warn('Copy to clipboard failed:', error);
    }
  }, [recoveryUrl]);
  
  /**
   * Google OAuth configuration
   */
  const googleLogin = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      try {
        setIsSubmitting(true);
        
        // Exchange authorization code for user info
        const userInfoResponse = await fetch(
          `https://www.googleapis.com/oauth2/v1/userinfo?access_token=${codeResponse.access_token}`,
          {
            headers: {
              Authorization: `Bearer ${codeResponse.access_token}`,
            },
          }
        );
        
        const userInfo = await userInfoResponse.json();
        
        // Create credential response for backend
        const credentialResponse = {
          credential: codeResponse.access_token,
          userInfo: userInfo
        };
        
        const result = await loginWithGoogle(credentialResponse);
        if (!result.success && result.error) {
          setError(result.error);
        }
      } catch (error) {
        setError(VALIDATION_MESSAGES.GOOGLE_AUTH_FAILED);
      } finally {
        setIsSubmitting(false);
      }
    },
    onError: () => {
      setError(VALIDATION_MESSAGES.GOOGLE_AUTH_FAILED);
    },
  });
  
  /**
   * Handles Google login button click
   */
  const handleGoogleLogin = useCallback(async () => {
    setIsSubmitting(true);
    try {
      googleLogin();
    } catch (error) {
      setError(VALIDATION_MESSAGES.GOOGLE_AUTH_FAILED);
      setIsSubmitting(false);
    }
  }, [googleLogin]);
  
  // Render helper components
  const renderHeader = () => (
    <div className="sm:mx-auto sm:w-full sm:max-w-md">
      <div className="flex justify-center mb-6">
        <div className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold text-xl">
          AL
        </div>
      </div>
      <h2 className="text-center text-3xl font-extrabold text-white">
        Aurum Life
      </h2>
      <p className="mt-2 text-center text-sm text-gray-400">
        Transform your potential into gold
      </p>
    </div>
  );
  
  const renderTabButtons = () => (
    <div className="flex mb-6">
      <button
        type="button"
        onClick={switchToLogin}
        className={`flex-1 py-2 px-4 text-sm font-medium rounded-l-md border ${
          isLogin
            ? 'bg-yellow-500 text-black border-yellow-500'
            : 'bg-gray-700 text-gray-300 border-gray-600 hover:bg-gray-600'
        }`}
        data-testid={isLogin ? 'auth-tab-login' : 'auth-tab-login-inactive'}
      >
        Login
      </button>
      <button
        type="button"
        onClick={switchToRegistration}
        className={`flex-1 py-2 px-4 text-sm font-medium rounded-r-md border-t border-r border-b ${
          !isLogin
            ? 'bg-yellow-500 text-black border-yellow-500'
            : 'bg-gray-700 text-gray-300 border-gray-600 hover:bg-gray-600'
        }`}
        data-testid={!isLogin ? 'auth-tab-signup' : 'auth-tab-signup-inactive'}
      >
        Sign Up
      </button>
    </div>
  );
  
  const renderStatusMessages = () => (
    <>
      {/* Duplicate email tip */}
      {isLogin && autoSwitchedDuplicate && (
        <div className="mb-4 p-3 bg-blue-900 border border-blue-700 text-blue-200 rounded flex items-start justify-between" role="alert" data-testid="duplicate-tip">
          <span>We found an account with this email. Please sign in.</span>
          <button
            type="button"
            className="ml-4 text-sm underline hover:no-underline"
            onClick={() => setAutoSwitchedDuplicate(false)}
            aria-label="Dismiss duplicate tip"
          >
            Dismiss
          </button>
        </div>
      )}
      
      {/* Auto-switch indicator (hidden, for testing) */}
      {justAutoSwitched && isLogin && (
        <div data-testid="auto-switched-to-login" className="hidden">auto-switched</div>
      )}
      
      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 bg-red-900 border border-red-700 text-red-300 rounded">
          {error}
        </div>
      )}
      
      {/* Success message */}
      {message && (
        <div className="mb-4 p-3 bg-green-900 border border-green-700 text-green-300 rounded" role="alert" data-testid="auth-success">
          {message}
        </div>
      )}
    </>
  );
  
  const renderRegistrationFields = () => {
    if (isLogin) return null;
    
    return (
      <>
        <div className="text-sm text-gray-400">
          Already have an account?{' '}
          <button
            type="button"
            className="text-yellow-500 hover:text-yellow-400 underline"
            onClick={switchToLogin}
            data-testid="signup-signin-instead"
          >
            Sign in instead
          </button>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-300">
              First Name
            </label>
            <input
              id="firstName"
              name="firstName"
              type="text"
              required={!isLogin}
              value={formData.firstName}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              placeholder="John"
            />
          </div>
          <div>
            <label htmlFor="lastName" className="block text-sm font-medium text-gray-300">
              Last Name
            </label>
            <input
              id="lastName"
              name="lastName"
              type="text"
              required={!isLogin}
              value={formData.lastName}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              placeholder="Doe"
            />
          </div>
        </div>
        
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-300">
            Username
          </label>
          <input
            id="username"
            name="username"
            type="text"
            value={formData.username}
            onChange={handleInputChange}
            className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
            placeholder="johndoe (optional)"
          />
        </div>
      </>
    );
  };
  
  return (
    <div className="min-h-screen bg-[#0B0D14] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {renderHeader()}
      
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-gray-800 py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {renderTabButtons()}
          {renderStatusMessages()}
          
          <form className="space-y-6" onSubmit={handleSubmit}>
            {renderRegistrationFields()}
            
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                placeholder="Enter your email"
                data-testid="auth-email"
              />
            </div>
            
            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300">
                Password
              </label>
              <div className="mt-1 relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                  required
                  ref={passwordInputRef}
                  value={formData.password}
                  onChange={handleInputChange}
                  className="block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent pr-10"
                  placeholder="Enter your password"
                  data-testid="auth-password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={isLogin ? 'Show current password' : 'Show new password'}
                >
                  {showPassword ? (
                    <EyeOffIcon className="h-5 w-5 text-gray-400 hover:text-gray-300" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400 hover:text-gray-300" />
                  )}
                </button>
              </div>
            </div>
            
            {/* Confirm Password Field (Registration only) */}
            {!isLogin && (
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  required={!isLogin}
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                  placeholder="Confirm your password"
                />
              </div>
            )}
            
            {/* Forgot Password Link */}
            {isLogin && (
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="text-sm text-yellow-500 hover:text-yellow-400"
                  disabled={isSubmitting}
                >
                  Forgot password?
                </button>
              </div>
            )}
            
            {/* Submit Button */}
            <div>
              <button
                type="submit"
                disabled={isSubmitting || loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-black bg-yellow-500 hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {(isSubmitting || loading) ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-black" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {isLogin ? 'Signing in...' : 'Creating account...'}
                  </span>
                ) : (
                  isLogin ? 'Sign In' : 'Create Account'
                )}
              </button>
            </div>
            
            {/* Google OAuth */}
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-600" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-gray-800 text-gray-400">Or continue with</span>
                </div>
              </div>
              
              <div className="mt-6">
                <button
                  type="button"
                  onClick={handleGoogleLogin}
                  disabled={isSubmitting}
                  className="w-full inline-flex justify-center py-2 px-4 border border-gray-600 rounded-md shadow-sm bg-gray-700 text-sm font-medium text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  data-testid="auth-google"
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Sign in with Google
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
      
      {/* Footer */}
      <div className="mt-8 text-center">
        <p className="text-sm text-gray-400">
          Welcome to your personal growth journey
        </p>
        {message && (
          <div className="mt-4 p-3 bg-green-900 border border-green-700 text-green-300 rounded max-w-md mx-auto">
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;