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
  TIMEOUT: 10000,
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
  
  // Request interceptor: Add authentication token
  client.interceptors.request.use(
    (config) => {
      const token = TokenManager.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );
  
  // Response interceptor: Handle 401 errors with token refresh
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
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
      return await apiClient.get(`${this.endpoint}${path}`, { params });
    } catch (error) {
      throw new Error(APIErrorHandler.extractErrorMessage(error));
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
   * Retrieves journal entries with filtering and pagination
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
    
    return this.get('', params);
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
  
  // Additional methods for legacy compatibility
  getTask: (taskId) => apiClient.get(`/tasks/${taskId}`),
  searchTasks: (q, limit = 20, page = 1) => apiClient.get('/tasks/search', { params: { q, limit, page } }),
  moveTaskColumn: (taskId, newColumn) => apiClient.post(`/tasks/${taskId}/move`, { column: newColumn }),
  getSubtasks: (taskId) => apiClient.get(`/tasks/${taskId}/subtasks`),
  createSubtask: (taskId, data) => apiClient.post(`/tasks/${taskId}/subtasks`, data),
  getAvailableDependencyTasks: (projectId, excludeTaskId = null) =>
    apiClient.get('/tasks/available-dependencies', { params: { project_id: projectId, exclude_task_id: excludeTaskId } }),
  getTaskDependencies: (taskId) => apiClient.get(`/tasks/${taskId}/dependencies`),
  updateTaskDependencies: (taskId, dependencyIds = []) => apiClient.post(`/tasks/${taskId}/dependencies`, { dependency_task_ids: dependencyIds }),
  suggestFocus: () => apiClient.get('/ai/suggest-focus'),
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

export const alignmentScoreAPI = {
  getDashboardData: async () => {
    try {
      return await apiClient.get('/alignment/dashboard');
    } catch (err) {
      return apiClient.get('/alignment-score');
    }
  },
  getWeeklyScore: () => apiClient.get('/alignment/weekly-score'),
  getMonthlyScore: () => apiClient.get('/alignment/monthly-score'),
  setMonthlyGoal: (goal) => apiClient.post('/alignment/monthly-goal', { goal }),
};

export const aiCoachAPI = {
  getTaskWhyStatements: (taskIds = []) => {
    const params = taskIds && taskIds.length > 0 ? { task_ids: taskIds.join(',') } : {};
    return apiClient.get('/ai/task-why-statements', { params });
  },
  suggestFocus: (topN = 3) => apiClient.get('/ai/suggest-focus', { params: { top_n: topN } }),
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

// Utility exports
export const handleApiError = APIErrorHandler.extractErrorMessage;
export const api = apiClient;
export default apiClient;