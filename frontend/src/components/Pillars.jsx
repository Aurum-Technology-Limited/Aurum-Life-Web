import React, { useState, useEffect, useContext, memo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useDataContext } from '../contexts/DataContext';
import { api } from '../services/api';
import { usePillarsQuery, useInvalidateQueries } from '../hooks/useQueries';
import {Plus, Trash2, Edit2, Layers} from 'lucide-react';
import IconPicker from './ui/IconPicker';

const Pillars = memo(({ onSectionChange }) => {
  const { onDataMutation } = useDataContext();
  const queryClient = useQueryClient();


  const { invalidatePillars } = useInvalidateQueries();
  
  // Use TanStack Query with include_areas=true to get accurate counts
  const { 
    data: pillarsData = [], 
    isLoading: loading, 
    error, 
    isError,
    refetch 
  } = usePillarsQuery(true, true, false); // includeSubPillars=true, includeAreas=true (REQUIRED for counts), includeArchived=false

  // Ensure we always have an array for rendering
  const pillars = Array.isArray(pillarsData) ? pillarsData : [];
  
  const [showModal, setShowModal] = useState(false);
  const [editingPillar, setEditingPillar] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    icon: '🎯',
    color: '#F4B400',
    time_allocation_percentage: null
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Icon options for pillars - now handled by IconPicker component
  const colorOptions = ['#F4B400', '#4CAF50', '#2196F3', '#FF5722', '#9C27B0', '#FF9800', '#795548', '#607D8B'];

  // Remove old useEffect and fetchPillars - now handled by TanStack Query

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      const submitData = {
        ...formData,
        time_allocation_percentage: formData.time_allocation_percentage ? parseFloat(formData.time_allocation_percentage) : null
      };

      if (editingPillar) {
        const res = await api.put(`/pillars/${editingPillar.id}`, submitData);
        const updated = res?.data || { ...editingPillar, ...submitData };
        // Optimistically update cache
        queryClient.setQueryData(['pillars', true, true, false], (prev) => {
          const arr = Array.isArray(prev) ? prev : [];
          return arr.map(p => (p.id === updated.id ? { ...p, ...updated } : p));
        });
      } else {
        const res = await api.post('/pillars', submitData);
        const created = res?.data || submitData;
        // Ensure created has an id; if not, rely on refetch, but still prepend a temporary item
        const newItem = created.id ? created : { ...created, id: `temp-${Date.now()}` };
        // Optimistically prepend to cache
        queryClient.setQueryData(['pillars', true, true, false], (prev) => {
          const arr = Array.isArray(prev) ? prev : [];
          return [newItem, ...arr];
        });
      }
      
      // Ensure backend writes are visible by invalidating and refetching pillars

      // Trigger data refresh and invalidate cache
      onDataMutation('pillar', editingPillar ? 'update' : 'create', submitData);
      // Invalidate and immediately refetch pillars to reflect new data
      // Ensure query cache is updated and refetched
      await queryClient.invalidateQueries({ predicate: (q) => Array.isArray(q.queryKey) && q.queryKey[0] === 'pillars' });

      // Force-fetch from standard endpoint to bypass any server-side ultra cache and update query cache
      try {
        const fresh = await api.get('/pillars', {
          params: {
            include_sub_pillars: true,
            include_areas: true,
            include_archived: false,
            // cache-buster to avoid intermediary caches
            _ts: Date.now()
          }
        });
        // Update the primary pillars query cache directly
        queryClient.setQueryData(['pillars', true, true, false], fresh.data);
      } catch (e) {
        console.warn('Fallback pillars fetch failed, will rely on refetch()', e?.message);
      }

      await refetch();
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
      time_allocation_percentage: pillar.time_allocation_percentage || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (pillar) => {
    const areaCount = pillar.area_count || 0;
    const projectCount = pillar.project_count || 0;
    const taskCount = pillar.task_count || 0;
    const message = `Are you sure you want to delete "${pillar.name}"?\n\nThis will permanently delete:\n• ${areaCount} Area(s) under this Pillar\n• ${projectCount} Project(s) in those Areas\n• ${taskCount} Task(s) in those Projects\n\nThis action cannot be undone.`;
    if (window.confirm(message)) {
      try {
        await api.delete(`/pillars/${pillar.id}`);
        // Trigger data refresh and invalidate cache
        onDataMutation('pillar', 'delete', { id: pillar.id, name: pillar.name });
        await queryClient.invalidateQueries({ predicate: (q) => Array.isArray(q.queryKey) && q.queryKey[0] === 'pillars' });
        // Also invalidate related caches
        await queryClient.invalidateQueries({ predicate: (q) => Array.isArray(q.queryKey) && ['areas', 'projects', 'tasks'].includes(q.queryKey[0]) });
        // Hydrate pillars from standard endpoint to avoid ultra staleness
        try {
          const fresh = await api.get('/pillars', {
            params: { include_sub_pillars: true, include_areas: true, include_archived: false, _ts: Date.now() }
          });
          queryClient.setQueryData(['pillars', true, true, false], fresh.data);
        } catch (e) {
          console.warn('Pillars standard fetch hydration after delete failed:', e?.message || e);
        }
        await refetch(); // Ensure UI updates immediately
      } catch (error) {
        console.error('Error deleting pillar:', error);
        alert(error.response?.data?.detail || 'Error deleting pillar');
      }
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
      time_allocation_percentage: null
    });
  };

  const renderPillar = (pillar) => {
    const handlePillarClick = () => {
      // Navigate to areas section filtered by this pillar
      onSectionChange('areas', { pillarId: pillar.id, pillarName: pillar.name });
    };

    return (
      <div 
        key={pillar.id} 
        className="bg-gray-900 rounded-lg shadow-sm border border-gray-800 cursor-pointer hover:border-gray-700 transition-all duration-200 hover:shadow-lg"
        onClick={handlePillarClick}
        title={`Click to view areas for ${pillar.name}`}
      >
        {/* Main Pillar Row */}
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 flex-1">
              <div 
                className="w-12 h-12 rounded-lg flex items-center justify-center text-xl"
                style={{ backgroundColor: pillar.color }}
              >
                {pillar.icon}
              </div>
              
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white">{pillar.name}</h3>
                {pillar.description && (
                  <p className="text-gray-400 text-sm mt-1">{pillar.description}</p>
                )}
                
                {/* Progress Stats */}
                <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                  <span className="flex items-center space-x-1">
                    <span className="font-medium text-blue-400">{pillar.area_count || 0}</span>
                    <span>areas</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <span className="font-medium text-green-400">{pillar.project_count || 0}</span>
                    <span>projects</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <span className="font-medium text-yellow-400">{pillar.task_count || 0}</span>
                    <span>tasks</span>
                  </span>
                  {pillar.progress_percentage > 0 && (
                    <span className="text-green-400">{pillar.progress_percentage.toFixed(1)}% complete</span>
                  )}
                  {pillar.created_at && (
                    <span className="text-gray-400">Created {new Date(pillar.created_at).toLocaleDateString()}</span>
                  )}
                </div>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              <button
                data-testid={`pillar-edit-${pillar.id}`}
                onClick={(e) => {
                  e.stopPropagation();
                  handleEdit(pillar);
                }}
                className="p-2 text-gray-400 hover:text-yellow-400 hover:bg-gray-800 rounded-lg transition-colors"
                title="Edit pillar"
              >
                <Edit2 size={16} />
              </button>
              
              <button
                data-testid={`pillar-delete-${pillar.id}`}
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(pillar);
                }}
                className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
                title="Delete pillar"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Handle loading and error states for TanStack Query
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-6">
        <div className="text-center">
          <p className="text-red-400 mb-4">Error loading pillars: {error?.message || 'Unknown error'}</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
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
          data-testid="pillar-new"
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
              
              <form onSubmit={handleSubmit} className="space-y-4" data-testid="pillar-form">
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

                {/* Icon Picker */}
                <IconPicker
                  value={formData.icon}
                  onChange={(icon) => setFormData({...formData, icon})}
                  label="Icon"
                  placeholder="🎯"
                  required={false}
                  iconSet="pillars"
                  allowCustom={true}
                />

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
});

Pillars.displayName = 'Pillars';

export default Pillars;