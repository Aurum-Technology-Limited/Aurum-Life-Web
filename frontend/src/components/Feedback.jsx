import React, { useState } from 'react';
import { useAuth } from '../contexts/BackendAuthContext';
import { ChatAltIcon, PaperAirplaneIcon } from '@heroicons/react/outline';
import api from '../services/api';

const Feedback = () => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    subject: '',
    message: '',
    category: 'suggestion',
    priority: 'medium'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      // Use centralized API client for authenticated requests
      const response = await api.feedback.submitFeedback(formData);
      
      if (response.status === 201) {
        setSubmitted(true);
        setFormData({
          subject: '',
          message: '',
          category: 'suggestion',
          priority: 'medium'
        });
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      
      // Handle specific error types
      if (error.response?.status === 422) {
        setError('Please check your input and try again.');
      } else if (error.response?.status === 401) {
        setError('Please log in again to submit feedback.');
      } else if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else if (error.message.includes('Network Error')) {
        setError('Network error. Please check your connection and try again.');
      } else {
        setError('Failed to submit feedback. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-green-900 border border-green-700 rounded-lg p-6 text-center">
          <div className="text-green-400 mb-4">
            <ChatAltIcon className="h-12 w-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">
            Thank you, your feedback has been sent!
          </h2>
          <p className="text-green-300 mb-4">
            We've received your message and our team will review it carefully. You should also receive an email confirmation shortly.
          </p>
          <button
            onClick={() => {
              setSubmitted(false);
              setError('');
            }}
            className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-medium hover:bg-yellow-600 transition-colors"
          >
            Submit More Feedback
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">Share Your Feedback</h1>
        <p className="text-gray-400">
          Help us improve Aurum Life by sharing your thoughts, suggestions, or reporting issues.
        </p>
      </div>

      {error && (
        <div className="bg-red-900 border border-red-700 text-red-300 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-300 mb-2">
                Category
              </label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              >
                <option value="suggestion">Suggestion</option>
                <option value="bug_report">Bug Report</option>
                <option value="feature_request">Feature Request</option>
                <option value="question">Question</option>
                <option value="complaint">Complaint</option>
                <option value="compliment">Compliment</option>
              </select>
            </div>

            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-300 mb-2">
                Priority
              </label>
              <select
                id="priority"
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="subject" className="block text-sm font-medium text-gray-300 mb-2">
              Subject
            </label>
            <input
              type="text"
              id="subject"
              name="subject"
              value={formData.subject}
              onChange={handleInputChange}
              placeholder="Brief description of your feedback"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-300 mb-2">
              Message
            </label>
            <textarea
              id="message"
              name="message"
              rows={6}
              value={formData.message}
              onChange={handleInputChange}
              placeholder="Please provide detailed feedback..."
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:ring-2 focus:ring-yellow-500 focus:border-transparent resize-none"
              required
            />
          </div>

          <div className="flex items-center justify-between pt-4">
            <div className="text-sm text-gray-400">
              {user?.email && (
                <span>Feedback will be sent from: {user.email}</span>
              )}
            </div>
            
            <button
              type="submit"
              disabled={isSubmitting}
              className="bg-yellow-500 text-black px-6 py-2 rounded-lg font-medium hover:bg-yellow-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-black" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <PaperAirplaneIcon className="h-4 w-4" />
                  <span>Send Feedback</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      <div className="mt-6 text-center text-gray-400 text-sm">
        <p>
          Your feedback helps us create a better experience for everyone. 
          We read every message and appreciate your input!
        </p>
      </div>
    </div>
  );
};

export default Feedback;