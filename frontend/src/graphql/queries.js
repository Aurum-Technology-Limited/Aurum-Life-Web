/**
 * GraphQL Queries
 * Efficient data fetching with exact field selection
 */

import { gql } from '@apollo/client';

// Fragments for reusable field selections
export const TASK_FIELDS = gql`
  fragment TaskFields on Task {
    id
    name
    description
    status
    priority
    dueDate
    completed
    completedAt
    estimatedDuration
    createdAt
    updatedAt
    hrmPriorityScore
    hrmReasoningSummary
  }
`;

export const PROJECT_FIELDS = gql`
  fragment ProjectFields on Project {
    id
    name
    description
    icon
    deadline
    status
    priority
    importance
    completionPercentage
    archived
    createdAt
    updatedAt
    hrmHealthScore
    goalCoherenceScore
  }
`;

export const AREA_FIELDS = gql`
  fragment AreaFields on Area {
    id
    name
    description
    icon
    color
    importance
    archived
    sortOrder
    timeAllocationActual
    timeAllocationRecommended
    balanceScore
  }
`;

export const PILLAR_FIELDS = gql`
  fragment PillarFields on Pillar {
    id
    name
    description
    icon
    color
    sortOrder
    archived
    timeAllocationPercentage
    visionStatement
    alignmentStrength
  }
`;

// Queries
export const GET_DASHBOARD = gql`
  query GetDashboard {
    dashboard {
      userStats {
        taskStats {
          total
          completed
          inProgress
          overdue
          completionRate
        }
        projectStats {
          total
          completed
          inProgress
          onHold
          averageCompletion
        }
        totalJournalEntries
        totalAreas
        totalPillars
        currentStreak
        totalPoints
      }
      recentTasks {
        ...TaskFields
      }
      upcomingDeadlines {
        ...TaskFields
      }
      recentInsights {
        id
        title
        summary
        confidenceScore
        impactScore
        createdAt
      }
    }
  }
  ${TASK_FIELDS}
`;

export const GET_PILLARS = gql`
  query GetPillars($archived: Boolean = false) {
    pillars(archived: $archived) {
      ...PillarFields
      areas {
        ...AreaFields
      }
    }
  }
  ${PILLAR_FIELDS}
  ${AREA_FIELDS}
`;

export const GET_AREAS = gql`
  query GetAreas($pillarId: ID, $archived: Boolean = false) {
    areas(pillarId: $pillarId, archived: $archived) {
      ...AreaFields
      pillar {
        id
        name
      }
      projects {
        id
        name
        status
        completionPercentage
      }
    }
  }
  ${AREA_FIELDS}
`;

export const GET_PROJECTS = gql`
  query GetProjects(
    $filter: ProjectFilterInput
    $pagination: PaginationInput
  ) {
    projects(filter: $filter, pagination: $pagination) {
      projects {
        ...ProjectFields
        area {
          id
          name
          icon
        }
        tasks {
          id
          completed
        }
      }
      totalCount
      hasNextPage
    }
  }
  ${PROJECT_FIELDS}
`;

export const GET_PROJECT_DETAIL = gql`
  query GetProjectDetail($id: ID!) {
    project(id: $id) {
      ...ProjectFields
      area {
        ...AreaFields
        pillar {
          id
          name
        }
      }
      tasks {
        ...TaskFields
      }
    }
  }
  ${PROJECT_FIELDS}
  ${AREA_FIELDS}
  ${TASK_FIELDS}
`;

export const GET_TASKS = gql`
  query GetTasks(
    $filter: TaskFilterInput
    $pagination: PaginationInput
  ) {
    tasks(filter: $filter, pagination: $pagination) {
      tasks {
        ...TaskFields
        project {
          id
          name
          icon
        }
      }
      totalCount
      hasNextPage
    }
  }
  ${TASK_FIELDS}
`;

export const GET_TASK_DETAIL = gql`
  query GetTaskDetail($id: ID!) {
    task(id: $id) {
      ...TaskFields
      project {
        ...ProjectFields
        area {
          id
          name
        }
      }
      subtasks {
        ...TaskFields
      }
    }
  }
  ${TASK_FIELDS}
  ${PROJECT_FIELDS}
`;

export const GET_JOURNAL_ENTRIES = gql`
  query GetJournalEntries(
    $pagination: PaginationInput
    $search: String
  ) {
    journalEntries(pagination: $pagination, search: $search) {
      entries {
        id
        title
        content
        mood
        energyLevel
        tags
        wordCount
        createdAt
        sentimentScore
        sentimentCategory
        emotionalKeywords
        dominantEmotions
      }
      totalCount
      hasNextPage
    }
  }
`;

export const GET_ME = gql`
  query GetMe {
    me {
      id
      email
      username
      firstName
      lastName
      profilePicture
      isActive
      fullName
    }
  }
`;

// Subscriptions (for future real-time updates)
export const TASK_UPDATED = gql`
  subscription OnTaskUpdated($userId: ID!) {
    taskUpdated(userId: $userId) {
      ...TaskFields
    }
  }
  ${TASK_FIELDS}
`;

export const PROJECT_UPDATED = gql`
  subscription OnProjectUpdated($userId: ID!) {
    projectUpdated(userId: $userId) {
      ...ProjectFields
    }
  }
  ${PROJECT_FIELDS}
`;