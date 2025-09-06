// Aurum Life API - Supabase Edge Function
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Initialize Supabase client with proper headers
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { 
            Authorization: req.headers.get('Authorization') ?? '',
            apikey: Deno.env.get('SUPABASE_ANON_KEY') ?? ''
          },
        },
      }
    )

    // Parse URL and method
    const url = new URL(req.url)
    const path = url.pathname
    const method = req.method

    // Route handling - Public endpoints (no auth required)
    if (path === '/' && method === 'GET') {
      return new Response(
        JSON.stringify({
          message: "Aurum Life API - Supabase Edge Function",
          version: "2.0.0",
          status: "operational",
          timestamp: new Date().toISOString()
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200 
        }
      )
    }

    // Health check - Public endpoint
    if (path === '/health' && method === 'GET') {
      return new Response(
        JSON.stringify({ 
          status: 'healthy', 
          timestamp: new Date().toISOString(),
          uptime: 'operational'
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200 
        }
      )
    }

    // Test endpoint - Public
    if (path === '/test' && method === 'GET') {
      return new Response(
        JSON.stringify({ 
          message: 'Aurum Life API Test Endpoint',
          status: 'success',
          timestamp: new Date().toISOString()
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200 
        }
      )
    }

    // API routes - These require authentication
    if (path.startsWith('/api/')) {
      const apiPath = path.replace('/api', '')
      
      // Handle different API endpoints
      switch (apiPath) {
        case '/tasks':
          return await handleTasks(req, supabaseClient)
        case '/projects':
          return await handleProjects(req, supabaseClient)
        case '/pillars':
          return await handlePillars(req, supabaseClient)
        case '/areas':
          return await handleAreas(req, supabaseClient)
        case '/journal':
          return await handleJournal(req, supabaseClient)
        default:
          return new Response(
            JSON.stringify({ error: 'Endpoint not found' }),
            { 
              headers: { ...corsHeaders, 'Content-Type': 'application/json' },
              status: 404 
            }
          )
      }
    }

    return new Response(
      JSON.stringify({ error: 'Route not found' }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 404 
      }
    )

  } catch (error) {
    console.error('Error:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500 
      }
    )
  }
})

// API Handler Functions
async function handleTasks(req: Request, supabase: any) {
  const { data, error } = await supabase
    .from('tasks')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error

  return new Response(
    JSON.stringify({ tasks: data }),
    { 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200 
    }
  )
}

async function handleProjects(req: Request, supabase: any) {
  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error

  return new Response(
    JSON.stringify({ projects: data }),
    { 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200 
    }
  )
}

async function handlePillars(req: Request, supabase: any) {
  const { data, error } = await supabase
    .from('pillars')
    .select('*')
    .order('sort_order', { ascending: true })

  if (error) throw error

  return new Response(
    JSON.stringify({ pillars: data }),
    { 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200 
    }
  )
}

async function handleAreas(req: Request, supabase: any) {
  const { data, error } = await supabase
    .from('areas')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error

  return new Response(
    JSON.stringify({ areas: data }),
    { 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200 
    }
  )
}

async function handleJournal(req: Request, supabase: any) {
  const { data, error } = await supabase
    .from('journal_entries')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) throw error

  return new Response(
    JSON.stringify({ entries: data }),
    { 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200 
    }
  )
}
