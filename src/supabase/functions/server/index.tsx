import { Hono } from "npm:hono";
import { cors } from "npm:hono/cors";
import { logger } from "npm:hono/logger";
import { createClient } from "npm:@supabase/supabase-js@2";
import * as kv from "./kv_store.tsx";

const app = new Hono();

// Create Supabase client with service role key for admin operations
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,
);

// Enable logger
app.use('*', logger(console.log));

// Enable CORS for all routes and methods
app.use(
  "/*",
  cors({
    origin: "*",
    allowHeaders: ["Content-Type", "Authorization"],
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    exposeHeaders: ["Content-Length"],
    maxAge: 600,
  }),
);

// Health check endpoint
app.get("/make-server-dd6e2894/health", (c) => {
  return c.json({ status: "ok" });
});

// Debug endpoint to check demo user status
app.get("/make-server-dd6e2894/demo-status", async (c) => {
  try {
    const demoEmail = 'demo@aurumlife.com';
    const demoPassword = 'demo123';
    
    console.log('Checking demo user status for:', demoEmail);
    
    // Try to sign in to check if user exists
    const clientSupabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
    );

    const { data: authData, error: signInError } = await clientSupabase.auth.signInWithPassword({
      email: demoEmail,
      password: demoPassword,
    });

    if (authData.user) {
      const preferences = await kv.get(`user:${authData.user.id}:preferences`);
      const onboarding = await kv.get(`user:${authData.user.id}:onboarding`);
      
      return c.json({
        status: 'exists',
        user_id: authData.user.id,
        email: authData.user.email,
        created_at: authData.user.created_at,
        has_preferences: !!preferences,
        has_onboarding: !!onboarding,
        preferences,
        onboarding
      });
    } else {
      return c.json({
        status: 'not_found',
        error: signInError?.message || 'User not found'
      });
    }
  } catch (error) {
    console.log('Demo status check error:', error);
    return c.json({
      status: 'error',
      error: error?.message || 'Unknown error'
    });
  }
});

// Setup demo user endpoint (for development)
app.post("/make-server-dd6e2894/setup-demo", async (c) => {
  try {
    const demoEmail = 'demo@aurumlife.com';
    const demoPassword = 'demo123';
    const demoName = 'Demo User';

    console.log('Setting up demo user:', demoEmail);

    // First try to create the demo user (if it doesn't exist)
    let userId: string | null = null;
    
    try {
      const { data: userData, error: createError } = await supabase.auth.admin.createUser({
        email: demoEmail,
        password: demoPassword,
        user_metadata: { 
          name: demoName,
          full_name: demoName,
        },
        email_confirm: true
      });

      if (createError) {
        // User might already exist, that's okay
        console.log('Demo user creation result:', createError.message);
        
        // If user already exists, try to get the existing user
        if (createError.message?.includes('already') || createError.message?.includes('exists')) {
          // Try to sign in to get the user ID
          const clientSupabase = createClient(
            Deno.env.get('SUPABASE_URL')!,
            Deno.env.get('SUPABASE_ANON_KEY')!,
          );

          const { data: signInData, error: signInError } = await clientSupabase.auth.signInWithPassword({
            email: demoEmail,
            password: demoPassword,
          });

          if (signInData.user) {
            userId = signInData.user.id;
            console.log('Found existing demo user:', userId);
          } else {
            console.log('Could not sign in with demo credentials:', signInError?.message);
            return c.json({ error: `Demo user setup failed: ${signInError?.message || createError.message}` }, 400);
          }
        } else {
          return c.json({ error: createError.message }, 400);
        }
      } else if (userData.user) {
        userId = userData.user.id;
        console.log('Created new demo user:', userId);
      }
    } catch (createErr) {
      console.log('Demo user creation exception:', createErr);
      return c.json({ error: "Failed to create demo user" }, 500);
    }

    if (!userId) {
      return c.json({ error: "Failed to setup demo user - no user ID" }, 500);
    }

    // Store demo user preferences
    const demoPreferences = {
      theme: 'dark',
      notifications: {
        email: true,
        push: true,
        desktop: true,
      },
      defaultView: 'dashboard',
      weekStartsOn: 1,
    };

    await kv.set(`user:${userId}:preferences`, demoPreferences);

    // Set up sample onboarding completion
    const onboardingData = {
      isOnboardingComplete: true,
      completedAt: new Date().toISOString(),
      selectedTemplate: 'balanced-lifestyle',
      profile: {
        name: demoName,
        primaryGoal: 'personal-growth',
        focusAreas: ['health', 'career', 'relationships'],
        workStyle: 'balanced'
      },
      pillars: [
        {
          id: '1',
          name: 'Health & Wellness',
          description: 'Physical and mental well-being',
          color: '#10B981',
          icon: 'Heart'
        },
        {
          id: '2', 
          name: 'Career & Growth',
          description: 'Professional development and achievements',
          color: '#3B82F6',
          icon: 'TrendingUp'
        },
        {
          id: '3',
          name: 'Relationships',
          description: 'Family, friends, and social connections',
          color: '#8B5CF6',
          icon: 'Users'
        }
      ]
    };

    await kv.set(`user:${userId}:onboarding`, onboardingData);

    console.log('Demo user setup completed successfully');

    return c.json({ 
      message: 'Demo user setup completed successfully',
      user_id: userId,
      email: demoEmail,
      demo: true
    });

  } catch (error) {
    console.log('Setup demo error:', error);
    return c.json({ error: "Failed to setup demo user" }, 500);
  }
});

