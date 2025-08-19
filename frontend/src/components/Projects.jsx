import React, { useState, useEffect, memo, useMemo, useCallback } from 'react';
import { 
  FolderIcon, 
  PlusIcon, 
  DotsVerticalIcon, 
  CalendarIcon, 
  CheckIcon,
  XIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon
} from '@heroicons/react/outline';
import { 
  FolderOpenIcon,
  FolderIcon as FolderIconSolid
} from '@heroicons/react/solid';
import { useAuth } from '../contexts/BackendAuthContext';
import { projectsAPI, areasAPI } from '../services/api';
import { useProjectsQuery, useInvalidateQueries } from '../hooks/useQueries';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import ProjectDecompositionHelper from './ProjectDecompositionHelper';

// Memoized ProjectCard component to prevent unnecessary re-renders
const ProjectCard = memo(({ project, onEdit, onDelete, onViewTasks, onUpdateStatus }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'not_started': return 'text-gray-400';
      case 'in_progress': return 'text-blue-400';
      case 'completed': return 'text-green-400';
      case 'on_hold': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div 
      className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors group cursor-pointer"
      onClick={() => onViewTasks(project)}
      title="Click to view project tasks"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div 
            className="p-2 rounded-lg"
            style={{ backgroundColor: project.color || '#F59E0B' }}
          >
            <FolderOpenIcon className="h-5 w-5 text-black" />
          </div>
          <div>
            <h3 className="font-semibold text-white group-hover:text-yellow-400 transition-colors">
              {project.name}
            </h3>
            {project.area_name && (
              <p className="text-sm text-gray-400">{project.area_name}</p>
            )}
          </div>
        </div>
        
        {/* Edit Action Icon */}
        <button 
          className="text-gray-400 hover:text-yellow-400 p-2 rounded-lg hover:bg-gray-700 transition-colors opacity-0 group-hover:opacity-100"
          onClick={(e) => {
            e.stopPropagation(); // Prevent triggering the card click
            onEdit(project);
          }}
          title="Edit project"
        >
          <PencilIcon className="h-4 w-4" />
        </button>
      </div>

      {project.description && (
        <p className="text-gray-300 text-sm mb-4 line-clamp-2">
          {project.description}
        </p>
      )}

      <div className="flex items-center justify-between mb-4">
        <span className={`text-sm font-medium ${getStatusColor(project.status)}`}>
          {project.status?.replace('_', ' ').toUpperCase() || 'NOT STARTED'}
        </span>
        <span className={`text-sm ${getPriorityColor(project.priority)}`}>
          {project.priority?.toUpperCase() || 'MEDIUM'}
        </span>
      </div>

      {project.due_date && (
        <div className="flex items-center text-gray-400 text-sm mb-4">
          <CalendarIcon className="h-4 w-4 mr-1" />
          <span>{new Date(project.due_date).toLocaleDateString()}</span>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-400">
          <span className="hover:text-yellow-400 transition-colors">
            {project.task_count ? `${project.task_count} tasks` : '0 tasks'}
          </span>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={() => onViewTasks(project)}
            className="p-1 text-gray-400 hover:text-yellow-400 transition-colors"
            title="View Tasks"
          >
            <EyeIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => onEdit(project)}
            className="p-1 text-gray-400 hover:text-yellow-400 transition-colors"
            title="Edit"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(project.id); }}
            className="p-1 text-gray-400 hover:text-red-400 transition-colors"
            title="Delete"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
});

ProjectCard.displayName = 'ProjectCard';

