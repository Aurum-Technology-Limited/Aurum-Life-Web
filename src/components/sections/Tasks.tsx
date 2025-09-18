import { useState, useMemo } from 'react';
import { CheckSquare, Plus, Calendar, Flag, CheckCircle2, Clock, Tag } from 'lucide-react';
import * as LucideIcons from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Checkbox } from '../ui/checkbox';
import { useAppStore } from '../../stores/basicAppStore';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import HierarchyCard from '../shared/HierarchyCard';
import CreateEditModal from '../shared/CreateEditModal';
import DeleteConfirmModal from '../shared/DeleteConfirmModal';
import { Task } from '../../types/enhanced-features';

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'urgent': return '#EF4444';
    case 'high': return '#F59E0B';
    case 'medium': return '#3B82F6';
    case 'low': return '#6B7280';
    default: return '#6B7280';
  }
};

// Get icon for task
const getIconForTask = (task: Task) => {
  if (task.icon) {
    const CustomIcon = (LucideIcons as any)[task.icon];
    if (CustomIcon) return CustomIcon;
  }
  return CheckSquare;
};

export default function Tasks() {
  const hierarchyContext = useAppStore(state => state.hierarchyContext);
  const { 
    getAllTasks, 
    getTasksByProjectId, 
    getProjectById, 
    getAreaById, 
    getPillarById,
    updateTask,
    deleteTask,
    pillars
  } = useEnhancedFeaturesStore();

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  
  // Memoize filtered tasks to prevent unnecessary re-computations
  const filteredTasks = useMemo(() => {
    const tasks = hierarchyContext.projectId 
      ? getTasksByProjectId(hierarchyContext.projectId)
      : getAllTasks();
    
    return tasks;
  }, [hierarchyContext.projectId, getTasksByProjectId, getAllTasks]);

  // Memoize context information
  const contextInfo = useMemo(() => ({
    currentProject: hierarchyContext.projectId ? getProjectById(hierarchyContext.projectId) : null,
    currentArea: hierarchyContext.areaId ? getAreaById(hierarchyContext.areaId) : null,
    currentPillar: hierarchyContext.pillarId ? getPillarById(hierarchyContext.pillarId) : null
  }), [hierarchyContext, getProjectById, getAreaById, getPillarById]);

  const { currentProject, currentArea, currentPillar } = contextInfo;



  // Memoize task contexts to avoid repeated hierarchy traversal
  const taskContextMap = useMemo(() => {
    const contextMap = new Map();
    
    // If we have full context from navigation, use it for all tasks
    if (currentProject && currentArea && currentPillar) {
      const defaultContext = {
        project: currentProject.name,
        area: currentArea.name,
        pillar: currentPillar.name
      };
      filteredTasks.forEach(task => {
        contextMap.set(task.id, defaultContext);
      });
      return contextMap;
    }
    
    // Otherwise, build context map by searching through hierarchy once
    for (const pillar of pillars) {
      for (const area of pillar.areas) {
        for (const project of area.projects) {
          for (const task of project.tasks) {
            contextMap.set(task.id, {
              project: project.name,
              area: area.name,
              pillar: pillar.name
            });
          }
        }
      }
    }
    
    return contextMap;
  }, [currentProject, currentArea, currentPillar, filteredTasks, pillars]);

  const getTaskContext = (task: Task) => {
    return taskContextMap.get(task.id) || {
      project: currentProject?.name || 'Unknown Project',
      area: currentArea?.name || 'Unknown Area',
      pillar: currentPillar?.name || 'Unknown Pillar'
    };
  };

  // Memoize task statistics
  const taskStats = useMemo(() => {
    const completed = filteredTasks.filter(task => task.status === 'completed').length;
    const total = filteredTasks.length;
    return { completed, total };
  }, [filteredTasks]);

  const { completed: completedTasks, total: totalTasks } = taskStats;

  const handleTaskToggle = (taskId: string, completed: boolean) => {
    updateTask(taskId, { 
      status: completed ? 'completed' : 'todo',
      completedAt: completed ? new Date() : undefined
    });
  };

  const handleEdit = (task: Task) => {
    setSelectedTask(task);
    setEditModalOpen(true);
  };

  const handleDelete = (task: Task) => {
    setSelectedTask(task);
    setDeleteModalOpen(true);
  };



  const confirmDelete = () => {
    if (selectedTask) {
      deleteTask(selectedTask.id);
      setDeleteModalOpen(false);
      setSelectedTask(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            {hierarchyContext.projectName ? `${hierarchyContext.projectName} - Tasks` : 'Tasks'}
          </h1>
          <p className="text-[#B8BCC8]">
            {hierarchyContext.projectName 
              ? `Tasks within the ${hierarchyContext.projectName} project`
              : 'Individual action items driving your projects forward'
            }
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-2xl font-bold text-[#F4D03F]">{completedTasks}/{totalTasks}</div>
            <div className="text-sm text-[#B8BCC8]">Completed</div>
          </div>
          <Button 
            className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
            onClick={() => setCreateModalOpen(true)}
            disabled={!hierarchyContext.projectId}
          >
            <Plus className="w-4 h-4 mr-2" />
            New Task
          </Button>
        </div>
      </div>

      {/* Tasks List */}
      <div className="space-y-3">
        <div className="space-y-3">
          {filteredTasks.slice(0, 10).map(task => {
          const taskContext = getTaskContext(task);
          const isCompleted = task.status === 'completed';
          const Icon = getIconForTask(task);
          
          return (
            <div key={task.id} className="flex items-start space-x-3">
              {/* Checkbox */}
              <Checkbox 
                checked={isCompleted}
                onCheckedChange={(checked) => handleTaskToggle(task.id, checked as boolean)}
                className="mt-2 data-[state=checked]:bg-[#10B981] data-[state=checked]:border-[#10B981]"
              />
              
              {/* Task Card */}
              <HierarchyCard
                level="task"
                title={task.name}
                description={task.description}
                icon={<Icon className="w-4 h-4" />}
                color={task.color}
                iconBgColor={task.color}
                compact={true}
                metrics={[
                  {
                    label: 'Priority',
                    value: task.priority,
                    icon: <Flag className="w-3 h-3" />,
                    color: getPriorityColor(task.priority),
                  },
                  ...(task.estimatedHours ? [{
                    label: 'Est. Hours',
                    value: `${task.estimatedHours}h`,
                    icon: <Clock className="w-3 h-3" />,
                    color: '#B8BCC8',
                  }] : []),
                  {
                    label: 'Due Date',
                    value: task.dueDate ? new Date(task.dueDate).toLocaleDateString() : 'No date',
                    icon: <Calendar className="w-3 h-3" />,
                    color: '#B8BCC8',
                  },
                ]}
                onEdit={() => handleEdit(task)}
                onDelete={() => handleDelete(task)}
                isClickable={false}
                className={`flex-1 ${isCompleted ? 'opacity-60' : ''}`}
              >
                {/* Context breadcrumb */}
                <div className="flex items-center space-x-1.5 text-xs mb-2">
                  <Badge variant="outline" className="border-[rgba(244,208,63,0.3)] text-[#F4D03F] text-xs px-1.5 py-0.5">
                    {taskContext.pillar}
                  </Badge>
                  <span className="text-[#6B7280] text-xs">→</span>
                  <Badge variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#B8BCC8] text-xs px-1.5 py-0.5">
                    {taskContext.area}
                  </Badge>
                  <span className="text-[#6B7280] text-xs">→</span>
                  <Badge variant="outline" className="border-[rgba(244,208,63,0.1)] text-[#6B7280] text-xs px-1.5 py-0.5">
                    {taskContext.project}
                  </Badge>
                </div>

                {/* Tags */}
                {task.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {task.tags.map(tag => (
                      <Badge 
                        key={tag}
                        variant="secondary"
                        className="text-xs bg-[rgba(244,208,63,0.05)] text-[#B8BCC8] border-[rgba(244,208,63,0.1)] px-1.5 py-0.5"
                      >
                        <Tag className="w-2.5 h-2.5 mr-1" />
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}

                {/* Status indicator */}
                <div className="flex items-center justify-between pt-2 border-t border-[rgba(244,208,63,0.1)]">
                  <span className={`text-xs font-medium ${
                    isCompleted ? 'text-[#10B981]' : 
                    task.status === 'in-progress' ? 'text-[#F59E0B]' :
                    task.status === 'cancelled' ? 'text-[#EF4444]' : 'text-[#B8BCC8]'
                  }`}>
                    {task.status === 'todo' ? 'To Do' :
                     task.status === 'in-progress' ? 'In Progress' :
                     task.status === 'completed' ? 'Completed' :
                     task.status === 'cancelled' ? 'Cancelled' : task.status}
                  </span>
                  {isCompleted && <CheckCircle2 className="w-4 h-4 text-[#10B981]" />}
                </div>
              </HierarchyCard>
            </div>
          );
        })}
        </div>
        
        {/* Overflow indicator when there are more than 10 tasks */}
        {filteredTasks.length > 10 && (
          <div className="text-center pt-4 border-t border-[rgba(244,208,63,0.1)]">
            <p className="text-[#6B7280] text-sm">
              Showing 10 of {filteredTasks.length} tasks
            </p>
            <p className="text-[#6B7280] text-xs mt-1">
              +{filteredTasks.length - 10} more tasks not displayed
            </p>
          </div>
        )}
      </div>

      {/* Modals */}
      <CreateEditModal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        mode="create"
        type="task"
        parentId={hierarchyContext.projectId || undefined}
        onSuccess={() => setCreateModalOpen(false)}
      />

      <CreateEditModal
        isOpen={editModalOpen}
        onClose={() => {
          setEditModalOpen(false);
          setSelectedTask(null);
        }}
        mode="edit"
        type="task"
        item={selectedTask || undefined}
        onSuccess={() => {
          setEditModalOpen(false);
          setSelectedTask(null);
        }}
      />

      <DeleteConfirmModal
        isOpen={deleteModalOpen}
        onClose={() => {
          setDeleteModalOpen(false);
          setSelectedTask(null);
        }}
        onConfirm={confirmDelete}
        title={`Are you sure you want to delete this task?`}
        itemName={selectedTask?.name || ''}
        type="task"
      />
    </div>
  );
}