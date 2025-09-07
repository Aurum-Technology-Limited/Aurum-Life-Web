/**
 * Custom GraphQL Hooks
 * Simplified data fetching and mutations with loading states
 */

import { useQuery, useMutation, useSubscription } from '@apollo/client';
import { useCallback, useMemo } from 'react';
import { toast } from 'sonner';
import {
  GET_DASHBOARD,
  GET_PILLARS,
  GET_AREAS,
  GET_PROJECTS,
  GET_TASKS,
  GET_PROJECT_DETAIL,
  GET_TASK_DETAIL,
  GET_JOURNAL_ENTRIES,
  GET_JOURNAL_INSIGHTS,
  GET_ANALYTICS_DASHBOARD,
  GET_ANALYTICS_PREFERENCES,
} from '../graphql/queries';
import {
  CREATE_TASK,
  UPDATE_TASK,
  DELETE_TASK,
  TOGGLE_TASK_COMPLETION,
  CREATE_PROJECT,
  UPDATE_PROJECT,
  CREATE_JOURNAL_ENTRY,
  UPDATE_JOURNAL_ENTRY,
  DELETE_JOURNAL_ENTRY,
  ANALYZE_JOURNAL_SENTIMENT,
  CREATE_AREA,
  UPDATE_AREA,
  DELETE_AREA,
  CREATE_PILLAR,
  UPDATE_PILLAR,
  DELETE_PILLAR,
  UPDATE_ANALYTICS_PREFERENCES,
} from '../graphql/mutations';
import { optimisticTaskUpdate, optimisticProjectUpdate } from '../services/apolloClient';

