/**
 * Apollo Client Configuration
 * Efficient GraphQL data fetching with caching
 */

import {
  ApolloClient,
  InMemoryCache,
  createHttpLink,
  ApolloLink,
  Observable,
} from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';
import { createPersistedQueryLink } from '@apollo/client/link/persisted-queries';
import { sha256 } from 'crypto-hash';

// Get backend URL
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const GRAPHQL_ENDPOINT = `${BACKEND_URL}/graphql`;

// Create HTTP link
const httpLink = createHttpLink({
  uri: GRAPHQL_ENDPOINT,
});

// Add authentication
const authLink = setContext((_, { headers }) => {
  // Get token from localStorage
  const token = localStorage.getItem('access_token');
  
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    },
  };
});

// Error handling
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `GraphQL error: Message: ${message}, Location: ${locations}, Path: ${path}`
      );
    });
  }

  if (networkError) {
    console.error(`Network error: ${networkError}`);
    
    // Handle auth errors
    if (networkError.statusCode === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
  }
});

// Request timing for performance monitoring
const timingLink = new ApolloLink((operation, forward) => {
  const startTime = Date.now();
  
  return new Observable((observer) => {
    const subscription = forward(operation).subscribe({
      next: (result) => {
        const duration = Date.now() - startTime;
        console.log(`GraphQL ${operation.operationName} took ${duration}ms`);
        
        // Track performance metrics
        if (window.performance && window.performance.mark) {
          window.performance.measure(
            `graphql-${operation.operationName}`,
            `graphql-${operation.operationName}-start`,
            `graphql-${operation.operationName}-end`
          );
        }
        
        observer.next(result);
      },
      error: observer.error.bind(observer),
      complete: observer.complete.bind(observer),
    });

    return () => subscription.unsubscribe();
  });
});

// Persisted queries for better performance
const persistedQueriesLink = createPersistedQueryLink({
  sha256,
  useGETForHashedQueries: true,
});

// Cache configuration
const cache = new InMemoryCache({
  typePolicies: {
    Query: {
      fields: {
        // Merge paginated results
        tasks: {
          keyArgs: ['filter'],
          merge(existing = { tasks: [], totalCount: 0 }, incoming) {
            return {
              ...incoming,
              tasks: [...(existing.tasks || []), ...(incoming.tasks || [])],
            };
          },
        },
        projects: {
          keyArgs: ['filter'],
          merge(existing = { projects: [], totalCount: 0 }, incoming) {
            return {
              ...incoming,
              projects: [...(existing.projects || []), ...(incoming.projects || [])],
            };
          },
        },
        journalEntries: {
          keyArgs: ['search'],
          merge(existing = { entries: [], totalCount: 0 }, incoming) {
            return {
              ...incoming,
              entries: [...(existing.entries || []), ...(incoming.entries || [])],
            };
          },
        },
      },
    },
    Task: {
      fields: {
        // Compute completion rate
        completionRate: {
          read(_, { readField }) {
            const completed = readField('completed');
            const subtasks = readField('subtasks') || [];
            if (subtasks.length === 0) return completed ? 100 : 0;
            
            const completedSubtasks = subtasks.filter(t => t.completed).length;
            return (completedSubtasks / subtasks.length) * 100;
          },
        },
      },
    },
    Project: {
      fields: {
        // Compute task completion
        taskCompletion: {
          read(_, { readField }) {
            const tasks = readField('tasks') || [];
            if (tasks.length === 0) return 0;
            
            const completedTasks = tasks.filter(t => t.completed).length;
            return (completedTasks / tasks.length) * 100;
          },
        },
      },
    },
  },
});

// Create Apollo Client
const apolloClient = new ApolloClient({
  link: ApolloLink.from([
    errorLink,
    authLink,
    timingLink,
    persistedQueriesLink,
    httpLink,
  ]),
  cache,
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'cache-and-network',
      errorPolicy: 'all',
    },
    query: {
      fetchPolicy: 'cache-first',
      errorPolicy: 'all',
    },
  },
});

// Export client and cache
export { apolloClient, cache };

// Cache utilities
export const clearCache = () => {
  apolloClient.clearStore();
};

export const resetCache = () => {
  apolloClient.resetStore();
};

// Optimistic response helpers
export const optimisticTaskUpdate = (taskId, updates) => ({
  __typename: 'Mutation',
  updateTask: {
    __typename: 'TaskMutationResponse',
    success: true,
    task: {
      __typename: 'Task',
      id: taskId,
      ...updates,
    },
  },
});

export const optimisticProjectUpdate = (projectId, updates) => ({
  __typename: 'Mutation',
  updateProject: {
    __typename: 'ProjectMutationResponse',
    success: true,
    project: {
      __typename: 'Project',
      id: projectId,
      ...updates,
    },
  },
});