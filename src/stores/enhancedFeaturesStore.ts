import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { 
  Pillar, 
  Area,
  QuickCaptureItem, 
  ProgressSnapshot, 
  Achievement, 
  ReviewSession, 
  TimeBlock, 
  EnergyPattern,
  SmartSuggestion,
  Task,
  Project,
  ProjectAttachment
} from '../types/enhanced-features';

interface EnhancedFeaturesState {
  // Quick Capture
  quickCaptureItems: QuickCaptureItem[];
  isQuickCaptureOpen: boolean;
  isVoiceRecording: boolean;
  
  // Progress & Analytics
  pillars: Pillar[];
  progressSnapshots: ProgressSnapshot[];
  achievements: Achievement[];
  
  // Review System
  reviewSessions: ReviewSession[];
  currentReview: ReviewSession | null;
  isReviewModalOpen: boolean;
  
  // Calendar & Time Blocking
  timeBlocks: TimeBlock[];
  energyPatterns: EnergyPattern[];
  smartSuggestions: SmartSuggestion[];
  
  // Actions
  // Quick Capture
  openQuickCapture: () => void;
  closeQuickCapture: () => void;
  addQuickCaptureItem: (item: Omit<QuickCaptureItem, 'id' | 'createdAt'>) => void;
  processQuickCaptureItem: (itemId: string, targetPillar: string, targetArea?: string, targetProject?: string) => void;
  deleteQuickCaptureItem: (itemId: string) => void;
  startVoiceRecording: () => void;
  stopVoiceRecording: () => void;
  
  // Progress & Analytics
  addPillar: (pillar: Omit<Pillar, 'id' | 'lastUpdated'>) => void;
  updatePillarHealth: (pillarId: string, healthScore: number) => void;
  updatePillarTimeTracking: (pillarId: string, actualHours: number) => void;
  addAchievement: (achievement: Omit<Achievement, 'id' | 'earnedAt'>) => void;
  takeProgressSnapshot: () => void;
  
  // Review System
  startReview: (type: 'weekly' | 'monthly' | 'quarterly') => void;
  updateReviewReflection: (prompt: string, response: string) => void;
  addReviewWin: (win: string) => void;
  addReviewImprovement: (improvement: string) => void;
  addNextWeekFocus: (focus: string) => void;
  completeReview: () => void;
  closeReviewModal: () => void;
  
  // Calendar & Time Blocking
  addTimeBlock: (timeBlock: Omit<TimeBlock, 'id'>) => void;
  updateTimeBlock: (blockId: string, updates: Partial<TimeBlock>) => void;
  completeTimeBlock: (blockId: string, notes?: string) => void;
  deleteTimeBlock: (blockId: string) => void;
  updateEnergyPattern: (hourOfDay: number, dayOfWeek: number, energyLevel: number) => void;
  addSmartSuggestion: (suggestion: Omit<SmartSuggestion, 'id' | 'createdAt'>) => void;
  dismissSuggestion: (suggestionId: string) => void;
  
  // Hierarchy Management
  addPillar: (pillar: Omit<Pillar, 'id' | 'lastUpdated'>) => void;
  addArea: (pillarId: string, area: Omit<Area, 'id' | 'pillarId'>) => void;
  addProject: (areaId: string, project: Omit<Project, 'id' | 'areaId'>) => void;
  addTask: (projectId: string, task: Omit<Task, 'id' | 'projectId'>) => void;
  updatePillar: (pillarId: string, updates: Partial<Pillar>) => void;
  updateArea: (areaId: string, updates: Partial<Area>) => void;
  updateProject: (projectId: string, updates: Partial<Project>) => void;
  updateTask: (taskId: string, updates: Partial<Task>) => void;
  deletePillar: (pillarId: string) => void;
  deleteArea: (areaId: string) => void;
  deleteProject: (projectId: string) => void;
  deleteTask: (taskId: string) => void;
  duplicatePillar: (pillarId: string) => void;
  duplicateArea: (areaId: string) => void;
  duplicateProject: (projectId: string) => void;
  duplicateTask: (taskId: string) => void;
  completeTask: (taskId: string) => void;
  
