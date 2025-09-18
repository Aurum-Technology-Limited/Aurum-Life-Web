import React from 'react';
import { TrendingUp, Calendar, Heart, Target, Zap, BookOpen, Award, Flame, Brain } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import { useJournalStore } from '../../stores/journalStore';

export default function JournalAnalytics() {
  const { 
    getStats, 
    getMoodTrend, 
    getWordCountTrend,
    insights,
    dismissInsight 
  } = useJournalStore();

  const stats = getStats();
  const moodTrend = getMoodTrend(30);
  const wordCountTrend = getWordCountTrend(30);

  // Process mood trend data for chart
  const moodChartData = moodTrend.reduce((acc, entry) => {
    const existing = acc.find(item => item.date === entry.date);
    if (existing) {
      existing.totalEntries++;
      existing.averageEnergy = (existing.averageEnergy + entry.energy) / existing.totalEntries;
    } else {
      acc.push({
        date: entry.date,
        totalEntries: 1,
        averageEnergy: entry.energy,
        mood: entry.mood
      });
    }
    return acc;
  }, [] as any[]);

  // Get mood color for visualization
  const getMoodColor = (mood: string) => {
    const moodColors = {
      excited: '#f97316',
      positive: '#10b981',
      neutral: '#6b7280',
      thoughtful: '#8b5cf6',
      challenging: '#ef4444',
      grateful: '#ec4899',
      motivated: '#3b82f6',
      accomplished: '#f59e0b',
      peaceful: '#14b8a6',
      energized: '#059669'
    };
    return moodColors[mood as keyof typeof moodColors] || '#6b7280';
  };

  const activeInsights = insights.filter(insight => !insight.dismissed).slice(0, 3);

  return (
    <div className="space-y-6">
      {/* Key Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="glassmorphism-card border-0">
          <CardContent className="p-4 text-center">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-2 rounded-full bg-primary/10">
              <BookOpen className="w-6 h-6 text-primary" />
            </div>
            <div className="text-2xl font-bold text-foreground">{stats.totalEntries}</div>
            <div className="text-sm text-muted-foreground">Total Entries</div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-4 text-center">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-2 rounded-full bg-orange-500/10">
              <Flame className="w-6 h-6 text-orange-400" />
            </div>
            <div className="text-2xl font-bold text-foreground">{stats.currentStreak}</div>
            <div className="text-sm text-muted-foreground">Day Streak</div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-4 text-center">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-2 rounded-full bg-blue-500/10">
              <TrendingUp className="w-6 h-6 text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-foreground">
              {Math.round(stats.averageWordsPerEntry)}
            </div>
            <div className="text-sm text-muted-foreground">Avg Words</div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-4 text-center">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-2 rounded-full bg-green-500/10">
              <Calendar className="w-6 h-6 text-green-400" />
            </div>
            <div className="text-2xl font-bold text-foreground">{stats.entriesThisMonth}</div>
            <div className="text-sm text-muted-foreground">This Month</div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Energy Trend */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="w-5 h-5 text-primary" />
              <span>Energy Levels (30 Days)</span>
            </CardTitle>
            <CardDescription>Track your energy patterns over time</CardDescription>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={moodChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(244,208,63,0.1)" />
                <XAxis 
                  dataKey="date" 
                  stroke="#B8BCC8"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis 
                  stroke="#B8BCC8"
                  tick={{ fontSize: 12 }}
                  domain={[1, 5]}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(26, 29, 41, 0.9)', 
                    border: '1px solid rgba(244,208,63,0.2)',
                    borderRadius: '8px',
                    color: '#FFFFFF'
                  }}
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  formatter={(value) => [`${value}/5`, 'Energy Level']}
                />
                <Area 
                  type="monotone" 
                  dataKey="averageEnergy" 
                  stroke="#F4D03F" 
                  fill="rgba(244,208,63,0.2)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Word Count Trend */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BookOpen className="w-5 h-5 text-primary" />
              <span>Writing Volume (30 Days)</span>
            </CardTitle>
            <CardDescription>Your daily word count progress</CardDescription>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={wordCountTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(244,208,63,0.1)" />
                <XAxis 
                  dataKey="date" 
                  stroke="#B8BCC8"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis 
                  stroke="#B8BCC8"
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(26, 29, 41, 0.9)', 
                    border: '1px solid rgba(244,208,63,0.2)',
                    borderRadius: '8px',
                    color: '#FFFFFF'
                  }}
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  formatter={(value) => [`${value}`, 'Words']}
                />
                <Bar 
                  dataKey="wordCount" 
                  fill="rgba(244,208,63,0.3)"
                  stroke="#F4D03F"
                  strokeWidth={1}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Insights and Patterns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI Insights */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="w-5 h-5 text-primary" />
              <span>AI Insights</span>
            </CardTitle>
            <CardDescription>Patterns and wisdom from your reflections</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {activeInsights.length > 0 ? (
              activeInsights.map((insight) => (
                <div 
                  key={insight.id} 
                  className="p-4 rounded-lg glassmorphism-subtle border border-border"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-foreground">{insight.title}</h4>
                    <button
                      onClick={() => dismissInsight(insight.id)}
                      className="text-muted-foreground hover:text-foreground text-xs"
                    >
                      ×
                    </button>
                  </div>
                  <p className="text-sm text-muted-foreground">{insight.description}</p>
                  {insight.actionable && (
                    <Badge variant="secondary" className="mt-2 text-xs">
                      Actionable
                    </Badge>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Brain className="w-12 h-12 mx-auto mb-4 text-muted-foreground/30" />
                <p className="text-muted-foreground">No insights available yet.</p>
                <p className="text-sm text-muted-foreground/70">Keep writing to unlock AI-powered insights!</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Mood & Tag Analysis */}
        <Card className="glassmorphism-card border-0">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Heart className="w-5 h-5 text-primary" />
              <span>Patterns</span>
            </CardTitle>
            <CardDescription>Your most common moods and topics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Most Used Moods */}
            <div>
              <h4 className="font-medium text-foreground mb-3">Top Moods</h4>
              <div className="space-y-2">
                {stats.mostUsedMoods.slice(0, 5).map((mood, index) => {
                  const percentage = (mood.count / stats.totalEntries) * 100;
                  return (
                    <div key={mood.mood} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: getMoodColor(mood.mood) }}
                        />
                        <span className="text-sm text-foreground capitalize">{mood.mood}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Progress 
                          value={percentage} 
                          className="w-16 h-2" 
                        />
                        <span className="text-xs text-muted-foreground w-8">
                          {mood.count}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Most Used Tags */}
            <div>
              <h4 className="font-medium text-foreground mb-3">Popular Topics</h4>
              <div className="flex flex-wrap gap-2">
                {stats.mostUsedTags.slice(0, 8).map((tag) => (
                  <Badge 
                    key={tag.tag}
                    variant="secondary" 
                    className="glassmorphism-card bg-primary/10 text-primary border-primary/20"
                  >
                    {tag.tag} ({tag.count})
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Streaks and Goals */}
      <Card className="glassmorphism-card border-0">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Award className="w-5 h-5 text-primary" />
            <span>Progress & Achievements</span>
          </CardTitle>
          <CardDescription>Track your journaling consistency and milestones</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-orange-400 to-red-500">
                <Flame className="w-8 h-8 text-white" />
              </div>
              <div className="text-xl font-bold text-foreground">{stats.currentStreak} days</div>
              <div className="text-sm text-muted-foreground">Current Streak</div>
              <Progress value={(stats.currentStreak / 30) * 100} className="mt-2 h-2" />
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-blue-400 to-purple-500">
                <Target className="w-8 h-8 text-white" />
              </div>
              <div className="text-xl font-bold text-foreground">{stats.longestStreak} days</div>
              <div className="text-sm text-muted-foreground">Longest Streak</div>
              <div className="text-xs text-muted-foreground mt-2">
                Personal best!
              </div>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-green-400 to-teal-500">
                <Calendar className="w-8 h-8 text-white" />
              </div>
              <div className="text-xl font-bold text-foreground">{stats.entriesThisWeek}/7</div>
              <div className="text-sm text-muted-foreground">This Week</div>
              <Progress value={(stats.entriesThisWeek / 7) * 100} className="mt-2 h-2" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}