import React, { useState, useEffect } from 'react';
import { Trophy, Award, Star, Target, Flame, Lock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { achievementsAPI, handleApiError } from '../services/api';

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
            Earned on {new Date(badge.earnedDate).toLocaleDateString()}
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
  
  const categories = [
    { key: 'all', label: 'All Badges' },
    { key: 'habits', label: 'Habits' },
    { key: 'learning', label: 'Learning' },
    { key: 'mindfulness', label: 'Mindfulness' },
    { key: 'productivity', label: 'Productivity' }
  ];

  const milestones = [
    {
      icon: Target,
      title: 'Habits Completed',
      description: 'Total habits completed this month',
      value: 156,
      unit: 'habits'
    },
    {
      icon: Flame,
      title: 'Longest Streak',
      description: 'Your personal best streak',
      value: 23,
      unit: 'days'
    },
    {
      icon: Award,
      title: 'Learning Hours',
      description: 'Time spent on courses',
      value: 47,
      unit: 'hours'
    },
    {
      icon: Star,
      title: 'Growth Points',
      description: 'Total points earned',
      value: mockStats.totalPoints,
      unit: 'points'
    }
  ];

  const filteredBadges = selectedCategory === 'all' 
    ? mockBadges 
    : mockBadges.filter(badge => badge.category === selectedCategory);

  const earnedBadges = mockBadges.filter(badge => badge.earned);
  const totalBadges = mockBadges.length;
  const completionRate = Math.round((earnedBadges.length / totalBadges) * 100);

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white mb-2">Achievements & Progress</h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Celebrate your growth journey and unlock new achievements as you build lasting habits and reach your goals
        </p>
      </div>

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
              <h3 className="text-2xl font-bold text-white">{mockStats.level}</h3>
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
              <h3 className="text-2xl font-bold text-white">{mockStats.totalPoints}</h3>
              <p className="text-sm text-gray-400">Total Points</p>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-white">Overall Progress</h3>
          <span className="text-yellow-400 font-medium">{completionRate}%</span>
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

      {/* Category Filters */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Achievements</h2>
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
          {mockBadges.map((badge) => (
            <BadgeCard key={badge.id} badge={badge} />
          ))}
        </div>
      </div>

      {/* Upcoming Achievements */}
      <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
        <h2 className="text-xl font-bold text-white mb-4">Almost There!</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {mockBadges
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
      </div>
    </div>
  );
};

export default Achievements;