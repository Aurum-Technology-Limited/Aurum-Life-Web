/**
 * Phase 2: Smart Search Interface Component
 * Advanced search UI with filters, suggestions, and real-time results
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, Filter, Clock, TrendingUp, Sparkles, X, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { smartSearchService, SearchResult, SearchFilters, SearchSuggestion } from '../../services/smartSearchService';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Separator } from '../ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Checkbox } from '../ui/checkbox';
import { DatePickerWithRange } from '../ui/date-picker-with-range';

interface SmartSearchInterfaceProps {
  onResultSelect?: (result: SearchResult) => void;
  onClose?: () => void;
  initialQuery?: string;
  compact?: boolean;
  placeholder?: string;
}

const SmartSearchInterface: React.FC<SmartSearchInterfaceProps> = ({
  onResultSelect,
  onClose,
  initialQuery = '',
  compact = false,
  placeholder = 'Search across your Aurum Life...'
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({});
  const [selectedTab, setSelectedTab] = useState<'all' | 'recent' | 'trending'>('all');
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout>();

  // Debounced search
  const debouncedSearch = useCallback(async (searchQuery: string) => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    searchTimeoutRef.current = setTimeout(async () => {
      if (searchQuery.trim()) {
        setIsLoading(true);
        try {
          const searchResults = await smartSearchService.search(searchQuery, filters);
          setResults(searchResults);
        } catch (error) {
          console.error('Search error:', error);
          setResults([]);
        } finally {
          setIsLoading(false);
        }
      } else {
        setResults([]);
      }
    }, 300);
  }, [filters]);

  // Get suggestions
  const getSuggestions = useCallback(async (partialQuery: string) => {
    try {
      const searchSuggestions = await smartSearchService.getSearchSuggestions(partialQuery);
      setSuggestions(searchSuggestions);
    } catch (error) {
      console.error('Error getting suggestions:', error);
      setSuggestions([]);
    }
  }, []);

  // Handle query change
  useEffect(() => {
    debouncedSearch(query);
    if (query.length > 0) {
      getSuggestions(query);
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  }, [query, debouncedSearch, getSuggestions]);

  // Handle filter changes
  useEffect(() => {
    if (query.trim()) {
      debouncedSearch(query);
    }
  }, [filters, debouncedSearch, query]);

  const handleResultClick = (result: SearchResult) => {
    onResultSelect?.(result);
    // Add to recent searches by performing a search
    smartSearchService.search(result.title, {});
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setQuery(suggestion.query);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const clearFilters = () => {
    setFilters({});
  };

  const getResultIcon = (type: SearchResult['type']) => {
    const icons = {
      pillar: '🏛️',
      area: '📂',
      project: '📋',
      task: '✅',
      journal: '📝',
      note: '📄'
    };
    return icons[type] || '📄';
  };

  const getTypeColor = (type: SearchResult['type']) => {
    const colors = {
      pillar: 'bg-yellow-500/20 text-yellow-300',
      area: 'bg-blue-500/20 text-blue-300',
      project: 'bg-green-500/20 text-green-300',
      task: 'bg-purple-500/20 text-purple-300',
      journal: 'bg-orange-500/20 text-orange-300',
      note: 'bg-gray-500/20 text-gray-300'
    };
    return colors[type] || 'bg-gray-500/20 text-gray-300';
  };

  const renderSearchResult = (result: SearchResult, index: number) => (
    <motion.div
      key={result.id}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="glassmorphism-card p-4 cursor-pointer hover:border-primary/40 transition-all"
      onClick={() => handleResultClick(result)}
    >
      <div className="flex items-start gap-3">
        <div className="text-xl flex-shrink-0 mt-1">
          {getResultIcon(result.type)}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-medium text-foreground truncate">
              {result.title}
            </h3>
            <Badge variant="secondary" className={`text-xs ${getTypeColor(result.type)}`}>
              {result.type}
            </Badge>
            <div className="text-xs text-primary font-medium">
              {Math.round(result.relevanceScore)}%
            </div>
          </div>
          
          {result.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
              {result.description}
            </p>
          )}
          
          {result.hierarchy && (
            <div className="flex items-center gap-1 text-xs text-muted-foreground mb-2">
              {result.hierarchy.pillar && (
                <>
                  <span>{result.hierarchy.pillar}</span>
                  {(result.hierarchy.area || result.hierarchy.project) && <ArrowRight className="w-3 h-3" />}
                </>
              )}
              {result.hierarchy.area && (
                <>
                  <span>{result.hierarchy.area}</span>
                  {result.hierarchy.project && <ArrowRight className="w-3 h-3" />}
                </>
              )}
              {result.hierarchy.project && (
                <span>{result.hierarchy.project}</span>
              )}
            </div>
          )}
          
          {result.matchedTerms.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {result.matchedTerms.slice(0, 3).map((term, i) => (
                <Badge key={i} variant="outline" className="text-xs px-1 py-0">
                  {term}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );

  const renderSuggestion = (suggestion: SearchSuggestion, index: number) => {
    const getSuggestionIcon = () => {
      switch (suggestion.type) {
        case 'recent': return <Clock className="w-4 h-4 text-muted-foreground" />;
        case 'popular': return <TrendingUp className="w-4 h-4 text-blue-400" />;
        case 'ai_suggested': return <Sparkles className="w-4 h-4 text-primary" />;
        default: return <Search className="w-4 h-4 text-muted-foreground" />;
      }
    };

    return (
      <motion.div
        key={`${suggestion.query}-${index}`}
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.03 }}
        className="flex items-center gap-3 p-2 hover:bg-accent/50 cursor-pointer rounded-md transition-colors"
        onClick={() => handleSuggestionClick(suggestion)}
      >
        {getSuggestionIcon()}
        <div className="flex-1">
          <div className="text-sm text-foreground">{suggestion.query}</div>
          {suggestion.context && (
            <div className="text-xs text-muted-foreground">{suggestion.context}</div>
          )}
        </div>
        <div className="text-xs text-primary">
          {Math.round(suggestion.confidence * 100)}%
        </div>
      </motion.div>
    );
  };

  if (compact) {
    return (
      <div className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            className="pl-10 pr-4 glassmorphism-card border-border/40"
          />
        </div>
        
        <AnimatePresence>
          {(showSuggestions && suggestions.length > 0) || results.length > 0 ? (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute top-full mt-2 w-full z-50 glassmorphism-card border border-border/40 max-h-96 overflow-y-auto custom-scrollbar"
            >
              {showSuggestions && suggestions.length > 0 && results.length === 0 && (
                <div className="p-2">
                  <div className="text-xs text-muted-foreground mb-2 px-2">Suggestions</div>
                  {suggestions.slice(0, 5).map(renderSuggestion)}
                </div>
              )}
              
              {results.length > 0 && (
                <div className="p-2 space-y-2">
                  {results.slice(0, 8).map(renderSearchResult)}
                </div>
              )}
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Search Header */}
      <div className="glassmorphism-card p-6 mb-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
            <Input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={placeholder}
              className="pl-12 pr-4 text-lg h-12 glassmorphism-panel border-border/40"
              autoFocus
            />
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2"
          >
            <Filter className="w-4 h-4" />
            Filters
            {Object.keys(filters).length > 0 && (
              <Badge variant="secondary" className="ml-1">
                {Object.keys(filters).length}
              </Badge>
            )}
          </Button>
          
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Active Filters */}
        {Object.keys(filters).length > 0 && (
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm text-muted-foreground">Active filters:</span>
            {filters.types?.map(type => (
              <Badge key={type} variant="secondary" className="text-xs">
                {type}
              </Badge>
            ))}
            {filters.pillars?.map(pillar => (
              <Badge key={pillar} variant="secondary" className="text-xs">
                📍 {pillar}
              </Badge>
            ))}
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="text-xs h-6 px-2"
            >
              Clear all
            </Button>
          </div>
        )}

        {/* Filters Panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="border-t border-border/40 pt-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm text-muted-foreground mb-2 block">Content Types</label>
                  <div className="space-y-2">
                    {['pillar', 'area', 'project', 'task', 'journal'].map(type => (
                      <div key={type} className="flex items-center space-x-2">
                        <Checkbox
                          id={type}
                          checked={filters.types?.includes(type as any) || false}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setFilters(prev => ({
                                ...prev,
                                types: [...(prev.types || []), type as any]
                              }));
                            } else {
                              setFilters(prev => ({
                                ...prev,
                                types: prev.types?.filter(t => t !== type)
                              }));
                            }
                          }}
                        />
                        <label htmlFor={type} className="text-sm capitalize">
                          {type}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="text-sm text-muted-foreground mb-2 block">Priority</label>
                  <Select
                    value={filters.priority?.[0] || ''}
                    onValueChange={(value) => {
                      setFilters(prev => ({
                        ...prev,
                        priority: value ? [value] : undefined
                      }));
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Any priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Any priority</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="text-sm text-muted-foreground mb-2 block">Date Range</label>
                  <DatePickerWithRange
                    date={filters.dateRange ? {
                      from: filters.dateRange.start,
                      to: filters.dateRange.end
                    } : undefined}
                    onDateChange={(range) => {
                      setFilters(prev => ({
                        ...prev,
                        dateRange: range?.from ? {
                          start: range.from,
                          end: range.to || range.from
                        } : undefined
                      }));
                    }}
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Search Results */}
      <Tabs value={selectedTab} onValueChange={(value) => setSelectedTab(value as any)} className="w-full">
        <TabsList className="grid w-full grid-cols-3 glassmorphism-panel">
          <TabsTrigger value="all">All Results ({results.length})</TabsTrigger>
          <TabsTrigger value="recent">Recent Searches</TabsTrigger>
          <TabsTrigger value="trending">Trending</TabsTrigger>
        </TabsList>
        
        <TabsContent value="all" className="mt-6">
          <AnimatePresence>
            {isLoading ? (
              <div className="glassmorphism-card p-8 text-center">
                <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
                <p className="text-muted-foreground">Searching...</p>
              </div>
            ) : results.length > 0 ? (
              <div className="space-y-4">
                {results.map(renderSearchResult)}
              </div>
            ) : query.trim() ? (
              <div className="glassmorphism-card p-8 text-center">
                <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No results found</h3>
                <p className="text-muted-foreground mb-4">
                  Try adjusting your search terms or filters
                </p>
                {suggestions.length > 0 && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Suggested searches:</p>
                    <div className="flex flex-wrap gap-2 justify-center">
                      {suggestions.slice(0, 3).map((suggestion, i) => (
                        <Button
                          key={i}
                          variant="outline"
                          size="sm"
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          {suggestion.query}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : showSuggestions && suggestions.length > 0 ? (
              <div className="glassmorphism-card p-4">
                <h3 className="text-sm text-muted-foreground mb-3">Search suggestions</h3>
                <div className="space-y-1">
                  {suggestions.slice(0, 8).map(renderSuggestion)}
                </div>
              </div>
            ) : null}
          </AnimatePresence>
        </TabsContent>
        
        <TabsContent value="recent" className="mt-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Recent Searches
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {smartSearchService.getTrendingSearches(10).map((search, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-2 hover:bg-accent/50 cursor-pointer rounded-md"
                    onClick={() => setQuery(search.query)}
                  >
                    <span className="text-sm">{search.query}</span>
                    <Badge variant="secondary" className="text-xs">
                      {search.count}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="trending" className="mt-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Trending Searches
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {smartSearchService.getTrendingSearches().map((search, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-2 hover:bg-accent/50 cursor-pointer rounded-md"
                    onClick={() => setQuery(search.query)}
                  >
                    <div className="flex items-center gap-2">
                      <div className="text-sm text-primary font-medium">#{i + 1}</div>
                      <span className="text-sm">{search.query}</span>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {search.count} searches
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SmartSearchInterface;