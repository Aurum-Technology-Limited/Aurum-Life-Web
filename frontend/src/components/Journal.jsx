import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Calendar, Tag, Smile, Meh, Frown, Loader2, AlertCircle, Search, Filter, BarChart3, FileText, Clock, TrendingUp } from 'lucide-react';
import { journalAPI, handleApiError } from '../services/api';

const JournalEntry = ({ entry, onClick, loading = false }) => {
  const getMoodIcon = (mood) => {
    switch (mood) {
      case 'optimistic':
      case 'inspired':
        return <Smile className="text-green-400" size={16} />;
      case 'reflective':
        return <Meh className="text-yellow-400" size={16} />;
      case 'challenging':
        return <Frown className="text-red-400" size={16} />;
      default:
        return <Meh className="text-gray-400" size={16} />;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div 
      onClick={() => !loading && onClick(entry)}
      className={`p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30 transition-all duration-300 cursor-pointer group hover:scale-105 ${
        loading ? 'opacity-50' : ''
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white group-hover:text-yellow-400 transition-colors">
          {entry.title}
        </h3>
        <div className="flex items-center space-x-2">
          {getMoodIcon(entry.mood)}
          <span className="text-sm text-gray-400">
            {formatDate(entry.created_at)}
          </span>
        </div>
      </div>
      
      <p className="text-gray-300 text-sm mb-4 line-clamp-3">
        {entry.content.length > 200 ? `${entry.content.substring(0, 200)}...` : entry.content}
      </p>
      
      <div className="flex items-center space-x-2">
        {entry.tags.map((tag, index) => (
          <span 
            key={index}
            className="px-2 py-1 rounded-full bg-gray-800 text-xs text-yellow-400 border border-gray-700"
          >
            #{tag}
          </span>
        ))}
      </div>
    </div>
  );
};

const JournalModal = ({ entry, isOpen, onClose, onSave, loading = false }) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    mood: 'reflective',
    tags: ''
  });

  useEffect(() => {
    if (entry) {
      setFormData({
        title: entry.title,
        content: entry.content,
        mood: entry.mood,
        tags: entry.tags.join(', ')
      });
    } else {
      setFormData({
        title: '',
        content: '',
        mood: 'reflective',
        tags: ''
      });
    }
  }, [entry, isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const processedData = {
      ...formData,
      tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
    };
    onSave(processedData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-xl p-6 w-full max-w-2xl border border-gray-800 max-h-screen overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">
            {entry ? 'Edit Entry' : 'New Journal Entry'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
            disabled={loading}
          >
            <Plus size={20} className="text-gray-400 rotate-45" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Title
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              placeholder="What's on your mind?"
              required
              disabled={loading}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Your Thoughts
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              rows="10"
              placeholder="Express your thoughts, feelings, and reflections..."
              required
              disabled={loading}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Mood
              </label>
              <select
                value={formData.mood}
                onChange={(e) => setFormData({ ...formData, mood: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                disabled={loading}
              >
                <option value="optimistic">Optimistic</option>
                <option value="inspired">Inspired</option>
                <option value="reflective">Reflective</option>
                <option value="challenging">Challenging</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Tags (comma separated)
              </label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                placeholder="growth, reflection, goals"
                disabled={loading}
              />
            </div>
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 px-4 rounded-lg border border-gray-700 text-gray-300 hover:bg-gray-800 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 hover:scale-105 flex items-center justify-center space-x-2"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
              disabled={loading}
            >
              {loading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <span>{entry ? 'Update' : 'Save Entry'}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Journal = () => {
  const [entries, setEntries] = useState([]);
  const [filteredEntries, setFilteredEntries] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [insights, setInsights] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [viewingEntry, setViewingEntry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [modalLoading, setModalLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // New state for advanced features
  const [currentView, setCurrentView] = useState('entries'); // 'entries', 'insights', 'templates'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMoodFilter, setSelectedMoodFilter] = useState('');
  const [selectedTagFilter, setSelectedTagFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchEntries();
    fetchTemplates();
    fetchInsights();
  }, []);

  useEffect(() => {
    // Filter entries based on search and filters
    let filtered = entries;

    if (searchTerm) {
      filtered = filtered.filter(entry =>
        entry.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        entry.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        entry.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    if (selectedMoodFilter) {
      filtered = filtered.filter(entry => entry.mood === selectedMoodFilter);
    }

    if (selectedTagFilter) {
      filtered = filtered.filter(entry => entry.tags.includes(selectedTagFilter));
    }

    setFilteredEntries(filtered);
  }, [entries, searchTerm, selectedMoodFilter, selectedTagFilter]);

  const fetchEntries = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await journalAPI.getEntries();
      setEntries(response.data);
    } catch (err) {
      setError(handleApiError(err, 'Failed to load journal entries'));
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await journalAPI.getTemplates();
      setTemplates(response.data);
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  };

  const fetchInsights = async () => {
    try {
      const response = await journalAPI.getInsights();
      setInsights(response.data);
    } catch (err) {
      console.error('Failed to load insights:', err);
    }
  };

  const handleCreateEntry = () => {
    setSelectedEntry(null);
    setModalOpen(true);
  };

  const handleEditEntry = (entry) => {
    setSelectedEntry(entry);
    setModalOpen(true);
    setViewingEntry(null);
  };

  const handleViewEntry = (entry) => {
    setViewingEntry(entry);
  };

  const handleSaveEntry = async (formData) => {
    try {
      setModalLoading(true);
      
      if (selectedEntry) {
        await journalAPI.updateEntry(selectedEntry.id, formData);
        // Update local state
        setEntries(prev => prev.map(entry =>
          entry.id === selectedEntry.id
            ? { ...entry, ...formData, tags: formData.tags || [] }
            : entry
        ));
      } else {
        const response = await journalAPI.createEntry(formData);
        // Add to local state
        setEntries(prev => [response.data, ...prev]);
      }
      
      setModalOpen(false);
      setSelectedEntry(null);
    } catch (err) {
      setError(handleApiError(err, selectedEntry ? 'Failed to update entry' : 'Failed to create entry'));
    } finally {
      setModalLoading(false);
    }
  };

  const handleDeleteEntry = async (entryId) => {
    if (!window.confirm('Are you sure you want to delete this journal entry?')) return;
    
    try {
      await journalAPI.deleteEntry(entryId);
      setEntries(prev => prev.filter(entry => entry.id !== entryId));
      setViewingEntry(null);
    } catch (err) {
      setError(handleApiError(err, 'Failed to delete entry'));
    }
  };

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Personal Journal</h1>
          <p className="text-gray-400">Reflect, explore, and document your growth journey</p>
        </div>
        <button
          onClick={handleCreateEntry}
          className="flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
          style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
        >
          <Plus size={20} />
          <span>New Entry</span>
        </button>
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
          <BarChart3 size={16} />
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
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center space-x-2">
          <AlertCircle size={20} className="text-red-400" />
          <span className="text-red-400">{error}</span>
          <button
            onClick={fetchEntries}
            className="ml-auto px-3 py-1 rounded bg-red-500 hover:bg-red-600 text-white text-sm transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Search and Filter Bar (only for Entries view) */}
      {currentView === 'entries' && (
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search entries..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
                showFilters 
                  ? 'border-yellow-400 bg-yellow-400/10 text-yellow-400' 
                  : 'border-gray-700 text-gray-400 hover:text-white hover:border-gray-600'
              }`}
            >
              <Filter size={16} />
              <span>Filters</span>
            </button>
          </div>

          {/* Filter Options */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 rounded-lg bg-gray-800/30 border border-gray-700">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Mood Filter</label>
                <select
                  value={selectedMoodFilter}
                  onChange={(e) => setSelectedMoodFilter(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                >
                  <option value="">All Moods</option>
                  <option value="optimistic">Optimistic</option>
                  <option value="inspired">Inspired</option>
                  <option value="reflective">Reflective</option>
                  <option value="challenging">Challenging</option>
                  <option value="anxious">Anxious</option>
                  <option value="grateful">Grateful</option>
                  <option value="excited">Excited</option>
                  <option value="frustrated">Frustrated</option>
                  <option value="peaceful">Peaceful</option>
                  <option value="motivated">Motivated</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Tag Filter</label>
                <select
                  value={selectedTagFilter}
                  onChange={(e) => setSelectedTagFilter(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                >
                  <option value="">All Tags</option>
                  {[...new Set(entries.flatMap(entry => entry.tags || []))].map(tag => (
                    <option key={tag} value={tag}>{tag}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Render different views based on currentView */}
      {currentView === 'entries' && renderEntriesView()}
      {currentView === 'insights' && renderInsightsView()}
      {currentView === 'templates' && renderTemplatesView()}

      {/* Create/Edit Modal */}
      <JournalModal
        entry={selectedEntry}
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedEntry(null);
        }}
        onSave={handleSaveEntry}
        loading={modalLoading}
        templates={templates}
      />

      {/* View Modal */}
      {viewingEntry && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 rounded-xl p-6 w-full max-w-2xl border border-gray-800 max-h-screen overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">{viewingEntry.title}</h2>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => {
                    setViewingEntry(null);
                    handleEditEntry(viewingEntry);
                  }}
                  className="px-4 py-2 rounded-lg bg-yellow-400 text-gray-900 hover:bg-yellow-300 transition-colors"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteEntry(viewingEntry.id)}
                  className="px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors"
                >
                  Delete
                </button>
                <button
                  onClick={() => setViewingEntry(null)}
                  className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
                >
                  <Plus size={20} className="text-gray-400 rotate-45" />
                </button>
              </div>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-400 mb-2">
                {new Date(viewingEntry.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
              <div className="flex items-center space-x-4 mb-4">
                <span className="text-sm text-gray-400 capitalize">Mood: {viewingEntry.mood}</span>
                <div className="flex items-center space-x-2">
                  {(viewingEntry.tags || []).map((tag, index) => (
                    <span 
                      key={index}
                      className="px-2 py-1 rounded-full bg-gray-800 text-xs text-yellow-400 border border-gray-700"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="prose prose-invert max-w-none">
              <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">
                {viewingEntry.content}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Journal;