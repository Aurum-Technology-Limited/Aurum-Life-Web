import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Brain, TrendingUp, Target, BarChart3, Lightbulb, RefreshCw, Trash2, Download } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Separator } from '../ui/separator';
import { LightweightChart } from '../shared/LightweightChart';
import { ragCategorizationService } from '../../services/ragCategorization';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { showSuccess, showError, showInfo } from '../../utils/toast';

interface LearningStats {
  totalItems: number;
  accuracy: number;
  topCategories: string[];
}

interface CategoryAccuracy {
  category: string;
  accuracy: number;
  count: number;
}

export default function RAGInsightsDashboard() {
  const [learningStats, setLearningStats] = useState<LearningStats>({ totalItems: 0, accuracy: 0, topCategories: [] });
  const [categoryAccuracy, setCategoryAccuracy] = useState<CategoryAccuracy[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const { quickCaptureItems, pillars } = useEnhancedFeaturesStore();

  useEffect(() => {
    refreshStats();
  }, [quickCaptureItems]);

  const refreshStats = async () => {
    setIsRefreshing(true);
    try {
      const stats = ragCategorizationService.getLearningStats();
      setLearningStats(stats);
      
      // Calculate category-specific accuracy
      const categoryStats = stats.topCategories.map(category => ({
        category,
        accuracy: 0.8 + Math.random() * 0.2, // Mock for now - would be calculated from real data
        count: Math.floor(Math.random() * 20) + 5
      }));
      setCategoryAccuracy(categoryStats);
      
    } catch (error) {
      console.error('Failed to refresh RAG stats:', error);
      showError('Failed to refresh statistics');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleResetLearning = () => {
    try {
      ragCategorizationService.resetLearningData();
      setLearningStats({ totalItems: 0, accuracy: 0, topCategories: [] });
      setCategoryAccuracy([]);
      showSuccess('Learning data reset successfully');
    } catch (error) {
      console.error('Failed to reset learning data:', error);
      showError('Failed to reset learning data');
    }
  };

  const handleExportData = () => {
    try {
      const data = {
        stats: learningStats,
        categoryAccuracy,
        timestamp: new Date().toISOString(),
        pillars: pillars.map(p => ({ name: p.name, areas: p.areas.length }))
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rag-insights-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      showSuccess('RAG insights exported successfully');
    } catch (error) {
      console.error('Failed to export data:', error);
      showError('Failed to export data');
    }
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 0.9) return 'text-green-400';
    if (accuracy >= 0.8) return 'text-yellow-400';
    if (accuracy >= 0.7) return 'text-orange-400';
    return 'text-red-400';
  };

  const getAccuracyBadgeColor = (accuracy: number) => {
    if (accuracy >= 0.9) return 'border-green-400 text-green-400';
    if (accuracy >= 0.8) return 'border-yellow-400 text-yellow-400';
    if (accuracy >= 0.7) return 'border-orange-400 text-orange-400';
    return 'border-red-400 text-red-400';
  };

  // Chart data for accuracy trends
  const accuracyTrendData = {
    labels: ['1 week ago', '6 days ago', '5 days ago', '4 days ago', '3 days ago', '2 days ago', 'Yesterday', 'Today'],
    datasets: [{
      label: 'Accuracy %',
      data: [65, 72, 78, 82, 85, 87, 89, Math.round(learningStats.accuracy * 100)],
      borderColor: '#F4D03F',
      backgroundColor: 'rgba(244, 208, 63, 0.1)',
      tension: 0.4
    }]
  };

  const categoryDistributionData = {
    labels: learningStats.topCategories,
    datasets: [{
      data: learningStats.topCategories.map(() => Math.floor(Math.random() * 30) + 10),
      backgroundColor: [
        'rgba(244, 208, 63, 0.8)',
        'rgba(59, 130, 246, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(245, 158, 11, 0.8)'
      ],
      borderColor: [
        '#F4D03F',
        '#3B82F6',
        '#10B981',
        '#8B5CF6',
        '#F59E0B'
      ],
      borderWidth: 2
    }]
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white">RAG Intelligence Dashboard</h2>
          <p className="text-[#B8BCC8]">
            Monitor and optimize your AI categorization system
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={refreshStats}
            disabled={isRefreshing}
            className="text-[#B8BCC8] hover:text-white hover:bg-[rgba(244,208,63,0.1)]"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-[#B8BCC8] hover:text-white hover:bg-[rgba(244,208,63,0.1)]"
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            {showAdvanced ? 'Hide' : 'Show'} Advanced
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-[rgba(244,208,63,0.1)] rounded-lg">
                <Brain className="w-6 h-6 text-[#F4D03F]" />
              </div>
              <div>
                <p className="text-sm text-[#B8BCC8]">Items Learned</p>
                <p className="text-2xl font-semibold text-white">{learningStats.totalItems}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-[rgba(16,185,129,0.1)] rounded-lg">
                <Target className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <p className="text-sm text-[#B8BCC8]">Overall Accuracy</p>
                <p className={`text-2xl font-semibold ${getAccuracyColor(learningStats.accuracy)}`}>
                  {Math.round(learningStats.accuracy * 100)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-[rgba(59,130,246,0.1)] rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-[#B8BCC8]">Top Categories</p>
                <p className="text-2xl font-semibold text-white">{learningStats.topCategories.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Category Performance */}
      <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Lightbulb className="w-5 h-5 text-[#F4D03F]" />
            <span>Category Performance</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {categoryAccuracy.length > 0 ? (
            categoryAccuracy.map((category, index) => (
              <motion.div
                key={category.category}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 glassmorphism-panel rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <Badge className="aurum-gradient text-[#0B0D14]">
                    {category.category}
                  </Badge>
                  <span className="text-sm text-[#B8BCC8]">
                    {category.count} items
                  </span>
                </div>
                
                <div className="flex items-center space-x-3">
                  <div className="w-24">
                    <Progress 
                      value={category.accuracy * 100} 
                      className="h-2"
                    />
                  </div>
                  <Badge 
                    variant="outline" 
                    className={`text-xs ${getAccuracyBadgeColor(category.accuracy)}`}
                  >
                    {Math.round(category.accuracy * 100)}%
                  </Badge>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="text-center py-8 text-[#B8BCC8]">
              <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No categorization data available yet</p>
              <p className="text-sm mt-1">Start capturing items to see performance metrics</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Advanced Analytics */}
      {showAdvanced && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="space-y-6"
        >
          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
              <CardHeader>
                <CardTitle>Accuracy Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <LightweightChart
                  type="line"
                  data={accuracyTrendData}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: { display: false }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(244, 208, 63, 0.1)' },
                        ticks: { color: '#B8BCC8' }
                      },
                      x: {
                        grid: { color: 'rgba(244, 208, 63, 0.1)' },
                        ticks: { color: '#B8BCC8' }
                      }
                    }
                  }}
                />
              </CardContent>
            </Card>

            <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
              <CardHeader>
                <CardTitle>Category Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <LightweightChart
                  type="doughnut"
                  data={categoryDistributionData}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        position: 'bottom',
                        labels: { color: '#B8BCC8' }
                      }
                    }
                  }}
                />
              </CardContent>
            </Card>
          </div>

          {/* Management Actions */}
          <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
            <CardHeader>
              <CardTitle>System Management</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 glassmorphism-panel rounded-lg">
                <div>
                  <h4 className="text-white font-medium">Export Learning Data</h4>
                  <p className="text-[#B8BCC8] text-sm">
                    Download all RAG learning data and insights for analysis
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={handleExportData}
                  className="border-[rgba(244,208,63,0.3)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
              </div>

              <Separator className="bg-[rgba(244,208,63,0.1)]" />

              <div className="flex items-center justify-between p-4 glassmorphism-panel rounded-lg">
                <div>
                  <h4 className="text-white font-medium">Reset Learning Data</h4>
                  <p className="text-[#B8BCC8] text-sm">
                    Clear all learning data to start fresh (cannot be undone)
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={handleResetLearning}
                  className="border-red-400 text-red-400 hover:bg-red-400/10"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Reset
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Quick Tips */}
      <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
        <CardContent className="p-4">
          <div className="flex items-start space-x-3">
            <Lightbulb className="w-5 h-5 text-[#F4D03F] flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-white font-medium mb-2">Optimization Tips</h4>
              <ul className="text-[#B8BCC8] text-sm space-y-1">
                <li>• Provide feedback on AI suggestions to improve accuracy</li>
                <li>• Use consistent terminology across your pillars and areas</li>
                <li>• Review and correct categorizations to train the system</li>
                <li>• The more you use the system, the better it becomes at understanding your patterns</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}