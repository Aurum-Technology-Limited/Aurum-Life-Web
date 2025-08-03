import React, { useState, useEffect } from 'react';
import { Bot, Target, TrendingUp, AlertTriangle, Loader2, AlertCircle, Brain, ChevronRight, Clock, Zap } from 'lucide-react';
import { api } from '../services/api';

const FeatureCard = ({ icon: Icon, title, description, buttonText, onClick, disabled = false, isLoading = false }) => (
  <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30 transition-all duration-300 group">
    <div className="flex items-center space-x-3 mb-4">
      <div className="w-12 h-12 rounded-lg bg-yellow-400 flex items-center justify-center group-hover:scale-110 transition-transform">
        <Icon size={24} style={{ color: '#0B0D14' }} />
      </div>
      <div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
    </div>
    <p className="text-gray-400 mb-6 leading-relaxed">{description}</p>
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className="w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
    >
      {isLoading ? (
        <Loader2 size={18} className="animate-spin" />
      ) : (
        <>
          <span>{buttonText}</span>
          <ChevronRight size={16} />
        </>
      )}
    </button>
  </div>
);

const QuotaDisplay = ({ remaining, total }) => (
  <div className="flex items-center space-x-3 p-4 rounded-lg bg-gray-800/50 border border-gray-700">
    <div className="w-10 h-10 rounded-lg bg-yellow-400/20 flex items-center justify-center">
      <Zap size={20} className="text-yellow-400" />
    </div>
    <div className="flex-1">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-gray-400">AI Interactions This Month</span>
        <span className="text-sm font-semibold text-white">{remaining}/{total}</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div 
          className="bg-yellow-400 h-2 rounded-full transition-all duration-500"
          style={{ width: `${(remaining / total) * 100}%` }}
        />
      </div>
    </div>
  </div>
);

const RateLimitWarning = ({ show }) => {
  if (!show) return null;
  
  return (
    <div className="p-3 rounded-lg bg-orange-900/20 border border-orange-500/30 flex items-center space-x-2 mb-4">
      <Clock size={16} className="text-orange-400" />
      <span className="text-orange-400 text-sm">Please wait a moment before making another request</span>
    </div>
  );
};

