import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Search, 
  Mic, 
  Brain, 
  Zap, 
  Calendar, 
  Plus, 
  Target,
  Clock,
  Command,
  ArrowRight,
  Loader2,
  Lightbulb,
  Sparkles
} from 'lucide-react';
import { hrmAPI } from '../services/api';
import { useSemanticSearch } from './SemanticSearch';

const AICommandCenter = ({ isOpen, onClose, onCommand }) => {
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [recentCommands, setRecentCommands] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const inputRef = useRef(null);

  // Context-aware suggestions based on current state
  const contextSuggestions = [
    { 
      text: "Show me my highest priority tasks", 
      icon: Target,
      action: async () => {
        setIsProcessing(true);
        try {
          const priorities = await hrmAPI.getTodayPriorities(5, true);
          onCommand({ type: 'show_priorities', data: priorities });
        } catch (error) {
          console.error('Failed to get priorities:', error);
        } finally {
          setIsProcessing(false);
        }
      }
    },
    { 
      text: "Analyze my work-life balance", 
      icon: Brain,
      action: async () => {
        setIsProcessing(true);
        try {
          const analysis = await hrmAPI.analyzeLifeBalance();
          onCommand({ type: 'show_analysis', data: analysis });
        } catch (error) {
          console.error('Failed to analyze balance:', error);
        } finally {
          setIsProcessing(false);
        }
      }
    },
    { 
      text: "What should I work on next?", 
      icon: Lightbulb,
      action: async () => {
        setIsProcessing(true);
        try {
          const insights = await hrmAPI.getHighConfidenceInsights(0.7);
          onCommand({ type: 'show_recommendations', data: insights });
        } catch (error) {
          console.error('Failed to get recommendations:', error);
        } finally {
          setIsProcessing(false);
        }
      }
    },
    { 
      text: "Plan my day", 
      icon: Calendar,
      action: () => onCommand({ type: 'plan_day' })
    },
    { 
      text: "Create a new task", 
      icon: Plus,
      action: () => onCommand({ type: 'create_task' })
    },
    { 
      text: "Review my recent patterns", 
      icon: Zap,
      action: async () => {
        setIsProcessing(true);
        try {
          const insights = await hrmAPI.getInsights({ 
            insight_type: 'pattern_recognition',
            is_active: true,
            limit: 10 
          });
          onCommand({ type: 'show_patterns', data: insights });
        } catch (error) {
          console.error('Failed to get patterns:', error);
        } finally {
          setIsProcessing(false);
        }
      }
    }
  ];

  useEffect(() => {
    if (isOpen) {
      // Focus input when opened
      setTimeout(() => inputRef.current?.focus(), 100);
      
      // Load recent commands from localStorage
      const recent = JSON.parse(localStorage.getItem('ai_recent_commands') || '[]');
      setRecentCommands(recent.slice(0, 5));
    }
  }, [isOpen]);

  useEffect(() => {
    // Filter suggestions based on input
    if (input.length > 0) {
      const filtered = contextSuggestions.filter(suggestion =>
        suggestion.text.toLowerCase().includes(input.toLowerCase())
      );
      setSuggestions(filtered);
    } else {
      setSuggestions(contextSuggestions.slice(0, 4)); // Show top 4 by default
    }
  }, [input]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;

    setIsProcessing(true);
    
    try {
      // Save to recent commands
      const newCommand = { text: input, timestamp: Date.now() };
      const updatedRecent = [newCommand, ...recentCommands.filter(c => c.text !== input)].slice(0, 5);
      setRecentCommands(updatedRecent);
      localStorage.setItem('ai_recent_commands', JSON.stringify(updatedRecent));

      // Process natural language command
      await processNaturalLanguageCommand(input);
      
      // Clear input and close
      setInput('');
      onClose();
    } catch (error) {
      console.error('Command processing failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const processNaturalLanguageCommand = async (command) => {
    const cmd = command.toLowerCase();
    
    // Simple pattern matching for MVP
    if (cmd.includes('priority') || cmd.includes('important')) {
      const priorities = await hrmAPI.getTodayPriorities(5, true);
      onCommand({ type: 'show_priorities', data: priorities });
    } else if (cmd.includes('balance') || cmd.includes('life')) {
      const analysis = await hrmAPI.analyzeLifeBalance();
      onCommand({ type: 'show_analysis', data: analysis });
    } else if (cmd.includes('next') || cmd.includes('should i')) {
      const insights = await hrmAPI.getHighConfidenceInsights(0.7);
      onCommand({ type: 'show_recommendations', data: insights });
    } else if (cmd.includes('plan') || cmd.includes('schedule')) {
      onCommand({ type: 'plan_day' });
    } else if (cmd.includes('create') || cmd.includes('add') || cmd.includes('new task')) {
      onCommand({ type: 'create_task' });
    } else if (cmd.includes('pattern') || cmd.includes('trend')) {
      const insights = await hrmAPI.getInsights({ 
        insight_type: 'pattern_recognition',
        is_active: true,
        limit: 10 
      });
      onCommand({ type: 'show_patterns', data: insights });
    } else {
      // Fallback to general analysis
      const analysis = await hrmAPI.triggerGlobalAnalysis('balanced');
      onCommand({ type: 'show_analysis', data: analysis });
    }
  };

  const executeSuggestion = async (suggestion) => {
    setInput('');
    try {
      await suggestion.action();
    } catch (error) {
      console.error('Suggestion execution failed:', error);
    }
    onClose();
  };

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'Enter' && e.metaKey) {
      handleSubmit(e);
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
      <div className="bg-gray-900/95 border border-gray-700 rounded-xl shadow-2xl w-full max-w-2xl mx-4">
        {/* Header */}
        <div className="flex items-center gap-3 p-4 border-b border-gray-700">
          <div className="p-2 bg-purple-600 rounded-lg">
            <Brain className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-white">AI Command Center</h2>
            <p className="text-sm text-gray-400">Ask AI anything or type a command</p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <kbd className="px-2 py-1 bg-gray-700 text-xs text-gray-300 rounded">⌘K</kbd>
          </div>
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="p-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask AI anything or type a command..."
              className="w-full bg-gray-800 border border-gray-600 rounded-lg pl-12 pr-12 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
              disabled={isProcessing}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
              {isProcessing ? (
                <Loader2 className="h-5 w-5 text-purple-400 animate-spin" />
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => setIsListening(!isListening)}
                    className={`p-1 rounded transition-colors ${
                      isListening ? 'text-red-400' : 'text-gray-400 hover:text-white'
                    }`}
                    title="Voice input"
                  >
                    <Mic className="h-5 w-5" />
                  </button>
                  <ArrowRight className="h-5 w-5 text-gray-400" />
                </>
              )}
            </div>
          </div>
        </form>

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="px-4 pb-4">
            <p className="text-sm text-gray-400 mb-3">
              {input ? 'Matching suggestions:' : 'Quick actions:'}
            </p>
            <div className="space-y-2">
              {suggestions.map((suggestion, index) => {
                const IconComponent = suggestion.icon;
                return (
                  <button
                    key={index}
                    onClick={() => executeSuggestion(suggestion)}
                    className="w-full flex items-center gap-3 p-3 bg-gray-800/50 hover:bg-gray-700/50 rounded-lg transition-colors text-left"
                    disabled={isProcessing}
                  >
                    <div className="p-2 bg-purple-600/20 rounded-lg">
                      <IconComponent className="h-4 w-4 text-purple-400" />
                    </div>
                    <span className="text-gray-300">{suggestion.text}</span>
                    <ArrowRight className="h-4 w-4 text-gray-500 ml-auto" />
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Recent Commands */}
        {recentCommands.length > 0 && !input && (
          <div className="px-4 pb-4 border-t border-gray-700/50">
            <p className="text-sm text-gray-400 mb-3 mt-4">Recent commands:</p>
            <div className="space-y-1">
              {recentCommands.map((command, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setInput(command.text);
                    inputRef.current?.focus();
                  }}
                  className="w-full text-left text-sm text-gray-400 hover:text-gray-300 py-1 px-2 hover:bg-gray-800/30 rounded transition-colors"
                >
                  <Clock className="h-3 w-3 inline mr-2" />
                  {command.text}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-700/50 text-center">
          <p className="text-xs text-gray-500">
            Press <kbd className="px-1 bg-gray-700 rounded text-gray-300">⌘⏎</kbd> to execute or{' '}
            <kbd className="px-1 bg-gray-700 rounded text-gray-300">Esc</kbd> to close
          </p>
        </div>
      </div>
    </div>
  );
};

// Hook for global command center access
export const useAICommandCenter = () => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false)
  };
};

export default AICommandCenter;