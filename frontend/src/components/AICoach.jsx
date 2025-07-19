import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, Bot, User, Lightbulb, Target, TrendingUp } from 'lucide-react';
import { mockChatMessages, getStoredData, setStoredData } from '../data/mock';

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
    </div>
  </div>
);

const InsightCard = ({ icon: Icon, title, description, action }) => (
  <div className="p-4 rounded-lg border border-gray-700 bg-gray-800/50 hover:bg-gray-700/50 transition-colors">
    <div className="flex items-center space-x-3 mb-3">
      <div className="w-8 h-8 rounded-lg bg-yellow-400 flex items-center justify-center">
        <Icon size={16} style={{ color: '#0B0D14' }} />
      </div>
      <h3 className="font-semibold text-white">{title}</h3>
    </div>
    <p className="text-sm text-gray-400 mb-3">{description}</p>
    {action && (
      <button className="text-sm text-yellow-400 hover:text-yellow-300 transition-colors">
        {action}
      </button>
    )}
  </div>
);

const AICoach = () => {
  const [messages, setMessages] = useState(() => getStoredData('chat_messages', mockChatMessages));
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    setStoredData('chat_messages', messages);
  }, [messages]);

  const generateAIResponse = (userMessage) => {
    const responses = [
      "That's a great insight! Building self-awareness is the first step toward meaningful change. Have you considered setting specific daily practices to reinforce this?",
      "I understand your perspective. It's normal to feel overwhelmed sometimes. Let's break this down into smaller, manageable steps.",
      "Your commitment to growth is inspiring! Based on what you've shared, I'd recommend focusing on consistency rather than perfection.",
      "That's a common challenge many people face. What if we explored some mindfulness techniques that could help you navigate these situations?",
      "I can sense you're making real progress. Remember, growth isn't always linear - every step forward counts, even the small ones.",
      "Your reflection shows deep self-awareness. How do you think you could apply this insight to other areas of your life?",
      "That's a wonderful goal! Let's create a specific action plan that aligns with your values and current habits.",
      "I appreciate your honesty. Vulnerability is actually a strength and shows you're ready for genuine growth."
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response delay
    setTimeout(() => {
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: generateAIResponse(inputValue),
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickPrompts = [
    "How can I stay motivated?",
    "Help me set better goals",
    "I'm feeling stuck lately",
    "Tips for better focus"
  ];

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white mb-2">AI Growth Coach</h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Get personalized guidance, insights, and motivation from your AI-powered personal development coach
        </p>
      </div>

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
                  isUser={message.type === 'user'}
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
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className="px-4 py-2 rounded-lg font-medium transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
                >
                  <Send size={18} />
                </button>
              </div>
              
              {/* Quick Prompts */}
              <div className="flex flex-wrap gap-2 mt-3">
                {quickPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => setInputValue(prompt)}
                    className="px-3 py-1 text-xs bg-gray-700 text-gray-300 rounded-full hover:bg-gray-600 transition-colors"
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
              <InsightCard
                icon={Lightbulb}
                title="Progress Recognition"
                description="You've maintained your meditation streak for 15 days straight!"
                action="View habit details →"
              />
              <InsightCard
                icon={Target}
                title="Goal Alignment"
                description="Your learning activities are well-aligned with your growth objectives."
                action="Explore more courses →"
              />
              <InsightCard
                icon={TrendingUp}
                title="Momentum Building"
                description="Your task completion rate has improved 23% this week."
                action="See full analytics →"
              />
            </div>
          </div>

          {/* Quick Stats */}
          <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
            <h3 className="text-lg font-semibold text-white mb-4">Your Journey</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Sessions with AI</span>
                <span className="text-white font-medium">24</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Goals achieved</span>
                <span className="text-white font-medium">8</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Growth score</span>
                <span className="text-yellow-400 font-medium">87/100</span>
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