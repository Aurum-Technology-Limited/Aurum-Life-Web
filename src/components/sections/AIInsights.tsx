import { useState } from 'react';
import { useAppStore } from '../../stores/basicAppStore';
import { Brain, RefreshCw, TrendingUp, Target, Activity, Lightbulb, X, ChevronDown, Smile, Clock, Zap } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Progress } from '../ui/progress';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function AIInsights() {
  const [timeRange, setTimeRange] = useState('this-week');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const setActiveSection = useAppStore(state => state.setActiveSection);
  const addNotification = useAppStore(state => state.addNotification);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 2000);
  };

  // Mock data for charts
  const emotionalData = [
    { day: 'Mon', mood: 7, energy: 6 },
    { day: 'Tue', mood: 8, energy: 8 },
    { day: 'Wed', mood: 6, energy: 5 },
    { day: 'Thu', mood: 9, energy: 7 },
    { day: 'Fri', mood: 8, energy: 9 },
    { day: 'Sat', mood: 9, energy: 8 },
    { day: 'Sun', mood: 7, energy: 6 },
  ];

  const focusData = [
    { name: 'Deep Work', value: 45, color: '#F4D03F' },
    { name: 'Meetings', value: 25, color: '#3B82F6' },
    { name: 'Admin', value: 15, color: '#10B981' },
    { name: 'Breaks', value: 15, color: '#F59E0B' },
  ];

  const recommendations = [
    {
      icon: <Clock className="w-5 h-5" />,
      title: "Optimize Morning Routine",
      description: "Your energy peaks at 9 AM. Schedule important tasks during this time.",
      action: "Adjust Schedule"
    },
    {
      icon: <Activity className="w-5 h-5" />,
      title: "Take More Breaks",
      description: "Adding 5-minute breaks every hour could boost your focus by 23%.",
      action: "Set Reminders"
    },
    {
      icon: <Target className="w-5 h-5" />,
      title: "Realign Health Goals",
      description: "Your fitness activities don't align with your wellness pillar priorities.",
      action: "Review Goals"
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <div className="aurum-gradient w-10 h-10 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-[#0B0D14]" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">My AI Insights</h1>
              <p className="text-[#B8BCC8]">Personalized intelligence for intentional living</p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-40 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="this-week">This Week</SelectItem>
              <SelectItem value="this-month">This Month</SelectItem>
              <SelectItem value="all-time">All Time</SelectItem>
            </SelectContent>
          </Select>
          
          <Button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Sync Insights
          </Button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Emotional Intelligence Card */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Smile className="w-5 h-5 text-[#F4D03F]" />
              <span>Emotional Patterns</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Your mood and energy trends over time
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={emotionalData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(244,208,63,0.1)" />
                  <XAxis dataKey="day" stroke="#B8BCC8" />
                  <YAxis stroke="#B8BCC8" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1A1D29', 
                      border: '1px solid rgba(244,208,63,0.2)',
                      borderRadius: '8px'
                    }}
                  />
                  <Line type="monotone" dataKey="mood" stroke="#F4D03F" strokeWidth={2} name="Mood" />
                  <Line type="monotone" dataKey="energy" stroke="#3B82F6" strokeWidth={2} name="Energy" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">😊</div>
                <p className="text-sm text-[#B8BCC8]">Current Mood</p>
              </div>
              <Button 
                variant="outline" 
                className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                onClick={() => {
                  addNotification({
                    type: 'info',
                    title: 'Detailed Analysis',
                    message: 'Opening comprehensive emotional pattern analysis...',
                    timestamp: new Date(),
                    isRead: false
                  });
                  console.log('Opening detailed emotional analysis');
                }}
              >
                View Detailed Analysis
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Productivity Insights Card */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-[#F4D03F]" />
              <span>Focus & Flow Analysis</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Your productivity patterns and peak performance times
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-center">
              <div className="relative w-32 h-32">
                <div className="absolute inset-0 rounded-full border-4 border-[rgba(244,208,63,0.2)]"></div>
                <div className="absolute inset-0 rounded-full border-4 border-[#F4D03F] border-t-transparent animate-pulse" style={{ clipPath: 'polygon(50% 0%, 100% 0%, 100% 75%, 50% 50%)' }}></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-[#F4D03F]">87%</div>
                    <div className="text-xs text-[#B8BCC8]">Focus Score</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-3">
              <h4 className="text-white font-medium">Peak Performance Times</h4>
              <div className="grid grid-cols-3 gap-2">
                <div className="glassmorphism-panel p-3 text-center">
                  <div className="text-[#F4D03F] font-medium">9:00 AM</div>
                  <div className="text-xs text-[#B8BCC8]">Morning Peak</div>
                </div>
                <div className="glassmorphism-panel p-3 text-center">
                  <div className="text-[#F4D03F] font-medium">2:00 PM</div>
                  <div className="text-xs text-[#B8BCC8]">Afternoon Peak</div>
                </div>
                <div className="glassmorphism-panel p-3 text-center">
                  <div className="text-[#F4D03F] font-medium">7:00 PM</div>
                  <div className="text-xs text-[#B8BCC8]">Evening Peak</div>
                </div>
              </div>
            </div>
            
            <Button 
              className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              onClick={() => {
                setActiveSection('today');
                addNotification({
                  type: 'success',
                  title: 'Schedule Optimization',
                  message: 'Redirecting to Today view for schedule optimization...',
                  timestamp: new Date(),
                  isRead: false
                });
              }}
            >
              Optimize Schedule
            </Button>
          </CardContent>
        </Card>

        {/* Goal Alignment Card */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Target className="w-5 h-5 text-[#F4D03F]" />
              <span>Strategic Alignment</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              How well your actions align with your life vision
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-[#B8BCC8]">Overall Alignment</span>
                <span className="text-[#F4D03F] font-medium">78%</span>
              </div>
              <Progress value={78} className="h-3 bg-[#1A1D29]" />
            </div>
            
            <div className="glassmorphism-panel p-4 border-l-4 border-[#F59E0B]">
              <h4 className="text-[#F59E0B] font-medium mb-2">Misaligned Activities</h4>
              <ul className="space-y-1 text-sm text-[#B8BCC8]">
                <li>• 3.5 hours of social media (Health pillar)</li>
                <li>• Skipped 2 workout sessions (Wellness goal)</li>
                <li>• Delayed learning project (Growth pillar)</li>
              </ul>
            </div>
            
            <Button 
              className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              onClick={() => {
                setActiveSection('goal-planner');
                addNotification({
                  type: 'info',
                  title: 'Goal Realignment',
                  message: 'Opening Goal Planner for strategic realignment...',
                  timestamp: new Date(),
                  isRead: false
                });
              }}
            >
              Realign Goals
            </Button>
          </CardContent>
        </Card>

        {/* Behavior Patterns Card */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Activity className="w-5 h-5 text-[#F4D03F]" />
              <span>Behavioral Insights</span>
            </CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Your habit patterns and strength indicators
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-white">Morning Meditation</span>
                <div className="flex items-center space-x-2">
                  <Progress value={85} className="w-20 h-2" />
                  <span className="text-[#F4D03F] text-sm">85%</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-white">Daily Exercise</span>
                <div className="flex items-center space-x-2">
                  <Progress value={65} className="w-20 h-2" />
                  <span className="text-[#F4D03F] text-sm">65%</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-white">Evening Reading</span>
                <div className="flex items-center space-x-2">
                  <Progress value={92} className="w-20 h-2" />
                  <span className="text-[#F4D03F] text-sm">92%</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-white">Healthy Eating</span>
                <div className="flex items-center space-x-2">
                  <Progress value={78} className="w-20 h-2" />
                  <span className="text-[#F4D03F] text-sm">78%</span>
                </div>
              </div>
            </div>
            
            <Button 
              variant="outline" 
              className="w-full border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
              onClick={() => {
                addNotification({
                  type: 'info',
                  title: 'Habit Builder',
                  message: 'Opening habit creation workflow...',
                  timestamp: new Date(),
                  isRead: false
                });
                console.log('Opening habit builder');
              }}
            >
              <span className="mr-2">+</span>
              Build New Habit
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* AI Recommendations Section */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Lightbulb className="w-5 h-5 text-[#F4D03F]" />
            <span>Personalized Recommendations</span>
          </CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            AI-powered suggestions to optimize your intentional living
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recommendations.map((rec, index) => (
              <div key={index} className="glassmorphism-panel p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="text-[#F4D03F]">{rec.icon}</div>
                    <h4 className="text-white font-medium">{rec.title}</h4>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="text-[#6B7280] hover:text-[#F4D03F] h-6 w-6"
                    onClick={() => {
                      addNotification({
                        type: 'info',
                        title: 'Recommendation Dismissed',
                        message: `Dismissed recommendation: ${rec.title}`,
                        timestamp: new Date(),
                        isRead: false
                      });
                    }}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <p className="text-[#B8BCC8] text-sm mb-4">{rec.description}</p>
                <div className="flex space-x-2">
                  <Button 
                    size="sm" 
                    className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                    onClick={() => {
                      addNotification({
                        type: 'success',
                        title: 'Action Triggered',
                        message: `Executing: ${rec.action} for ${rec.title}`,
                        timestamp: new Date(),
                        isRead: false
                      });
                      
                      // Handle specific actions
                      if (rec.action === 'Adjust Schedule') {
                        setActiveSection('today');
                      } else if (rec.action === 'Review Goals') {
                        setActiveSection('goal-planner');
                      }
                    }}
                  >
                    {rec.action}
                  </Button>
                  <Button 
                    variant="link" 
                    size="sm" 
                    className="text-[#F4D03F] hover:text-[#F7DC6F] p-0"
                    onClick={() => {
                      addNotification({
                        type: 'info',
                        title: 'Learning Resource',
                        message: `Opening detailed information about: ${rec.title}`,
                        timestamp: new Date(),
                        isRead: false
                      });
                    }}
                  >
                    Learn More
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Bottom Actions */}
      <div className="flex items-center justify-center space-x-4">
        <Button 
          className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
          onClick={() => {
            handleRefresh();
            addNotification({
              type: 'success',
              title: 'Insights Generated',
              message: 'New AI insights have been generated based on your latest data.',
              timestamp: new Date(),
              isRead: false
            });
          }}
        >
          Generate New Insights
        </Button>
        <Button 
          variant="outline" 
          className="border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
          onClick={() => {
            addNotification({
              type: 'success',
              title: 'Report Exported',
              message: 'AI insights report has been exported and downloaded.',
              timestamp: new Date(),
              isRead: false
            });
            console.log('Exporting AI insights report...');
          }}
        >
          Export Report
        </Button>
        <Button 
          variant="ghost" 
          className="text-[#B8BCC8] hover:text-[#F4D03F]"
          onClick={() => {
            addNotification({
              type: 'info',
              title: 'Review Scheduled',
              message: 'AI insights review has been scheduled for next week.',
              timestamp: new Date(),
              isRead: false
            });
            console.log('Scheduling AI insights review...');
          }}
        >
          Schedule Review
        </Button>
      </div>
    </div>
  );
}