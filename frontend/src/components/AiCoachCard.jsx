import React, { useState, useEffect } from 'react';
import { Brain, Clock, Flag, Play, RefreshCw, CheckCircle2, AlertCircle, MessageCircle, Send } from 'lucide-react';
import emergencyAPI from '../services/emergencyApi';

const AiCoachCard = ({ onStartFocusSession }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    loadTodaysPriorities();
  }, []);

  const loadTodaysPriorities = async () => {
    setLoading(true);
    setError('');
    
    try {
      console.log('🤖 AI Coach: Loading priorities');
      const response = await emergencyAPI.aiCoach();
      setRecommendations(response.data.recommendations || []);
      setMessage(response.data.message || '');
      console.log('🤖 AI Coach: Priorities loaded successfully');
    } catch (err) {
      console.error('🤖 AI Coach: Error loading priorities:', err);
      setError('Unable to load today\'s priorities');
    } finally {
      setLoading(false);
    }
  };

  const handleStartFocus = (taskId, taskName) => {
    if (onStartFocusSession) {
      onStartFocusSession(taskId, taskName);
    } else {
      // Fallback: could integrate with existing Pomodoro timer
      alert(`Starting focus session for: ${taskName}`);
    }
  };

  const handleChatSubmit = async () => {
    if (!chatMessage.trim()) return;
    
    const userMessage = chatMessage.trim();
    setChatMessage('');
    setChatLoading(true);
    
    // Add user message to chat history
    const newHistory = [...chatHistory, { 
      type: 'user', 
      message: userMessage, 
      timestamp: new Date() 
    }];
    setChatHistory(newHistory);
    
    try {
      const response = await aiCoachAPI.chatWithCoach(userMessage);
      
      // Add AI response to chat history
      setChatHistory([...newHistory, { 
        type: 'ai', 
        message: response.data.response, 
        timestamp: new Date() 
      }]);
    } catch (err) {
      console.error('Error chatting with AI coach:', err);
      setChatHistory([...newHistory, { 
        type: 'ai', 
        message: "I'm having trouble responding right now. Please try again in a moment.", 
        timestamp: new Date() 
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleChatKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleChatSubmit();
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-400/10';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10';
      case 'low': return 'text-green-400 bg-green-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const formatDueDate = (dueDateStr) => {
    if (!dueDateStr) return null;
    
    try {
      const dueDate = new Date(dueDateStr);
      const today = new Date();
      const diffTime = dueDate - today;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) {
        return `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) > 1 ? 's' : ''}`;
      } else if (diffDays === 0) {
        return 'Due today';
      } else if (diffDays === 1) {
        return 'Due tomorrow';
      } else {
        return `Due in ${diffDays} days`;
      }
    } catch {
      return 'Due date';
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-800/30 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Brain className="h-6 w-6 text-blue-400" />
          <h2 className="text-xl font-semibold text-white">AI Coach</h2>
        </div>
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="h-6 w-6 text-blue-400 animate-spin" />
          <span className="ml-2 text-gray-300">Analyzing your priorities...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-800/30 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Brain className="h-6 w-6 text-blue-400" />
          <h2 className="text-xl font-semibold text-white">AI Coach</h2>
        </div>
        <div className="flex items-center text-red-400">
          <AlertCircle className="h-5 w-5 mr-2" />
          <span>{error}</span>
          <button 
            onClick={loadTodaysPriorities}
            className="ml-4 px-3 py-1 bg-red-600/20 hover:bg-red-600/30 rounded-lg text-sm transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-800/30 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <Brain className="h-6 w-6 text-blue-400" />
          <h2 className="text-xl font-semibold text-white">AI Coach</h2>
        </div>
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => setShowChat(!showChat)}
            className={`p-2 rounded-lg transition-colors ${
              showChat 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
            title="Chat with AI Coach"
          >
            <MessageCircle className="h-4 w-4" />
          </button>
          <button 
            onClick={loadTodaysPriorities}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800/50 rounded-lg transition-colors"
            title="Refresh recommendations"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Coach Message */}
      {message && (
        <div className="bg-blue-900/30 border border-blue-700/30 rounded-lg p-3 mb-4">
          <p className="text-blue-200 text-sm italic">{message}</p>
        </div>
      )}

      {/* No Recommendations */}
      {recommendations.length === 0 ? (
        <div className="text-center py-6">
          <CheckCircle2 className="h-12 w-12 text-green-400 mx-auto mb-3" />
          <p className="text-gray-300 mb-2">You're all caught up!</p>
          <p className="text-gray-400 text-sm">No urgent tasks today. Great work staying on top of things.</p>
        </div>
      ) : (
        /* Recommendations */
        <div className="space-y-4">
          {recommendations.map((rec, index) => (
            <div 
              key={rec.task_id} 
              className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4 hover:border-gray-600/50 transition-colors"
            >
              {/* Task Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-blue-400 font-medium text-sm">#{index + 1}</span>
                    <h3 className="text-white font-medium">{rec.task_name}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(rec.priority)}`}>
                      {rec.priority}
                    </span>
                  </div>
                  
                  {rec.project_name && (
                    <p className="text-gray-400 text-sm mb-1">{rec.project_name}</p>
                  )}
                  
                  {rec.task_description && (
                    <p className="text-gray-300 text-sm line-clamp-2">{rec.task_description}</p>
                  )}
                </div>
              </div>

              {/* Coaching Message */}
              <div className="bg-blue-900/30 border-l-4 border-blue-400 pl-3 py-2 mb-3">
                <p className="text-blue-200 text-sm italic">{rec.coaching_message}</p>
              </div>

              {/* Task Meta & Actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 text-xs text-gray-400">
                  {rec.due_date && (
                    <div className="flex items-center space-x-1">
                      <Clock className="h-3 w-3" />
                      <span>{formatDueDate(rec.due_date)}</span>
                    </div>
                  )}
                  
                  {rec.reasons && rec.reasons.length > 0 && (
                    <div className="flex items-center space-x-1">
                      <Flag className="h-3 w-3" />
                      <span>{rec.reasons.join(', ')}</span>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleStartFocus(rec.task_id, rec.task_name)}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
                >
                  <Play className="h-4 w-4" />
                  <span>Start Focus Session</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Interactive Chat Interface */}
      {showChat && (
        <div className="mt-6 border-t border-gray-700/30 pt-4">
          <h3 className="text-sm font-medium text-gray-300 mb-3">
            Ask your AI Coach anything about your goals and progress
          </h3>
          
          {/* Chat History */}
          {chatHistory.length > 0 && (
            <div className="max-h-60 overflow-y-auto mb-4 space-y-3">
              {chatHistory.map((chat, index) => (
                <div key={index} className={`flex ${chat.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-3 rounded-lg ${
                    chat.type === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-800 text-gray-200 border border-gray-700'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap">{chat.message}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {chat.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-800 border border-gray-700 p-3 rounded-lg">
                    <div className="flex items-center space-x-2 text-gray-400">
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      <span className="text-sm">AI Coach is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Chat Input */}
          <div className="flex space-x-2">
            <input
              type="text"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              onKeyPress={handleChatKeyPress}
              placeholder="Ask about your pillars, areas, projects, tasks..."
              className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              disabled={chatLoading}
            />
            <button
              onClick={handleChatSubmit}
              disabled={chatLoading || !chatMessage.trim()}
              className="p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
          
          {/* Quick Questions */}
          {chatHistory.length === 0 && (
            <div className="mt-3">
              <p className="text-xs text-gray-500 mb-2">Quick questions to get started:</p>
              <div className="flex flex-wrap gap-2">
                {[
                  "How am I doing with my goals?",
                  "What needs my attention?",
                  "Show me my progress patterns",
                  "Which pillar needs focus?"
                ].map((question) => (
                  <button
                    key={question}
                    onClick={() => setChatMessage(question)}
                    className="px-2 py-1 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded text-xs transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-gray-700/30">
        <p className="text-xs text-gray-500 text-center">
          Recommendations update based on your deadlines, priorities, and progress
        </p>
      </div>
    </div>
  );
};

export default AiCoachCard;