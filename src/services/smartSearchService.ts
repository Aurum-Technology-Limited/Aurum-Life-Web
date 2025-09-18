/**
 * Phase 2: Smart Search Service
 * Cross-hierarchy intelligent search with AI-powered suggestions
 */

interface SearchResult {
  id: string;
  type: 'pillar' | 'area' | 'project' | 'task' | 'journal' | 'note';
  title: string;
  description?: string;
  content?: string;
  hierarchy: {
    pillar?: string;
    area?: string;
    project?: string;
  };
  relevanceScore: number;
  matchedTerms: string[];
  lastModified: string;
  tags: string[];
  metadata?: Record<string, any>;
}

interface SearchFilters {
  types?: SearchResult['type'][];
  pillars?: string[];
  areas?: string[];
  projects?: string[];
  dateRange?: {
    start: Date;
    end: Date;
  };
  tags?: string[];
  priority?: string[];
  status?: string[];
  minRelevanceScore?: number;
}

interface SearchSuggestion {
  query: string;
  type: 'recent' | 'popular' | 'ai_suggested' | 'autocomplete';
  confidence: number;
  context?: string;
}

interface SearchAnalytics {
  query: string;
  timestamp: string;
  resultsCount: number;
  clickedResult?: string;
  filters?: SearchFilters;
}

class SmartSearchService {
  private searchIndex: Map<string, SearchResult> = new Map();
  private recentSearches: string[] = [];
  private popularSearches: Map<string, number> = new Map();
  private searchAnalytics: SearchAnalytics[] = [];
  private indexLastUpdated: string = new Date().toISOString();

  constructor() {
    this.loadSearchData();
    this.buildInitialIndex();
  }

  private loadSearchData() {
    try {
      const stored = localStorage.getItem('aurum-search-data');
      if (stored) {
        const data = JSON.parse(stored);
        this.recentSearches = data.recentSearches || [];
        this.popularSearches = new Map(data.popularSearches || []);
        this.searchAnalytics = data.searchAnalytics || [];
        this.indexLastUpdated = data.indexLastUpdated || new Date().toISOString();
      }
    } catch (error) {
      console.warn('Failed to load search data:', error);
    }
  }

  private saveSearchData() {
    try {
      const data = {
        recentSearches: this.recentSearches,
        popularSearches: Array.from(this.popularSearches.entries()),
        searchAnalytics: this.searchAnalytics.slice(-1000), // Keep last 1000 searches
        indexLastUpdated: this.indexLastUpdated
      };
      localStorage.setItem('aurum-search-data', JSON.stringify(data));
    } catch (error) {
      console.warn('Failed to save search data:', error);
    }
  }

  private async buildInitialIndex() {
    try {
      console.log('Building search index...');
      
      // Load data from various stores
      const pillars = await this.loadPillars();
      const areas = await this.loadAreas();
      const projects = await this.loadProjects();
      const tasks = await this.loadTasks();
      const journalEntries = await this.loadJournalEntries();
      
      // Index all items
      this.indexItems(pillars, 'pillar');
      this.indexItems(areas, 'area');
      this.indexItems(projects, 'project');
      this.indexItems(tasks, 'task');
      this.indexItems(journalEntries, 'journal');
      
      this.indexLastUpdated = new Date().toISOString();
      console.log(`Search index built with ${this.searchIndex.size} items`);
      
    } catch (error) {
      console.error('Failed to build search index:', error);
    }
  }

  private indexItems(items: any[], type: SearchResult['type']) {
    items.forEach(item => {
      const searchResult: SearchResult = {
        id: item.id,
        type,
        title: item.title || item.name,
        description: item.description,
        content: item.content || item.notes,
        hierarchy: this.buildHierarchy(item, type),
        relevanceScore: 1.0,
        matchedTerms: [],
        lastModified: item.updatedAt || item.createdAt || new Date().toISOString(),
        tags: item.tags || [],
        metadata: {
          priority: item.priority,
          status: item.status,
          dueDate: item.dueDate,
          completedAt: item.completedAt
        }
      };
      
      this.searchIndex.set(item.id, searchResult);
    });
  }