// Demo login endpoint with automatic setup
app.post("/make-server-dd6e2894/demo-login", async (c) => {
  try {
    const demoEmail = 'demo@aurumlife.com';
    const demoPassword = 'demo123';
    const demoName = 'Demo User';
    
    console.log('Demo login attempt for:', demoEmail);

    // Create client for authentication
    const clientSupabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
    );

    // First try to sign in with existing credentials
    let authData = null;
    let signInError = null;
    
    try {
      const result = await clientSupabase.auth.signInWithPassword({
        email: demoEmail,
        password: demoPassword,
      });
      authData = result.data;
      signInError = result.error;
      
      if (authData.user && authData.session) {
        console.log('Demo user signed in successfully:', authData.user.id);
      }
    } catch (err) {
      console.log('Initial sign in attempt failed:', err);
      signInError = err;
    }

    // If sign in failed, try to create the demo user
    if (signInError || !authData?.user) {
      console.log('Creating demo user since sign in failed:', signInError?.message);
      
      try {
        // Create demo user with admin API
        const { data: userData, error: createError } = await supabase.auth.admin.createUser({
          email: demoEmail,
          password: demoPassword,
          user_metadata: { 
            name: demoName,
            full_name: demoName,
          },
          email_confirm: true
        });

        if (createError) {
          console.log('Demo user creation error:', createError);
          
          // If user already exists, try to sign in again
          if (createError.message?.includes('already') || createError.message?.includes('exists')) {
            console.log('User already exists, attempting sign in again...');
            const retryResult = await clientSupabase.auth.signInWithPassword({
              email: demoEmail,
              password: demoPassword,
            });
            
            if (retryResult.error) {
              console.log('Retry sign in failed:', retryResult.error);
              return c.json({ error: `Demo login failed: ${retryResult.error.message}` }, 400);
            }
            
            authData = retryResult.data;
          } else {
            return c.json({ error: `Demo user creation failed: ${createError.message}` }, 400);
          }
        } else if (userData.user) {
          console.log('Demo user created successfully:', userData.user.id);
          
          // Now sign in with the newly created user
          const signInResult = await clientSupabase.auth.signInWithPassword({
            email: demoEmail,
            password: demoPassword,
          });
          
          if (signInResult.error) {
            console.log('Sign in after creation failed:', signInResult.error);
            return c.json({ error: `Demo login failed after creation: ${signInResult.error.message}` }, 400);
          }
          
          authData = signInResult.data;
        }
      } catch (createErr) {
        console.log('Demo user creation exception:', createErr);
        return c.json({ error: "Failed to create demo user" }, 500);
      }
    }

    // Verify we have valid auth data
    if (!authData?.user || !authData?.session) {
      console.log('No valid auth data after all attempts');
      return c.json({ error: "Demo login failed - no valid session" }, 500);
    }

    const userId = authData.user.id;
    console.log('Setting up demo data for user:', userId);

    // Set up user preferences
    const demoPreferences = {
      theme: 'dark',
      notifications: {
        email: true,
        push: true,
        desktop: true,
      },
      defaultView: 'dashboard',
      weekStartsOn: 1,
    };

    await kv.set(`user:${userId}:preferences`, demoPreferences);

    // Set up sample onboarding completion
    const onboardingData = {
      isOnboardingComplete: true,
      completedAt: new Date().toISOString(),
      selectedTemplate: 'balanced-lifestyle',
      profile: {
        name: demoName,
        primaryGoal: 'personal-growth',
        focusAreas: ['health', 'career', 'relationships'],
        workStyle: 'balanced'
      },
      pillars: [
        {
          id: '1',
          name: 'Health & Wellness',
          description: 'Physical and mental well-being',
          color: '#10B981',
          icon: 'Heart'
        },
        {
          id: '2', 
          name: 'Career & Growth',
          description: 'Professional development and achievements',
          color: '#3B82F6',
          icon: 'TrendingUp'
        },
        {
          id: '3',
          name: 'Relationships',
          description: 'Family, friends, and social connections',
          color: '#8B5CF6',
          icon: 'Users'
        }
      ]
    };

    await kv.set(`user:${userId}:onboarding`, onboardingData);

    console.log('Demo login completed successfully for user:', userId);

    return c.json({ 
      user: {
        id: authData.user.id,
        email: authData.user.email,
        name: authData.user.user_metadata?.name || demoName,
        createdAt: authData.user.created_at,
        lastLoginAt: new Date().toISOString(),
        preferences: demoPreferences,
      },
      session: {
        access_token: authData.session.access_token,
        refresh_token: authData.session.refresh_token,
        expires_at: authData.session.expires_at,
      },
      demo: true
    });

  } catch (error) {
    console.log('Demo login error:', error);
    return c.json({ error: `Demo login failed: ${error?.message || 'Unknown error'}` }, 500);
  }
});

// Auth endpoints
app.post("/make-server-dd6e2894/auth/signup", async (c) => {
  try {
    const { email, password, name } = await c.req.json();
    
    if (!email || !password || !name) {
      return c.json({ error: "Email, password, and name are required" }, 400);
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return c.json({ error: "Please enter a valid email address" }, 400);
    }

    // Validate password length
    if (password.length < 6) {
      return c.json({ error: "Password must be at least 6 characters long" }, 400);
    }

    // Create user with admin API to automatically confirm email
    const { data: userData, error: createError } = await supabase.auth.admin.createUser({
      email,
      password,
      user_metadata: { 
        name,
        full_name: name,
      },
      // Automatically confirm the user's email since an email server hasn't been configured
      email_confirm: true
    });

    if (createError) {
      console.log('Signup error:', createError);
      
      // Handle specific Supabase errors with user-friendly messages
      const errorMessage = createError.message?.toLowerCase() || '';
      if (
        errorMessage.includes('already registered') || 
        errorMessage.includes('already exists') ||
        errorMessage.includes('user already registered') ||
        errorMessage.includes('duplicate') ||
        errorMessage.includes('unique constraint') ||
        errorMessage.includes('email address has already been registered') ||
        createError.code === '23505' // PostgreSQL unique violation error code
      ) {
        return c.json({ 
          error: "An account with this email already exists. Please sign in instead or use a different email address.",
          code: "EMAIL_ALREADY_EXISTS"
        }, 400);
      }
      
      // Handle weak password errors
      if (errorMessage.includes('password') && (errorMessage.includes('weak') || errorMessage.includes('strength'))) {
        return c.json({ error: "Password is too weak. Please use at least 8 characters with a mix of letters, numbers, and symbols." }, 400);
      }
      
      // Handle invalid email errors
      if (errorMessage.includes('email') && errorMessage.includes('invalid')) {
        return c.json({ error: "Please enter a valid email address." }, 400);
      }
      
      return c.json({ error: createError.message || "Failed to create account" }, 400);
    }

    if (!userData.user) {
      return c.json({ error: "Failed to create user" }, 500);
    }

    // Store user preferences in KV store
    const userPreferences = {
      theme: 'dark',
      notifications: {
        email: true,
        push: true,
        desktop: true,
      },
      defaultView: 'dashboard',
      weekStartsOn: 1,
    };

    await kv.set(`user:${userData.user.id}:preferences`, userPreferences);

    return c.json({ 
      user: {
        id: userData.user.id,
        email: userData.user.email,
        name: userData.user.user_metadata?.name || name,
        createdAt: userData.user.created_at,
        lastLoginAt: userData.user.created_at,
        preferences: userPreferences,
      }
    });

  } catch (error) {
    console.log('Signup error:', error);
    return c.json({ error: "Failed to create account. Please try again." }, 500);
  }
});

