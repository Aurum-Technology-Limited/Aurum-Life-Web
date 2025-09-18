import { useState } from 'react';
import { Zap, Mic, Plus, Play, Edit, Clock, Target, Heart, Activity, Calendar, Timer, BarChart3, Brain, CheckCircle, Repeat } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

export default function AIQuickActions() {
  const [isListening, setIsListening] = useState(false);
  const [recentActions] = useState([
    {
      name: "Created smart task breakdown",
      timestamp: "2 minutes ago",
      preview: "Split 'Launch Marketing Campaign' into 8 actionable tasks",
      result: "8 tasks created"
    },
    {
      name: "Optimized daily schedule",
      timestamp: "1 hour ago", 
      preview: "Rearranged tasks based on energy levels and priorities",
      result: "Schedule optimized"
    },
    {
      name: "Generated reflection prompt",
      timestamp: "3 hours ago",
      preview: "What am I most grateful for today?",
      result: "Prompt created"
    }
  ]);

  const [customActions] = useState([
    {
      icon: <Target className="w-5 h-5" />,
      name: "Weekly Review",
      description: "Comprehensive week analysis"
    },
    {
      icon: <Brain className="w-5 h-5" />,
      name: "Learning Path",
      description: "AI-curated skill development"
    },
    {
      icon: <Heart className="w-5 h-5" />,
      name: "Wellness Check",
      description: "Holistic health assessment"
    }
  ]);

  const handleVoiceInput = () => {
    setIsListening(!isListening);
    // Simulate voice recognition
    if (!isListening) {
      setTimeout(() => setIsListening(false), 3000);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="aurum-gradient w-10 h-10 rounded-lg flex items-center justify-center">
            <Zap className="w-6 h-6 text-[#0B0D14]" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">AI Quick Actions</h1>
            <p className="text-[#B8BCC8]">Instant AI assistance for daily tasks</p>
          </div>
        </div>
        
        <Button
          onClick={handleVoiceInput}
          className={`${isListening ? 'bg-[#EF4444] hover:bg-[#DC2626]' : 'bg-[#F4D03F] hover:bg-[#F7DC6F]'} text-[#0B0D14]`}
        >
          <Mic className={`w-4 h-4 mr-2 ${isListening ? 'animate-pulse' : ''}`} />
          {isListening ? 'Listening...' : 'Speak to AI'}
        </Button>
      </div>

      {/* Quick Action Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Task Management Section */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-[#F4D03F]" />
              <span>Task Management</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Intelligent task creation and organization
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Brain className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Create Smart Task
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <BarChart3 className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Prioritize My Day
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Target className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Break Down Project
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <CheckCircle className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Find Similar Tasks
            </Button>
          </CardContent>
        </Card>

        {/* Goal Planning Section */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Target className="w-5 h-5 text-[#F4D03F]" />
              <span>Goal Planning</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Strategic goal setting and progress tracking
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Target className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Set SMART Goal
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <BarChart3 className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Check Goal Progress
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Zap className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Suggest Next Steps
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Brain className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Goal Conflict Analysis
            </Button>
          </CardContent>
        </Card>

        {/* Emotional Support Section */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Heart className="w-5 h-5 text-[#F4D03F]" />
              <span>Emotional Support</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Mental wellness and emotional intelligence tools
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Heart className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Mood Check-in
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Activity className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Stress Relief Suggestions
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Target className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Gratitude Generator
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Brain className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Reflection Prompt
            </Button>
          </CardContent>
        </Card>

        {/* Productivity Section */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Activity className="w-5 h-5 text-[#F4D03F]" />
              <span>Productivity</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Focus enhancement and time optimization
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Timer className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Focus Session Timer
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Activity className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Energy Level Assessment
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Calendar className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Calendar Optimizer
            </Button>
            <Button className="w-full justify-start bg-[rgba(244,208,63,0.1)] hover:bg-[rgba(244,208,63,0.2)] text-white border border-[rgba(244,208,63,0.2)]">
              <Zap className="w-4 h-4 mr-3 text-[#F4D03F]" />
              Distraction Blocker
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Actions Panel */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Clock className="w-5 h-5 text-[#F4D03F]" />
            <span>Recent AI Actions</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Your latest AI-assisted activities
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActions.map((action, index) => (
              <div key={index} className="glassmorphism-panel p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="text-white font-medium">{action.name}</h4>
                      <span className="text-[#6B7280] text-sm">{action.timestamp}</span>
                    </div>
                    <p className="text-[#B8BCC8] text-sm mb-2">{action.preview}</p>
                    <span className="text-[#F4D03F] text-xs">{action.result}</span>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <Button size="sm" variant="ghost" className="text-[#F4D03F] hover:text-[#F7DC6F] hover:bg-[rgba(244,208,63,0.1)]">
                      <Repeat className="w-4 h-4 mr-1" />
                      Repeat
                    </Button>
                    <Button size="sm" variant="link" className="text-[#B8BCC8] hover:text-[#F4D03F] p-0">
                      View Details
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Custom Actions Section */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Plus className="w-5 h-5 text-[#F4D03F]" />
            <span>Custom Actions</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Your personalized AI workflows
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button className="w-full border-2 border-dashed border-[rgba(244,208,63,0.3)] bg-transparent hover:bg-[rgba(244,208,63,0.05)] text-[#F4D03F]">
            <Plus className="w-4 h-4 mr-2" />
            Create Custom Action
          </Button>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {customActions.map((action, index) => (
              <div key={index} className="glassmorphism-panel p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="text-[#F4D03F]">{action.icon}</div>
                  <div>
                    <h4 className="text-white font-medium">{action.name}</h4>
                    <p className="text-[#B8BCC8] text-sm">{action.description}</p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button size="sm" className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                    <Play className="w-3 h-3 mr-1" />
                    Run
                  </Button>
                  <Button size="sm" variant="ghost" className="text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]">
                    <Edit className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}