import axios from 'axios';

// Central API client (axios)
const apiClient = axios.create({
  baseURL: (process.env.REACT_APP_BACKEND_URL || '') + '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Attach auth token automatically
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

let isRefreshing = false;
let refreshSubscribers = [];
const onRefreshed = (newToken) => {
  refreshSubscribers.forEach((cb) => cb(newToken));
  refreshSubscribers = [];
};
const addRefreshSubscriber = (cb) => {
  refreshSubscribers.push(cb);
};

async function refreshToken() {
  if (isRefreshing) return null;
  isRefreshing = true;
  try {
    const rt = localStorage.getItem('refresh_token');
    if (!rt) throw new Error('No refresh token');
    const base = (process.env.REACT_APP_BACKEND_URL || '') + '/api';
    const resp = await axios.post(base + '/auth/refresh', { refresh_token: rt }, { headers: { 'Content-Type': 'application/json' } });
    if (resp.status === 200 && resp.data?.access_token) {
      localStorage.setItem('auth_token', resp.data.access_token);
      if (resp.data.refresh_token) localStorage.setItem('refresh_token', resp.data.refresh_token);
      // store expiry timestamp if provided
      if (resp.data.expires_in) {
        const expAt = Date.now() + resp.data.expires_in * 1000;
        localStorage.setItem('auth_token_exp', String(expAt));
      }
      return resp.data.access_token;
    }
    throw new Error('Refresh failed');
  } finally {
    isRefreshing = false;
  }
}

// Response interceptor: attempt refresh on 401 once
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const newToken = await refreshToken();
        if (newToken) {
          onRefreshed(newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        }
      } catch (e) {
        // fallthrough
      }
    }
    return Promise.reject(error);
  }
);

// -------------- Journal API --------------
export const journalAPI = {
  getEntries: (skip = 0, limit = 20, moodFilter = null, tagFilter = null, dateFrom = null, dateTo = null) => {
    const params = { skip, limit };
    if (moodFilter) params.mood_filter = moodFilter;
    if (tagFilter) params.tag_filter = tagFilter;
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    return apiClient.get('/journal', { params });
  },
  createEntry: (entryData) => apiClient.post('/journal', entryData),
  updateEntry: (entryId, entryData) => apiClient.put(`/journal/${entryId}`, entryData),
  deleteEntry: (entryId) => apiClient.delete(`/journal/${entryId}`),
  restoreEntry: (entryId) => apiClient.post(`/journal/${entryId}/restore`),
  getTrash: (skip = 0, limit = 20) => apiClient.get('/journal/trash', { params: { skip, limit } }),
  purgeEntry: (entryId) => apiClient.delete(`/journal/${entryId}/purge`),
  searchEntries: (query, limit = 20) => apiClient.get('/journal/search', { params: { q: query, limit } }),
  getInsights: () => apiClient.get('/journal/insights'),
  getOnThisDay: (date = null) => apiClient.get('/journal/on-this-day', { params: date ? { date } : {} }),
  getTemplates: () => apiClient.get('/journal/templates'),
  getTemplate: (templateId) => apiClient.get(`/journal/templates/${templateId}`),
  createTemplate: (templateData) => apiClient.post('/journal/templates', templateData),
  updateTemplate: (templateId, templateData) => apiClient.put(`/journal/templates/${templateId}`, templateData),
  deleteTemplate: (templateId) => apiClient.delete(`/journal/templates/${templateId}`),
};

// -------------- Pillars / Areas / Projects / Tasks --------------
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

export const tasksAPI = {
  getTasks: (arg = {}) => {
    const params = {};
    if (typeof arg === 'string') {
      if (arg) params.project_id = arg;
    } else if (arg && typeof arg === 'object') {
      const {
        projectId = null,
        q = null,
        status = null,
        priority = null,
        dueDate = null,
        page = null,
        limit = null,
        returnMeta = false,
      } = arg;
      if (projectId) params.project_id = projectId;
      if (q) params.q = q;
      if (status) params.status = status;
      if (priority) params.priority = priority;
      if (dueDate) params.due_date = dueDate;
      if (page) params.page = page;
      if (limit) params.limit = limit;
      if (returnMeta) params.return_meta = true;
    }
    return apiClient.get('/tasks', { params });
  },
  getTask: (taskId) => apiClient.get(`/tasks/${taskId}`),
  createTask: (data) => apiClient.post('/tasks', data),
  updateTask: (taskId, data) => apiClient.put(`/tasks/${taskId}`, data),
  deleteTask: (taskId) => apiClient.delete(`/tasks/${taskId}`),
  searchTasks: (q, limit = 20, page = 1) => apiClient.get('/tasks/search', { params: { q, limit, page } }),
  moveTaskColumn: (taskId, newColumn) => apiClient.post(`/tasks/${taskId}/move`, { column: newColumn }),
  getSubtasks: (taskId) => apiClient.get(`/tasks/${taskId}/subtasks`),
  createSubtask: (taskId, data) => apiClient.post(`/tasks/${taskId}/subtasks`, data),
  getAvailableDependencyTasks: (projectId, excludeTaskId = null) =>
    apiClient.get('/tasks/available-dependencies', { params: { project_id: projectId, exclude_task_id: excludeTaskId } }),
  getTaskDependencies: (taskId) => apiClient.get(`/tasks/${taskId}/dependencies`),
  updateTaskDependencies: (taskId, dependencyIds = []) => apiClient.post(`/tasks/${taskId}/dependencies`, { dependency_task_ids: dependencyIds }),
  suggestFocus: () => apiClient.get('/ai/suggest-focus'),
};

export const recurringTasksAPI = {
  getRecurringTasks: () => apiClient.get('/tasks/recurring'),
  createRecurringTask: (data) => apiClient.post('/tasks/recurring', data),
  updateRecurringTask: (id, data) => apiClient.put(`/tasks/recurring/${id}`, data),
  deleteRecurringTask: (id) => apiClient.delete(`/tasks/recurring/${id}`),
  generateRecurringTaskInstances: () => apiClient.post('/tasks/recurring/generate'),
};

export const dashboardAPI = {
  getDashboard: () => apiClient.get('/dashboard'),
};

export const insightsAPI = {
  getInsights: (dateRange = 'all_time', areaId = null) =>
    apiClient.get('/insights', { params: { date_range: dateRange, ...(areaId ? { area_id: areaId } : {}) } }),
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

// Temporary minimal stubs to satisfy Insights imports without breaking the app.
// These return empty datasets and can be replaced with real backend routes later.
export const todayAPI = {
  getTodayView: async () => ({ data: [] }),
  addTaskToToday: async (_taskId) => ({ data: { success: true } }),
  removeTaskFromToday: async (_taskId) => ({ data: { success: true } }),
};

export const insightsDrilldownAPI = {
  getEisenhowerTasks: async (_quadrant, _state) => ({ data: { tasks: [] } }),
  getPillarTasks: async (_pillarId, _scope) => ({ data: { tasks: [] } }),
  getProjectTasks: async (_projectId, _scope) => ({ data: { tasks: [] } }),
  getAreaTasks: async (_areaId, _scope) => ({ data: { tasks: [] } }),
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

export const handleApiError = (error, defaultMessage = 'An error occurred') => {
  if (error?.response) {
    return error.response.data?.message || error.response.data?.detail || defaultMessage;
  } else if (error?.request) {
    return 'Network error - please check your connection';
  } else {
    return error?.message || defaultMessage;
  }
};

export const api = apiClient;
export default apiClient;