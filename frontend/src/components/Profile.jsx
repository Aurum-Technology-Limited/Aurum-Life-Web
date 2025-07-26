import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import { 
  User, 
  Mail, 
  Calendar, 
  Trophy, 
  Target, 
  Edit2, 
  Save, 
  X, 
  Camera,
  Shield,
  Bell,
  Palette,
  Globe,
  Lock
} from 'lucide-react';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const { addNotification } = useNotification();
  
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    bio: '',
    location: '',
    website: '',
    timezone: '',
    language: 'en',
    theme: 'dark',
    notifications_enabled: true,
    email_notifications: true,
    push_notifications: true
  });

  // Initialize form data when user data is available
  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        username: user.username || '',
        email: user.email || '',
        bio: user.bio || '',
        location: user.location || '',
        website: user.website || '',
        timezone: user.timezone || '',
        language: user.language || 'en',
        theme: user.theme || 'dark',
        notifications_enabled: user.notifications_enabled ?? true,
        email_notifications: user.email_notifications ?? true,
        push_notifications: user.push_notifications ?? true
      });
    }
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    
    try {
      const result = await updateProfile(formData);
      
      if (result.success) {
        addNotification({
          type: 'success',
          title: 'Profile Updated',
          message: 'Your profile has been updated successfully.'
        });
        setIsEditing(false);
      } else {
        addNotification({
          type: 'error',
          title: 'Update Failed',
          message: result.error || 'Failed to update profile.'
        });
      }
    } catch (error) {
      console.error('Profile update error:', error);
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: 'An unexpected error occurred.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    // Reset form data to original user data
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        username: user.username || '',
        email: user.email || '',
        bio: user.bio || '',
        location: user.location || '',
        website: user.website || '',
        timezone: user.timezone || '',
        language: user.language || 'en',
        theme: user.theme || 'dark',
        notifications_enabled: user.notifications_enabled ?? true,
        email_notifications: user.email_notifications ?? true,
        push_notifications: user.push_notifications ?? true
      });
    }
    setIsEditing(false);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getInitials = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`;
    } else if (user?.username) {
      return user.username.slice(0, 2).toUpperCase();
    } else if (user?.email) {
      return user.email.slice(0, 2).toUpperCase();
    }
    return 'U';
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Profile</h1>
          <p className="text-gray-400 mt-1">Manage your account settings and preferences</p>
        </div>
        
        {!isEditing ? (
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600 flex items-center gap-2"
          >
            <Edit2 className="h-4 w-4" />
            Edit Profile
          </button>
        ) : (
          <div className="flex gap-3">
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 flex items-center gap-2"
            >
              <X className="h-4 w-4" />
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={loading}
              className="px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600 disabled:bg-yellow-700 flex items-center gap-2"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-gray-900 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Save className="h-4 w-4" />
              )}
              Save Changes
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Overview */}
        <div className="lg:col-span-1">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 space-y-6">
            {/* Avatar */}
            <div className="text-center">
              <div className="relative inline-block">
                <div className="w-24 h-24 bg-yellow-500 rounded-full flex items-center justify-center text-2xl font-bold text-gray-900">
                  {user.profile_picture ? (
                    <img 
                      src={user.profile_picture} 
                      alt="Profile" 
                      className="w-24 h-24 rounded-full object-cover"
                    />
                  ) : (
                    getInitials()
                  )}
                </div>
                {isEditing && (
                  <button className="absolute bottom-0 right-0 w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center text-white hover:bg-gray-600">
                    <Camera className="h-4 w-4" />
                  </button>
                )}
              </div>
              
              <div className="mt-4">
                <h2 className="text-xl font-semibold text-white">
                  {user.first_name && user.last_name 
                    ? `${user.first_name} ${user.last_name}`
                    : user.username || 'User'
                  }
                </h2>
                <p className="text-gray-400">@{user.username || 'username'}</p>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-2xl font-bold text-yellow-500">{user.level || 1}</div>
                <div className="text-gray-400 text-sm">Level</div>
              </div>
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-2xl font-bold text-yellow-500">{user.total_points || 0}</div>
                <div className="text-gray-400 text-sm">Points</div>
              </div>
            </div>

            {/* Streak */}
            {user.current_streak > 0 && (
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-2xl">🔥</div>
                <div className="text-lg font-semibold text-white">{user.current_streak} Days</div>
                <div className="text-gray-400 text-sm">Current Streak</div>
              </div>
            )}

            {/* Member Since */}
            <div className="text-center text-sm text-gray-400">
              <Calendar className="h-4 w-4 inline mr-2" />
              Member since {formatDate(user.created_at)}
            </div>
          </div>
        </div>

        {/* Profile Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Personal Information */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-6">
              <User className="h-5 w-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-white">Personal Information</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  First Name
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  />
                ) : (
                  <p className="text-white py-2">{user.first_name || 'Not set'}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Last Name
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  />
                ) : (
                  <p className="text-white py-2">{user.last_name || 'Not set'}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Username
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  />
                ) : (
                  <p className="text-white py-2">{user.username || 'Not set'}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email
                </label>
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-gray-400" />
                  <p className="text-white py-2">{user.email}</p>
                </div>
                <p className="text-xs text-gray-500 mt-1">Email cannot be changed here</p>
              </div>
            </div>
            
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Bio
              </label>
              {isEditing ? (
                <textarea
                  name="bio"
                  value={formData.bio}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  placeholder="Tell us about yourself..."
                />
              ) : (
                <p className="text-white py-2">{user.bio || 'No bio added yet'}</p>
              )}
            </div>
          </div>

          {/* Contact & Location */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-6">
              <Globe className="h-5 w-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-white">Contact & Location</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Location
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="City, Country"
                  />
                ) : (
                  <p className="text-white py-2">{user.location || 'Not set'}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Website
                </label>
                {isEditing ? (
                  <input
                    type="url"
                    name="website"
                    value={formData.website}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="https://yourwebsite.com"
                  />
                ) : (
                  <p className="text-white py-2">
                    {user.website ? (
                      <a 
                        href={user.website} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-yellow-500 hover:text-yellow-400"
                      >
                        {user.website}
                      </a>
                    ) : (
                      'Not set'
                    )}
                  </p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Timezone
                </label>
                {isEditing ? (
                  <select
                    name="timezone"
                    value={formData.timezone}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  >
                    <option value="">Select timezone</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                    <option value="Europe/London">London</option>
                    <option value="Europe/Paris">Paris</option>
                    <option value="Asia/Tokyo">Tokyo</option>
                    <option value="Asia/Shanghai">Shanghai</option>
                    <option value="Australia/Sydney">Sydney</option>
                  </select>
                ) : (
                  <p className="text-white py-2">{user.timezone || 'Not set'}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Language
                </label>
                {isEditing ? (
                  <select
                    name="language"
                    value={formData.language}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  >
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                    <option value="it">Italian</option>
                    <option value="pt">Portuguese</option>
                    <option value="ja">Japanese</option>
                    <option value="ko">Korean</option>
                    <option value="zh">Chinese</option>
                  </select>
                ) : (
                  <p className="text-white py-2">
                    {user.language === 'en' ? 'English' : 
                     user.language === 'es' ? 'Spanish' :
                     user.language === 'fr' ? 'French' :
                     user.language === 'de' ? 'German' :
                     user.language === 'it' ? 'Italian' :
                     user.language === 'pt' ? 'Portuguese' :
                     user.language === 'ja' ? 'Japanese' :
                     user.language === 'ko' ? 'Korean' :
                     user.language === 'zh' ? 'Chinese' : 'English'}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-6">
              <Palette className="h-5 w-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-white">Preferences</h3>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Theme
                </label>
                {isEditing ? (
                  <select
                    name="theme"
                    value={formData.theme}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  >
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                    <option value="auto">Auto</option>
                  </select>
                ) : (
                  <p className="text-white py-2 capitalize">{user.theme || 'Dark'}</p>
                )}
              </div>
            </div>
          </div>

          {/* Notification Settings */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-6">
              <Bell className="h-5 w-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-white">Notification Settings</h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white font-medium">Enable Notifications</div>
                  <div className="text-gray-400 text-sm">Receive notifications about your progress</div>
                </div>
                {isEditing ? (
                  <input
                    type="checkbox"
                    name="notifications_enabled"
                    checked={formData.notifications_enabled}
                    onChange={handleInputChange}
                    className="w-4 h-4 text-yellow-500 bg-gray-800 border-gray-700 rounded focus:ring-yellow-500"
                  />
                ) : (
                  <div className={`w-4 h-4 rounded ${user.notifications_enabled ? 'bg-yellow-500' : 'bg-gray-600'}`} />
                )}
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white font-medium">Email Notifications</div>
                  <div className="text-gray-400 text-sm">Receive email updates and reminders</div>
                </div>
                {isEditing ? (
                  <input
                    type="checkbox"
                    name="email_notifications"
                    checked={formData.email_notifications}
                    onChange={handleInputChange}
                    className="w-4 h-4 text-yellow-500 bg-gray-800 border-gray-700 rounded focus:ring-yellow-500"
                  />
                ) : (
                  <div className={`w-4 h-4 rounded ${user.email_notifications ? 'bg-yellow-500' : 'bg-gray-600'}`} />
                )}
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white font-medium">Push Notifications</div>
                  <div className="text-gray-400 text-sm">Receive push notifications in your browser</div>
                </div>
                {isEditing ? (
                  <input
                    type="checkbox"
                    name="push_notifications"
                    checked={formData.push_notifications}
                    onChange={handleInputChange}
                    className="w-4 h-4 text-yellow-500 bg-gray-800 border-gray-700 rounded focus:ring-yellow-500"
                  />
                ) : (
                  <div className={`w-4 h-4 rounded ${user.push_notifications ? 'bg-yellow-500' : 'bg-gray-600'}`} />
                )}
              </div>
            </div>
          </div>

          {/* Account Security */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-6">
              <Shield className="h-5 w-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-white">Account Security</h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white font-medium">Password</div>
                  <div className="text-gray-400 text-sm">Last updated: {formatDate(user.updated_at)}</div>
                </div>
                <button className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 flex items-center gap-2">
                  <Lock className="h-4 w-4" />
                  Change Password
                </button>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white font-medium">Two-Factor Authentication</div>
                  <div className="text-gray-400 text-sm">Add an extra layer of security</div>
                </div>
                <button className="px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600">
                  Enable 2FA
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;