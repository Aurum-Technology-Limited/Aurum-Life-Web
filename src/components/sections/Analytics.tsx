import { useState } from 'react';
import { BarChart3, Download, TrendingUp, Clock, Target, Flame, Activity, Calendar, Filter } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Progress } from '../ui/progress';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { DatePickerWithRange } from '../ui/date-picker-with-range';

export default function Analytics() {
  const [dateRange, setDateRange] = useState({ from: new Date(2024, 0, 1), to: new Date() });
  const [selectedPillar, setSelectedPillar] = useState('all');

  // Mock data for charts
  const alignmentData = [
    { week: 'W1', alignment: 65, health: 70, career: 60, relationships: 65, finance: 60 },
    { week: 'W2', alignment: 72, health: 75, career: 68, relationships: 70, finance: 65 },
    { week: 'W3', alignment: 68, health: 65, career: 75, relationships: 68, finance: 70 },
    { week: 'W4', alignment: 78, health: 80, career: 78, relationships: 75, finance: 78 },
    { week: 'W5', alignment: 82, health: 85, career: 80, relationships: 80, finance: 82 },
    { week: 'W6', alignment: 85, health: 88, career: 82, relationships: 85, finance: 85 }
  ];

  const timeDistributionData = [
    { name: 'Deep Work', value: 35, color: '#F4D03F' },
    { name: 'Meetings', value: 25, color: '#3B82F6' },
    { name: 'Learning', value: 15, color: '#10B981' },
    { name: 'Admin', value: 12, color: '#F59E0B' },
    { name: 'Breaks', value: 13, color: '#EF4444' }
  ];

  const productivityHeatmapData = [
    { day: 'Mon', hour: 9, value: 90 },
    { day: 'Mon', hour: 14, value: 75 },
    { day: 'Tue', hour: 10, value: 85 },
    { day: 'Wed', hour: 11, value: 95 },
    { day: 'Thu', hour: 9, value: 88 },
    { day: 'Fri', hour: 15, value: 70 }
  ];

  const moodEnergyData = [
    { day: 'Mon', mood: 7, energy: 8 },
    { day: 'Tue', mood: 8, energy: 7 },
    { day: 'Wed', mood: 6, energy: 6 },
    { day: 'Thu', mood: 9, energy: 8 },
    { day: 'Fri', mood: 8, energy: 9 },
    { day: 'Sat', mood: 9, energy: 7 },
    { day: 'Sun', mood: 7, energy: 6 }
  ];

  const goalProgressData = [
    { goal: 'React Certification', completed: 12, total: 15, successRate: 80 },
    { goal: 'Fitness Journey', completed: 28, total: 30, successRate: 93 },
    { goal: 'Reading Challenge', completed: 18, total: 24, successRate: 75 },
    { goal: 'Side Project', completed: 6, total: 10, successRate: 60 }
  ];

  const habitData = [
    { habit: 'Morning Meditation', streak: 23, successRate: 85 },
    { habit: 'Daily Exercise', streak: 12, successRate: 70 },
    { habit: 'Evening Reading', streak: 31, successRate: 92 },
    { habit: 'Healthy Eating', streak: 8, successRate: 65 }
  ];

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="aurum-gradient w-10 h-10 rounded-lg flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-[#0B0D14]" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Analytics Dashboard</h1>
            <p className="text-[#B8BCC8]">Data-driven insights for intentional living</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <DatePickerWithRange 
            date={dateRange} 
            setDate={setDateRange}
            className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white"
          />
          <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[#B8BCC8] text-sm">Alignment Score</p>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl font-bold text-[#F4D03F]">85%</span>
                  <TrendingUp className="w-4 h-4 text-[#10B981]" />
                </div>
              </div>
              <Target className="w-8 h-8 text-[#F4D03F]" />
            </div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[#B8BCC8] text-sm">Focus Hours</p>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl font-bold text-white">6.5h</span>
                  <span className="text-[#10B981] text-sm">+12%</span>
                </div>
              </div>
              <Clock className="w-8 h-8 text-[#3B82F6]" />
            </div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[#B8BCC8] text-sm">Goals Completed</p>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl font-bold text-white">12/15</span>
                  <span className="text-[#F4D03F] text-sm">80%</span>
                </div>
              </div>
              <Target className="w-8 h-8 text-[#10B981]" />
            </div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[#B8BCC8] text-sm">Streak Days</p>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl font-bold text-white">31</span>
                  <Flame className="w-4 h-4 text-[#F59E0B]" />
                </div>
              </div>
              <Flame className="w-8 h-8 text-[#F59E0B]" />
            </div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[#B8BCC8] text-sm">Energy Level</p>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl font-bold text-white">7.8</span>
                  <span className="text-2xl">⚡</span>
                </div>
              </div>
              <Activity className="w-8 h-8 text-[#F4D03F]" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alignment Trend Chart */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-white">Alignment Trend</CardTitle>
                <CardDescription className="text-[#B8BCC8]">
                  Track how well your actions align with your values
                </CardDescription>
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                  Health
                </Button>
                <Button variant="outline" size="sm" className="border-[rgba(244,208,63,0.2)] text-[#F4D03F]">
                  Career
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={alignmentData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(244,208,63,0.1)" />
                  <XAxis dataKey="week" stroke="#B8BCC8" />
                  <YAxis stroke="#B8BCC8" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1A1D29', 
                      border: '1px solid rgba(244,208,63,0.2)',
                      borderRadius: '8px'
                    }}
                  />
                  <Line type="monotone" dataKey="alignment" stroke="#F4D03F" strokeWidth={3} name="Overall" />
                  <Line type="monotone" dataKey="health" stroke="#10B981" strokeWidth={2} name="Health" />
                  <Line type="monotone" dataKey="career" stroke="#3B82F6" strokeWidth={2} name="Career" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <Button className="mt-4 w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
              View Details
            </Button>
          </CardContent>
        </Card>

        {/* Time Distribution Chart */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white">Time Distribution</CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              How you spend your focused time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={timeDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {timeDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-4">
              {timeDistributionData.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: item.color }}></div>
                  <span className="text-[#B8BCC8] text-sm">{item.name}</span>
                  <span className="text-white text-sm">{item.value}%</span>
                </div>
              ))}
            </div>
            <Button className="mt-4 w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
              Optimize Time
            </Button>
          </CardContent>
        </Card>

        {/* Mood & Energy Tracking */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white">Mood & Energy Tracking</CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Daily emotional and energy patterns
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={moodEnergyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(244,208,63,0.1)" />
                  <XAxis dataKey="day" stroke="#B8BCC8" />
                  <YAxis stroke="#B8BCC8" domain={[0, 10]} />
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
            <div className="mt-4 glassmorphism-panel p-3">
              <p className="text-[#B8BCC8] text-sm">
                <strong className="text-[#F4D03F]">Insight:</strong> Your mood and energy are highest on Thursdays and Saturdays. 
                Consider scheduling important tasks during these peak periods.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Productivity Heatmap */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white">Productivity Heatmap</CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Peak performance times throughout the week
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-7 gap-2 mb-4">
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                <div key={day} className="text-center text-[#B8BCC8] text-sm p-2">
                  {day}
                </div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-2">
              {Array.from({ length: 7 * 12 }, (_, i) => {
                const intensity = Math.random();
                return (
                  <div
                    key={i}
                    className="aspect-square rounded"
                    style={{
                      backgroundColor: `rgba(244, 208, 63, ${intensity * 0.8 + 0.1})`
                    }}
                  />
                );
              })}
            </div>
            <div className="flex items-center justify-between mt-4">
              <span className="text-[#B8BCC8] text-sm">Less</span>
              <div className="flex space-x-1">
                {[0.1, 0.3, 0.5, 0.7, 0.9].map((opacity, i) => (
                  <div
                    key={i}
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: `rgba(244, 208, 63, ${opacity})` }}
                  />
                ))}
              </div>
              <span className="text-[#B8BCC8] text-sm">More</span>
            </div>
            <Button className="mt-4 w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
              Find Patterns
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Goal Progress Section */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white">Goal Progress</CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Performance across active goals
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {goalProgressData.map((goal, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-white text-sm">{goal.goal}</span>
                  <span className="text-[#F4D03F] text-sm">{goal.completed}/{goal.total}</span>
                </div>
                <Progress value={goal.successRate} className="h-2" />
                <span className="text-[#B8BCC8] text-xs">{goal.successRate}% success rate</span>
              </div>
            ))}
            <Button className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] mt-4">
              Goal Performance Report
            </Button>
          </CardContent>
        </Card>

        {/* Habit Tracking Section */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white">Habit Tracking</CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Daily habit consistency and streaks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {habitData.map((habit, index) => (
              <div key={index} className="glassmorphism-panel p-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-white text-sm">{habit.habit}</span>
                  <div className="flex items-center space-x-1">
                    <Flame className="w-4 h-4 text-[#F59E0B]" />
                    <span className="text-[#F59E0B] text-sm">{habit.streak}</span>
                  </div>
                </div>
                <Progress value={habit.successRate} className="h-2" />
                <span className="text-[#B8BCC8] text-xs">{habit.successRate}% consistency</span>
              </div>
            ))}
            <Button className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] mt-4">
              Habit Optimization
            </Button>
          </CardContent>
        </Card>

        {/* Focus Analysis Section */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="text-white">Focus Analysis</CardTitle>
            <CardDescription className="text-[#B8BCC8]">
              Deep work patterns and distractions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="glassmorphism-panel p-4">
              <h4 className="text-[#F4D03F] font-medium mb-2">Peak Focus Times</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-[#B8BCC8] text-sm">9:00 - 11:00 AM</span>
                  <span className="text-[#10B981] text-sm">92% focus</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#B8BCC8] text-sm">2:00 - 4:00 PM</span>
                  <span className="text-[#F4D03F] text-sm">87% focus</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#B8BCC8] text-sm">7:00 - 9:00 PM</span>
                  <span className="text-[#F59E0B] text-sm">74% focus</span>
                </div>
              </div>
            </div>
            
            <div className="glassmorphism-panel p-4">
              <h4 className="text-[#F4D03F] font-medium mb-2">Top Distractions</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-[#B8BCC8]">Social Media</span>
                  <span className="text-[#EF4444]">23 interruptions</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#B8BCC8]">Email</span>
                  <span className="text-[#F59E0B]">15 interruptions</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#B8BCC8]">Meetings</span>
                  <span className="text-[#3B82F6]">8 interruptions</span>
                </div>
              </div>
            </div>
            
            <Button className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
              Focus Improvement Plan
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Report Generation */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="text-white">Report Generation</CardTitle>
          <CardDescription className="text-[#B8BCC8]">
            Create comprehensive analytics reports
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="report-type" className="text-white">Report Type</label>
              <Select>
                <SelectTrigger className="mt-2 bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectValue placeholder="Select report type" />
                </SelectTrigger>
                <SelectContent className="bg-[#1A1D29] border-[rgba(244,208,63,0.2)] text-white">
                  <SelectItem value="weekly">Weekly Summary</SelectItem>
                  <SelectItem value="monthly">Monthly Report</SelectItem>
                  <SelectItem value="quarterly">Quarterly Analysis</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="md:col-span-2">
              <label className="text-white">Include Sections</label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {['Goal Progress', 'Habit Analysis', 'Time Distribution', 'Focus Patterns', 'Mood Trends', 'Recommendations'].map((section) => (
                  <div key={section} className="flex items-center space-x-2">
                    <input type="checkbox" defaultChecked className="w-4 h-4 rounded border-[rgba(244,208,63,0.2)]" />
                    <span className="text-[#B8BCC8] text-sm">{section}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="flex space-x-4">
            <Button className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
              Generate Report
            </Button>
            <Button variant="link" className="text-[#F4D03F] hover:text-[#F7DC6F]">
              Schedule Automated Report
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}