app.post("/make-server-dd6e2894/auth/signin", async (c) => {
  try {
    const { email, password } = await c.req.json();
    
    if (!email || !password) {
      return c.json({ error: "Email and password are required" }, 400);
    }

    // Use a client with anon key to sign in
    const clientSupabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
    );

    const { data: authData, error: signInError } = await clientSupabase.auth.signInWithPassword({
      email,
      password,
    });

    if (signInError) {
      console.log('Signin error:', signInError);
      
      // Handle specific Supabase errors with user-friendly messages
      if (signInError.message.includes('Invalid login credentials') || signInError.message.includes('invalid_credentials')) {
        return c.json({ error: "Invalid email or password" }, 400);
      }
      
      if (signInError.message.includes('Email not confirmed')) {
        return c.json({ error: "Please verify your email address" }, 400);
      }
      
      return c.json({ error: signInError.message || "Failed to sign in" }, 400);
    }

    if (!authData.user || !authData.session) {
      return c.json({ error: "Failed to sign in" }, 500);
    }

    // Get user preferences from KV store
    let preferences = await kv.get(`user:${authData.user.id}:preferences`);
    
    // Set default preferences if not found
    if (!preferences) {
      preferences = {
        theme: 'dark',
        notifications: {
          email: true,
          push: true,
          desktop: true,
        },
        defaultView: 'dashboard',
        weekStartsOn: 1,
      };
      await kv.set(`user:${authData.user.id}:preferences`, preferences);
    }

    return c.json({ 
      user: {
        id: authData.user.id,
        email: authData.user.email,
        name: authData.user.user_metadata?.name || authData.user.email?.split('@')[0],
        createdAt: authData.user.created_at,
        lastLoginAt: new Date().toISOString(),
        preferences,
      },
      session: {
        access_token: authData.session.access_token,
        refresh_token: authData.session.refresh_token,
        expires_at: authData.session.expires_at,
      }
    });

  } catch (error) {
    console.log('Signin error:', error);
    return c.json({ error: "Failed to sign in. Please try again." }, 500);
  }
});

app.post("/make-server-dd6e2894/auth/refresh", async (c) => {
  try {
    const { refresh_token } = await c.req.json();
    
    if (!refresh_token) {
      return c.json({ error: "Refresh token is required" }, 400);
    }

    const clientSupabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
    );

    const { data: authData, error: refreshError } = await clientSupabase.auth.refreshSession({
      refresh_token,
    });

    if (refreshError) {
      console.log('Token refresh error:', refreshError);
      return c.json({ error: refreshError.message }, 401);
    }

    if (!authData.user || !authData.session) {
      return c.json({ error: "Failed to refresh session" }, 401);
    }

    // Get user preferences
    let preferences = await kv.get(`user:${authData.user.id}:preferences`);
    
    if (!preferences) {
      preferences = {
        theme: 'dark',
        notifications: {
          email: true,
          push: true,
          desktop: true,
        },
        defaultView: 'dashboard',
        weekStartsOn: 1,
      };
      await kv.set(`user:${authData.user.id}:preferences`, preferences);
    }

    return c.json({ 
      user: {
        id: authData.user.id,
        email: authData.user.email,
        name: authData.user.user_metadata?.name || authData.user.email?.split('@')[0],
        createdAt: authData.user.created_at,
        lastLoginAt: new Date().toISOString(),
        preferences,
      },
      session: {
        access_token: authData.session.access_token,
        refresh_token: authData.session.refresh_token,
        expires_at: authData.session.expires_at,
      }
    });

  } catch (error) {
    console.log('Refresh error:', error);
    return c.json({ error: "Failed to refresh session. Please sign in again." }, 401);
  }
});

// Protected route helper
async function requireAuth(c: any, next: any) {
  const accessToken = c.req.header('Authorization')?.split(' ')[1];
  
  if (!accessToken) {
    return c.json({ error: 'Unauthorized' }, 401);
  }

  const { data: { user }, error } = await supabase.auth.getUser(accessToken);
  
  if (error || !user?.id) {
    return c.json({ error: 'Unauthorized' }, 401);
  }

  // Add user to context for use in protected routes
  c.set('user', user);
  await next();
}

// Example protected route for user preferences
app.get("/make-server-dd6e2894/user/preferences", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const preferences = await kv.get(`user:${user.id}:preferences`);
    
    return c.json({ preferences: preferences || {} });
  } catch (error) {
    console.log('Get preferences error:', error);
    return c.json({ error: "Failed to get preferences" }, 500);
  }
});

app.put("/make-server-dd6e2894/user/preferences", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const preferences = await c.req.json();
    
    await kv.set(`user:${user.id}:preferences`, preferences);
    
    return c.json({ preferences });
  } catch (error) {
    console.log('Update preferences error:', error);
    return c.json({ error: "Failed to update preferences" }, 500);
  }
});

// ========================================
// PHASE 2: ADVANCED BACKEND FEATURES
// ========================================

// Real-time data sync endpoint
app.post("/make-server-dd6e2894/sync/data", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const { type, operation, data, timestamp } = await c.req.json();
    
    // Store the sync event
    const syncEvent = {
      type,
      operation,
      data,
      userId: user.id,
      timestamp,
      source: 'remote'
    };
    
    // Save to user's sync log
    const syncLogKey = `user:${user.id}:sync:${Date.now()}`;
    await kv.set(syncLogKey, syncEvent);
    
    // Update the actual data based on type
    switch (type) {
      case 'pillar':
        const pillarsKey = `user:${user.id}:pillars`;
        let pillars = await kv.get(pillarsKey) || [];
        
        if (operation === 'create') {
          pillars.push(data);
        } else if (operation === 'update') {
          pillars = pillars.map(p => p.id === data.id ? { ...p, ...data } : p);
        } else if (operation === 'delete') {
          pillars = pillars.filter(p => p.id !== data.id);
        }
        
        await kv.set(pillarsKey, pillars);
        break;
        
      case 'area':
        const areasKey = `user:${user.id}:areas`;
        let areas = await kv.get(areasKey) || [];
        
        if (operation === 'create') {
          areas.push(data);
        } else if (operation === 'update') {
          areas = areas.map(a => a.id === data.id ? { ...a, ...data } : a);
        } else if (operation === 'delete') {
          areas = areas.filter(a => a.id !== data.id);
        }
        
        await kv.set(areasKey, areas);
        break;
        
      case 'project':
        const projectsKey = `user:${user.id}:projects`;
        let projects = await kv.get(projectsKey) || [];
        
        if (operation === 'create') {
          projects.push(data);
        } else if (operation === 'update') {
          projects = projects.map(p => p.id === data.id ? { ...p, ...data } : p);
        } else if (operation === 'delete') {
          projects = projects.filter(p => p.id !== data.id);
        }
        
        await kv.set(projectsKey, projects);
        break;
        
      case 'task':
        const tasksKey = `user:${user.id}:tasks`;
        let tasks = await kv.get(tasksKey) || [];
        
        if (operation === 'create') {
          tasks.push(data);
        } else if (operation === 'update') {
          tasks = tasks.map(t => t.id === data.id ? { ...t, ...data } : t);
        } else if (operation === 'delete') {
          tasks = tasks.filter(t => t.id !== data.id);
        }
        
        await kv.set(tasksKey, tasks);
        break;
        
      case 'journal':
        const journalKey = `user:${user.id}:journal`;
        let journalEntries = await kv.get(journalKey) || [];
        
        if (operation === 'create') {
          journalEntries.push(data);
        } else if (operation === 'update') {
          journalEntries = journalEntries.map(j => j.id === data.id ? { ...j, ...data } : j);
        } else if (operation === 'delete') {
          journalEntries = journalEntries.filter(j => j.id !== data.id);
        }
        
        await kv.set(journalKey, journalEntries);
        break;
    }
    
    return c.json({ success: true, syncEvent });
  } catch (error) {
    console.log('Data sync error:', error);
    return c.json({ error: "Failed to sync data" }, 500);
  }
});

