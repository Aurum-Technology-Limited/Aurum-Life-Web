import React, { useState, useEffect, memo } from 'react';
import {Plus, Edit2, Trash2, AlertCircle, X, Save, Layers, Archive, ArchiveRestore, Eye, EyeOff, Mountain} from 'lucide-react';
import { areasAPI, api, pillarsAPI } from '../services/api';
import { useDataContext } from '../contexts/DataContext';
import {useAreasQuery, usePillarsQuery} from '../hooks/useQueries';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import DonutChart from './ui/DonutChart';
import IconPicker from './ui/IconPicker';
import {getDynamicFontSize, CHARACTER_LIMITS, getCharacterCounterData} from '../utils/textUtils';

// Memoized AreaCard component to prevent unnecessary re-renders
const AreaCard = memo(({ area, onSectionChange, onArchive, onEdit, onDelete }) => (
  <div
    key={area.id}
    className={`bg-gray-900/50 border rounded-xl p-6 hover:border-gray-700 transition-all duration-200 hover:shadow-lg cursor-pointer ${
      area.archived ? 'border-gray-700 opacity-75' : 'border-gray-800'
    }`}
    onClick={() => onSectionChange && onSectionChange('projects', { areaId: area.id, areaName: area.name })}
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
            onArchive(area.id, area.archived);
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
          data-testid={`area-edit-${area.id}`}
          onClick={(e) => {
            e.stopPropagation();
            onEdit(area);
          }}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
        >
          <Edit2 className="h-4 w-4" />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(area.id);
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
          {area.project_count ? (area.project_count - (area.completed_project_count || 0)) : 
           area.projects?.filter(p => p.status && p.status.toLowerCase() === 'active').length || 0}
        </p>
        <p className="text-xs text-gray-400">Active Projects</p>
      </div>
      <div>
        <p className="text-2xl font-bold text-white">
          {area.completed_project_count || 
           area.projects?.filter(p => p.status && p.status.toLowerCase() === 'completed').length || 0}
        </p>
        <p className="text-xs text-gray-400">Completed</p>
      </div>
    </div>

    {/* Progress Bar */}
    {area.projects && area.projects.length > 0 && (
      <div className="mt-4">
        <div className="flex justify-between text-xs text-gray-400 mb-2">
          <span>Progress</span>
          <span>
            {Math.round(
              ((area.projects?.filter(p => p.status === 'completed').length || 0) / 
               area.projects.length) * 100
            )}%
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className="h-2 rounded-full transition-all duration-500"
            style={{
              backgroundColor: area.color || '#F4B400',
              width: `${Math.round(
                ((area.projects?.filter(p => p.status === 'completed').length || 0) / 
                 area.projects.length) * 100
              )}%`
            }}
          />
        </div>
      </div>
    )}
  </div>
));

AreaCard.displayName = 'AreaCard';

