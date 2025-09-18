import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Switch } from '../ui/switch';
import { Slider } from '../ui/slider';
import { 
  TrendingUp,
  TrendingDown,
  Brain,
  Target,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Calendar,
  BarChart3,
  LineChart,
  PieChart,
  Activity,
  Heart,
  Zap,
  Star,
  Award,
  Info,
  Settings,
  RefreshCw,
  Download,
  Filter,
  Eye,
  EyeOff
} from 'lucide-react';

interface Prediction {
  id: string;
  type: 'goal_achievement' | 'burnout_risk' | 'optimal_time' | 'life_satisfaction' | 'habit_success' | 'energy_pattern';
  title: string;
  description: string;
  confidence: number;
  probability: number;
  timeframe: 'week' | 'month' | 'quarter' | 'year';
  impact: 'low' | 'medium' | 'high';
  category: 'productivity' | 'wellness' | 'goals' | 'habits' | 'energy' | 'satisfaction';
  factors: PredictionFactor[];
  recommendations: Recommendation[];
  trend: 'improving' | 'declining' | 'stable' | 'volatile';
  lastUpdated: Date;
}

interface PredictionFactor {
  name: string;
  influence: number; // -100 to 100
  description: string;
  weight: number; // 0 to 1
}

interface Recommendation {
  id: string;
  action: string;
  impact: number; // 0 to 100
  effort: 'low' | 'medium' | 'high';
  timeToImplement: number; // days
  category: 'immediate' | 'short_term' | 'long_term';
}

interface ForecastData {
  date: string;
  actual?: number;
  predicted: number;
  confidence_upper: number;
  confidence_lower: number;
  category: string;
}

interface LifeSatisfactionMetric {
  pillar: string;
  currentScore: number;
  predictedScore: number;
  trend: 'up' | 'down' | 'stable';
  factors: string[];
}