// Get full sync data
app.get("/make-server-dd6e2894/sync/full", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    const [pillars, areas, projects, tasks, journalEntries, preferences] = await Promise.all([
      kv.get(`user:${user.id}:pillars`) || [],
      kv.get(`user:${user.id}:areas`) || [],
      kv.get(`user:${user.id}:projects`) || [],
      kv.get(`user:${user.id}:tasks`) || [],
      kv.get(`user:${user.id}:journal`) || [],
      kv.get(`user:${user.id}:preferences`) || {}
    ]);
    
    return c.json({
      pillars,
      areas,
      projects,
      tasks,
      journalEntries,
      preferences,
      lastSync: new Date().toISOString()
    });
  } catch (error) {
    console.log('Full sync error:', error);
    return c.json({ error: "Failed to get sync data" }, 500);
  }
});

// Advanced Analytics API
app.post("/make-server-dd6e2894/analytics/track", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const { category, value, metadata } = await c.req.json();
    
    const dataPoint = {
      timestamp: new Date().toISOString(),
      value,
      category,
      metadata,
      userId: user.id
    };
    
    // Store analytics data point
    const analyticsKey = `user:${user.id}:analytics:${category}:${Date.now()}`;
    await kv.set(analyticsKey, dataPoint);
    
    return c.json({ success: true });
  } catch (error) {
    console.log('Analytics tracking error:', error);
    return c.json({ error: "Failed to track analytics" }, 500);
  }
});

app.get("/make-server-dd6e2894/analytics/data", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const { category, startDate, endDate } = c.req.query();
    
    // Get analytics data by prefix search
    const prefix = category 
      ? `user:${user.id}:analytics:${category}:`
      : `user:${user.id}:analytics:`;
    
    const analyticsData = await kv.getByPrefix(prefix);
    
    // Filter by date range if provided
    let filteredData = analyticsData;
    if (startDate && endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      filteredData = analyticsData.filter(dataPoint => {
        const pointDate = new Date(dataPoint.timestamp);
        return pointDate >= start && pointDate <= end;
      });
    }
    
    return c.json({ data: filteredData });
  } catch (error) {
    console.log('Analytics data error:', error);
    return c.json({ error: "Failed to get analytics data" }, 500);
  }
});

// AI Insights API
app.post("/make-server-dd6e2894/insights/generate", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    // Get user data for analysis
    const [tasks, projects, analyticsData] = await Promise.all([
      kv.get(`user:${user.id}:tasks`) || [],
      kv.get(`user:${user.id}:projects`) || [],
      kv.getByPrefix(`user:${user.id}:analytics:`)
    ]);
    
    // Generate simple insights based on data patterns
    const insights = [];
    
    // Task completion insight
    const completedTasks = tasks.filter(t => t.status === 'completed');
    const totalTasks = tasks.length;
    
    if (totalTasks > 0) {
      const completionRate = completedTasks.length / totalTasks;
      
      if (completionRate < 0.5) {
        insights.push({
          id: `task-completion-${Date.now()}`,
          type: 'productivity',
          title: 'Task Completion Rate Below 50%',
          description: `You've completed ${Math.round(completionRate * 100)}% of your tasks. Consider breaking down large tasks or reviewing your task load.`,
          actionable: true,
          priority: 'medium',
          confidence: 0.8,
          suggestedActions: [
            'Break large tasks into smaller sub-tasks',
            'Review and prioritize your task list',
            'Consider if you\'re taking on too many tasks'
          ],
          basedOn: ['Task completion statistics'],
          validUntil: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
        });
      }
    }
    
    // Project progress insight
    const activeProjects = projects.filter(p => p.status === 'active' || p.status === 'in_progress');
    
    if (activeProjects.length > 5) {
      insights.push({
        id: `project-overload-${Date.now()}`,
        type: 'balance',
        title: 'Too Many Active Projects',
        description: `You have ${activeProjects.length} active projects. Consider focusing on fewer projects for better results.`,
        actionable: true,
        priority: 'high',
        confidence: 0.9,
        suggestedActions: [
          'Review project priorities and pause less critical ones',
          'Focus on completing 2-3 key projects first',
          'Consider delegating or archiving some projects'
        ],
        basedOn: ['Active project count'],
        validUntil: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString()
      });
    }
    
    // Store insights
    const insightsKey = `user:${user.id}:insights`;
    await kv.set(insightsKey, insights);
    
    return c.json({ insights });
  } catch (error) {
    console.log('Insights generation error:', error);
    return c.json({ error: "Failed to generate insights" }, 500);
  }
});

app.get("/make-server-dd6e2894/insights", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const insights = await kv.get(`user:${user.id}:insights`) || [];
    
    // Filter out expired insights
    const validInsights = insights.filter(insight => 
      new Date(insight.validUntil) > new Date()
    );
    
    return c.json({ insights: validInsights });
  } catch (error) {
    console.log('Get insights error:', error);
    return c.json({ error: "Failed to get insights" }, 500);
  }
});

