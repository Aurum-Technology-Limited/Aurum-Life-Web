import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface JournalEntry {
  id: string;
  title: string;
  content: string;
  date: Date;
  mood: 'excited' | 'positive' | 'neutral' | 'thoughtful' | 'challenging' | 'grateful' | 'motivated' | 'accomplished' | 'peaceful' | 'energized';
  energy: 1 | 2 | 3 | 4 | 5; // 1 = low, 5 = high
  tags: string[];
  pillarId?: string;
  areaId?: string;
  projectId?: string;
  weather?: string;
  location?: string;
  createdAt: Date;
  updatedAt: Date;
  wordCount: number;
  isPrivate: boolean;
  attachments?: string[]; // URLs to attached images/files
  templateUsed?: string;
}

export interface JournalTemplate {
  id: string;
  name: string;
  description: string;
  prompts: string[];
  category: 'daily' | 'gratitude' | 'reflection' | 'goal-setting' | 'problem-solving' | 'creative' | 'custom';
  icon: string;
}

export interface JournalInsight {
  id: string;
  type: 'mood-pattern' | 'energy-correlation' | 'pillar-focus' | 'growth-trend' | 'habit-insight' | 'goal-progress';
  title: string;
  description: string;
  data: any;
  generatedAt: Date;
  actionable: boolean;
  dismissed: boolean;
}

export interface JournalStats {
  totalEntries: number;
  currentStreak: number;
  longestStreak: number;
  averageWordsPerEntry: number;
  mostUsedMoods: Array<{ mood: string; count: number }>;
  mostUsedTags: Array<{ tag: string; count: number }>;
  entriesThisMonth: number;
  entriesThisWeek: number;
  pillarFocus: Array<{ pillarId: string; pillarName: string; count: number }>;
}

interface JournalState {
  // Core state
  entries: JournalEntry[];
  templates: JournalTemplate[];
  insights: JournalInsight[];
  currentEntry: JournalEntry | null;
  
  // UI state
  isEntryModalOpen: boolean;
  isEditMode: boolean;
  selectedDate: Date | null;
  searchQuery: string;
  selectedMoodFilter: string | null;
  selectedPillarFilter: string | null;
  selectedTagFilter: string | null;
  sortBy: 'date' | 'mood' | 'title' | 'wordCount';
  sortOrder: 'asc' | 'desc';
  viewMode: 'list' | 'grid' | 'calendar';
  
  // Actions
  // Entry management
  createEntry: (entry: Omit<JournalEntry, 'id' | 'createdAt' | 'updatedAt' | 'wordCount'>) => void;
  updateEntry: (entryId: string, updates: Partial<JournalEntry>) => void;
  deleteEntry: (entryId: string) => void;
  duplicateEntry: (entryId: string) => void;
  
  // Template management
  createTemplate: (template: Omit<JournalTemplate, 'id'>) => void;
  updateTemplate: (templateId: string, updates: Partial<JournalTemplate>) => void;
  deleteTemplate: (templateId: string) => void;
  
  // UI actions
  openEntryModal: (entry?: JournalEntry, template?: JournalTemplate) => void;
  closeEntryModal: () => void;
  setEditMode: (isEdit: boolean) => void;
  setSelectedDate: (date: Date | null) => void;
  setSearchQuery: (query: string) => void;
  setMoodFilter: (mood: string | null) => void;
  setPillarFilter: (pillarId: string | null) => void;
  setTagFilter: (tag: string | null) => void;
  setSortBy: (sortBy: 'date' | 'mood' | 'title' | 'wordCount') => void;
  setSortOrder: (order: 'asc' | 'desc') => void;
  setViewMode: (mode: 'list' | 'grid' | 'calendar') => void;
  
  // Analytics
  generateInsights: () => void;
  dismissInsight: (insightId: string) => void;
  getStats: () => JournalStats;
  getEntriesForDate: (date: Date) => JournalEntry[];
  getEntriesForDateRange: (startDate: Date, endDate: Date) => JournalEntry[];
  getFilteredEntries: () => JournalEntry[];
  getMoodTrend: (days: number) => Array<{ date: string; mood: string; energy: number }>;
  getWordCountTrend: (days: number) => Array<{ date: string; wordCount: number }>;
  
