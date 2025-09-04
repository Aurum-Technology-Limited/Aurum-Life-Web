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

// Journal Mutations
export const CREATE_JOURNAL_ENTRY = gql`
  mutation CreateJournalEntry($entry: CreateJournalEntryInput!) {
    createJournalEntry(entry: $entry) {
      success
      message
      journalEntry {
        id
        title
        content
        mood
        tags
        sentimentScore
        sentimentCategory
        createdAt
      }
    }
  }
`;

export const UPDATE_JOURNAL_ENTRY = gql`
  mutation UpdateJournalEntry($id: ID!, $entry: UpdateJournalEntryInput!) {
    updateJournalEntry(id: $id, entry: $entry) {
      success
      message
      journalEntry {
        id
        title
        content
        mood
        tags
        sentimentScore
        sentimentCategory
        updatedAt
      }
    }
  }
`;

export const DELETE_JOURNAL_ENTRY = gql`
  mutation DeleteJournalEntry($id: ID!) {
    deleteJournalEntry(id: $id) {
      success
      message
    }
  }
`;

export const ANALYZE_JOURNAL_SENTIMENT = gql`
  mutation AnalyzeJournalSentiment($entryId: ID!) {
    analyzeJournalSentiment(entryId: $entryId) {
      success
      message
      sentimentData {
        score
        category
        confidence
        emotionalKeywords
      }
    }
  }
`;

// Area Mutations
export const CREATE_AREA = gql`
  mutation CreateArea($area: CreateAreaInput!) {
    createArea(area: $area) {
      success
      message
      area {
        id
        name
        description
        icon
        color
        importance
        pillarId
      }
    }
  }
`;

export const UPDATE_AREA = gql`
  mutation UpdateArea($id: ID!, $area: UpdateAreaInput!) {
    updateArea(id: $id, area: $area) {
      success
      message
      area {
        id
        name
        description
        icon
        color
        importance
        archived
      }
    }
  }
`;

export const DELETE_AREA = gql`
  mutation DeleteArea($id: ID!) {
    deleteArea(id: $id) {
      success
      message
    }
  }
`;

// Pillar Mutations
export const CREATE_PILLAR = gql`
  mutation CreatePillar($pillar: CreatePillarInput!) {
    createPillar(pillar: $pillar) {
      success
      message
      pillar {
        id
        name
        description
        icon
        color
      }
    }
  }
`;

export const UPDATE_PILLAR = gql`
  mutation UpdatePillar($id: ID!, $pillar: UpdatePillarInput!) {
    updatePillar(id: $id, pillar: $pillar) {
      success
      message
      pillar {
        id
        name
        description
        icon
        color
        archived
      }
    }
  }
`;

export const DELETE_PILLAR = gql`
  mutation DeletePillar($id: ID!) {
    deletePillar(id: $id) {
      success
      message
    }
  }
`;