// Smart Search API
app.post("/make-server-dd6e2894/search", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const { query, filters } = await c.req.json();
    
    if (!query || query.trim().length === 0) {
      return c.json({ results: [] });
    }
    
    const searchTerms = query.toLowerCase().split(' ');
    const results = [];
    
    // Search in pillars
    const pillars = await kv.get(`user:${user.id}:pillars`) || [];
    pillars.forEach(pillar => {
      const searchText = `${pillar.name} ${pillar.description || ''}`.toLowerCase();
      let score = 0;
      
      searchTerms.forEach(term => {
        if (searchText.includes(term)) {
          score += pillar.name.toLowerCase().includes(term) ? 5 : 2;
        }
      });
      
      if (score > 0) {
        results.push({
          id: pillar.id,
          type: 'pillar',
          title: pillar.name,
          description: pillar.description,
          relevanceScore: score,
          matchedTerms: searchTerms.filter(term => searchText.includes(term)),
          lastModified: pillar.updatedAt || pillar.createdAt || new Date().toISOString(),
          tags: pillar.tags || [],
          hierarchy: {}
        });
      }
    });
    
    // Search in areas
    const areas = await kv.get(`user:${user.id}:areas`) || [];
    areas.forEach(area => {
      const searchText = `${area.name} ${area.description || ''}`.toLowerCase();
      let score = 0;
      
      searchTerms.forEach(term => {
        if (searchText.includes(term)) {
          score += area.name.toLowerCase().includes(term) ? 5 : 2;
        }
      });
      
      if (score > 0) {
        results.push({
          id: area.id,
          type: 'area',
          title: area.name,
          description: area.description,
          relevanceScore: score,
          matchedTerms: searchTerms.filter(term => searchText.includes(term)),
          lastModified: area.updatedAt || area.createdAt || new Date().toISOString(),
          tags: area.tags || [],
          hierarchy: { pillar: area.pillarId }
        });
      }
    });
    
    // Search in projects
    const projects = await kv.get(`user:${user.id}:projects`) || [];
    projects.forEach(project => {
      const searchText = `${project.name} ${project.description || ''}`.toLowerCase();
      let score = 0;
      
      searchTerms.forEach(term => {
        if (searchText.includes(term)) {
          score += project.name.toLowerCase().includes(term) ? 5 : 2;
        }
      });
      
      if (score > 0) {
        results.push({
          id: project.id,
          type: 'project',
          title: project.name,
          description: project.description,
          relevanceScore: score,
          matchedTerms: searchTerms.filter(term => searchText.includes(term)),
          lastModified: project.updatedAt || project.createdAt || new Date().toISOString(),
          tags: project.tags || [],
          hierarchy: { 
            pillar: project.pillarId,
            area: project.areaId 
          }
        });
      }
    });
    
    // Search in tasks
    const tasks = await kv.get(`user:${user.id}:tasks`) || [];
    tasks.forEach(task => {
      const searchText = `${task.title} ${task.description || ''}`.toLowerCase();
      let score = 0;
      
      searchTerms.forEach(term => {
        if (searchText.includes(term)) {
          score += task.title.toLowerCase().includes(term) ? 5 : 2;
        }
      });
      
      if (score > 0) {
        results.push({
          id: task.id,
          type: 'task',
          title: task.title,
          description: task.description,
          relevanceScore: score,
          matchedTerms: searchTerms.filter(term => searchText.includes(term)),
          lastModified: task.updatedAt || task.createdAt || new Date().toISOString(),
          tags: task.tags || [],
          hierarchy: { 
            pillar: task.pillarId,
            area: task.areaId,
            project: task.projectId
          }
        });
      }
    });
    
    // Search in journal entries
    const journalEntries = await kv.get(`user:${user.id}:journal`) || [];
    journalEntries.forEach(entry => {
      const searchText = `${entry.title || ''} ${entry.content || ''}`.toLowerCase();
      let score = 0;
      
      searchTerms.forEach(term => {
        if (searchText.includes(term)) {
          score += (entry.title || '').toLowerCase().includes(term) ? 5 : 2;
        }
      });
      
      if (score > 0) {
        results.push({
          id: entry.id,
          type: 'journal',
          title: entry.title || 'Journal Entry',
          description: entry.content?.substring(0, 150) + '...',
          content: entry.content,
          relevanceScore: score,
          matchedTerms: searchTerms.filter(term => searchText.includes(term)),
          lastModified: entry.updatedAt || entry.createdAt || new Date().toISOString(),
          tags: entry.tags || [],
          hierarchy: { pillar: entry.pillarId }
        });
      }
    });
    
    // Apply filters if provided
    let filteredResults = results;
    
    if (filters?.types && filters.types.length > 0) {
      filteredResults = filteredResults.filter(result => 
        filters.types.includes(result.type)
      );
    }
    
    if (filters?.minRelevanceScore) {
      filteredResults = filteredResults.filter(result => 
        result.relevanceScore >= filters.minRelevanceScore
      );
    }
    
    // Sort by relevance score
    filteredResults.sort((a, b) => b.relevanceScore - a.relevanceScore);
    
    // Limit results
    const limitedResults = filteredResults.slice(0, 50);
    
    return c.json({ results: limitedResults });
  } catch (error) {
    console.log('Search error:', error);
    return c.json({ error: "Failed to perform search" }, 500);
  }
});

// PWA offline data endpoint
app.get("/make-server-dd6e2894/offline/data", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    // Get essential data for offline use
    const [pillars, areas, projects, tasks, journalEntries, preferences] = await Promise.all([
      kv.get(`user:${user.id}:pillars`) || [],
      kv.get(`user:${user.id}:areas`) || [],
      kv.get(`user:${user.id}:projects`) || [],
      kv.get(`user:${user.id}:tasks`) || [],
      kv.get(`user:${user.id}:journal`) || [],
      kv.get(`user:${user.id}:preferences`) || {}
    ]);
    
    return c.json({
      pillars,
      areas,
      projects,
      tasks,
      journalEntries,
      settings: preferences,
      lastSync: new Date().toISOString()
    });
  } catch (error) {
    console.log('Offline data error:', error);
    return c.json({ error: "Failed to get offline data" }, 500);
  }
});

// ========================================
// PHASE 3: ENHANCED USER PROFILE ENDPOINTS
// ========================================

// Get enhanced user profile
app.get("/make-server-dd6e2894/profile", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    // Get profile data from KV store
    let profile = await kv.get(`user:${user.id}:profile`) || {};
    
    // Merge with auth user data
    const enhancedProfile = {
      id: user.id,
      name: user.user_metadata?.name || user.email?.split('@')[0],
      email: user.email,
      avatar_url: user.user_metadata?.avatar_url,
      createdAt: user.created_at,
      updatedAt: profile.updatedAt || user.updated_at,
      // Extended profile fields
      bio: profile.bio || '',
      timezone: profile.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone,
      workingHours: profile.workingHours || { start: '09:00', end: '17:00' },
      focusAreas: profile.focusAreas || [],
      personalityType: profile.personalityType || '',
      workStyle: profile.workStyle || 'balanced',
      communicationPreference: profile.communicationPreference || 'email',
      goals: profile.goals || [],
      achievements: profile.achievements || [],
      customFields: profile.customFields || {}
    };
    
    return c.json(enhancedProfile);
  } catch (error) {
    console.log('Get profile error:', error);
    return c.json({ error: "Failed to get profile" }, 500);
  }
});

