// Test script to get JWT token and test Edge Function
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://sftppbnqlsumjlrgyzgo.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDgzNjI3OTUsImV4cCI6MjAyMzk3ODc5NX0.PzL5W-OcWZwwFGj_YIAjGDCdtqvgM8mPQy1Yl-xW-S8'

const supabase = createClient(supabaseUrl, supabaseKey)

async function testAuth() {
  try {
    // Sign in with email/password (replace with your credentials)
    const { data, error } = await supabase.auth.signInWithPassword({
      email: 'your-email@example.com',
      password: 'your-password'
    })

    if (error) {
      console.error('Auth error:', error)
      return
    }

    console.log('✅ Authentication successful!')
    console.log('User:', data.user.email)
    console.log('JWT Token:', data.session.access_token)
    
    // Test the Edge Function
    const response = await fetch('https://sftppbnqlsumjlrgyzgo.supabase.co/functions/v1/aurum-api', {
      headers: {
        'Authorization': `Bearer ${data.session.access_token}`,
        'Content-Type': 'application/json'
      }
    })

    const result = await response.json()
    console.log('✅ Edge Function Response:', result)

  } catch (error) {
    console.error('Test error:', error)
  }
}

testAuth()
