import React, { createContext, useContext, useState, useEffect } from 'react';

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
      console.log('🔄 AuthContext - Fetching current user with token:', authToken ? 'present' : 'null');
      
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      console.log('🔄 AuthContext - fetchCurrentUser response status:', response.status);

      if (response.ok) {
        const userData = await response.json();
        console.log('🔄 AuthContext - User data received:', userData);
        setUser(userData);
      } else {
        // Token is invalid, clear it
        console.log('🔄 AuthContext - Invalid token, logging out');
        logout();
      }
    } catch (error) {
      console.error('🔄 AuthContext - Error fetching current user:', error);
      logout();
    } finally {
      console.log('🔄 AuthContext - Setting loading to false');
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      console.log('🔐 Starting login process for:', email);
      
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      console.log('🔐 Login API response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        const authToken = data.access_token;
        
        console.log('🔐 Token received, saving to localStorage');
        localStorage.setItem('auth_token', authToken);
        setToken(authToken);
        
        // Fetch user data
        console.log('🔐 Fetching user data...');
        const userResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
          },
        });

        console.log('🔐 User data API response status:', userResponse.status);

        if (userResponse.ok) {
          const userData = await userResponse.json();
          console.log('🔐 User data received:', userData);
          setUser(userData);
          return { success: true };
        } else {
          // Handle user data fetch failure
          console.error('🔐 Failed to fetch user data after login');
          const userErrorData = await userResponse.json();
          return { success: false, error: userErrorData.detail || 'Failed to fetch user data' };
        }
      } else {
        const errorData = await response.json();
        console.error('🔐 Login failed:', errorData);
        return { success: false, error: errorData.detail || 'Login failed' };
      }
    } catch (error) {
      console.error('🔐 Login error:', error);
      return { success: false, error: 'Network error' };
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

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    updateProfile,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;