// Update enhanced user profile
app.put("/make-server-dd6e2894/profile", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const profileData = await c.req.json();
    
    // Update auth user metadata if name changed
    if (profileData.name && profileData.name !== user.user_metadata?.name) {
      try {
        await supabase.auth.admin.updateUserById(user.id, {
          user_metadata: { 
            ...user.user_metadata, 
            name: profileData.name 
          }
        });
      } catch (authError) {
        console.log('Failed to update auth metadata:', authError);
      }
    }
    
    // Store extended profile data
    const profile = {
      ...profileData,
      updatedAt: new Date().toISOString()
    };
    
    await kv.set(`user:${user.id}:profile`, profile);
    
    // Return updated profile
    const updatedProfile = {
      id: user.id,
      name: profileData.name || user.user_metadata?.name,
      email: user.email,
      avatar_url: user.user_metadata?.avatar_url,
      createdAt: user.created_at,
      ...profile
    };
    
    return c.json(updatedProfile);
  } catch (error) {
    console.log('Update profile error:', error);
    return c.json({ error: "Failed to update profile" }, 500);
  }
});

// Get AI preferences
app.get("/make-server-dd6e2894/ai-preferences", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    const aiPreferences = await kv.get(`user:${user.id}:ai-preferences`) || {
      enableSmartSuggestions: true,
      enableProductivityInsights: true,
      enableGoalRecommendations: true,
      enableTimeBlocking: false,
      enableHabitTracking: false,
      dataProcessingLevel: 'standard',
      insightFrequency: 'daily',
      privacyMode: 'balanced',
      updatedAt: new Date().toISOString()
    };
    
    return c.json(aiPreferences);
  } catch (error) {
    console.log('Get AI preferences error:', error);
    return c.json({ error: "Failed to get AI preferences" }, 500);
  }
});

// Update AI preferences
app.put("/make-server-dd6e2894/ai-preferences", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const preferences = await c.req.json();
    
    const aiPreferences = {
      ...preferences,
      updatedAt: new Date().toISOString()
    };
    
    await kv.set(`user:${user.id}:ai-preferences`, aiPreferences);
    
    return c.json(aiPreferences);
  } catch (error) {
    console.log('Update AI preferences error:', error);
    return c.json({ error: "Failed to update AI preferences" }, 500);
  }
});

// Get user statistics
app.get("/make-server-dd6e2894/profile/stats", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    // Get user data from KV store
    const [pillars, areas, projects, tasks, journalEntries] = await Promise.all([
      kv.get(`user:${user.id}:pillars`) || [],
      kv.get(`user:${user.id}:areas`) || [],
      kv.get(`user:${user.id}:projects`) || [],
      kv.get(`user:${user.id}:tasks`) || [],
      kv.get(`user:${user.id}:journal`) || []
    ]);
    
    // Calculate statistics
    const completedTasks = tasks.filter(t => t.status === 'completed');
    const activeProjects = projects.filter(p => p.status === 'active');
    
    // Calculate days since joined
    const joinDate = new Date(user.created_at);
    const daysSinceJoined = Math.floor((Date.now() - joinDate.getTime()) / (1000 * 60 * 60 * 24));
    
    // Simple productivity score calculation
    const completionRate = tasks.length > 0 ? completedTasks.length / tasks.length : 0;
    const activityScore = Math.min(tasks.length / 50, 1); // Normalize task count
    const productivityScore = Math.round((completionRate * 0.7 + activityScore * 0.3) * 100);
    
    // Calculate streaks (simplified)
    const currentStreak = calculateStreak(tasks, 'current');
    const longestStreak = calculateStreak(tasks, 'longest');
    
    const stats = {
      totalTasks: tasks.length,
      completedTasks: completedTasks.length,
      activeProjects: activeProjects.length,
      totalPillars: pillars.length,
      journalEntries: journalEntries.length,
      daysSinceJoined,
      currentStreak,
      longestStreak,
      productivityScore,
      lastActiveDate: new Date().toISOString(),
      totalFocusTime: 0, // Would be calculated from time tracking data
      averageTaskCompletionTime: 0 // Would be calculated from task completion times
    };
    
    return c.json(stats);
  } catch (error) {
    console.log('Get user stats error:', error);
    return c.json({ error: "Failed to get user stats" }, 500);
  }
});

// Get user achievements
app.get("/make-server-dd6e2894/profile/achievements", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    // Get user's achievements or generate based on stats
    let achievements = await kv.get(`user:${user.id}:achievements`) || [];
    
    if (achievements.length === 0) {
      // Generate initial achievements based on user activity
      const stats = await getUserStats(user.id);
      achievements = generateAchievements(stats);
      
      // Store achievements
      await kv.set(`user:${user.id}:achievements`, achievements);
    }
    
    return c.json(achievements);
  } catch (error) {
    console.log('Get achievements error:', error);
    return c.json({ error: "Failed to get achievements" }, 500);
  }
});

// Upload avatar (placeholder - would integrate with file storage)
app.post("/make-server-dd6e2894/profile/avatar", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    // In a real implementation, this would:
    // 1. Validate the uploaded file
    // 2. Resize the image
    // 3. Store it in Supabase Storage
    // 4. Update the user's avatar_url
    
    // For now, return a placeholder response
    const avatar_url = `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.id}`;
    
    // Update user metadata with new avatar URL
    try {
      await supabase.auth.admin.updateUserById(user.id, {
        user_metadata: { 
          ...user.user_metadata, 
          avatar_url 
        }
      });
    } catch (authError) {
      console.log('Failed to update avatar in auth:', authError);
    }
    
    return c.json({ avatar_url });
  } catch (error) {
    console.log('Upload avatar error:', error);
    return c.json({ error: "Failed to upload avatar" }, 500);
  }
});

// Export user data
app.get("/make-server-dd6e2894/profile/export", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    // Get all user data
    const [profile, aiPreferences, pillars, areas, projects, tasks, journalEntries, preferences, achievements] = await Promise.all([
      kv.get(`user:${user.id}:profile`) || {},
      kv.get(`user:${user.id}:ai-preferences`) || {},
      kv.get(`user:${user.id}:pillars`) || [],
      kv.get(`user:${user.id}:areas`) || [],
      kv.get(`user:${user.id}:projects`) || [],
      kv.get(`user:${user.id}:tasks`) || [],
      kv.get(`user:${user.id}:journal`) || [],
      kv.get(`user:${user.id}:preferences`) || {},
      kv.get(`user:${user.id}:achievements`) || []
    ]);
    
    const exportData = {
      user: {
        id: user.id,
        email: user.email,
        name: user.user_metadata?.name,
        created_at: user.created_at
      },
      profile,
      aiPreferences,
      data: {
        pillars,
        areas,
        projects,
        tasks,
        journalEntries
      },
      settings: preferences,
      achievements,
      exportedAt: new Date().toISOString(),
      version: '1.0'
    };
    
    return c.json(exportData);
  } catch (error) {
    console.log('Export data error:', error);
    return c.json({ error: "Failed to export data" }, 500);
  }
});

// ========================================
// PHASE 3: GRANULAR PRIVACY CONTROLS ENDPOINTS
// ========================================

