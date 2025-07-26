import React, { useState } from 'react';
import { Send, MessageSquare, Bug, Lightbulb, Heart, Star } from 'lucide-react';
import { useAuth } from '../contexts/SupabaseAuthContext';
import { useNotification } from '../contexts/NotificationContext';

const Feedback = () => {
  const { user } = useAuth();
  const { addNotification } = useNotification();
  
  const [feedbackType, setFeedbackType] = useState('general');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [rating, setRating] = useState(0);
  const [loading, setLoading] = useState(false);

  const feedbackTypes = [
    { id: 'general', label: 'General Feedback', icon: MessageSquare, color: 'text-blue-500' },
    { id: 'bug', label: 'Bug Report', icon: Bug, color: 'text-red-500' },
    { id: 'feature', label: 'Feature Request', icon: Lightbulb, color: 'text-yellow-500' },
    { id: 'appreciation', label: 'Appreciation', icon: Heart, color: 'text-pink-500' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Simulate API call - replace with actual feedback submission
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      addNotification({
        type: 'success',
        title: 'Feedback Submitted',
        message: 'Thank you for your feedback! We\'ll review it and get back to you if needed.'
      });

      // Reset form
      setSubject('');
      setMessage('');
      setRating(0);
      setFeedbackType('general');
      
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Submission Failed',
        message: 'Failed to submit feedback. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  const selectedType = feedbackTypes.find(type => type.id === feedbackType);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white mb-4">Feedback & Support</h1>
        <p className="text-gray-400 text-lg">
          Help us improve Aurum Life by sharing your thoughts, reporting issues, or requesting features
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Feedback Form */}
        <div className="lg:col-span-2">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-6">Submit Feedback</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Feedback Type */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3">
                  Feedback Type
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {feedbackTypes.map((type) => {
                    const Icon = type.icon;
                    return (
                      <button
                        key={type.id}
                        type="button"
                        onClick={() => setFeedbackType(type.id)}
                        className={`
                          p-4 border rounded-lg text-left transition-colors
                          ${feedbackType === type.id
                            ? 'border-yellow-500 bg-yellow-500/10'
                            : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                          }
                        `}
                      >
                        <div className="flex items-center gap-3">
                          <Icon className={`h-5 w-5 ${type.color}`} />
                          <span className="text-white font-medium">{type.label}</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Rating (for general feedback and appreciation) */}
              {(feedbackType === 'general' || feedbackType === 'appreciation') && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">
                    How would you rate your experience?
                  </label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setRating(star)}
                        className={`
                          p-1 rounded transition-colors
                          ${star <= rating ? 'text-yellow-500' : 'text-gray-600 hover:text-yellow-400'}
                        `}
                      >
                        <Star className="h-8 w-8 fill-current" />
                      </button>
                    ))}
                  </div>
                  {rating > 0 && (
                    <p className="text-sm text-gray-400 mt-2">
                      {rating === 1 && "We're sorry to hear that. Please let us know how we can improve."}
                      {rating === 2 && "We appreciate your feedback. How can we do better?"}
                      {rating === 3 && "Thanks for the feedback. What would make it better?"}
                      {rating === 4 && "Great! We'd love to know what we're doing right."}
                      {rating === 5 && "Awesome! We're thrilled you're enjoying Aurum Life."}
                    </p>
                  )}
                </div>
              )}

              {/* Subject */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Subject
                </label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder={
                    feedbackType === 'bug' ? 'Brief description of the issue' :
                    feedbackType === 'feature' ? 'Feature you\'d like to see' :
                    feedbackType === 'appreciation' ? 'What you love about Aurum Life' :
                    'Brief summary of your feedback'
                  }
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  required
                />
              </div>

              {/* Message */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Message
                </label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows={6}
                  placeholder={
                    feedbackType === 'bug' ? 'Please describe the bug in detail. Include steps to reproduce, expected behavior, and what actually happened.' :
                    feedbackType === 'feature' ? 'Describe the feature you\'d like to see and how it would help you.' :
                    feedbackType === 'appreciation' ? 'Tell us what you love about Aurum Life and how it\'s helping you.' :
                    'Share your thoughts, suggestions, or any other feedback you have for us.'
                  }
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500 resize-none"
                  required
                />
              </div>

              {/* User Info */}
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-300 mb-2">Your Information</h3>
                <div className="text-sm text-gray-400 space-y-1">
                  <p>Email: {user?.email}</p>
                  <p>Username: {user?.username}</p>
                  <p>User Level: {user?.level || 1}</p>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  This information helps us provide better support and follow up if needed.
                </p>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600 disabled:bg-yellow-700 font-semibold flex items-center justify-center gap-2 transition-colors"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-gray-900 border-t-transparent rounded-full animate-spin"></div>
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="h-5 w-5" />
                    Submit Feedback
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button
                onClick={() => setFeedbackType('bug')}
                className="w-full text-left p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Bug className="h-5 w-5 text-red-500" />
                  <div>
                    <div className="text-white font-medium">Report a Bug</div>
                    <div className="text-gray-400 text-sm">Something not working?</div>
                  </div>
                </div>
              </button>
              
              <button
                onClick={() => setFeedbackType('feature')}
                className="w-full text-left p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Lightbulb className="h-5 w-5 text-yellow-500" />
                  <div>
                    <div className="text-white font-medium">Request Feature</div>
                    <div className="text-gray-400 text-sm">Have an idea?</div>
                  </div>
                </div>
              </button>
              
              <button
                onClick={() => setFeedbackType('appreciation')}
                className="w-full text-left p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Heart className="h-5 w-5 text-pink-500" />
                  <div>
                    <div className="text-white font-medium">Share Love</div>
                    <div className="text-gray-400 text-sm">Tell us what you love</div>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Contact Info */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Other Ways to Reach Us</h3>
            <div className="space-y-3 text-sm">
              <div>
                <div className="text-gray-300 font-medium">Email Support</div>
                <div className="text-gray-400">support@aurumlife.com</div>
              </div>
              <div>
                <div className="text-gray-300 font-medium">Response Time</div>
                <div className="text-gray-400">Usually within 24 hours</div>
              </div>
              <div>
                <div className="text-gray-300 font-medium">Community</div>
                <div className="text-gray-400">Join our Discord server</div>
              </div>
            </div>
          </div>

          {/* Tips */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Tips for Better Feedback</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>• Be specific about the issue or suggestion</li>
              <li>• Include steps to reproduce bugs</li>
              <li>• Mention your browser and device</li>
              <li>• Screenshots help us understand better</li>
              <li>• Tell us how it affects your workflow</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Feedback;