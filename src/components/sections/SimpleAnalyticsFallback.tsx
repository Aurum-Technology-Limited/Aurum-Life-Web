import { BarChart3, TrendingUp, Clock, Target, Flame, Activity, RefreshCw } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Progress } from '../ui/progress';

export default function SimpleAnalyticsFallback() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-3">
          <div className="aurum-gradient w-10 h-10 rounded-lg flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-[#0B0D14]" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Analytics Dashboard</h1>
            <p className="text-[#B8BCC8]">Data-driven insights for intentional living</p>
          </div>
        </div>
        <Button 
          className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
          onClick={() => window.location.reload()}
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Simple Key Metrics */}
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

      {/* Simple Progress Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <h3 className="text-white text-lg font-semibold mb-4">Goal Progress</h3>
            <div className="space-y-4">
              {[
                { name: 'React Certification', progress: 80 },
                { name: 'Fitness Journey', progress: 93 },
                { name: 'Reading Challenge', progress: 75 },
                { name: 'Side Project', progress: 60 }
              ].map((goal, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-white text-sm">{goal.name}</span>
                    <span className="text-[#F4D03F] text-sm">{goal.progress}%</span>
                  </div>
                  <Progress value={goal.progress} className="h-2" />
                </div>
              ))}
            </div>
            <Button 
              className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] mt-4"
              onClick={() => window.location.reload()}
            >
              View Full Analytics
            </Button>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <h3 className="text-white text-lg font-semibold mb-4">Habit Tracking</h3>
            <div className="space-y-4">
              {[
                { name: 'Morning Meditation', streak: 23, success: 85 },
                { name: 'Daily Exercise', streak: 12, success: 70 },
                { name: 'Evening Reading', streak: 31, success: 92 },
                { name: 'Healthy Eating', streak: 8, success: 65 }
              ].map((habit, index) => (
                <div key={index} className="glassmorphism-panel p-3">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-white text-sm">{habit.name}</span>
                    <div className="flex items-center space-x-1">
                      <Flame className="w-4 h-4 text-[#F59E0B]" />
                      <span className="text-[#F59E0B] text-sm">{habit.streak}</span>
                    </div>
                  </div>
                  <Progress value={habit.success} className="h-2" />
                  <span className="text-[#B8BCC8] text-xs">{habit.success}% consistency</span>
                </div>
              ))}
            </div>
            <Button 
              className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] mt-4"
              onClick={() => window.location.reload()}
            >
              View All Habits
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Loading Message */}
      <Card className="glassmorphism-card border-0">
        <CardContent className="p-8 text-center">
          <div className="space-y-4">
            <BarChart3 className="w-16 h-16 text-[#F4D03F] mx-auto opacity-50" />
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Analytics Loading
              </h3>
              <p className="text-[#B8BCC8] mb-4">
                The full analytics dashboard is taking longer than expected to load. 
                This simplified view shows your key metrics.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button
                  onClick={() => window.location.reload()}
                  className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try Full Dashboard
                </Button>
                <Button
                  variant="outline"
                  className="border-[#F4D03F] text-[#F4D03F] hover:bg-[#F4D03F] hover:text-[#0B0D14]"
                  onClick={() => {
                    // Navigate to a simpler section
                    const appStore = { setActiveSection: (section: string) => console.log('Navigate to', section) };
                    // This would normally use the actual store
                  }}
                >
                  View Dashboard Instead
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}