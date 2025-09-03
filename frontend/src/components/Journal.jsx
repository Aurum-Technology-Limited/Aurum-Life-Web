import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, AlertCircle, BookOpen, TrendingUp, FileText, RotateCcw, Search, Filter, Calendar, Tag, Smile, Meh, Frown, X, Brain, Heart, Zap, Target, BarChart3, Activity, Sparkles } from 'lucide-react';
import { journalAPI, sentimentAPI, handleApiError } from '../services/api';
import SentimentIndicator, { SentimentBadge } from './ui/SentimentIndicator';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Journal = ({ onSectionChange, sectionParams }) => {
  const [currentView, setCurrentView] = useState('entries'); // 'entries', 'insights', 'templates', 'trash'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMoodFilter, setSelectedMoodFilter] = useState('');
  const [selectedTagFilter, setSelectedTagFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [trashEntries, setTrashEntries] = useState([]);
  const [entries, setEntries] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [viewingEntry, setViewingEntry] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newEntryTitle, setNewEntryTitle] = useState('');
  const [newEntryContent, setNewEntryContent] = useState('');

  // Sentiment analysis states
  const [sentimentTrends, setSentimentTrends] = useState([]);
  const [wellnessScore, setWellnessScore] = useState(null);
  const [emotionalInsights, setEmotionalInsights] = useState([]);
  const [activityCorrelations, setActivityCorrelations] = useState([]);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [insightsTimeRange, setInsightsTimeRange] = useState(30);
  const [realTimeSentiment, setRealTimeSentiment] = useState(null);
  const [bulkAnalyzing, setBulkAnalyzing] = useState(false);

  // Real-time sentiment analysis while typing
  const analyzeSentimentRealTime = async (text) => {
    if (!text || text.length < 10) {
      setRealTimeSentiment(null);
      return;
    }

    try {
      const result = await sentimentAPI.analyzeText(text);
      setRealTimeSentiment(result);
    } catch (error) {
      console.warn('Real-time sentiment analysis failed:', error);
      setRealTimeSentiment(null);
    }
  };

  // Fetch sentiment insights data
  const fetchSentimentInsights = async () => {
    try {
      setInsightsLoading(true);
      
      // Fetch all sentiment data in parallel
      const [trendsData, wellnessData, insightsData, correlationsData] = await Promise.all([
        sentimentAPI.getTrends(insightsTimeRange),
        sentimentAPI.getWellnessScore(insightsTimeRange),
        sentimentAPI.getInsights(insightsTimeRange),
        sentimentAPI.getCorrelations(insightsTimeRange)
      ]);

      setSentimentTrends(trendsData.trends || []);
      setWellnessScore(wellnessData);
      setEmotionalInsights(insightsData.insights || []);
      setActivityCorrelations(correlationsData.correlations || []);
    } catch (error) {
      console.error('Failed to fetch sentiment insights:', error);
      setError('Failed to load emotional insights');
    } finally {
      setInsightsLoading(false);
    }
  };

  // Bulk analyze existing entries
  const handleBulkAnalyze = async () => {
    try {
      setBulkAnalyzing(true);
      const result = await sentimentAPI.bulkAnalyze(50);
      
      // Refresh entries to show updated sentiment data
      await fetchEntriesWithFallback();
      
      // Refresh insights
      await fetchSentimentInsights();
      
      setError(null);
    } catch (error) {
      setError('Failed to analyze entries. Please try again.');
    } finally {
      setBulkAnalyzing(false);
    }
  };

  // Handle create entry with sentiment analysis
  const handleCreateEntry = async () => {
    if (!newEntryTitle.trim() || !newEntryContent.trim()) {
      setError('Please fill in both title and content');
      return;
    }

    try {
      setIsSyncing(true);
      const entryData = {
        title: newEntryTitle.trim(),
        content: newEntryContent.trim()
      };
      
      const response = await journalAPI.createEntry(entryData);
      
      // Add the new entry to the entries list
      if (response.data) {
        setEntries(prev => [response.data, ...prev]);
      }
      
      // Reset form and close modal
      setNewEntryTitle('');
      setNewEntryContent('');
      setRealTimeSentiment(null);
      setShowCreateModal(false);
      setError(null);

      // Refresh insights if we're on the insights tab
      if (currentView === 'insights') {
        fetchSentimentInsights();
      }
    } catch (err) {
      setError(handleApiError(err, 'Failed to create entry'));
    } finally {
      setIsSyncing(false);
    }
  };

  // Fetch entries with fallback
  const fetchEntriesWithFallback = async () => {
    try {
      setLoading(true);
      console.log('📖 Journal: Fetching entries...');
      
      const response = await journalAPI.getEntries({
        skip: 0,
        limit: 20,
        moodFilter: selectedMoodFilter || null,
        tagFilter: selectedTagFilter || null
      });
      
      console.log('📖 Journal: Raw API response:', response);
      
      // Handle both direct data and wrapped data response formats
      const data = response.data || response || [];
      console.log('📖 Journal: Processed data:', data);
      
      setEntries(Array.isArray(data) ? data : []);
      setError(null);
      console.log('✅ Journal: Entries loaded successfully');
    } catch (err) {
      console.error('❌ Journal entries fetch error:', err);
      console.warn('⚠️ Journal entries endpoint not available:', err.message);
      setEntries([]);
      setError(handleApiError(err, 'Failed to load entries'));
    } finally {
      setLoading(false);
    }
  };

  // Fetch templates with fallback
  const fetchTemplatesWithFallback = async () => {
    try {
      console.log('📋 Journal: Fetching templates...');
      
      const response = await journalAPI.getTemplates();
      console.log('📋 Journal: Raw templates response:', response);
      
      // Handle both direct data and wrapped data response formats
      const data = response.data || response || [];
      console.log('📋 Journal: Processed templates data:', data);
      
      setTemplates(Array.isArray(data) ? data : []);
      console.log('✅ Journal: Templates loaded successfully');
    } catch (err) {
      console.error('❌ Journal templates fetch error:', err);
      console.warn('⚠️ Journal templates endpoint not available:', err.message);
      setTemplates([]);
    }
  };

  const fetchTrash = async () => {
    try {
      const response = await journalAPI.getTrash();
      const data = response.data || [];
      setTrashEntries(Array.isArray(data) ? data : []);
    } catch (err) {
      console.warn('⚠️ Journal trash endpoint not available:', err.message);
      setTrashEntries([]);
    }
  };

  // Load data on component mount
  useEffect(() => {
    fetchEntriesWithFallback();
    fetchTemplatesWithFallback();
  }, [selectedMoodFilter, selectedTagFilter]);

  // Load insights data when switching to insights tab
  useEffect(() => {
    if (currentView === 'insights') {
      fetchSentimentInsights();
    }
  }, [currentView, insightsTimeRange]);

  const handleDeleteEntry = async (entryId) => {
    if (!window.confirm('Are you sure you want to delete this journal entry?')) return;
    
    try {
      setIsSyncing(true);
      await journalAPI.deleteEntry(entryId);
      setEntries(prev => prev.filter(entry => entry.id !== entryId));
      setViewingEntry(null);
      // Refresh trash to include this entry if server marks as deleted
      fetchTrash();
    } catch (err) {
      setError(handleApiError(err, 'Failed to delete entry'));
    } finally {
      setIsSyncing(false);
    }
  };

  const handleRestoreEntry = async (entryId) => {
    try {
      setIsSyncing(true);
      await journalAPI.restoreEntry(entryId);
      // Move from trash to entries by refetching lists
      await fetchEntriesWithFallback();
      setTrashEntries(prev => prev.filter(e => e.id !== entryId));
    } catch (err) {
      setError(handleApiError(err, 'Failed to restore entry'));
    } finally {
      setIsSyncing(false);
    }
  };

  const handlePurgeEntry = async (entryId) => {
    if (!window.confirm('Permanently delete this entry? This cannot be undone.')) return;
    try {
      setIsSyncing(true);
      await journalAPI.purgeEntry(entryId);
      setTrashEntries(prev => prev.filter(e => e.id !== entryId));
    } catch (err) {
      setError(handleApiError(err, 'Failed to permanently delete entry'));
    } finally {
      setIsSyncing(false);
    }
  };

  const renderEntriesView = () => (
    <div className="space-y-6">
      {/* Create Entry Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Journal Entries</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-yellow-400 text-gray-900 px-4 py-2 rounded-lg hover:bg-yellow-300 transition-colors flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>New Entry</span>
        </button>
      </div>

      {/* Entries List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading entries...</p>
        </div>
      ) : entries.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {entries.map((entry) => (
            <div key={entry.id} className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <h3 className="text-lg font-semibold text-white">{entry.title}</h3>
                  {entry.sentiment_category && (
                    <SentimentBadge
                      sentimentCategory={entry.sentiment_category}
                      sentimentScore={entry.sentiment_score}
                      sentimentEmoji={entry.sentiment_emoji}
                      size="small"
                    />
                  )}
                </div>
                <span className="text-xs text-gray-500">{new Date(entry.created_at).toLocaleDateString()}</span>
              </div>
              <p className="text-gray-300 text-sm mb-4 line-clamp-3">{entry.content}</p>
              
              {/* Emotional Keywords */}
              {entry.emotional_keywords && entry.emotional_keywords.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {entry.emotional_keywords.slice(0, 3).map((keyword, index) => (
                    <span 
                      key={index}
                      className="px-2 py-1 text-xs rounded-full bg-purple-600/20 text-purple-400 border border-purple-600/30"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              )}
              
              <div className="flex items-center gap-3">
                <button className="px-3 py-2 rounded bg-blue-600 text-white hover:bg-blue-500 transition-colors">View</button>
                <button className="px-3 py-2 rounded bg-gray-600 text-white hover:bg-gray-500 transition-colors">Edit</button>
                <button 
                  onClick={() => handleDeleteEntry(entry.id)}
                  className="px-3 py-2 rounded bg-red-600 text-white hover:bg-red-500 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-lg bg-yellow-400/20 flex items-center justify-center mx-auto mb-4">
            <BookOpen size={32} className="text-yellow-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">No entries yet</h3>
          <p className="text-gray-400 mb-4">Start your journaling journey by creating your first entry.</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-yellow-400 text-gray-900 px-6 py-3 rounded-lg hover:bg-yellow-300 transition-colors"
          >
            Create First Entry
          </button>
        </div>
      )}
    </div>
  );

  const renderInsightsView = () => {
    // Prepare chart data for sentiment trends
    const chartData = {
      labels: sentimentTrends.map(trend => new Date(trend.date).toLocaleDateString()),
      datasets: [
        {
          label: 'Daily Sentiment',
          data: sentimentTrends.map(trend => trend.average_sentiment),
          borderColor: '#F59E0B',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: sentimentTrends.map(trend => {
            if (trend.average_sentiment > 0.2) return '#10B981';
            if (trend.average_sentiment < -0.2) return '#EF4444';
            return '#6B7280';
          }),
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 4,
        }
      ]
    };

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(17, 24, 39, 0.9)',
          titleColor: '#ffffff',
          bodyColor: '#ffffff',
          borderColor: '#374151',
          borderWidth: 1,
          callbacks: {
            label: function(context) {
              const value = context.parsed.y;
              const category = value > 0.6 ? 'Very Positive' :
                             value > 0.2 ? 'Positive' :
                             value > -0.2 ? 'Neutral' :
                             value > -0.6 ? 'Negative' : 'Very Negative';
              return `${category}: ${value.toFixed(2)}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(75, 85, 99, 0.3)'
          },
          ticks: {
            color: '#9CA3AF'
          }
        },
        y: {
          min: -1,
          max: 1,
          grid: {
            color: 'rgba(75, 85, 99, 0.3)'
          },
          ticks: {
            color: '#9CA3AF',
            callback: function(value) {
              if (value === 1) return 'Very Positive';
              if (value === 0.5) return 'Positive';
              if (value === 0) return 'Neutral';
              if (value === -0.5) return 'Negative';
              if (value === -1) return 'Very Negative';
              return '';
            }
          }
        }
      }
    };

    return (
      <div className="space-y-6">
        {/* Header with Time Range Selector */}
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">Emotional Insights</h2>
          <div className="flex items-center gap-3">
            <select
              value={insightsTimeRange}
              onChange={(e) => setInsightsTimeRange(Number(e.target.value))}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-yellow-400"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
            <button
              onClick={handleBulkAnalyze}
              disabled={bulkAnalyzing}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-500 transition-colors flex items-center space-x-2 disabled:opacity-50"
            >
              {bulkAnalyzing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Brain size={16} />
                  <span>Analyze Past Entries</span>
                </>
              )}
            </button>
          </div>
        </div>

        {insightsLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
            <p className="text-gray-400">Loading emotional insights...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Emotional Wellness Score */}
            {wellnessScore && (
              <div className="lg:col-span-2 p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 rounded-lg bg-green-400/20 flex items-center justify-center">
                    <Heart size={24} className="text-green-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white">Emotional Wellness Score</h3>
                    <p className="text-gray-400 text-sm">Your overall emotional health indicator</p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-white mb-2">
                      {wellnessScore.wellness_score?.toFixed(1) || '0.0'}
                      <span className="text-2xl text-gray-400">/100</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{wellnessScore.wellness_emoji}</span>
                      <span className="text-sm text-gray-300 capitalize">
                        {wellnessScore.wellness_category?.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="bg-gray-700 rounded-full h-3 mb-2">
                      <div 
                        className="h-3 rounded-full bg-gradient-to-r from-green-400 to-green-500"
                        style={{ width: `${Math.min(wellnessScore.wellness_score || 0, 100)}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400">{wellnessScore.interpretation}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Sentiment Trends Chart */}
            {sentimentTrends.length > 0 && (
              <div className="lg:col-span-2 p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-blue-400/20 flex items-center justify-center">
                    <TrendingUp size={20} className="text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Emotional Trends</h3>
                    <p className="text-gray-400 text-sm">Your sentiment patterns over time</p>
                  </div>
                </div>
                <div className="h-64">
                  <Line data={chartData} options={chartOptions} />
                </div>
              </div>
            )}

            {/* Emotional Keywords Cloud */}
            {sentimentTrends.length > 0 && (
              <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-purple-400/20 flex items-center justify-center">
                    <Sparkles size={20} className="text-purple-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Emotional Keywords</h3>
                    <p className="text-gray-400 text-sm">Most frequent emotional expressions</p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {sentimentTrends
                    .flatMap(trend => trend.emotional_keywords || [])
                    .reduce((acc, keyword) => {
                      acc[keyword] = (acc[keyword] || 0) + 1;
                      return acc;
                    }, {})
                    && Object.entries(
                      sentimentTrends
                        .flatMap(trend => trend.emotional_keywords || [])
                        .reduce((acc, keyword) => {
                          acc[keyword] = (acc[keyword] || 0) + 1;
                          return acc;
                        }, {})
                    )
                    .sort(([,a], [,b]) => b - a)
                    .slice(0, 12)
                    .map(([keyword, count]) => (
                      <span 
                        key={keyword}
                        className="px-3 py-1 text-sm rounded-full bg-purple-600/20 text-purple-400 border border-purple-600/30"
                        title={`Appeared ${count} times`}
                      >
                        {keyword}
                      </span>
                    ))}
                </div>
              </div>
            )}

            {/* Activity Correlations */}
            {activityCorrelations.length > 0 && (
              <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-orange-400/20 flex items-center justify-center">
                    <Activity size={20} className="text-orange-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Activity Impact</h3>
                    <p className="text-gray-400 text-sm">How activities affect your emotions</p>
                  </div>
                </div>
                <div className="space-y-3">
                  {activityCorrelations.slice(0, 5).map((correlation, index) => (
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50">
                      <div>
                        <p className="text-white font-medium">{correlation.activity_name}</p>
                        <p className="text-xs text-gray-400 capitalize">{correlation.activity_type}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="text-right">
                          <p className="text-sm font-medium" style={{ 
                            color: correlation.average_sentiment > 0 ? '#10B981' : 
                                   correlation.average_sentiment < 0 ? '#EF4444' : '#6B7280' 
                          }}>
                            {correlation.average_sentiment > 0 ? '+' : ''}{correlation.average_sentiment.toFixed(2)}
                          </p>
                          <p className="text-xs text-gray-400">{correlation.entry_count} entries</p>
                        </div>
                        <span className="text-lg">
                          {correlation.average_sentiment > 0.2 ? '😊' : 
                           correlation.average_sentiment < -0.2 ? '😞' : '😐'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Actions Panel */}
            <div className="lg:col-span-2 p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-yellow-400/20 flex items-center justify-center">
                  <Target size={20} className="text-yellow-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Emotional Intelligence Actions</h3>
                  <p className="text-gray-400 text-sm">Tools to enhance your emotional awareness</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={handleBulkAnalyze}
                  disabled={bulkAnalyzing}
                  className="p-4 rounded-lg border border-gray-700 hover:border-purple-500 transition-colors text-left disabled:opacity-50"
                >
                  <Brain className="text-purple-400 mb-2" size={20} />
                  <h4 className="text-white font-medium mb-1">Analyze Past Entries</h4>
                  <p className="text-gray-400 text-sm">Get emotional insights from your existing journal entries</p>
                </button>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="p-4 rounded-lg border border-gray-700 hover:border-green-500 transition-colors text-left"
                >
                  <Heart className="text-green-400 mb-2" size={20} />
                  <h4 className="text-white font-medium mb-1">Emotional Check-in</h4>
                  <p className="text-gray-400 text-sm">Write about your current emotional state</p>
                </button>
                <button
                  onClick={() => setInsightsTimeRange(7)}
                  className="p-4 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors text-left"
                >
                  <BarChart3 className="text-blue-400 mb-2" size={20} />
                  <h4 className="text-white font-medium mb-1">Weekly Patterns</h4>
                  <p className="text-gray-400 text-sm">Explore your emotional patterns this week</p>
                </button>
              </div>
            </div>

            {/* No Data State */}
            {sentimentTrends.length === 0 && !insightsLoading && (
              <div className="lg:col-span-2 text-center py-12">
                <div className="w-16 h-16 rounded-lg bg-blue-400/20 flex items-center justify-center mx-auto mb-4">
                  <Brain size={32} className="text-blue-400" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">No Emotional Data Yet</h3>
                <p className="text-gray-400 mb-6">Start journaling or analyze your existing entries to see emotional insights.</p>
                <div className="flex justify-center gap-4">
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="bg-yellow-400 text-gray-900 px-6 py-3 rounded-lg hover:bg-yellow-300 transition-colors"
                  >
                    Write First Entry
                  </button>
                  <button
                    onClick={handleBulkAnalyze}
                    disabled={bulkAnalyzing}
                    className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50"
                  >
                    {bulkAnalyzing ? 'Analyzing...' : 'Analyze Existing Entries'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderTemplatesView = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Journal Templates</h2>
      <div className="text-center py-12">
        <div className="w-16 h-16 rounded-lg bg-green-400/20 flex items-center justify-center mx-auto mb-4">
          <FileText size={32} className="text-green-400" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">Templates Coming Soon</h3>
        <p className="text-gray-400">Pre-made templates will help you get started with different types of journal entries.</p>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Journal</h1>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center space-x-1 bg-gray-800/50 p-1 rounded-lg">
        <button
          onClick={() => setCurrentView('entries')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
            currentView === 'entries' 
              ? 'bg-yellow-400 text-gray-900' 
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          <BookOpen size={16} />
          <span>Entries</span>
        </button>
        <button
          onClick={() => setCurrentView('insights')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
            currentView === 'insights' 
              ? 'bg-yellow-400 text-gray-900' 
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          <TrendingUp size={16} />
          <span>Insights</span>
        </button>
        <button
          onClick={() => setCurrentView('templates')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
            currentView === 'templates' 
              ? 'bg-yellow-400 text-gray-900' 
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          <FileText size={16} />
          <span>Templates</span>
        </button>
        <button
          onClick={() => {
            setCurrentView('trash');
            fetchTrash();
          }}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
            currentView === 'trash' 
              ? 'bg-yellow-400 text-gray-900' 
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          <RotateCcw size={16} />
          <span>Trash</span>
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center space-x-2">
          <AlertCircle size={20} className="text-red-400" />
          <span className="text-red-400">{error}</span>
        </div>
      )}

      {/* Render different views based on currentView */}
      {currentView === 'entries' && renderEntriesView()}
      {currentView === 'insights' && renderInsightsView()}
      {currentView === 'templates' && renderTemplatesView()}
      {currentView === 'trash' && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-white">Trash</h2>
          {trashEntries.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {trashEntries.map((entry) => (
                <div key={entry.id} className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold text-white">{entry.title}</h3>
                    <span className="text-xs text-gray-500">Deleted {new Date(entry.deleted_at || entry.updated_at || entry.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-gray-300 text-sm mb-4 line-clamp-3">{entry.content}</p>
                  <div className="flex items-center gap-3">
                    <button onClick={() => handleRestoreEntry(entry.id)} className="px-3 py-2 rounded bg-green-600 text-white hover:bg-green-500 transition-colors">Restore</button>
                    <button onClick={() => handlePurgeEntry(entry.id)} className="px-3 py-2 rounded bg-red-600 text-white hover:bg-red-500 transition-colors">Delete Forever</button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-lg bg-yellow-400/20 flex items-center justify-center mx-auto mb-4">
                <RotateCcw size={32} className="text-yellow-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Trash is empty</h3>
              <p className="text-gray-400">Deleted entries will appear here for review.</p>
            </div>
          )}
        </div>
      )}

      {/* Create Entry Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-lg p-6 w-full max-w-2xl mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">New Journal Entry</h2>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setNewEntryTitle('');
                  setNewEntryContent('');
                  setRealTimeSentiment(null);
                  setError(null);
                }}
                className="text-gray-400 hover:text-white"
              >
                <X size={24} />
              </button>
            </div>
            
            {/* Real-time Sentiment Feedback */}
            {realTimeSentiment && (
              <div className="mb-4 p-3 rounded-lg bg-gray-800/50 border border-gray-700">
                <div className="flex items-center gap-3 mb-2">
                  <Zap size={16} className="text-yellow-400" />
                  <span className="text-sm font-medium text-white">Live Emotional Analysis</span>
                </div>
                <div className="flex items-center gap-4">
                  <SentimentIndicator
                    sentimentCategory={realTimeSentiment.sentiment_analysis?.sentiment_category}
                    sentimentScore={realTimeSentiment.sentiment_analysis?.sentiment_score}
                    sentimentEmoji={realTimeSentiment.sentiment_emoji}
                    emotionalKeywords={realTimeSentiment.sentiment_analysis?.emotional_keywords}
                    showDetails={true}
                    size="small"
                  />
                  <div className="text-xs text-gray-400">
                    {realTimeSentiment.human_readable}
                  </div>
                </div>
              </div>
            )}
            
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Entry title..."
                value={newEntryTitle}
                onChange={(e) => setNewEntryTitle(e.target.value)}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400"
              />
              <textarea
                placeholder="What's on your mind?"
                rows={8}
                value={newEntryContent}
                onChange={(e) => {
                  setNewEntryContent(e.target.value);
                  // Debounce real-time sentiment analysis
                  clearTimeout(window.sentimentTimeout);
                  window.sentimentTimeout = setTimeout(() => {
                    analyzeSentimentRealTime(e.target.value);
                  }, 1000);
                }}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 resize-none"
              />
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setNewEntryTitle('');
                    setNewEntryContent('');
                    setRealTimeSentiment(null);
                    setError(null);
                  }}
                  className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateEntry}
                  disabled={isSyncing}
                  className="px-4 py-2 bg-yellow-400 text-gray-900 rounded-lg hover:bg-yellow-300 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {isSyncing && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>}
                  Save Entry
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Journal;