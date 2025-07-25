import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Edit2, 
  Trash2, 
  Target, 
  BarChart3, 
  FolderOpen, 
  Calendar,
  AlertCircle,
  X,
  Save,
  Layers,
  Archive,
  ArchiveRestore,
  Eye,
  EyeOff,
  Mountain
} from 'lucide-react';
import { areasAPI, api } from '../services/api';
import { useDataContext } from '../contexts/DataContext';
import DonutChart from './ui/DonutChart';
import IconPicker from './ui/IconPicker';
import { 
  getDynamicFontSize, 
  validateTextLength, 
  CHARACTER_LIMITS,
  getCharacterCounterData
} from '../utils/textUtils';

const Areas = ({ onSectionChange }) => {
  const { onDataMutation } = useDataContext();
  const [areas, setAreas] = useState([]);
  const [pillars, setPillars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingArea, setEditingArea] = useState(null);
  const [showArchived, setShowArchived] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#F4B400',
    icon: '🎯', // Use emoji instead of component reference
    pillar_id: '',
    importance: 3  // Default to medium importance
  });

  // Remove old iconOptions and getIconComponent - we'll use emoji icons now
  const colorOptions = [
    '#F4B400', '#EF4444', '#10B981', '#3B82F6', '#8B5CF6',
    '#F59E0B', '#06B6D4', '#84CC16', '#F97316', '#EC4899'
  ];

  const loadAreas = async () => {
    try {
      setLoading(true);
      const response = await areasAPI.getAreas(true, showArchived); // Include projects and optionally archived
      setAreas(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load areas');
      console.error('Error loading areas:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadPillars = async () => {
    try {
      const response = await api.get('/pillars', {
        params: {
          include_sub_pillars: false,
          include_areas: false,
          include_archived: false
        }
      });
      setPillars(response.data);
    } catch (err) {
      console.error('Error loading pillars:', err);
    }
  };

  useEffect(() => {
    loadAreas();
    loadPillars();
  }, [showArchived]); // Reload when showArchived changes

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingArea) {
        await areasAPI.updateArea(editingArea.id, formData);
        // Notify data context of the mutation
        onDataMutation('area', 'update', { areaId: editingArea.id, ...formData });
      } else {
        const response = await areasAPI.createArea(formData);
        // Notify data context of the mutation
        onDataMutation('area', 'create', response.data || formData);
      }
      loadAreas();
      handleCloseModal();
    } catch (err) {
      console.error('Error saving area:', err);
      setError(editingArea ? 'Failed to update area' : 'Failed to create area');
    }
  };

  const handleArchive = async (areaId, isArchived) => {
    try {
      if (isArchived) {
        await areasAPI.unarchiveArea(areaId);
        // Notify data context of the mutation
        onDataMutation('area', 'unarchive', { areaId });
      } else {
        await areasAPI.archiveArea(areaId);
        // Notify data context of the mutation  
        onDataMutation('area', 'archive', { areaId });
      }
      loadAreas();
    } catch (err) {
      console.error('Error archiving/unarchiving area:', err);
      setError(`Failed to ${isArchived ? 'unarchive' : 'archive'} area`);
    }
  };

  const handleDelete = async (areaId) => {
    if (window.confirm('Are you sure? This will delete all projects and tasks in this area.')) {
      try {
        await areasAPI.deleteArea(areaId);
        loadAreas();
        // Notify data context of the mutation
        onDataMutation('area', 'delete', { areaId });
      } catch (err) {
        console.error('Error deleting area:', err);
        setError('Failed to delete area');
      }
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingArea(null);
    setFormData({
      name: '',
      description: '',
      color: '#F4B400',
      icon: '🎯',
      pillar_id: '',
      importance: 3
    });
  };

  const handleEdit = (area) => {
    setEditingArea(area);
    setFormData({
      name: area.name,
      description: area.description || '',
      color: area.color || '#F4B400',
      icon: area.icon || '🎯', // Use emoji icon
      pillar_id: area.pillar_id || '',
      importance: area.importance || 3
    });
    setShowModal(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-48 bg-gray-800 rounded-xl"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
              Life Areas
            </h1>
            <p className="text-gray-400 mt-1">
              Organize your life into meaningful domains
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {/* Archive Toggle */}
            <button
              onClick={() => setShowArchived(!showArchived)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                showArchived 
                  ? 'bg-gray-700 text-white border border-gray-600' 
                  : 'bg-gray-800 text-gray-400 border border-gray-700 hover:bg-gray-700'
              }`}
            >
              {showArchived ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              <span>{showArchived ? 'Hide Archived' : 'Show Archived'}</span>
            </button>
            <button
              onClick={() => setShowModal(true)}
              className="flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:shadow-lg"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              <Plus className="h-5 w-5" />
              <span>New Area</span>
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/20 border border-red-600 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
              <span className="text-red-400">{error}</span>
            </div>
          </div>
        )}

        {/* Areas Grid */}
        {areas.length === 0 ? (
          <div className="text-center py-12">
            <Layers className="mx-auto h-16 w-16 text-gray-600 mb-4" />
            <h3 className="text-xl font-medium text-gray-400 mb-2">No areas yet</h3>
            <p className="text-gray-500 mb-6">Create your first life area to get started</p>
            <button
              onClick={() => setShowModal(true)}
              className="px-6 py-3 rounded-lg font-medium"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              Create First Area
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {areas.map((area) => {
              return (
                <div
                  key={area.id}
                  className={`bg-gray-900/50 border rounded-xl p-6 hover:border-gray-700 transition-all duration-200 hover:shadow-lg cursor-pointer ${
                    area.archived ? 'border-gray-700 opacity-75' : 'border-gray-800'
                  }`}
                  onClick={() => onSectionChange && onSectionChange('projects', { areaId: area.id })}
                >
                  {/* Area Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <div
                        className="p-3 rounded-lg flex-shrink-0"
                        style={{ backgroundColor: area.color + '20' }}
                      >
                        <span className="text-2xl">{area.icon || '🎯'}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className={`font-semibold text-white dynamic-text ${getDynamicFontSize(area.name, 'title')}`}>
                            {area.name}
                          </h3>
                          {area.archived && (
                            <span className="px-2 py-1 text-xs rounded-full bg-gray-600 text-gray-300 flex-shrink-0">
                              Archived
                            </span>
                          )}
                        </div>
                        <div className="flex flex-wrap items-center gap-2 text-sm text-gray-400 mb-1">
                          {area.pillar_name && (
                            <div className="flex items-center space-x-1 flex-shrink-0">
                              <Mountain className="h-3 w-3 flex-shrink-0" />
                              <span className="dynamic-text">{area.pillar_name}</span>
                            </div>
                          )}
                          <span className="flex-shrink-0">
                            {area.projects?.length || 0} projects
                          </span>
                          {area.date_created && (
                            <span className="text-xs text-gray-500 dynamic-text">
                              Created {new Date(area.date_created).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                        {/* Importance Indicator */}
                        {area.importance && (
                          <div className="mt-2">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              area.importance >= 5 ? 'bg-red-900/30 text-red-300 border border-red-600' :
                              area.importance >= 4 ? 'bg-orange-900/30 text-orange-300 border border-orange-600' :
                              area.importance >= 3 ? 'bg-yellow-900/30 text-yellow-300 border border-yellow-600' :
                              'bg-gray-800/30 text-gray-400 border border-gray-600'
                            }`}>
                              {area.importance >= 5 ? '🔥 Critical' :
                               area.importance >= 4 ? '⚡ High' :
                               area.importance >= 3 ? '📊 Medium' :
                               '📝 Low'}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleArchive(area.id, area.archived);
                        }}
                        className={`p-2 rounded-lg transition-colors ${
                          area.archived
                            ? 'text-blue-400 hover:text-blue-300 hover:bg-gray-800'
                            : 'text-gray-400 hover:text-yellow-400 hover:bg-gray-800'
                        }`}
                        title={area.archived ? 'Unarchive Area' : 'Archive Area'}
                      >
                        {area.archived ? <ArchiveRestore className="h-4 w-4" /> : <Archive className="h-4 w-4" />}
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(area);
                        }}
                        className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(area.id);
                        }}
                        className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {/* Description */}
                  {area.description && (
                    <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                      {area.description}
                    </p>
                  )}

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-2xl font-bold text-white">
                        {area.projects?.filter(p => p.status === 'active').length || 0}
                      </p>
                      <p className="text-xs text-gray-500">Active Projects</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">
                        {area.total_task_count || 0}
                      </p>
                      <p className="text-xs text-gray-500">Total Tasks</p>
                    </div>
                  </div>

                  {/* Progress Visualization */}
                  <div className="mt-4">
                    {/* Traditional Progress Bar */}
                    <div className="mb-4">
                      <div className="w-full bg-gray-800 rounded-full h-2">
                        <div
                          className="h-2 rounded-full transition-all duration-300"
                          style={{
                            backgroundColor: area.color,
                            width: `${area.total_task_count > 0 ? (area.completed_task_count / area.total_task_count) * 100 : 0}%`
                          }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {area.completed_task_count || 0} of {area.total_task_count || 0} tasks complete
                      </p>
                    </div>

                    {/* Enhanced Donut Chart Visualization */}
                    {area.total_task_count > 0 && (
                      <div className="flex justify-center mt-4">
                        <DonutChart
                          data={{
                            labels: ['Completed', 'Active', 'Not Started'],
                            values: [
                              area.completed_task_count || 0,
                              Math.max(0, (area.total_task_count || 0) - (area.completed_task_count || 0)),
                              0 // For now, we don't distinguish between active and not started
                            ],
                            colors: [
                              '#10B981', // Green for completed
                              area.color, // Area color for active
                              '#6B7280', // Gray for not started
                            ]
                          }}
                          size="sm"
                          showLegend={false}
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-gray-900 rounded-xl p-6 w-full max-w-md border border-gray-800">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">
                  {editingArea ? 'Edit Area' : 'Create New Area'}
                </h2>
                <button
                  onClick={handleCloseModal}
                  className="p-2 text-gray-400 hover:text-white rounded-lg"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="input-with-counter">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => {
                      const newValue = e.target.value;
                      if (newValue.length <= CHARACTER_LIMITS.AREA_NAME) {
                        setFormData({ ...formData, name: newValue });
                      }
                    }}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="e.g., Health & Fitness"
                    maxLength={CHARACTER_LIMITS.AREA_NAME}
                    required
                  />
                  <div className={getCharacterCounterData(formData.name, CHARACTER_LIMITS.AREA_NAME).className}>
                    {getCharacterCounterData(formData.name, CHARACTER_LIMITS.AREA_NAME).count}/{CHARACTER_LIMITS.AREA_NAME}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="Brief description of this life area"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Pillar
                  </label>
                  <select
                    value={formData.pillar_id}
                    onChange={(e) => setFormData({ ...formData, pillar_id: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  >
                    <option value="">No Pillar</option>
                    {pillars.map((pillar) => (
                      <option key={pillar.id} value={pillar.id}>
                        {pillar.icon} {pillar.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Icon Picker */}
                <IconPicker
                  value={formData.icon}
                  onChange={(icon) => setFormData({ ...formData, icon })}
                  label="Icon"
                  placeholder="🎯"
                  required={false}
                  iconSet="areas"
                  allowCustom={true}
                />

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Color
                  </label>
                  <div className="grid grid-cols-5 gap-2">
                    {colorOptions.map((color) => (
                      <button
                        key={color}
                        type="button"
                        onClick={() => setFormData({ ...formData, color })}
                        className={`w-10 h-10 rounded-lg border-2 transition-all ${
                          formData.color === color
                            ? 'border-white scale-110'
                            : 'border-gray-600 hover:border-gray-500'
                        }`}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>

                {/* Importance Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Importance Level
                  </label>
                  <select
                    value={formData.importance}
                    onChange={(e) => setFormData({ ...formData, importance: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  >
                    <option value={1}>1 - Low Impact</option>
                    <option value={2}>2 - Minor Impact</option>
                    <option value={3}>3 - Medium Impact</option>
                    <option value={4}>4 - High Impact</option>
                    <option value={5}>5 - Critical Impact</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    How important is this area to your overall life goals?
                  </p>
                </div>

                <div className="flex space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors"
                    style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
                  >
                    <Save className="h-4 w-4" />
                    <span>{editingArea ? 'Update' : 'Create'}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Areas;