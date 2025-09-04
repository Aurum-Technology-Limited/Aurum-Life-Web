/**
 * Migration Adapter Hooks
 * Seamlessly switch between REST and GraphQL based on feature flags
 */

import { useCallback, useEffect, useRef } from 'react';
import { useQuery as useRestQuery, useMutation as useRestMutation } from '@tanstack/react-query';
import { 
  useGraphQLForFeature, 
  trackMigrationPerformance,
  GRAPHQL_MIGRATION_FLAGS 
} from '../config/migrationConfig';
import * as graphQLHooks from './useGraphQL';
import * as apiServices from '../services/api';

/**
 * Performance tracking wrapper
 */
const withPerformanceTracking = (fn, feature, apiType) => {
  return async (...args) => {
    const startTime = performance.now();
    try {
      const result = await fn(...args);
      const duration = performance.now() - startTime;
      trackMigrationPerformance(feature, apiType, duration);
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      trackMigrationPerformance(feature, apiType, duration);
      throw error;
    }
  };
};

/**
 * Adaptive Dashboard Hook
 */
export function useAdaptiveDashboard() {
  const useGraphQL = useGraphQLForFeature('DASHBOARD');
  
  // GraphQL version
  const graphQLResult = graphQLHooks.useDashboard();
  
  // REST version
  const restResult = useRestQuery({
    queryKey: ['dashboard'],
    queryFn: withPerformanceTracking(
      apiServices.dashboardAPI.getDashboard,
      'DASHBOARD',
      'REST'
    ),
    enabled: !useGraphQL,
  });
  
  // Track GraphQL performance
  useEffect(() => {
    if (useGraphQL && !graphQLResult.loading && graphQLResult.dashboard) {
      // Performance already tracked by Apollo
    }
  }, [useGraphQL, graphQLResult.loading, graphQLResult.dashboard]);
  
  // Return unified interface
  if (useGraphQL) {
    return {
      data: graphQLResult.dashboard,
      loading: graphQLResult.loading,
      error: graphQLResult.error,
      refetch: graphQLResult.refetch,
      source: 'graphql',
    };
  }
  
  return {
    data: restResult.data,
    loading: restResult.isLoading,
    error: restResult.error,
    refetch: restResult.refetch,
    source: 'rest',
  };
}

/**
 * Adaptive Tasks Hook
 */
export function useAdaptiveTasks(filter = {}, pagination = { limit: 20, offset: 0 }) {
  const useGraphQL = useGraphQLForFeature('TASKS');
  
  // GraphQL version
  const graphQLResult = graphQLHooks.useTasks(filter, pagination);
  
  // REST version
  const restResult = useRestQuery({
    queryKey: ['tasks', filter, pagination],
    queryFn: withPerformanceTracking(
      () => apiServices.tasksAPI.getTasks({ ...filter, ...pagination }),
      'TASKS',
      'REST'
    ),
    enabled: !useGraphQL,
  });
  
  // Unified interface
  if (useGraphQL) {
    return {
      tasks: graphQLResult.tasks,
      totalCount: graphQLResult.totalCount,
      hasNextPage: graphQLResult.hasNextPage,
      loading: graphQLResult.loading,
      error: graphQLResult.error,
      refetch: graphQLResult.refetch,
      loadMore: graphQLResult.loadMore,
      source: 'graphql',
    };
  }
  
  // Transform REST response to match GraphQL interface
  const restData = restResult.data || {};
  return {
    tasks: restData.tasks || [],
    totalCount: restData.total || 0,
    hasNextPage: (pagination.offset + pagination.limit) < (restData.total || 0),
    loading: restResult.isLoading,
    error: restResult.error,
    refetch: restResult.refetch,
    loadMore: () => {
      // Implement REST pagination
      pagination.offset += pagination.limit;
      restResult.refetch();
    },
    source: 'rest',
  };
}

/**
 * Adaptive Create Task Hook
 */
export function useAdaptiveCreateTask() {
  const useGraphQL = useGraphQLForFeature('TASKS');
  
  // GraphQL version
  const graphQLMutation = graphQLHooks.useCreateTask();
  
  // REST version
  const restMutation = useRestMutation({
    mutationFn: withPerformanceTracking(
      apiServices.tasksAPI.createTask,
      'TASKS',
      'REST'
    ),
    onSuccess: () => {
      // Invalidate queries
      queryClient.invalidateQueries(['tasks']);
    },
  });
  
  // Unified interface
  if (useGraphQL) {
    return {
      createTask: graphQLMutation.createTask,
      loading: graphQLMutation.loading,
      error: graphQLMutation.error,
      source: 'graphql',
    };
  }
  
  return {
    createTask: (input) => {
      // Transform GraphQL input to REST format
      const restInput = {
        project_id: input.projectId,
        name: input.name,
        description: input.description,
        priority: input.priority.toLowerCase(),
        due_date: input.dueDate,
        estimated_duration: input.estimatedDuration,
      };
      return restMutation.mutate(restInput);
    },
    loading: restMutation.isLoading,
    error: restMutation.error,
    source: 'rest',
  };
}

