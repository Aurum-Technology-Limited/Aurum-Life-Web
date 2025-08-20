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

  // helper
  const sleep = (ms) => new Promise(res => setTimeout(res, ms));

  // Check if user is authenticated on app load
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('auth_token');
      const storedRefresh = localStorage.getItem('refresh_token');
      const exp = Number(localStorage.getItem('auth_token_exp') || 0);

      // If token expired but refresh exists, try refresh first
      if ((!storedToken || (exp && Date.now() > exp)) && storedRefresh) {
        try {
          const r = await fetch(`${BACKEND_URL}/api/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: storedRefresh })
          });
          if (r.ok) {
            const data = await r.json();
            localStorage.setItem('auth_token', data.access_token);
            if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token);
            if (data.expires_in) localStorage.setItem('auth_token_exp', String(Date.now() + data.expires_in * 1000));
          }
        } catch (_) {}
      }

      const freshToken = localStorage.getItem('auth_token');
      if (freshToken) {
        try {
          let userData = null;
          for (let i = 0; i < 3; i++) {
            const response = await fetch(`${BACKEND_URL}/api/auth/me`, {
              headers: {
                'Authorization': `Bearer ${freshToken}`,
                'Content-Type': 'application/json'
              }
            });
            if (response.ok) {
              userData = await response.json();
              break;
            }
            await sleep(300);
          }
          if (userData) {
            setUser(userData);
            setToken(freshToken);
          } else {
            localStorage.removeItem('auth_token');
            setToken(null); setUser(null);
          }
        } catch (error) {
          console.error('Auth verification failed:', error);
          localStorage.removeItem('auth_token');
          setToken(null); setUser(null);
        }
      }
      setLoading(false);
    };
    initializeAuth();
  }, []);

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
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const loginData = await response.json();
      if (response.ok && loginData.access_token) {
        const authToken = loginData.access_token;
        const refreshToken = loginData.refresh_token;
        const expiresIn = loginData.expires_in || 3600;
        localStorage.setItem('auth_token', authToken);
        if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
        localStorage.setItem('auth_token_exp', String(Date.now() + expiresIn * 1000));
        setToken(authToken);
        const { ok, data: profileData, error } = await fetchUserWithRetry(authToken, 3, 400);
        if (ok) {
          setUser(profileData);
          setLoading(false);
          return { success: true, message: 'Login successful!' };
        } else {
          setLoading(false);
          throw new Error(error?.message || 'Failed to get user profile');
        }
      } else {
        setLoading(false);
        let errMsg = loginData.detail || 'Login failed';
        if (/legacy/i.test(errMsg)) errMsg = 'Your old account is no longer supported. Please create a new account.';
        return { success: false, error: errMsg };
      }
    } catch (error) {
      console.error('Login error:', error);
      setLoading(false);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const logout = async () => {
    try {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('auth_token_exp');
      setToken(null); setUser(null);
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('auth_token_exp');
      setToken(null); setUser(null);
      return { success: true };
    }
  };

  const scheduleRefresh = () => {
    const exp = Number(localStorage.getItem('auth_token_exp') || 0);
    if (!exp) return;
    const msUntil = exp - Date.now() - 60000; // refresh 60s before expiry
    if (msUntil <= 0) {
      doRefresh();
      return;
    }
    const id = setTimeout(() => doRefresh(), msUntil);
    return () => clearTimeout(id);
  };

  const doRefresh = async () => {
    const rt = localStorage.getItem('refresh_token');
    if (!rt) return;
    try {
      const r = await fetch(`${BACKEND_URL}/api/auth/refresh`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: rt })
      });
      if (r.ok) {
        const data = await r.json();
        localStorage.setItem('auth_token', data.access_token);
        if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token);
        if (data.expires_in) localStorage.setItem('auth_token_exp', String(Date.now() + data.expires_in * 1000));
        setToken(data.access_token);
        // Optionally refresh user data
        await fetchUserWithRetry(data.access_token, 1, 0);
      } else {
        // If refresh fails, force logout
        await logout();
      }
    } catch (e) {
      await logout();
    }
  };

  // Auto-schedule token refresh when token/exp changes
  useEffect(() => {
    if (!token) return;
    const cleanup = scheduleRefresh();
    return () => { if (cleanup) cleanup(); };
  }, [token]);

  // Keep-alive ping (doesn't replace refresh)
  useEffect(() => {
    if (!token) return;
    const controller = new AbortController();
    const ping = async () => {
      try {
        await fetch(`${BACKEND_URL}/api/health`, {
          headers: { 'Authorization': `Bearer ${token}` },
          signal: controller.signal,
        });
      } catch (_) {}
    };
    const id = setInterval(ping, 120000);
    return () => { clearInterval(id); controller.abort(); };
  }, [token]);

  const value = {
    user,
    loading,
    token,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;