/**
 * Supabase Client Configuration for Aurum Life
 * Replaces custom backend authentication
 */

import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Auth helpers
export const auth = supabase.auth;

// Database helpers  
export const database = supabase;

// Storage helpers
export const storage = supabase.storage;

// Real-time helpers
export const realtime = supabase;