import React, { useState } from 'react';
import { Send, MessageSquare, HelpCircle, Bug, Lightbulb, Heart, CheckCircle } from 'lucide-react';
import { feedbackAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Feedback = () => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    category: '',
    subject: '',
    message: '',
    email: user?.email || ''
  });
  
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const feedbackCategories = [
    { value: 'suggestion', label: 'Feature Suggestion', icon: Lightbulb, description: 'Ideas for new features or improvements' },
    { value: 'bug_report', label: 'Bug Report', icon: Bug, description: 'Something is not working correctly' },
    { value: 'general_feedback', label: 'General Feedback', icon: MessageSquare, description: 'Overall thoughts about the app' },
    { value: 'support_request', label: 'Support Request', icon: HelpCircle, description: 'Need help with something' },
    { value: 'compliment', label: 'Compliment', icon: Heart, description: 'Share what you love about Aurum Life' },
  ];

  const handleCategoryChange = (e) => {
    const selectedCategory = e.target.value;
    setFormData({ 
      ...formData, 
      category: selectedCategory,
      subject: selectedCategory ? feedbackCategories.find(cat => cat.value === selectedCategory)?.label || '' : ''
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.category || !formData.message.trim()) {
      setError('Please select a category and provide your message.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await feedbackAPI.submitFeedback({
        category: formData.category,
        subject: formData.subject,
        message: formData.message.trim(),
        email: formData.email,
        user_name: user ? `${user.first_name} ${user.last_name}` : 'Anonymous'
      });

      setSuccess(true);
      setFormData({
        category: '',
        subject: '',
        message: '',
        email: user?.email || ''
      });

      // Reset success message after 5 seconds
      setTimeout(() => setSuccess(false), 5000);

    } catch (err) {
      setError('Failed to submit feedback. Please try again later.');
      console.error('Feedback submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectedCategory = feedbackCategories.find(cat => cat.value === formData.category);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <MessageSquare className="h-12 w-12 text-yellow-500 mr-3" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-yellow-400 to-yellow-600 bg-clip-text text-transparent">
              Feedback & Support
            </h1>
          </div>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Your thoughts and suggestions help us make Aurum Life better for everyone. 
            We read every message and appreciate your input!
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-900/20 border border-green-600 rounded-lg p-4 mb-6 flex items-center">
            <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-green-400 font-semibold">Thank You!</h3>
              <p className="text-green-300 text-sm">
                Your feedback has been sent successfully. We'll get back to you soon!
              </p>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-600 rounded-lg p-4 mb-6">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {/* Feedback Form */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Category Selection */}
            <div>
              <label className="block text-lg font-semibold text-gray-300 mb-4">
                What type of feedback would you like to share?
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {feedbackCategories.map((category) => {
                  const Icon = category.icon;
                  const isSelected = formData.category === category.value;
                  
                  return (
                    <div
                      key={category.value}
                      className={`relative cursor-pointer rounded-lg border-2 p-4 transition-all duration-200 ${
                        isSelected
                          ? 'border-yellow-500 bg-yellow-500/10'
                          : 'border-gray-700 bg-gray-800/30 hover:border-gray-600 hover:bg-gray-800/50'
                      }`}
                      onClick={() => handleCategoryChange({ target: { value: category.value } })}
                    >
                      <input
                        type="radio"
                        name="category"
                        value={category.value}
                        checked={isSelected}
                        onChange={handleCategoryChange}
                        className="sr-only"
                      />
                      <div className="flex items-start">
                        <Icon className={`h-6 w-6 mt-1 mr-3 ${isSelected ? 'text-yellow-500' : 'text-gray-400'}`} />
                        <div>
                          <h3 className={`font-semibold ${isSelected ? 'text-yellow-500' : 'text-white'}`}>
                            {category.label}
                          </h3>
                          <p className="text-sm text-gray-400 mt-1">
                            {category.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Subject Field (auto-populated based on category) */}
            {selectedCategory && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Subject
                </label>
                <input
                  type="text"
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                  placeholder="Brief description of your feedback"
                />
              </div>
            )}

            {/* Message Field */}
            {formData.category && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Your Message
                </label>
                <textarea
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  rows="6"
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent resize-vertical"
                  placeholder={`Tell us more about your ${selectedCategory?.label.toLowerCase()}...`}
                  required
                />
                <div className="flex justify-between items-center mt-2">
                  <p className="text-xs text-gray-500">
                    Please be as detailed as possible to help us understand your feedback.
                  </p>
                  <span className="text-xs text-gray-500">
                    {formData.message.length}/1000 characters
                  </span>
                </div>
              </div>
            )}

            {/* Email Field */}
            {formData.category && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email Address (for follow-up)
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                  placeholder="your@email.com"
                />
                <p className="text-xs text-gray-500 mt-1">
                  We'll only use this to respond to your feedback if needed.
                </p>
              </div>
            )}

            {/* Submit Button */}
            {formData.category && (
              <div className="pt-4">
                <button
                  type="submit"
                  disabled={loading || !formData.message.trim()}
                  className="w-full md:w-auto bg-gradient-to-r from-yellow-600 to-yellow-500 hover:from-yellow-500 hover:to-yellow-400 disabled:from-gray-700 disabled:to-gray-600 disabled:cursor-not-allowed text-white font-semibold px-8 py-3 rounded-lg transition-all duration-200 flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send className="h-5 w-5 mr-2" />
                      Send Feedback
                    </>
                  )}
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Footer Note */}
        <div className="text-center mt-8 p-6 bg-gray-900/30 rounded-lg border border-gray-800">
          <h3 className="text-lg font-semibold text-yellow-500 mb-2">We Value Your Input</h3>
          <p className="text-gray-400 text-sm max-w-2xl mx-auto">
            Your feedback is sent directly to our development team. We review every submission and 
            use your insights to prioritize improvements and new features for Aurum Life.
          </p>
          <p className="text-xs text-gray-500 mt-3">
            Response time: 1-3 business days for most inquiries
          </p>
        </div>
      </div>
    </div>
  );
};

export default Feedback;