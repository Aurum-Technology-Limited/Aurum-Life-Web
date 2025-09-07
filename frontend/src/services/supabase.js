/**
 * Supabase Client Configuration for Aurum Life
 * Replaces custom backend authentication
 */

import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

// Debug environment variables
console.log('🔍 Supabase Environment Variables:', {
  url: supabaseUrl ? '✅ Set' : '❌ Missing',
  anonKey: supabaseAnonKey ? '✅ Set' : '❌ Missing',
  urlValue: supabaseUrl,
  anonKeyValue: supabaseAnonKey ? `${supabaseAnonKey.substring(0, 20)}...` : 'undefined'
});

// Create Supabase client or mock based on environment variables
let supabaseClient;
let authClient;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('⚠️ Missing Supabase environment variables - using mock mode:', {
    REACT_APP_SUPABASE_URL: supabaseUrl,
    REACT_APP_SUPABASE_ANON_KEY: supabaseAnonKey ? 'Set' : 'Missing'
  });
  
  // Create a mock Supabase client for development
  supabaseClient = {
    auth: {
      getSession: () => Promise.resolve({ data: { session: null }, error: null }),
      onAuthStateChange: (callback) => {
        // Immediately call the callback to resolve loading state
        setTimeout(() => callback('SIGNED_OUT', null), 0);
        return { data: { subscription: { unsubscribe: () => {} } } };
      },
      signInWithPassword: () => Promise.resolve({ data: { user: null }, error: null }),
      signUp: () => Promise.resolve({ data: { user: null }, error: null }),
      signOut: () => Promise.resolve({ error: null }),
    }
  };
  
  console.log('🔧 Using mock Supabase client for development');
} else {
  // Create real Supabase client
  supabaseClient = createClient(supabaseUrl, supabaseAnonKey);
}

export const supabase = supabaseClient;

// Auth helpers
export const auth = supabase.auth;

// Database helpers  
export const database = supabase;

// Storage helpers
export const storage = supabase.storage;

// Real-time helpers
export const realtime = supabase;