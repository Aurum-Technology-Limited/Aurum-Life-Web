import React, { useState, useEffect, useContext } from 'react';
import { useDataContext } from '../contexts/DataContext';
import { api } from '../services/api';
import { 
  Plus, 
  Layers, 
  Target, 
  TrendingUp, 
  Archive,
  ArchiveRestore,
  Trash2, 
  Edit2,
  ChevronDown,
  ChevronRight,
  BarChart3
} from 'lucide-react';

const Pillars = () => {
  const { onDataMutation } = useDataContext();
  const [pillars, setPillars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPillar, setEditingPillar] = useState(null);
  const [expandedPillars, setExpandedPillars] = useState(new Set());
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    icon: '🎯',
    color: '#F4B400',
    parent_pillar_id: '',
    time_allocation_percentage: null
  });

  // Icon options for pillars
  const iconOptions = ['🎯', '🏃‍♂️', '💪', '🧠', '💼', '❤️', '🌟', '🚀', '🌱', '🎨', '📚', '⚡'];
  const colorOptions = ['#F4B400', '#4CAF50', '#2196F3', '#FF5722', '#9C27B0', '#FF9800', '#795548', '#607D8B'];

  useEffect(() => {
    fetchPillars();
  }, []);

  const fetchPillars = async () => {
    try {
      setLoading(true);
      const response = await api.get('/pillars', {
        params: {
          include_sub_pillars: true,
          include_areas: false,
          include_archived: false
        }
      });
      setPillars(response.data);
    } catch (error) {
      console.error('Error fetching pillars:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        time_allocation_percentage: formData.time_allocation_percentage ? parseFloat(formData.time_allocation_percentage) : null
      };

      if (editingPillar) {
        await api.put(`/pillars/${editingPillar.id}`, submitData);
      } else {
        await api.post('/pillars', submitData);
      }
      
      await fetchPillars();
      onDataMutation?.();
      handleCloseModal();
    } catch (error) {
      console.error('Error saving pillar:', error);
      alert(error.response?.data?.detail || 'Error saving pillar');
    }
  };

  const handleEdit = (pillar) => {
    setEditingPillar(pillar);
    setFormData({
      name: pillar.name,
      description: pillar.description,
      icon: pillar.icon,
      color: pillar.color,
      parent_pillar_id: pillar.parent_pillar_id || '',
      time_allocation_percentage: pillar.time_allocation_percentage || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (pillarId) => {
    if (window.confirm('Are you sure you want to delete this pillar? This will unlink all associated areas.')) {
      try {
        await api.delete(`/pillars/${pillarId}`);
        await fetchPillars();
        onDataMutation?.();
      } catch (error) {
        console.error('Error deleting pillar:', error);
        alert(error.response?.data?.detail || 'Error deleting pillar');
      }
    }
  };

  const handleArchive = async (pillarId) => {
    try {
      await api.put(`/pillars/${pillarId}/archive`);
      await fetchPillars();
      onDataMutation?.();
    } catch (error) {
      console.error('Error archiving pillar:', error);
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingPillar(null);
    setFormData({
      name: '',
      description: '',
      icon: '🎯',
      color: '#F4B400',
      parent_pillar_id: '',
      time_allocation_percentage: null
    });
  };

  const toggleExpanded = (pillarId) => {
    const newExpanded = new Set(expandedPillars);
    if (newExpanded.has(pillarId)) {
      newExpanded.delete(pillarId);
    } else {
      newExpanded.add(pillarId);
    }
    setExpandedPillars(newExpanded);
  };

  const getAvailableParentPillars = () => {
    const flattenPillars = (pillars) => {
      let result = [];
      for (const pillar of pillars) {
        result.push(pillar);
        if (pillar.sub_pillars) {
          result = result.concat(flattenPillars(pillar.sub_pillars));
        }
      }
      return result;
    };
    
    const allPillars = flattenPillars(pillars);
    // Exclude the pillar being edited and its descendants
    return allPillars.filter(p => p.id !== editingPillar?.id);
  };

  const renderPillar = (pillar, depth = 0) => {
    const hasSubPillars = pillar.sub_pillars && pillar.sub_pillars.length > 0;
    const isExpanded = expandedPillars.has(pillar.id);

    return (
      <div key={pillar.id} className="bg-gray-900 rounded-lg shadow-sm border border-gray-800">
        {/* Main Pillar Row */}
        <div 
          className="p-4 hover:bg-gray-800 transition-colors"
          style={{ marginLeft: `${depth * 20}px` }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 flex-1">
              {/* Expand/Collapse Button */}
              <button
                onClick={() => toggleExpanded(pillar.id)}
                className={`p-1 rounded hover:bg-gray-700 transition-colors ${!hasSubPillars ? 'invisible' : ''}`}
              >
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4 text-gray-400" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                )}
              </button>

              {/* Pillar Icon and Color */}
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                style={{ backgroundColor: pillar.color }}
              >
                {pillar.icon}
              </div>

              {/* Pillar Details */}
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h3 className="text-lg font-medium text-white">{pillar.name}</h3>
                  {pillar.time_allocation_percentage && (
                    <span className="text-sm text-gray-400">
                      ({pillar.time_allocation_percentage}%)
                    </span>
                  )}
                </div>
                {pillar.description && (
                  <p className="text-sm text-gray-400 mt-1">{pillar.description}</p>
                )}
                
                {/* Progress Summary */}
                <div className="flex items-center space-x-4 text-xs text-gray-500 mt-2">
                  <span className="flex items-center space-x-1">
                    <Layers className="h-3 w-3" />
                    <span>{pillar.area_count} areas</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <Target className="h-3 w-3" />
                    <span>{pillar.project_count} projects</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <BarChart3 className="h-3 w-3" />
                    <span>{pillar.progress_percentage.toFixed(1)}% complete</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleEdit(pillar)}
                className="p-2 text-gray-400 hover:text-blue-400 hover:bg-gray-800 rounded-lg transition-colors"
                title="Edit Pillar"
              >
                <Edit2 className="h-4 w-4" />
              </button>
              <button
                onClick={() => handleArchive(pillar.id)}
                className="p-2 text-gray-400 hover:text-yellow-400 hover:bg-gray-800 rounded-lg transition-colors"
                title="Archive Pillar"
              >
                <Archive className="h-4 w-4" />
              </button>
              <button
                onClick={() => handleDelete(pillar.id)}
                className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
                title="Delete Pillar"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Sub-Pillars */}
        {hasSubPillars && isExpanded && (
          <div className="border-t border-gray-800">
            {pillar.sub_pillars.map(subPillar => renderPillar(subPillar, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">Pillars</h1>
          <p className="text-gray-400 mt-1">
            Organize your life domains and track high-level progress
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>New Pillar</span>
        </button>
      </div>

      {/* Pillars List */}
      <div className="space-y-3">
        {pillars.length === 0 ? (
          <div className="text-center py-12 bg-gray-900 border border-gray-800 rounded-lg">
            <Layers className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No pillars yet</h3>
            <p className="text-gray-400 mb-4">
              Create your first pillar to organize your life domains
            </p>
            <button
              onClick={() => setShowModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create First Pillar
            </button>
          </div>
        ) : (
          pillars.map(pillar => renderPillar(pillar))
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto border border-gray-800">
            <div className="p-6">
              <h2 className="text-xl font-bold text-white mb-4">
                {editingPillar ? 'Edit Pillar' : 'Create New Pillar'}
              </h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows="3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Icon
                  </label>
                  <div className="grid grid-cols-6 gap-2">
                    {iconOptions.map(icon => (
                      <button
                        key={icon}
                        type="button"
                        onClick={() => setFormData({...formData, icon})}
                        className={`p-2 text-lg rounded-lg border-2 transition-colors ${
                          formData.icon === icon ? 'border-blue-500 bg-blue-500/20' : 'border-gray-700 hover:border-gray-600 bg-gray-800'
                        }`}
                      >
                        {icon}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Color
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {colorOptions.map(color => (
                      <button
                        key={color}
                        type="button"
                        onClick={() => setFormData({...formData, color})}
                        className={`w-8 h-8 rounded-full border-2 transition-all ${
                          formData.color === color ? 'border-white scale-110' : 'border-gray-600'
                        }`}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Parent Pillar
                  </label>
                  <select
                    value={formData.parent_pillar_id}
                    onChange={(e) => setFormData({...formData, parent_pillar_id: e.target.value})}
                    className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">None (Root Pillar)</option>
                    {getAvailableParentPillars().map(pillar => (
                      <option key={pillar.id} value={pillar.id}>
                        {pillar.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Time Allocation (%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={formData.time_allocation_percentage}
                    onChange={(e) => setFormData({...formData, time_allocation_percentage: e.target.value})}
                    className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 25.0"
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="px-4 py-2 text-gray-300 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    {editingPillar ? 'Update Pillar' : 'Create Pillar'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Pillars;