  private buildHierarchy(item: any, type: SearchResult['type']) {
    const hierarchy: SearchResult['hierarchy'] = {};
    
    switch (type) {
      case 'task':
        hierarchy.project = item.projectId;
        hierarchy.area = item.areaId;
        hierarchy.pillar = item.pillarId;
        break;
      case 'project':
        hierarchy.area = item.areaId;
        hierarchy.pillar = item.pillarId;
        break;
      case 'area':
        hierarchy.pillar = item.pillarId;
        break;
      case 'pillar':
        // Pillars are top-level
        break;
      case 'journal':
        // Journal entries might be tagged with pillars
        hierarchy.pillar = item.pillarId;
        break;
    }
    
    return hierarchy;
  }

  /**
   * Perform intelligent search across all content
   */
  async search(query: string, filters?: SearchFilters): Promise<SearchResult[]> {
    const normalizedQuery = this.normalizeQuery(query);
    const searchTerms = this.extractSearchTerms(normalizedQuery);
    
    // Record search analytics
    this.recordSearch(query, filters);
    
    if (searchTerms.length === 0) {
      return [];
    }
    
    let results: SearchResult[] = [];
    
    // Search through index
    for (const [id, item] of this.searchIndex.entries()) {
      const relevanceScore = this.calculateRelevanceScore(item, searchTerms, query);
      
      if (relevanceScore > 0) {
        const result = {
          ...item,
          relevanceScore,
          matchedTerms: this.findMatchedTerms(item, searchTerms)
        };
        results.push(result);
      }
    }
    
    // Apply filters
    if (filters) {
      results = this.applyFilters(results, filters);
    }
    
    // Sort by relevance score
    results.sort((a, b) => b.relevanceScore - a.relevanceScore);
    
    // Limit results
    return results.slice(0, 50);
  }

  /**
   * Get AI-powered search suggestions
   */
  async getSearchSuggestions(partialQuery: string): Promise<SearchSuggestion[]> {
    const suggestions: SearchSuggestion[] = [];
    const normalizedQuery = partialQuery.toLowerCase().trim();
    
    if (normalizedQuery.length < 2) {
      // Show recent searches for short queries
      return this.recentSearches.slice(-5).map(query => ({
        query,
        type: 'recent' as const,
        confidence: 0.8
      }));
    }
    
    // Autocomplete suggestions from index
    const autocompleteTerms = this.getAutocompleteTerms(normalizedQuery);
    autocompleteTerms.forEach(term => {
      suggestions.push({
        query: term,
        type: 'autocomplete',
        confidence: 0.7
      });
    });
    
    // Popular searches that match
    for (const [query, count] of this.popularSearches.entries()) {
      if (query.toLowerCase().includes(normalizedQuery)) {
        suggestions.push({
          query,
          type: 'popular',
          confidence: Math.min(count / 10, 1.0)
        });
      }
    }
    
    // AI-generated contextual suggestions
    const aiSuggestions = await this.generateAISuggestions(normalizedQuery);
    suggestions.push(...aiSuggestions);
    
    // Remove duplicates and sort by confidence
    const uniqueSuggestions = suggestions
      .filter((suggestion, index, self) => 
        index === self.findIndex(s => s.query === suggestion.query)
      )
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 8);
    
