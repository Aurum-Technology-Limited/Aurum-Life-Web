/**
 * @fileoverview Centralized API Service Layer
 * 
 * Provides a unified interface for all backend API communications with automatic
 * authentication, token refresh, error handling, and request/response interceptors.
 * 
 * @version 1.0.0
 * @author Aurum Life Development Team
 */

import axios from 'axios';
import { getBackendBaseUrl } from './baseUrl';

// Configuration constants
const API_CONFIG = {
  TIMEOUT: 30000, // Increased from 10s to 30s
  ALIGNMENT_TIMEOUT: 45000, // Increased from 25s to 45s
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  TOKEN_STORAGE_KEY: 'auth_token',
  REFRESH_TOKEN_KEY: 'refresh_token',
  TOKEN_EXPIRY_KEY: 'auth_token_exp'
};

/**
 * Token management utility
 */
class TokenManager {
  /**
   * Retrieves the current authentication token
   * @returns {string|null} Authentication token or null
   */
  static getToken() {
    return localStorage.getItem(API_CONFIG.TOKEN_STORAGE_KEY) || 
           localStorage.getItem('token'); // Legacy support
  }
  
  /**
   * Retrieves the refresh token
   * @returns {string|null} Refresh token or null
   */
  static getRefreshToken() {
    return localStorage.getItem(API_CONFIG.REFRESH_TOKEN_KEY);
  }
  
  /**
   * Stores authentication tokens
   * @param {string} accessToken - Access token
   * @param {string} refreshToken - Refresh token
   * @param {number} expiresIn - Token expiry in seconds
   */
  static storeTokens(accessToken, refreshToken = null, expiresIn = null) {
    localStorage.setItem(API_CONFIG.TOKEN_STORAGE_KEY, accessToken);
    
    if (refreshToken) {
      localStorage.setItem(API_CONFIG.REFRESH_TOKEN_KEY, refreshToken);
    }
    
    if (expiresIn) {
      const expiryTime = Date.now() + (expiresIn * 1000);
      localStorage.setItem(API_CONFIG.TOKEN_EXPIRY_KEY, expiryTime.toString());
    }
  }
  
  /**
   * Clears all stored tokens
   */
  static clearTokens() {
    localStorage.removeItem(API_CONFIG.TOKEN_STORAGE_KEY);
    localStorage.removeItem(API_CONFIG.REFRESH_TOKEN_KEY);
    localStorage.removeItem(API_CONFIG.TOKEN_EXPIRY_KEY);
  }
}

/**
 * Token refresh management with concurrency control
 */
class TokenRefreshManager {
  constructor() {
    this.isRefreshing = false;
    this.refreshSubscribers = [];
  }
  
  /**
   * Adds a callback to be executed when token refresh completes
   * @param {Function} callback - Callback function
   */
  addRefreshSubscriber(callback) {
    this.refreshSubscribers.push(callback);
  }
  
  /**
   * Notifies all subscribers that token refresh is complete
   * @param {string} newToken - New access token
   */
  notifyRefreshSubscribers(newToken) {
    this.refreshSubscribers.forEach(callback => callback(newToken));
    this.refreshSubscribers = [];
  }
  
  /**
   * Attempts to refresh the authentication token
   * @returns {Promise<string|null>} New access token or null if failed
   */
  async refreshToken() {
    if (this.isRefreshing) {
      return null; // Prevent concurrent refresh attempts
    }
    
    this.isRefreshing = true;
    
    try {
      const refreshToken = TokenManager.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const baseURL = getBackendBaseUrl();
      const response = await axios.post(
        `${baseURL}/api/auth/refresh`,
        { refresh_token: refreshToken },
        { 
          headers: { 'Content-Type': 'application/json' },
          timeout: API_CONFIG.TIMEOUT
        }
      );
      
      if (response.status === 200 && response.data?.access_token) {
        const { access_token, refresh_token, expires_in } = response.data;
        
        TokenManager.storeTokens(access_token, refresh_token, expires_in);
        this.notifyRefreshSubscribers(access_token);
        
        return access_token;
      }
      
      throw new Error('Invalid refresh response');
      
    } catch (error) {
      console.error('Token refresh failed:', error);
      TokenManager.clearTokens(); // Clear invalid tokens
      return null;
    } finally {
      this.isRefreshing = false;
    }
  }
}

