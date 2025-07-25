import React, { useState, useEffect } from 'react';
import { Trophy, Award, Star, Target, Flame, Lock, CheckCircle, AlertCircle, Loader2, Plus, X, Save } from 'lucide-react';
import { achievementsAPI, customAchievementsAPI, projectsAPI, handleApiError } from '../services/api';
import { useToast } from '../hooks/use-toast';

const BadgeCard = ({ badge }) => {
  const getRarityColor = (rarity) => {
    switch (rarity) {
      case 'gold': return 'from-yellow-400 to-yellow-600';
      case 'silver': return 'from-gray-300 to-gray-500';
      case 'bronze': return 'from-orange-400 to-orange-600';
      default: return 'from-gray-400 to-gray-600';
    }
  };

  const getRarityBorder = (rarity) => {
    switch (rarity) {
      case 'gold': return 'border-yellow-400';
      case 'silver': return 'border-gray-400';
      case 'bronze': return 'border-orange-400';
      default: return 'border-gray-600';
    }
  };

  return (
    <div className={`p-6 rounded-xl border ${
      badge.earned 
        ? `${getRarityBorder(badge.rarity)} bg-gradient-to-br from-gray-900/50 to-gray-800/30` 
        : 'border-gray-700 bg-gray-800/30'
    } transition-all duration-300 hover:scale-105 group relative overflow-hidden`}>
      
      {badge.earned && (
        <div className="absolute top-2 right-2">
          <CheckCircle size={20} className="text-green-400" />
        </div>
      )}
      
      <div className="text-center">
        <div className={`w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center text-4xl ${
          badge.earned 
            ? `bg-gradient-to-r ${getRarityColor(badge.rarity)} shadow-lg` 
            : 'bg-gray-700 opacity-50'
        }`}>
          {badge.earned ? badge.icon : <Lock size={24} className="text-gray-400" />}
        </div>
        
        <h3 className={`text-lg font-semibold mb-2 ${
          badge.earned ? 'text-white' : 'text-gray-500'
        }`}>
          {badge.name}
        </h3>
        
        <p className={`text-sm mb-4 ${
          badge.earned ? 'text-gray-300' : 'text-gray-600'
        }`}>
          {badge.description}
        </p>
        
        {badge.earned ? (
          <div className="text-xs text-gray-400">
            Earned on {badge.earned_date ? new Date(badge.earned_date).toLocaleDateString() : 'Unknown date'}
          </div>
        ) : (
          <div className="space-y-2">
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="h-2 rounded-full bg-gradient-to-r from-yellow-400 to-yellow-600 transition-all duration-500"
                style={{ width: `${badge.progress || 0}%` }}
              />
            </div>
            <div className="text-xs text-gray-400">
              Progress: {badge.progress || 0}%
            </div>
          </div>
        )}
        
        <div className="mt-3">
          <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium capitalize ${
            badge.rarity === 'gold' ? 'bg-yellow-400 text-gray-900' :
            badge.rarity === 'silver' ? 'bg-gray-300 text-gray-900' :
            badge.rarity === 'bronze' ? 'bg-orange-400 text-gray-900' :
            'bg-gray-600 text-white'
          }`}>
            {badge.rarity}
          </span>
        </div>
      </div>
    </div>
  );
};

const MilestoneCard = ({ milestone }) => (
  <div className="p-4 rounded-lg border border-gray-700 bg-gradient-to-r from-gray-800/50 to-gray-700/50 hover:from-gray-700/50 hover:to-gray-600/50 transition-all duration-300">
    <div className="flex items-center space-x-3">
      <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
        <milestone.icon size={20} style={{ color: '#0B0D14' }} />
      </div>
      <div className="flex-1">
        <h3 className="font-semibold text-white">{milestone.title}</h3>
        <p className="text-sm text-gray-400">{milestone.description}</p>
      </div>
      <div className="text-right">
        <div className="text-lg font-bold text-yellow-400">{milestone.value}</div>
        <div className="text-xs text-gray-500">{milestone.unit}</div>
      </div>
    </div>
  </div>
);

const Achievements = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [achievements, setAchievements] = useState([]);
  const [customAchievements, setCustomAchievements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [projects, setProjects] = useState([]);
  const { toast } = useToast();

  // Create modal form state
  const [createForm, setCreateForm] = useState({
    name: '',
    description: '',
    icon: '🎯',
    target_type: 'complete_tasks',
    target_id: '',
    target_count: 1
  });
  
  const categories = [
    { key: 'all', label: 'All Badges' },
    { key: 'habits', label: 'Habits' },
    { key: 'learning', label: 'Learning' },
    { key: 'reflection', label: 'Reflection' },
    { key: 'productivity', label: 'Productivity' },
    { key: 'general', label: 'General' }
  ];

  useEffect(() => {
    loadAchievements();
    loadProjects();
  }, []);

  const loadAchievements = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load both predefined and custom achievements
      const [achievementsResponse, customResponse] = await Promise.all([
        achievementsAPI.getAchievements(),
        customAchievementsAPI.getCustomAchievements()
      ]);
      
      setAchievements(achievementsResponse.data.achievements);
      setCustomAchievements(customResponse.data.custom_achievements);
    } catch (err) {
      setError(handleApiError(err, 'Failed to load achievements'));
    } finally {
      setLoading(false);
    }
  };

  const loadProjects = async () => {
    try {
      const response = await projectsAPI.getProjects();
      setProjects(response.data);
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  };

  const handleCheckAchievements = async () => {
    try {
      const [predefinedResponse, customResponse] = await Promise.all([
        achievementsAPI.checkAchievements(),
        customAchievementsAPI.checkCustomAchievements()
      ]);
      
      // Show toast notifications for newly unlocked predefined achievements
      if (predefinedResponse.data.newly_unlocked > 0) {
        predefinedResponse.data.achievements.forEach(achievement => {
          toast({
            title: "🎉 Achievement Unlocked!",
            description: `Congratulations! You've earned the '${achievement.name}' badge!`,
            duration: 5000,
          });
        });
      }
      
      // Show toast notifications for newly completed custom achievements
      if (customResponse.data.newly_completed > 0) {
        customResponse.data.achievements.forEach(achievement => {
          toast({
            title: "🎯 Custom Goal Achieved!",
            description: `Congratulations! You've completed your goal: '${achievement.name}'!`,
            duration: 5000,
          });
        });
      }
      
      // Reload achievements to see any newly unlocked ones
      await loadAchievements();
    } catch (err) {
      setError(handleApiError(err, 'Failed to check achievements'));
    }
  };

  const handleCreateCustomAchievement = async () => {
    try {
      if (!createForm.name.trim()) {
        toast({
          title: "Validation Error",
          description: "Please enter a name for your achievement",
          variant: "destructive"
        });
        return;
      }

      await customAchievementsAPI.createCustomAchievement(createForm);
      
      toast({
        title: "✨ Custom Achievement Created!",
        description: `Your custom achievement "${createForm.name}" has been created successfully!`,
        duration: 4000,
      });
      
      // Reset form and close modal
      setCreateForm({
        name: '',
        description: '',
        icon: '🎯',
        target_type: 'complete_tasks',
        target_id: '',
        target_count: 1
      });
      setShowCreateModal(false);
      
      // Reload achievements
      await loadAchievements();
      
    } catch (err) {
      toast({
        title: "Error",
        description: handleApiError(err, 'Failed to create custom achievement'),
        variant: "destructive"
      });
    }
  };

  const handleDeleteCustomAchievement = async (achievementId) => {
    try {
      await customAchievementsAPI.deleteCustomAchievement(achievementId);
      
      toast({
        title: "Achievement Deleted",
        description: "Custom achievement has been deleted successfully",
        duration: 3000,
      });
      
      await loadAchievements();
    } catch (err) {
      toast({
        title: "Error",
        description: handleApiError(err, 'Failed to delete custom achievement'),
        variant: "destructive"
      });
    }
  };

  const filteredBadges = selectedCategory === 'all' 
    ? achievements 
    : achievements.filter(badge => badge.category === selectedCategory);

  const earnedBadges = achievements.filter(badge => badge.earned);
  const totalBadges = achievements.length;
  const completionRate = totalBadges > 0 ? Math.round((earnedBadges.length / totalBadges) * 100) : 0;

  // Calculate stats from achievements
  const stats = {
    level: Math.floor(earnedBadges.length / 3) + 1, // Simple level calculation
    totalPoints: earnedBadges.length * 100, // Simple points calculation
    totalTasks: 0, // Would need to get from user stats API
    totalJournalEntries: 0 // Would need to get from user stats API
  };

  const milestones = [
    {
      icon: Target,
      title: 'Tasks Completed',
      description: 'Total tasks completed',
      value: stats.totalTasks,
      unit: 'tasks'
    },
    {
      icon: Flame,
      title: 'Current Level',
      description: 'Your achievement level',
      value: stats.level,
      unit: 'level'
    },
    {
      icon: Award,
      title: 'Achievement Points',
      description: 'Points from achievements',
      value: stats.totalPoints,
      unit: 'points'
    },
    {
      icon: Star,
      title: 'Badges Earned',
      description: 'Total badges unlocked',
      value: earnedBadges.length,
      unit: 'badges'
    }
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
        <h1 className="text-3xl font-bold text-white mb-2">Achievements & Progress</h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Celebrate your growth journey and unlock new achievements as you build lasting habits and reach your goals
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center space-x-2">
          <AlertCircle size={20} className="text-red-400" />
          <span className="text-red-400">{error}</span>
          <button
            onClick={loadAchievements}
            className="ml-auto px-3 py-1 rounded bg-red-500 hover:bg-red-600 text-white text-sm transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <Trophy size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{earnedBadges.length}</h3>
              <p className="text-sm text-gray-400">Badges Earned</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-blue-400 flex items-center justify-center">
              <Target size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{completionRate}%</h3>
              <p className="text-sm text-gray-400">Completion Rate</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-purple-400 flex items-center justify-center">
              <Star size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{stats.level}</h3>
              <p className="text-sm text-gray-400">Current Level</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-green-400 flex items-center justify-center">
              <Award size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{stats.totalPoints}</h3>
              <p className="text-sm text-gray-400">Total Points</p>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-white">Overall Progress</h3>
          <div className="flex items-center space-x-2">
            <span className="text-yellow-400 font-medium">{completionRate}%</span>
            <button
              onClick={handleCheckAchievements}
              className="px-3 py-1 text-xs bg-yellow-400 text-gray-900 rounded hover:bg-yellow-500 transition-colors"
            >
              Check Progress
            </button>
          </div>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-4 mb-2">
          <div 
            className="h-4 rounded-full bg-gradient-to-r from-yellow-400 to-yellow-600 transition-all duration-1000"
            style={{ width: `${completionRate}%` }}
          />
        </div>
        <p className="text-sm text-gray-400">
          {earnedBadges.length} of {totalBadges} badges unlocked
        </p>
      </div>

      {/* Key Milestones */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Key Milestones</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {milestones.map((milestone, index) => (
            <MilestoneCard key={index} milestone={milestone} />
          ))}
        </div>
      </div>

      {/* Achievements Section with Create Button */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Achievements</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-yellow-400 text-gray-900 rounded-lg hover:bg-yellow-500 transition-colors font-medium"
          >
            <Plus size={20} />
            <span>Create Your Own Achievement</span>
          </button>
        </div>
        
        {/* Category Filters */}
        <div className="flex flex-wrap gap-2 mb-6">
          {categories.map((category) => (
            <button
              key={category.key}
              onClick={() => setSelectedCategory(category.key)}
              className={`px-4 py-2 rounded-lg transition-all duration-200 ${
                selectedCategory === category.key
                  ? 'text-gray-900 font-medium'
                  : 'text-gray-400 hover:text-white'
              }`}
              style={{
                backgroundColor: selectedCategory === category.key ? '#F4B400' : 'transparent',
                border: selectedCategory === category.key ? 'none' : '1px solid #374151'
              }}
            >
              {category.label}
            </button>
          ))}
        </div>

        {/* Badges Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredBadges.map((badge) => (
            <BadgeCard key={badge.id} badge={badge} />
          ))}
        </div>
      </div>

      {/* Custom Achievements Section */}
      {customAchievements.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">Your Custom Goals</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {customAchievements.map((achievement) => (
              <CustomAchievementCard 
                key={achievement.id} 
                achievement={achievement} 
                onDelete={handleDeleteCustomAchievement}
              />
            ))}
          </div>
        </div>
      )}

      {/* Upcoming Achievements */}
      <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
        <h2 className="text-xl font-bold text-white mb-4">Almost There!</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {achievements
            .filter(badge => !badge.earned && badge.progress > 50)
            .slice(0, 4)
            .map((badge) => (
              <div key={badge.id} className="p-4 rounded-lg bg-gray-800/50 border border-gray-700">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl opacity-70">{badge.icon}</div>
                  <div className="flex-1">
                    <h3 className="font-medium text-white">{badge.name}</h3>
                    <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                      <div 
                        className="h-2 rounded-full bg-gradient-to-r from-yellow-400 to-yellow-600 transition-all duration-500"
                        style={{ width: `${badge.progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-1">{badge.progress}% complete</p>
                  </div>
                </div>
              </div>
            ))}
        </div>
        {achievements.filter(badge => !badge.earned && badge.progress > 50).length === 0 && (
          <p className="text-gray-400 text-center py-4">
            Keep working towards your goals to see upcoming achievements!
          </p>
        )}
      </div>

      {/* Create Custom Achievement Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Create Your Own Achievement</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Achievement Name *
                </label>
                <input
                  type="text"
                  value={createForm.name}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Complete My First Marathon"
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-yellow-400 focus:outline-none"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  value={createForm.description}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Optional description for your achievement"
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-yellow-400 focus:outline-none"
                />
              </div>

              {/* Icon */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Icon
                </label>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{createForm.icon}</span>
                  <input
                    type="text"
                    value={createForm.icon}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, icon: e.target.value }))}
                    placeholder="🎯"
                    className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-yellow-400 focus:outline-none"
                  />
                </div>
              </div>

              {/* Goal Type */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Goal Type
                </label>
                <select
                  value={createForm.target_type}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, target_type: e.target.value, target_id: '' }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-yellow-400 focus:outline-none"
                >
                  <option value="complete_tasks">Complete Tasks</option>
                  <option value="complete_project">Complete Project</option>
                  <option value="write_journal_entries">Write Journal Entries</option>
                  <option value="complete_courses">Complete Courses</option>
                  <option value="maintain_streak">Maintain Streak</option>
                </select>
              </div>

              {/* Target Project (if applicable) */}
              {(createForm.target_type === 'complete_project' || createForm.target_type === 'complete_tasks') && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    {createForm.target_type === 'complete_project' ? 'Target Project' : 'Project (optional)'}
                  </label>
                  <select
                    value={createForm.target_id}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, target_id: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-yellow-400 focus:outline-none"
                  >
                    <option value="">
                      {createForm.target_type === 'complete_project' ? 'Select a project' : 'Any project'}
                    </option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Target Count */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Target {createForm.target_type === 'complete_project' ? 'Count' : 'Number'}
                </label>
                <input
                  type="number"
                  min="1"
                  value={createForm.target_count}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, target_count: parseInt(e.target.value) || 1 }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-yellow-400 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex items-center space-x-3 mt-6">
              <button
                onClick={handleCreateCustomAchievement}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-yellow-400 text-gray-900 rounded-lg hover:bg-yellow-500 transition-colors font-medium"
              >
                <Save size={20} />
                <span>Create Achievement</span>
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Achievements;