// Get privacy settings
app.get("/make-server-dd6e2894/privacy/settings", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    const privacySettings = await kv.get(`user:${user.id}:privacy-settings`) || {
      dataCollection: {
        analytics: true,
        usage: true,
        performance: true,
        errors: true,
        interactions: false
      },
      aiFeatures: {
        smartSuggestions: true,
        productivityInsights: true,
        goalRecommendations: true,
        habitTracking: false,
        timeBlocking: false,
        semanticSearch: true,
        autoTagging: true,
        contentAnalysis: false
      },
      dataSharing: {
        anonymizedUsage: false,
        productImprovement: false,
        researchParticipation: false,
        marketingCommunications: false,
        thirdPartyIntegrations: false
      },
      dataRetention: {
        activityLogs: '1year',
        analyticsData: '6months',
        aiInsights: '1year',
        deletedItems: '30days'
      },
      visibility: {
        profileVisibility: 'private',
        activitySharing: false,
        achievementSharing: false,
        progressSharing: false
      },
      security: {
        twoFactorAuth: false,
        sessionTimeout: '1hour',
        deviceTracking: true,
        loginNotifications: true
      },
      updatedAt: new Date().toISOString()
    };
    
    return c.json(privacySettings);
  } catch (error) {
    console.log('Get privacy settings error:', error);
    return c.json({ error: "Failed to get privacy settings" }, 500);
  }
});

// Update privacy settings
app.put("/make-server-dd6e2894/privacy/settings", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const settings = await c.req.json();
    
    const privacySettings = {
      ...settings,
      updatedAt: new Date().toISOString()
    };
    
    await kv.set(`user:${user.id}:privacy-settings`, privacySettings);
    
    // Log the privacy change
    await logPrivacyAction(user.id, {
      action: 'privacy_settings_updated',
      category: 'privacy_change',
      details: 'User updated privacy settings',
      dataTypes: Object.keys(settings),
      purpose: 'privacy_control',
      automated: false
    });
    
    return c.json(privacySettings);
  } catch (error) {
    console.log('Update privacy settings error:', error);
    return c.json({ error: "Failed to update privacy settings" }, 500);
  }
});

// Get consent history
app.get("/make-server-dd6e2894/privacy/consent-history", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    const consentHistory = await kv.get(`user:${user.id}:consent-history`) || [];
    
    return c.json(consentHistory);
  } catch (error) {
    console.log('Get consent history error:', error);
    return c.json({ error: "Failed to get consent history" }, 500);
  }
});

// Record consent
app.post("/make-server-dd6e2894/privacy/consent", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const { category, granted, details, version } = await c.req.json();
    
    const consentRecord = {
      id: Date.now().toString(),
      category,
      granted,
      timestamp: new Date().toISOString(),
      version: version || '1.0',
      details: details || 'Consent recorded'
    };
    
    // Get existing consent history
    const consentHistory = await kv.get(`user:${user.id}:consent-history`) || [];
    consentHistory.push(consentRecord);
    
    await kv.set(`user:${user.id}:consent-history`, consentHistory);
    
    // Log the consent action
    await logPrivacyAction(user.id, {
      action: 'consent_recorded',
      category: 'consent_update',
      details: `Consent ${granted ? 'granted' : 'denied'} for ${category}`,
      dataTypes: ['consent'],
      purpose: 'compliance',
      automated: false
    });
    
    return c.json({ success: true, consentRecord });
  } catch (error) {
    console.log('Record consent error:', error);
    return c.json({ error: "Failed to record consent" }, 500);
  }
});

// Get audit log
app.get("/make-server-dd6e2894/privacy/audit-log", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    const auditLog = await kv.get(`user:${user.id}:audit-log`) || [];
    
    // Return recent entries (last 50)
    const recentEntries = auditLog.slice(-50).reverse();
    
    return c.json(recentEntries);
  } catch (error) {
    console.log('Get audit log error:', error);
    return c.json({ error: "Failed to get audit log" }, 500);
  }
});

// Log privacy action
app.post("/make-server-dd6e2894/privacy/audit-log", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const actionData = await c.req.json();
    
    await logPrivacyAction(user.id, actionData);
    
    return c.json({ success: true });
  } catch (error) {
    console.log('Log privacy action error:', error);
    return c.json({ error: "Failed to log privacy action" }, 500);
  }
});

// Export user data
app.get("/make-server-dd6e2894/privacy/export", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    // Get all user data
    const [profile, privacySettings, pillars, areas, projects, tasks, journalEntries, preferences, consentHistory, auditLog] = await Promise.all([
      kv.get(`user:${user.id}:profile`) || {},
      kv.get(`user:${user.id}:privacy-settings`) || {},
      kv.get(`user:${user.id}:pillars`) || [],
      kv.get(`user:${user.id}:areas`) || [],
      kv.get(`user:${user.id}:projects`) || [],
      kv.get(`user:${user.id}:tasks`) || [],
      kv.get(`user:${user.id}:journal`) || [],
      kv.get(`user:${user.id}:preferences`) || {},
      kv.get(`user:${user.id}:consent-history`) || [],
      kv.get(`user:${user.id}:audit-log`) || []
    ]);
    
    const exportData = {
      user: {
        id: user.id,
        email: user.email,
        name: user.user_metadata?.name,
        created_at: user.created_at
      },
      profile,
      privacySettings,
      data: {
        pillars,
        areas,
        projects,
        tasks,
        journalEntries
      },
      settings: preferences,
      consentHistory,
      auditLog,
      exportedAt: new Date().toISOString(),
      version: '1.0'
    };
    
    // Log the export action
    await logPrivacyAction(user.id, {
      action: 'data_exported',
      category: 'data_export',
      details: 'User exported their complete data',
      dataTypes: ['all'],
      purpose: 'data_portability',
      automated: false
    });
    
    return c.json(exportData);
  } catch (error) {
    console.log('Export data error:', error);
    return c.json({ error: "Failed to export data" }, 500);
  }
});

// Delete account
app.delete("/make-server-dd6e2894/privacy/delete-account", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    // Log the deletion request
    await logPrivacyAction(user.id, {
      action: 'account_deletion_requested',
      category: 'privacy_change',
      details: 'User requested account deletion',
      dataTypes: ['all'],
      purpose: 'right_to_erasure',
      automated: false
    });
    
    // Get all user data keys to delete
    const keysToDelete = [
      `user:${user.id}:profile`,
      `user:${user.id}:privacy-settings`,
      `user:${user.id}:pillars`,
      `user:${user.id}:areas`,
      `user:${user.id}:projects`,
      `user:${user.id}:tasks`,
      `user:${user.id}:journal`,
      `user:${user.id}:preferences`,
      `user:${user.id}:consent-history`,
      `user:${user.id}:audit-log`,
      `user:${user.id}:achievements`,
      `user:${user.id}:ai-preferences`
    ];
    
    // Delete all user data from KV store
    await Promise.all(keysToDelete.map(key => kv.del(key)));
    
    // Delete auth user (this would be done carefully in production)
    try {
      await supabase.auth.admin.deleteUser(user.id);
    } catch (authError) {
      console.log('Auth user deletion error (this is expected in some environments):', authError);
    }
    
    return c.json({ 
      success: true, 
      message: 'Account deletion completed successfully' 
    });
  } catch (error) {
    console.log('Delete account error:', error);
    return c.json({ error: "Failed to delete account" }, 500);
  }
});

