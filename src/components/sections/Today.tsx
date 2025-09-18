import { useState } from 'react';
import { Calendar, Sun, CheckCircle2, Clock, Plus, Target, Users, Timer } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import CreateEditModal from '../shared/CreateEditModal';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import TodayButtonDebug from '../debug/TodayButtonDebug';

const mockTodayTasks = [
  {
    id: 1,
    title: 'Morning workout - Week 8 training',
    pillar: 'Health & Wellness',
    priority: 'high',
    timeEstimate: '60 min',
    completed: true
  },
  {
    id: 2,
    title: 'React component code review',
    pillar: 'Career Growth',
    priority: 'high',
    timeEstimate: '45 min',
    completed: false
  },
  {
    id: 3,
    title: 'Call mom for birthday planning',
    pillar: 'Relationships',
    priority: 'medium',
    timeEstimate: '30 min',
    completed: false
  },
  {
    id: 4,
    title: 'Review investment performance',
    pillar: 'Personal Finance',
    priority: 'medium',
    timeEstimate: '20 min',
    completed: false
  },
  {
    id: 5,
    title: 'Evening journaling session',
    pillar: 'Learning & Growth',
    priority: 'low',
    timeEstimate: '15 min',
    completed: false
  }
];

const mockTimeBlocks = [
  { time: '06:00', activity: 'Morning Routine', type: 'personal', duration: '60 min' },
  { time: '07:00', activity: 'Workout Session', type: 'health', duration: '60 min' },
  { time: '09:00', activity: 'Deep Work Block', type: 'career', duration: '120 min' },
  { time: '11:00', activity: 'Team Standup', type: 'career', duration: '30 min' },
  { time: '14:00', activity: 'Family Time', type: 'relationships', duration: '90 min' },
  { time: '16:00', activity: 'Financial Review', type: 'finance', duration: '30 min' },
  { time: '19:00', activity: 'Learning Time', type: 'growth', duration: '60 min' },
  { time: '21:00', activity: 'Reflection & Planning', type: 'personal', duration: '30 min' }
];

