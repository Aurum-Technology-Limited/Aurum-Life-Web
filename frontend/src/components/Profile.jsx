import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { User, Mail, Edit2, Save, X, AlertCircle, CheckCircle2, MessageCircle, LogOut, Bell } from 'lucide-react';

const Profile = ({ onSectionChange }) => {
  const { user, updateProfile, logout } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'
  
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
  });

  const handleEdit = () => {
    setFormData({
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
    });
    setIsEditing(true);
    setMessage('');
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
    });
    setMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    const result = await updateProfile(formData);
    
    if (result.success) {
      setIsEditing(false);
      setMessage('Profile updated successfully!');
      setMessageType('success');
      setTimeout(() => setMessage(''), 3000);
    } else {
      setMessage(result.error || 'Failed to update profile');
      setMessageType('error');
    }
    
    setLoading(false);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
            My Profile
          </h1>
          <p className="text-gray-400 mt-1">
            Manage your account information
          </p>
        </div>

        {/* Message Display */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center ${
            messageType === 'success' 
              ? 'bg-green-900/20 border border-green-600 text-green-400'
              : 'bg-red-900/20 border border-red-600 text-red-400'
          }`}>
            {messageType === 'success' ? (
              <CheckCircle2 className="h-5 w-5 mr-3" />
            ) : (
              <AlertCircle className="h-5 w-5 mr-3" />
            )}
            <span>{message}</span>
          </div>
        )}

        {/* Profile Card */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-full flex items-center justify-center">
                <User className="h-8 w-8 text-gray-900" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">
                  {user?.first_name} {user?.last_name}
                </h2>
                <p className="text-gray-400">@{user?.username}</p>
              </div>
            </div>
            
            {!isEditing && (
              <button
                onClick={handleEdit}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <Edit2 className="h-4 w-4" />
                <span>Edit Profile</span>
              </button>
            )}
          </div>

          {isEditing ? (
            /* Edit Form */
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="Enter first name"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="Enter last name"
                    required
                  />
                </div>
              </div>

              <div className="flex space-x-4 pt-4">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                >
                  <X className="h-4 w-4" />
                  <span>Cancel</span>
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors"
                  style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
                >
                  <Save className="h-4 w-4" />
                  <span>{loading ? 'Saving...' : 'Save Changes'}</span>
                </button>
              </div>
            </form>
          ) : (
            /* Profile Display */
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Email Address</label>
                <div className="flex items-center space-x-3">
                  <Mail className="h-5 w-5 text-gray-400" />
                  <span className="text-white">{user?.email}</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Full Name</label>
                <div className="flex items-center space-x-3">
                  <User className="h-5 w-5 text-gray-400" />
                  <span className="text-white">
                    {user?.first_name} {user?.last_name}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{user?.level}</div>
                  <div className="text-sm text-gray-400">Level</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{user?.total_points}</div>
                  <div className="text-sm text-gray-400">Total Points</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{user?.current_streak}</div>
                  <div className="text-sm text-gray-400">Current Streak</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Account Actions */}
        <div className="mt-8 bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Help & Account</h3>
          <div className="space-y-3">
            {/* Send Feedback Button */}
            <button
              onClick={() => onSectionChange && onSectionChange('feedback')}
              className="w-full flex items-center space-x-3 px-4 py-3 bg-green-900/20 hover:bg-green-900/30 border border-green-700/30 hover:border-green-600/50 text-green-400 rounded-lg transition-all duration-200 group"
            >
              <div className="p-2 rounded-lg bg-green-500/20 group-hover:bg-green-500/30 transition-colors duration-200">
                <MessageCircle className="h-4 w-4 text-green-400" />
              </div>
              <div className="flex-1 text-left">
                <p className="text-green-400 font-medium text-sm">Send Feedback</p>
                <p className="text-green-500/70 text-xs">Share your thoughts and suggestions</p>
              </div>
            </button>

            {/* Notifications Button */}
            <button
              onClick={() => onSectionChange && onSectionChange('notification-settings')}
              className="w-full flex items-center space-x-3 px-4 py-3 bg-blue-900/20 hover:bg-blue-900/30 border border-blue-700/30 hover:border-blue-600/50 text-blue-400 rounded-lg transition-all duration-200 group"
            >
              <div className="p-2 rounded-lg bg-blue-500/20 group-hover:bg-blue-500/30 transition-colors duration-200">
                <Bell className="h-4 w-4 text-blue-400" />
              </div>
              <div className="flex-1 text-left">
                <p className="text-blue-400 font-medium text-sm">Notifications</p>
                <p className="text-blue-500/70 text-xs">Manage notification preferences</p>
              </div>
            </button>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="w-full flex items-center space-x-3 px-4 py-3 bg-red-900/20 hover:bg-red-900/30 border border-red-700/30 hover:border-red-600/50 text-red-400 rounded-lg transition-all duration-200 group"
            >
              <div className="p-2 rounded-lg bg-red-500/20 group-hover:bg-red-500/30 transition-colors duration-200">
                <LogOut className="h-4 w-4 text-red-400" />
              </div>
              <div className="flex-1 text-left">
                <p className="text-red-400 font-medium text-sm">Sign Out</p>
                <p className="text-red-500/70 text-xs">Sign out of your account</p>
              </div>
            </button>
          </div>
        </div>

        {/* Account Info */}
        <div className="mt-6 text-center text-sm text-gray-400">
          <p>Member since {new Date(user?.created_at).toLocaleDateString()}</p>
        </div>
      </div>
    </div>
  );
};

export default Profile;