/**
 * Adaptive Projects Hook
 */
export function useAdaptiveProjects(filter = {}, pagination = { limit: 20, offset: 0 }) {
  const useGraphQL = useGraphQLForFeature('PROJECTS');
  
  // GraphQL version
  const graphQLResult = graphQLHooks.useProjects(filter, pagination);
  
  // REST version
  const restResult = useRestQuery({
    queryKey: ['projects', filter, pagination],
    queryFn: withPerformanceTracking(
      () => apiServices.projectsAPI.getProjects({ ...filter, ...pagination }),
      'PROJECTS',
      'REST'
    ),
    enabled: !useGraphQL,
  });
  
  // Unified interface
  if (useGraphQL) {
    return {
      projects: graphQLResult.projects,
      totalCount: graphQLResult.totalCount,
      loading: graphQLResult.loading,
      error: graphQLResult.error,
      refetch: graphQLResult.refetch,
      source: 'graphql',
    };
  }
  
  return {
    projects: restResult.data?.projects || [],
    totalCount: restResult.data?.total || 0,
    loading: restResult.isLoading,
    error: restResult.error,
    refetch: restResult.refetch,
    source: 'rest',
  };
}

/**
 * Adaptive Journal Entries Hook
 */
export function useAdaptiveJournalEntries(search = '', pagination = { limit: 20, offset: 0 }) {
  const useGraphQL = useGraphQLForFeature('JOURNAL');
  
  // GraphQL version
  const graphQLResult = graphQLHooks.useJournalEntries(search, pagination);
  
  // REST version
  const restResult = useRestQuery({
    queryKey: ['journal', search, pagination],
    queryFn: withPerformanceTracking(
      () => apiServices.journalAPI.getEntries({ search, ...pagination }),
      'JOURNAL',
      'REST'
    ),
    enabled: !useGraphQL,
  });
  
  // Unified interface
  if (useGraphQL) {
    return {
      entries: graphQLResult.entries,
      totalCount: graphQLResult.totalCount,
      loading: graphQLResult.loading,
      error: graphQLResult.error,
      refetch: graphQLResult.refetch,
      loadMore: graphQLResult.loadMore,
      source: 'graphql',
    };
  }
  
  return {
    entries: restResult.data?.entries || [],
    totalCount: restResult.data?.total || 0,
    loading: restResult.isLoading,
    error: restResult.error,
    refetch: restResult.refetch,
    loadMore: () => {
      pagination.offset += pagination.limit;
      restResult.refetch();
    },
    source: 'rest',
  };
}

/**
 * Adaptive Pillars Hook
 */
export function useAdaptivePillars(archived = false) {
  const useGraphQL = useGraphQLForFeature('PILLARS');
  
  // GraphQL version
  const graphQLResult = graphQLHooks.usePillars(archived);
  
  // REST version
  const restResult = useRestQuery({
    queryKey: ['pillars', archived],
    queryFn: withPerformanceTracking(
      () => apiServices.pillarsAPI.getPillars({ archived }),
      'PILLARS',
      'REST'
    ),
    enabled: !useGraphQL,
  });
  
  // Unified interface
  if (useGraphQL) {
    return {
      pillars: graphQLResult.pillars,
      loading: graphQLResult.loading,
      error: graphQLResult.error,
      refetch: graphQLResult.refetch,
      source: 'graphql',
    };
  }
  
  return {
    pillars: restResult.data || [],
    loading: restResult.isLoading,
    error: restResult.error,
    refetch: restResult.refetch,
    source: 'rest',
  };
}

/**
 * Hook to check current API source
 */
export function useAPISource(feature) {
  const useGraphQL = useGraphQLForFeature(feature);
  return useGraphQL ? 'graphql' : 'rest';
}

/**
 * Hook to toggle between REST and GraphQL (for testing)
 */
export function useAPIToggle(feature) {
  const currentSource = useAPISource(feature);
  
  const toggle = useCallback(() => {
    const { setLocalOverride } = require('../config/migrationConfig');
    setLocalOverride(feature, currentSource === 'rest');
  }, [feature, currentSource]);
  
  return {
    source: currentSource,
    toggle,
    isGraphQL: currentSource === 'graphql',
  };
}

// Export all adaptive hooks
export const adaptiveHooks = {
  useAdaptiveDashboard,
  useAdaptiveTasks,
  useAdaptiveCreateTask,
  useAdaptiveProjects,
  useAdaptiveJournalEntries,
  useAdaptivePillars,
};