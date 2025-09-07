import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Plus, Edit2, Trash2, AlertCircle, BookOpen, TrendingUp, FileText, Search, Filter, Calendar, Tag, Smile, Meh, Frown, X, Brain, Heart, Zap, Target, BarChart3, Activity, Sparkles, Loader2 } from 'lucide-react';
import { 
  useJournalEntries, 
  useJournalInsights,
  useCreateJournalEntry, 
  useUpdateJournalEntry, 
  useDeleteJournalEntry,
  useAnalyzeJournalSentiment 
} from '../hooks/useGraphQL';
// SentimentIndicator removed during refactoring
// import { OptimizedLineChart } from './optimized/OptimizedCharts'; // Removed - using placeholder
// import { OptimizedJournalEntryCard } from './optimized/OptimizedLists'; // Removed - using placeholder

const Journal = ({ onSectionChange, sectionParams }) => {
  const [currentView, setCurrentView] = useState('entries'); // 'entries', 'insights', 'templates', 'trash'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMoodFilter, setSelectedMoodFilter] = useState('');
  const [selectedTagFilter, setSelectedTagFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [viewingEntry, setViewingEntry] = useState(null);
  const [editingEntry, setEditingEntry] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newEntryTitle, setNewEntryTitle] = useState('');
  const [newEntryContent, setNewEntryContent] = useState('');
  const [editEntryTitle, setEditEntryTitle] = useState('');
  const [editEntryContent, setEditEntryContent] = useState('');
  const [insightsTimeRange, setInsightsTimeRange] = useState(30);

  // GraphQL hooks
  const { entries, loading: entriesLoading, error: entriesError, refetch: refetchEntries } = useJournalEntries({
    moodFilter: selectedMoodFilter || undefined,
    tagFilter: selectedTagFilter || undefined,
  });

  const { insights, loading: insightsLoading, refetch: refetchInsights } = useJournalInsights(insightsTimeRange);
  const { createEntry, loading: createLoading } = useCreateJournalEntry();
  const { updateEntry, loading: updateLoading } = useUpdateJournalEntry();
  const { deleteEntry, loading: deleteLoading } = useDeleteJournalEntry();
  const { analyzeSentiment, loading: analyzeLoading } = useAnalyzeJournalSentiment();

  // Loading state
  const loading = entriesLoading || insightsLoading;
  const isSyncing = createLoading || updateLoading || deleteLoading || analyzeLoading;

  // Process entries for display
  const filteredEntries = useMemo(() => {
    let filtered = entries || [];
    
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(entry => 
        entry.title.toLowerCase().includes(search) ||
        entry.content.toLowerCase().includes(search)
      );
    }
    
    return filtered;
  }, [entries, searchTerm]);

  // Extract unique tags and moods for filters
  const { availableTags, availableMoods } = useMemo(() => {
    const tags = new Set();
    const moods = new Set();
    
    entries?.forEach(entry => {
      entry.tags?.forEach(tag => tags.add(tag));
      if (entry.mood) moods.add(entry.mood);
    });
    
    return {
      availableTags: Array.from(tags),
      availableMoods: Array.from(moods)
    };
  }, [entries]);

  // Handle create entry
  const handleCreateEntry = async () => {
    if (!newEntryTitle.trim() || !newEntryContent.trim()) {
      return;
    }

    try {
      await createEntry({
        title: newEntryTitle.trim(),
        content: newEntryContent.trim(),
        mood: 'reflective', // Default mood
        tags: []
      });
      
      // Reset form
      setNewEntryTitle('');
      setNewEntryContent('');
      setShowCreateModal(false);
      
      // Refetch entries
      refetchEntries();
    } catch (error) {
      console.error('Failed to create entry:', error);
    }
  };

  // Handle update entry
  const handleUpdateEntry = async () => {
    if (!editingEntry || !editEntryTitle.trim() || !editEntryContent.trim()) {
      return;
    }

    try {
      await updateEntry(editingEntry.id, {
        title: editEntryTitle.trim(),
        content: editEntryContent.trim()
      });
      
      // Close edit modal
      setEditingEntry(null);
      setEditEntryTitle('');
      setEditEntryContent('');
      
      // Refetch entries
      refetchEntries();
    } catch (error) {
      console.error('Failed to update entry:', error);
    }
  };

  // Handle delete entry
  const handleDeleteEntry = async (entryId) => {
    if (!window.confirm('Are you sure you want to delete this entry?')) {
      return;
    }

    try {
      await deleteEntry(entryId);
      refetchEntries();
    } catch (error) {
      console.error('Failed to delete entry:', error);
    }
  };

  // Handle analyze sentiment
  const handleAnalyzeSentiment = async (entryId) => {
    try {
      await analyzeSentiment(entryId);
      refetchEntries();
    } catch (error) {
      console.error('Failed to analyze sentiment:', error);
    }
  };

  // Prepare chart data
  const chartData = useMemo(() => {
    if (!insights?.sentimentTrends) return [];
    
    return insights.sentimentTrends.map(trend => ({
      date: new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      score: parseFloat((trend.score * 100).toFixed(1)),
      category: trend.category
    }));
  }, [insights?.sentimentTrends]);

  // Entry card component with GraphQL data
  const EntryCard = ({ entry }) => (
    <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-sm hover:shadow-md transition-all duration-200 p-6 border border-purple-100">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{entry.title}</h3>
          <p className="text-sm text-gray-500">
            {new Date(entry.createdAt).toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {entry.sentimentScore !== null && (
            <div className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">
              Sentiment: {entry.sentimentCategory || 'Neutral'}
            </div>
          )}
          <button
            onClick={() => handleAnalyzeSentiment(entry.id)}
            className="p-2 hover:bg-purple-50 rounded-lg transition-colors"
            title="Analyze sentiment"
          >
            <Brain className="w-4 h-4 text-purple-600" />
          </button>
          <button
            onClick={() => {
              setEditingEntry(entry);
              setEditEntryTitle(entry.title);
              setEditEntryContent(entry.content);
            }}
            className="p-2 hover:bg-purple-50 rounded-lg transition-colors"
          >
            <Edit2 className="w-4 h-4 text-purple-600" />
          </button>
          <button
            onClick={() => handleDeleteEntry(entry.id)}
            className="p-2 hover:bg-red-50 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4 text-red-600" />
          </button>
        </div>
      </div>
      
      <p className="text-gray-700 line-clamp-3 mb-4">{entry.content}</p>
      
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap gap-2">
          {entry.mood && (
            <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
              {entry.mood}
            </span>
          )}
          {entry.tags?.map((tag, index) => (
            <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
              {tag}
            </span>
          ))}
        </div>
        {entry.wordCount > 0 && (
          <span className="text-xs text-gray-500">{entry.wordCount} words</span>
        )}
      </div>
    </div>
  );

  if (loading && !entries?.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Journal</h2>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded-lg transition-colors ${
              showFilters ? 'bg-purple-100 text-purple-700' : 'hover:bg-gray-100'
            }`}
          >
            <Filter className="w-5 h-5" />
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all duration-200 flex items-center gap-2 shadow-sm"
          >
            <Plus className="w-4 h-4" />
            New Entry
          </button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 shadow-sm border border-purple-100">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search entries..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mood</label>
              <select
                value={selectedMoodFilter}
                onChange={(e) => setSelectedMoodFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">All Moods</option>
                {availableMoods.map(mood => (
                  <option key={mood} value={mood}>{mood}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tag</label>
              <select
                value={selectedTagFilter}
                onChange={(e) => setSelectedTagFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">All Tags</option>
                {availableTags.map(tag => (
                  <option key={tag} value={tag}>{tag}</option>
                ))}
              </select>
            </div>

            {currentView === 'insights' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Time Range</label>
                <select
                  value={insightsTimeRange}
                  onChange={(e) => {
                    setInsightsTimeRange(Number(e.target.value));
                    refetchInsights();
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value={7}>Last 7 days</option>
                  <option value={30}>Last 30 days</option>
                  <option value={90}>Last 90 days</option>
                </select>
              </div>
            )}
          </div>
        </div>
      )}

      {/* View Tabs */}
      <div className="flex gap-1 p-1 bg-gray-100 rounded-lg">
        <button
          onClick={() => setCurrentView('entries')}
          className={`flex-1 px-4 py-2 rounded-md transition-all duration-200 ${
            currentView === 'entries'
              ? 'bg-white text-purple-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Entries
        </button>
        <button
          onClick={() => setCurrentView('insights')}
          className={`flex-1 px-4 py-2 rounded-md transition-all duration-200 ${
            currentView === 'insights'
              ? 'bg-white text-purple-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Insights
        </button>
      </div>

      {/* Content */}
      {currentView === 'entries' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredEntries.length === 0 ? (
            <div className="col-span-2 text-center py-12">
              <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No journal entries found</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Create your first entry
              </button>
            </div>
          ) : (
            filteredEntries.map(entry => (
              <EntryCard key={entry.id} entry={entry} />
            ))
          )}
        </div>
      )}

      {currentView === 'insights' && insights && (
        <div className="space-y-6">
          {/* Wellness Score */}
          <div className="bg-white/90 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-purple-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Wellness Overview</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(insights.wellnessScore.overall * 100)}%
                </div>
                <p className="text-sm text-gray-600">Overall</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {Math.round(insights.wellnessScore.emotional * 100)}%
                </div>
                <p className="text-sm text-gray-600">Emotional</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {Math.round(insights.wellnessScore.productivity * 100)}%
                </div>
                <p className="text-sm text-gray-600">Productivity</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {Math.round(insights.wellnessScore.balance * 100)}%
                </div>
                <p className="text-sm text-gray-600">Balance</p>
              </div>
            </div>
          </div>

          {/* Sentiment Trends */}
          {chartData.length > 0 && (
            <div className="bg-white/90 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-purple-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Trends</h3>
              <div className="h-64">
                <OptimizedLineChart
                  data={chartData}
                  dataKey="score"
                  name="Sentiment Score"
                  color="#9333ea"
                  showGrid={true}
                />
              </div>
            </div>
          )}

          {/* Emotional Insights */}
          {insights.emotionalInsights.length > 0 && (
            <div className="bg-white/90 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-purple-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Insights</h3>
              <div className="space-y-3">
                {insights.emotionalInsights.map((insight, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
                    <Sparkles className="w-5 h-5 text-purple-600 mt-0.5" />
                    <div>
                      <p className="text-gray-800">{insight.message}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        Confidence: {Math.round(insight.confidence * 100)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">New Journal Entry</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={newEntryTitle}
                  onChange={(e) => setNewEntryTitle(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Give your entry a title..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                <textarea
                  value={newEntryContent}
                  onChange={(e) => setNewEntryContent(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent h-64 resize-none"
                  placeholder="Write your thoughts..."
                />
              </div>
              
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateEntry}
                  disabled={!newEntryTitle.trim() || !newEntryContent.trim() || createLoading}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createLoading ? 'Creating...' : 'Create Entry'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editingEntry && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">Edit Journal Entry</h3>
              <button
                onClick={() => setEditingEntry(null)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={editEntryTitle}
                  onChange={(e) => setEditEntryTitle(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                <textarea
                  value={editEntryContent}
                  onChange={(e) => setEditEntryContent(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent h-64 resize-none"
                />
              </div>
              
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setEditingEntry(null)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateEntry}
                  disabled={!editEntryTitle.trim() || !editEntryContent.trim() || updateLoading}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {updateLoading ? 'Updating...' : 'Update Entry'}
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