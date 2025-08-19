import React, { useState, useEffect, memo, useMemo } from 'react';
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
          data-testid={`area-delete-${area.id}`}
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
  const [search, setSearch] = useState('');
  
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

  const displayedAreas = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return areas;
    return areas.filter(a => {
      const fields = [a.name, a.description, a.pillar_name].map(v => (v || '').toLowerCase());
      return fields.some(f => f.includes(q));
    });
  }, [areas, search]);
  
  // Get basic pillars data for filtering (separate from main pillars page)
  const { 
    data: pillars = [], 
    isLoading: pillarsLoading,
    refetch: refetchPillarsBasic
  } = useQuery({
    queryKey: ['pillars', 'basic'], // Different query key to avoid cache conflicts
    queryFn: async () => {
      const response = await pillarsAPI.getPillars(false, false, false); // Basic pillars without counts
      return response.data; // Ensure we return an array of pillars, not the axios response object
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });

  // Ensure Pillar dropdown is always fresh when opening Area modal
  useEffect(() => {
    if (showModal) {
      // Invalidate any cached pillars queries and refetch the lightweight list used by the dropdown
      try {
        queryClient.invalidateQueries({ predicate: (q) => Array.isArray(q.queryKey) && q.queryKey[0] === 'pillars' });
      } catch {}
      // Kick a microtask + RAF to refetch to avoid race with modal mount
      Promise.resolve().then(() => {
        requestAnimationFrame(() => {
          try { refetchPillarsBasic && refetchPillarsBasic(); } catch {}
        });
      });
    }
  }, [showModal, queryClient, refetchPillarsBasic]);
  
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

      // Set a short-lived consistency window to bypass ultra cache in getAreas
      try { localStorage.setItem('AREAS_FORCE_STANDARD_UNTIL', String(Date.now() + 2500)); } catch {}

      // Force-fetch from standard endpoint (bypass ultra) and hydrate cache to avoid transient stale ultra cache
      (async () => {
        try {
          const standardResp = await api.get('/areas', { params: { include_projects: true, include_archived: showArchived } });
          const list = Array.isArray(standardResp.data) ? standardResp.data : (standardResp.data?.data || []);
          queryClient.setQueryData(['areas', true, showArchived], list);
          queryClient.setQueryData(['areas', false, showArchived], list);
        } catch (e) {
          console.warn('Areas standard fetch hydration failed, falling back to refetch:', e?.message || e);
        }
      })();

      // Safety refetch after a short delay to avoid any race with ultra-cache
      setTimeout(() => {
        try { refetchAreas && refetchAreas(); } catch (e) {}
      }, 200);
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
    mutationFn: async (areaId) => {
      try {
        await areasAPI.deleteArea(areaId);
        return { areaId };
      } catch (err) {
        // Treat 404 as idempotent success
        if (err?.response?.status === 404) {
          return { areaId, already: true };
        }
        throw err;
      }
    },
    onSuccess: async (_resp, areaId) => {
      console.log('🗂️ Areas: Delete mutation successful:', _resp);
      // Optimistically remove from both caches
      queryClient.setQueryData(['areas', true, showArchived], (prev) => Array.isArray(prev) ? prev.filter(a => a.id !== areaId) : prev);
      queryClient.setQueryData(['areas', false, showArchived], (prev) => Array.isArray(prev) ? prev.filter(a => a.id !== areaId) : prev);
      // Invalidate related caches
      await queryClient.invalidateQueries({ predicate: (q) => Array.isArray(q.queryKey) && ['areas','projects','tasks'].includes(q.queryKey[0]) });
      onDataMutation('area', 'delete', { areaId });
      // Consistency window to bypass ultra
      try { localStorage.setItem('AREAS_FORCE_STANDARD_UNTIL', String(Date.now() + 2500)); } catch {}
      // Hydrate from standard endpoint
      try {
        const backendURL = process.env.REACT_APP_BACKEND_URL || '';
        const params = new URLSearchParams();
        params.append('include_projects', 'true');
        params.append('include_archived', String(!!showArchived));
        params.append('_ts', String(Date.now()));
        const resp = await fetch(`${backendURL}/api/areas?${params.toString()}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}` }
        });
        if (resp.ok) {
          const list = await resp.json();
          queryClient.setQueryData(['areas', true, showArchived], list);
          queryClient.setQueryData(['areas', false, showArchived], list);
        }
      } catch (e) {
        console.warn('Areas standard fetch hydration after delete failed:', e?.message || e);
      }
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
    if (window.confirm('Are you sure? This will permanently delete all Projects and Tasks in this Area. This action cannot be undone.')) {
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

  const handleEdit = (area) => {
    setEditingArea(area);
    setFormData({
      name: area.name,
      description: area.description,
      color: area.color,
      icon: area.icon,
      pillar_id: area.pillar_id,
      importance: area.importance || 3
    });
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingArea(null);
    setFormData({
      name: '',
      description: '',
      color: '#F4B400',
      icon: '🎯',
      pillar_id: activePillarId || '',
      importance: 3
    });
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
          <h1 className="text-2xl font-bold text-white">Areas</h1>
          <p className="text-gray-400 mt-1">
            {activePillarName ? `Areas in ${activePillarName}` : 'Organize your life into focused areas'}
          </p>
          {activePillarName && (
            <button
              onClick={() => onSectionChange('pillars')}
              className="mt-2 text-sm text-yellow-400 hover:text-yellow-300 transition-colors"
            >
              ← Back to all pillars
            </button>
          )}
        </div>
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search areas..."
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => setShowArchived(!showArchived)}
            className={`px-3 py-2 rounded-lg transition-colors ${
              showArchived 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
            title={showArchived ? 'Hide archived areas' : 'Show archived areas'}
          >
            {showArchived ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
          <button
            data-testid="area-new"
            onClick={() => setShowModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>New Area</span>
          </button>
        </div>
      </div>

      {/* Error Display */}
      {isError && (
        <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-red-400" />
          <span className="text-red-400">{error?.message || 'Failed to load areas'}</span>
        </div>
      )}

      {/* Areas Grid */}
      <div className="space-y-4">
        {displayedAreas.length === 0 ? (
          <div className="text-center py-12 bg-gray-900 border border-gray-800 rounded-lg">
            <Layers className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No areas {search ? 'match your search' : 'yet'}</h3>
            <p className="text-gray-400 mb-4">
              {search ? 'Try a different search term' : 'Create your first area to organize your projects'}
            </p>
            {!search && (
              <button
                onClick={() => setShowModal(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create First Area
              </button>
            )}
          </div>
        ) : (
          displayedAreas.map(area => (
            <AreaCard
              key={area.id}
              area={area}
              onSectionChange={onSectionChange}
              onArchive={handleArchive}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto border border-gray-800">
            <div className="p-6">
              <h2 className="text-xl font-bold text-white mb-4">
                {editingArea ? 'Edit Area' : 'Create New Area'}
              </h2>
              
              <form onSubmit={handleSubmit} className="space-y-4" data-testid="area-form">
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
                    Pillar *
                  </label>
                  <select
                    value={formData.pillar_id}
                    onChange={(e) => setFormData({...formData, pillar_id: e.target.value})}
                    className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select a pillar</option>
                    {pillars.map(pillar => (
                      <option key={pillar.id} value={pillar.id}>
                        {pillar.icon} {pillar.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Icon Picker */}
                <IconPicker
                  value={formData.icon}
                  onChange={(icon) => setFormData({...formData, icon})}
                  label="Icon"
                  placeholder="🎯"
                  required={false}
                  iconSet="areas"
                  allowCustom={true}
                />

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Color
                  </label>
                  <div className="grid grid-cols-5 gap-2">
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
                    Importance Level
                  </label>
                  <select
                    value={formData.importance}
                    onChange={(e) => setFormData({...formData, importance: parseInt(e.target.value)})}
                    className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value={1}>1 - Very Low</option>
                    <option value={2}>2 - Low</option>
                    <option value={3}>3 - Medium</option>
                    <option value={4}>4 - High</option>
                    <option value={5}>5 - Critical</option>
                  </select>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
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
                    disabled={!formData.name.trim() || !formData.pillar_id || updateAreaMutation.isPending || createAreaMutation.isPending}
                    className={`relative z-50 flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors pointer-events-auto ${
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