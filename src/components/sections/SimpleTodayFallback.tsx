import { Sun, CheckCircle2, Clock, Plus, Target, Calendar } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';

const SimpleTodayFallback = () => {
  const currentDate = new Date();
  const dateString = currentDate.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <Sun className="w-8 h-8 text-[#F4D03F]" />
          <h1 className="text-3xl font-bold text-white">Today</h1>
        </div>
        <p className="text-[#B8BCC8]">{dateString}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Today's Focus */}
        <div className="space-y-6">
          
          {/* Progress Overview */}
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-white">Daily Progress</CardTitle>
                  <CardDescription className="text-[#B8BCC8]">
                    Your focus for today aligned with strategic goals
                  </CardDescription>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-[#F4D03F]">25%</div>
                  <div className="text-sm text-[#B8BCC8]">1/4 completed</div>
                </div>
              </div>
              <Progress value={25} className="h-3" />
            </CardHeader>
          </Card>

          {/* Today's Tasks */}
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white">Priority Tasks</CardTitle>
                <Button size="sm" className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Task
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-center py-8">
                <CheckCircle2 className="w-12 h-12 text-[#F4D03F] mx-auto mb-4" />
                <p className="text-[#B8BCC8] mb-4">
                  No tasks scheduled for today
                </p>
                <Button 
                  size="sm" 
                  className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Task
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Simple Calendar Preview */}
        <div className="space-y-6">
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Calendar className="w-5 h-5 mr-2 text-[#F4D03F]" />
                Today's Schedule
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-center py-8">
                <Calendar className="w-12 h-12 text-[#F4D03F] mx-auto mb-4" />
                <p className="text-[#B8BCC8] mb-4">
                  Your daily schedule and time blocks will appear here
                </p>
                <Button 
                  size="sm" 
                  className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Time Block
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SimpleTodayFallback;