  // Utility
  getEntryById: (entryId: string) => JournalEntry | undefined;
  getTemplateById: (templateId: string) => JournalTemplate | undefined;
  getAllTags: () => string[];
  getMoodColors: (mood: string) => { bg: string; text: string; border: string };
}

const defaultTemplates: JournalTemplate[] = [
  {
    id: 'daily-reflection',
    name: 'Daily Reflection',
    description: 'A simple daily check-in to reflect on your day',
    prompts: [
      'What were the highlights of my day?',
      'What challenges did I face and how did I handle them?',
      'What am I grateful for today?',
      'What would I do differently?',
      'How am I feeling right now?'
    ],
    category: 'daily',
    icon: '📝'
  },
  {
    id: 'gratitude-practice',
    name: 'Gratitude Practice',
    description: 'Focus on appreciation and positive moments',
    prompts: [
      'Three things I\'m grateful for today:',
      'Someone who made my day better:',
      'A small moment that brought me joy:',
      'Something about myself I appreciate:',
      'How can I express gratitude tomorrow?'
    ],
    category: 'gratitude',
    icon: '🙏'
  },
  {
    id: 'goal-progress',
    name: 'Goal Progress Review',
    description: 'Track your progress toward important goals',
    prompts: [
      'Which goals did I make progress on today?',
      'What obstacles am I facing?',
      'What actions can I take tomorrow?',
      'How do I feel about my current trajectory?',
      'What support or resources do I need?'
    ],
    category: 'goal-setting',
    icon: '🎯'
  },
  {
    id: 'creative-exploration',
    name: 'Creative Exploration',
    description: 'Free-form creative writing and idea generation',
    prompts: [
      'What\'s sparking my creativity today?',
      'An idea I want to explore:',
      'If I could create anything, it would be:',
      'What inspires me right now?',
      'How can I nurture my creative side?'
    ],
    category: 'creative',
    icon: '🎨'
  },
  {
    id: 'problem-solving',
    name: 'Problem Solving Session',
    description: 'Work through challenges and find solutions',
    prompts: [
      'What problem am I trying to solve?',
      'What information do I have?',
      'What are possible solutions?',
      'What would success look like?',
      'What\'s my next step?'
    ],
    category: 'problem-solving',
    icon: '🧩'
  }
];