  // File attachment management
  addProjectAttachment: (projectId: string, attachment: Omit<ProjectAttachment, 'id' | 'uploadedAt'>) => void;
  removeProjectAttachment: (projectId: string, attachmentId: string) => void;
  getProjectAttachments: (projectId: string) => ProjectAttachment[];
  
  // Utility
  getPillarById: (pillarId: string) => Pillar | undefined;
  getAreaById: (areaId: string) => Area | undefined;
  getProjectById: (projectId: string) => Project | undefined;
  getTaskById: (taskId: string) => Task | undefined;
  getAreasByPillarId: (pillarId: string) => Area[];
  getProjectsByAreaId: (areaId: string) => Project[];
  getTasksByProjectId: (projectId: string) => Task[];
  getAllAreas: () => Area[];
  getAllProjects: () => Project[];
  getAllTasks: () => Task[];
  getUnprocessedQuickCapture: () => QuickCaptureItem[];
  getTodaysTimeBlocks: () => TimeBlock[];
  getPillarHealthTrend: (pillarId: string, days: number) => number[];
}

export const useEnhancedFeaturesStore = create<EnhancedFeaturesState>()(
  persist(
    (set, get) => ({
      // Initial state
      quickCaptureItems: [],
      isQuickCaptureOpen: false,
      isVoiceRecording: false,
      pillars: [],
      progressSnapshots: [],
      achievements: [],
      reviewSessions: [],
      currentReview: null,
      isReviewModalOpen: false,
      timeBlocks: [],
      energyPatterns: [],
      smartSuggestions: [],

      // Quick Capture Actions
      openQuickCapture: () => set({ isQuickCaptureOpen: true }),
      closeQuickCapture: () => set({ isQuickCaptureOpen: false, isVoiceRecording: false }),
      
      addQuickCaptureItem: (item) => {
        const newItem: QuickCaptureItem = {
          ...item,
          id: crypto.randomUUID(),
          createdAt: new Date(),
        };
        set(state => ({
          quickCaptureItems: [newItem, ...state.quickCaptureItems]
        }));
      },
      
      processQuickCaptureItem: (itemId, targetPillar, targetArea, targetProject) => {
        set(state => ({
          quickCaptureItems: state.quickCaptureItems.map(item =>
            item.id === itemId
              ? { ...item, processed: true, suggestedPillar: targetPillar, suggestedArea: targetArea, suggestedProject: targetProject }
              : item
          )
        }));
      },
      
      deleteQuickCaptureItem: (itemId) => {
        set(state => ({
          quickCaptureItems: state.quickCaptureItems.filter(item => item.id !== itemId)
        }));
      },
      
      startVoiceRecording: () => set({ isVoiceRecording: true }),
      stopVoiceRecording: () => set({ isVoiceRecording: false }),

      // Progress & Analytics Actions
      addPillar: (pillar) => {
        const newPillar: Pillar = {
          ...pillar,
          id: crypto.randomUUID(),
          lastUpdated: new Date(),
        };
        set(state => ({
          pillars: [...state.pillars, newPillar]
        }));
      },
      
      updatePillarHealth: (pillarId, healthScore) => {
        set(state => ({
          pillars: state.pillars.map(pillar =>
            pillar.id === pillarId
              ? { ...pillar, healthScore, lastUpdated: new Date() }
              : pillar
          )
        }));
      },
      
      updatePillarTimeTracking: (pillarId, actualHours) => {
        set(state => ({
          pillars: state.pillars.map(pillar =>
            pillar.id === pillarId
              ? { ...pillar, weeklyTimeActual: actualHours, lastUpdated: new Date() }
              : pillar
          )
        }));
      },
      
      addAchievement: (achievement) => {
        const newAchievement: Achievement = {
          ...achievement,
          id: crypto.randomUUID(),
          earnedAt: new Date(),
        };
        set(state => ({
          achievements: [newAchievement, ...state.achievements]
        }));
      },
      
      takeProgressSnapshot: () => {
        const state = get();
        const snapshot: ProgressSnapshot = {
          id: crypto.randomUUID(),
          date: new Date(),
          pillarHealthScores: state.pillars.reduce((acc, pillar) => {
            acc[pillar.id] = pillar.healthScore;
            return acc;
          }, {} as Record<string, number>),
          totalTasksCompleted: 0, // Calculate from tasks
          totalHoursLogged: state.pillars.reduce((sum, pillar) => sum + pillar.weeklyTimeActual, 0),
          energyLevels: {},
          achievements: state.achievements.filter(a => 
            new Date(a.earnedAt).toDateString() === new Date().toDateString()
          ),
        };
        
        set(state => ({
          progressSnapshots: [snapshot, ...state.progressSnapshots]
        }));
      },

      // Review System Actions
      startReview: (type) => {
        const newReview: ReviewSession = {
          id: crypto.randomUUID(),
          type,
          date: new Date(),
          reflections: {},
          wins: [],
          improvements: [],
          nextWeekFocus: [],
          pillarAdjustments: {},
          completed: false,
        };
        set({
          currentReview: newReview,
          isReviewModalOpen: true,
        });
      },
      
      updateReviewReflection: (prompt, response) => {
        set(state => ({
          currentReview: state.currentReview
            ? { ...state.currentReview, reflections: { ...state.currentReview.reflections, [prompt]: response } }
            : null
        }));
      },
      
      addReviewWin: (win) => {
        set(state => ({
          currentReview: state.currentReview
            ? { ...state.currentReview, wins: [...state.currentReview.wins, win] }
            : null
        }));
      },
      
      addReviewImprovement: (improvement) => {
        set(state => ({
          currentReview: state.currentReview
            ? { ...state.currentReview, improvements: [...state.currentReview.improvements, improvement] }
            : null
        }));
      },
      
      addNextWeekFocus: (focus) => {
        set(state => ({
          currentReview: state.currentReview
            ? { ...state.currentReview, nextWeekFocus: [...state.currentReview.nextWeekFocus, focus] }
            : null
        }));
      },
      
      completeReview: () => {
        set(state => {
          if (!state.currentReview) return state;
          
          const completedReview = { ...state.currentReview, completed: true };
          return {
            reviewSessions: [completedReview, ...state.reviewSessions],
            currentReview: null,
            isReviewModalOpen: false,
          };
        });
      },
      
      closeReviewModal: () => set({ isReviewModalOpen: false, currentReview: null }),

      // Calendar & Time Blocking Actions
      addTimeBlock: (timeBlock) => {
        const newTimeBlock: TimeBlock = {
          ...timeBlock,
          id: crypto.randomUUID(),
        };
        set(state => ({
          timeBlocks: [...state.timeBlocks, newTimeBlock]
        }));
      },
      
      updateTimeBlock: (blockId, updates) => {
        set(state => ({
          timeBlocks: state.timeBlocks.map(block =>
            block.id === blockId ? { ...block, ...updates } : block
          )
        }));
      },
      
      completeTimeBlock: (blockId, notes) => {
        set(state => ({
          timeBlocks: state.timeBlocks.map(block =>
            block.id === blockId
              ? { ...block, completed: true, actualEndTime: new Date(), notes }
              : block
          )
        }));
      },
      
      deleteTimeBlock: (blockId) => {
        set(state => ({
          timeBlocks: state.timeBlocks.filter(block => block.id !== blockId)
        }));
      },
      
      updateEnergyPattern: (hourOfDay, dayOfWeek, energyLevel) => {
        set(state => {
          const existing = state.energyPatterns.find(
            p => p.hourOfDay === hourOfDay && p.dayOfWeek === dayOfWeek
          );
          
          if (existing) {
            return {
              energyPatterns: state.energyPatterns.map(pattern =>
                pattern.hourOfDay === hourOfDay && pattern.dayOfWeek === dayOfWeek
                  ? {
                      ...pattern,
                      averageEnergyLevel: (pattern.averageEnergyLevel * pattern.sampleSize + energyLevel) / (pattern.sampleSize + 1),
                      sampleSize: pattern.sampleSize + 1,
                      lastUpdated: new Date(),
                    }
                  : pattern
              )
            };
          } else {
            const newPattern: EnergyPattern = {
              userId: 'current-user', // TODO: Get from auth
              hourOfDay,
              dayOfWeek,
              averageEnergyLevel: energyLevel,
              sampleSize: 1,
              lastUpdated: new Date(),
            };
            return {
              energyPatterns: [...state.energyPatterns, newPattern]
            };
          }
        });
      },
      
      addSmartSuggestion: (suggestion) => {
        const newSuggestion: SmartSuggestion = {
          ...suggestion,
          id: crypto.randomUUID(),
          createdAt: new Date(),
        };
        set(state => ({
          smartSuggestions: [newSuggestion, ...state.smartSuggestions]
        }));
      },
      
      dismissSuggestion: (suggestionId) => {
        set(state => ({
          smartSuggestions: state.smartSuggestions.map(suggestion =>
            suggestion.id === suggestionId
              ? { ...suggestion, dismissed: true }
              : suggestion
          )
        }));
      },

      // Hierarchy Management Actions
      addPillar: (pillar) => {
        const newPillar: Pillar = {
          ...pillar,
          id: crypto.randomUUID(),
          lastUpdated: new Date(),
        };
        
        set(state => ({
          pillars: [...state.pillars, newPillar]
        }));
      },

      addArea: (pillarId, area) => {
        const newArea: Area = {
          ...area,
          id: crypto.randomUUID(),
          pillarId,
        };
        
        set(state => ({
          pillars: state.pillars.map(pillar =>
            pillar.id === pillarId
              ? { ...pillar, areas: [...pillar.areas, newArea] }
              : pillar
          )
        }));
      },

      addProject: (areaId, project) => {
        const newProject: Project = {
          ...project,
          id: crypto.randomUUID(),
          areaId,
          attachments: []
        };
        
        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.map(area =>
              area.id === areaId
                ? { ...area, projects: [...area.projects, newProject] }
                : area
            )
          }))
        }));
      },

      addTask: (projectId, task) => {
        const newTask: Task = {
          ...task,
          id: crypto.randomUUID(),
          projectId,
        };
        
        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.map(area => ({
              ...area,
              projects: area.projects.map(project =>
                project.id === projectId
                  ? { ...project, tasks: [...project.tasks, newTask] }
                  : project
              )
            }))
          }))
        }));
      },

      updateTask: (taskId, updates) => {
        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.map(area => ({
              ...area,
              projects: area.projects.map(project => ({
                ...project,
                tasks: project.tasks.map(task =>
                  task.id === taskId ? { ...task, ...updates } : task
                )
              }))
            }))
          }))
        }));
      },

      completeTask: (taskId) => {
        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.map(area => ({
              ...area,
              projects: area.projects.map(project => ({
                ...project,
                tasks: project.tasks.map(task =>
                  task.id === taskId 
                    ? { ...task, status: 'completed', completedAt: new Date() }
                    : task
                )
              }))
            }))
          }))
        }));
      },

      // Update methods
      updatePillar: (pillarId, updates) => {
        set(state => ({
          pillars: state.pillars.map(pillar =>
            pillar.id === pillarId
              ? { ...pillar, ...updates, lastUpdated: new Date() }
              : pillar
          )
        }));
      },

      updateArea: (areaId, updates) => {
        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.map(area =>
              area.id === areaId ? { ...area, ...updates } : area
            )
          }))
        }));
      },

      updateProject: (projectId, updates) => {
        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.map(area => ({
              ...area,
              projects: area.projects.map(project =>
                project.id === projectId ? { ...project, ...updates } : project
              )
            }))
          }))
        }));
      },

      // Delete methods
      deletePillar: (pillarId) => {
        set(state => ({
          pillars: state.pillars.filter(pillar => pillar.id !== pillarId)
        }));
      },

      deleteArea: (areaId) => {
        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.filter(area => area.id !== areaId)
          }))
        }));
      },

      deleteProject: (projectId) => {
        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.map(area => ({
              ...area,
              projects: area.projects.filter(project => project.id !== projectId)
            }))
          }))
        }));
      },

      deleteTask: (taskId) => {
        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.map(area => ({
              ...area,
              projects: area.projects.map(project => ({
                ...project,
                tasks: project.tasks.filter(task => task.id !== taskId)
              }))
            }))
          }))
        }));
      },

      // Duplicate methods
      duplicatePillar: (pillarId) => {
        const state = get();
        const pillarToDuplicate = state.pillars.find(p => p.id === pillarId);
        if (!pillarToDuplicate) return;

        const duplicatedPillar: Pillar = {
          ...pillarToDuplicate,
          id: crypto.randomUUID(),
          name: `${pillarToDuplicate.name} (Copy)`,
          lastUpdated: new Date(),
          areas: pillarToDuplicate.areas.map(area => ({
            ...area,
            id: crypto.randomUUID(),
            pillarId: pillarToDuplicate.id, // Will be updated below
            projects: area.projects.map(project => ({
              ...project,
              id: crypto.randomUUID(),
              areaId: area.id, // Will be updated below
              tasks: project.tasks.map(task => ({
                ...task,
                id: crypto.randomUUID(),
                projectId: project.id, // Will be updated below
              }))
            }))
          }))
        };

        // Update IDs to maintain relationships
        duplicatedPillar.areas.forEach(area => {
          area.pillarId = duplicatedPillar.id;
          area.projects.forEach(project => {
            project.areaId = area.id;
            project.tasks.forEach(task => {
              task.projectId = project.id;
            });
          });
        });

        set(state => ({
          pillars: [...state.pillars, duplicatedPillar]
        }));
      },

      duplicateArea: (areaId) => {
        const state = get();
        for (const pillar of state.pillars) {
          const areaToDuplicate = pillar.areas.find(a => a.id === areaId);
          if (areaToDuplicate) {
            const duplicatedArea: Area = {
              ...areaToDuplicate,
              id: crypto.randomUUID(),
              name: `${areaToDuplicate.name} (Copy)`,
              projects: areaToDuplicate.projects.map(project => ({
                ...project,
                id: crypto.randomUUID(),
                areaId: areaToDuplicate.id, // Will be updated below
                tasks: project.tasks.map(task => ({
                  ...task,
                  id: crypto.randomUUID(),
                  projectId: project.id, // Will be updated below
                }))
              }))
            };

            // Update IDs to maintain relationships
            duplicatedArea.projects.forEach(project => {
              project.areaId = duplicatedArea.id;
              project.tasks.forEach(task => {
                task.projectId = project.id;
              });
            });

            set(state => ({
              pillars: state.pillars.map(p =>
                p.id === pillar.id
                  ? { ...p, areas: [...p.areas, duplicatedArea] }
                  : p
              )
            }));
            break;
          }
        }
      },

      duplicateProject: (projectId) => {
        const state = get();
        for (const pillar of state.pillars) {
          for (const area of pillar.areas) {
            const projectToDuplicate = area.projects.find(p => p.id === projectId);
            if (projectToDuplicate) {
              const duplicatedProject: Project = {
                ...projectToDuplicate,
                id: crypto.randomUUID(),
                name: `${projectToDuplicate.name} (Copy)`,
                tasks: projectToDuplicate.tasks.map(task => ({
                  ...task,
                  id: crypto.randomUUID(),
                  projectId: projectToDuplicate.id, // Will be updated below
                }))
              };

              // Update task project IDs
              duplicatedProject.tasks.forEach(task => {
                task.projectId = duplicatedProject.id;
              });

              set(state => ({
                pillars: state.pillars.map(p => ({
                  ...p,
                  areas: p.areas.map(a =>
                    a.id === area.id
                      ? { ...a, projects: [...a.projects, duplicatedProject] }
                      : a
                  )
                }))
              }));
              return;
            }
          }
        }
      },

      duplicateTask: (taskId) => {
        const state = get();
        for (const pillar of state.pillars) {
          for (const area of pillar.areas) {
            for (const project of area.projects) {
              const taskToDuplicate = project.tasks.find(t => t.id === taskId);
              if (taskToDuplicate) {
                const duplicatedTask: Task = {
                  ...taskToDuplicate,
                  id: crypto.randomUUID(),
                  name: `${taskToDuplicate.name} (Copy)`,
                  status: 'todo',
                  completedAt: undefined,
                  actualHours: undefined,
                };

                set(state => ({
                  pillars: state.pillars.map(p => ({
                    ...p,
                    areas: p.areas.map(a => ({
                      ...a,
                      projects: a.projects.map(pr =>
                        pr.id === project.id
                          ? { ...pr, tasks: [...pr.tasks, duplicatedTask] }
                          : pr
                      )
                    }))
                  }))
                }));
                return;
              }
            }
          }
        }
      },

      // Utility functions
      getPillarById: (pillarId) => {
        return get().pillars.find(pillar => pillar.id === pillarId);
      },

      getAreaById: (areaId) => {
        for (const pillar of get().pillars) {
          const area = pillar.areas.find(area => area.id === areaId);
          if (area) return area;
        }
        return undefined;
      },

      getProjectById: (projectId) => {
        for (const pillar of get().pillars) {
          for (const area of pillar.areas) {
            const project = area.projects.find(project => project.id === projectId);
            if (project) return project;
          }
        }
        return undefined;
      },

      getTaskById: (taskId) => {
        for (const pillar of get().pillars) {
          for (const area of pillar.areas) {
            for (const project of area.projects) {
              const task = project.tasks.find(task => task.id === taskId);
              if (task) return task;
            }
          }
        }
        return undefined;
      },

      getAreasByPillarId: (pillarId) => {
        const state = get();
        const pillar = state.pillars.find(p => p.id === pillarId);
        return pillar ? pillar.areas : [];
      },

      getProjectsByAreaId: (areaId) => {
        for (const pillar of get().pillars) {
          const area = pillar.areas.find(area => area.id === areaId);
          if (area) return area.projects;
        }
        return [];
      },

      getTasksByProjectId: (projectId) => {
        for (const pillar of get().pillars) {
          for (const area of pillar.areas) {
            const project = area.projects.find(project => project.id === projectId);
            if (project) return project.tasks;
          }
        }
        return [];
      },

      getAllAreas: () => {
        return get().pillars.flatMap(pillar => pillar.areas);
      },

      getAllProjects: () => {
        return get().pillars.flatMap(pillar => 
          pillar.areas.flatMap(area => area.projects)
        );
      },

      getAllTasks: () => {
        return get().pillars.flatMap(pillar => 
          pillar.areas.flatMap(area => 
            area.projects.flatMap(project => project.tasks)
          )
        );
      },
      
      getUnprocessedQuickCapture: () => {
        return get().quickCaptureItems.filter(item => !item.processed);
      },
      
      getTodaysTimeBlocks: () => {
        const today = new Date();
        return get().timeBlocks.filter(block => {
          const blockDate = new Date(block.startTime);
          return blockDate.toDateString() === today.toDateString();
        });
      },
      
      getPillarHealthTrend: (pillarId, days) => {
        const snapshots = get().progressSnapshots
          .filter(snapshot => {
            const snapshotDate = new Date(snapshot.date);
            const daysAgo = new Date();
            daysAgo.setDate(daysAgo.getDate() - days);
            return snapshotDate >= daysAgo;
          })
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
        
        return snapshots.map(snapshot => snapshot.pillarHealthScores[pillarId] || 0);
      },

      // File attachment management
      addProjectAttachment: (projectId, attachmentData) => {
        const newAttachment: ProjectAttachment = {
          ...attachmentData,
          id: crypto.randomUUID(),
          uploadedAt: new Date(),
        };

        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.map(area => ({
              ...area,
              projects: area.projects.map(project =>
                project.id === projectId
                  ? { ...project, attachments: [...project.attachments, newAttachment] }
                  : project
              )
            }))
          }))
        }));
      },

      removeProjectAttachment: (projectId, attachmentId) => {
        set(state => ({
          pillars: state.pillars.map(pillar => ({
            ...pillar,
            areas: pillar.areas.map(area => ({
              ...area,
              projects: area.projects.map(project =>
                project.id === projectId
                  ? { 
                      ...project, 
                      attachments: project.attachments.filter(att => att.id !== attachmentId) 
                    }
                  : project
              )
            }))
          }))
        }));
      },

      getProjectAttachments: (projectId) => {
        const state = get();
        for (const pillar of state.pillars) {
          for (const area of pillar.areas) {
            const project = area.projects.find(p => p.id === projectId);
            if (project) {
              return project.attachments;
            }
          }
        }
        return [];
      },
    }),
    {
      name: 'aurum-life-enhanced-features',
    }
  )
);