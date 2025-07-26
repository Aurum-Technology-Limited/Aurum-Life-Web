/**
 * Supabase AuthContext for Aurum Life
 * Enhanced authentication using Supabase Auth with backward compatibility
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../services/supabase';

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
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Backward compatibility - token from session
  const token = session?.access_token || localStorage.getItem('auth_token');

  useEffect(() => {
    // Get initial session
    const getInitialSession = async () => {
      try {
        const { data: { session: initialSession }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('Error getting session:', error);
        } else {
          setSession(initialSession);
          if (initialSession?.user) {
            await fetchUserProfile(initialSession.user);
          }
        }
      } catch (error) {
        console.error('Session initialization error:', error);
      } finally {
        setLoading(false);
      }
    };

    getInitialSession();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email);
        
        setSession(session);
        
        if (session?.user) {
          await fetchUserProfile(session.user);
          // Update localStorage for backward compatibility
          localStorage.setItem('auth_token', session.access_token);
        } else {
          setUser(null);
          localStorage.removeItem('auth_token');
        }
        
        setLoading(false);
      }
    );

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  const fetchUserProfile = async (supabaseUser) => {
    try {
      // First try to get profile from Supabase user_profiles table
      const { data: profile, error: profileError } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('id', supabaseUser.id)
        .single();

      if (profileError && profileError.code !== 'PGRST116') {
        console.error('Error fetching user profile:', profileError);
      }

      // Combine Supabase user data with profile data
      const userData = {
        id: supabaseUser.id,
        email: supabaseUser.email,
        username: profile?.username || supabaseUser.email?.split('@')[0],
        first_name: profile?.first_name || supabaseUser.user_metadata?.first_name || '',
        last_name: profile?.last_name || supabaseUser.user_metadata?.last_name || '',
        is_active: profile?.is_active ?? true,
        level: profile?.level || 1,
        total_points: profile?.total_points || 0,
        current_streak: profile?.current_streak || 0,
        profile_picture: profile?.profile_picture || null,
        google_id: profile?.google_id || null,
        created_at: supabaseUser.created_at,
        updated_at: profile?.updated_at || supabaseUser.updated_at
      };

      setUser(userData);
    } catch (error) {
      console.error('Error in fetchUserProfile:', error);
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        return { 
          success: false, 
          error: error.message || 'Login failed' 
        };
      }

      if (data.session) {
        setSession(data.session);
        localStorage.setItem('auth_token', data.session.access_token);
        
        if (data.user) {
          await fetchUserProfile(data.user);
        }
        
        return { success: true };
      } else {
        return { 
          success: false, 
          error: 'Authentication failed' 
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: 'Network error' 
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);

      const { data, error } = await supabase.auth.signUp({
        email: userData.email,
        password: userData.password,
        options: {
          data: {
            first_name: userData.first_name,
            last_name: userData.last_name,
            username: userData.username
          }
        }
      });

      if (error) {
        return { 
          success: false, 
          error: error.message || 'Registration failed' 
        };
      }

      if (data.user) {
        // Create user profile in our user_profiles table
        const { error: profileError } = await supabase
          .from('user_profiles')
          .insert({
            id: data.user.id,
            username: userData.username,
            first_name: userData.first_name,
            last_name: userData.last_name,
            is_active: true,
            level: 1,
            total_points: 0,
            current_streak: 0
          });

        if (profileError) {
          console.error('Error creating user profile:', profileError);
        }

        // Also create a user in the public.users table for backend compatibility
        try {
          const { error: usersError } = await supabase
            .from('users')
            .insert({
              id: data.user.id,
              username: userData.username,
              email: userData.email,
              first_name: userData.first_name,
              last_name: userData.last_name,
              is_active: true,
              level: 1,
              total_points: 0,
              current_streak: 0
            });

          if (usersError) {
            console.error('Error creating users record:', usersError);
          }
        } catch (userCreateError) {
          console.error('Users table creation failed:', userCreateError);
        }

        return { 
          success: true,
          message: 'Registration successful! Please check your email for verification.'
        };
      }

      return { 
        success: false, 
        error: 'Registration failed - no user created' 
      };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: 'Network error' 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) {
        console.error('Logout error:', error);
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
    
    // Clear state
    setUser(null);
    setSession(null);
    localStorage.removeItem('auth_token');
  };

  const forgotPassword = async (email) => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`
      });

      if (error) {
        return { 
          success: false, 
          error: error.message || 'Password reset failed' 
        };
      }

      return { 
        success: true, 
        message: 'Password reset email sent! Please check your inbox.' 
      };
    } catch (error) {
      console.error('Password reset error:', error);
      return { 
        success: false, 
        error: 'Network error' 
      };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      if (!user) return { success: false, error: 'User not authenticated' };

      // Update user_profiles table
      const { error: profileError } = await supabase
        .from('user_profiles')
        .update(profileData)
        .eq('id', user.id);

      if (profileError) {
        return { 
          success: false, 
          error: profileError.message || 'Profile update failed' 
        };
      }

      // Update local user state
      setUser(prev => ({ ...prev, ...profileData }));

      return { success: true };
    } catch (error) {
      console.error('Profile update error:', error);
      return { 
        success: false, 
        error: 'Network error' 
      };
    }
  };

  // Google OAuth login
  const loginWithGoogle = async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/dashboard`
        }
      });

      if (error) {
        return { 
          success: false, 
          error: error.message || 'Google login failed' 
        };
      }

      return { success: true };
    } catch (error) {
      console.error('Google login error:', error);
      return { 
        success: false, 
        error: 'Network error' 
      };
    }
  };

  const value = {
    // Core auth state
    user,
    token,
    session,
    loading,
    
    // Auth methods
    login,
    register,
    logout,
    forgotPassword,
    updateProfile,
    loginWithGoogle,
    
    // Supabase-specific
    supabase,
    fetchUserProfile,
    
    // Backward compatibility
    isAuthenticated: !!user,
    isLoading: loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;