// Dashboard Hook
export function useDashboard() {
  const { data, loading, error, refetch } = useQuery(GET_DASHBOARD, {
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  return {
    dashboard: data?.dashboard,
    loading,
    error,
    refetch,
  };
}

// Pillars Hook
export function usePillars(archived = false) {
  const { data, loading, error, refetch } = useQuery(GET_PILLARS, {
    variables: { archived },
    fetchPolicy: 'cache-first',
  });

  return {
    pillars: data?.pillars || [],
    loading,
    error,
    refetch,
  };
}

// Areas Hook
export function useAreas(pillarId = null, archived = false) {
  const { data, loading, error, refetch } = useQuery(GET_AREAS, {
    variables: { pillarId, archived },
    fetchPolicy: 'cache-first',
    skip: false, // Always query, let GraphQL handle filtering
  });

  return {
    areas: data?.areas || [],
    loading,
    error,
    refetch,
  };
}

// Projects Hook with filters
export function useProjects(filter = {}, pagination = {}) {
  const variables = {
    filter: {
      areaId: filter.areaId,
      status: filter.status,
      priority: filter.priority,
      searchTerm: filter.searchTerm,
      archived: filter.archived || false,
    },
    pagination: {
      skip: pagination.skip || 0,
      limit: pagination.limit || 20,
    },
  };

  const { data, loading, error, refetch, fetchMore } = useQuery(GET_PROJECTS, {
    variables,
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  const loadMore = useCallback(() => {
    if (!data?.projects?.hasNextPage) return;
    
    return fetchMore({
      variables: {
        ...variables,
        pagination: {
          ...variables.pagination,
          skip: data.projects.projects.length,
        },
      },
      updateQuery: (prev, { fetchMoreResult }) => {
        if (!fetchMoreResult) return prev;
        return {
          projects: {
            ...fetchMoreResult.projects,
            projects: [...prev.projects.projects, ...fetchMoreResult.projects.projects],
          },
        };
      },
    });
  }, [data?.projects, fetchMore, variables]);

  return {
    projects: data?.projects?.projects || [],
    totalCount: data?.projects?.totalCount || 0,
    hasNextPage: data?.projects?.hasNextPage || false,
    loading,
    error,
    refetch,
    loadMore,
  };
}

// Project Detail Hook
export function useProjectDetail(id) {
  const { data, loading, error, refetch } = useQuery(GET_PROJECT_DETAIL, {
    variables: { id },
    skip: !id,
    fetchPolicy: 'cache-and-network',
  });

  return {
    project: data?.project,
    loading,
    error,
    refetch,
  };
}

// Tasks Hook with filters
export function useTasks(filter = {}, pagination = {}) {
  const variables = {
    filter: {
      projectId: filter.projectId,
      status: filter.status,
      priority: filter.priority,
      completed: filter.completed,
      searchTerm: filter.searchTerm,
    },
    pagination: {
      skip: pagination.skip || 0,
      limit: pagination.limit || 50,
    },
  };

  const { data, loading, error, refetch, fetchMore } = useQuery(GET_TASKS, {
    variables,
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  const loadMore = useCallback(() => {
    if (!data?.tasks?.hasNextPage) return;
    
    return fetchMore({
      variables: {
        ...variables,
        pagination: {
          ...variables.pagination,
          skip: data.tasks.tasks.length,
        },
      },
      updateQuery: (prev, { fetchMoreResult }) => {
        if (!fetchMoreResult) return prev;
        return {
          tasks: {
            ...fetchMoreResult.tasks,
            tasks: [...prev.tasks.tasks, ...fetchMoreResult.tasks.tasks],
          },
        };
      },
    });
  }, [data?.tasks, fetchMore, variables]);

  return {
    tasks: data?.tasks?.tasks || [],
    totalCount: data?.tasks?.totalCount || 0,
    hasNextPage: data?.tasks?.hasNextPage || false,
    loading,
    error,
    refetch,
    loadMore,
  };
}

// Task Detail Hook
export function useTaskDetail(id) {
  const { data, loading, error, refetch } = useQuery(GET_TASK_DETAIL, {
    variables: { id },
    skip: !id,
    fetchPolicy: 'cache-and-network',
  });

  return {
    task: data?.task,
    loading,
    error,
    refetch,
  };
}

// Task Mutations
export function useCreateTask() {
  const [createTask, { loading, error }] = useMutation(CREATE_TASK, {
    onCompleted: (data) => {
      if (data.createTask.success) {
        toast.success(data.createTask.message || 'Task created successfully');
      } else {
        toast.error(data.createTask.message || 'Failed to create task');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to create task');
    },
    update: (cache, { data }) => {
      if (data?.createTask?.success && data.createTask.task) {
        // Update tasks list in cache
        cache.modify({
          fields: {
            tasks(existingTasks = { tasks: [], totalCount: 0 }) {
              return {
                ...existingTasks,
                tasks: [data.createTask.task, ...existingTasks.tasks],
                totalCount: existingTasks.totalCount + 1,
              };
            },
          },
        });
      }
    },
  });

  return {
    createTask: (task) => createTask({ variables: { task } }),
    loading,
    error,
  };
}

export function useUpdateTask() {
  const [updateTask, { loading, error }] = useMutation(UPDATE_TASK, {
    onCompleted: (data) => {
      if (data.updateTask.success) {
        toast.success(data.updateTask.message || 'Task updated successfully');
      } else {
        toast.error(data.updateTask.message || 'Failed to update task');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to update task');
    },
  });

  return {
    updateTask: (id, updates) => updateTask({ 
      variables: { id, updates },
      optimisticResponse: optimisticTaskUpdate(id, updates),
    }),
    loading,
    error,
  };
}

export function useDeleteTask() {
  const [deleteTask, { loading, error }] = useMutation(DELETE_TASK, {
    onCompleted: (data) => {
      if (data.deleteTask.success) {
        toast.success(data.deleteTask.message || 'Task deleted successfully');
      } else {
        toast.error(data.deleteTask.message || 'Failed to delete task');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to delete task');
    },
    update: (cache, { data, variables }) => {
      if (data?.deleteTask?.success) {
        // Remove task from cache
        cache.modify({
          fields: {
            tasks(existingTasks = { tasks: [], totalCount: 0 }, { readField }) {
              return {
                ...existingTasks,
                tasks: existingTasks.tasks.filter(
                  taskRef => readField('id', taskRef) !== variables.id
                ),
                totalCount: existingTasks.totalCount - 1,
              };
            },
          },
        });
      }
    },
  });

  return {
    deleteTask: (id) => deleteTask({ variables: { id } }),
    loading,
    error,
  };
}

export function useToggleTaskCompletion() {
  const [toggleTask, { loading, error }] = useMutation(TOGGLE_TASK_COMPLETION);

  return {
    toggleCompletion: (id) => toggleTask({
      variables: { id },
      optimisticResponse: {
        __typename: 'Mutation',
        toggleTaskCompletion: {
          __typename: 'TaskMutationResponse',
          success: true,
          message: 'Task updated',
          task: {
            __typename: 'Task',
            id,
            completed: true, // Will be toggled by server
          },
        },
      },
    }),
    loading,
    error,
  };
}

// Project Mutations
export function useCreateProject() {
  const [createProject, { loading, error }] = useMutation(CREATE_PROJECT, {
    onCompleted: (data) => {
      if (data.createProject.success) {
        toast.success(data.createProject.message || 'Project created successfully');
      } else {
        toast.error(data.createProject.message || 'Failed to create project');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to create project');
    },
    update: (cache, { data }) => {
      if (data?.createProject?.success && data.createProject.project) {
        // Update projects list in cache
        cache.modify({
          fields: {
            projects(existingProjects = { projects: [], totalCount: 0 }) {
              return {
                ...existingProjects,
                projects: [data.createProject.project, ...existingProjects.projects],
                totalCount: existingProjects.totalCount + 1,
              };
            },
          },
        });
      }
    },
  });

  return {
    createProject: (project) => createProject({ variables: { project } }),
    loading,
    error,
  };
}

export function useUpdateProject() {
  const [updateProject, { loading, error }] = useMutation(UPDATE_PROJECT, {
    onCompleted: (data) => {
      if (data.updateProject.success) {
        toast.success(data.updateProject.message || 'Project updated successfully');
      } else {
        toast.error(data.updateProject.message || 'Failed to update project');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to update project');
    },
  });

  return {
    updateProject: (id, updates) => updateProject({ 
      variables: { id, updates },
      optimisticResponse: optimisticProjectUpdate(id, updates),
    }),
    loading,
    error,
  };
}

// Journal Hooks
export function useJournalEntries(options = {}) {
  const variables = {
    skip: options.skip || 0,
    limit: options.limit || 20,
    moodFilter: options.moodFilter,
    tagFilter: options.tagFilter,
    dateFrom: options.dateFrom,
    dateTo: options.dateTo,
  };

  const { data, loading, error, refetch, fetchMore } = useQuery(GET_JOURNAL_ENTRIES, {
    variables,
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  const loadMore = useCallback(() => {
    if (!data?.journalEntries) return;
    
    return fetchMore({
      variables: {
        ...variables,
        skip: data.journalEntries.length,
      },
      updateQuery: (prev, { fetchMoreResult }) => {
        if (!fetchMoreResult) return prev;
        return {
          journalEntries: [...prev.journalEntries, ...fetchMoreResult.journalEntries],
        };
      },
    });
  }, [data?.journalEntries, fetchMore, variables]);

  return {
    entries: data?.journalEntries || [],
    loading,
    error,
    refetch,
    loadMore,
  };
}

export function useJournalInsights(timeRange = 30) {
  const { data, loading, error, refetch } = useQuery(GET_JOURNAL_INSIGHTS, {
    variables: { timeRange },
    fetchPolicy: 'cache-first',
  });

  return {
    insights: data?.journalInsights,
    loading,
    error,
    refetch,
  };
}

// Journal Entry Creation Hook
export function useCreateJournalEntry() {
  const [createEntry, { loading, error }] = useMutation(CREATE_JOURNAL_ENTRY, {
    onCompleted: (data) => {
      if (data.createJournalEntry.success) {
        toast.success(data.createJournalEntry.message || 'Entry created successfully');
      } else {
        toast.error(data.createJournalEntry.message || 'Failed to create entry');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to create entry');
    },
    update: (cache, { data }) => {
      if (data?.createJournalEntry?.success && data.createJournalEntry.journalEntry) {
        // Add new entry to cache
        cache.modify({
          fields: {
            journalEntries(existingEntries = []) {
              return [data.createJournalEntry.journalEntry, ...existingEntries];
            },
          },
        });
      }
    },
  });

  return {
    createEntry: (entry) => createEntry({ variables: { entry } }),
    loading,
    error,
  };
}

// Journal Entry Update Hook
export function useUpdateJournalEntry() {
  const [updateEntry, { loading, error }] = useMutation(UPDATE_JOURNAL_ENTRY, {
    onCompleted: (data) => {
      if (data.updateJournalEntry.success) {
        toast.success(data.updateJournalEntry.message || 'Entry updated successfully');
      } else {
        toast.error(data.updateJournalEntry.message || 'Failed to update entry');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to update entry');
    },
  });

  return {
    updateEntry: (id, entry) => updateEntry({ variables: { id, entry } }),
    loading,
    error,
  };
}

// Journal Entry Delete Hook
export function useDeleteJournalEntry() {
  const [deleteEntry, { loading, error }] = useMutation(DELETE_JOURNAL_ENTRY, {
    onCompleted: (data) => {
      if (data.deleteJournalEntry.success) {
        toast.success(data.deleteJournalEntry.message || 'Entry deleted successfully');
      } else {
        toast.error(data.deleteJournalEntry.message || 'Failed to delete entry');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to delete entry');
    },
    update: (cache, { data, variables }) => {
      if (data?.deleteJournalEntry?.success) {
        // Remove entry from cache
        cache.modify({
          fields: {
            journalEntries(existingEntries = [], { readField }) {
              return existingEntries.filter(
                entry => readField('id', entry) !== variables.id
              );
            },
          },
        });
      }
    },
  });

  return {
    deleteEntry: (id) => deleteEntry({ variables: { id } }),
    loading,
    error,
  };
}

// Journal Sentiment Analysis Hook
export function useAnalyzeJournalSentiment() {
  const [analyzeSentiment, { loading, error }] = useMutation(ANALYZE_JOURNAL_SENTIMENT, {
    onCompleted: (data) => {
      if (data.analyzeJournalSentiment.success) {
        toast.success('Sentiment analysis completed');
      } else {
        toast.error(data.analyzeJournalSentiment.message || 'Analysis failed');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to analyze sentiment');
    },
  });

  return {
    analyzeSentiment: (entryId) => analyzeSentiment({ variables: { entryId } }),
    loading,
    error,
  };
}

// Area Hooks
export function useCreateArea() {
  const [createArea, { loading, error }] = useMutation(CREATE_AREA, {
    onCompleted: (data) => {
      if (data.createArea.success) {
        toast.success(data.createArea.message || 'Area created successfully');
      } else {
        toast.error(data.createArea.message || 'Failed to create area');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to create area');
    },
    update: (cache, { data }) => {
      if (data?.createArea?.success && data.createArea.area) {
        // Update areas list in cache
        cache.modify({
          fields: {
            areas(existingAreas = []) {
              return [...existingAreas, data.createArea.area];
            },
          },
        });
      }
    },
  });

  return {
    createArea: (area) => createArea({ variables: { area } }),
    loading,
    error,
  };
}

export function useUpdateArea() {
  const [updateArea, { loading, error }] = useMutation(UPDATE_AREA, {
    onCompleted: (data) => {
      if (data.updateArea.success) {
        toast.success(data.updateArea.message || 'Area updated successfully');
      } else {
        toast.error(data.updateArea.message || 'Failed to update area');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to update area');
    },
  });

  return {
    updateArea: (id, area) => updateArea({ variables: { id, area } }),
    loading,
    error,
  };
}

export function useDeleteArea() {
  const [deleteArea, { loading, error }] = useMutation(DELETE_AREA, {
    onCompleted: (data) => {
      if (data.deleteArea.success) {
        toast.success(data.deleteArea.message || 'Area deleted successfully');
      } else {
        toast.error(data.deleteArea.message || 'Failed to delete area');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to delete area');
    },
    update: (cache, { data, variables }) => {
      if (data?.deleteArea?.success) {
        // Remove area from cache
        cache.modify({
          fields: {
            areas(existingAreas = [], { readField }) {
              return existingAreas.filter(
                area => readField('id', area) !== variables.id
              );
            },
          },
        });
      }
    },
  });

  return {
    deleteArea: (id) => deleteArea({ variables: { id } }),
    loading,
    error,
  };
}

// Pillar Hooks
export function useCreatePillar() {
  const [createPillar, { loading, error }] = useMutation(CREATE_PILLAR, {
    onCompleted: (data) => {
      if (data.createPillar.success) {
        toast.success(data.createPillar.message || 'Pillar created successfully');
      } else {
        toast.error(data.createPillar.message || 'Failed to create pillar');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to create pillar');
    },
    update: (cache, { data }) => {
      if (data?.createPillar?.success && data.createPillar.pillar) {
        // Update pillars list in cache
        cache.modify({
          fields: {
            pillars(existingPillars = []) {
              return [...existingPillars, data.createPillar.pillar];
            },
          },
        });
      }
    },
  });

  return {
    createPillar: (pillar) => createPillar({ variables: { pillar } }),
    loading,
    error,
  };
}

export function useUpdatePillar() {
  const [updatePillar, { loading, error }] = useMutation(UPDATE_PILLAR, {
    onCompleted: (data) => {
      if (data.updatePillar.success) {
        toast.success(data.updatePillar.message || 'Pillar updated successfully');
      } else {
        toast.error(data.updatePillar.message || 'Failed to update pillar');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to update pillar');
    },
  });

  return {
    updatePillar: (id, pillar) => updatePillar({ variables: { id, pillar } }),
    loading,
    error,
  };
}

export function useDeletePillar() {
  const [deletePillar, { loading, error }] = useMutation(DELETE_PILLAR, {
    onCompleted: (data) => {
      if (data.deletePillar.success) {
        toast.success(data.deletePillar.message || 'Pillar deleted successfully');
      } else {
        toast.error(data.deletePillar.message || 'Failed to delete pillar');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to delete pillar');
    },
    update: (cache, { data, variables }) => {
      if (data?.deletePillar?.success) {
        // Remove pillar from cache
        cache.modify({
          fields: {
            pillars(existingPillars = [], { readField }) {
              return existingPillars.filter(
                pillar => readField('id', pillar) !== variables.id
              );
            },
          },
        });
      }
    },
  });

  return {
    deletePillar: (id) => deletePillar({ variables: { id } }),
    loading,
    error,
  };
}

// Analytics Hooks
export function useAnalyticsDashboard(days = 30) {
  const { data, loading, error, refetch } = useQuery(GET_ANALYTICS_DASHBOARD, {
    variables: { days },
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  return {
    dashboard: data?.analyticsDashboard,
    loading,
    error,
    refetch,
  };
}

export function useAnalyticsPreferences() {
  const { data, loading, error, refetch } = useQuery(GET_ANALYTICS_PREFERENCES, {
    fetchPolicy: 'cache-first',
  });

  return {
    preferences: data?.analyticsPreferences,
    loading,
    error,
    refetch,
  };
}

export function useUpdateAnalyticsPreferences() {
  const [updatePreferences, { loading, error }] = useMutation(UPDATE_ANALYTICS_PREFERENCES, {
    onCompleted: (data) => {
      if (data.updateAnalyticsPreferences.success) {
        toast.success(data.updateAnalyticsPreferences.message || 'Preferences updated successfully');
      } else {
        toast.error(data.updateAnalyticsPreferences.message || 'Failed to update preferences');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to update preferences');
    },
  });

  return {
    updatePreferences: (preferences) => updatePreferences({ variables: { preferences } }),
    loading,
    error,
  };
}