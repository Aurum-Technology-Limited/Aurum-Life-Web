/**
 * ULTRA-OPTIMIZED API CLIENT - Complete Performance Overhaul
 * Fixes: timeouts, runtime errors, memory leaks, concurrent request issues
 */

// Simple cache implementation
const apiCache = new Map();
const CACHE_TTL = 30000; // 30 seconds

// Request tracking to prevent duplicates
const activeRequests = new Map();

// Simple fetch wrapper with retry and timeout
const safeFetch = async (url, options = {}, retries = 2) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout
  
  try {
    console.log(`🌐 API Call: ${url}`);
    
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`✅ API Success: ${url}`);
    return { data };
    
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError') {
      console.error(`⏰ API Timeout: ${url}`);
      if (retries > 0) {
        console.log(`🔄 Retrying: ${url}`);
        await new Promise(resolve => setTimeout(resolve, 1000));
        return safeFetch(url, options, retries - 1);
      }
      throw new Error('Request timeout');
    }
    
    console.error(`❌ API Error: ${url}`, error.message);
    throw error;
  }
};

// Get auth token safely
const getAuthToken = () => {
  try {
    return localStorage.getItem('auth_token');
  } catch (e) {
    console.warn('Failed to get auth token:', e);
    return null;
  }
};

// API URL builder
const buildUrl = (endpoint) => {
  const baseUrl = process.env.REACT_APP_BACKEND_URL || '';
  return `${baseUrl}${endpoint}`;
};

// Ultra-simplified API methods
export const fixedAPI = {
  // Authentication
  login: async (credentials) => {
    const url = buildUrl('/api/auth/login');
    return safeFetch(url, {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
  },
  
  // Current user
  getCurrentUser: async () => {
    const cacheKey = 'current_user';
    
    // Check cache first
    if (apiCache.has(cacheKey)) {
      const cached = apiCache.get(cacheKey);
      if (Date.now() - cached.timestamp < CACHE_TTL) {
        console.log('📦 Using cached user data');
        return cached.data;
      }
    }
    
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    const url = buildUrl('/api/auth/me');
    const result = await safeFetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    // Cache the result
    apiCache.set(cacheKey, {
      data: result,
      timestamp: Date.now()
    });
    
    return result;
  },
  
  // Dashboard data
  getDashboard: async () => {
    const cacheKey = 'dashboard';
    
    // Check cache
    if (apiCache.has(cacheKey)) {
      const cached = apiCache.get(cacheKey);
      if (Date.now() - cached.timestamp < CACHE_TTL) {
        console.log('📦 Using cached dashboard data');
        return cached.data;
      }
    }
    
    // Prevent duplicate requests
    if (activeRequests.has(cacheKey)) {
      console.log('⏳ Dashboard request already in progress');
      return activeRequests.get(cacheKey);
    }
    
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    const url = buildUrl('/api/dashboard');
    const requestPromise = safeFetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    activeRequests.set(cacheKey, requestPromise);
    
    try {
      const result = await requestPromise;
      
      // Cache successful result
      apiCache.set(cacheKey, {
        data: result,
        timestamp: Date.now()
      });
      
      return result;
    } finally {
      activeRequests.delete(cacheKey);
    }
  },
  
  // AI Coach
  getAiCoach: async () => {
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    const url = buildUrl('/api/ai/task-why-statements');
    return safeFetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    });
  },
  
  // Insights (simplified)
  getInsights: async (dateRange = 'all_time') => {
    const cacheKey = `insights_${dateRange}`;
    
    // Check cache
    if (apiCache.has(cacheKey)) {
      const cached = apiCache.get(cacheKey);
      if (Date.now() - cached.timestamp < CACHE_TTL) {
        return cached.data;
      }
    }
    
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    const url = buildUrl(`/api/insights?date_range=${dateRange}`);
    const result = await safeFetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    // Cache result
    apiCache.set(cacheKey, {
      data: result,
      timestamp: Date.now()
    });
    
    return result;
  },
  
  // Areas
  getAreas: async (includeProjects = true, includeArchived = false) => {
    const cacheKey = `areas_${includeProjects}_${includeArchived}`;
    
    if (apiCache.has(cacheKey)) {
      const cached = apiCache.get(cacheKey);
      if (Date.now() - cached.timestamp < CACHE_TTL) {
        return cached.data;
      }
    }
    
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    const url = buildUrl(`/api/areas?include_projects=${includeProjects}&include_archived=${includeArchived}`);
    const result = await safeFetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    apiCache.set(cacheKey, {
      data: result,
      timestamp: Date.now()
    });
    
    return result;
  }
};

// Clear cache periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, value] of apiCache.entries()) {
    if (now - value.timestamp > CACHE_TTL) {
      apiCache.delete(key);
    }
  }
}, 60000); // Clean every minute

export default fixedAPI;