import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Search, 
  Brain, 
  BookOpen, 
  CheckSquare, 
  Folder, 
  Sun, 
  Circle,
  ArrowRight,
  Loader2,
  Filter,
  X,
  Sparkles,
  TrendingUp,
  Clock
} from 'lucide-react';
import { semanticSearchAPI } from '../services/api';

const SemanticSearch = ({ isOpen, onClose, onResultSelect, placeholder = "Find content by meaning..." }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchMetadata, setSearchMetadata] = useState(null);
  const [filters, setFilters] = useState({
    contentTypes: ['all'],
    minSimilarity: 0.3,
    dateRangeDays: null
  });
  const [showFilters, setShowFilters] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const inputRef = useRef(null);
  const searchTimeoutRef = useRef(null);

  // Load recent searches on mount
  useEffect(() => {
    if (isOpen) {
      console.log('🔍 Semantic search modal opened, loading recent searches...');
      const recent = JSON.parse(localStorage.getItem('semantic_recent_searches') || '[]');
      setRecentSearches(recent.slice(0, 5));
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      console.log('🔍 Semantic search modal closed');
    }
  }, [isOpen]);

  // Debounced search
  useEffect(() => {
    if (query.trim().length > 2) {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
      
      searchTimeoutRef.current = setTimeout(() => {
        performSearch(query);
      }, 500);
    } else {
      setResults([]);
      setSearchMetadata(null);
    }

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [query, filters]);

  const performSearch = async (searchQuery) => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const response = await semanticSearchAPI.search(
        searchQuery,
        filters.contentTypes,
        10,
        filters.minSimilarity,
        filters.dateRangeDays
      );

      setResults(response.results || []);
      setSearchMetadata(response.search_metadata);

      // Save to recent searches
      const newSearch = { query: searchQuery, timestamp: Date.now() };
      const updatedRecent = [newSearch, ...recentSearches.filter(s => s.query !== searchQuery)].slice(0, 5);
      setRecentSearches(updatedRecent);
      localStorage.setItem('semantic_recent_searches', JSON.stringify(updatedRecent));

    } catch (error) {
      console.error('Semantic search failed:', error);
      setResults([]);
      setSearchMetadata(null);
    } finally {
      setIsSearching(false);
    }
  };

  const handleResultClick = (result) => {
    if (onResultSelect) {
      onResultSelect(result);
    }
    onClose();
  };

  const handleRecentSearchClick = (recentQuery) => {
    setQuery(recentQuery);
    inputRef.current?.focus();
  };

  const getEntityIcon = (entityType) => {
    const icons = {
      journal_entry: BookOpen,
      task: CheckSquare,
      project: Folder,
      daily_reflection: Sun,
      ai_insight: Brain
    };
    return icons[entityType] || Circle;
  };

  const getConfidenceColor = (level) => {
    const colors = {
      high: 'text-green-400 bg-green-400/10',
      medium: 'text-yellow-400 bg-yellow-400/10',
      low: 'text-orange-400 bg-orange-400/10'
    };
    return colors[level] || colors.low;
  };

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Escape') {
      onClose();
    }
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-start justify-center z-50 pt-24">
      <div className="bg-gray-900/95 border border-gray-700 rounded-xl shadow-2xl w-full max-w-4xl mx-4 max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center gap-3 p-4 border-b border-gray-700">
          <div className="p-2 bg-purple-600 rounded-lg">
            <Brain className="h-5 w-5 text-white" />
          </div>
          <div className="flex-1">
            <h2 className="font-semibold text-white">Semantic Search</h2>
            <p className="text-sm text-gray-400">Find content by meaning and context</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2 rounded-lg transition-colors ${
                showFilters ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
              title="Search filters"
            >
              <Filter className="h-4 w-4" />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Search Input */}
        <div className="p-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={placeholder}
              className="w-full bg-gray-800 border border-gray-600 rounded-lg pl-12 pr-12 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
              disabled={isSearching}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
              {isSearching ? (
                <Loader2 className="h-5 w-5 text-purple-400 animate-spin" />
              ) : (
                <Sparkles className="h-5 w-5 text-gray-400" />
              )}
            </div>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="px-4 pb-4">
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Content Types
                  </label>
                  <select
                    value={filters.contentTypes[0]}
                    onChange={(e) => setFilters(prev => ({ 
                      ...prev, 
                      contentTypes: e.target.value === 'all' ? ['all'] : [e.target.value]
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  >
                    <option value="all">All Content</option>
                    <option value="journal_entry">Journal Entries</option>
                    <option value="task">Tasks</option>
                    <option value="project">Projects</option>
                    <option value="daily_reflection">Daily Reflections</option>
                    <option value="ai_insight">AI Insights</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Similarity Threshold
                  </label>
                  <select
                    value={filters.minSimilarity}
                    onChange={(e) => setFilters(prev => ({ 
                      ...prev, 
                      minSimilarity: parseFloat(e.target.value)
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  >
                    <option value={0.2}>Very Loose (20%)</option>
                    <option value={0.3}>Loose (30%)</option>
                    <option value={0.4}>Moderate (40%)</option>
                    <option value={0.5}>Strict (50%)</option>
                    <option value={0.6}>Very Strict (60%)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Time Range
                  </label>
                  <select
                    value={filters.dateRangeDays || ''}
                    onChange={(e) => setFilters(prev => ({ 
                      ...prev, 
                      dateRangeDays: e.target.value ? parseInt(e.target.value) : null
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  >
                    <option value="">All Time</option>
                    <option value="7">Last Week</option>
                    <option value="30">Last Month</option>
                    <option value="90">Last 3 Months</option>
                    <option value="365">Last Year</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        <div className="flex-1 overflow-y-auto">
          {query.trim().length <= 2 && recentSearches.length > 0 && (
            <div className="p-4">
              <p className="text-sm text-gray-400 mb-3">Recent searches:</p>
              <div className="space-y-2">
                {recentSearches.map((search, index) => (
                  <button
                    key={index}
                    onClick={() => handleRecentSearchClick(search.query)}
                    className="w-full text-left text-sm text-gray-400 hover:text-gray-300 py-2 px-3 hover:bg-gray-800/30 rounded transition-colors flex items-center gap-2"
                  >
                    <Clock className="h-3 w-3" />
                    {search.query}
                  </button>
                ))}
              </div>
            </div>
          )}

          {results.length > 0 && (
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm text-gray-400">
                  Found {results.length} results
                  {searchMetadata && (
                    <span className="ml-2 text-xs text-gray-500">
                      • {searchMetadata.embedding_model}
                    </span>
                  )}
                </p>
              </div>

              <div className="space-y-3">
                {results.map((result, index) => {
                  const IconComponent = getEntityIcon(result.entity_type);
                  
                  return (
                    <button
                      key={`${result.entity_type}-${result.id}-${index}`}
                      onClick={() => handleResultClick(result)}
                      className="w-full text-left p-4 bg-gray-800/50 hover:bg-gray-700/50 rounded-lg transition-colors border border-gray-700/50 hover:border-gray-600"
                    >
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-purple-600/20 rounded-lg flex-shrink-0">
                          <IconComponent className="h-4 w-4 text-purple-400" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-medium text-white truncate">
                              {result.title}
                            </h3>
                            <span className={`px-2 py-1 text-xs rounded-full ${getConfidenceColor(result.confidence_level)}`}>
                              {result.similarity_score}%
                            </span>
                          </div>
                          
                          <p className="text-sm text-gray-400 mb-2">
                            {result.entity_display_name}
                            {result.metadata?.project_name && (
                              <span className="ml-2 text-gray-500">
                                • {result.metadata.project_name}
                              </span>
                            )}
                          </p>
                          
                          <p className="text-sm text-gray-300 line-clamp-2">
                            {result.content_preview}
                          </p>
                          
                          {result.created_at && (
                            <p className="text-xs text-gray-500 mt-2">
                              {new Date(result.created_at).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                        
                        <ArrowRight className="h-4 w-4 text-gray-500 flex-shrink-0" />
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {query.trim().length > 2 && results.length === 0 && !isSearching && (
            <div className="p-8 text-center">
              <Search className="h-12 w-12 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-400 mb-2">No results found</h3>
              <p className="text-sm text-gray-500">
                Try adjusting your search terms or filters
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-700/50 text-center">
          <p className="text-xs text-gray-500">
            Press <kbd className="px-1 bg-gray-700 rounded text-gray-300">Esc</kbd> to close
            {results.length > 0 && (
              <span className="ml-2">• Click any result to view details</span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

// Hook for global semantic search access
export const useSemanticSearch = () => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'f') {
        e.preventDefault();
        console.log('🔍 Semantic search opened via keyboard shortcut');
        setIsOpen(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const openSearch = () => {
    console.log('🔍 Semantic search opened via button click');
    setIsOpen(true);
  };

  const closeSearch = () => {
    console.log('🔍 Semantic search closed');
    setIsOpen(false);
  };

  return {
    isOpen,
    open: openSearch,
    close: closeSearch
  };
};

export default SemanticSearch;