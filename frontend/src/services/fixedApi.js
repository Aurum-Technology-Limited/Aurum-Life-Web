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
  // Ultra-Fast Authentication with Performance Optimization
  login: async (credentials) => {
    console.log('🚀 Starting ultra-fast login process...');
    const startTime = Date.now();
    
    try {
      const url = buildUrl('/api/auth/login');
      
      // Optimized login with reduced timeout for faster failure detection
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout for login
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`Login failed: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      const loginTime = Date.now() - startTime;
      
      console.log(`✅ Ultra-fast login completed in ${loginTime}ms`);
      
      // Performance target check
      if (loginTime > 500) {
        console.warn(`⚠️ Login time ${loginTime}ms exceeds 500ms target`);
      } else {
        console.log(`🎯 Login performance target achieved: ${loginTime}ms < 500ms`);
      }
      
      return { data };
      
    } catch (error) {
      const failTime = Date.now() - startTime;
      console.error(`❌ Login failed after ${failTime}ms:`, error.message);
      throw error;
    }
  },
  
  // Ultra-Fast Current User with Performance Monitoring
  getCurrentUser: async () => {
    const startTime = Date.now();
    const cacheKey = 'current_user';
    
    // Check cache first for instant response
    if (apiCache.has(cacheKey)) {
      const cached = apiCache.get(cacheKey);
      if (Date.now() - cached.timestamp < CACHE_TTL) {
        const cacheTime = Date.now() - startTime;
        console.log(`📦 Using cached user data (${cacheTime}ms)`);
        return cached.data;
      }
    }
    
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    try {
      const url = buildUrl('/api/auth/me');
      
      // Optimized user fetch with reduced timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
      
      const response = await fetch(url, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`User fetch failed: ${response.status}`);
      }
      
      const data = await response.json();
      const result = { data };
      
      // Cache the result for future requests
      apiCache.set(cacheKey, {
        data: result,
        timestamp: Date.now()
      });
      
      const totalTime = Date.now() - startTime;
      console.log(`✅ User data fetched in ${totalTime}ms`);
      
      if (totalTime > 200) {
        console.warn(`⚠️ User fetch time ${totalTime}ms exceeds 200ms target`);
      }
      
      return result;
      
    } catch (error) {
      const failTime = Date.now() - startTime;
      console.error(`❌ User fetch failed after ${failTime}ms:`, error.message);
      throw error;
    }
  },
  
  // Ultra-Performance Dashboard data
  getUltraDashboard: async () => {
    const cacheKey = 'ultra_dashboard';
    
    // Check cache
    if (apiCache.has(cacheKey)) {
      const cached = apiCache.get(cacheKey);
      if (Date.now() - cached.timestamp < CACHE_TTL) {
        console.log('📦 Using cached ultra dashboard data');
        return cached.data;
      }
    }
    
    // Prevent duplicate requests
    if (activeRequests.has(cacheKey)) {
      console.log('⏳ Ultra dashboard request already in progress');
      return activeRequests.get(cacheKey);
    }
    
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    const url = buildUrl('/api/ultra/dashboard');
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
  
  // Dashboard data (fallback to regular endpoint)
  getDashboard: async () => {
    // Try ultra-performance first, fallback to regular
    try {
      return await fixedAPI.getUltraDashboard();
    } catch (error) {
      console.warn('Ultra dashboard failed, falling back to regular dashboard:', error);
      
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