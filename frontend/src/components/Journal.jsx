import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, AlertCircle, BookOpen, TrendingUp, FileText, RotateCcw, Search, Filter, Calendar, Tag, Smile, Meh, Frown, X } from 'lucide-react';
import { journalAPI, handleApiError } from '../services/api';

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

  // Handle create entry
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
      setShowCreateModal(false);
      setError(null);
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
      const response = await journalAPI.getEntries(0, 20, selectedMoodFilter, selectedTagFilter);
      const data = response.data || [];
      setEntries(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
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
      const response = await journalAPI.getTemplates();
      const data = response.data || [];
      setTemplates(Array.isArray(data) ? data : []);
    } catch (err) {
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
                <h3 className="text-lg font-semibold text-white">{entry.title}</h3>
                <span className="text-xs text-gray-500">{new Date(entry.created_at).toLocaleDateString()}</span>
              </div>
              <p className="text-gray-300 text-sm mb-4 line-clamp-3">{entry.content}</p>
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

  const renderInsightsView = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Journal Insights</h2>
      <div className="text-center py-12">
        <div className="w-16 h-16 rounded-lg bg-blue-400/20 flex items-center justify-center mx-auto mb-4">
          <TrendingUp size={32} className="text-blue-400" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">Insights Coming Soon</h3>
        <p className="text-gray-400">We're working on providing meaningful insights from your journal entries.</p>
      </div>
    </div>
  );

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
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={24} />
              </button>
            </div>
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
                onChange={(e) => setNewEntryContent(e.target.value)}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 resize-none"
              />
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setNewEntryTitle('');
                    setNewEntryContent('');
                    setError(null);
                  }}
                  className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateEntry}
                  className="px-4 py-2 bg-yellow-400 text-gray-900 rounded-lg hover:bg-yellow-300 transition-colors"
                >
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