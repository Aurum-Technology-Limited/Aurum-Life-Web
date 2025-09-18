import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface WorkflowRule {
  id: string;
  name: string;
  description: string;
  trigger: {
    type: 'schedule' | 'completion' | 'deadline' | 'energy' | 'context';
    conditions: any;
  };
  actions: WorkflowAction[];
  enabled: boolean;
  priority: number;
  learningScore: number;
  executionCount: number;
  successRate: number;
  createdAt: Date;
  lastExecuted?: Date;
}

export interface WorkflowAction {
  id: string;
  type: 'create_task' | 'reschedule' | 'prioritize' | 'notify' | 'analyze' | 'suggest';
  parameters: any;
  confidence: number;
}

export interface AIInsight {
  id: string;
  type: 'pattern' | 'optimization' | 'prediction' | 'recommendation';
  title: string;
  description: string;
  confidence: number;
  impact: 'low' | 'medium' | 'high';
  actionable: boolean;
  createdAt: Date;
  category: string;
  source: 'workflow' | 'analysis' | 'prediction' | 'user_feedback';
}

export interface AutomationMetrics {
  totalExecutions: number;
  successfulExecutions: number;
  failedExecutions: number;
  timeSaved: number; // in minutes
  tasksAutomated: number;
  lastUpdated: Date;
}

export interface Phase4Settings {
  aiWorkflowsEnabled: boolean;
  learningMode: 'active' | 'passive' | 'disabled';
  automationLevel: 'conservative' | 'moderate' | 'aggressive';
  insightFrequency: 'real-time' | 'daily' | 'weekly';
  privacyMode: 'standard' | 'enhanced' | 'maximum';
  
  // Phase 3 Completion Features
  auditLoggingEnabled: boolean;
  performanceMonitoringEnabled: boolean;
  automatedTestingEnabled: boolean;
}

interface Phase4State {
  // Workflows
  workflows: WorkflowRule[];
  insights: AIInsight[];
  metrics: AutomationMetrics;
  settings: Phase4Settings;
  
  // UI State
  activeWorkflowTab: string;
  selectedWorkflow: string | null;
  isCreatingWorkflow: boolean;
  
  // Actions
  addWorkflow: (workflow: Omit<WorkflowRule, 'id' | 'createdAt'>) => void;
  updateWorkflow: (id: string, updates: Partial<WorkflowRule>) => void;
  deleteWorkflow: (id: string) => void;
  toggleWorkflow: (id: string) => void;
  executeWorkflow: (id: string) => Promise<boolean>;
  
  addInsight: (insight: Omit<AIInsight, 'id' | 'createdAt'>) => void;
  markInsightAsActionable: (id: string, actionable: boolean) => void;
  applyInsightSuggestion: (id: string) => Promise<boolean>;
  
  updateMetrics: (metrics: Partial<AutomationMetrics>) => void;
  updateSettings: (settings: Partial<Phase4Settings>) => void;
  
  // UI Actions
  setActiveWorkflowTab: (tab: string) => void;
  setSelectedWorkflow: (id: string | null) => void;
  setIsCreatingWorkflow: (creating: boolean) => void;
  
  // Analytics
  getWorkflowPerformance: (id: string) => {
    successRate: number;
    avgExecutionTime: number;
    timeSaved: number;
    learningProgress: number;
  } | null;
  getInsightsByCategory: (category: string) => AIInsight[];
  getTopPerformingWorkflows: (limit?: number) => WorkflowRule[];
  
  // Learning
  recordWorkflowExecution: (id: string, success: boolean, timeTaken: number) => void;
  updateLearningScore: (id: string, feedback: 'positive' | 'negative' | 'neutral') => void;
  
  // Initialization
  initializePhase4: () => void;
  resetPhase4Data: () => void;
}

const defaultSettings: Phase4Settings = {
  aiWorkflowsEnabled: true,
  learningMode: 'active',
  automationLevel: 'moderate',
  insightFrequency: 'daily',
  privacyMode: 'standard',
  
  // Phase 3 Features - All enabled by default
  auditLoggingEnabled: true,
  performanceMonitoringEnabled: true,
  automatedTestingEnabled: true
};

const defaultMetrics: AutomationMetrics = {
  totalExecutions: 0,
  successfulExecutions: 0,
  failedExecutions: 0,
  timeSaved: 0,
  tasksAutomated: 0,
  lastUpdated: new Date()
};

