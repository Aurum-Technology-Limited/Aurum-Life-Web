import { FolderKanban, Plus, CheckSquare, Calendar, Target } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';

const SimpleProjectsFallback = () => {
  const mockProjects = [
    {
      id: '1',
      name: '30-Day Running Challenge',
      description: 'Complete daily running sessions to build endurance',
      area: 'Training & Exercise',
      pillar: 'Health & Wellness',
      color: '#10B981',
      progress: 75,
      tasks: 15,
      completedTasks: 11,
      priority: 'high',
      dueDate: '2024-12-31'
    },
    {
      id: '2',
      name: 'React Certification Course',
      description: 'Master advanced React concepts and get certified',
      area: 'Skill Development',
      pillar: 'Career Growth',
      color: '#3B82F6',
      progress: 60,
      tasks: 20,
      completedTasks: 12,
      priority: 'high',
      dueDate: '2024-12-15'
    },
    {
      id: '3',
      name: 'Family Vacation Planning',
      description: 'Plan and organize summer family vacation',
      area: 'Family Time',
      pillar: 'Relationships',
      color: '#EF4444',
      progress: 40,
      tasks: 8,
      completedTasks: 3,
      priority: 'medium',
      dueDate: '2024-06-01'
    }
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#EF4444';
      case 'medium': return '#F59E0B';
      case 'low': return '#6B7280';
      default: return '#6B7280';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Projects</h1>
          <p className="text-[#B8BCC8]">
            Concrete initiatives within your focus areas that move you toward your goals
          </p>
        </div>
        <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
          <Plus className="w-4 h-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {mockProjects.map(project => (
          <Card key={project.id} className="glassmorphism-card border-0 group cursor-pointer hover:scale-[1.01] transition-all duration-200">
            <CardHeader className="pb-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-12 h-12 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: `${project.color}15`, border: `1px solid ${project.color}30` }}
                  >
                    <FolderKanban className="w-6 h-6" style={{ color: project.color }} />
                  </div>
                  <div>
                    <CardTitle className="text-white text-lg">{project.name}</CardTitle>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant="outline" className="text-xs border-[rgba(244,208,63,0.3)] text-[#B8BCC8]">
                        {project.area}
                      </Badge>
                      <Badge 
                        variant="outline" 
                        className="text-xs border-[rgba(244,208,63,0.3)]"
                        style={{ color: getPriorityColor(project.priority) }}
                      >
                        {project.priority}
                      </Badge>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-[#F4D03F]">{project.progress}%</div>
                  <div className="text-xs text-[#B8BCC8]">Complete</div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <CardDescription className="text-[#B8BCC8]">
                {project.description}
              </CardDescription>
              
              {/* Progress */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[#B8BCC8]">Progress</span>
                  <span className="text-sm text-[#F4D03F]">{project.completedTasks}/{project.tasks} tasks</span>
                </div>
                <Progress value={project.progress} className="h-2" />
              </div>

              {/* Metrics */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckSquare className="w-4 h-4 text-[#10B981]" />
                  <span className="text-sm text-[#B8BCC8]">{project.tasks} Tasks</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-[#F59E0B]" />
                  <span className="text-sm text-[#B8BCC8]">Due {project.dueDate}</span>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex items-center space-x-2 pt-2 border-t border-[rgba(244,208,63,0.1)]">
                <Button variant="ghost" size="sm" className="text-[#B8BCC8] hover:text-[#F4D03F] flex-1">
                  View Tasks
                </Button>
                <Button variant="ghost" size="sm" className="text-[#B8BCC8] hover:text-[#F4D03F]">
                  Edit
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Stats Summary */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <Target className="w-5 h-5 mr-2 text-[#F4D03F]" />
            Project Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-[#F4D03F] mb-1">3</div>
              <div className="text-sm text-[#B8BCC8]">Active Projects</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-[#10B981] mb-1">58%</div>
              <div className="text-sm text-[#B8BCC8]">Average Progress</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-[#3B82F6] mb-1">43</div>
              <div className="text-sm text-[#B8BCC8]">Total Tasks</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Empty State */}
      <div className="text-center py-12">
        <Card className="glassmorphism-card border-0 max-w-md mx-auto">
          <CardContent className="p-8">
            <FolderKanban className="w-16 h-16 text-[#F4D03F] mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Ready to Start Building?</h3>
            <p className="text-[#B8BCC8] mb-6">
              Create projects to organize your tasks and track progress toward your goals. Each project should be specific and actionable.
            </p>
            <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Project
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SimpleProjectsFallback;