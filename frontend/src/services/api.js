import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Default user ID for demo
const DEFAULT_USER_ID = 'demo-user-123';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for common parameters and authentication
apiClient.interceptors.request.use((config) => {
  // Add authentication token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Add user_id to query params for endpoints that need it (legacy support)
  if (!config.params) {
    config.params = {};
  }
  
  // Only add user_id for legacy endpoints that don't use authentication
  const legacyEndpoints = ['/dashboard', '/habits', '/journal', '/areas', '/projects', '/tasks', '/today', '/users', '/stats', '/chat', '/courses'];
  const isLegacyEndpoint = legacyEndpoints.some(endpoint => config.url.includes(endpoint) && !config.url.includes('/insights'));
  
  if (isLegacyEndpoint && !config.params.user_id) {
    config.params.user_id = DEFAULT_USER_ID;
  }
  
  return config;
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Areas API
export const areasAPI = {
  getAreas: (includeProjects = false) => apiClient.get('/areas', { params: { include_projects: includeProjects } }),
  getArea: (areaId) => apiClient.get(`/areas/${areaId}`),
  createArea: (areaData) => apiClient.post('/areas', areaData),
  updateArea: (areaId, areaData) => apiClient.put(`/areas/${areaId}`, areaData),
  deleteArea: (areaId) => apiClient.delete(`/areas/${areaId}`),
};

// Projects API
export const projectsAPI = {
  getProjects: (areaId = null) => apiClient.get('/projects', { params: areaId ? { area_id: areaId } : {} }),
  getProject: (projectId, includeTasks = false) => apiClient.get(`/projects/${projectId}`, { params: { include_tasks: includeTasks } }),
  createProject: (projectData) => apiClient.post('/projects', projectData),
  updateProject: (projectId, projectData) => apiClient.put(`/projects/${projectId}`, projectData),
  deleteProject: (projectId) => apiClient.delete(`/projects/${projectId}`),
  getProjectTasks: (projectId) => apiClient.get(`/projects/${projectId}/tasks`),
  getKanbanBoard: (projectId) => apiClient.get(`/projects/${projectId}/kanban`),
};

// Enhanced Tasks API
export const tasksAPI = {
  getTasks: (projectId = null) => apiClient.get('/tasks', { params: projectId ? { project_id: projectId } : {} }),
  createTask: (taskData) => apiClient.post('/tasks', taskData),
  updateTask: (taskId, taskData) => apiClient.put(`/tasks/${taskId}`, taskData),
  deleteTask: (taskId) => apiClient.delete(`/tasks/${taskId}`),
  moveTaskColumn: (taskId, newColumn) => apiClient.put(`/tasks/${taskId}/column`, null, { params: { new_column: newColumn } }),
};

// Today View API
export const todayAPI = {
  getTodayView: () => apiClient.get('/today'),
};

// Insights API
export const insightsAPI = {
  getInsights: (dateRange = 'all_time', areaId = null) => {
    let url = `/insights?date_range=${dateRange}`;
    if (areaId) {
      url += `&area_id=${areaId}`;
    }
    return apiClient.get(url);
  },
  getAreaDrillDown: (areaId, dateRange = 'all_time') => apiClient.get(`/insights/areas/${areaId}?date_range=${dateRange}`),
  getProjectDrillDown: (projectId, dateRange = 'all_time') => apiClient.get(`/insights/projects/${projectId}?date_range=${dateRange}`),
};

// Dashboard API (updated)
export const dashboardAPI = {
  getDashboard: () => apiClient.get('/dashboard'),
};

// User API
export const userAPI = {
  getUser: (userId = DEFAULT_USER_ID) => apiClient.get(`/users/${userId}`),
  updateUser: (userData, userId = DEFAULT_USER_ID) => apiClient.put(`/users/${userId}`, userData),
  createUser: (userData) => apiClient.post('/users', userData),
};

// Habits API
export const habitsAPI = {
  getHabits: () => apiClient.get('/habits'),
  createHabit: (habitData) => apiClient.post('/habits', habitData),
  updateHabit: (habitId, habitData) => apiClient.put(`/habits/${habitId}`, habitData),
  toggleHabit: (habitId, completed) => apiClient.post(`/habits/${habitId}/toggle`, { habit_id: habitId, completed }),
  deleteHabit: (habitId) => apiClient.delete(`/habits/${habitId}`),
};

// Journal API
export const journalAPI = {
  getEntries: (skip = 0, limit = 20) => apiClient.get('/journal', { params: { skip, limit } }),
  createEntry: (entryData) => apiClient.post('/journal', entryData),
  updateEntry: (entryId, entryData) => apiClient.put(`/journal/${entryId}`, entryData),
  deleteEntry: (entryId) => apiClient.delete(`/journal/${entryId}`),
};

// Chat API
export const chatAPI = {
  sendMessage: (messageData) => apiClient.post('/chat', messageData),
  getMessages: (sessionId) => apiClient.get(`/chat/${sessionId}`),
};

// Courses API
export const coursesAPI = {
  getAllCourses: () => apiClient.get('/courses'),
  getEnrolledCourses: () => apiClient.get('/courses/enrolled'),
  enrollInCourse: (courseId) => apiClient.post(`/courses/${courseId}/enroll`),
};

// Stats API
export const statsAPI = {
  getUserStats: () => apiClient.get('/stats'),
  updateUserStats: () => apiClient.post('/stats/update'),
};

// Health check
export const healthAPI = {
  check: () => apiClient.get('/health'),
  root: () => apiClient.get('/'),
};

// Utility functions
export const handleApiError = (error, defaultMessage = 'An error occurred') => {
  const message = error.response?.data?.detail || error.message || defaultMessage;
  console.error('API Error:', message);
  return message;
};

export const isApiError = (error) => {
  return error.response && error.response.status;
};

export const getApiErrorStatus = (error) => {
  return error.response?.status;
};