export const useJournalStore = create<JournalState>()(
  persist(
    (set, get) => ({
      // Initial state
      entries: [],
      templates: defaultTemplates,
      insights: [],
      currentEntry: null,
      isEntryModalOpen: false,
      isEditMode: false,
      selectedDate: null,
      searchQuery: '',
      selectedMoodFilter: null,
      selectedPillarFilter: null,
      selectedTagFilter: null,
      sortBy: 'date',
      sortOrder: 'desc',
      viewMode: 'list',

      // Entry management actions
      createEntry: (entryData) => {
        const newEntry: JournalEntry = {
          ...entryData,
          id: crypto.randomUUID(),
          createdAt: new Date(),
          updatedAt: new Date(),
          wordCount: entryData.content.trim().split(/\s+/).length,
        };
        
        set(state => ({
          entries: [newEntry, ...state.entries]
        }));
      },

      updateEntry: (entryId, updates) => {
        set(state => ({
          entries: state.entries.map(entry =>
            entry.id === entryId
              ? {
                  ...entry,
                  ...updates,
                  updatedAt: new Date(),
                  wordCount: updates.content ? updates.content.trim().split(/\s+/).length : entry.wordCount
                }
              : entry
          )
        }));
      },

      deleteEntry: (entryId) => {
        set(state => ({
          entries: state.entries.filter(entry => entry.id !== entryId)
        }));
      },

      duplicateEntry: (entryId) => {
        const state = get();
        const entryToDuplicate = state.entries.find(e => e.id === entryId);
        if (!entryToDuplicate) return;

        const duplicatedEntry: JournalEntry = {
          ...entryToDuplicate,
          id: crypto.randomUUID(),
          title: `${entryToDuplicate.title} (Copy)`,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        set(state => ({
          entries: [duplicatedEntry, ...state.entries]
        }));
      },

      // Template management
      createTemplate: (templateData) => {
        const newTemplate: JournalTemplate = {
          ...templateData,
          id: crypto.randomUUID(),
        };
        
        set(state => ({
          templates: [...state.templates, newTemplate]
        }));
      },

      updateTemplate: (templateId, updates) => {
        set(state => ({
          templates: state.templates.map(template =>
            template.id === templateId ? { ...template, ...updates } : template
          )
        }));
      },

      deleteTemplate: (templateId) => {
        set(state => ({
          templates: state.templates.filter(template => template.id !== templateId)
        }));
      },

      // UI actions
      openEntryModal: (entry, template) => {
        const currentDate = new Date();
        
        if (entry) {
          set({ 
            currentEntry: entry, 
            isEntryModalOpen: true, 
            isEditMode: true 
          });
        } else if (template) {
          // Create new entry from template
          const newEntry: JournalEntry = {
            id: crypto.randomUUID(),
            title: `${template.name} - ${currentDate.toLocaleDateString()}`,
            content: template.prompts.map(prompt => `**${prompt}**\n\n`).join('\n'),
            date: currentDate,
            mood: 'neutral',
            energy: 3,
            tags: [template.category],
            createdAt: currentDate,
            updatedAt: currentDate,
            wordCount: 0,
            isPrivate: false,
            templateUsed: template.id
          };
          set({ 
            currentEntry: newEntry, 
            isEntryModalOpen: true, 
            isEditMode: false 
          });
        } else {
          // Create blank entry
          const newEntry: JournalEntry = {
            id: crypto.randomUUID(),
            title: `Journal Entry - ${currentDate.toLocaleDateString()}`,
            content: '',
            date: currentDate,
            mood: 'neutral',
            energy: 3,
            tags: [],
            createdAt: currentDate,
            updatedAt: currentDate,
            wordCount: 0,
            isPrivate: false
          };
          set({ 
            currentEntry: newEntry, 
            isEntryModalOpen: true, 
            isEditMode: false 
          });
        }
      },

      closeEntryModal: () => {
        set({ 
          currentEntry: null, 
          isEntryModalOpen: false, 
          isEditMode: false 
        });
      },

      setEditMode: (isEdit) => set({ isEditMode: isEdit }),
      setSelectedDate: (date) => set({ selectedDate: date }),
      setSearchQuery: (query) => set({ searchQuery: query }),
      setMoodFilter: (mood) => set({ selectedMoodFilter: mood }),
      setPillarFilter: (pillarId) => set({ selectedPillarFilter: pillarId }),
      setTagFilter: (tag) => set({ selectedTagFilter: tag }),
      setSortBy: (sortBy) => set({ sortBy }),
      setSortOrder: (order) => set({ sortOrder: order }),
      setViewMode: (mode) => set({ viewMode: mode }),

      // Analytics
      generateInsights: () => {
        const state = get();
        const entries = state.entries;
        const insights: JournalInsight[] = [];

        // Mood pattern insight
        if (entries.length >= 7) {
          const recentEntries = entries.slice(0, 7);
          const moodCounts = recentEntries.reduce((acc, entry) => {
            acc[entry.mood] = (acc[entry.mood] || 0) + 1;
            return acc;
          }, {} as Record<string, number>);
          
          const dominantMood = Object.entries(moodCounts)
            .sort(([,a], [,b]) => b - a)[0];

          insights.push({
            id: crypto.randomUUID(),
            type: 'mood-pattern',
            title: 'Weekly Mood Pattern',
            description: `Your dominant mood this week has been "${dominantMood[0]}" appearing in ${dominantMood[1]} out of ${recentEntries.length} entries.`,
            data: moodCounts,
            generatedAt: new Date(),
            actionable: true,
            dismissed: false
          });
        }

        // Writing consistency insight
        const thisMonth = new Date();
        const startOfMonth = new Date(thisMonth.getFullYear(), thisMonth.getMonth(), 1);
        const entriesThisMonth = entries.filter(entry => 
          new Date(entry.date) >= startOfMonth
        );

        if (entriesThisMonth.length > 0) {
          const avgWordsPerEntry = entriesThisMonth.reduce((sum, entry) => sum + entry.wordCount, 0) / entriesThisMonth.length;
          
          insights.push({
            id: crypto.randomUUID(),
            type: 'growth-trend',
            title: 'Writing Growth',
            description: `This month you've written ${entriesThisMonth.length} entries with an average of ${Math.round(avgWordsPerEntry)} words per entry.`,
            data: { entriesCount: entriesThisMonth.length, avgWords: avgWordsPerEntry },
            generatedAt: new Date(),
            actionable: false,
            dismissed: false
          });
        }

        set(state => ({
          insights: [...insights, ...state.insights.filter(i => !insights.some(ni => ni.type === i.type))]
        }));
      },

      dismissInsight: (insightId) => {
        set(state => ({
          insights: state.insights.map(insight =>
            insight.id === insightId ? { ...insight, dismissed: true } : insight
          )
        }));
      },

      // Analytics getters
      getStats: () => {
        const state = get();
        const entries = state.entries;
        
        // Calculate streak
        let currentStreak = 0;
        let longestStreak = 0;
        let tempStreak = 0;
        
        const sortedEntries = [...entries].sort((a, b) => 
          new Date(b.date).getTime() - new Date(a.date).getTime()
        );
        
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        // Check if there's an entry today or yesterday to start streak
        if (sortedEntries.length > 0) {
          const lastEntryDate = new Date(sortedEntries[0].date);
          if (lastEntryDate.toDateString() === today.toDateString() || 
              lastEntryDate.toDateString() === yesterday.toDateString()) {
            currentStreak = 1;
            tempStreak = 1;
          }
        }
        
        // Calculate streaks
        for (let i = 1; i < sortedEntries.length; i++) {
          const currentDate = new Date(sortedEntries[i-1].date);
          const previousDate = new Date(sortedEntries[i].date);
          const diffTime = currentDate.getTime() - previousDate.getTime();
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          
          if (diffDays === 1) {
            tempStreak++;
            if (i === 1) currentStreak = tempStreak;
          } else {
            longestStreak = Math.max(longestStreak, tempStreak);
            if (i === 1) currentStreak = 0;
            tempStreak = 1;
          }
        }
        longestStreak = Math.max(longestStreak, tempStreak);

        // Mood analysis
        const moodCounts = entries.reduce((acc, entry) => {
          acc[entry.mood] = (acc[entry.mood] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);
        
        const mostUsedMoods = Object.entries(moodCounts)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 5)
          .map(([mood, count]) => ({ mood, count }));

        // Tag analysis
        const tagCounts = entries.reduce((acc, entry) => {
          entry.tags.forEach(tag => {
            acc[tag] = (acc[tag] || 0) + 1;
          });
          return acc;
        }, {} as Record<string, number>);
        
        const mostUsedTags = Object.entries(tagCounts)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 10)
          .map(([tag, count]) => ({ tag, count }));

        // Time-based counts
        const thisWeek = new Date();
        thisWeek.setDate(thisWeek.getDate() - 7);
        const thisMonth = new Date();
        thisMonth.setDate(thisMonth.getDate() - 30);
        
        const entriesThisWeek = entries.filter(entry => new Date(entry.date) >= thisWeek).length;
        const entriesThisMonth = entries.filter(entry => new Date(entry.date) >= thisMonth).length;

        return {
          totalEntries: entries.length,
          currentStreak,
          longestStreak,
          averageWordsPerEntry: entries.length > 0 ? entries.reduce((sum, entry) => sum + entry.wordCount, 0) / entries.length : 0,
          mostUsedMoods,
          mostUsedTags,
          entriesThisMonth,
          entriesThisWeek,
          pillarFocus: [] // Will be populated when integrated with pillar system
        };
      },

      getEntriesForDate: (date) => {
        const state = get();
        return state.entries.filter(entry => 
          new Date(entry.date).toDateString() === date.toDateString()
        );
      },

      getEntriesForDateRange: (startDate, endDate) => {
        const state = get();
        return state.entries.filter(entry => {
          const entryDate = new Date(entry.date);
          return entryDate >= startDate && entryDate <= endDate;
        });
      },

      getFilteredEntries: () => {
        const state = get();
        let filtered = [...state.entries];

        // Apply search filter
        if (state.searchQuery) {
          const query = state.searchQuery.toLowerCase();
          filtered = filtered.filter(entry =>
            entry.title.toLowerCase().includes(query) ||
            entry.content.toLowerCase().includes(query) ||
            entry.tags.some(tag => tag.toLowerCase().includes(query))
          );
        }

        // Apply mood filter
        if (state.selectedMoodFilter) {
          filtered = filtered.filter(entry => entry.mood === state.selectedMoodFilter);
        }

        // Apply pillar filter
        if (state.selectedPillarFilter) {
          filtered = filtered.filter(entry => entry.pillarId === state.selectedPillarFilter);
        }

        // Apply tag filter
        if (state.selectedTagFilter) {
          filtered = filtered.filter(entry => entry.tags.includes(state.selectedTagFilter));
        }

        // Apply date filter
        if (state.selectedDate) {
          filtered = filtered.filter(entry =>
            new Date(entry.date).toDateString() === state.selectedDate!.toDateString()
          );
        }

        // Apply sorting
        filtered.sort((a, b) => {
          let aVal, bVal;
          
          switch (state.sortBy) {
            case 'date':
              aVal = new Date(a.date).getTime();
              bVal = new Date(b.date).getTime();
              break;
            case 'mood':
              aVal = a.mood;
              bVal = b.mood;
              break;
            case 'title':
              aVal = a.title.toLowerCase();
              bVal = b.title.toLowerCase();
              break;
            case 'wordCount':
              aVal = a.wordCount;
              bVal = b.wordCount;
              break;
            default:
              aVal = new Date(a.date).getTime();
              bVal = new Date(b.date).getTime();
          }

          if (state.sortOrder === 'asc') {
            return aVal > bVal ? 1 : -1;
          } else {
            return aVal < bVal ? 1 : -1;
          }
        });

        return filtered;
      },

      getMoodTrend: (days) => {
        const state = get();
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days);
        
        return state.entries
          .filter(entry => new Date(entry.date) >= cutoffDate)
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
          .map(entry => ({
            date: new Date(entry.date).toISOString().split('T')[0],
            mood: entry.mood,
            energy: entry.energy
          }));
      },

      getWordCountTrend: (days) => {
        const state = get();
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days);
        
        return state.entries
          .filter(entry => new Date(entry.date) >= cutoffDate)
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
          .map(entry => ({
            date: new Date(entry.date).toISOString().split('T')[0],
            wordCount: entry.wordCount
          }));
      },

      // Utility functions
      getEntryById: (entryId) => {
        return get().entries.find(entry => entry.id === entryId);
      },

      getTemplateById: (templateId) => {
        return get().templates.find(template => template.id === templateId);
      },

      getAllTags: () => {
        const state = get();
        const allTags = state.entries.flatMap(entry => entry.tags);
        return [...new Set(allTags)].sort();
      },

      getMoodColors: (mood) => {
        const moodColorMap = {
          excited: { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/30' },
          positive: { bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/30' },
          neutral: { bg: 'bg-gray-500/10', text: 'text-gray-400', border: 'border-gray-500/30' },
          thoughtful: { bg: 'bg-purple-500/10', text: 'text-purple-400', border: 'border-purple-500/30' },
          challenging: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30' },
          grateful: { bg: 'bg-pink-500/10', text: 'text-pink-400', border: 'border-pink-500/30' },
          motivated: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/30' },
          accomplished: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/30' },
          peaceful: { bg: 'bg-teal-500/10', text: 'text-teal-400', border: 'border-teal-500/30' },
          energized: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30' }
        };
        
        return moodColorMap[mood as keyof typeof moodColorMap] || moodColorMap.neutral;
      }
    }),
    {
      name: 'aurum-life-journal',
    }
  )
);