const AICoach = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [userStats, setUserStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    initializeChat();
  }, []);

  const initializeChat = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load user stats for insights
      const statsResponse = await statsAPI.getUserStats();
      setUserStats(statsResponse.data);
      
      // Add welcome message if no messages exist
      if (messages.length === 0) {
        const welcomeMessage = {
          id: Date.now(),
          content: "Hello! I'm your AI Growth Coach. I'm here to help you with insights, motivation, and guidance on your personal development journey. How can I assist you today?",
          message_type: 'ai',
          timestamp: new Date().toISOString()
        };
        setMessages([welcomeMessage]);
      }
    } catch (err) {
      setError(handleApiError(err, 'Failed to initialize chat'));
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      content: inputValue,
      message_type: 'user',
      timestamp: new Date().toISOString()
    };

    // Add user message to the chat immediately
    setMessages(prev => [...prev, userMessage]);
    
    try {
      setIsTyping(true);
      setInputValue('');
      
      // Send message to AI Coach API
      const response = await aiCoachAPI.chatWithCoach(inputValue);
      
      // Create AI response message
      const aiMessage = {
        id: Date.now() + 1,
        content: response.data.response,
        message_type: 'ai',
        timestamp: response.data.timestamp
      };
      
      // Add AI response to messages
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (err) {
      setError(handleApiError(err, 'Failed to send message'));
      
      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        content: "I apologize, but I'm having trouble responding right now. Please try again in a moment.",
        message_type: 'ai',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickPrompt = (prompt) => {
    setInputValue(prompt);
  };

  const quickPrompts = [
    "How can I stay motivated?",
    "Help me set better goals",
    "I'm feeling stuck lately",
    "Tips for better focus"
  ];

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <Loader2 size={48} className="animate-spin text-yellow-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white mb-2">AI Growth Coach</h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Get personalized guidance, insights, and motivation from your AI-powered personal development coach
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center space-x-2">
          <AlertCircle size={20} className="text-red-400" />
          <span className="text-red-400">{error}</span>
          <button
            onClick={initializeChat}
            className="ml-auto px-3 py-1 rounded bg-red-500 hover:bg-red-600 text-white text-sm transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Chat Area */}
        <div className="lg:col-span-2">
          <div className="h-96 bg-gradient-to-br from-gray-900/50 to-gray-800/30 rounded-xl border border-gray-800 flex flex-col">
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
                  <Bot size={20} style={{ color: '#0B0D14' }} />
                </div>
                <div>
                  <h3 className="font-semibold text-white">AI Coach</h3>
                  <p className="text-sm text-gray-400">Your personal growth assistant</p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div 
              ref={chatContainerRef}
              className="flex-1 p-4 overflow-y-auto"
            >
              {messages.map((message) => (
                <Message
                  key={message.id}
                  message={message}
                  isUser={message.message_type === 'user'}
                />
              ))}
              
              {isTyping && (
                <div className="flex items-start space-x-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                    <Bot size={16} className="text-yellow-400" />
                  </div>
                  <div className="bg-gray-800 text-white border border-gray-700 px-4 py-3 rounded-lg">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-700">
              <div className="flex space-x-2">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Share your thoughts, challenges, or goals..."
                  className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 transition-colors resize-none"
                  rows="1"
                  style={{ minHeight: '40px' }}
                  disabled={isTyping}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className="px-4 py-2 rounded-lg font-medium transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
                >
                  {isTyping ? (
                    <Loader2 size={18} className="animate-spin" />
                  ) : (
                    <Send size={18} />
                  )}
                </button>
              </div>
              
              {/* Quick Prompts */}
              <div className="flex flex-wrap gap-2 mt-3">
                {quickPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickPrompt(prompt)}
                    className="px-3 py-1 text-xs bg-gray-700 text-gray-300 rounded-full hover:bg-gray-600 transition-colors"
                    disabled={isTyping}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Insights Panel */}
        <div className="space-y-6">
          {/* Today's Insights */}
          <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
            <h3 className="text-lg font-semibold text-white mb-4">Today's Insights</h3>
            <div className="space-y-4">
              {userStats && (
                <>
                  <InsightCard
                    icon={Lightbulb}
                    title="Progress Recognition"
                    description={`You've completed ${userStats.habits_completed_today} out of ${userStats.total_habits} habits today!`}
                    action="View habit details →"
                    onClick={() => handleQuickPrompt("Tell me about my habit progress")}
                  />
                  <InsightCard
                    icon={Target}
                    title="Goal Alignment"
                    description={`You have ${userStats.total_tasks} tasks and ${userStats.courses_enrolled} courses in progress.`}
                    action="Explore learning →"
                    onClick={() => handleQuickPrompt("How can I better manage my learning goals?")}
                  />
                  <InsightCard
                    icon={TrendingUp}
                    title="Growth Journey"
                    description={`You've written ${userStats.total_journal_entries} journal entries for reflection.`}
                    action="See insights →"
                    onClick={() => handleQuickPrompt("What patterns do you see in my growth journey?")}
                  />
                </>
              )}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
            <h3 className="text-lg font-semibold text-white mb-4">Your Journey</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Chat sessions</span>
                <span className="text-white font-medium">{messages.length > 0 ? Math.ceil(messages.length / 4) : 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Goals discussed</span>
                <span className="text-white font-medium">{userStats?.total_tasks || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Growth score</span>
                <span className="text-yellow-400 font-medium">
                  {userStats ? Math.min(87 + (userStats.habits_completed_today * 5), 100) : 87}/100
                </span>
              </div>
            </div>
          </div>

          {/* Coach Tips */}
          <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
            <h3 className="text-lg font-semibold text-white mb-4">Coach Tips</h3>
            <div className="space-y-3 text-sm">
              <div className="p-3 bg-gray-800/50 rounded-lg">
                <p className="text-gray-300">💡 <strong>Be specific:</strong> The more detailed your questions, the better I can help you.</p>
              </div>
              <div className="p-3 bg-gray-800/50 rounded-lg">
                <p className="text-gray-300">🎯 <strong>Set intentions:</strong> Share your goals and I'll help you create actionable plans.</p>
              </div>
              <div className="p-3 bg-gray-800/50 rounded-lg">
                <p className="text-gray-300">📈 <strong>Track progress:</strong> Regular check-ins help maintain momentum and accountability.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AICoach;