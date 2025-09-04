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
} from '../graphql/queries';
import {
  CREATE_TASK,
  UPDATE_TASK,
  DELETE_TASK,
  TOGGLE_TASK_COMPLETION,
  CREATE_PROJECT,
  UPDATE_PROJECT,
  CREATE_JOURNAL_ENTRY,
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
  });

  return {
    areas: data?.areas || [],
    loading,
    error,
    refetch,
  };
}

// Projects Hook with Pagination
export function useProjects(filter = {}, pagination = { limit: 20, offset: 0 }) {
  const { data, loading, error, fetchMore, refetch } = useQuery(GET_PROJECTS, {
    variables: { filter, pagination },
    fetchPolicy: 'cache-first',
    notifyOnNetworkStatusChange: true,
  });

  const loadMore = useCallback(() => {
    if (data?.projects?.hasNextPage) {
      return fetchMore({
        variables: {
          pagination: {
            ...pagination,
            offset: data.projects.projects.length,
          },
        },
      });
    }
  }, [data, fetchMore, pagination]);

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

// Tasks Hook with Pagination
export function useTasks(filter = {}, pagination = { limit: 20, offset: 0 }) {
  const { data, loading, error, fetchMore, refetch } = useQuery(GET_TASKS, {
    variables: { filter, pagination },
    fetchPolicy: 'cache-first',
    notifyOnNetworkStatusChange: true,
  });

  const loadMore = useCallback(() => {
    if (data?.tasks?.hasNextPage) {
      return fetchMore({
        variables: {
          pagination: {
            ...pagination,
            offset: data.tasks.tasks.length,
          },
        },
      });
    }
  }, [data, fetchMore, pagination]);

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
export function useTaskDetail(taskId) {
  const { data, loading, error, refetch } = useQuery(GET_TASK_DETAIL, {
    variables: { id: taskId },
    skip: !taskId,
  });

  return {
    task: data?.task,
    loading,
    error,
    refetch,
  };
}

// Project Detail Hook
export function useProjectDetail(projectId) {
  const { data, loading, error, refetch } = useQuery(GET_PROJECT_DETAIL, {
    variables: { id: projectId },
    skip: !projectId,
  });

  return {
    project: data?.project,
    loading,
    error,
    refetch,
  };
}

// Journal Entries Hook
export function useJournalEntries(search = '', pagination = { limit: 20, offset: 0 }) {
  const { data, loading, error, fetchMore, refetch } = useQuery(GET_JOURNAL_ENTRIES, {
    variables: { search, pagination },
    fetchPolicy: 'cache-first',
  });

  const loadMore = useCallback(() => {
    if (data?.journalEntries?.hasNextPage) {
      return fetchMore({
        variables: {
          pagination: {
            ...pagination,
            offset: data.journalEntries.entries.length,
          },
        },
      });
    }
  }, [data, fetchMore, pagination]);

  return {
    entries: data?.journalEntries?.entries || [],
    totalCount: data?.journalEntries?.totalCount || 0,
    hasNextPage: data?.journalEntries?.hasNextPage || false,
    loading,
    error,
    refetch,
    loadMore,
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
    createTask: (input) => createTask({ variables: { input } }),
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
    updateTask: (input) => updateTask({
      variables: { input },
      optimisticResponse: optimisticTaskUpdate(input.id, input),
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
        cache.evict({ id: cache.identify({ __typename: 'Task', id: variables.id }) });
        cache.gc();
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
  const [toggleTask, { loading, error }] = useMutation(TOGGLE_TASK_COMPLETION, {
    onError: (error) => {
      toast.error(error.message || 'Failed to update task');
    },
  });

  return {
    toggleTask: (id) => toggleTask({
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
    createProject: (input) => createProject({ variables: { input } }),
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
    updateProject: (input) => updateProject({
      variables: { input },
      optimisticResponse: optimisticProjectUpdate(input.id, input),
    }),
    loading,
    error,
  };
}

// Journal Mutations
export function useCreateJournalEntry() {
  const [createEntry, { loading, error }] = useMutation(CREATE_JOURNAL_ENTRY, {
    onCompleted: (data) => {
      if (data.createJournalEntry.success) {
        toast.success(data.createJournalEntry.message || 'Journal entry created');
      } else {
        toast.error(data.createJournalEntry.message || 'Failed to create entry');
      }
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to create entry');
    },
  });

  return {
    createEntry: (input) => createEntry({ variables: { input } }),
    loading,
    error,
  };
}