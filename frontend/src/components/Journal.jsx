import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Calendar, Tag, Smile, Meh, Frown } from 'lucide-react';
import { mockJournalEntries, getStoredData, setStoredData } from '../data/mock';

const JournalEntry = ({ entry, onClick }) => {
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

  return (
    <div 
      onClick={() => onClick(entry)}
      className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30 transition-all duration-300 cursor-pointer group hover:scale-105"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white group-hover:text-yellow-400 transition-colors">
          {entry.title}
        </h3>
        <div className="flex items-center space-x-2">
          {getMoodIcon(entry.mood)}
          <span className="text-sm text-gray-400">{entry.date}</span>
        </div>
      </div>
      
      <p className="text-gray-300 text-sm mb-4 line-clamp-3">
        {entry.content.substring(0, 200)}...
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

const JournalModal = ({ entry, isOpen, onClose, onSave }) => {
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
              />
            </div>
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 px-4 rounded-lg border border-gray-700 text-gray-300 hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 hover:scale-105"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              {entry ? 'Update' : 'Save Entry'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Journal = () => {
  const [entries, setEntries] = useState(() => getStoredData('journal', mockJournalEntries));
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [viewingEntry, setViewingEntry] = useState(null);

  useEffect(() => {
    setStoredData('journal', entries);
  }, [entries]);

  const handleCreateEntry = () => {
    setSelectedEntry(null);
    setModalOpen(true);
  };

  const handleEditEntry = (entry) => {
    setSelectedEntry(entry);
    setModalOpen(true);
  };

  const handleViewEntry = (entry) => {
    setViewingEntry(entry);
  };

  const handleSaveEntry = (formData) => {
    if (selectedEntry) {
      setEntries(prev => prev.map(entry =>
        entry.id === selectedEntry.id
          ? { ...entry, ...formData }
          : entry
      ));
    } else {
      const newEntry = {
        id: Date.now().toString(),
        ...formData,
        date: new Date().toISOString().split('T')[0]
      };
      setEntries(prev => [newEntry, ...prev]);
    }
    setModalOpen(false);
    setSelectedEntry(null);
  };

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

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <BookOpen size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{entries.length}</h3>
              <p className="text-sm text-gray-400">Total Entries</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <Calendar size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">7</h3>
              <p className="text-sm text-gray-400">Day Streak</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <Tag size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">12</h3>
              <p className="text-sm text-gray-400">Unique Tags</p>
            </div>
          </div>
        </div>
      </div>

      {/* Entries Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {entries.map((entry) => (
          <JournalEntry
            key={entry.id}
            entry={entry}
            onClick={handleViewEntry}
          />
        ))}
      </div>

      {/* Create/Edit Modal */}
      <JournalModal
        entry={selectedEntry}
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedEntry(null);
        }}
        onSave={handleSaveEntry}
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
                  onClick={() => setViewingEntry(null)}
                  className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
                >
                  <Plus size={20} className="text-gray-400 rotate-45" />
                </button>
              </div>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-400 mb-2">{viewingEntry.date}</p>
              <div className="flex items-center space-x-4 mb-4">
                <span className="text-sm text-gray-400 capitalize">Mood: {viewingEntry.mood}</span>
                <div className="flex items-center space-x-2">
                  {viewingEntry.tags.map((tag, index) => (
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