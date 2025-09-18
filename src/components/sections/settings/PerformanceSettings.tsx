import React, { useState, useEffect } from 'react';
import { Activity, Zap, Database, AlertTriangle, CheckCircle, TrendingUp, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import { Switch } from '../../ui/switch';
import { Label } from '../../ui/label';
import { Progress } from '../../ui/progress';
import { Separator } from '../../ui/separator';
import { Alert, AlertDescription } from '../../ui/alert';
import { toast } from 'sonner@2.0.3';
import performanceUtils, { 
  PerformanceMetrics, 
  cacheManager, 
  performanceMonitor,
  runPerformanceAudit,
  clearUnusedData,
  reportPerformanceMetrics 
} from '../../../utils/performanceOptimizations.tsx';

const PerformanceSettings: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [performanceIssues, setPerformanceIssues] = useState<string[]>([]);
  const [optimizationsEnabled, setOptimizationsEnabled] = useState(true);
  const [cacheEnabled, setCacheEnabled] = useState(true);
  const [prefetchEnabled, setPrefetchEnabled] = useState(true);
  const [imageOptimizationEnabled, setImageOptimizationEnabled] = useState(true);
  const [isOptimizing, setIsOptimizing] = useState(false);

  useEffect(() => {
    loadPerformanceData();
    const interval = setInterval(loadPerformanceData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadPerformanceData = () => {
    const currentMetrics = performanceMonitor.getAverageMetrics();
    setMetrics(currentMetrics);
    
    const issues = runPerformanceAudit();
    setPerformanceIssues(issues);
  };

  const handleOptimizeNow = async () => {
    setIsOptimizing(true);
    
    try {
      // Clear unused data
      clearUnusedData();
      
      // Report metrics
      reportPerformanceMetrics();
      
      // Simulate optimization process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Reload performance data
      loadPerformanceData();
      
      toast.success('Performance optimization completed');
    } catch (error) {
      toast.error('Performance optimization failed');
    } finally {
      setIsOptimizing(false);
    }
  };

  const getPerformanceScore = (): number => {
    if (!metrics) return 0;
    
    let score = 100;
    
    // Deduct points for poor performance
    if (metrics.loadTime > 3000) score -= 20;
    if (metrics.renderTime > 16) score -= 15;
    if (metrics.memoryUsage > 50) score -= 15;
    if (metrics.cacheHitRate < 0.7) score -= 15;
    if (metrics.errorRate > 0.05) score -= 10;
    if (metrics.userInteractionDelay > 100) score -= 15;
    
    return Math.max(0, score);
  };

  const getScoreColor = (score: number): string => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (ms: number): string => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const performanceScore = getPerformanceScore();

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Performance Optimization</h3>
        <p className="text-sm text-muted-foreground mt-1">
          Monitor and optimize application performance for the best user experience
        </p>
      </div>

      {/* Performance Score */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Performance Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <div className={`text-4xl font-bold ${getScoreColor(performanceScore)}`}>
              {performanceScore}/100
            </div>
            <Progress value={performanceScore} className="mt-4" />
            <p className="text-sm text-muted-foreground mt-2">
              {performanceScore >= 90 ? 'Excellent' : 
               performanceScore >= 70 ? 'Good' : 'Needs Improvement'}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      {metrics && (
        <Card className="glassmorphism-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Performance Metrics
            </CardTitle>
            <CardDescription>Real-time application performance data</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-card rounded-lg">
                <div className="text-lg font-bold">{formatTime(metrics.loadTime)}</div>
                <div className="text-sm text-muted-foreground">Load Time</div>
                {metrics.loadTime > 3000 && (
                  <Badge variant="destructive" className="mt-1">Slow</Badge>
                )}
              </div>
              
              <div className="text-center p-4 bg-card rounded-lg">
                <div className="text-lg font-bold">{formatTime(metrics.renderTime)}</div>
                <div className="text-sm text-muted-foreground">Render Time</div>
                {metrics.renderTime > 16 && (
                  <Badge variant="destructive" className="mt-1">Slow</Badge>
                )}
              </div>
              
              <div className="text-center p-4 bg-card rounded-lg">
                <div className="text-lg font-bold">{metrics.memoryUsage.toFixed(1)} MB</div>
                <div className="text-sm text-muted-foreground">Memory Usage</div>
                {metrics.memoryUsage > 50 && (
                  <Badge variant="destructive" className="mt-1">High</Badge>
                )}
              </div>
              
              <div className="text-center p-4 bg-card rounded-lg">
                <div className="text-lg font-bold">{(metrics.cacheHitRate * 100).toFixed(1)}%</div>
                <div className="text-sm text-muted-foreground">Cache Hit Rate</div>
                {metrics.cacheHitRate < 0.7 && (
                  <Badge variant="destructive" className="mt-1">Low</Badge>
                )}
              </div>
              
              <div className="text-center p-4 bg-card rounded-lg">
                <div className="text-lg font-bold">{(metrics.errorRate * 100).toFixed(2)}%</div>
                <div className="text-sm text-muted-foreground">Error Rate</div>
                {metrics.errorRate > 0.05 && (
                  <Badge variant="destructive" className="mt-1">High</Badge>
                )}
              </div>
              
              <div className="text-center p-4 bg-card rounded-lg">
                <div className="text-lg font-bold">{formatTime(metrics.userInteractionDelay)}</div>
                <div className="text-sm text-muted-foreground">Interaction Delay</div>
                {metrics.userInteractionDelay > 100 && (
                  <Badge variant="destructive" className="mt-1">Slow</Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Performance Issues */}
      {performanceIssues.length > 0 && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <div className="font-medium mb-2">Performance Issues Detected:</div>
            <ul className="list-disc list-inside space-y-1">
              {performanceIssues.map((issue, index) => (
                <li key={index} className="text-sm">{issue}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Optimization Controls */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Optimization Settings
          </CardTitle>
          <CardDescription>
            Configure automatic performance optimizations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="optimizations">Enable Optimizations</Label>
              <p className="text-sm text-muted-foreground">
                Automatically optimize performance in the background
              </p>
            </div>
            <Switch
              id="optimizations"
              checked={optimizationsEnabled}
              onCheckedChange={setOptimizationsEnabled}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="cache">Smart Caching</Label>
              <p className="text-sm text-muted-foreground">
                Cache frequently accessed data for faster loading
              </p>
            </div>
            <Switch
              id="cache"
              checked={cacheEnabled}
              onCheckedChange={setCacheEnabled}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="prefetch">Resource Prefetching</Label>
              <p className="text-sm text-muted-foreground">
                Preload resources that you're likely to need
              </p>
            </div>
            <Switch
              id="prefetch"
              checked={prefetchEnabled}
              onCheckedChange={setPrefetchEnabled}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="imageOpt">Image Optimization</Label>
              <p className="text-sm text-muted-foreground">
                Automatically optimize images for faster loading
              </p>
            </div>
            <Switch
              id="imageOpt"
              checked={imageOptimizationEnabled}
              onCheckedChange={setImageOptimizationEnabled}
            />
          </div>
        </CardContent>
      </Card>

      {/* Cache Management */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            Cache Management
          </CardTitle>
          <CardDescription>
            Manage application cache for optimal performance
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-card rounded-lg">
              <div className="text-lg font-bold">{cacheManager.size()}</div>
              <div className="text-sm text-muted-foreground">Cached Items</div>
            </div>
            <div className="text-center p-4 bg-card rounded-lg">
              <div className="text-lg font-bold">{formatBytes(cacheManager.size() * 1024)}</div>
              <div className="text-sm text-muted-foreground">Estimated Size</div>
            </div>
          </div>

          <div className="flex gap-4">
            <Button
              variant="outline"
              onClick={() => {
                cacheManager.invalidate();
                toast.success('Cache cleared successfully');
                loadPerformanceData();
              }}
              className="flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Clear Cache
            </Button>
            
            <Button
              onClick={handleOptimizeNow}
              disabled={isOptimizing}
              className="flex items-center gap-2"
            >
              {isOptimizing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Optimizing...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Optimize Now
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card className="glassmorphism-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Performance Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
              <div>
                <div className="font-medium">Enable all optimizations</div>
                <div className="text-sm text-muted-foreground">
                  Turn on caching, prefetching, and image optimization for best performance
                </div>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
              <div>
                <div className="font-medium">Regular cache cleanup</div>
                <div className="text-sm text-muted-foreground">
                  Clear cache periodically to prevent memory buildup
                </div>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
              <div>
                <div className="font-medium">Monitor performance metrics</div>
                <div className="text-sm text-muted-foreground">
                  Keep an eye on load times and memory usage for optimal experience
                </div>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
              <div>
                <div className="font-medium">Use latest browser</div>
                <div className="text-sm text-muted-foreground">
                  Modern browsers provide better performance and optimization features
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PerformanceSettings;