// Create global token refresh manager instance
const tokenRefreshManager = new TokenRefreshManager();

/**
 * API client configuration and setup
 */
function createAPIClient() {
  const baseURL = getBackendBaseUrl();
  
  const client = axios.create({
    baseURL: `${baseURL}/api`,
    timeout: API_CONFIG.TIMEOUT,
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  // Request interceptor: Add authentication token and CORS headers
  client.interceptors.request.use(
    (config) => {
      const token = TokenManager.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      // Add CORS headers
      config.headers['Content-Type'] = 'application/json';
      config.headers['Accept'] = 'application/json';
      
      // Add Supabase apikey header for Edge Functions
      const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;
      if (supabaseAnonKey) {
        config.headers['apikey'] = supabaseAnonKey;
      }
      
      return config;
    },
    (error) => {
      console.error('Request interceptor error:', error);
      return Promise.reject(error);
    }
  );
  
  // Response interceptor: Handle errors including CORS and network issues
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      // Handle CORS errors
      if (error.code === 'ERR_NETWORK' || error.message?.includes('CORS')) {
        console.warn('CORS or network error detected:', error.message);
        // Return a mock response for development
        if (process.env.NODE_ENV === 'development') {
          return {
            data: { error: 'CORS error - API not accessible', mock: true },
            status: 200
          };
        }
      }
      
      // Handle 406 errors
      if (error.response?.status === 406) {
        console.warn('406 Not Acceptable error:', error.response.data);
        return {
          data: { error: 'API endpoint not available', status: 406 },
          status: 406
        };
      }
      const originalRequest = error.config;
      
      // Handle 401 Unauthorized errors with token refresh
      if (
        error.response?.status === 401 && 
        !originalRequest._retry &&
        TokenManager.getRefreshToken()
      ) {
        originalRequest._retry = true;
        
        const newToken = await tokenRefreshManager.refreshToken();
        if (newToken) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return client(originalRequest);
        }
      }
      
      return Promise.reject(error);
    }
  );
  
  return client;
}

// Create the main API client
const apiClient = createAPIClient();

/**
 * Error handling utilities
 */
class APIErrorHandler {
  /**
   * Extracts user-friendly error message from API error
   * @param {Error} error - API error object
   * @param {string} defaultMessage - Default error message
   * @returns {string} User-friendly error message
   */
  static extractErrorMessage(error, defaultMessage = 'An error occurred') {
    if (error?.response) {
      return error.response.data?.message || 
             error.response.data?.detail || 
             `Server error: ${error.response.status}`;
    } else if (error?.request) {
      return 'Network error - please check your connection';
    } else {
      return error?.message || defaultMessage;
    }
  }
  
  /**
   * Determines if an error is retryable
   * @param {Error} error - API error object
   * @returns {boolean} True if error is retryable
   */
  static isRetryableError(error) {
    if (error?.response) {
      const status = error.response.status;
      // Retry on server errors (5xx) and some client errors
      return status >= 500 || status === 408 || status === 429;
    }
    // Retry on network errors
    return error?.code === 'ECONNABORTED' || error?.code === 'ENOTFOUND';
  }
}

/**
 * Base API service class with common functionality
 */
class BaseAPIService {
  constructor(endpoint) {
    this.endpoint = endpoint;
  }
  
  /**
   * Generic GET request with error handling
   * @param {string} path - API path
   * @param {Object} params - Query parameters
   * @returns {Promise} API response
   */
  async get(path = '', params = {}) {
    try {
      const fullPath = `${this.endpoint}${path}`;
      console.log(`🌐 API Request: GET ${fullPath}`, { params });
      
      const response = await apiClient.get(fullPath, { params });
      console.log(`✅ API Response: GET ${fullPath}`, { 
        status: response.status, 
        dataType: typeof response.data,
        dataLength: Array.isArray(response.data) ? response.data.length : 'not-array'
      });
      
      return response;
    } catch (error) {
      console.error(`❌ API Error: GET ${this.endpoint}${path}`, {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        request: !!error.request,
        code: error.code
      });
      throw new Error(APIErrorHandler.extractErrorMessage(error));
    }
  }
  
