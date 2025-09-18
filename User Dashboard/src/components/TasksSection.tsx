import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Checkbox } from './ui/checkbox';
import { 
  Search, 
  Filter, 
  Plus, 
  Clock, 
  Zap, 
  Target, 
  ArrowRight,
  CheckCircle,
  Circle,
  AlertTriangle,
  Calendar,
  Energy
} from 'lucide-react';

interface Task {
  id: string;
  title: string;
  pillar: string;
  area: string;
  project: string;
  priority: 'P1' | 'P2' | 'P3' | 'P4';
  status: 'Active' | 'Completed' | 'Queued' | 'Backlog';
  estimatedTime: number;
  energyLevel: 'High' | 'Medium' | 'Low';
  workType: 'Deep Work' | 'Shallow Work';
  strategicImpact: 'High' | 'Medium' | 'Low';
  dueDate?: string;
  completed: boolean;
}

export function TasksSection() {
  const [searchTerm, setSearchTerm] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<string>('All');
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [energyFilter, setEnergyFilter] = useState<string>('All');
  const [workTypeFilter, setWorkTypeFilter] = useState<string>('All');

  const tasks: Task[] = [
    {
      id: '1',
      title: 'Deep work: Write project proposal draft',
      pillar: 'Work',
      area: 'Portfolio',
      project: 'Alchemy Site',
      priority: 'P1',
      status: 'Active',
      estimatedTime: 90,
      energyLevel: 'High',
      workType: 'Deep Work',
      strategicImpact: 'High',
      dueDate: 'Today',
      completed: false
    },
    {
      id: '2',
      title: '30m jog + mobility',
      pillar: 'Health',
      area: 'Training',
      project: 'Strength Cycle',
      priority: 'P2',
      status: 'Completed',
      estimatedTime: 30,
      energyLevel: 'Medium',
      workType: 'Shallow Work',
      strategicImpact: 'Medium',
      completed: true
    },
    {
      id: '3',
      title: 'Call mom and plan Sunday lunch',
      pillar: 'Relationships',
      area: 'Family',
      project: 'Spring Brunch',
      priority: 'P3',
      status: 'Queued',
      estimatedTime: 10,
      energyLevel: 'Low',
      workType: 'Shallow Work',
      strategicImpact: 'Low',
      dueDate: 'Tomorrow',
      completed: false
    },
    {
      id: '4',
      title: 'Read 10 pages: Atomic Habits',
      pillar: 'Growth',
      area: 'Learning',
      project: 'Reading Queue',
      priority: 'P4',
      status: 'Backlog',
      estimatedTime: 20,
      energyLevel: 'Low',
      workType: 'Shallow Work',
      strategicImpact: 'Medium',
      completed: false
    },
    {
      id: '5',
      title: 'Review competitor analysis',
      pillar: 'Work',
      area: 'Portfolio',
      project: 'Alchemy Site',
      priority: 'P2',
      status: 'Active',
      estimatedTime: 45,
      energyLevel: 'Medium',
      workType: 'Deep Work',
      strategicImpact: 'High',
      dueDate: 'Today',
      completed: false
    },
    {
      id: '6',
      title: 'Update LinkedIn profile',
      pillar: 'Work',
      area: 'Network',
      project: 'Networking Ritual',
      priority: 'P3',
      status: 'Queued',
      estimatedTime: 15,
      energyLevel: 'Low',
      workType: 'Shallow Work',
      strategicImpact: 'Medium',
      completed: false
    }
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'P1': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'P2': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'P3': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'P4': return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'bg-green-500/20 text-green-400';
      case 'Completed': return 'bg-green-500/20 text-green-400';
      case 'Queued': return 'bg-blue-500/20 text-blue-400';
      case 'Backlog': return 'bg-yellow-500/20 text-yellow-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getEnergyColor = (energy: string) => {
    switch (energy) {
      case 'High': return 'text-red-400';
      case 'Medium': return 'text-yellow-400';
      case 'Low': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'High': return 'text-green-400';
      case 'Medium': return 'text-yellow-400';
      case 'Low': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.pillar.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.area.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.project.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesPriority = priorityFilter === 'All' || task.priority === priorityFilter;
    const matchesStatus = statusFilter === 'All' || task.status === statusFilter;
    const matchesEnergy = energyFilter === 'All' || task.energyLevel === energyFilter;
    const matchesWorkType = workTypeFilter === 'All' || task.workType === workTypeFilter;

    return matchesSearch && matchesPriority && matchesStatus && matchesEnergy && matchesWorkType;
  });

  const toggleTask = (taskId: string) => {
    // In a real app, this would update the task's completed status
    console.log('Toggle task:', taskId);
  };

  return (
    <div className="tasks-section space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Tasks</h2>
          <p className="text-sm" style={{color: '#B8BCC8'}}>Strategic task management with alignment visibility</p>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>
            <Plus className="w-4 h-4 mr-2" />
            Add Task
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
        <CardContent className="p-4">
          <div className="space-y-4">
            {/* Search */}
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4" style={{color: '#B8BCC8'}} />
              <Input
                placeholder="Search tasks, projects, pillars..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="flex-1"
                style={{background: 'rgba(11,13,20,0.35)', borderColor: 'rgba(244,208,63,0.15)'}}
              />
            </div>

            {/* Filter Buttons */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm" style={{color: '#B8BCC8'}}>Priority:</span>
              {['All', 'P1', 'P2', 'P3', 'P4'].map((priority) => (
                <Button
                  key={priority}
                  size="sm"
                  variant={priorityFilter === priority ? "default" : "outline"}
                  onClick={() => setPriorityFilter(priority)}
                  className="text-xs"
                  style={{
                    backgroundColor: priorityFilter === priority ? '#F4D03F' : 'transparent',
                    color: priorityFilter === priority ? '#0B0D14' : '#B8BCC8',
                    borderColor: 'rgba(244,208,63,0.25)'
                  }}
                >
                  {priority}
                </Button>
              ))}

              <span className="ml-4 text-sm" style={{color: '#B8BCC8'}}>Status:</span>
              {['All', 'Active', 'Completed', 'Queued', 'Backlog'].map((status) => (
                <Button
                  key={status}
                  size="sm"
                  variant={statusFilter === status ? "default" : "outline"}
                  onClick={() => setStatusFilter(status)}
                  className="text-xs"
                  style={{
                    backgroundColor: statusFilter === status ? '#F4D03F' : 'transparent',
                    color: statusFilter === status ? '#0B0D14' : '#B8BCC8',
                    borderColor: 'rgba(244,208,63,0.15)'
                  }}
                >
                  {status}
                </Button>
              ))}

              <span className="ml-4 text-sm" style={{color: '#B8BCC8'}}>Energy:</span>
              {['All', 'High', 'Medium', 'Low'].map((energy) => (
                <Button
                  key={energy}
                  size="sm"
                  variant={energyFilter === energy ? "default" : "outline"}
                  onClick={() => setEnergyFilter(energy)}
                  className="text-xs"
                  style={{
                    backgroundColor: energyFilter === energy ? '#F4D03F' : 'transparent',
                    color: energyFilter === energy ? '#0B0D14' : '#B8BCC8',
                    borderColor: 'rgba(244,208,63,0.15)'
                  }}
                >
                  {energy}
                </Button>
              ))}

              <span className="ml-4 text-sm" style={{color: '#B8BCC8'}}>Work Type:</span>
              {['All', 'Deep Work', 'Shallow Work'].map((workType) => (
                <Button
                  key={workType}
                  size="sm"
                  variant={workTypeFilter === workType ? "default" : "outline"}
                  onClick={() => setWorkTypeFilter(workType)}
                  className="text-xs"
                  style={{
                    backgroundColor: workTypeFilter === workType ? '#F4D03F' : 'transparent',
                    color: workTypeFilter === workType ? '#0B0D14' : '#B8BCC8',
                    borderColor: 'rgba(244,208,63,0.15)'
                  }}
                >
                  {workType}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tasks List */}
      <div className="space-y-3">
        {filteredTasks.map((task) => (
          <Card 
            key={task.id} 
            className={`transition-all hover:shadow-lg ${
              task.completed ? 'opacity-60' : ''
            }`}
            style={{
              background: 'rgba(26,29,41,0.45)',
              backdropFilter: 'blur(12px)',
              borderColor: 'rgba(244,208,63,0.15)'
            }}
          >
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                {/* Checkbox */}
                <Checkbox
                  checked={task.completed}
                  onCheckedChange={() => toggleTask(task.id)}
                  className="mt-1"
                />

                {/* Task Content */}
                <div className="flex-1 space-y-2">
                  {/* Task Title */}
                  <div className="flex items-center gap-2">
                    <h3 className={`text-sm font-medium ${task.completed ? 'line-through text-gray-400' : ''}`}>
                      {task.title}
                    </h3>
                    <Badge className={`text-xs ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </Badge>
                    <Badge className={`text-xs ${getStatusColor(task.status)}`}>
                      {task.status}
                    </Badge>
                  </div>

                  {/* Strategic Path */}
                  <div className="flex items-center gap-1 text-xs">
                    <span className="px-2 py-0.5 rounded border" style={{borderColor: 'rgba(244,208,63,0.18)'}}>
                      {task.pillar} → {task.area}
                    </span>
                    <ArrowRight className="w-3 h-3" style={{color: '#B8BCC8'}} />
                    <span className="px-2 py-0.5 rounded border" style={{borderColor: 'rgba(244,208,63,0.18)'}}>
                      {task.project}
                    </span>
                    <ArrowRight className="w-3 h-3" style={{color: '#B8BCC8'}} />
                    <span className="px-2 py-0.5 rounded" style={{background: 'rgba(16,185,129,0.15)', color: '#10B981'}}>
                      Impact: {task.strategicImpact}
                    </span>
                  </div>

                  {/* Task Metadata */}
                  <div className="flex flex-wrap items-center gap-3 text-xs">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" style={{color: '#3B82F6'}} />
                      <span style={{color: '#3B82F6'}}>{task.estimatedTime}m</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Zap className={`w-3 h-3 ${getEnergyColor(task.energyLevel)}`} />
                      <span className={getEnergyColor(task.energyLevel)}>{task.energyLevel} Energy</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Target className={`w-3 h-3 ${getImpactColor(task.strategicImpact)}`} />
                      <span className={getImpactColor(task.strategicImpact)}>{task.workType}</span>
                    </div>
                    {task.dueDate && (
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" style={{color: '#F59E0B'}} />
                        <span style={{color: '#F59E0B'}}>Due: {task.dueDate}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1">
                  <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                    <Filter className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Task Summary */}
      <Card style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
        <CardContent className="p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold" style={{color: '#F4D03F'}}>{tasks.length}</div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Total Tasks</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-green-400">
                {tasks.filter(t => t.status === 'Active').length}
              </div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Active</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-blue-400">
                {tasks.filter(t => t.priority === 'P1').length}
              </div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>P1 Priority</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold" style={{color: '#F4D03F'}}>
                {tasks.reduce((acc, t) => acc + t.estimatedTime, 0)}m
              </div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Total Time</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
