import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, Bot, User, Lightbulb, Target, TrendingUp, Loader2, AlertCircle } from 'lucide-react';
import { chatAPI, statsAPI, handleApiError } from '../services/api';

const Message = ({ message, isUser }) => (
  <div className={`flex items-start space-x-3 mb-6 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
      isUser ? 'bg-yellow-400' : 'bg-gray-700'
    }`}>
      {isUser ? (
        <User size={16} style={{ color: '#0B0D14' }} />
      ) : (
        <Bot size={16} className="text-yellow-400" />
      )}
    </div>
    <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
      isUser 
        ? 'bg-yellow-400 text-gray-900' 
        : 'bg-gray-800 text-white border border-gray-700'
    }`}>
      <p className="text-sm leading-relaxed">{message.content}</p>
      <p className="text-xs mt-2 opacity-70">
        {new Date(message.timestamp).toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit'
        })}
      </p>
    </div>
  </div>
);

const InsightCard = ({ icon: Icon, title, description, action, onClick }) => (
  <div 
    className="p-4 rounded-lg border border-gray-700 bg-gray-800/50 hover:bg-gray-700/50 transition-colors cursor-pointer"
    onClick={onClick}
  >
    <div className="flex items-center space-x-3 mb-3">
      <div className="w-8 h-8 rounded-lg bg-yellow-400 flex items-center justify-center">
        <Icon size={16} style={{ color: '#0B0D14' }} />
      </div>
      <h3 className="font-semibold text-white">{title}</h3>
    </div>
    <p className="text-sm text-gray-400 mb-3">{description}</p>
    {action && (
      <p className="text-sm text-yellow-400 hover:text-yellow-300 transition-colors">
        {action}
      </p>
    )}
  </div>
);

const AICoach = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}`);
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
      
      // Load existing messages for this session
      const messagesResponse = await chatAPI.getMessages(sessionId);
      setMessages(messagesResponse.data);
      
      // Load user stats for insights
      const statsResponse = await statsAPI.getUserStats();
      setUserStats(statsResponse.data);
      
      // If no messages exist, send welcome message
      if (messagesResponse.data.length === 0) {
        await sendWelcomeMessage();
      }
    } catch (err) {
      setError(handleApiError(err, 'Failed to initialize chat'));
    } finally {
      setLoading(false);
    }
  };

  const sendWelcomeMessage = async () => {
    const welcomeMessage = {
      session_id: sessionId,
      message_type: 'ai',
      content: "Hello! I'm your AI Growth Coach. I'm here to help you on your personal development journey. How are you feeling about your progress today?"
    };
    
    try {
      const response = await chatAPI.sendMessage(welcomeMessage);
      setMessages([response.data]);
    } catch (err) {
      console.error('Failed to send welcome message:', err);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      session_id: sessionId,
      message_type: 'user',
      content: inputValue
    };

    try {
      setIsTyping(true);
      
      // Send user message to backend
      const response = await chatAPI.sendMessage(userMessage);
      
      // Refresh messages to get both user message and AI response
      setTimeout(async () => {
        try {
          const messagesResponse = await chatAPI.getMessages(sessionId);
          setMessages(messagesResponse.data);
        } catch (err) {
          console.error('Failed to refresh messages:', err);
        }
        setIsTyping(false);
      }, 1000);
      
    } catch (err) {
      setError(handleApiError(err, 'Failed to send message'));
      setIsTyping(false);
    }

    setInputValue('');
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