  /**
   * GET request with retry logic for critical endpoints
   * @param {string} path - API path
   * @param {Object} params - Query parameters  
   * @param {number} maxRetries - Maximum retry attempts
   * @returns {Promise} API response
   */
  async getWithRetry(path = '', params = {}, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await this.get(path, params);
      } catch (error) {
        if (attempt === maxRetries) {
          throw error;
        }
        
        // Check if error is retryable
        if (APIErrorHandler.isRetryableError(error)) {
          const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, attempt - 1);
          console.log(`⏳ Retrying API request in ${delay}ms (attempt ${attempt + 1}/${maxRetries})`);
          await new Promise(resolve => setTimeout(resolve, delay));
        } else {
          throw error; // Don't retry non-retryable errors
        }
      }
    }
  }
  
  /**
   * Generic POST request with error handling
   * @param {string} path - API path
   * @param {Object} data - Request body data
   * @returns {Promise} API response
   */
  async post(path = '', data = {}) {
    try {
      return await apiClient.post(`${this.endpoint}${path}`, data);
    } catch (error) {
      throw new Error(APIErrorHandler.extractErrorMessage(error));
    }
  }
  
  /**
   * Generic PUT request with error handling
   * @param {string} path - API path
   * @param {Object} data - Request body data
   * @returns {Promise} API response
   */
  async put(path = '', data = {}) {
    try {
      return await apiClient.put(`${this.endpoint}${path}`, data);
    } catch (error) {
      throw new Error(APIErrorHandler.extractErrorMessage(error));
    }
  }
  
  /**
   * Generic DELETE request with error handling
   * @param {string} path - API path
   * @returns {Promise} API response
   */
  async delete(path = '') {
    try {
      return await apiClient.delete(`${this.endpoint}${path}`);
    } catch (error) {
      throw new Error(APIErrorHandler.extractErrorMessage(error));
    }
  }
}

/**
 * Journal API Service
 */
class JournalAPIService extends BaseAPIService {
  constructor() {
    super('/journal');
  }
  
  /**
   * Retrieves journal entries with retry logic
   * @param {Object} options - Query options
   * @returns {Promise} Journal entries
   */
  async getEntries({
    skip = 0,
    limit = 20,
    moodFilter = null,
    tagFilter = null,
    dateFrom = null,
    dateTo = null
  } = {}) {
    const params = { skip, limit };
    if (moodFilter) params.mood_filter = moodFilter;
    if (tagFilter) params.tag_filter = tagFilter;
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    
    // Retry logic for journal entries
    return this.getWithRetry('', params, 3);
  }
  
  /**
   * Retrieves journal templates with retry logic
   * @returns {Promise} Journal templates
   */
  async getTemplates() {
    return this.getWithRetry('/templates', {}, 3);
  }
  
