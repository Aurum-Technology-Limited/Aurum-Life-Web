import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { X, Plus } from 'lucide-react';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { Pillar, Area, Project, Task, ProjectAttachment } from '../../types/enhanced-features';
import ColorPicker from './ColorPicker';
import IconPicker from './IconPicker';
import FileUpload, { UploadedFile, FileUploadConfig } from './FileUpload';
import LimitedInput from '../forms/LimitedInput';
import LimitedTextarea from '../forms/LimitedTextarea';

interface CreateEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: 'create' | 'edit';
  type: 'pillar' | 'area' | 'project' | 'task';
  item?: Pillar | Area | Project | Task;
  parentId?: string; // For creating child items
  onSuccess?: () => void;
}

const priorityOptions = [
  { value: 'low', label: 'Low', color: '#6B7280' },
  { value: 'medium', label: 'Medium', color: '#F59E0B' },
  { value: 'high', label: 'High', color: '#EF4444' },
  { value: 'urgent', label: 'Urgent', color: '#DC2626' },
];

const statusOptions = {
  project: [
    { value: 'planning', label: 'Planning' },
    { value: 'active', label: 'Active' },
    { value: 'paused', label: 'Paused' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
  ],
  task: [
    { value: 'todo', label: 'To Do' },
    { value: 'in-progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
  ],
};

const pillarColors = [
  '#10B981', '#3B82F6', '#EC4899', '#F59E0B', 
  '#8B5CF6', '#06B6D4', '#EF4444', '#84CC16'
];

const projectFileConfig: FileUploadConfig = {
  maxFileSize: 50, // 50MB limit for projects
  maxFiles: 10,    // Maximum 10 files per project
  allowedTypes: [
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
    'application/pdf',
    'text/plain', 'text/csv',
    'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/zip', 'application/x-zip-compressed',
    'application/json', 'text/markdown'
  ],
  allowedExtensions: [
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
    '.pdf',
    '.txt', '.csv', '.md',
    '.doc', '.docx',
    '.xls', '.xlsx',
    '.ppt', '.pptx',
    '.zip', '.json'
  ]
};

export default function CreateEditModal({
  isOpen,
  onClose,
  mode,
  type,
  item,
  parentId,
  onSuccess,
}: CreateEditModalProps) {
  const { 
    addPillar, 
    addArea, 
    addProject, 
    addTask,
    updatePillar,
    updateArea,
    updateProject,
    updateTask,
    addProjectAttachment,
    removeProjectAttachment,
    getProjectAttachments,
    pillars,
    getAllAreas,
    getAllProjects,
  } = useEnhancedFeaturesStore();

  const [formData, setFormData] = useState<any>({});
  const [tags, setTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [projectFiles, setProjectFiles] = useState<UploadedFile[]>([]);

  useEffect(() => {
    if (isOpen) {
      if (mode === 'edit' && item) {
        setFormData({
          name: item.name,
          description: item.description || '',
          ...('color' in item && { color: item.color }),
          ...('icon' in item && { icon: item.icon }),
          ...('priority' in item && { priority: item.priority }),
          ...('status' in item && { status: item.status }),
          ...('estimatedHours' in item && { estimatedHours: item.estimatedHours || '' }),
          ...('healthScore' in item && { healthScore: item.healthScore }),
          ...('weeklyTimeTarget' in item && { weeklyTimeTarget: item.weeklyTimeTarget }),
          ...('impactScore' in item && { impactScore: item.impactScore }),
        });
        if ('tags' in item) {
          setTags(item.tags || []);
        }
        
        // Load existing project files if editing a project
        if (type === 'project' && 'attachments' in item) {
          const existingFiles: UploadedFile[] = (item as Project).attachments.map(attachment => ({
            id: attachment.id,
            file: new File([], attachment.fileName, { type: attachment.fileType }),
            name: attachment.originalName,
            size: attachment.fileSize,
            type: attachment.fileType,
            uploadProgress: 100,
            uploaded: true
          }));
          setProjectFiles(existingFiles);
        }
      } else {
        // Default values for create mode
        setProjectFiles([]);
        setFormData({
          name: '',
          description: '',
          ...(type === 'pillar' && { 
            color: pillarColors[0],
            icon: 'Target',
            healthScore: 75,
            weeklyTimeTarget: 10 
          }),
          ...(type === 'area' && { 
            color: '#3B82F6',
            icon: 'Target',
            healthScore: 75 
          }),
          ...(type === 'project' && { 
            color: '#10B981',
            icon: 'FolderKanban',
            priority: 'medium', 
            status: 'active',
            impactScore: 5 
          }),
          ...(type === 'task' && { 
            color: '#F59E0B',
            icon: 'CheckSquare',
            priority: 'medium', 
            status: 'todo',
            estimatedHours: '' 
          }),
        });
        setTags([]);
      }
      setNewTag('');
    }
  }, [isOpen, mode, item, type]);

  // File handling functions
  const handleFilesUploaded = (files: UploadedFile[]) => {
    setProjectFiles(files);
  };

  const handleFileRemoved = (fileId: string) => {
    setProjectFiles(files => files.filter(f => f.id !== fileId));
    
    // If editing and the file was already attached to the project, remove it from the store
    if (mode === 'edit' && item && type === 'project') {
      removeProjectAttachment(item.id, fileId);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (mode === 'create') {
        const baseData = {
          name: formData.name,
          description: formData.description,
        };

        switch (type) {
          case 'pillar':
            addPillar({
              ...baseData,
              color: formData.color,
              icon: formData.icon,
              healthScore: formData.healthScore,
              weeklyTimeTarget: formData.weeklyTimeTarget,
              weeklyTimeActual: 0,
              streak: 0,
              areas: [],
            });
            break;

          case 'area':
            if (!parentId) throw new Error('Parent pillar ID required');
            addArea(parentId, {
              ...baseData,
              color: formData.color,
              icon: formData.icon,
              healthScore: formData.healthScore,
              projects: [],
            });
            break;

          case 'project':
            if (!parentId) throw new Error('Parent area ID required');
            // Create project first
            const newProject = {
              ...baseData,
              color: formData.color,
              icon: formData.icon,
              status: formData.status,
              priority: formData.priority,
              impactScore: formData.impactScore,
              tasks: []
            };
            addProject(parentId, newProject);
            
            // Add file attachments after project creation
            // We'll need to get the project ID from the store after creation
            if (projectFiles.length > 0) {
              setTimeout(() => {
                // Get the most recently created project
                const allProjects = getAllProjects();
                const latestProject = allProjects[allProjects.length - 1];
                if (latestProject) {
                  projectFiles.forEach(file => {
                    if (file.uploaded) {
                      addProjectAttachment(latestProject.id, {
                        fileName: file.name,
                        originalName: file.name,
                        fileSize: file.size,
                        fileType: file.type,
                        uploadedBy: 'current-user' // TODO: Get from auth
                      });
                    }
                  });
                }
              }, 100);
            }
            break;

          case 'task':
            if (!parentId) throw new Error('Parent project ID required');
            addTask(parentId, {
              ...baseData,
              color: formData.color,
              icon: formData.icon,
              status: formData.status,
              priority: formData.priority,
              estimatedHours: formData.estimatedHours ? parseFloat(formData.estimatedHours) : undefined,
              tags,
            });
            break;
        }
      } else {
        // Edit mode
        if (!item) throw new Error('Item required for edit mode');
        
        switch (type) {
          case 'pillar':
            updatePillar(item.id, {
              name: formData.name,
              description: formData.description,
              color: formData.color,
              icon: formData.icon,
              healthScore: formData.healthScore,
              weeklyTimeTarget: formData.weeklyTimeTarget,
            });
            break;

          case 'area':
            updateArea(item.id, {
              name: formData.name,
              description: formData.description,
              color: formData.color,
              icon: formData.icon,
              healthScore: formData.healthScore,
            });
            break;

          case 'project':
            updateProject(item.id, {
              name: formData.name,
              description: formData.description,
              color: formData.color,
              icon: formData.icon,
              status: formData.status,
              priority: formData.priority,
              impactScore: formData.impactScore,
            });
            
            // Handle new file attachments
            projectFiles.forEach(file => {
              if (file.uploaded && !getProjectAttachments(item.id).some(att => att.id === file.id)) {
                addProjectAttachment(item.id, {
                  fileName: file.name,
                  originalName: file.name,
                  fileSize: file.size,
                  fileType: file.type,
                  uploadedBy: 'current-user' // TODO: Get from auth
                });
              }
            });
            break;

          case 'task':
            updateTask(item.id, {
              name: formData.name,
              description: formData.description,
              color: formData.color,
              icon: formData.icon,
              status: formData.status,
              priority: formData.priority,
              estimatedHours: formData.estimatedHours ? parseFloat(formData.estimatedHours) : undefined,
              tags,
            });
            break;
        }
      }

      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Error saving item:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const addTag = () => {
    const trimmedTag = newTag.trim();
    if (trimmedTag && !tags.includes(trimmedTag) && trimmedTag.length <= 20 && tags.length < 10) {
      setTags([...tags, trimmedTag]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const getNameLimit = () => {
    switch (type) {
      case 'pillar':
        return 50;  // Pillars should have concise, memorable names
      case 'area':
        return 40;  // Areas should be clearly defined
      case 'project':
        return 60;  // Projects can have slightly longer descriptive names
      case 'task':
        return 80;  // Tasks can have longer action-oriented names
      default:
        return 50;
    }
  };

  const getDescriptionLimit = () => {
    switch (type) {
      case 'pillar':
        return 200; // Strategic pillars need comprehensive descriptions
      case 'area':
        return 150; // Areas need clear focus descriptions
      case 'project':
        return 120; // Projects need concise goal descriptions
      case 'task':
        return 80;  // Tasks need brief action descriptions
      default:
        return 100;
    }
  };

  const getModalTitle = () => {
    const action = mode === 'create' ? 'Create' : 'Edit';
    const typeLabel = type.charAt(0).toUpperCase() + type.slice(1);
    return `${action} ${typeLabel}`;
  };

  const getParentOptions = () => {
    switch (type) {
      case 'area':
        return pillars.map(pillar => ({ value: pillar.id, label: pillar.name }));
      case 'project':
        return getAllAreas().map(area => ({ value: area.id, label: area.name }));
      case 'task':
        return getAllProjects().map(project => ({ value: project.id, label: project.name }));
      default:
        return [];
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white max-w-4xl max-h-[95vh] overflow-y-auto p-8">
        <DialogHeader>
          <DialogTitle>{getModalTitle()}</DialogTitle>
          <DialogDescription>
            {mode === 'create' 
              ? `Create a new ${type} in your hierarchy`
              : `Edit the details of this ${type}`
            }
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Name */}
          <div>
            <LimitedInput
              label="Name"
              value={formData.name || ''}
              onValueChange={(value) => setFormData(prev => ({ ...prev, name: value }))}
              placeholder={`Enter ${type} name`}
              maxLength={getNameLimit()}
              showProgress={true}
              showIcon={true}
              helperText={`Choose a clear, descriptive name for this ${type}`}
              required
            />
          </div>

          {/* Description */}
          <div>
            <LimitedTextarea
              label="Description"
              value={formData.description || ''}
              onValueChange={(value) => setFormData(prev => ({ ...prev, description: value }))}
              placeholder={`Describe this ${type}`}
              maxLength={getDescriptionLimit()}
              rows={3}
              showProgress={true}
              showIcon={true}
              helperText={`Provide context and purpose for this ${type}`}
            />
          </div>

          {/* Parent Selection (for create mode) */}
          {mode === 'create' && type !== 'pillar' && (
            <div className="space-y-2">
              <Label htmlFor="parent">Parent {type === 'area' ? 'Pillar' : type === 'project' ? 'Area' : 'Project'}</Label>
              <Select
                value={parentId || ''}
                onValueChange={(value) => {
                  // This would need to be handled by the parent component
                  // For now, we'll rely on parentId being passed correctly
                }}
              >
                <SelectTrigger className="glassmorphism-panel border-0">
                  <SelectValue placeholder={`Select parent ${type === 'area' ? 'pillar' : type === 'project' ? 'area' : 'project'}`} />
                </SelectTrigger>
                <SelectContent className="glassmorphism-card border-0">
                  {getParentOptions().map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Pillar-specific fields */}
          {type === 'pillar' && (
            <>
              <div className="grid grid-cols-1 gap-8">
                <ColorPicker
                  value={formData.color || pillarColors[0]}
                  onChange={(color) => setFormData(prev => ({ ...prev, color }))}
                  label="Pillar Color"
                  id="pillar-color"
                />
                <IconPicker
                  value={formData.icon || 'Target'}
                  onChange={(icon) => setFormData(prev => ({ ...prev, icon }))}
                  label="Pillar Icon"
                  id="pillar-icon"
                />
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-3">
                  <Label htmlFor="healthScore">Health Score (%)</Label>
                  <Input
                    id="healthScore"
                    type="number"
                    min="0"
                    max="100"
                    value={formData.healthScore || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, healthScore: parseInt(e.target.value) || 0 }))}
                    className="glassmorphism-panel border-0"
                  />
                </div>
                <div className="space-y-3">
                  <Label htmlFor="weeklyTimeTarget">Weekly Time Target (hours)</Label>
                  <Input
                    id="weeklyTimeTarget"
                    type="number"
                    min="0"
                    value={formData.weeklyTimeTarget || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, weeklyTimeTarget: parseInt(e.target.value) || 0 }))}
                    className="glassmorphism-panel border-0"
                  />
                </div>
              </div>
            </>
          )}

          {/* Area-specific fields */}
          {type === 'area' && (
            <>
              <div className="grid grid-cols-1 gap-8">
                <ColorPicker
                  value={formData.color || '#3B82F6'}
                  onChange={(color) => setFormData(prev => ({ ...prev, color }))}
                  label="Area Color"
                  id="area-color"
                />
                <IconPicker
                  value={formData.icon || 'Target'}
                  onChange={(icon) => setFormData(prev => ({ ...prev, icon }))}
                  label="Area Icon"
                  id="area-icon"
                />
              </div>
              <div className="space-y-3">
                <Label htmlFor="healthScore">Health Score (%)</Label>
                <Input
                  id="healthScore"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.healthScore || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, healthScore: parseInt(e.target.value) || 0 }))}
                  className="glassmorphism-panel border-0"
                />
              </div>
            </>
          )}

          {/* Project-specific fields */}
          {type === 'project' && (
            <>
              <div className="grid grid-cols-1 gap-8">
                <ColorPicker
                  value={formData.color || '#10B981'}
                  onChange={(color) => setFormData(prev => ({ ...prev, color }))}
                  label="Project Color"
                  id="project-color"
                />
                <IconPicker
                  value={formData.icon || 'FolderKanban'}
                  onChange={(icon) => setFormData(prev => ({ ...prev, icon }))}
                  label="Project Icon"
                  id="project-icon"
                />
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-3">
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={formData.status || ''}
                    onValueChange={(value) => setFormData(prev => ({ ...prev, status: value }))}
                  >
                    <SelectTrigger className="glassmorphism-panel border-0">
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent className="glassmorphism-card border-0">
                      {statusOptions.project.map(option => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-3">
                  <Label htmlFor="priority">Priority</Label>
                  <Select
                    value={formData.priority || ''}
                    onValueChange={(value) => setFormData(prev => ({ ...prev, priority: value }))}
                  >
                    <SelectTrigger className="glassmorphism-panel border-0">
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent className="glassmorphism-card border-0">
                      {priorityOptions.map(option => (
                        <SelectItem key={option.value} value={option.value}>
                          <span style={{ color: option.color }}>{option.label}</span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-3">
                <Label htmlFor="impactScore">Impact Score (1-10)</Label>
                <Input
                  id="impactScore"
                  type="number"
                  min="1"
                  max="10"
                  value={formData.impactScore || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, impactScore: parseInt(e.target.value) || 5 }))}
                  className="glassmorphism-panel border-0"
                />
              </div>
              
              {/* File Attachments */}
              <div className="space-y-3">
                <Label>Project Files</Label>
                <FileUpload
                  config={projectFileConfig}
                  onFilesUploaded={handleFilesUploaded}
                  onFileRemoved={handleFileRemoved}
                  existingFiles={projectFiles}
                  disabled={isSubmitting}
                  className="glassmorphism-panel border-0"
                />
              </div>
            </>
          )}

          {/* Task-specific fields */}
          {type === 'task' && (
            <>
              <div className="grid grid-cols-1 gap-8">
                <ColorPicker
                  value={formData.color || '#F59E0B'}
                  onChange={(color) => setFormData(prev => ({ ...prev, color }))}
                  label="Task Color"
                  id="task-color"
                />
                <IconPicker
                  value={formData.icon || 'CheckSquare'}
                  onChange={(icon) => setFormData(prev => ({ ...prev, icon }))}
                  label="Task Icon"
                  id="task-icon"
                />
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-3">
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={formData.status || ''}
                    onValueChange={(value) => setFormData(prev => ({ ...prev, status: value }))}
                  >
                    <SelectTrigger className="glassmorphism-panel border-0">
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent className="glassmorphism-card border-0">
                      {statusOptions.task.map(option => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-3">
                  <Label htmlFor="priority">Priority</Label>
                  <Select
                    value={formData.priority || ''}
                    onValueChange={(value) => setFormData(prev => ({ ...prev, priority: value }))}
                  >
                    <SelectTrigger className="glassmorphism-panel border-0">
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent className="glassmorphism-card border-0">
                      {priorityOptions.map(option => (
                        <SelectItem key={option.value} value={option.value}>
                          <span style={{ color: option.color }}>{option.label}</span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-3">
                <Label htmlFor="estimatedHours">Estimated Hours</Label>
                <Input
                  id="estimatedHours"
                  type="number"
                  min="0"
                  step="0.25"
                  value={formData.estimatedHours || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, estimatedHours: e.target.value }))}
                  placeholder="e.g. 2.5"
                  className="glassmorphism-panel border-0"
                />
              </div>

              {/* Tags */}
              <div className="space-y-3">
                <Label htmlFor="tags">
                  Tags 
                  <span className="text-xs text-muted-foreground ml-2">
                    ({tags.length}/10 tags)
                  </span>
                </Label>
                <div className="space-y-3">
                  <div className="flex space-x-3">
                    <LimitedInput
                      value={newTag}
                      onValueChange={setNewTag}
                      placeholder="Add a tag"
                      maxLength={20}
                      showProgress={false}
                      showIcon={false}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                      disabled={tags.length >= 10}
                      className="flex-1"
                    />
                    <Button 
                      type="button" 
                      onClick={addTag} 
                      size="sm" 
                      variant="outline"
                      disabled={!newTag.trim() || tags.length >= 10 || newTag.length > 20}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  {tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {tags.map(tag => (
                        <Badge key={tag} variant="secondary" className="pr-1">
                          {tag}
                          <button
                            type="button"
                            onClick={() => removeTag(tag)}
                            className="ml-1 hover:bg-destructive hover:text-destructive-foreground rounded-full"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-[rgba(244,208,63,0.1)]">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              disabled={isSubmitting || !formData.name}
            >
              {isSubmitting ? 'Saving...' : mode === 'create' ? 'Create' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}