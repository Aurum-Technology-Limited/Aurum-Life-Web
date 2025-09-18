import { Target, Plus, FolderKanban, Layers3 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';

const SimpleAreasFallback = () => {
  const mockAreas = [
    {
      id: '1',
      name: 'Training & Exercise',
      description: 'Physical fitness and workout routines',
      pillar: 'Health & Wellness',
      color: '#10B981',
      projects: 3,
      tasks: 12,
      health: 85
    },
    {
      id: '2',
      name: 'Skill Development',
      description: 'Learning new technologies and improving expertise',
      pillar: 'Career Growth',
      color: '#3B82F6',
      projects: 5,
      tasks: 18,
      health: 92
    },
    {
      id: '3',
      name: 'Family Time',
      description: 'Quality time and activities with family',
      pillar: 'Relationships',
      color: '#EF4444',
      projects: 2,
      tasks: 8,
      health: 78
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Focus Areas</h1>
          <p className="text-[#B8BCC8]">
            Specific focus categories within your strategic pillars
          </p>
        </div>
        <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
          <Plus className="w-4 h-4 mr-2" />
          New Area
        </Button>
      </div>

      {/* Areas Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockAreas.map(area => (
          <Card key={area.id} className="glassmorphism-card border-0 group cursor-pointer hover:scale-[1.02] transition-all duration-200">
            <CardHeader className="pb-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-12 h-12 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: `${area.color}15`, border: `1px solid ${area.color}30` }}
                  >
                    <Target className="w-6 h-6" style={{ color: area.color }} />
                  </div>
                  <div>
                    <CardTitle className="text-white text-lg">{area.name}</CardTitle>
                    <Badge variant="outline" className="text-xs border-[rgba(244,208,63,0.3)] text-[#B8BCC8] mt-1">
                      {area.pillar}
                    </Badge>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-[#F4D03F]">{area.health}%</div>
                  <div className="text-xs text-[#B8BCC8]">Health</div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <CardDescription className="text-[#B8BCC8]">
                {area.description}
              </CardDescription>
              
              {/* Metrics */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <FolderKanban className="w-4 h-4 text-[#3B82F6]" />
                  <span className="text-sm text-[#B8BCC8]">{area.projects} Projects</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Layers3 className="w-4 h-4 text-[#10B981]" />
                  <span className="text-sm text-[#B8BCC8]">{area.tasks} Tasks</span>
                </div>
              </div>

              {/* Health Bar */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[#B8BCC8]">Area Health</span>
                  <span className="text-xs text-[#F4D03F]">{area.health}%</span>
                </div>
                <div className="w-full bg-[rgba(244,208,63,0.1)] rounded-full h-2">
                  <div 
                    className="h-2 rounded-full bg-gradient-to-r from-[#F4D03F] to-[#F7DC6F]"
                    style={{ width: `${area.health}%` }}
                  />
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex items-center space-x-2 pt-2 border-t border-[rgba(244,208,63,0.1)]">
                <Button variant="ghost" size="sm" className="text-[#B8BCC8] hover:text-[#F4D03F] flex-1">
                  View Projects
                </Button>
                <Button variant="ghost" size="sm" className="text-[#B8BCC8] hover:text-[#F4D03F]">
                  Edit
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State for No Areas */}
      <div className="text-center py-12">
        <Card className="glassmorphism-card border-0 max-w-md mx-auto">
          <CardContent className="p-8">
            <Target className="w-16 h-16 text-[#F4D03F] mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Start Organizing Your Focus</h3>
            <p className="text-[#B8BCC8] mb-6">
              Create focus areas to organize your projects within strategic pillars. Areas help you maintain clarity and direction.
            </p>
            <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Area
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SimpleAreasFallback;