  /**
   * GET request with retry logic
   * @param {string} path - API path
   * @param {Object} params - Query parameters
   * @param {number} retries - Number of retry attempts
   * @returns {Promise} API response
   */
  async getWithRetry(path = '', params = {}, retries = 3) {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        console.log(`🔄 Journal API attempt ${attempt}/${retries}: GET ${this.endpoint}${path}`);
        
        const response = await this.get(path, params);
        console.log(`✅ Journal API success on attempt ${attempt}`);
        return response;
        
      } catch (error) {
        console.warn(`❌ Journal API attempt ${attempt} failed:`, error.message);
        
        if (attempt === retries) {
          console.error(`🚫 Journal API failed after ${retries} attempts`);
          throw error;
        }
        
        // Wait before retrying (exponential backoff)
        const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, attempt - 1);
        console.log(`⏳ Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  /**
   * Creates a new journal entry
   * @param {Object} entryData - Entry data
   * @returns {Promise} Created entry
   */
  async createEntry(entryData) {
    return this.post('', entryData);
  }
  
  /**
   * Updates an existing journal entry
   * @param {string} entryId - Entry ID
   * @param {Object} entryData - Updated entry data
   * @returns {Promise} Updated entry
   */
  async updateEntry(entryId, entryData) {
    return this.put(`/${entryId}`, entryData);
  }
  
  /**
   * Soft deletes a journal entry
   * @param {string} entryId - Entry ID
   * @returns {Promise} Delete confirmation
   */
  async deleteEntry(entryId) {
    return this.delete(`/${entryId}`);
  }
  
  /**
   * Restores a soft-deleted journal entry
   * @param {string} entryId - Entry ID
   * @returns {Promise} Restore confirmation
   */
  async restoreEntry(entryId) {
    return this.post(`/${entryId}/restore`);
  }
  
  /**
   * Retrieves soft-deleted entries (trash)
   * @param {Object} options - Pagination options
   * @returns {Promise} Trash entries
   */
  async getTrash({ skip = 0, limit = 20 } = {}) {
    return this.get('/trash', { skip, limit });
  }
  
  /**
   * Permanently deletes a journal entry
   * @param {string} entryId - Entry ID
   * @returns {Promise} Purge confirmation
   */
  async purgeEntry(entryId) {
    return this.delete(`/${entryId}/purge`);
  }

  /**
   * Retrieves journal templates
   * @returns {Promise} Journal templates
   */
  async getTemplates() {
    return this.get('/templates');
  }

  /**
   * Creates a new journal template
   * @param {Object} templateData - Template data
   * @returns {Promise} Created template
   */
  async createTemplate(templateData) {
    return this.post('/templates', templateData);
  }

  /**
   * Updates a journal template
   * @param {string} templateId - Template ID
   * @param {Object} templateData - Updated template data
   * @returns {Promise} Updated template
   */
  async updateTemplate(templateId, templateData) {
    return this.put(`/templates/${templateId}`, templateData);
  }

  /**
   * Deletes a journal template
   * @param {string} templateId - Template ID
   * @returns {Promise} Delete confirmation
   */
  async deleteTemplate(templateId) {
    return this.delete(`/templates/${templateId}`);
  }
}

/**
 * Tasks API Service
 */
class TasksAPIService extends BaseAPIService {
  constructor() {
    super('/tasks');
  }
  
  /**
   * Retrieves tasks with advanced filtering and pagination
   * @param {Object|string} options - Query options or project ID
   * @returns {Promise} Tasks data
   */
  async getTasks(options = {}) {
    const params = {};
    
    // Handle legacy string parameter (project ID)
    if (typeof options === 'string') {
      if (options) params.project_id = options;
    } else if (options && typeof options === 'object') {
      const {
        projectId,
        q,
        status,
        priority,
        dueDate,
        page,
        limit,
        returnMeta = false
      } = options;
      
      if (projectId) params.project_id = projectId;
      if (q) params.q = q;
      if (status) params.status = status;
      if (priority) params.priority = priority;
      if (dueDate) params.due_date = dueDate;
      if (page) params.page = page;
      if (limit) params.limit = limit;
      if (returnMeta) params.return_meta = true;
    }
    
    return this.get('', params);
  }
  
  /**
   * Creates a new task
   * @param {Object} taskData - Task data
   * @returns {Promise} Created task
   */
  async createTask(taskData) {
    return this.post('', taskData);
  }
  
  /**
   * Updates an existing task
   * @param {string} taskId - Task ID
   * @param {Object} taskData - Updated task data
   * @returns {Promise} Updated task
   */
  async updateTask(taskId, taskData) {
    return this.put(`/${taskId}`, taskData);
  }
  
  /**
   * Deletes a task
   * @param {string} taskId - Task ID
   * @returns {Promise} Delete confirmation
   */
  async deleteTask(taskId) {
    return this.delete(`/${taskId}`);
  }
  
  /**
   * Gets a specific task
   * @param {string} taskId - Task ID
   * @returns {Promise} Task data
   */
  async getTask(taskId) {
    return this.get(`/${taskId}`);
  }
  
  /**
   * Searches tasks
   * @param {string} q - Search query
   * @param {number} limit - Result limit
   * @param {number} page - Page number
   * @param {boolean} useHRM - Use HRM for enhanced results
   * @returns {Promise} Search results
   */
  async searchTasks(q, limit = 20, page = 1, useHRM = true) {
    return this.get('/search', { q, limit, page, use_hrm: useHRM });
  }

  /**
   * Get AI-enhanced task suggestions for focus
   * @param {number} topN - Number of suggestions
   * @param {boolean} useHRM - Use HRM for enhanced suggestions
   * @returns {Promise} Task suggestions
   */
  async suggestFocus(topN = 3, useHRM = true) {
    return this.get('/suggest-focus', { top_n: topN, use_hrm: useHRM });
  }
}

// Create service instances
export const journalAPI = new JournalAPIService();
export const tasksAPI = new TasksAPIService();

// Legacy API objects for backward compatibility
export const pillarsAPI = {
  getPillars: (includeSubPillars = true, includeAreas = false, includeArchived = false) =>
    apiClient.get('/pillars', {
      params: {
        include_sub_pillars: includeSubPillars,
        include_areas: includeAreas,
        include_archived: includeArchived,
      },
    }),
  getPillar: (id) => apiClient.get(`/pillars/${id}`),
  createPillar: (data) => apiClient.post('/pillars', data),
  updatePillar: (id, data) => apiClient.put(`/pillars/${id}`, data),
  deletePillar: (id) => apiClient.delete(`/pillars/${id}`),
};

export const areasAPI = {
  getAreas: (includeProjects = true, includeArchived = false) =>
    apiClient.get('/areas', {
      params: { include_projects: includeProjects, include_archived: includeArchived },
    }),
  getArea: (id) => apiClient.get(`/areas/${id}`),
  createArea: (data) => apiClient.post('/areas', data),
  updateArea: (id, data) => apiClient.put(`/areas/${id}`, data),
  deleteArea: (id) => apiClient.delete(`/areas/${id}`),
  archiveArea: (id, archived) => apiClient.post(`/areas/${id}/archive`, { archived }),
};

export const projectsAPI = {
  getProjects: (areaId = null, includeArchived = false) =>
    apiClient.get('/projects', {
      params: { ...(areaId ? { area_id: areaId } : {}), include_archived: includeArchived },
    }),
  getProject: (id) => apiClient.get(`/projects/${id}`),
  createProject: (data) => apiClient.post('/projects', data),
  updateProject: (id, data) => apiClient.put(`/projects/${id}`, data),
  deleteProject: (id) => apiClient.delete(`/projects/${id}`),
};

export const projectTemplatesAPI = {
  getTemplates: () => apiClient.get('/project-templates'),
  getTemplate: (id) => apiClient.get(`/project-templates/${id}`),
  createTemplate: (data) => apiClient.post('/project-templates', data),
  updateTemplate: (id, data) => apiClient.put(`/project-templates/${id}`, data),
  deleteTemplate: (id) => apiClient.delete(`/project-templates/${id}`),
  useTemplate: (templateId, projectData) => apiClient.post(`/project-templates/${templateId}/use`, projectData),
};

export const alignmentScoreAPI = {
  getDashboardData: async (useHRM = true) => {
    try {
      const params = useHRM ? { use_hrm: true } : {};
      return await apiClient.get('/alignment/dashboard', { 
        params,
        timeout: API_CONFIG.ALIGNMENT_TIMEOUT 
      });
    } catch (error) {
      console.warn('Primary alignment endpoint failed, trying fallback:', error.message);
      try {
        return await apiClient.get('/alignment-score', { 
          params: useHRM ? { use_hrm: true } : {},
          timeout: API_CONFIG.ALIGNMENT_TIMEOUT 
        });
      } catch (fallbackError) {
        console.error('Both alignment endpoints failed:', fallbackError.message);
        throw fallbackError;
      }
    }
  },
  getWeeklyScore: async (useHRM = true) => {
    try {
      return await apiClient.get('/alignment/weekly-score', { 
        params: useHRM ? { use_hrm: true } : {},
        timeout: API_CONFIG.ALIGNMENT_TIMEOUT 
      });
    } catch (error) {
      console.error('Weekly alignment score failed:', error.message);
      throw error;
    }
  },
  getMonthlyScore: async (useHRM = true) => {
    try {
      return await apiClient.get('/alignment/monthly-score', { 
        params: useHRM ? { use_hrm: true } : {},
        timeout: API_CONFIG.ALIGNMENT_TIMEOUT 
      });
    } catch (error) {
      console.error('Monthly alignment score failed:', error.message);
      throw error;
    }
  },
  setMonthlyGoal: async (goal) => {
    try {
      return await apiClient.post('/alignment/monthly-goal', { goal });
    } catch (error) {
      console.error('Set monthly goal failed:', error.message);
      throw error;
    }
  },
};

export const aiCoachAPI = {
  getTaskWhyStatements: async (taskIds = [], useHRM = true) => {
    try {
      const params = { use_hrm: useHRM };
      if (taskIds && taskIds.length > 0) {
        params.task_ids = taskIds.join(',');
      }
      return await apiClient.get('/ai/task-why-statements', { params });
    } catch (error) {
      console.warn('AI task-why-statements API not available:', error.message);
      // Return mock data for development
      return {
        data: {
          statements: [
            { task_id: taskIds[0] || '1', why_statement: 'This task aligns with your long-term goals and contributes to your overall success.' },
            { task_id: taskIds[1] || '2', why_statement: 'Completing this task will help you make progress on important projects.' }
          ]
        }
      };
    }
  },
  suggestFocus: async (topN = 3, useHRM = true) => {
    try {
      return await apiClient.get('/ai/suggest-focus', { params: { top_n: topN, use_hrm: useHRM } });
    } catch (error) {
      console.warn('AI suggest-focus API not available:', error.message);
      // Return mock data for development
      return {
        data: {
          suggestions: [
            { task: 'Review and update project priorities', priority: 'high', reason: 'Aligns with strategic goals' },
            { task: 'Complete daily reflection', priority: 'medium', reason: 'Supports personal growth' }
          ]
        }
      };
    }
  },
  getTodayPriorities: async (useHRM = true, topN = 5) => {
    try {
      return await apiClient.get('/ai/today-priorities', { params: { use_hrm: useHRM, top_n: topN } });
    } catch (error) {
      console.warn('AI today-priorities API not available:', error.message);
      // Return mock data for development
      return {
        data: {
          priorities: [
            { task: 'Focus on high-impact work', priority: 1, reasoning: 'Maximizes daily productivity' },
            { task: 'Review strategic alignment', priority: 2, reasoning: 'Ensures goal consistency' }
          ]
        }
      };
    }
  },
  decomposeProject: (projectName, projectDescription = '', templateType = 'general') =>
    apiClient.post('/ai/decompose-project', {
      project_name: projectName,
      project_description: projectDescription,
      template_type: templateType,
    }),
  createTasksFromSuggestions: (projectId, suggestedTasks = []) =>
    apiClient.post('/ai/create-tasks-from-suggestions', { project_id: projectId, suggested_tasks: suggestedTasks }),
  getQuota: () => apiClient.get('/ai/quota'),
};

// Additional APIs for Insights and other components
export const insightsAPI = {
  getInsights: (dateRange = 'all_time', areaId = null) =>
    apiClient.get('/insights', { params: { date_range: dateRange, ...(areaId ? { area_id: areaId } : {}) } }),
};

export const insightsDrilldownAPI = {
  // Placeholder for drilldown functionality - implement as needed
  getDrilldownData: (params = {}) => apiClient.get('/insights/drilldown', { params }),
};

export const todayAPI = {
  // Placeholder for Today functionality - implement as needed  
  addTaskToToday: (taskId) => apiClient.post(`/today/tasks/${taskId}`),
  removeTaskFromToday: (taskId) => apiClient.delete(`/today/tasks/${taskId}`),
  getTodayTasks: () => apiClient.get('/today/tasks'),
};

export const dashboardAPI = {
  getDashboard: () => apiClient.get('/dashboard'),
};

export const recurringTasksAPI = {
  getRecurringTasks: () => apiClient.get('/tasks/recurring'),
  createRecurringTask: (data) => apiClient.post('/tasks/recurring', data),
  updateRecurringTask: (id, data) => apiClient.put(`/tasks/recurring/${id}`, data),
  deleteRecurringTask: (id) => apiClient.delete(`/tasks/recurring/${id}`),
  generateRecurringTaskInstances: () => apiClient.post('/tasks/recurring/generate'),
};

export const uploadsAPI = {
  initiate: ({ filename, size, parentType = null, parentId = null }) =>
    apiClient.post('/uploads/initiate', { filename, size, parent_type: parentType, parent_id: parentId }),
  uploadChunk: ({ uploadId, index, total, blob }) => {
    const form = new FormData();
    form.append('upload_id', uploadId);
    form.append('index', String(index));
    form.append('total_chunks', String(total));
    form.append('chunk', blob, `chunk_${index}`);
    return apiClient.post('/uploads/chunk', form, { headers: { 'Content-Type': 'multipart/form-data' } });
  },
  complete: ({ uploadId }) => {
    const form = new FormData();
    form.append('upload_id', uploadId);
    return apiClient.post('/uploads/complete', form);
  },
};

export const notificationsAPI = {
  getNotifications: (params = {}) => apiClient.get('/notifications', { params }),
  markAsRead: (notificationId) => apiClient.put(`/notifications/${notificationId}/read`),
  markAllAsRead: () => apiClient.put('/notifications/mark-all-read'),
  getSettings: () => apiClient.get('/notifications/settings'),
  updateSettings: (settings) => apiClient.put('/notifications/settings', settings),
  testNotification: (type) => apiClient.post('/notifications/test', { type }),
};

// Import HRM API
import { hrmAPI } from './hrmApi';

// Re-export HRM API
export { hrmAPI };

// Analytics API Service
export const analyticsAPI = {
  /**
   * Get analytics dashboard data
   * @param {number} days - Number of days to fetch data for (default: 30)
   * @returns {Promise} Dashboard data
   */
  getDashboard: async (days = 30) => {
    try {
      const response = await apiClient.get(`/analytics/dashboard?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Analytics dashboard fetch failed:', error);
      throw error;
    }
  },

  /**
   * Get user analytics preferences
   * @returns {Promise} User preferences
   */
  getPreferences: async () => {
    try {
      const response = await apiClient.get('/analytics/preferences');
      return response.data;
    } catch (error) {
      console.error('Analytics preferences fetch failed:', error);
      throw error;
    }
  },

  /**
   * Update user analytics preferences
   * @param {Object} data - Preferences data
   * @returns {Promise} Updated preferences
   */
  updatePreferences: async (data) => {
    try {
      const response = await apiClient.put('/analytics/preferences', data);
      return response.data;
    } catch (error) {
      console.error('Analytics preferences update failed:', error);
      throw error;
    }
  },

  /**
   * Track an analytics event
   * @param {Object} event - Event data
   * @returns {Promise} Tracking result
   */
  trackEvent: async (event) => {
    try {
      const response = await apiClient.post('/analytics/track-event', event);
      return response.data;
    } catch (error) {
      console.error('Analytics event tracking failed:', error);
      throw error;
    }
  },

  /**
   * Start an analytics session
   * @param {Object} session - Session data
   * @returns {Promise} Session result
   */
  startSession: async (session) => {
    try {
      const response = await apiClient.post('/analytics/start-session', session);
      return response.data;
    } catch (error) {
      console.error('Analytics session start failed:', error);
      throw error;
    }
  },

  /**
   * End an analytics session
   * @param {string} sessionId - Session ID
   * @param {string} exitPage - Exit page URL
   * @returns {Promise} Session end result
   */
  endSession: async (sessionId, exitPage) => {
    try {
      const response = await apiClient.post(`/analytics/end-session/${sessionId}?exit_page=${encodeURIComponent(exitPage)}`);
      return response.data;
    } catch (error) {
      console.error('Analytics session end failed:', error);
      throw error;
    }
  },

  /**
   * Get AI features usage data
   * @param {number} days - Number of days to fetch data for (default: 30)
   * @returns {Promise} AI features data
   */
  getAIFeatures: async (days = 30) => {
    try {
      const response = await apiClient.get(`/analytics/ai-features?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Analytics AI features fetch failed:', error);
      throw error;
    }
  },

  /**
   * Get engagement metrics
   * @param {number} days - Number of days to fetch data for (default: 30)
   * @returns {Promise} Engagement data
   */
  getEngagement: async (days = 30) => {
    try {
      const response = await apiClient.get(`/analytics/engagement?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Analytics engagement fetch failed:', error);
      throw error;
    }
  }
};

