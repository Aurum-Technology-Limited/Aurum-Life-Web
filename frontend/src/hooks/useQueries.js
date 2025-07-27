import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import emergencyAPI from '../services/emergencyApi';
import { dashboardAPI, areasAPI, pillarsAPI, projectsAPI, tasksAPI, insightsAPI, aiCoachAPI } from '../services/api';

// Query keys for consistent cache management
export const queryKeys = {
  dashboard: ['dashboard'],
  areas: (includeProjects = false, includeArchived = false) => ['areas', includeProjects, includeArchived],
  pillars: (includeSubPillars = true, includeAreas = false, includeArchived = false) => 
    ['pillars', includeSubPillars, includeAreas, includeArchived],
  projects: (areaId = null, includeArchived = false) => ['projects', areaId, includeArchived],
  tasks: (projectId = null) => ['tasks', projectId],
  insights: (dateRange = 'all_time', areaId = null) => ['insights', dateRange, areaId],
  aiCoach: ['aiCoach', 'today'],
};

// Dashboard Query Hook
export const useDashboardQuery = () => {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: async () => {
      const response = await emergencyAPI.dashboard();
      return response.data; // Extract data from axios response
    },
    staleTime: 3 * 60 * 1000, // 3 minutes - dashboard needs fresher data
    gcTime: 10 * 60 * 1000, // 10 minutes cache
    retry: 2, // Retry twice for critical dashboard data
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    meta: {
      description: 'Dashboard main data including stats, recent tasks, and user info'
    }
  });
};

// Areas Query Hook
export const useAreasQuery = (includeProjects = false, includeArchived = false) => {
  return useQuery({
    queryKey: queryKeys.areas(includeProjects, includeArchived),
    queryFn: async () => {
      const response = await areasAPI.getAreas(includeProjects, includeArchived);
      return response.data; // Extract data from axios response
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes - areas change less frequently
    meta: {
      description: `Areas data - includeProjects: ${includeProjects}, includeArchived: ${includeArchived}`
    }
  });
};

// Pillars Query Hook
export const usePillarsQuery = (includeSubPillars = true, includeAreas = false, includeArchived = false) => {
  return useQuery({
    queryKey: queryKeys.pillars(includeSubPillars, includeAreas, includeArchived),
    queryFn: async () => {
      const response = await pillarsAPI.getPillars(includeSubPillars, includeAreas, includeArchived);
      return response.data; // Extract data from axios response
    },
    staleTime: 10 * 60 * 1000, // 10 minutes - pillars change infrequently
    gcTime: 20 * 60 * 1000, // 20 minutes cache
    meta: {
      description: `Pillars data - includeSubPillars: ${includeSubPillars}, includeAreas: ${includeAreas}`
    }
  });
};

// Projects Query Hook
export const useProjectsQuery = (areaId = null, includeArchived = false) => {
  return useQuery({
    queryKey: queryKeys.projects(areaId, includeArchived),
    queryFn: () => projectsAPI.getProjects(areaId, includeArchived),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes cache
    enabled: true, // Always enabled, but can be conditional if needed
    meta: {
      description: `Projects data - areaId: ${areaId}, includeArchived: ${includeArchived}`
    }
  });
};

// Tasks Query Hook
export const useTasksQuery = (projectId = null) => {
  return useQuery({
    queryKey: queryKeys.tasks(projectId),
    queryFn: () => tasksAPI.getTasks(projectId),
    staleTime: 2 * 60 * 1000, // 2 minutes - tasks change frequently
    gcTime: 10 * 60 * 1000, // 10 minutes cache
    meta: {
      description: `Tasks data - projectId: ${projectId}`
    }
  });
};

// Insights Query Hook
export const useInsightsQuery = (dateRange = 'all_time', areaId = null) => {
  return useQuery({
    queryKey: queryKeys.insights(dateRange, areaId),
    queryFn: () => insightsAPI.getInsights(dateRange, areaId),
    staleTime: 10 * 60 * 1000, // 10 minutes - insights are computational
    gcTime: 30 * 60 * 1000, // 30 minutes cache
    meta: {
      description: `Insights data - dateRange: ${dateRange}, areaId: ${areaId}`
    }
  });
};

// AI Coach Query Hook
export const useAiCoachQuery = () => {
  return useQuery({
    queryKey: queryKeys.aiCoach,
    queryFn: () => aiCoachAPI.getTodaysPriorities(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes cache
    retry: 1, // AI coach can fail more gracefully
    meta: {
      description: 'AI Coach today priorities and recommendations'
    }
  });
};

// Mutation hooks for data updates with optimistic updates

// Dashboard refresh mutation
export const useDashboardMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => dashboardAPI.getDashboard(),
    onSuccess: (data) => {
      // Update the dashboard cache with fresh data
      queryClient.setQueryData(queryKeys.dashboard, data);
    },
    onError: (error) => {
      console.error('Dashboard refresh failed:', error);
    },
  });
};

// Generic invalidation helper
export const useInvalidateQueries = () => {
  const queryClient = useQueryClient();
  
  return {
    invalidateDashboard: () => queryClient.invalidateQueries({ queryKey: queryKeys.dashboard }),
    invalidateAreas: () => queryClient.invalidateQueries({ queryKey: ['areas'] }),
    invalidatePillars: () => queryClient.invalidateQueries({ queryKey: ['pillars'] }),
    invalidateProjects: () => queryClient.invalidateQueries({ queryKey: ['projects'] }),
    invalidateTasks: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
    invalidateInsights: () => queryClient.invalidateQueries({ queryKey: ['insights'] }),
    invalidateAiCoach: () => queryClient.invalidateQueries({ queryKey: queryKeys.aiCoach }),
    invalidateAll: () => queryClient.invalidateQueries(),
  };
};

// Prefetch helpers for improved navigation performance
export const usePrefetchQueries = () => {
  const queryClient = useQueryClient();
  
  return {
    prefetchAreas: () => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.areas(true, false),
        queryFn: () => areasAPI.getAreas(true, false),
        staleTime: 5 * 60 * 1000,
      });
    },
    prefetchProjects: (areaId = null) => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.projects(areaId, false),
        queryFn: () => projectsAPI.getProjects(areaId, false),
        staleTime: 5 * 60 * 1000,
      });
    },
    prefetchInsights: () => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.insights(),
        queryFn: () => insightsAPI.getInsights(),
        staleTime: 10 * 60 * 1000,
      });
    },
  };
};

export default {
  useDashboardQuery,
  useAreasQuery,
  usePillarsQuery,
  useProjectsQuery,
  useTasksQuery,
  useInsightsQuery,
  useAiCoachQuery,
  useDashboardMutation,
  useInvalidateQueries,
  usePrefetchQueries,
  queryKeys,
};