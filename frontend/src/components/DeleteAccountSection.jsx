import React, { useState } from 'react';
import { useAuth } from '../contexts/BackendAuthContext';
import { ExclamationTriangleIcon, ArrowLeftIcon, TrashIcon } from '@heroicons/react/outline';
import api from '../services/api';

const DeleteAccountSection = ({ onBack }) => {
  const { user, logout } = useAuth();
  const [step, setStep] = useState(1); // 1: Warning, 2: Confirmation, 3: Processing
  const [confirmationText, setConfirmationText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState('');

  const handleDeleteAccount = async () => {
    if (confirmationText !== 'DELETE') {
      setError('Please type "DELETE" exactly as shown to confirm');
      return;
    }

    setIsDeleting(true);
    setError('');

    try {
      const response = await api.auth.deleteAccount({
        confirmation_text: confirmationText
      });

      if (response.data.success) {
        // Account deleted successfully - logout and show success message
        await logout();
        // Redirect to login page using window.location since we don't have React Router
        window.location.href = '/';
        // Note: We could also use a callback or state management to show success message
      }
    } catch (error) {
      console.error('Error deleting account:', error);
      setError(
        error.response?.data?.detail || 
        'Failed to delete account. Please try again or contact support.'
      );
      setIsDeleting(false);
    }
  };

  const renderStep1Warning = () => (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={onBack}
              className="mr-3 p-1 rounded-lg hover:bg-gray-700 transition-colors"
            >
              <ArrowLeftIcon className="h-5 w-5 text-gray-400" />
            </button>
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-400 mr-2" />
              <h2 className="text-xl font-semibold text-white">Delete Account</h2>
            </div>
          </div>
        </div>

        {/* Warning Content */}
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-red-400 font-semibold text-lg mb-2">
                This action cannot be undone
              </h3>
              <p className="text-gray-300 mb-4">
                Deleting your account will permanently remove all of your data from our servers. 
                This includes:
              </p>
              <ul className="text-gray-300 space-y-2 mb-6">
                <li className="flex items-center">
                  <span className="text-red-400 mr-2">•</span>
                  All your tasks, projects, areas, and pillars
                </li>
                <li className="flex items-center">
                  <span className="text-red-400 mr-2">•</span>
                  Journal entries and daily reflections
                </li>
                <li className="flex items-center">
                  <span className="text-red-400 mr-2">•</span>
                  AI Coach interactions and alignment scores
                </li>
                <li className="flex items-center">
                  <span className="text-red-400 mr-2">•</span>
                  File attachments and resources
                </li>
                <li className="flex items-center">
                  <span className="text-red-400 mr-2">•</span>
                  Account preferences and settings
                </li>
                <li className="flex items-center">
                  <span className="text-red-400 mr-2">•</span>
                  Your user profile and login credentials
                </li>
              </ul>
              <div className="bg-red-800/30 border border-red-700 rounded-lg p-3">
                <p className="text-red-300 text-sm font-medium">
                  ⚠️ There is no way to recover your data after deletion. Please ensure you have exported 
                  any important information before proceeding.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between">
          <button
            onClick={onBack}
            className="bg-gray-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => setStep(2)}
            className="bg-red-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors"
          >
            I Understand, Continue
          </button>
        </div>
      </div>
    </div>
  );

  const renderStep2Confirmation = () => (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => setStep(1)}
              className="mr-3 p-1 rounded-lg hover:bg-gray-700 transition-colors"
            >
              <ArrowLeftIcon className="h-5 w-5 text-gray-400" />
            </button>
            <div className="flex items-center">
              <TrashIcon className="h-6 w-6 text-red-400 mr-2" />
              <h2 className="text-xl font-semibold text-white">Confirm Account Deletion</h2>
            </div>
          </div>
        </div>

        {/* Confirmation Form */}
        <div className="space-y-4">
          <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
            <p className="text-gray-300 mb-3">
              You are about to delete the account for <span className="text-white font-medium">{user?.email}</span>.
            </p>
            <p className="text-red-300 text-sm font-medium mb-4">
              This action is permanent and cannot be reversed.
            </p>
          </div>

          <div>
            <label htmlFor="confirmation" className="block text-sm font-medium text-gray-300 mb-2">
              Type <span className="text-red-400 font-bold">DELETE</span> to confirm:
            </label>
            <input
              type="text"
              id="confirmation"
              value={confirmationText}
              onChange={(e) => {
                setConfirmationText(e.target.value);
                setError('');
              }}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="Type DELETE here..."
              disabled={isDeleting}
            />
            {error && (
              <p className="text-red-400 text-sm mt-2">{error}</p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between">
          <button
            onClick={() => setStep(1)}
            disabled={isDeleting}
            className="bg-gray-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Back
          </button>
          <button
            onClick={handleDeleteAccount}
            disabled={isDeleting || confirmationText !== 'DELETE'}
            className="bg-red-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isDeleting ? (
              <>
                <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Deleting Account...</span>
              </>
            ) : (
              <>
                <TrashIcon className="h-4 w-4" />
                <span>Delete My Account</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto">
      {step === 1 && renderStep1Warning()}
      {step === 2 && renderStep2Confirmation()}
    </div>
  );
};

export default DeleteAccountSection;