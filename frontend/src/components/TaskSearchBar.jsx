import React, { useState, useEffect, useRef } from 'react';
import { Search, Plus, Loader2 } from 'lucide-react';
import { tasksAPI } from '../services/api';

const TaskSearchBar = ({ onAddTask, placeholder = "Search for tasks to add to today's focus..." }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [error, setError] = useState('');
  
  const searchTimeoutRef = useRef(null);
  const dropdownRef = useRef(null);

  // Debounced search with 350ms delay
  useEffect(() => {
    const q = (query || '').trim();
    if (q.length < 2) {
      setResults([]);
      setShowResults(false);
      return;
    }

    // Clear existing timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Set new timeout for debounced search
    searchTimeoutRef.current = setTimeout(async () => {
      setLoading(true);
      setError('');
      
      try {
        const response = await tasksAPI.searchTasks(q, limit, page);
        const results = response.data || [];
        // Normalize shapes from backend
        const normalized = results.map((r) => ({
          id: r.id || r.taskId,
          name: r.name || r.title,
          description: r.description,
          project_name: r.project_name || r.project,
          priority: r.priority
        })).filter(x => x.id && x.name);
        
        setResults(normalized);
        setShowResults(true);
      } catch (err) {
        console.error('Error searching tasks:', err);
        setError('Failed to search tasks. Please try again');
        setResults([]);
        setShowResults(false);
      } finally {
        setLoading(false);
      }
    }, 350); // 350ms debounce delay

    // Cleanup timeout on unmount or query change
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [query]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleAddTask = (task) => {
    onAddTask(task);
    setQuery('');
    setResults([]);
    setShowResults(false);
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return 'text-red-400 bg-red-400/10';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10';
      case 'low': return 'text-green-400 bg-green-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  return (
    <div className="relative w-full" ref={dropdownRef}>
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          value={query}
          onKeyDown={(e) => {
            if (!showResults) return;
            if (e.key === 'ArrowDown') {
              e.preventDefault();
              setActiveIndex((prev) => Math.min(prev + 1, results.length - 1));
            } else if (e.key === 'ArrowUp') {
              e.preventDefault();
              setActiveIndex((prev) => Math.max(prev - 1, 0));
            } else if (e.key === 'Enter') {
              if (activeIndex >= 0 && activeIndex < results.length) {
                e.preventDefault();
                handleAddTask(results[activeIndex]);
              }
            } else if (e.key === 'Escape') {
              setShowResults(false);
            }
          }}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-gray-800/50 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-400 focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400 focus:outline-none transition-colors"
        />
        {loading && (
          <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-yellow-400 animate-spin" />
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="mt-2 p-2 bg-red-900/20 border border-red-600 rounded text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Search Results Dropdown */}
      {showResults && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-gray-800/95 border border-gray-700 rounded-lg shadow-xl max-h-80 overflow-y-auto z-50 backdrop-blur-sm">
          {results.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Searching...</span>
                </div>
              ) : (
                query.length >= 2 ? 'No tasks found matching your search' : 'Type at least 2 characters to search'
              )}
            </div>
          ) : (
            <div className="py-2">
              {results.map((task, idx) => (
                <div
                  key={task.id}
                  className="px-4 py-3 hover:bg-gray-700/50 transition-colors border-b border-gray-700/50 last:border-b-0"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="text-sm font-medium text-white truncate">
                          {task.name}
                        </h4>
                        <span className={`px-2 py-1 text-xs rounded-full flex-shrink-0 ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                      </div>
                      
                      {task.description && (
                        <p className="text-xs text-gray-400 mb-1 line-clamp-2">
                          {task.description}
                        </p>
                      )}
                      
                      <div className="flex items-center space-x-3 text-xs text-gray-500">
                        {task.project_name && (
                          <span className="text-blue-400">
                            📁 {task.project_name}
                          </span>
                        )}
                        {task.status && (
                          <span className="capitalize">
                            {task.status === 'todo' ? 'To Do' : task.status.replace('_', ' ')}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <button
                      onClick={() => handleAddTask(task)}
                      className="ml-3 p-2 text-gray-400 hover:text-yellow-400 hover:bg-gray-700/50 rounded-lg transition-colors flex-shrink-0"
                      title="Add to Today's Focus"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TaskSearchBar;