// Sentiment Analysis API
export const sentimentAPI = {
  /**
   * Analyze sentiment for arbitrary text (real-time analysis)
   * @param {string} text - Text to analyze
   * @returns {Promise} Sentiment analysis result
   */
  analyzeText: async (text) => {
    try {
      const response = await apiClient.post('/sentiment/analyze-text', { text });
      return response.data;
    } catch (error) {
      console.error('Text sentiment analysis failed:', error);
      throw error;
    }
  },

  /**
   * Get sentiment trends over time
   * @param {number} days - Number of days to analyze (default: 30)
   * @returns {Promise} Sentiment trends data
   */
  getTrends: async (days = 30) => {
    try {
      const response = await apiClient.get(`/sentiment/trends?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Sentiment trends fetch failed:', error);
      throw error;
    }
  },

  /**
   * Get emotional wellness score
   * @param {number} days - Number of days for calculation (default: 30)
   * @returns {Promise} Wellness score data
   */
  getWellnessScore: async (days = 30) => {
    try {
      const response = await apiClient.get(`/sentiment/wellness-score?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Wellness score fetch failed:', error);
      throw error;
    }
  },

  /**
   * Get activity-sentiment correlations
   * @param {number} days - Number of days to analyze (default: 30)
   * @returns {Promise} Correlation data
   */
  getCorrelations: async (days = 30) => {
    try {
      const response = await apiClient.get(`/sentiment/correlations?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Activity correlations fetch failed:', error);
      throw error;
    }
  },

  /**
   * Bulk analyze existing journal entries
   * @param {number} limit - Maximum entries to analyze (default: 50)
   * @returns {Promise} Bulk analysis result
   */
  bulkAnalyze: async (limit = 50) => {
    try {
      const response = await apiClient.post(`/sentiment/bulk-analyze?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Bulk sentiment analysis failed:', error);
      throw error;
    }
  },

  /**
   * Get emotional insights
   * @param {number} days - Number of days for insights (default: 30)
   * @returns {Promise} Emotional insights data
   */
  getInsights: async (days = 30) => {
    try {
      const response = await apiClient.get(`/sentiment/insights?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Emotional insights fetch failed:', error);
      throw error;
    }
  }
};

// Semantic Search API
export const semanticSearchAPI = {
  /**
   * Perform semantic search across user's content
   * @param {string} query - Search query text
   * @param {Array} contentTypes - Content types to search (default: ['all'])
   * @param {number} limit - Maximum results (default: 10)
   * @param {number} minSimilarity - Minimum similarity threshold (default: 0.3)
   * @param {number} dateRangeDays - Limit to recent days (optional)
   */
  async search(query, contentTypes = ['all'], limit = 10, minSimilarity = 0.3, dateRangeDays = null) {
    try {
      const params = new URLSearchParams({
        query,
        limit: limit.toString(),
        min_similarity: minSimilarity.toString()
      });
      
      // Add content types
      contentTypes.forEach(type => params.append('content_types', type));
      
      // Add date range if specified
      if (dateRangeDays) {
        params.append('date_range_days', dateRangeDays.toString());
      }
      
      const response = await apiClient.get(`/semantic/search?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Semantic search failed:', error);
      throw error;
    }
  },

  /**
   * Find content similar to a specific entity
   * @param {string} entityType - Type of entity (task, project, journal_entry)
   * @param {string} entityId - ID of the entity
   * @param {number} limit - Maximum results (default: 5)
   * @param {number} minSimilarity - Minimum similarity threshold (default: 0.4)
   */
  async findSimilar(entityType, entityId, limit = 5, minSimilarity = 0.4) {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        min_similarity: minSimilarity.toString()
      });
      
      const response = await apiClient.get(`/semantic/similar/${entityType}/${entityId}?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Find similar content failed:', error);
      throw error;
    }
  },

  /**
   * Search for content similar to a text query with specific content type
   * @param {string} query - Search query
   * @param {string} contentType - Specific content type to search
   * @param {number} limit - Maximum results
   */
  async searchByType(query, contentType, limit = 10) {
    return this.search(query, [contentType], limit);
  },

  /**
   * Find similar journal entries
   * @param {string} query - Search query
   * @param {number} limit - Maximum results
   */
  async searchJournalEntries(query, limit = 10) {
    return this.searchByType(query, 'journal_entry', limit);
  },

  /**
   * Find similar tasks
   * @param {string} query - Search query
   * @param {number} limit - Maximum results
   */
  async searchTasks(query, limit = 10) {
    return this.searchByType(query, 'task', limit);
  },

  /**
   * Find similar projects
   * @param {string} query - Search query
   * @param {number} limit - Maximum results
   */
  async searchProjects(query, limit = 10) {
    return this.searchByType(query, 'project', limit);
  }
};

// Utility exports
export const handleApiError = APIErrorHandler.extractErrorMessage;
export const api = apiClient;
export default apiClient;