import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Button } from './ui/button';
import { 
  Dumbbell, 
  BookOpen, 
  Heart, 
  Briefcase, 
  Home, 
  Brain,
  TrendingUp,
  Clock,
  Target,
  Plus,
  Settings
} from 'lucide-react';

interface Area {
  id: string;
  name: string;
  pillar: string;
  progress: number;
  activeProjects: number;
  tasks: number;
  priority: 'High' | 'Medium' | 'Low';
  capacity: number;
  focusTime: number;
  lastActivity: string;
}

interface Project {
  id: string;
  name: string;
  area: string;
  progress: number;
  status: 'Active' | 'Planning' | 'Blocked';
  strategicValue: number;
}

export function AreasSection() {
  const [selectedArea, setSelectedArea] = useState<string | null>(null);

  const areas: Area[] = [
    {
      id: '1',
      name: 'Training',
      pillar: 'Health',
      progress: 70,
      activeProjects: 3,
      tasks: 12,
      priority: 'High',
      capacity: 85,
      focusTime: 8,
      lastActivity: '2 hours ago'
    },
    {
      id: '2',
      name: 'Learning',
      pillar: 'Growth',
      progress: 55,
      activeProjects: 2,
      tasks: 7,
      priority: 'High',
      capacity: 60,
      focusTime: 6,
      lastActivity: '1 day ago'
    },
    {
      id: '3',
      name: 'Family',
      pillar: 'Relationships',
      progress: 41,
      activeProjects: 1,
      tasks: 5,
      priority: 'Medium',
      capacity: 40,
      focusTime: 4,
      lastActivity: '3 days ago'
    },
    {
      id: '4',
      name: 'Portfolio',
      pillar: 'Work',
      progress: 62,
      activeProjects: 2,
      tasks: 8,
      priority: 'High',
      capacity: 75,
      focusTime: 10,
      lastActivity: '1 hour ago'
    },
    {
      id: '5',
      name: 'Network',
      pillar: 'Work',
      progress: 38,
      activeProjects: 1,
      tasks: 4,
      priority: 'Medium',
      capacity: 45,
      focusTime: 3,
      lastActivity: '1 week ago'
    },
    {
      id: '6',
      name: 'Renovation',
      pillar: 'Home',
      progress: 25,
      activeProjects: 1,
      tasks: 6,
      priority: 'Low',
      capacity: 30,
      focusTime: 2,
      lastActivity: '2 weeks ago'
    }
  ];

  const projects: Project[] = [
    { id: '1', name: 'Strength Cycle', area: 'Training', progress: 48, status: 'Active', strategicValue: 65 },
    { id: '2', name: 'UI Mastery Path', area: 'Learning', progress: 35, status: 'Active', strategicValue: 70 },
    { id: '3', name: 'Spring Brunch', area: 'Family', progress: 35, status: 'Planning', strategicValue: 40 },
    { id: '4', name: 'Alchemy Site', area: 'Portfolio', progress: 62, status: 'Active', strategicValue: 85 },
    { id: '5', name: 'Networking Ritual', area: 'Network', progress: 20, status: 'Active', strategicValue: 55 },
    { id: '6', name: 'Kitchen Remodel', area: 'Renovation', progress: 25, status: 'Blocked', strategicValue: 45 }
  ];

  const getPillarIcon = (pillar: string) => {
    switch (pillar) {
      case 'Health': return <Dumbbell className="w-4 h-4" style={{color: '#F4D03F'}} />;
      case 'Growth': return <BookOpen className="w-4 h-4" style={{color: '#F4D03F'}} />;
      case 'Relationships': return <Heart className="w-4 h-4" style={{color: '#F4D03F'}} />;
      case 'Work': return <Briefcase className="w-4 h-4" style={{color: '#F4D03F'}} />;
      case 'Home': return <Home className="w-4 h-4" style={{color: '#F4D03F'}} />;
      default: return <Brain className="w-4 h-4" style={{color: '#F4D03F'}} />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'Medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'Low': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getCapacityColor = (capacity: number) => {
    if (capacity >= 80) return 'text-red-400';
    if (capacity >= 60) return 'text-yellow-400';
    return 'text-green-400';
  };

  const selectedAreaData = areas.find(area => area.id === selectedArea);
  const selectedAreaProjects = selectedAreaData ? 
    projects.filter(project => project.area === selectedAreaData.name) : [];

  return (
    <div className="areas-section space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Areas</h2>
          <p className="text-sm" style={{color: '#B8BCC8'}}>Strategic focus areas within your life pillars</p>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>
            <Plus className="w-4 h-4 mr-2" />
            New Area
          </Button>
          <Button size="sm" variant="outline" style={{borderColor: 'rgba(244,208,63,0.15)'}}>
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Areas Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {areas.map((area) => (
          <Card 
            key={area.id} 
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedArea === area.id ? 'ring-2' : ''
            }`}
            style={{
              background: 'rgba(26,29,41,0.45)',
              backdropFilter: 'blur(12px)',
              borderColor: selectedArea === area.id ? 'rgba(244,208,63,0.4)' : 'rgba(244,208,63,0.18)',
              ringColor: 'rgba(244,208,63,0.3)'
            }}
            onClick={() => setSelectedArea(selectedArea === area.id ? null : area.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getPillarIcon(area.pillar)}
                  <CardTitle className="text-sm font-medium">{area.name}</CardTitle>
                </div>
                <Badge className={`text-xs ${getPriorityColor(area.priority)}`}>
                  {area.priority}
                </Badge>
              </div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>{area.pillar}</div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                {/* Progress */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span>Progress</span>
                    <span className="font-medium">{area.progress}%</span>
                  </div>
                  <Progress value={area.progress} className="h-2" />
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-1">
                    <Target className="w-3 h-3" />
                    <span>{area.activeProjects} projects</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{area.tasks} tasks</span>
                  </div>
                </div>

                {/* Capacity */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span>Capacity</span>
                    <span className={`font-medium ${getCapacityColor(area.capacity)}`}>
                      {area.capacity}%
                    </span>
                  </div>
                  <div className="h-1 rounded-full overflow-hidden" style={{background: 'rgba(11,13,20,0.4)'}}>
                    <div 
                      className="h-full transition-all" 
                      style={{
                        width: `${area.capacity}%`,
                        background: area.capacity >= 80 ? 'linear-gradient(90deg, #EF4444, #F87171)' :
                                   area.capacity >= 60 ? 'linear-gradient(90deg, #F59E0B, #FCD34D)' :
                                   'linear-gradient(90deg, #10B981, #34D399)'
                      }}
                    ></div>
                  </div>
                </div>

                {/* Focus Time */}
                <div className="flex items-center justify-between text-xs">
                  <span>Focus Time</span>
                  <span className="font-medium" style={{color: '#F4D03F'}}>{area.focusTime}h</span>
                </div>

                {/* Last Activity */}
                <div className="text-xs" style={{color: '#6B7280'}}>
                  Last activity: {area.lastActivity}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Selected Area Details */}
      {selectedAreaData && (
        <Card className="mt-6" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getPillarIcon(selectedAreaData.pillar)}
                <CardTitle>{selectedAreaData.name} - Project Pipeline</CardTitle>
              </div>
              <Button size="sm" variant="outline" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>
                <Plus className="w-4 h-4 mr-2" />
                Add Project
              </Button>
            </div>
            <div className="text-sm" style={{color: '#B8BCC8'}}>
              {selectedAreaData.pillar} • {selectedAreaData.activeProjects} active projects • {selectedAreaData.tasks} tasks
            </div>
          </CardHeader>
          <CardContent>
            {selectedAreaProjects.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {selectedAreaProjects.map((project) => (
                  <div key={project.id} className="p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-sm font-medium">{project.name}</div>
                      <Badge variant="outline" className="text-xs">
                        {project.status}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span>Progress</span>
                        <span className="font-medium">{project.progress}%</span>
                      </div>
                      <Progress value={project.progress} className="h-1.5" />
                      <div className="flex items-center justify-between text-xs">
                        <span>Strategic Value</span>
                        <span className="font-medium" style={{color: '#F4D03F'}}>{project.strategicValue}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-sm" style={{color: '#B8BCC8'}}>
                No projects in this area yet. Create one to get started.
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Area Performance Summary */}
      <Card className="mt-6" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
        <CardHeader>
          <CardTitle className="text-lg">Area Performance Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
              <div className="text-lg font-semibold" style={{color: '#F4D03F'}}>{areas.length}</div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Total Areas</div>
            </div>
            <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
              <div className="text-lg font-semibold text-green-400">
                {areas.filter(a => a.priority === 'High').length}
              </div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>High Priority</div>
            </div>
            <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
              <div className="text-lg font-semibold text-yellow-400">
                {areas.filter(a => a.capacity >= 80).length}
              </div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Over Capacity</div>
            </div>
            <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
              <div className="text-lg font-semibold" style={{color: '#F4D03F'}}>
                {Math.round(areas.reduce((acc, a) => acc + a.progress, 0) / areas.length)}%
              </div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Avg Progress</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