const Areas = memo(({ onSectionChange, sectionParams }) => {
  const { onDataMutation } = useDataContext();
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingArea, setEditingArea] = useState(null);
  const [showArchived, setShowArchived] = useState(false);
  
  // Extract pillar filter from section params
  const activePillarId = sectionParams?.pillarId || null;
  const activePillarName = sectionParams?.pillarName || null;
  
  // Use TanStack Query for areas and pillars data
  const { 
    data: allAreas = [], 
    isLoading: loading, 
    error, 
    isError,
    refetch: refetchAreas 
  } = useAreasQuery(true, showArchived); // Include projects, respect archived filter
  
  // Filter areas by pillar if pillarId is provided
  const areas = activePillarId 
    ? allAreas.filter(area => area.pillar_id === activePillarId)
    : allAreas;
  
  // Get basic pillars data for filtering (separate from main pillars page)
  const { 
    data: pillars = [], 
    isLoading: pillarsLoading 
  } = useQuery({
    queryKey: ['pillars', 'basic'], // Different query key to avoid cache conflicts
    queryFn: async () => {
      const response = await pillarsAPI.getPillars(false, false, false); // Basic pillars without counts
      return response.data; // Ensure we return an array of pillars, not the axios response object
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
  
  // Create mutations for area operations
  const updateAreaMutation = useMutation({
    mutationFn: ({ areaId, areaData }) => areasAPI.updateArea(areaId, areaData),
    onSuccess: (resp) => {
      const updated = resp?.data || resp;
      console.log('🗂️ Areas: Update mutation successful:', updated);
      // Optimistically update query caches for areas (with and without projects)
      queryClient.setQueryData(['areas', true, showArchived], (prev) => {
        const arr = Array.isArray(prev) ? prev : [];
        return arr.map(a => (a.id === updated.id ? { ...a, ...updated } : a));
      });
      queryClient.setQueryData(['areas', false, showArchived], (prev) => {
        const arr = Array.isArray(prev) ? prev : [];
        return arr.map(a => (a.id === updated.id ? { ...a, ...updated } : a));
      });
      // Invalidate to ensure server truth
      queryClient.invalidateQueries({ queryKey: ['areas'] });
      onDataMutation('area', 'update', updated);
    },
    onError: (error) => {
      console.error('🗂️ Areas: Update mutation failed:', error);
      alert(`Failed to update area: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
    }
  });
  
  const createAreaMutation = useMutation({
    mutationFn: (areaData) => areasAPI.createArea(areaData),
    onSuccess: (resp) => {
      const created = resp?.data || resp;
      const newItem = created?.id ? created : { ...created, id: `temp-${Date.now()}` };
      console.log('🗂️ Areas: Create mutation successful:', newItem);
      // Optimistically prepend to both areas caches (with and without projects)
      queryClient.setQueryData(['areas', true, showArchived], (prev) => {
        const arr = Array.isArray(prev) ? prev : [];
        return [newItem, ...arr];
      });
      queryClient.setQueryData(['areas', false, showArchived], (prev) => {
        const arr = Array.isArray(prev) ? prev : [];
        return [newItem, ...arr];
      });
      // Immediately invalidate to fetch server truth
      queryClient.invalidateQueries({ queryKey: ['areas'] });
      onDataMutation('area', 'create', newItem);
    },
    onError: (error) => {
      console.error('🗂️ Areas: Create mutation failed:', error);
      alert(`Failed to create area: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
    }
  });
  
  const archiveAreaMutation = useMutation({
    mutationFn: ({ areaId, isArchived }) => areasAPI.archiveArea(areaId, !isArchived),
    onSuccess: (data, variables) => {
      console.log('🗂️ Areas: Archive mutation successful:', data);
      // Invalidate and refetch areas data
      queryClient.invalidateQueries({ queryKey: ['areas'] });
      onDataMutation('area', 'archive', { areaId: variables.areaId, archived: !variables.isArchived });
    },
    onError: (error, variables) => {
      console.error('🗂️ Areas: Archive mutation failed:', error);
      alert(`Failed to ${variables.isArchived ? 'unarchive' : 'archive'} area: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
    }
  });
  
  const deleteAreaMutation = useMutation({
    mutationFn: (areaId) => areasAPI.deleteArea(areaId),
    onSuccess: (data, areaId) => {
      console.log('🗂️ Areas: Delete mutation successful:', data);
      // Invalidate and refetch areas data
      queryClient.invalidateQueries({ queryKey: ['areas'] });
      onDataMutation('area', 'delete', { areaId });
    },
    onError: (error) => {
      console.error('🗂️ Areas: Delete mutation failed:', error);
      alert(`Failed to delete area: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
    }
  });
  
  // Performance logging
  useEffect(() => {
    if (loading) {
      console.log('🗂️ Areas: TanStack Query - Loading areas data...');
    } else if (areas.length >= 0) {
      console.log(`🗂️ Areas: TanStack Query - ${areas.length} areas loaded from cache/network`);
    }
  }, [loading, areas.length]);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#F4B400',
    icon: '🎯', // Use emoji instead of component reference
    pillar_id: activePillarId || '', // Pre-populate with active pillar
    importance: 3  // Default to medium importance
  });

  // Remove old iconOptions and getIconComponent - we'll use emoji icons now
  const colorOptions = [
    '#F4B400', '#EF4444', '#10B981', '#3B82F6', '#8B5CF6',
    '#F59E0B', '#06B6D4', '#84CC16', '#F97316', '#EC4899'
  ];

  // Old manual data loading functions removed - TanStack Query handles this automatically
  // Data is now fetched via useAreasQuery and usePillarsQuery hooks above

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('🗂️ Areas: Submitting form...', { editingArea: !!editingArea, formData });
    
    try {
      if (editingArea) {
        console.log('🗂️ Areas: Updating area with ID:', editingArea.id);
        await updateAreaMutation.mutateAsync({ areaId: editingArea.id, areaData: formData });
      } else {
        console.log('🗂️ Areas: Creating new area');
        await createAreaMutation.mutateAsync(formData);
      }
      
      handleCloseModal();
      console.log('🗂️ Areas: Form submission successful');
    } catch (err) {
      // Error handling is done in the mutation's onError callback
      console.error('🗂️ Areas: Form submission failed:', err);
    }
  };

  const handleArchive = async (areaId, isArchived) => {
    console.log('🗂️ Areas: Archiving/unarchiving area:', { areaId, isArchived });
    try {
      await archiveAreaMutation.mutateAsync({ areaId, isArchived });
      console.log('🗂️ Areas: Archive operation successful');
    } catch (err) {
      // Error handling is done in the mutation's onError callback
      console.error('🗂️ Areas: Archive operation failed:', err);
    }
  };

  const handleDelete = async (areaId) => {
    if (window.confirm('Are you sure? This will delete all projects and tasks in this area.')) {
      console.log('🗂️ Areas: Deleting area:', areaId);
      try {
        await deleteAreaMutation.mutateAsync(areaId);
        console.log('🗂️ Areas: Delete operation successful');
      } catch (err) {
        // Error handling is done in the mutation's onError callback
        console.error('🗂️ Areas: Delete operation failed:', err);
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
      pillar_id: activePillarId || '', // Reset to active pillar if present
      importance: 3
    });
  };

  const handleEdit = (area) => {
    console.log('🗂️ Areas: Starting edit for area:', area);
    setEditingArea(area);
    const editFormData = {
      name: area.name,
      description: area.description || '',
      color: area.color || '#F4B400',
      icon: area.icon || '🎯', // Use emoji icon
      pillar_id: area.pillar_id || '',
      importance: area.importance || 3
    };
    console.log('🗂️ Areas: Setting edit form data:', editFormData);
    setFormData(editFormData);
    setShowModal(true);
  };

  if (loading) {
    console.log('🗂️ Areas: Rendering loading state');
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

  console.log('🗂️ Areas: Rendering main component, areas length:', areas.length, 'error:', error);

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
                Life Areas
              </h1>
              {activePillarName && (
                <>
                  <span className="text-2xl text-gray-500">›</span>
                  <div className="flex items-center space-x-2">
                    <Mountain className="h-5 w-5 text-blue-400" />
                    <span className="text-xl font-medium text-blue-400">{activePillarName}</span>
                  </div>
                </>
              )}
            </div>
            <p className="text-gray-400 mt-1">
              {activePillarName 
                ? `Areas within the ${activePillarName} pillar`
                : 'Organize your life into meaningful domains'
              }
            </p>
            {activePillarName && (
              <button
                onClick={() => onSectionChange('pillars')}
                className="mt-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                ← Back to all pillars
              </button>
            )}
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
              data-testid="area-new"
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
        {isError && (
          <div className="bg-red-900/20 border border-red-600 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
                <span className="text-red-400">{error?.message || 'Failed to load areas'}</span>
              </div>
              <button
                onClick={() => refetchAreas()}
                className="px-3 py-1 rounded bg-red-500 hover:bg-red-600 text-white text-sm transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Areas Grid */}
        {areas.length === 0 ? (
          <div className="text-center py-12">
            <Layers className="mx-auto h-16 w-16 text-gray-600 mb-4" />
            <h3 className="text-xl font-medium text-gray-400 mb-2">
              {activePillarName ? `No areas in ${activePillarName} pillar yet` : 'No areas yet'}
            </h3>
            <p className="text-gray-500 mb-6">
              {activePillarName 
                ? `Create your first area for the ${activePillarName} pillar`
                : 'Create your first life area to get started'
              }
            </p>
            <button
              onClick={() => setShowModal(true)}
              className="px-6 py-3 rounded-lg font-medium"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              {activePillarName ? `Create Area for ${activePillarName}` : 'Create First Area'}
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {areas.map((area) => (
              <AreaCard 
                key={area.id}
                area={area}
                onSectionChange={onSectionChange}
                onArchive={handleArchive}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
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

              <form onSubmit={handleSubmit} className="space-y-4" data-testid="area-form">
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
                    data-testid="area-submit"
                    type="submit"
                    disabled={!formData.name.trim() || updateAreaMutation.isPending || createAreaMutation.isPending}
                    className={`relative z-50 flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                      (!formData.name.trim() || updateAreaMutation.isPending || createAreaMutation.isPending)
                        ? 'bg-gray-600 cursor-not-allowed opacity-50' 
                        : 'hover:opacity-90'
                    }`}
                    style={{ 
                      backgroundColor: (!formData.name.trim() || updateAreaMutation.isPending || createAreaMutation.isPending) ? '#6B7280' : '#F4B400', 
                      color: '#0B0D14',
                      zIndex: 60
                    }}
                  >
                    <Save className="h-4 w-4" />
                    <span>
                      {updateAreaMutation.isPending || createAreaMutation.isPending 
                        ? 'Saving...' 
                        : editingArea ? 'Update' : 'Create'}
                    </span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

Areas.displayName = 'Areas';

export default Areas;