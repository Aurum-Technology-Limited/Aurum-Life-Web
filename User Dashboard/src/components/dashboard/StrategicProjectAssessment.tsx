import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { TrendingUp, AlertTriangle, CheckCircle, Clock, Target, Zap } from 'lucide-react';

interface Project {
  id: string;
  name: string;
  pillar: string;
  area: string;
  impact: 'High' | 'Medium' | 'Low';
  progress: number;
  health: 'On Track' | 'At Risk' | 'Blocked';
  strategicValue: number;
  estimatedCompletion: string;
  focusTime: number;
  energyLevel: 'High' | 'Medium' | 'Low';
}

export function StrategicProjectAssessment() {
  const projects: Project[] = [
    {
      id: '1',
      name: 'Alchemy Site',
      pillar: 'Work',
      area: 'Portfolio',
      impact: 'High',
      progress: 62,
      health: 'On Track',
      strategicValue: 85,
      estimatedCompletion: '2 weeks',
      focusTime: 12,
      energyLevel: 'High'
    },
    {
      id: '2',
      name: 'Strength Cycle',
      pillar: 'Health',
      area: 'Training',
      impact: 'Medium',
      progress: 48,
      health: 'At Risk',
      strategicValue: 65,
      estimatedCompletion: '3 weeks',
      focusTime: 8,
      energyLevel: 'Medium'
    },
    {
      id: '3',
      name: 'Spring Brunch',
      pillar: 'Relationships',
      area: 'Family',
      impact: 'Low',
      progress: 35,
      health: 'On Track',
      strategicValue: 40,
      estimatedCompletion: '1 week',
      focusTime: 4,
      energyLevel: 'Low'
    },
    {
      id: '4',
      name: 'Kitchen Remodel',
      pillar: 'Home',
      area: 'Renovation',
      impact: 'Medium',
      progress: 25,
      health: 'Blocked',
      strategicValue: 55,
      estimatedCompletion: '6 weeks',
      focusTime: 0,
      energyLevel: 'Low'
    }
  ];

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'High': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'Medium': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'Low': return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'On Track': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'At Risk': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case 'Blocked': return <Clock className="w-4 h-4 text-red-400" />;
      default: return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'On Track': return 'text-green-400';
      case 'At Risk': return 'text-yellow-400';
      case 'Blocked': return 'text-red-400';
      default: return 'text-gray-400';
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

  const highImpactProjects = projects.filter(p => p.impact === 'High');
  const mediumImpactProjects = projects.filter(p => p.impact === 'Medium');
  const lowImpactProjects = projects.filter(p => p.impact === 'Low');

  return (
    <div className="strategic-project-assessment rounded-2xl border p-5 mb-6" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold tracking-tight">Strategic Project Assessment</h3>
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5" style={{color: '#F4D03F'}} />
          <span className="text-sm" style={{color: '#B8BCC8'}}>Impact-Based Organization</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* High Impact Projects */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <h4 className="text-sm font-medium" style={{color: '#B8BCC8'}}>High Strategic Impact</h4>
            <Badge variant="secondary" className="text-xs">{highImpactProjects.length}</Badge>
          </div>
          <div className="space-y-3">
            {highImpactProjects.map((project) => (
              <Card key={project.id} className="border-green-500/20 bg-green-500/5">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{project.name}</CardTitle>
                    {getHealthIcon(project.health)}
                  </div>
                  <div className="text-xs" style={{color: '#B8BCC8'}}>{project.pillar} → {project.area}</div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span>Progress</span>
                      <span className="font-medium">{project.progress}%</span>
                    </div>
                    <Progress value={project.progress} className="h-2" />
                    
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        <span>{project.strategicValue}%</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Zap className={`w-3 h-3 ${getEnergyColor(project.energyLevel)}`} />
                        <span className={getEnergyColor(project.energyLevel)}>{project.energyLevel}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs">
                      <span className={getHealthColor(project.health)}>{project.health}</span>
                      <span style={{color: '#B8BCC8'}}>{project.estimatedCompletion}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Medium Impact Projects */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <h4 className="text-sm font-medium" style={{color: '#B8BCC8'}}>Medium Strategic Impact</h4>
            <Badge variant="secondary" className="text-xs">{mediumImpactProjects.length}</Badge>
          </div>
          <div className="space-y-3">
            {mediumImpactProjects.map((project) => (
              <Card key={project.id} className="border-blue-500/20 bg-blue-500/5">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{project.name}</CardTitle>
                    {getHealthIcon(project.health)}
                  </div>
                  <div className="text-xs" style={{color: '#B8BCC8'}}>{project.pillar} → {project.area}</div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span>Progress</span>
                      <span className="font-medium">{project.progress}%</span>
                    </div>
                    <Progress value={project.progress} className="h-2" />
                    
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        <span>{project.strategicValue}%</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Zap className={`w-3 h-3 ${getEnergyColor(project.energyLevel)}`} />
                        <span className={getEnergyColor(project.energyLevel)}>{project.energyLevel}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs">
                      <span className={getHealthColor(project.health)}>{project.health}</span>
                      <span style={{color: '#B8BCC8'}}>{project.estimatedCompletion}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Low Impact Projects */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-500"></div>
            <h4 className="text-sm font-medium" style={{color: '#B8BCC8'}}>Low Strategic Impact</h4>
            <Badge variant="secondary" className="text-xs">{lowImpactProjects.length}</Badge>
          </div>
          <div className="space-y-3">
            {lowImpactProjects.map((project) => (
              <Card key={project.id} className="border-gray-500/20 bg-gray-500/5">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{project.name}</CardTitle>
                    {getHealthIcon(project.health)}
                  </div>
                  <div className="text-xs" style={{color: '#B8BCC8'}}>{project.pillar} → {project.area}</div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span>Progress</span>
                      <span className="font-medium">{project.progress}%</span>
                    </div>
                    <Progress value={project.progress} className="h-2" />
                    
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        <span>{project.strategicValue}%</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Zap className={`w-3 h-3 ${getEnergyColor(project.energyLevel)}`} />
                        <span className={getEnergyColor(project.energyLevel)}>{project.energyLevel}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs">
                      <span className={getHealthColor(project.health)}>{project.health}</span>
                      <span style={{color: '#B8BCC8'}}>{project.estimatedCompletion}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Strategic Project Summary */}
      <div className="mt-6 pt-4 border-t" style={{borderColor: 'rgba(244,208,63,0.1)'}}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
            <div className="text-lg font-semibold" style={{color: '#F4D03F'}}>{projects.length}</div>
            <div className="text-xs" style={{color: '#B8BCC8'}}>Total Projects</div>
          </div>
          <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
            <div className="text-lg font-semibold text-green-400">{highImpactProjects.length}</div>
            <div className="text-xs" style={{color: '#B8BCC8'}}>High Impact</div>
          </div>
          <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
            <div className="text-lg font-semibold text-yellow-400">{projects.filter(p => p.health === 'At Risk').length}</div>
            <div className="text-xs" style={{color: '#B8BCC8'}}>At Risk</div>
          </div>
          <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
            <div className="text-lg font-semibold" style={{color: '#F4D03F'}}>
              {Math.round(projects.reduce((acc, p) => acc + p.progress, 0) / projects.length)}%
            </div>
            <div className="text-xs" style={{color: '#B8BCC8'}}>Avg Progress</div>
          </div>
        </div>
      </div>
    </div>
  );
}
