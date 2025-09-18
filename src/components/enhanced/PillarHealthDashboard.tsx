import { useState } from 'react';
import { motion } from 'motion/react';
import { TrendingUp, TrendingDown, Minus, Target, Clock, Flame, Award } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadialBarChart, RadialBar, Cell } from 'recharts';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';

interface PillarHealthMetrics {
  pillar: string;
  health: number;
  trend: 'up' | 'down' | 'stable';
  timeProgress: number;
  streak: number;
  weeklyGoal: number;
  weeklyActual: number;
}

export default function PillarHealthDashboard() {
  const { pillars, getPillarHealthTrend, achievements } = useEnhancedFeaturesStore();
  const [selectedTimeframe, setSelectedTimeframe] = useState<'week' | 'month' | 'quarter'>('week');

  // Calculate metrics for each pillar
  const pillarMetrics: PillarHealthMetrics[] = pillars.map(pillar => {
    const trend = getPillarHealthTrend(pillar.id, 7);
    const trendDirection = trend.length >= 2 
      ? trend[trend.length - 1] > trend[trend.length - 2] ? 'up' 
      : trend[trend.length - 1] < trend[trend.length - 2] ? 'down' 
      : 'stable'
      : 'stable';

    return {
      pillar: pillar.name,
      health: pillar.healthScore,
      trend: trendDirection,
      timeProgress: pillar.weeklyTimeTarget > 0 ? (pillar.weeklyTimeActual / pillar.weeklyTimeTarget) * 100 : 0,
      streak: pillar.streak,
      weeklyGoal: pillar.weeklyTimeTarget,
      weeklyActual: pillar.weeklyTimeActual,
    };
  });

  // Overall health score
  const overallHealth = pillars.length > 0 
    ? Math.round(pillars.reduce((sum, pillar) => sum + pillar.healthScore, 0) / pillars.length)
    : 0;

  // Generate chart data
  const chartData = Array.from({ length: 30 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (29 - i));
    return {
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      overall: Math.max(0, overallHealth + Math.random() * 20 - 10),
      ...pillars.reduce((acc, pillar) => {
        acc[pillar.name] = Math.max(0, pillar.healthScore + Math.random() * 15 - 7.5);
        return acc;
      }, {} as Record<string, number>)
    };
  });

  const getHealthColor = (health: number) => {
    if (health >= 80) return '#10B981'; // green
    if (health >= 60) return '#F59E0B'; // yellow
    return '#EF4444'; // red
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-400" />;
      default:
        return <Minus className="w-4 h-4 text-[#B8BCC8]" />;
    }
  };

  // Recent achievements
  const recentAchievements = achievements.slice(0, 3);

  return (
    <div className="space-y-6">
      {/* Overall Health Score */}
      <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Target className="w-5 h-5 text-[#F4D03F]" />
            <span>Life Balance Overview</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Overall Health */}
            <div className="text-center">
              <div className="relative w-32 h-32 mx-auto mb-4">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" data={[{ value: overallHealth }]}>
                    <RadialBar 
                      dataKey="value" 
                      cornerRadius={10} 
                      fill={getHealthColor(overallHealth)}
                    />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white">{overallHealth}</div>
                    <div className="text-xs text-[#B8BCC8]">Health Score</div>
                  </div>
                </div>
              </div>
              <div className="text-sm text-[#B8BCC8]">Overall Life Balance</div>
            </div>

            {/* Total Time This Week */}
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Clock className="w-8 h-8 text-[#F4D03F]" />
              </div>
              <div className="text-3xl font-bold text-white mb-1">
                {pillars.reduce((sum, pillar) => sum + pillar.weeklyTimeActual, 0).toFixed(1)}h
              </div>
              <div className="text-sm text-[#B8BCC8]">Total Time This Week</div>
              <div className="text-xs text-[#6B7280] mt-1">
                Goal: {pillars.reduce((sum, pillar) => sum + pillar.weeklyTimeTarget, 0)}h
              </div>
            </div>

            {/* Active Streaks */}
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Flame className="w-8 h-8 text-orange-400" />
              </div>
              <div className="text-3xl font-bold text-white mb-1">
                {Math.max(...pillars.map(p => p.streak), 0)}
              </div>
              <div className="text-sm text-[#B8BCC8]">Best Streak</div>
              <div className="text-xs text-[#6B7280] mt-1">
                {pillars.filter(p => p.streak > 0).length} active streaks
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pillar Health Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {pillarMetrics.map((metric, index) => (
          <motion.div
            key={metric.pillar}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white hover:border-[rgba(244,208,63,0.3)] transition-all duration-200">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center justify-between text-lg">
                  <span className="text-white truncate">{metric.pillar}</span>
                  {getTrendIcon(metric.trend)}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Health Score */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-[#B8BCC8]">Health Score</span>
                    <span className="text-lg font-semibold" style={{ color: getHealthColor(metric.health) }}>
                      {metric.health}%
                    </span>
                  </div>
                  <Progress 
                    value={metric.health} 
                    className="h-2"
                    style={{ 
                      backgroundColor: 'rgba(244,208,63,0.1)',
                    }}
                  />
                </div>

                {/* Time Progress */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-[#B8BCC8]">Weekly Time</span>
                    <span className="text-sm text-white">
                      {metric.weeklyActual}h / {metric.weeklyGoal}h
                    </span>
                  </div>
                  <Progress 
                    value={Math.min(100, metric.timeProgress)} 
                    className="h-2"
                    style={{ 
                      backgroundColor: 'rgba(244,208,63,0.1)',
                    }}
                  />
                </div>

                {/* Streak */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Flame className="w-4 h-4 text-orange-400" />
                    <span className="text-sm text-[#B8BCC8]">Streak</span>
                  </div>
                  <Badge 
                    variant="outline" 
                    className={`border-orange-400 text-orange-400 ${metric.streak === 0 ? 'opacity-50' : ''}`}
                  >
                    {metric.streak} days
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Health Trends Chart */}
      <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-[#F4D03F]" />
              <span>Health Trends</span>
            </div>
            <Tabs value={selectedTimeframe} onValueChange={(value) => setSelectedTimeframe(value as any)}>
              <TabsList className="bg-[#0B0D14] border-[rgba(244,208,63,0.2)]">
                <TabsTrigger value="week" className="text-[#B8BCC8] data-[state=active]:text-[#F4D03F]">Week</TabsTrigger>
                <TabsTrigger value="month" className="text-[#B8BCC8] data-[state=active]:text-[#F4D03F]">Month</TabsTrigger>
                <TabsTrigger value="quarter" className="text-[#B8BCC8] data-[state=active]:text-[#F4D03F]">Quarter</TabsTrigger>
              </TabsList>
            </Tabs>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(244,208,63,0.1)" />
                <XAxis 
                  dataKey="date" 
                  stroke="#B8BCC8" 
                  fontSize={12}
                />
                <YAxis 
                  stroke="#B8BCC8" 
                  fontSize={12}
                  domain={[0, 100]}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1A1D29', 
                    border: '1px solid rgba(244,208,63,0.2)',
                    borderRadius: '8px',
                    color: '#FFFFFF'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="overall" 
                  stroke="#F4D03F" 
                  strokeWidth={3}
                  dot={{ fill: '#F4D03F', strokeWidth: 2, r: 4 }}
                  name="Overall Health"
                />
                {pillars.slice(0, 3).map((pillar, index) => (
                  <Line
                    key={pillar.id}
                    type="monotone"
                    dataKey={pillar.name}
                    stroke={['#10B981', '#3B82F6', '#EF4444'][index]}
                    strokeWidth={2}
                    dot={{ strokeWidth: 2, r: 3 }}
                    name={pillar.name}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Recent Achievements */}
      {recentAchievements.length > 0 && (
        <Card className="glassmorphism-card border-0 bg-[#1A1D29] text-white">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-[#F4D03F]" />
              <span>Recent Achievements</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentAchievements.map((achievement) => (
                <motion.div
                  key={achievement.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center space-x-3 p-3 glassmorphism-panel rounded-lg"
                >
                  <div className="text-2xl">{achievement.icon}</div>
                  <div className="flex-1">
                    <div className="font-semibold text-white">{achievement.title}</div>
                    <div className="text-sm text-[#B8BCC8]">{achievement.description}</div>
                  </div>
                  <div className="text-xs text-[#6B7280]">
                    {new Date(achievement.earnedAt).toLocaleDateString()}
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}