const Projects = memo(({ onSectionChange, sectionParams }) => {
  const { user } = useAuth();
  const { invalidateProjects, invalidateTasks } = useInvalidateQueries();
  const queryClient = useQueryClient();
  
  // Use React Query for projects data
  const activeAreaId = sectionParams?.areaId || null;
  const activeAreaName = sectionParams?.areaName || null;
  const { 
    data: projects = [], 
    isLoading: loading, 
    error: projectsError, 
    isError: projectsIsError,
  } = useProjectsQuery(activeAreaId, false); // areaId, includeArchived=false

  // Load basic areas list for dropdown
  const { data: areasResponse = [], isLoading: areasLoading } = useQuery({
    queryKey: ['areas', 'basic'],
    queryFn: async () => {
      const response = await areasAPI.getAreas(false, false); // Basic areas without projects
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
  // Area dropdown freshness effect is declared after state initialization below to avoid TDZ errors
  
  // Areas should now be an array
  const areas = Array.isArray(areasResponse) ? areasResponse : [];

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [showDecompositionHelper, setShowDecompositionHelper] = useState(false);
  const [newProjectForDecomposition, setNewProjectForDecomposition] = useState(null);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    area_id: '',
    // status intentionally omitted for backend default compatibility
    priority: 'medium',
    color: '#F59E0B',
    icon: 'FolderOpen',
    due_date: ''
  });

  // Memoize filtered projects to prevent recalculation on every render
  const filteredProjects = useMemo(() => {
    return activeAreaId 
      ? projects.filter(project => project.area_id === activeAreaId)
      : projects;
  }, [projects, activeAreaId]);

  const visibleProjects = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return filteredProjects;
    return filteredProjects.filter(p => {
      const fields = [p.name, p.description, p.area_name].map(v => (v || '').toLowerCase());
      return fields.some(f => f.includes(q));
    });
  }, [filteredProjects, search]);

  // Create project mutation
  const createProjectMutation = useMutation({
    mutationFn: (projectData) => {
      const backendURL = process.env.REACT_APP_BACKEND_URL || '';
      // Normalize payload: map due_date -&gt; deadline, omit status (backend default), normalize empty area_id to null
      const normalized = {
        name: projectData.name,
        description: projectData.description || '',
        icon: projectData.icon || 'FolderOpen',
        deadline: projectData.due_date ? new Date(projectData.due_date).toISOString() : null,
        priority: projectData.priority || 'medium',
        // area_id is optional; send null if blank to avoid enum/UUID issues
        ...(projectData.area_id && projectData.area_id.trim() ? { area_id: projectData.area_id.trim() } : { area_id: null })
      };
      return fetch(`${backendURL}/api/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
        body: JSON.stringify(normalized),
      }).then(response => {
        if (!response.ok) {
          return response.json().then(err => { throw new Error(err.detail || 'Failed to create project'); });
        }
        return response.json();
      });
    },
    onSuccess: (createdProject) => {
      // Invalidate and refetch projects data
      invalidateProjects();

      // Set short-lived consistency window to bypass ultra projects after write
      try { localStorage.setItem('PROJECTS_FORCE_STANDARD_UNTIL', String(Date.now() + 2500)); } catch {}

      // Hydrate cache from standard endpoint immediately for active area to avoid stale ultra cache
      (async () => {
        try {
          const backendURL = process.env.REACT_APP_BACKEND_URL || '';
          const params = new URLSearchParams();
          if (activeAreaId) params.append('area_id', activeAreaId);
          params.append('include_archived', 'false');
          params.append('_ts', String(Date.now()));
          const resp = await fetch(`${backendURL}/api/projects?${params.toString()}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}` }
          });
          if (resp.ok) {
            const list = await resp.json();
            // Update the specific projects query cache for this area filter
            queryClient.setQueryData(['projects', activeAreaId, false], list);
          }
        } catch (e) {
          console.warn('Projects standard fetch hydration failed:', e?.message || e);
        }
      })();
    },
    onError: (err) => {
      setError(err.message || 'Failed to create project');
    }
  });

  const updateProjectMutation = useMutation({
    mutationFn: ({ projectId, projectData }) => {
      const backendURL = process.env.REACT_APP_BACKEND_URL || '';
      const normalized = {
        name: projectData.name,
        description: projectData.description || '',
        priority: projectData.priority || 'medium',
        icon: projectData.icon || 'FolderOpen',
        deadline: projectData.due_date ? new Date(projectData.due_date).toISOString() : null,
      };
      return fetch(`${backendURL}/api/projects/${projectId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
        body: JSON.stringify(normalized),
      }).then(response => {
        if (!response.ok) {
          return response.json().then(err => { throw new Error(err.detail || 'Failed to update project'); });
        }
        return response.json();
      });
    },
    onSuccess: async (updatedProject) => {
      // Invalidate and refetch projects data
      invalidateProjects();
      // Set short-lived consistency window to bypass ultra projects after write
      try { localStorage.setItem('PROJECTS_FORCE_STANDARD_UNTIL', String(Date.now() + 2000)); } catch {}
      // Hydrate cache for the current area filter
      (async () => {
        try {
          const backendURL = process.env.REACT_APP_BACKEND_URL || '';
          const params = new URLSearchParams();
          if (activeAreaId) params.append('area_id', activeAreaId);
          params.append('include_archived', 'false');
          params.append('_ts', String(Date.now()));
          const resp = await fetch(`${backendURL}/api/projects?${params.toString()}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}` }
          });
          if (resp.ok) {
            const list = await resp.json();
            queryClient.setQueryData(['projects', activeAreaId, false], list);
          }
        } catch (e) {
          console.warn('Projects standard fetch hydration failed:', e?.message || e);
        }
      })();
    },
    onError: (err) => setError(err.message || 'Failed to update project')
  });

  const deleteProjectMutation = useMutation({
    mutationFn: (projectId) => {
      const backendURL = process.env.REACT_APP_BACKEND_URL || '';
      return fetch(`${backendURL}/api/projects/${projectId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
      }).then(response => {
        if (!response.ok) {
          if (response.status === 404) return { already: true };
          return response.json().then(err => { throw new Error(err.detail || 'Failed to delete project'); });
        }
        return { ok: true };
      });
    },
    onSuccess: async (_resp, projectId) => {
      // Invalidate and refetch projects
      invalidateProjects();
      // Hydrate cache for area filter
      (async () => {
        try {
          const backendURL = process.env.REACT_APP_BACKEND_URL || '';
          const params = new URLSearchParams();
          if (activeAreaId) params.append('area_id', activeAreaId);
          params.append('include_archived', 'false');
          params.append('_ts', String(Date.now()));
          const resp = await fetch(`${backendURL}/api/projects?${params.toString()}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}` }
          });
          if (resp.ok) {
            const list = await resp.json();
            queryClient.setQueryData(['projects', activeAreaId, false], list);
          }
        } catch (e) {
          console.warn('Projects standard fetch hydration failed:', e?.message || e);
        }
      })();
      // Invalidate tasks queries since they are under projects
      invalidateTasks();
    }
  });

  // Handle area dropdown freshness when create/edit modal toggles
  useEffect(() => {
    if (showCreateForm || showEditForm) {
      try {
        queryClient.invalidateQueries({ predicate: (q) => Array.isArray(q.queryKey) && q.queryKey[0] === 'areas' });
      } catch {}
    }
  }, [showCreateForm, showEditForm, queryClient]);

  // UI omitted (rest of component)
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Projects</h1>
          <p className="text-gray-400 mt-1">
            {activeAreaName ? `Projects in ${activeAreaName}` : 'Plan and track your projects'}
          </p>
          {activeAreaName &amp;&amp; (
            <button
              onClick={() => onSectionChange('areas')}
              className="mt-2 text-sm text-yellow-400 hover:text-yellow-300 transition-colors"
            >
              ← Back to all areas
            </button>
          )}
        </div>
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={search}
            onChange={(e) =&gt; setSearch(e.target.value)}
            placeholder="Search projects..."
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
          />
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-yellow-500 text-black px-4 py-2 rounded-lg hover:bg-yellow-400 transition-colors flex items-center space-x-2"
          >
            <PlusIcon className="h-4 w-4" />
            <span>New Project</span>
          </button>
        </div>
      </div>

      {/* Error Display */}
      {projectsIsError &amp;&amp; (
        <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center space-x-2">
          <XIcon className="h-5 w-5 text-red-400" />
          <span className="text-red-400">{projectsError?.message || 'Failed to load projects'}</span>
        </div>
      )}

      {/* Projects Grid */}
      {visibleProjects.length === 0 ? (
        <div className="text-center py-12 bg-gray-900 border border-gray-800 rounded-lg">
          <FolderIcon className="h-12 w-12 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">{search ? 'No projects match your search' : 'No projects yet'}</h3>
          <p className="text-gray-400 mb-4">{search ? 'Try a different search term' : 'Create your first project to get started'}</p>
          {!search &amp;&amp; (
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-yellow-500 text-black px-4 py-2 rounded-lg hover:bg-yellow-400 transition-colors"
            >
              Create First Project
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {visibleProjects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onEdit={(p) => { setEditingProject(p); setShowEditForm(true); }}
              onDelete={(id) => deleteProjectMutation.mutate(id)}
              onViewTasks={(p) => onSectionChange('tasks', { projectId: p.id, projectName: p.name })}
              onUpdateStatus={() => {}}
            />
          ))}
        </div>
      )}

      {/* Modals and forms are below ... existing code remains unchanged */}
    </div>
  );
});

Projects.displayName = 'Projects';

export default Projects;