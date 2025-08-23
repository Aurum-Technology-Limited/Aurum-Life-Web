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

  const sleep = (ms) => new Promise(res => setTimeout(res, ms));

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('auth_token');
      const storedRefresh = localStorage.getItem('refresh_token');
      const exp = Number(localStorage.getItem('auth_token_exp') || 0);
      if ((!storedToken || (exp && Date.now() > exp)) && storedRefresh) {
        try {
          const r = await fetch(`${BACKEND_URL}/api/auth/refresh`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
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
        await refreshUserInternal(freshToken);
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
          headers: { 'Authorization': `Bearer ${authToken}`, 'Content-Type': 'application/json' }
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

  const refreshUserInternal = async (authToken) => {
    try {
      const { ok, data } = await fetchUserWithRetry(authToken, 3, 400);
      if (ok) {
        setUser(data);
        setToken(authToken);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  const refreshUser = async () => {
    const t = localStorage.getItem('auth_token');
    if (!t) return false;
    return await refreshUserInternal(t);
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
        const ok = await refreshUserInternal(authToken);
        setLoading(false);
        return ok ? { success: true, message: 'Login successful!' } : { success: false, error: 'Failed to get user profile' };
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

  const forgotPassword = async (email) => {
    try {
      const r = await fetch(`${BACKEND_URL}/api/auth/forgot-password`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await (async () => { try { return await r.json(); } catch { return {}; } })();
      if (r.ok) {
        return { success: true, message: data?.message || 'If an account exists, a password reset email has been sent.', recovery_url: data?.recovery_url };
      }
      return { success: false, error: data?.detail || 'Failed to send password reset email' };
    } catch (e) {
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
    const msUntil = exp - Date.now() - 60000;
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
        await refreshUserInternal(data.access_token);
      } else {
        await logout();
      }
    } catch (e) {
      await logout();
    }
  };

  useEffect(() => {
    if (!token) return;
    const cleanup = scheduleRefresh();
    return () => { if (cleanup) cleanup(); };
  }, [token]);

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
    forgotPassword,
    logout,
    refreshUser,
  };

  return (
    &lt;AuthContext.Provider value={value}&gt;
      {children}
    &lt;/AuthContext.Provider&gt;
  );
};

export default AuthContext;