export default function PredictiveLifeAnalytics() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTimeframe, setSelectedTimeframe] = useState('month');
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [forecastData, setForecastData] = useState<ForecastData[]>([]);
  const [lifeSatisfactionMetrics, setLifeSatisfactionMetrics] = useState<LifeSatisfactionMetric[]>([]);
  const [showConfidenceIntervals, setShowConfidenceIntervals] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['all']);

  // Sample predictions data
  useEffect(() => {
    const samplePredictions: Prediction[] = [
      {
        id: '1',
        type: 'goal_achievement',
        title: 'Q1 Fitness Goal Achievement',
        description: 'Based on current pace and historical patterns, 89% probability of achieving your fitness goals this quarter',
        confidence: 0.94,
        probability: 0.89,
        timeframe: 'quarter',
        impact: 'high',
        category: 'wellness',
        factors: [
          { name: 'Current consistency', influence: 45, description: 'You\'ve maintained 4+ workouts per week', weight: 0.3 },
          { name: 'Seasonal patterns', influence: 12, description: 'Winter motivation typically decreases', weight: 0.2 },
          { name: 'Calendar availability', influence: 23, description: 'Fewer meetings scheduled in coming weeks', weight: 0.25 },
          { name: 'Recovery metrics', influence: 18, description: 'Sleep quality improving', weight: 0.25 }
        ],
        recommendations: [
          { id: 'r1', action: 'Schedule workouts as calendar blocks', impact: 15, effort: 'low', timeToImplement: 1, category: 'immediate' },
          { id: 'r2', action: 'Prepare for motivation dip in week 3', impact: 25, effort: 'medium', timeToImplement: 14, category: 'short_term' }
        ],
        trend: 'improving',
        lastUpdated: new Date()
      },
      {
        id: '2',
        type: 'burnout_risk',
        title: 'Burnout Risk Assessment',
        description: 'Elevated risk detected for late February. 67% chance of experiencing significant stress symptoms.',
        confidence: 0.82,
        probability: 0.67,
        timeframe: 'month',
        impact: 'high',
        category: 'wellness',
        factors: [
          { name: 'Meeting density', influence: -35, description: 'Back-to-back meetings increasing', weight: 0.4 },
          { name: 'Sleep pattern disruption', influence: -28, description: 'Later bedtimes noted', weight: 0.3 },
          { name: 'Project deadlines', influence: -22, description: 'Multiple deadlines converging', weight: 0.2 },
          { name: 'Support system', influence: 15, description: 'Active social connections', weight: 0.1 }
        ],
        recommendations: [
          { id: 'r3', action: 'Block 30-min buffers between meetings', impact: 30, effort: 'low', timeToImplement: 1, category: 'immediate' },
          { id: 'r4', action: 'Implement evening wind-down routine', impact: 40, effort: 'medium', timeToImplement: 3, category: 'short_term' },
          { id: 'r5', action: 'Delegate non-critical tasks', impact: 35, effort: 'high', timeToImplement: 7, category: 'short_term' }
        ],
        trend: 'declining',
        lastUpdated: new Date()
      },
      {
        id: '3',
        type: 'optimal_time',
        title: 'Peak Productivity Windows',
        description: 'Your optimal creative work window is predicted to shift 30 minutes earlier next month due to daylight changes.',
        confidence: 0.76,
        probability: 0.84,
        timeframe: 'month',
        impact: 'medium',
        category: 'productivity',
        factors: [
          { name: 'Circadian rhythm tracking', influence: 32, description: 'Natural shift with daylight', weight: 0.4 },
          { name: 'Historical productivity data', influence: 28, description: 'Previous seasonal patterns', weight: 0.3 },
          { name: 'Sleep schedule adaptation', influence: 19, description: 'Earlier wake times trending', weight: 0.3 }
        ],
        recommendations: [
          { id: 'r6', action: 'Gradually shift creative work 15 minutes earlier', impact: 20, effort: 'low', timeToImplement: 7, category: 'short_term' },
          { id: 'r7', action: 'Update calendar templates for optimal scheduling', impact: 25, effort: 'medium', timeToImplement: 3, category: 'immediate' }
        ],
        trend: 'stable',
        lastUpdated: new Date()
      },
      {
        id: '4',
        type: 'life_satisfaction',
        title: 'Life Satisfaction Forecast',
        description: 'Overall life satisfaction predicted to increase 12% over next quarter with current trajectory.',
        confidence: 0.71,
        probability: 0.78,
        timeframe: 'quarter',
        impact: 'high',
        category: 'satisfaction',
        factors: [
          { name: 'Goal progress acceleration', influence: 25, description: 'Multiple goals on track', weight: 0.3 },
          { name: 'Relationship investment', influence: 20, description: 'Increased social activities', weight: 0.25 },
          { name: 'Career milestone approach', influence: 18, description: 'Promotion timeline favorable', weight: 0.25 },
          { name: 'Health improvements', influence: 15, description: 'Consistent wellness gains', weight: 0.2 }
        ],
        recommendations: [
          { id: 'r8', action: 'Continue current momentum across all pillars', impact: 30, effort: 'low', timeToImplement: 1, category: 'immediate' },
          { id: 'r9', action: 'Plan celebration for reaching milestones', impact: 15, effort: 'low', timeToImplement: 14, category: 'short_term' }
        ],
        trend: 'improving',
        lastUpdated: new Date()
      }
    ];

    const sampleForecastData: ForecastData[] = [
      { date: '2024-01-01', actual: 7.2, predicted: 7.1, confidence_upper: 7.8, confidence_lower: 6.4, category: 'satisfaction' },
      { date: '2024-01-08', actual: 7.5, predicted: 7.3, confidence_upper: 8.0, confidence_lower: 6.6, category: 'satisfaction' },
      { date: '2024-01-15', actual: 7.1, predicted: 7.2, confidence_upper: 7.9, confidence_lower: 6.5, category: 'satisfaction' },
      { date: '2024-01-22', actual: 7.8, predicted: 7.6, confidence_upper: 8.3, confidence_lower: 6.9, category: 'satisfaction' },
      { date: '2024-01-29', predicted: 7.9, confidence_upper: 8.6, confidence_lower: 7.2, category: 'satisfaction' },
      { date: '2024-02-05', predicted: 8.1, confidence_upper: 8.8, confidence_lower: 7.4, category: 'satisfaction' },
      { date: '2024-02-12', predicted: 8.3, confidence_upper: 9.0, confidence_lower: 7.6, category: 'satisfaction' },
      { date: '2024-02-19', predicted: 8.0, confidence_upper: 8.7, confidence_lower: 7.3, category: 'satisfaction' }
    ];

    const sampleLifeMetrics: LifeSatisfactionMetric[] = [
      {
        pillar: 'Health & Wellness',
        currentScore: 8.2,
        predictedScore: 8.7,
        trend: 'up',
        factors: ['Consistent exercise routine', 'Improved sleep quality', 'Better nutrition tracking']
      },
      {
        pillar: 'Career & Growth',
        currentScore: 7.1,
        predictedScore: 7.8,
        trend: 'up',
        factors: ['Upcoming promotion opportunity', 'New skill development', 'Positive feedback trends']
      },
      {
        pillar: 'Relationships',
        currentScore: 6.8,
        predictedScore: 6.9,
        trend: 'stable',
        factors: ['Stable family relationships', 'Limited social expansion', 'Steady friend connections']
      },
      {
        pillar: 'Financial Security',
        currentScore: 7.5,
        predictedScore: 7.2,
        trend: 'down',
        factors: ['Market volatility concerns', 'Increased expenses planned', 'Emergency fund stable']
      },
      {
        pillar: 'Personal Growth',
        currentScore: 8.0,
        predictedScore: 8.4,
        trend: 'up',
        factors: ['Active learning goals', 'Meditation practice improving', 'Journal insights increasing']
      }
    ];

    setPredictions(samplePredictions);
    setForecastData(sampleForecastData);
    setLifeSatisfactionMetrics(sampleLifeMetrics);
  }, []);

  const getPredictionIcon = (type: string) => {
    switch (type) {
      case 'goal_achievement': return <Target className="h-5 w-5" />;
      case 'burnout_risk': return <AlertTriangle className="h-5 w-5" />;
      case 'optimal_time': return <Clock className="h-5 w-5" />;
      case 'life_satisfaction': return <Heart className="h-5 w-5" />;
      case 'habit_success': return <CheckCircle2 className="h-5 w-5" />;
      case 'energy_pattern': return <Zap className="h-5 w-5" />;
      default: return <Brain className="h-5 w-5" />;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp className="h-4 w-4 text-green-400" />;
      case 'declining': return <TrendingDown className="h-4 w-4 text-red-400" />;
      case 'stable': return <Activity className="h-4 w-4 text-blue-400" />;
      case 'volatile': return <BarChart3 className="h-4 w-4 text-yellow-400" />;
      default: return <Activity className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'bg-red-500/20 text-red-300';
      case 'medium': return 'bg-yellow-500/20 text-yellow-300';
      case 'low': return 'bg-green-500/20 text-green-300';
      default: return 'bg-gray-500/20 text-gray-300';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-400';
    if (confidence >= 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  const filteredPredictions = selectedCategories.includes('all') 
    ? predictions 
    : predictions.filter(p => selectedCategories.includes(p.category));

  const highConfidencePredictions = predictions.filter(p => p.confidence >= 0.8).length;
  const highImpactPredictions = predictions.filter(p => p.impact === 'high').length;
  const averageConfidence = Math.round(predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length * 100);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center space-x-3">
              <Brain className="h-8 w-8 text-primary" />
              <span>Predictive Life Analytics</span>
            </h1>
            <p className="text-muted-foreground mt-1">
              AI-powered forecasting and trend analysis for life optimization
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">High Confidence</p>
                  <p className="text-2xl font-bold">{highConfidencePredictions}</p>
                </div>
                <CheckCircle2 className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">High Impact</p>
                  <p className="text-2xl font-bold">{highImpactPredictions}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-orange-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg Confidence</p>
                  <p className="text-2xl font-bold">{averageConfidence}%</p>
                </div>
                <Brain className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="glassmorphism-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Auto Refresh</p>
                  <Switch checked={autoRefresh} onCheckedChange={setAutoRefresh} />
                </div>
                <Settings className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="forecasts">Forecasts</TabsTrigger>
          <TabsTrigger value="satisfaction">Life Satisfaction</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Key Predictions Summary */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5" />
                <span>Key Predictions This {selectedTimeframe}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {predictions.slice(0, 4).map((prediction) => (
                  <div key={prediction.id} className="glassmorphism-panel p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {getPredictionIcon(prediction.type)}
                        <h4 className="font-semibold text-sm">{prediction.title}</h4>
                      </div>
                      <div className="flex items-center space-x-1">
                        {getTrendIcon(prediction.trend)}
                        <span className={`text-sm font-bold ${getConfidenceColor(prediction.confidence)}`}>
                          {Math.round(prediction.probability * 100)}%
                        </span>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">{prediction.description}</p>
                    <div className="flex items-center justify-between">
                      <Badge className={getImpactColor(prediction.impact)} variant="outline">
                        {prediction.impact} impact
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {Math.round(prediction.confidence * 100)}% confidence
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5" />
                <span>Recommended Actions</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {predictions.flatMap(p => p.recommendations)
                .filter(r => r.category === 'immediate')
                .slice(0, 5)
                .map((rec) => (
                <div key={rec.id} className="flex items-center justify-between glassmorphism-panel p-3">
                  <div>
                    <p className="text-sm font-medium">{rec.action}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant="outline" className="text-xs">{rec.effort} effort</Badge>
                      <span className="text-xs text-muted-foreground">
                        +{rec.impact}% impact • {rec.timeToImplement} day{rec.timeToImplement !== 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                  <Button size="sm" variant="outline">
                    Apply
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-6">
          {/* Filters */}
          <div className="flex items-center space-x-4 glassmorphism-panel p-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4" />
              <span className="text-sm font-medium">Filters:</span>
            </div>
            <Select value={selectedTimeframe} onValueChange={setSelectedTimeframe}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="week">This Week</SelectItem>
                <SelectItem value="month">This Month</SelectItem>
                <SelectItem value="quarter">This Quarter</SelectItem>
                <SelectItem value="year">This Year</SelectItem>
              </SelectContent>
            </Select>
            <div className="flex items-center space-x-2">
              <span className="text-sm">Show Confidence Intervals:</span>
              <Switch checked={showConfidenceIntervals} onCheckedChange={setShowConfidenceIntervals} />
            </div>
          </div>

          {/* Predictions List */}
          <div className="space-y-4">
            {filteredPredictions.map((prediction) => (
              <Card key={prediction.id} className="glassmorphism-card">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 rounded-lg bg-primary/20">
                      {getPredictionIcon(prediction.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-semibold">{prediction.title}</h3>
                        <div className="flex items-center space-x-2">
                          {getTrendIcon(prediction.trend)}
                          <Badge className={getImpactColor(prediction.impact)}>
                            {prediction.impact} impact
                          </Badge>
                          <Badge variant="outline">{prediction.timeframe}</Badge>
                        </div>
                      </div>
                      
                      <p className="text-muted-foreground mb-4">{prediction.description}</p>

                      {/* Probability and Confidence */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="glassmorphism-panel p-3">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium">Probability</span>
                            <span className="text-lg font-bold text-primary">
                              {Math.round(prediction.probability * 100)}%
                            </span>
                          </div>
                          <Progress value={prediction.probability * 100} className="h-2" />
                        </div>
                        <div className="glassmorphism-panel p-3">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium">Confidence</span>
                            <span className={`text-lg font-bold ${getConfidenceColor(prediction.confidence)}`}>
                              {Math.round(prediction.confidence * 100)}%
                            </span>
                          </div>
                          <Progress value={prediction.confidence * 100} className="h-2" />
                        </div>
                      </div>

                      {/* Factors */}
                      <div className="space-y-2 mb-4">
                        <h4 className="font-medium">Key Factors</h4>
                        {prediction.factors.slice(0, 3).map((factor, index) => (
                          <div key={index} className="flex items-center justify-between glassmorphism-panel p-2">
                            <span className="text-sm">{factor.name}</span>
                            <div className="flex items-center space-x-2">
                              <span className={`text-sm font-medium ${
                                factor.influence > 0 ? 'text-green-400' : 'text-red-400'
                              }`}>
                                {factor.influence > 0 ? '+' : ''}{factor.influence}%
                              </span>
                              <Progress 
                                value={Math.abs(factor.influence)} 
                                className="w-16 h-1" 
                              />
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Recommendations */}
                      <div className="space-y-2">
                        <h4 className="font-medium">Recommendations</h4>
                        {prediction.recommendations.map((rec) => (
                          <div key={rec.id} className="flex items-center justify-between glassmorphism-panel p-3">
                            <div>
                              <p className="text-sm font-medium">{rec.action}</p>
                              <div className="flex items-center space-x-2 mt-1">
                                <Badge variant="outline" className="text-xs">{rec.effort}</Badge>
                                <Badge variant="outline" className="text-xs">{rec.category}</Badge>
                                <span className="text-xs text-muted-foreground">
                                  +{rec.impact}% • {rec.timeToImplement}d
                                </span>
                              </div>
                            </div>
                            <Button size="sm">
                              Apply
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="forecasts" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <LineChart className="h-5 w-5" />
                <span>Life Satisfaction Forecast</span>
              </CardTitle>
              <CardDescription>
                Predicted trends based on current patterns and planned changes
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="h-64 flex items-center justify-center bg-background/50 rounded-lg">
                <p className="text-muted-foreground">Interactive forecast chart would be implemented here</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glassmorphism-panel p-4 text-center">
                  <div className="text-2xl font-bold text-green-400">+12%</div>
                  <div className="text-sm text-muted-foreground">Predicted Improvement</div>
                </div>
                <div className="glassmorphism-panel p-4 text-center">
                  <div className="text-2xl font-bold text-blue-400">94%</div>
                  <div className="text-sm text-muted-foreground">Model Accuracy</div>
                </div>
                <div className="glassmorphism-panel p-4 text-center">
                  <div className="text-2xl font-bold text-primary">3.2</div>
                  <div className="text-sm text-muted-foreground">Months to Peak</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="satisfaction" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {lifeSatisfactionMetrics.map((metric) => (
              <Card key={metric.pillar} className="glassmorphism-card">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center justify-between">
                    {metric.pillar}
                    {metric.trend === 'up' && <TrendingUp className="h-5 w-5 text-green-400" />}
                    {metric.trend === 'down' && <TrendingDown className="h-5 w-5 text-red-400" />}
                    {metric.trend === 'stable' && <Activity className="h-5 w-5 text-blue-400" />}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Current</span>
                      <span className="font-bold">{metric.currentScore}/10</span>
                    </div>
                    <Progress value={metric.currentScore * 10} className="h-2" />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Predicted</span>
                      <span className="font-bold text-primary">{metric.predictedScore}/10</span>
                    </div>
                    <Progress value={metric.predictedScore * 10} className="h-2" />
                  </div>

                  <div className="space-y-1">
                    <span className="text-sm font-medium">Key Factors:</span>
                    {metric.factors.slice(0, 2).map((factor, index) => (
                      <p key={index} className="text-xs text-muted-foreground">• {factor}</p>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <Card className="glassmorphism-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5" />
                <span>AI-Generated Insights</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="glassmorphism-panel p-4">
                <h4 className="font-semibold mb-2">Pattern Recognition</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  Your productivity peaks consistently occur 2.3 hours after waking, regardless of actual wake time. This suggests a strong circadian influence on cognitive performance.
                </p>
                <Badge className="bg-blue-500/20 text-blue-300">High Confidence</Badge>
              </div>

              <div className="glassmorphism-panel p-4">
                <h4 className="font-semibold mb-2">Correlation Discovery</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  Days with 20+ minutes of morning sunlight show 34% higher mood ratings and 28% better decision quality throughout the day.
                </p>
                <Badge className="bg-green-500/20 text-green-300">Actionable</Badge>
              </div>

              <div className="glassmorphism-panel p-4">
                <h4 className="font-semibold mb-2">Trend Prediction</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  Based on current habits, you're 89% likely to exceed your annual learning goals by June if you maintain current reading pace.
                </p>
                <Badge className="bg-yellow-500/20 text-yellow-300">Opportunity</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}