export const usePhase4Store = create<Phase4State>()(
  persist(
    (set, get) => ({
      // Initial State
      workflows: [],
      insights: [],
      metrics: defaultMetrics,
      settings: defaultSettings,
      
      // UI State
      activeWorkflowTab: 'dashboard',
      selectedWorkflow: null,
      isCreatingWorkflow: false,
      
      // Workflow Actions
      addWorkflow: (workflowData) => {
        const workflow: WorkflowRule = {
          ...workflowData,
          id: `workflow_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          createdAt: new Date(),
          executionCount: 0,
          successRate: 0,
          learningScore: 5.0
        };
        
        set((state) => ({
          workflows: [...state.workflows, workflow]
        }));
      },
      
      updateWorkflow: (id, updates) => {
        set((state) => ({
          workflows: state.workflows.map(workflow =>
            workflow.id === id ? { ...workflow, ...updates } : workflow
          )
        }));
      },
      
      deleteWorkflow: (id) => {
        set((state) => ({
          workflows: state.workflows.filter(workflow => workflow.id !== id),
          selectedWorkflow: state.selectedWorkflow === id ? null : state.selectedWorkflow
        }));
      },
      
      toggleWorkflow: (id) => {
        set((state) => ({
          workflows: state.workflows.map(workflow =>
            workflow.id === id ? { ...workflow, enabled: !workflow.enabled } : workflow
          )
        }));
      },
      
      executeWorkflow: async (id) => {
        const workflow = get().workflows.find(w => w.id === id);
        if (!workflow || !workflow.enabled) return false;
        
        try {
          // Simulate workflow execution
          const success = Math.random() > 0.1; // 90% success rate
          const timeTaken = Math.random() * 5 + 1; // 1-6 seconds
          
          get().recordWorkflowExecution(id, success, timeTaken);
          
          if (success) {
            // Generate insight from successful execution
            get().addInsight({
              type: 'pattern',
              title: `Workflow "${workflow.name}" executed successfully`,
              description: `Automated task completed with ${Math.round(workflow.successRate * 100)}% success rate`,
              confidence: 0.85,
              impact: 'medium',
              actionable: false,
              category: 'automation',
              source: 'workflow'
            });
          }
          
          return success;
        } catch (error) {
          console.error('Workflow execution failed:', error);
          get().recordWorkflowExecution(id, false, 0);
          return false;
        }
      },
      
      // Insight Actions
      addInsight: (insightData) => {
        const insight: AIInsight = {
          ...insightData,
          id: `insight_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          createdAt: new Date()
        };
        
        set((state) => ({
          insights: [insight, ...state.insights].slice(0, 100) // Keep only latest 100 insights
        }));
      },
      
      markInsightAsActionable: (id, actionable) => {
        set((state) => ({
          insights: state.insights.map(insight =>
            insight.id === id ? { ...insight, actionable } : insight
          )
        }));
      },
      
      applyInsightSuggestion: async (id) => {
        const insight = get().insights.find(i => i.id === id);
        if (!insight || !insight.actionable) return false;
        
        try {
          // Simulate applying suggestion
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Mark as applied by removing actionable flag
          get().markInsightAsActionable(id, false);
          
          return true;
        } catch (error) {
          console.error('Failed to apply insight suggestion:', error);
          return false;
        }
      },
      
      // Metrics Actions
      updateMetrics: (updates) => {
        set((state) => ({
          metrics: {
            ...state.metrics,
            ...updates,
            lastUpdated: new Date()
          }
        }));
      },
      
      updateSettings: (updates) => {
        set((state) => ({
          settings: {
            ...state.settings,
            ...updates
          }
        }));
      },
      
      // UI Actions
      setActiveWorkflowTab: (tab) => {
        set({ activeWorkflowTab: tab });
      },
      
      setSelectedWorkflow: (id) => {
        set({ selectedWorkflow: id });
      },
      
      setIsCreatingWorkflow: (creating) => {
        set({ isCreatingWorkflow: creating });
      },
      
      // Analytics
      getWorkflowPerformance: (id) => {
        const workflow = get().workflows.find(w => w.id === id);
        if (!workflow) return null;
        
        return {
          successRate: workflow.successRate,
          avgExecutionTime: 2.5, // Mock data
          timeSaved: workflow.executionCount * 3, // Mock calculation
          learningProgress: workflow.learningScore
        };
      },
      
      getInsightsByCategory: (category) => {
        return get().insights.filter(insight => insight.category === category);
      },
      
      getTopPerformingWorkflows: (limit = 5) => {
        return get().workflows
          .filter(w => w.enabled)
          .sort((a, b) => b.successRate - a.successRate)
          .slice(0, limit);
      },
      
      // Learning
      recordWorkflowExecution: (id, success, timeTaken) => {
        set((state) => {
          const updatedWorkflows = state.workflows.map(workflow => {
            if (workflow.id === id) {
              const newExecutionCount = workflow.executionCount + 1;
              const newSuccessRate = success 
                ? (workflow.successRate * workflow.executionCount + 1) / newExecutionCount
                : (workflow.successRate * workflow.executionCount) / newExecutionCount;
              
              return {
                ...workflow,
                executionCount: newExecutionCount,
                successRate: newSuccessRate,
                lastExecuted: new Date()
              };
            }
            return workflow;
          });
          
          const metrics = state.metrics;
          return {
            workflows: updatedWorkflows,
            metrics: {
              ...metrics,
              totalExecutions: metrics.totalExecutions + 1,
              successfulExecutions: success ? metrics.successfulExecutions + 1 : metrics.successfulExecutions,
              failedExecutions: !success ? metrics.failedExecutions + 1 : metrics.failedExecutions,
              timeSaved: success ? metrics.timeSaved + Math.round(timeTaken * 2) : metrics.timeSaved,
              tasksAutomated: success ? metrics.tasksAutomated + 1 : metrics.tasksAutomated,
              lastUpdated: new Date()
            }
          };
        });
      },
      
      updateLearningScore: (id, feedback) => {
        set((state) => ({
          workflows: state.workflows.map(workflow => {
            if (workflow.id === id) {
              let scoreAdjustment = 0;
              switch (feedback) {
                case 'positive': scoreAdjustment = 0.2; break;
                case 'negative': scoreAdjustment = -0.3; break;
                case 'neutral': scoreAdjustment = 0.1; break;
              }
              
              return {
                ...workflow,
                learningScore: Math.max(0, Math.min(10, workflow.learningScore + scoreAdjustment))
              };
            }
            return workflow;
          })
        }));
      },
      
      // Initialization
      initializePhase4: () => {
        // Initialize with sample data if empty
        const state = get();
        if (state.workflows.length === 0) {
          // Add sample workflows and insights
          const sampleWorkflows: Omit<WorkflowRule, 'id' | 'createdAt'>[] = [
            {
              name: 'Smart Morning Routine',
              description: 'Automatically adjusts morning tasks based on energy levels and calendar',
              trigger: {
                type: 'schedule',
                conditions: { time: '06:00', days: ['mon', 'tue', 'wed', 'thu', 'fri'] }
              },
              actions: [
                {
                  id: 'a1',
                  type: 'analyze',
                  parameters: { target: 'energy_level', timeframe: 'last_7_days' },
                  confidence: 0.92
                }
              ],
              enabled: true,
              priority: 5,
              learningScore: 8.4,
              executionCount: 24,
              successRate: 0.91
            }
          ];
          
          sampleWorkflows.forEach(workflow => get().addWorkflow(workflow));
          
          // Add sample insights
          get().addInsight({
            type: 'pattern',
            title: 'High Productivity Pattern Detected',
            description: 'You consistently achieve 40% more on Tuesdays when you start with creative tasks',
            confidence: 0.89,
            impact: 'high',
            actionable: true,
            category: 'productivity',
            source: 'analysis'
          });
        }
      },
      
      resetPhase4Data: () => {
        set({
          workflows: [],
          insights: [],
          metrics: defaultMetrics,
          settings: defaultSettings,
          activeWorkflowTab: 'dashboard',
          selectedWorkflow: null,
          isCreatingWorkflow: false
        });
      }
    }),
    {
      name: 'aurum-phase4-store',
      version: 1,
      // Persist everything except UI state
      partialize: (state) => ({
        workflows: state.workflows,
        insights: state.insights,
        metrics: state.metrics,
        settings: state.settings
      })
    }
  )
);