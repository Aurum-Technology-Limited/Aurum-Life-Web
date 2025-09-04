/**
 * GraphQL Mutations
 * Efficient data modifications with optimistic updates
 */

import { gql } from '@apollo/client';
import { TASK_FIELDS, PROJECT_FIELDS } from './queries';

// Task Mutations
export const CREATE_TASK = gql`
  mutation CreateTask($input: CreateTaskInput!) {
    createTask(input: $input) {
      success
      message
      task {
        ...TaskFields
      }
    }
  }
  ${TASK_FIELDS}
`;

export const UPDATE_TASK = gql`
  mutation UpdateTask($input: UpdateTaskInput!) {
    updateTask(input: $input) {
      success
      message
      task {
        ...TaskFields
      }
    }
  }
  ${TASK_FIELDS}
`;

export const DELETE_TASK = gql`
  mutation DeleteTask($id: ID!) {
    deleteTask(id: $id) {
      success
      message
    }
  }
`;

export const TOGGLE_TASK_COMPLETION = gql`
  mutation ToggleTaskCompletion($id: ID!) {
    toggleTaskCompletion(id: $id) {
      success
      message
      task {
        ...TaskFields
      }
    }
  }
  ${TASK_FIELDS}
`;

// Project Mutations
export const CREATE_PROJECT = gql`
  mutation CreateProject($input: CreateProjectInput!) {
    createProject(input: $input) {
      success
      message
      project {
        ...ProjectFields
      }
    }
  }
  ${PROJECT_FIELDS}
`;

export const UPDATE_PROJECT = gql`
  mutation UpdateProject($input: UpdateProjectInput!) {
    updateProject(input: $input) {
      success
      message
      project {
        ...ProjectFields
      }
    }
  }
  ${PROJECT_FIELDS}
`;

// Journal Mutations
export const CREATE_JOURNAL_ENTRY = gql`
  mutation CreateJournalEntry($input: CreateJournalEntryInput!) {
    createJournalEntry(input: $input) {
      success
      message
      entry {
        id
        title
        content
        mood
        energyLevel
        tags
        wordCount
        createdAt
      }
    }
  }
`;

// Batch Operations
export const BATCH_UPDATE_TASKS = gql`
  mutation BatchUpdateTasks($taskIds: [ID!]!, $updates: UpdateTaskInput!) {
    batchUpdateTasks(taskIds: $taskIds, updates: $updates) {
      success
      message
      updatedCount
    }
  }
`;

export const BATCH_DELETE_TASKS = gql`
  mutation BatchDeleteTasks($taskIds: [ID!]!) {
    batchDeleteTasks(taskIds: $taskIds) {
      success
      message
      deletedCount
    }
  }
`;