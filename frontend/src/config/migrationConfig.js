/**
 * GraphQL Migration Configuration
 * Controls which components use GraphQL vs REST
 */

// Feature flags for gradual migration
export const GRAPHQL_MIGRATION_FLAGS = {
  // Core Features
  DASHBOARD: process.env.REACT_APP_GRAPHQL_DASHBOARD === 'true' || false,
  TASKS: process.env.REACT_APP_GRAPHQL_TASKS === 'true' || false,
  PROJECTS: process.env.REACT_APP_GRAPHQL_PROJECTS === 'true' || false,
  JOURNAL: process.env.REACT_APP_GRAPHQL_JOURNAL === 'true' || false,
  PILLARS: process.env.REACT_APP_GRAPHQL_PILLARS === 'true' || false,
  AREAS: process.env.REACT_APP_GRAPHQL_AREAS === 'true' || false,
  
  // Sub-features
  TASK_LIST: process.env.REACT_APP_GRAPHQL_TASK_LIST === 'true' || false,
  TASK_DETAILS: process.env.REACT_APP_GRAPHQL_TASK_DETAILS === 'true' || false,
  PROJECT_LIST: process.env.REACT_APP_GRAPHQL_PROJECT_LIST === 'true' || false,
  PROJECT_DETAILS: process.env.REACT_APP_GRAPHQL_PROJECT_DETAILS === 'true' || false,
  
  // Analytics & Insights
  ANALYTICS: process.env.REACT_APP_GRAPHQL_ANALYTICS === 'true' || false,
  INSIGHTS: process.env.REACT_APP_GRAPHQL_INSIGHTS === 'true' || false,
  
  // User Features
  USER_PROFILE: process.env.REACT_APP_GRAPHQL_USER_PROFILE === 'true' || false,
  USER_STATS: process.env.REACT_APP_GRAPHQL_USER_STATS === 'true' || false,
};

// Migration phases
export const MIGRATION_PHASES = {
  PHASE_1: ['DASHBOARD', 'USER_STATS'], // Start with read-heavy features
  PHASE_2: ['TASKS', 'TASK_LIST', 'TASK_DETAILS'], // Core functionality
  PHASE_3: ['PROJECTS', 'PROJECT_LIST', 'PROJECT_DETAILS'], // Related features
  PHASE_4: ['JOURNAL', 'PILLARS', 'AREAS'], // Additional features
  PHASE_5: ['ANALYTICS', 'INSIGHTS', 'USER_PROFILE'], // Complete migration
};

// Get current migration phase
export const getCurrentPhase = () => {
  const enabledFlags = Object.entries(GRAPHQL_MIGRATION_FLAGS)
    .filter(([_, enabled]) => enabled)
    .map(([flag]) => flag);
  
  for (const [phase, flags] of Object.entries(MIGRATION_PHASES)) {
    if (flags.every(flag => enabledFlags.includes(flag))) {
      return phase;
    }
  }
  
  return 'PHASE_0';
};

// Check if a feature should use GraphQL
export const useGraphQLForFeature = (feature) => {
  return GRAPHQL_MIGRATION_FLAGS[feature] || false;
};

// Migration metrics
export const getMigrationMetrics = () => {
  const total = Object.keys(GRAPHQL_MIGRATION_FLAGS).length;
  const migrated = Object.values(GRAPHQL_MIGRATION_FLAGS).filter(Boolean).length;
  const percentage = Math.round((migrated / total) * 100);
  
  return {
    total,
    migrated,
    remaining: total - migrated,
    percentage,
    phase: getCurrentPhase(),
  };
};

// Local storage for A/B testing
const STORAGE_KEY = 'graphql_migration_overrides';

export const getLocalOverrides = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch {
    return {};
  }
};

export const setLocalOverride = (feature, enabled) => {
  const overrides = getLocalOverrides();
  overrides[feature] = enabled;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides));
  
  // Reload to apply changes
  window.location.reload();
};

// Apply local overrides
const localOverrides = getLocalOverrides();
Object.entries(localOverrides).forEach(([feature, enabled]) => {
  if (feature in GRAPHQL_MIGRATION_FLAGS) {
    GRAPHQL_MIGRATION_FLAGS[feature] = enabled;
  }
});

// Export helper to check migration status
export const isMigrationComplete = () => {
  return Object.values(GRAPHQL_MIGRATION_FLAGS).every(Boolean);
};

// Performance tracking
export const trackMigrationPerformance = (feature, apiType, duration) => {
  const key = `migration_perf_${feature}_${apiType}`;
  const existing = JSON.parse(localStorage.getItem(key) || '[]');
  
  existing.push({
    timestamp: Date.now(),
    duration,
  });
  
  // Keep last 100 entries
  if (existing.length > 100) {
    existing.shift();
  }
  
  localStorage.setItem(key, JSON.stringify(existing));
};

// Get performance comparison
export const getPerformanceComparison = (feature) => {
  const restKey = `migration_perf_${feature}_REST`;
  const graphqlKey = `migration_perf_${feature}_GRAPHQL`;
  
  const restData = JSON.parse(localStorage.getItem(restKey) || '[]');
  const graphqlData = JSON.parse(localStorage.getItem(graphqlKey) || '[]');
  
  const avgRest = restData.reduce((sum, item) => sum + item.duration, 0) / restData.length || 0;
  const avgGraphQL = graphqlData.reduce((sum, item) => sum + item.duration, 0) / graphqlData.length || 0;
  
  return {
    rest: {
      average: avgRest,
      samples: restData.length,
    },
    graphql: {
      average: avgGraphQL,
      samples: graphqlData.length,
    },
    improvement: avgRest > 0 ? ((avgRest - avgGraphQL) / avgRest) * 100 : 0,
  };
};