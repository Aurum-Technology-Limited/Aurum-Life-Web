import React, { createContext, useContext, useState, useEffect } from 'react';
import fixedAPI from '../services/fixedApi';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    if (token) {
      // Verify token and get user info
      fetchCurrentUser(token);
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async (authToken) => {
    try {
      console.log('🔐 Verifying user authentication...');
      const response = await fixedAPI.getCurrentUser();
      console.log('🔐 User authenticated successfully:', response.data.email);
      setUser(response.data);
    } catch (error) {
      console.warn('🔐 Token validation failed:', error.message);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      console.log('🔐 Attempting login...');
      const response = await fixedAPI.login({ email, password });
      
      const authToken = response.data.access_token;
      localStorage.setItem('auth_token', authToken);
      setToken(authToken);
      
      // Fetch user data with new token
      const userData = await fixedAPI.getCurrentUser();
      setUser(userData.data);
      
      console.log('🔐 Login successful:', userData.data.email);
      return { success: true };
    } catch (error) {
      console.error('🔐 Login failed:', error.message);
      return { success: false, error: error.message };
    }
  };

  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        // After successful registration, automatically log in
        return await login(userData.email, userData.password);
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Registration failed' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Network error' };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profileData),
      });

      if (response.ok) {
        // Refresh user data
        await fetchCurrentUser(token);
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Update failed' };
      }
    } catch (error) {
      console.error('Profile update error:', error);
      return { success: false, error: 'Network error' };
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  };

  const forgotPassword = async (email) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        const data = await response.json();
        return { success: true, message: data.message };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Password reset failed' };
      }
    } catch (error) {
      console.error('Forgot password error:', error);
      return { success: false, error: 'Network error' };
    }
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    updateProfile,
    logout,
    forgotPassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;