export default function Today() {
  // State for modals
  const [createTaskModalOpen, setCreateTaskModalOpen] = useState(false);
  const [createTimeBlockModalOpen, setCreateTimeBlockModalOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<string>('');
  
  // Enhanced features store
  const { 
    getAllTasks, 
    getAllProjects, 
    addTimeBlock, 
    getTodaysTimeBlocks,
    completeTask,
    pillars 
  } = useEnhancedFeaturesStore();

  // Get real data from store
  const allTasks = getAllTasks();
  const allProjects = getAllProjects();
  const timeBlocks = getTodaysTimeBlocks();
  
  // Filter today's priority tasks (high and medium priority tasks that are not completed)
  const todaysTasks = allTasks.filter(task => 
    task.status !== 'completed' && 
    (task.priority === 'high' || task.priority === 'medium')
  ).slice(0, 5); // Show max 5 priority tasks

  const completedTasks = allTasks.filter(task => task.status === 'completed').length;
  const totalTasks = allTasks.length;
  const progressPercentage = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const currentDate = new Date();
  const dateString = currentDate.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  // Handle task completion toggle with error protection
  const handleTaskComplete = (taskId: string) => {
    try {
      window.dispatchEvent(new CustomEvent('aurumDebugEvent', {
        detail: { 
          type: 'TASK_ACTION', 
          message: `Task completion clicked for task: ${taskId}`,
          data: { taskId, action: 'complete' }
        }
      }));
      
      completeTask(taskId);
    } catch (error) {
      console.log('Task completion error (non-critical):', error);
    }
  };

  // Handle quick task creation with timeout protection
  const handleQuickTaskCreate = () => {
    try {
      // Dispatch debug event
      window.dispatchEvent(new CustomEvent('aurumDebugEvent', {
        detail: { 
          type: 'BUTTON_CLICK', 
          message: 'Add Task button clicked',
          data: { projectsCount: allProjects.length }
        }
      }));
      
      if (allProjects.length === 0) {
        // If no projects exist, offer to create one first
        const shouldCreateProject = window.confirm(
          'You need at least one project to add tasks to. Would you like to go to the Projects section to create one first?'
        );
        
        if (shouldCreateProject) {
          // Dispatch navigation event to go to Projects section
          try {
            window.dispatchEvent(new CustomEvent('aurumNavigate', {
              detail: { section: 'projects' }
            }));
          } catch (error) {
            console.log('Navigation dispatch failed (non-critical):', error);
          }
        }
        return;
      }
      
      window.dispatchEvent(new CustomEvent('aurumDebugEvent', {
        detail: { 
          type: 'MODAL_OPEN', 
          message: 'Opening task creation modal',
          data: { modalType: 'createTask' }
        }
      }));
      
      setCreateTaskModalOpen(true);
    } catch (error) {
      console.log('Task creation handler error (non-critical):', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <Sun className="w-8 h-8 text-[#F4D03F]" />
          <h1 className="text-3xl font-bold text-white">Today</h1>
        </div>
        <p className="text-[#B8BCC8]">{dateString}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Today's Focus */}
        <div className="space-y-6">
          
          {/* Progress Overview */}
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-white">Daily Progress</CardTitle>
                  <CardDescription className="text-[#B8BCC8]">
                    Your focus for today aligned with strategic goals
                  </CardDescription>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-[#F4D03F]">{progressPercentage}%</div>
                  <div className="text-sm text-[#B8BCC8]">{completedTasks}/{totalTasks} completed</div>
                </div>
              </div>
              <Progress value={progressPercentage} className="h-3" />
            </CardHeader>
          </Card>

          {/* Today's Tasks */}
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white">Priority Tasks</CardTitle>
                <Button 
                  size="sm" 
                  className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleQuickTaskCreate();
                  }}
                  data-testid="add-task-button"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Task
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {todaysTasks.length === 0 ? (
                <div className="text-center py-8">
                  <Target className="w-12 h-12 text-[#F4D03F] mx-auto mb-4" />
                  <p className="text-[#B8BCC8] mb-4">
                    No priority tasks for today. Create your first task to get started!
                  </p>
                  <Button 
                    size="sm" 
                    className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleQuickTaskCreate();
                    }}
                    data-testid="create-first-task-button"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Create Your First Task
                  </Button>
                </div>
              ) : (
                todaysTasks.map(task => {
                  // Find the project and pillar for this task
                  const project = allProjects.find(p => p.id === task.projectId);
                  const pillar = pillars.find(p => p.areas.some(a => a.projects.some(pr => pr.id === task.projectId)));
                  
                  return (
                    <div key={task.id} className="flex items-center space-x-3 p-3 rounded-lg bg-[rgba(244,208,63,0.02)] hover:bg-[rgba(244,208,63,0.05)] transition-colors">
                      <CheckCircle2 
                        className={`w-5 h-5 cursor-pointer ${
                          task.status === 'completed' ? 'text-[#10B981]' : 'text-[#6B7280] hover:text-[#10B981]'
                        }`}
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleTaskComplete(task.id);
                        }}
                        data-testid="task-checkbox"
                      />
                      <div className="flex-1">
                        <p className={`font-medium ${task.status === 'completed' ? 'line-through text-[#6B7280]' : 'text-white'}`}>
                          {task.name}
                        </p>
                        <div className="flex items-center space-x-3 mt-1">
                          <Badge 
                            variant="outline" 
                            className="text-xs border-[rgba(244,208,63,0.3)] text-[#B8BCC8]"
                          >
                            <Target className="w-3 h-3 mr-1" />
                            {pillar?.name || 'Unknown Pillar'}
                          </Badge>
                          <span className={`text-xs ${
                            task.priority === 'high' ? 'text-[#EF4444]' : 
                            task.priority === 'medium' ? 'text-[#F59E0B]' : 
                            task.priority === 'urgent' ? 'text-[#DC2626]' :
                            'text-[#6B7280]'
                          }`}>
                            {task.priority} priority
                          </span>
                          {task.estimatedHours && (
                            <span className="text-xs text-[#6B7280]">
                              {task.estimatedHours}h estimated
                            </span>
                          )}
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" className="text-[#B8BCC8] hover:text-[#F4D03F]">
                        <Clock className="w-4 h-4" />
                      </Button>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>
        </div>

        {/* Simple Calendar Preview */}
        <div className="space-y-6">
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Calendar className="w-5 h-5 mr-2 text-[#F4D03F]" />
                Today's Schedule
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-center py-8">
                <Calendar className="w-12 h-12 text-[#F4D03F] mx-auto mb-4" />
                <p className="text-[#B8BCC8] mb-4">
                  Your daily schedule and time blocks will appear here
                </p>
                <Button 
                  size="sm" 
                  className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    window.dispatchEvent(new CustomEvent('aurumDebugEvent', {
                      detail: { 
                        type: 'BUTTON_CLICK', 
                        message: 'Add Time Block button clicked - Schedule section',
                        data: { modalType: 'createTimeBlock' }
                      }
                    }));
                    setCreateTimeBlockModalOpen(true);
                  }}
                  data-testid="add-time-block-button"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Time Block
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Quick Time Blocks Preview */}
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <CardTitle className="text-white text-lg">Time Blocks</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {timeBlocks.length === 0 ? (
                <div className="text-center py-6">
                  <Timer className="w-8 h-8 text-[#F4D03F] mx-auto mb-2" />
                  <p className="text-[#B8BCC8] text-sm mb-3">
                    No time blocks scheduled for today
                  </p>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      window.dispatchEvent(new CustomEvent('aurumDebugEvent', {
                        detail: { 
                          type: 'BUTTON_CLICK', 
                          message: 'Add First Time Block button clicked',
                          data: { modalType: 'createTimeBlock', context: 'empty-state' }
                        }
                      }));
                      setCreateTimeBlockModalOpen(true);
                    }}
                    data-testid="add-first-time-block-button"
                  >
                    <Plus className="w-3 h-3 mr-1" />
                    Add First Time Block
                  </Button>
                </div>
              ) : (
                <>
                  {timeBlocks.slice(0, 4).map((block) => (
                    <div key={block.id} className="flex items-center justify-between p-2 rounded-lg bg-[rgba(244,208,63,0.02)] hover:bg-[rgba(244,208,63,0.05)] transition-colors">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: block.color || '#F4D03F' }}
                        />
                        <div>
                          <p className="text-white text-sm font-medium">{block.title}</p>
                          <p className="text-[#B8BCC8] text-xs">
                            {new Date(block.startTime).toLocaleTimeString('en-US', { 
                              hour: '2-digit', 
                              minute: '2-digit',
                              hour12: true 
                            })} • {block.duration || '60'} min
                          </p>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-xs border-[rgba(244,208,63,0.3)] text-[#B8BCC8]">
                        {block.type || 'focus'}
                      </Badge>
                    </div>
                  ))}
                  {timeBlocks.length > 4 && (
                    <div className="text-center pt-2">
                      <Button variant="ghost" size="sm" className="text-[#B8BCC8] hover:text-[#F4D03F]">
                        View all {timeBlocks.length} time blocks
                      </Button>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Task Creation Modal - Always render, but handle empty projects inside modal */}
      <CreateEditModal
        isOpen={createTaskModalOpen}
        onClose={() => {
          window.dispatchEvent(new CustomEvent('aurumDebugEvent', {
            detail: { 
              type: 'MODAL_CLOSE', 
              message: 'Task creation modal closed',
              data: { modalType: 'createTask' }
            }
          }));
          setCreateTaskModalOpen(false);
          setSelectedProject('');
        }}
        mode="create"
        type="task"
        parentId={selectedProject || allProjects[0]?.id}
        onSuccess={() => {
          window.dispatchEvent(new CustomEvent('aurumDebugEvent', {
            detail: { 
              type: 'TASK_ACTION', 
              message: 'Task created successfully',
              data: { action: 'create', context: 'today-screen' }
            }
          }));
          setCreateTaskModalOpen(false);
          setSelectedProject('');
        }}
      />

      {/* Time Block Creation Modal */}
      <TimeBlockModal
        isOpen={createTimeBlockModalOpen}
        onClose={() => setCreateTimeBlockModalOpen(false)}
        onSave={(timeBlockData) => {
          addTimeBlock(timeBlockData);
          setCreateTimeBlockModalOpen(false);
        }}
      />

      {/* Debug Component - only shows in development */}
      {process.env.NODE_ENV === 'development' && <TodayButtonDebug />}
    </div>
  );
}

// Time Block Creation Modal Component
function TimeBlockModal({ 
  isOpen, 
  onClose, 
  onSave 
}: { 
  isOpen: boolean; 
  onClose: () => void; 
  onSave: (timeBlock: any) => void; 
}) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    startTime: '',
    endTime: '',
    type: 'focus',
    color: '#F4D03F'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      window.dispatchEvent(new CustomEvent('aurumDebugEvent', {
        detail: { 
          type: 'FORM_SUBMIT', 
          message: 'Time block form submitted',
          data: { formType: 'timeBlock', hasTitle: !!formData.title }
        }
      }));
      
      if (!formData.title || !formData.startTime || !formData.endTime) {
        alert('Please fill in all required fields');
        return;
      }

      const today = new Date();
      const startDateTime = new Date(`${today.toDateString()} ${formData.startTime}`);
      const endDateTime = new Date(`${today.toDateString()} ${formData.endTime}`);
      
      if (endDateTime <= startDateTime) {
        alert('End time must be after start time');
        return;
      }

      const duration = Math.round((endDateTime.getTime() - startDateTime.getTime()) / (1000 * 60));

      const timeBlockData = {
        title: formData.title,
        description: formData.description,
        startTime: startDateTime,
        endTime: endDateTime,
        type: formData.type,
        color: formData.color,
        duration: `${duration}`,
        completed: false,
        pillarId: '', // Can be enhanced later
        areaId: '', // Can be enhanced later
        projectId: '' // Can be enhanced later
      };

      window.dispatchEvent(new CustomEvent('aurumDebugEvent', {
        detail: { 
          type: 'TIME_BLOCK_ACTION', 
          message: 'Time block saved successfully',
          data: { action: 'create', duration: timeBlockData.duration }
        }
      }));
      
      onSave(timeBlockData);

      // Reset form
      setFormData({
        title: '',
        description: '',
        startTime: '',
        endTime: '',
        type: 'focus',
        color: '#F4D03F'
      });
    } catch (error) {
      console.log('Time block submission error (non-critical):', error);
      alert('Error creating time block. Please try again.');
    }
  };

  const timeBlockTypes = [
    { value: 'focus', label: 'Deep Focus' },
    { value: 'meeting', label: 'Meeting' },
    { value: 'break', label: 'Break' },
    { value: 'exercise', label: 'Exercise' },
    { value: 'learning', label: 'Learning' },
    { value: 'personal', label: 'Personal Time' },
    { value: 'admin', label: 'Admin Tasks' }
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="glassmorphism-card border-0 bg-[#1A1D29] text-white max-w-lg">
        <DialogHeader>
          <DialogTitle 
            style={{ 
              color: 'var(--aurum-text-primary)',
              fontSize: '1.5rem',
              fontWeight: '600'
            }}
          >
            Create Time Block
          </DialogTitle>
          <DialogDescription 
            style={{ color: 'var(--aurum-text-secondary)' }}
          >
            Schedule a focused time block for today
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div className="space-y-2">
            <Label 
              htmlFor="title"
              style={{ 
                color: 'var(--aurum-text-primary)',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}
            >
              Title *
            </Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              placeholder="e.g., Deep Work Session"
              className="glassmorphism-panel border-0"
              style={{ 
                backgroundColor: 'var(--aurum-secondary-bg)',
                color: 'var(--aurum-text-primary)'
              }}
              required
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label 
              htmlFor="description"
              style={{ 
                color: 'var(--aurum-text-primary)',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}
            >
              Description
            </Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="What will you focus on during this time?"
              className="glassmorphism-panel border-0"
              style={{ 
                backgroundColor: 'var(--aurum-secondary-bg)',
                color: 'var(--aurum-text-primary)'
              }}
              rows={3}
            />
          </div>

          {/* Time Range */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label 
                htmlFor="startTime"
                style={{ 
                  color: 'var(--aurum-text-primary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}
              >
                Start Time *
              </Label>
              <Input
                id="startTime"
                type="time"
                value={formData.startTime}
                onChange={(e) => setFormData(prev => ({ ...prev, startTime: e.target.value }))}
                className="glassmorphism-panel border-0"
                style={{ 
                  backgroundColor: 'var(--aurum-secondary-bg)',
                  color: 'var(--aurum-text-primary)'
                }}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label 
                htmlFor="endTime"
                style={{ 
                  color: 'var(--aurum-text-primary)',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}
              >
                End Time *
              </Label>
              <Input
                id="endTime"
                type="time"
                value={formData.endTime}
                onChange={(e) => setFormData(prev => ({ ...prev, endTime: e.target.value }))}
                className="glassmorphism-panel border-0"
                style={{ 
                  backgroundColor: 'var(--aurum-secondary-bg)',
                  color: 'var(--aurum-text-primary)'
                }}
                required
              />
            </div>
          </div>

          {/* Type */}
          <div className="space-y-2">
            <Label 
              htmlFor="type"
              style={{ 
                color: 'var(--aurum-text-primary)',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}
            >
              Block Type
            </Label>
            <Select
              value={formData.type}
              onValueChange={(value) => setFormData(prev => ({ ...prev, type: value }))}
            >
              <SelectTrigger className="glassmorphism-panel border-0">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="glassmorphism-card border-0">
                {timeBlockTypes.map(type => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              style={{ 
                color: 'var(--aurum-text-secondary)',
                fontSize: '0.875rem'
              }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              style={{ fontSize: '0.875rem' }}
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Time Block
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}