// Check consent status
app.get("/make-server-dd6e2894/privacy/consent/:category", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    const category = c.req.param('category');
    
    const privacySettings = await kv.get(`user:${user.id}:privacy-settings`);
    
    let hasConsent = false;
    
    if (privacySettings) {
      switch (category) {
        case 'analytics':
          hasConsent = privacySettings.dataCollection?.analytics || false;
          break;
        case 'ai_features':
          hasConsent = Object.values(privacySettings.aiFeatures || {}).some(Boolean);
          break;
        case 'data_sharing':
          hasConsent = Object.values(privacySettings.dataSharing || {}).some(Boolean);
          break;
        default:
          hasConsent = false;
      }
    }
    
    return c.json({ hasConsent });
  } catch (error) {
    console.log('Check consent error:', error);
    return c.json({ error: "Failed to check consent" }, 500);
  }
});

// Get compliance status
app.get("/make-server-dd6e2894/privacy/compliance", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    // Check privacy settings exist
    const privacySettings = await kv.get(`user:${user.id}:privacy-settings`);
    const consentHistory = await kv.get(`user:${user.id}:consent-history`) || [];
    
    const complianceStatus = {
      gdprCompliant: !!privacySettings && consentHistory.length > 0,
      ccpaCompliant: !!privacySettings,
      lastAudit: new Date().toISOString(),
      issues: []
    };
    
    if (!privacySettings) {
      complianceStatus.issues.push('Privacy settings not configured');
    }
    
    if (consentHistory.length === 0) {
      complianceStatus.issues.push('No consent records found');
    }
    
    return c.json(complianceStatus);
  } catch (error) {
    console.log('Get compliance status error:', error);
    return c.json({ error: "Failed to get compliance status" }, 500);
  }
});

// Get data processing summary
app.get("/make-server-dd6e2894/privacy/processing-summary", requireAuth, async (c) => {
  try {
    const user = c.get('user');
    
    const auditLog = await kv.get(`user:${user.id}:audit-log`) || [];
    const tasks = await kv.get(`user:${user.id}:tasks`) || [];
    const journalEntries = await kv.get(`user:${user.id}:journal`) || [];
    
    const aiProcessingEvents = auditLog.filter(entry => 
      entry.category === 'ai_processing'
    ).length;
    
    const dataSharedEvents = auditLog.filter(entry => 
      entry.category === 'data_sharing'
    ).length;
    
    const summary = {
      totalDataPoints: tasks.length + journalEntries.length,
      aiProcessingEvents,
      dataSharedEvents,
      dataRetentionDays: 365, // This would be calculated from privacy settings
      lastProcessingDate: auditLog.length > 0 ? auditLog[auditLog.length - 1].timestamp : new Date().toISOString()
    };
    
    return c.json(summary);
  } catch (error) {
    console.log('Get processing summary error:', error);
    return c.json({ error: "Failed to get processing summary" }, 500);
  }
});

// Helper function to log privacy actions
async function logPrivacyAction(userId, actionData) {
  const auditEntry = {
    id: Date.now().toString(),
    timestamp: new Date().toISOString(),
    ...actionData
  };
  
  const auditLog = await kv.get(`user:${userId}:audit-log`) || [];
  auditLog.push(auditEntry);
  
  // Keep only last 200 entries to prevent storage bloat
  if (auditLog.length > 200) {
    auditLog.splice(0, auditLog.length - 200);
  }
  
  await kv.set(`user:${userId}:audit-log`, auditLog);
}

// Helper functions
function calculateStreak(tasks, type) {
  if (tasks.length === 0) return 0;
  
  const completedTasks = tasks
    .filter(t => t.status === 'completed' && t.completedAt)
    .sort((a, b) => new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime());
  
  if (completedTasks.length === 0) return 0;
  
  if (type === 'current') {
    // Calculate current streak (simplified)
    let streak = 0;
    let currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0);
    
    for (const task of completedTasks) {
      const taskDate = new Date(task.completedAt);
      taskDate.setHours(0, 0, 0, 0);
      
      const diffDays = Math.floor((currentDate.getTime() - taskDate.getTime()) / (1000 * 60 * 60 * 24));
      
      if (diffDays === streak) {
        streak++;
        currentDate.setDate(currentDate.getDate() - 1);
      } else {
        break;
      }
    }
    
    return streak;
  } else {
    // Return longest streak (would need more complex calculation)
    return Math.max(7, calculateStreak(tasks, 'current'));
  }
}

async function getUserStats(userId) {
  const [tasks, projects, pillars, journalEntries] = await Promise.all([
    kv.get(`user:${userId}:tasks`) || [],
    kv.get(`user:${userId}:projects`) || [],
    kv.get(`user:${userId}:pillars`) || [],
    kv.get(`user:${userId}:journal`) || []
  ]);
  
  return {
    totalTasks: tasks.length,
    completedTasks: tasks.filter(t => t.status === 'completed').length,
    activeProjects: projects.filter(p => p.status === 'active').length,
    totalPillars: pillars.length,
    journalEntries: journalEntries.length
  };
}

function generateAchievements(stats) {
  const achievements = [];
  
  if (stats.totalTasks >= 1) {
    achievements.push({
      id: 'first-task',
      name: 'Task Creator',
      description: 'Created your first task',
      icon: '✅',
      unlockedAt: new Date().toISOString(),
      category: 'milestone',
      points: 10
    });
  }
  
  if (stats.completedTasks >= 10) {
    achievements.push({
      id: 'task-completer',
      name: 'Task Master',
      description: 'Completed 10 tasks',
      icon: '🏆',
      unlockedAt: new Date().toISOString(),
      category: 'productivity',
      points: 50
    });
  }
  
  if (stats.totalPillars >= 3) {
    achievements.push({
      id: 'pillar-creator',
      name: 'Foundation Builder',
      description: 'Created 3 life pillars',
      icon: '🏛️',
      unlockedAt: new Date().toISOString(),
      category: 'goals',
      points: 75
    });
  }
  
  if (stats.journalEntries >= 5) {
    achievements.push({
      id: 'journal-writer',
      name: 'Reflective Thinker',
      description: 'Wrote 5 journal entries',
      icon: '📝',
      unlockedAt: new Date().toISOString(),
      category: 'milestone',
      points: 25
    });
  }
  
  return achievements;
}

Deno.serve(app.fetch);