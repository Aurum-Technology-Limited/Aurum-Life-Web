import { useState } from 'react';
import { Target, ChevronRight, Plus, Calendar, BarChart3, CheckCircle, Clock, ArrowLeft, Save, Zap, Edit } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Slider } from '../ui/slider';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';

export default function GoalPlanner() {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [goalData, setGoalData] = useState({
    vision: '',
    why: '',
    specific: '',
    measurable: '',
    achievable: 5,
    relevant: '',
    timebound: '',
    milestones: [],
    tasks: []
  });

  const [activeGoals] = useState([
    {
      id: 1,
      title: "Complete React Certification",
      progress: 65,
      daysRemaining: 12,
      status: "on-track"
    },
    {
      id: 2,
      title: "Launch Side Business",
      progress: 40,
      daysRemaining: 45,
      status: "at-risk"
    },
    {
      id: 3,
      title: "Read 24 Books This Year",
      progress: 83,
      daysRemaining: 89,
      status: "ahead"
    }
  ]);

  const templates = [
    { id: 'personal', name: 'Personal Development', description: 'Self-improvement and growth goals' },
    { id: 'professional', name: 'Professional', description: 'Career and skill advancement' },
    { id: 'health', name: 'Health & Fitness', description: 'Physical and mental wellness' },
    { id: 'financial', name: 'Financial', description: 'Money and investment goals' },
    { id: 'relationships', name: 'Relationships', description: 'Social and family connections' },
    { id: 'learning', name: 'Learning', description: 'Education and knowledge acquisition' }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'on-track': return 'text-[#10B981]';
      case 'at-risk': return 'text-[#F59E0B]';
      case 'ahead': return 'text-[#F4D03F]';
      default: return 'text-[#B8BCC8]';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'on-track': return <Badge className="bg-[#10B981] text-white">On Track</Badge>;
      case 'at-risk': return <Badge className="bg-[#F59E0B] text-white">At Risk</Badge>;
      case 'ahead': return <Badge className="bg-[#F4D03F] text-[#0B0D14]">Ahead</Badge>;
      default: return <Badge className="bg-[#B8BCC8] text-white">Unknown</Badge>;
    }
  };

  const nextStep = () => {
    if (currentStep < 5) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="vision" className="text-white text-lg">What do you want to achieve?</Label>
                <Textarea
                  id="vision"
                  placeholder="Describe your goal in detail..."
                  className="mt-2 min-h-[120px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                  value={goalData.vision}
                  onChange={(e) => setGoalData(prev => ({ ...prev, vision: e.target.value }))}
                />
              </div>
              
              <div>
                <Label htmlFor="why" className="text-white text-lg">Why is this important?</Label>
                <Textarea
                  id="why"
                  placeholder="What motivates you to achieve this goal?"
                  className="mt-2 min-h-[100px] bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                  value={goalData.why}
                  onChange={(e) => setGoalData(prev => ({ ...prev, why: e.target.value }))}
                />
              </div>
            </div>
            
            <Button 
              onClick={nextStep} 
              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              disabled={!goalData.vision || !goalData.why}
            >
              Next: Make it SMART
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        );
      
      case 2:
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-6">
              <div>
                <Label htmlFor="specific" className="text-white">Specific</Label>
                <Input
                  id="specific"
                  placeholder="Make your goal specific and clear"
                  className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                  value={goalData.specific}
                  onChange={(e) => setGoalData(prev => ({ ...prev, specific: e.target.value }))}
                />
              </div>
              
              <div>
                <Label htmlFor="measurable" className="text-white">Measurable</Label>
                <Input
                  id="measurable"
                  placeholder="How will you measure progress?"
                  className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
                  value={goalData.measurable}
                  onChange={(e) => setGoalData(prev => ({ ...prev, measurable: e.target.value }))}
                />
              </div>
              
              <div>
                <Label className="text-white">Achievable (Confidence Level: {goalData.achievable}/10)</Label>
                <Slider
                  value={[goalData.achievable]}
                  onValueChange={(value) => setGoalData(prev => ({ ...prev, achievable: value[0] }))}
                  max={10}
                  min={1}
                  step={1}
                  className="mt-2"
                />
              </div>
              
              <div>
                <Label htmlFor="relevant" className="text-white">Relevant (Pillar Connection)</Label>
                <Select value={goalData.relevant} onValueChange={(value) => setGoalData(prev => ({ ...prev, relevant: value }))}>
                  <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                    <SelectValue placeholder="Select related pillar" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                    <SelectItem value="health">Health & Wellness</SelectItem>
                    <SelectItem value="career">Career & Growth</SelectItem>
                    <SelectItem value="relationships">Relationships</SelectItem>
                    <SelectItem value="finances">Financial Security</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="timebound" className="text-white">Time-bound (Deadline)</Label>
                <Input
                  id="timebound"
                  type="date"
                  className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white [color-scheme:dark]"
                  value={goalData.timebound}
                  onChange={(e) => setGoalData(prev => ({ ...prev, timebound: e.target.value }))}
                />
              </div>
            </div>
            
            <div className="flex space-x-3">
              <Button onClick={prevStep} variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <Button onClick={nextStep} className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                Next: Break it Down
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        );
      
      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-white text-lg font-medium mb-4">AI Suggested Milestones</h3>
              <div className="space-y-3">
                {['Complete initial research phase', 'Build MVP version', 'Gather user feedback', 'Refine and optimize'].map((milestone, index) => (
                  <div key={index} className="glassmorphism-panel p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-white font-medium">{milestone}</h4>
                        <p className="text-[#B8BCC8] text-sm">Due: {new Date(Date.now() + (index + 1) * 30 * 24 * 60 * 60 * 1000).toLocaleDateString()}</p>
                      </div>
                      <Button size="sm" variant="ghost" className="text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]">
                        <Edit className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              
              <Button className="mt-4 border-2 border-dashed border-[rgba(244,208,63,0.3)] bg-transparent hover:bg-[rgba(244,208,63,0.05)] text-[#F4D03F] w-full">
                <Plus className="w-4 h-4 mr-2" />
                Add Custom Milestone
              </Button>
            </div>
            
            <div className="flex space-x-3">
              <Button onClick={prevStep} variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <Button onClick={nextStep} className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                Next: Create Tasks
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        );
      
      case 4:
        return (
          <div className="space-y-6">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white text-lg font-medium">Generated Tasks</h3>
                <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                  <Zap className="w-4 h-4 mr-2" />
                  Auto-generate Tasks
                </Button>
              </div>
              
              <div className="space-y-3">
                {['Research market opportunities', 'Create project timeline', 'Set up development environment', 'Design user interface mockups'].map((task, index) => (
                  <div key={index} className="glassmorphism-panel p-4">
                    <div className="flex items-center space-x-3">
                      <input type="checkbox" className="w-4 h-4 rounded border-[rgba(244,208,63,0.2)]" />
                      <span className="text-white flex-1">{task}</span>
                      <Select defaultValue="medium">
                        <SelectTrigger className="w-24 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                ))}
              </div>
              
              <Button className="mt-4 border-2 border-dashed border-[rgba(244,208,63,0.3)] bg-transparent hover:bg-[rgba(244,208,63,0.05)] text-[#F4D03F] w-full">
                <Plus className="w-4 h-4 mr-2" />
                Add Manual Task
              </Button>
            </div>
            
            <div className="flex space-x-3">
              <Button onClick={prevStep} variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <Button onClick={nextStep} className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                Next: Review
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        );
      
      case 5:
        return (
          <div className="space-y-6">
            <Card className="glassmorphism-card border-0">
              <CardHeader>
                <CardTitle className="text-white">Goal Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="text-[#F4D03F] font-medium">Vision</h4>
                  <p className="text-[#B8BCC8]">{goalData.vision || 'Complete a comprehensive React certification program'}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-[#F4D03F] font-medium">Deadline</h4>
                    <p className="text-[#B8BCC8]">{goalData.timebound || '2024-06-15'}</p>
                  </div>
                  <div>
                    <h4 className="text-[#F4D03F] font-medium">Confidence</h4>
                    <p className="text-[#B8BCC8]">{goalData.achievable}/10</p>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-[#F4D03F] font-medium">Milestones: 4</h4>
                  <h4 className="text-[#F4D03F] font-medium">Tasks: 12</h4>
                </div>
              </CardContent>
            </Card>
            
            <div className="flex space-x-3">
              <Button onClick={prevStep} variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                <Target className="w-4 h-4 mr-2" />
                Launch Goal
              </Button>
              <Button variant="outline" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                <Save className="w-4 h-4 mr-2" />
                Save as Draft
              </Button>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="aurum-gradient w-10 h-10 rounded-lg flex items-center justify-center">
            <Target className="w-6 h-6 text-[#0B0D14]" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Goal Planner</h1>
            <p className="text-[#B8BCC8]">Transform aspirations into actionable plans</p>
          </div>
        </div>
        
        <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
          <SelectTrigger className="w-48 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
            <SelectValue placeholder="Choose Template" />
          </SelectTrigger>
          <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
            {templates.map((template) => (
              <SelectItem key={template.id} value={template.id}>
                {template.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Goal Creation Wizard */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-white">Create New Goal</CardTitle>
            <div className="flex space-x-2">
              {[1, 2, 3, 4, 5].map((step) => (
                <div
                  key={step}
                  className={`w-3 h-3 rounded-full ${
                    step <= currentStep ? 'bg-[#F4D03F]' : 'bg-[rgba(244,208,63,0.2)]'
                  }`}
                />
              ))}
            </div>
          </div>
          <CardDescription className="text-[#B8BCC8]">
            Step {currentStep} of 5: {
              currentStep === 1 ? 'Vision' :
              currentStep === 2 ? 'SMART Goals' :
              currentStep === 3 ? 'Breakdown' :
              currentStep === 4 ? 'Task Generation' : 'Review & Launch'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Active Goals Dashboard */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white">Active Goals</CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Track progress on your current objectives
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {activeGoals.map((goal) => (
              <div key={goal.id} className="glassmorphism-panel p-4">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <h4 className="text-white font-medium">{goal.title}</h4>
                    {getStatusBadge(goal.status)}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-[#B8BCC8]">Progress</span>
                      <span className="text-[#F4D03F]">{goal.progress}%</span>
                    </div>
                    <Progress value={goal.progress} className="h-2" />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1 text-[#B8BCC8] text-sm">
                      <Clock className="w-4 h-4" />
                      <span>{goal.daysRemaining} days left</span>
                    </div>
                    <div className="flex space-x-2">
                      <Button size="sm" variant="ghost" className="text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]">
                        View
                      </Button>
                      <Button size="sm" className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                        Update
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Goal Templates Section */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white">Goal Templates</CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Start with proven frameworks for common goal types
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <div key={template.id} className="glassmorphism-panel p-4">
                <h4 className="text-white font-medium mb-2">{template.name}</h4>
                <p className="text-[#B8BCC8] text-sm mb-4">{template.description}</p>
                <Button 
                  size="sm" 
                  className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                  onClick={() => setSelectedTemplate(template.id)}
                >
                  Use Template
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}