    return uniqueSuggestions;
  }

  /**
   * Get semantic search results using AI understanding
   */
  async semanticSearch(query: string, context?: string): Promise<SearchResult[]> {
    // This would integrate with an AI service for semantic understanding
    const semanticTerms = await this.generateSemanticTerms(query, context);
    
    // Combine original query with semantic terms
    const expandedQuery = `${query} ${semanticTerms.join(' ')}`;
    
    return this.search(expandedQuery);
  }

  /**
   * Search within a specific hierarchy level
   */
  async hierarchySearch(query: string, hierarchy: Partial<SearchResult['hierarchy']>): Promise<SearchResult[]> {
    const filters: SearchFilters = {};
    
    if (hierarchy.pillar) {
      filters.pillars = [hierarchy.pillar];
    }
    if (hierarchy.area) {
      filters.areas = [hierarchy.area];
    }
    if (hierarchy.project) {
      filters.projects = [hierarchy.project];
    }
    
    return this.search(query, filters);
  }

  /**
   * Get trending search terms
   */
  getTrendingSearches(limit: number = 10): Array<{query: string; count: number}> {
    return Array.from(this.popularSearches.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([query, count]) => ({ query, count }));
  }

  /**
   * Update search index with new or modified item
   */
  updateIndex(item: any, type: SearchResult['type']) {
    const searchResult: SearchResult = {
      id: item.id,
      type,
      title: item.title || item.name,
      description: item.description,
      content: item.content || item.notes,
      hierarchy: this.buildHierarchy(item, type),
      relevanceScore: 1.0,
      matchedTerms: [],
      lastModified: new Date().toISOString(),
      tags: item.tags || [],
      metadata: {
        priority: item.priority,
        status: item.status,
        dueDate: item.dueDate,
        completedAt: item.completedAt
      }
    };
    
    this.searchIndex.set(item.id, searchResult);
    this.indexLastUpdated = new Date().toISOString();
  }

  /**
   * Remove item from search index
   */
  removeFromIndex(itemId: string) {
    this.searchIndex.delete(itemId);
    this.indexLastUpdated = new Date().toISOString();
  }

  // Private helper methods

  private normalizeQuery(query: string): string {
    return query.toLowerCase().trim().replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ');
  }

  private extractSearchTerms(query: string): string[] {
    return query.split(' ').filter(term => term.length > 1);
  }

  private calculateRelevanceScore(item: SearchResult, searchTerms: string[], originalQuery: string): number {
    let score = 0;
    const itemTextLower = `${item.title} ${item.description || ''} ${item.content || ''}`.toLowerCase();
    
    // Exact phrase match gets highest score
    if (itemTextLower.includes(originalQuery.toLowerCase())) {
      score += 10;
    }
    
    // Title matches get high score
    if (item.title.toLowerCase().includes(originalQuery.toLowerCase())) {
      score += 8;
    }
    
    // Individual term matches
    searchTerms.forEach(term => {
      if (item.title.toLowerCase().includes(term)) {
        score += 5;
      }
      if (item.description?.toLowerCase().includes(term)) {
        score += 3;
      }
      if (item.content?.toLowerCase().includes(term)) {
        score += 2;
      }
      if (item.tags.some(tag => tag.toLowerCase().includes(term))) {
        score += 4;
      }
    });
    
    // Boost recent items
    const daysSinceModified = (Date.now() - new Date(item.lastModified).getTime()) / (24 * 60 * 60 * 1000);
    if (daysSinceModified < 7) {
      score += 2;
    } else if (daysSinceModified < 30) {
      score += 1;
    }
    
    // Boost items with higher status/priority
    if (item.metadata?.priority === 'high') {
      score += 1;
    }
    if (item.metadata?.status === 'active' || item.metadata?.status === 'in_progress') {
      score += 1;
    }
    
    return score;
  }

  private findMatchedTerms(item: SearchResult, searchTerms: string[]): string[] {
    const itemText = `${item.title} ${item.description || ''} ${item.content || ''}`.toLowerCase();
    return searchTerms.filter(term => itemText.includes(term));
  }

  private applyFilters(results: SearchResult[], filters: SearchFilters): SearchResult[] {
    return results.filter(result => {
      // Type filter
      if (filters.types && !filters.types.includes(result.type)) {
        return false;
      }
      
      // Hierarchy filters
      if (filters.pillars && result.hierarchy.pillar && !filters.pillars.includes(result.hierarchy.pillar)) {
        return false;
      }
      if (filters.areas && result.hierarchy.area && !filters.areas.includes(result.hierarchy.area)) {
        return false;
      }
      if (filters.projects && result.hierarchy.project && !filters.projects.includes(result.hierarchy.project)) {
        return false;
      }
      
      // Date range filter
      if (filters.dateRange) {
        const itemDate = new Date(result.lastModified);
        if (itemDate < filters.dateRange.start || itemDate > filters.dateRange.end) {
          return false;
        }
      }
      
      // Tags filter
      if (filters.tags && !filters.tags.some(tag => result.tags.includes(tag))) {
        return false;
      }
      
      // Priority filter
      if (filters.priority && result.metadata?.priority && !filters.priority.includes(result.metadata.priority)) {
        return false;
      }
      
      // Status filter
      if (filters.status && result.metadata?.status && !filters.status.includes(result.metadata.status)) {
        return false;
      }
      
      // Minimum relevance score
      if (filters.minRelevanceScore && result.relevanceScore < filters.minRelevanceScore) {
        return false;
      }
      
      return true;
    });
  }

  private getAutocompleteTerms(partialQuery: string): string[] {
    const terms: Set<string> = new Set();
    
    for (const [id, item] of this.searchIndex.entries()) {
      const allText = `${item.title} ${item.description || ''} ${item.tags.join(' ')}`.toLowerCase();
      const words = allText.split(/\s+/);
      
      words.forEach(word => {
        if (word.startsWith(partialQuery) && word.length > partialQuery.length) {
          terms.add(word);
        }
      });
    }
    
    return Array.from(terms).slice(0, 5);
  }

  private async generateAISuggestions(query: string): Promise<SearchSuggestion[]> {
    // Simulate AI-generated suggestions based on query context
    const suggestions: SearchSuggestion[] = [];
    
    // Context-aware suggestions
    if (query.includes('task') || query.includes('todo')) {
      suggestions.push({
        query: 'incomplete tasks',
        type: 'ai_suggested',
        confidence: 0.8,
        context: 'You might be looking for unfinished work'
      });
      suggestions.push({
        query: 'overdue tasks',
        type: 'ai_suggested',
        confidence: 0.7,
        context: 'Tasks that need immediate attention'
      });
    }
    
    if (query.includes('meeting') || query.includes('calendar')) {
      suggestions.push({
        query: 'upcoming meetings',
        type: 'ai_suggested',
        confidence: 0.8,
        context: 'Your scheduled meetings'
      });
    }
    
    if (query.includes('goal') || query.includes('objective')) {
      suggestions.push({
        query: 'goal progress',
        type: 'ai_suggested',
        confidence: 0.9,
        context: 'Track your goal achievements'
      });
    }
    
    return suggestions;
  }

  private async generateSemanticTerms(query: string, context?: string): Promise<string[]> {
    // This would use an AI service to generate semantically related terms
    // For now, using a simple rule-based approach
    const semanticMap: Record<string, string[]> = {
      'task': ['todo', 'assignment', 'work', 'action', 'item'],
      'project': ['initiative', 'endeavor', 'plan', 'program'],
      'goal': ['objective', 'target', 'aim', 'aspiration'],
      'meeting': ['call', 'conference', 'discussion', 'session'],
      'deadline': ['due', 'urgent', 'time-sensitive', 'expiring'],
      'complete': ['finished', 'done', 'accomplished', 'achieved']
    };
    
    const terms: string[] = [];
    const queryWords = query.toLowerCase().split(' ');
    
    queryWords.forEach(word => {
      if (semanticMap[word]) {
        terms.push(...semanticMap[word]);
      }
    });
    
    return terms;
  }

  private recordSearch(query: string, filters?: SearchFilters) {
    // Update recent searches
    this.recentSearches = this.recentSearches.filter(q => q !== query);
    this.recentSearches.push(query);
    if (this.recentSearches.length > 20) {
      this.recentSearches.shift();
    }
    
    // Update popular searches
    const currentCount = this.popularSearches.get(query) || 0;
    this.popularSearches.set(query, currentCount + 1);
    
    // Record analytics
    this.searchAnalytics.push({
      query,
      timestamp: new Date().toISOString(),
      resultsCount: 0, // Will be updated when results are returned
      filters
    });
    
    this.saveSearchData();
  }

  private async loadPillars(): Promise<any[]> {
    try {
      const stored = localStorage.getItem('aurum-pillars');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  private async loadAreas(): Promise<any[]> {
    try {
      const stored = localStorage.getItem('aurum-areas');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  private async loadProjects(): Promise<any[]> {
    try {
      const stored = localStorage.getItem('aurum-projects');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  private async loadTasks(): Promise<any[]> {
    try {
      const stored = localStorage.getItem('aurum-tasks');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  private async loadJournalEntries(): Promise<any[]> {
    try {
      const stored = localStorage.getItem('aurum-journal-entries');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  /**
   * Force rebuild the search index
   */
  async rebuildIndex() {
    this.searchIndex.clear();
    await this.buildInitialIndex();
  }

  /**
   * Get index statistics
   */
  getIndexStats() {
    const typeCount: Record<string, number> = {};
    
    for (const [id, item] of this.searchIndex.entries()) {
      typeCount[item.type] = (typeCount[item.type] || 0) + 1;
    }
    
    return {
      totalItems: this.searchIndex.size,
      typeBreakdown: typeCount,
      lastUpdated: this.indexLastUpdated,
      recentSearches: this.recentSearches.length,
      popularSearches: this.popularSearches.size
    };
  }
}

export const smartSearchService = new SmartSearchService();
export type { SearchResult, SearchFilters, SearchSuggestion, SearchAnalytics };