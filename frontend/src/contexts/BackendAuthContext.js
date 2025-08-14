/**
 * Backend AuthContext for Aurum Life
 * Clean authentication using our Supabase-only backend API
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));

  // Check if user is authenticated on app load
  useEffect(() => {
    const initializeAuth = async () => {
      const sleep = (ms) => new Promise(res => setTimeout(res, ms));
      const storedToken = localStorage.getItem('auth_token');
      
      if (storedToken) {
        try {
          // Verify token with backend
          const response = await fetch(`${BACKEND_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${storedToken}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
            setToken(storedToken);
          } else {
            // Token is invalid, clear it
            localStorage.removeItem('auth_token');
            setToken(null);
            setUser(null);
          }
        } catch (error) {
          console.error('Auth verification failed:', error);
          localStorage.removeItem('auth_token');
          setToken(null);
          setUser(null);
        }
      }
      
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const sleep = (ms) => new Promise(res => setTimeout(res, ms));

  const fetchUserWithRetry = async (authToken, maxAttempts = 3, delayMs = 500) => {
    let lastErr = null;
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const userResponse = await fetch(`${BACKEND_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          }
        });
        if (userResponse.ok) {
          const userData = await userResponse.json();
          return { ok: true, data: userData };
        } else {
          const err = await (async () => { try { return await userResponse.json(); } catch { return {}; } })();
          lastErr = new Error(err?.detail || `auth/me failed with ${userResponse.status}`);
        }
      } catch (e) {
        lastErr = e;
      }
      await sleep(delayMs);
    }
    return { ok: false, error: lastErr };
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        const authToken = data.access_token;
        
        // Store token
        localStorage.setItem('auth_token', authToken);
        setToken(authToken);

        // Get user profile
        const { ok, data, error } = await fetchUserWithRetry(authToken, 3, 400);
        if (ok) {
          setUser(data);
          setLoading(false); // AFTER setting user
          return { success: true, message: 'Login successful!' };
        } else {
          setLoading(false);
          throw new Error(error?.message || 'Failed to get user profile');
        }
        
      } else {
        setLoading(false);
        return { 
          success: false, 
          error: data.detail || 'Login failed' 
        };
      }
      
    } catch (error) {
      console.error('Login error:', error);
      setLoading(false);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${BACKEND_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      const data = await response.json();

      if (response.ok) {
        return { 
          success: true, 
          message: data.message || 'Registration successful! You can now log in.'
        };
      } else {
        return { 
          success: false, 
          error: data.detail || 'Registration failed' 
        };
      }
      
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      // Clear local storage
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
      
      // Optional: Call backend logout endpoint if it exists
      if (token) {
        try {
          await fetch(`${BACKEND_URL}/api/auth/logout`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
        } catch (error) {
          // Logout endpoint might not exist, that's okay
          console.log('Backend logout not available');
        }
      }
      
      return { success: true };
      
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local state even if backend call fails
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
      return { success: true };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      if (!token) {
        throw new Error('Not authenticated');
      }
      
      const response = await fetch(`${BACKEND_URL}/api/auth/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });

      const data = await response.json();

      if (response.ok) {
        setUser({ ...user, ...data });
        return { 
          success: true, 
          message: 'Profile updated successfully!' 
        };
      } else {
        // Handle different error types properly
        let errorMessage = 'Profile update failed';
        
        if (response.status === 422 && data.detail && Array.isArray(data.detail)) {
          // Parse Pydantic validation errors
          const validationErrors = data.detail.map(err => {
            const field = Array.isArray(err.loc) ? err.loc[err.loc.length - 1] : 'field';
            const fieldName = field === 'username' ? 'Username' 
                            : field === 'first_name' ? 'First Name'
                            : field === 'last_name' ? 'Last Name' 
                            : field;
            return `${fieldName}: ${err.msg || 'Invalid value'}`;
          });
          errorMessage = validationErrors.join(', ');
        } else if (response.status === 429) {
          // Rate limiting error
          errorMessage = data.detail || 'Username can only be changed once every 7 days';
        } else if (response.status === 409) {
          // Username already taken
          errorMessage = data.detail || 'Username is already taken';
        } else if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        }
        
        return { 
          success: false, 
          error: errorMessage 
        };
      }
      
    } catch (error) {
      console.error('Profile update error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const forgotPassword = async (email) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (response.ok) {
        return { 
          success: true, 
          message: data.message || 'Password reset email sent!' 
        };
      } else {
        return { 
          success: false, 
          error: data.detail || 'Password reset failed' 
        };
      }
      
    } catch (error) {
      console.error('Forgot password error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const loginWithGoogle = async (credentialResponse) => {
    try {
      setLoading(true);
      
      // Use the access token to get user info directly
      if (credentialResponse?.userInfo) {
        // We already have user info, create our own session
        const userData = {
          id: credentialResponse.userInfo.id,
          email: credentialResponse.userInfo.email,
          name: credentialResponse.userInfo.name,
          picture: credentialResponse.userInfo.picture
        };
        
        // Create session token locally (simplified approach)
        const sessionToken = `google_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Store token and user data
        localStorage.setItem('auth_token', sessionToken);
        setToken(sessionToken);
        setUser(userData);
        
        return { 
          success: true, 
          message: 'Google login successful!'
        };
      } else {
        return { 
          success: false, 
          error: 'Failed to get user information from Google' 
        };
      }
      
    } catch (error) {
      console.error('Google login error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleCallback = async (sessionId) => {
    // This method is no longer needed with the new Google OAuth flow
    // but keeping it for backward compatibility
    console.warn('handleGoogleCallback is deprecated with new Google OAuth flow');
    return { 
      success: false, 
      error: 'This method is no longer supported'
    };
  };

  const refreshUser = async () => {
    try {
      if (!token) {
        console.log('No token available for user refresh');
        return { success: false, error: 'Not authenticated' };
      }

      console.log('🔄 Refreshing user data from backend...');
      
      const response = await fetch(`${BACKEND_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        console.log('✅ User data refreshed successfully', userData);
        return { 
          success: true, 
          data: userData 
        };
      } else {
        console.error('Failed to refresh user data:', response.status);
        return { 
          success: false, 
          error: 'Failed to refresh user data' 
        };
      }
      
    } catch (error) {
      console.error('Refresh user error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const value = {
    user,
    loading,
    token,
    login,
    register,
    logout,
    updateProfile,
    refreshUser,
    forgotPassword,
    loginWithGoogle,
    handleGoogleCallback
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;