/**
 * Phase 2: Advanced Analytics Service with AI Insights
 * Provides deep analytics, predictive insights, and performance tracking
 */

interface AnalyticsDataPoint {
  timestamp: string;
  value: number;
  category: string;
  metadata?: Record<string, any>;
}

interface ProductivityMetrics {
  tasksCompleted: number;
  tasksCreated: number;
  averageCompletionTime: number;
  productivityScore: number;
  focusTime: number;
  distractionEvents: number;
}

interface PillarHealth {
  pillarId: string;
  pillarName: string;
  healthScore: number; // 0-100
  trend: 'improving' | 'stable' | 'declining';
  areasCount: number;
  activeProjectsCount: number;
  completedTasksCount: number;
  lastActivity: string;
  recommendations: string[];
}

interface AIInsight {
  id: string;
  type: 'productivity' | 'balance' | 'goal_progress' | 'time_management' | 'habit_formation';
  title: string;
  description: string;
  actionable: boolean;
  priority: 'low' | 'medium' | 'high' | 'critical';
  confidence: number; // 0-1
  suggestedActions: string[];
  basedOn: string[];
  validUntil: string;
}

interface TimeBlockingAnalysis {
  totalPlannedTime: number;
  totalActualTime: number;
  adherenceRate: number;
  commonOverruns: string[];
  underutilizedSlots: string[];
  optimalTimeBlocks: { activity: string; recommendedDuration: number; bestTimeSlot: string }[];
}

interface GoalProgressAnalytics {
  pillarId: string;
  goalId: string;
  currentProgress: number;
  projectedCompletion: string;
  velocityTrend: 'accelerating' | 'stable' | 'slowing';
  blockers: string[];
  accelerators: string[];
  recommendedAdjustments: string[];
}

class AdvancedAnalyticsService {
  private dataPoints: Map<string, AnalyticsDataPoint[]> = new Map();
  private insights: AIInsight[] = [];
  private lastAnalysisTime: string = new Date().toISOString();

  constructor() {
    this.loadStoredData();
    this.scheduleAnalysis();
  }

  private loadStoredData() {
    try {
      const stored = localStorage.getItem('aurum-analytics-data');
      if (stored) {
        const data = JSON.parse(stored);
        this.dataPoints = new Map(data.dataPoints || []);
        this.insights = data.insights || [];
        this.lastAnalysisTime = data.lastAnalysisTime || new Date().toISOString();
      }
    } catch (error) {
      console.warn('Failed to load analytics data:', error);
    }
  }

  private saveData() {
    try {
      const data = {
        dataPoints: Array.from(this.dataPoints.entries()),
        insights: this.insights,
        lastAnalysisTime: this.lastAnalysisTime
      };
      localStorage.setItem('aurum-analytics-data', JSON.stringify(data));
    } catch (error) {
      console.warn('Failed to save analytics data:', error);
    }
  }

  private scheduleAnalysis() {
    // Run analysis every hour
    setInterval(() => {
      this.runAnalysis();
    }, 60 * 60 * 1000);

    // Run initial analysis after a short delay
    setTimeout(() => {
      this.runAnalysis();
    }, 5000);
  }

  /**
   * Record a data point for analytics
   */
  recordDataPoint(category: string, value: number, metadata?: Record<string, any>) {
    const dataPoint: AnalyticsDataPoint = {
      timestamp: new Date().toISOString(),
      value,
      category,
      metadata
    };

    if (!this.dataPoints.has(category)) {
      this.dataPoints.set(category, []);
    }

    const categoryData = this.dataPoints.get(category)!;
    categoryData.push(dataPoint);

    // Keep only last 1000 data points per category
    if (categoryData.length > 1000) {
      categoryData.splice(0, categoryData.length - 1000);
    }

    this.saveData();
  }

  /**
   * Get productivity metrics for a time period
   */
  getProductivityMetrics(startDate: Date, endDate: Date): ProductivityMetrics {
    const taskCompletions = this.getDataPointsInRange('task_completed', startDate, endDate);
    const taskCreations = this.getDataPointsInRange('task_created', startDate, endDate);
    const focusEvents = this.getDataPointsInRange('focus_session', startDate, endDate);
    const distractionEvents = this.getDataPointsInRange('distraction', startDate, endDate);

    const completionTimes = taskCompletions
      .filter(dp => dp.metadata?.completionTime)
      .map(dp => dp.metadata!.completionTime as number);

    const averageCompletionTime = completionTimes.length > 0 
      ? completionTimes.reduce((sum, time) => sum + time, 0) / completionTimes.length
      : 0;

    const totalFocusTime = focusEvents.reduce((sum, dp) => sum + dp.value, 0);
    
    // Calculate productivity score (0-100)
    const tasksCompleted = taskCompletions.length;
    const tasksCreated = taskCreations.length;
    const completionRate = tasksCreated > 0 ? tasksCompleted / tasksCreated : 0;
    const focusScore = Math.min(totalFocusTime / (8 * 60), 1); // Assuming 8h target
    const distractionPenalty = Math.min(distractionEvents.length * 0.1, 0.3);
    
    const productivityScore = Math.round(
      (completionRate * 0.4 + focusScore * 0.4 + (1 - distractionPenalty) * 0.2) * 100
    );

    return {
      tasksCompleted,
      tasksCreated,
      averageCompletionTime,
      productivityScore,
      focusTime: totalFocusTime,
      distractionEvents: distractionEvents.length
    };
  }

  /**
   * Analyze pillar health across all pillars
   */
  async analyzePillarHealth(): Promise<PillarHealth[]> {
    // This would typically fetch from your data stores
    const pillars = await this.getPillarsData();
    
    return pillars.map(pillar => {
      const recentActivity = this.getDataPointsInRange(
        `pillar_activity_${pillar.id}`,
        new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // Last 7 days
        new Date()
      );

      const taskCompletions = this.getDataPointsInRange(
        `pillar_tasks_completed_${pillar.id}`,
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // Last 30 days
        new Date()
      );

      const healthScore = this.calculatePillarHealthScore(pillar, recentActivity, taskCompletions);
      const trend = this.calculateTrend(recentActivity);
      const recommendations = this.generatePillarRecommendations(pillar, healthScore, trend);

      return {
        pillarId: pillar.id,
        pillarName: pillar.name,
        healthScore,
        trend,
        areasCount: pillar.areas?.length || 0,
        activeProjectsCount: pillar.activeProjects?.length || 0,
        completedTasksCount: taskCompletions.length,
        lastActivity: recentActivity.length > 0 ? recentActivity[recentActivity.length - 1].timestamp : 'Never',
        recommendations
      };
    });
  }

  /**
   * Generate AI-powered insights
   */
  async generateAIInsights(): Promise<AIInsight[]> {
    const newInsights: AIInsight[] = [];
    
    // Productivity insights
    const productivityInsight = await this.analyzeProductivityPatterns();
    if (productivityInsight) newInsights.push(productivityInsight);

    // Work-life balance insights
    const balanceInsight = await this.analyzeWorkLifeBalance();
    if (balanceInsight) newInsights.push(balanceInsight);

    // Goal progress insights
    const goalInsights = await this.analyzeGoalProgress();
    newInsights.push(...goalInsights);

    // Time management insights
    const timeInsight = await this.analyzeTimeManagement();
    if (timeInsight) newInsights.push(timeInsight);

    // Filter out insights that are too similar to existing ones
    const filteredInsights = this.deduplicateInsights(newInsights);

    // Update insights array
    this.insights = [
      ...filteredInsights,
      ...this.insights.filter(insight => new Date(insight.validUntil) > new Date())
    ].slice(0, 20); // Keep only top 20 insights

    this.saveData();
    return this.insights;
  }

  /**
   * Analyze time blocking effectiveness
   */
  analyzeTimeBlocking(startDate: Date, endDate: Date): TimeBlockingAnalysis {
    const plannedBlocks = this.getDataPointsInRange('time_block_planned', startDate, endDate);
    const actualBlocks = this.getDataPointsInRange('time_block_actual', startDate, endDate);

    const totalPlannedTime = plannedBlocks.reduce((sum, dp) => sum + dp.value, 0);
    const totalActualTime = actualBlocks.reduce((sum, dp) => sum + dp.value, 0);
    
    const adherenceRate = totalPlannedTime > 0 ? totalActualTime / totalPlannedTime : 0;

    // Analyze overruns and underutilized slots
    const overruns = this.identifyTimeBlockOverruns(plannedBlocks, actualBlocks);
    const underutilized = this.identifyUnderutilizedSlots(plannedBlocks, actualBlocks);
    const optimal = this.recommendOptimalTimeBlocks();

    return {
      totalPlannedTime,
      totalActualTime,
      adherenceRate,
      commonOverruns: overruns,
      underutilizedSlots: underutilized,
      optimalTimeBlocks: optimal
    };
  }

  /**
   * Track goal progress with predictive analytics
   */
  analyzeGoalProgress(goalId: string): GoalProgressAnalytics {
    const progressData = this.getDataPointsInRange(
      `goal_progress_${goalId}`,
      new Date(Date.now() - 90 * 24 * 60 * 60 * 1000), // Last 90 days
      new Date()
    );

    const currentProgress = progressData.length > 0 ? progressData[progressData.length - 1].value : 0;
    const velocity = this.calculateVelocity(progressData);
    const projectedCompletion = this.projectCompletion(currentProgress, velocity);
    const velocityTrend = this.calculateVelocityTrend(progressData);

    return {
      pillarId: 'pillar-id', // Would come from goal data
      goalId,
      currentProgress,
      projectedCompletion,
      velocityTrend,
      blockers: this.identifyBlockers(progressData),
      accelerators: this.identifyAccelerators(progressData),
      recommendedAdjustments: this.recommendAdjustments(velocity, velocityTrend)
    };
  }

  // Private helper methods

  private getDataPointsInRange(category: string, startDate: Date, endDate: Date): AnalyticsDataPoint[] {
    const categoryData = this.dataPoints.get(category) || [];
    return categoryData.filter(dp => {
      const dpDate = new Date(dp.timestamp);
      return dpDate >= startDate && dpDate <= endDate;
    });
  }

  private async getPillarsData(): Promise<any[]> {
    // This would fetch from your actual pillar store
    try {
      const stored = localStorage.getItem('aurum-pillars');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  private calculatePillarHealthScore(pillar: any, recentActivity: AnalyticsDataPoint[], taskCompletions: AnalyticsDataPoint[]): number {
    let score = 50; // Base score

    // Activity boost
    if (recentActivity.length > 0) score += 20;
    if (recentActivity.length > 5) score += 10;

    // Task completion boost
    score += Math.min(taskCompletions.length * 2, 20);

    // Recency boost
    const lastActivityDate = recentActivity.length > 0 ? new Date(recentActivity[recentActivity.length - 1].timestamp) : null;
    if (lastActivityDate) {
      const daysSinceActivity = (Date.now() - lastActivityDate.getTime()) / (24 * 60 * 60 * 1000);
      if (daysSinceActivity < 1) score += 10;
      else if (daysSinceActivity > 7) score -= 15;
    }

    return Math.max(0, Math.min(100, score));
  }

  private calculateTrend(dataPoints: AnalyticsDataPoint[]): 'improving' | 'stable' | 'declining' {
    if (dataPoints.length < 3) return 'stable';

    const recent = dataPoints.slice(-3);
    const older = dataPoints.slice(-6, -3);

    const recentAvg = recent.reduce((sum, dp) => sum + dp.value, 0) / recent.length;
    const olderAvg = older.length > 0 ? older.reduce((sum, dp) => sum + dp.value, 0) / older.length : recentAvg;

    const improvement = (recentAvg - olderAvg) / olderAvg;

    if (improvement > 0.1) return 'improving';
    if (improvement < -0.1) return 'declining';
    return 'stable';
  }

  private generatePillarRecommendations(pillar: any, healthScore: number, trend: string): string[] {
    const recommendations: string[] = [];

    if (healthScore < 30) {
      recommendations.push('This pillar needs immediate attention');
      recommendations.push('Consider creating specific action items');
    } else if (healthScore < 60) {
      recommendations.push('Schedule regular check-ins for this pillar');
      recommendations.push('Break down large tasks into smaller ones');
    }

    if (trend === 'declining') {
      recommendations.push('Recent activity has decreased - consider what might be blocking progress');
    } else if (trend === 'improving') {
      recommendations.push('Great momentum! Consider what\'s working well to apply to other pillars');
    }

    return recommendations.slice(0, 3); // Limit to 3 recommendations
  }

  private async analyzeProductivityPatterns(): Promise<AIInsight | null> {
    const recentMetrics = this.getProductivityMetrics(
      new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      new Date()
    );

    if (recentMetrics.productivityScore < 50) {
      return {
        id: `productivity-${Date.now()}`,
        type: 'productivity',
        title: 'Productivity Score Below Average',
        description: `Your productivity score is ${recentMetrics.productivityScore}%. Consider focusing on task completion and reducing distractions.`,
        actionable: true,
        priority: 'medium',
        confidence: 0.8,
        suggestedActions: [
          'Use time blocking for focused work sessions',
          'Identify and eliminate common distractions',
          'Break large tasks into smaller, manageable pieces'
        ],
        basedOn: ['Task completion rate', 'Focus time', 'Distraction events'],
        validUntil: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
      };
    }

    return null;
  }

  private async analyzeWorkLifeBalance(): Promise<AIInsight | null> {
    // Analyze work vs personal pillar activity
    const workActivity = this.getDataPointsInRange('work_activity', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), new Date());
    const personalActivity = this.getDataPointsInRange('personal_activity', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), new Date());

    const workTime = workActivity.reduce((sum, dp) => sum + dp.value, 0);
    const personalTime = personalActivity.reduce((sum, dp) => sum + dp.value, 0);

    if (workTime > personalTime * 3) {
      return {
        id: `balance-${Date.now()}`,
        type: 'balance',
        title: 'Work-Life Balance Attention Needed',
        description: 'You\'ve been focusing heavily on work-related activities. Consider dedicating more time to personal growth and relationships.',
        actionable: true,
        priority: 'medium',
        confidence: 0.7,
        suggestedActions: [
          'Schedule dedicated time for personal pillars',
          'Set boundaries around work hours',
          'Plan activities that bring you joy and fulfillment'
        ],
        basedOn: ['Work vs personal activity ratio'],
        validUntil: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString()
      };
    }

    return null;
  }

  private async analyzeGoalProgress(): Promise<AIInsight[]> {
    // This would analyze all active goals
    return [];
  }

  private async analyzeTimeManagement(): Promise<AIInsight | null> {
    const timeBlocks = this.getDataPointsInRange('time_block_adherence', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), new Date());
    
    if (timeBlocks.length > 0) {
      const averageAdherence = timeBlocks.reduce((sum, dp) => sum + dp.value, 0) / timeBlocks.length;
      
      if (averageAdherence < 0.6) {
        return {
          id: `time-management-${Date.now()}`,
          type: 'time_management',
          title: 'Time Block Adherence Could Improve',
          description: `You're following your planned schedule ${Math.round(averageAdherence * 100)}% of the time. Better planning might help.`,
          actionable: true,
          priority: 'low',
          confidence: 0.6,
          suggestedActions: [
            'Build in buffer time between activities',
            'Be more realistic about task duration estimates',
            'Identify common causes of schedule disruption'
          ],
          basedOn: ['Time block adherence rate'],
          validUntil: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
        };
      }
    }

    return null;
  }

  private deduplicateInsights(insights: AIInsight[]): AIInsight[] {
    // Remove insights that are too similar
    const unique: AIInsight[] = [];
    
    for (const insight of insights) {
      const isDuplicate = unique.some(existing => 
        existing.type === insight.type && 
        existing.title.toLowerCase().includes(insight.title.toLowerCase().slice(0, 10))
      );
      
      if (!isDuplicate) {
        unique.push(insight);
      }
    }
    
    return unique;
  }

  private identifyTimeBlockOverruns(planned: AnalyticsDataPoint[], actual: AnalyticsDataPoint[]): string[] {
    // Implementation would compare planned vs actual times
    return ['Meetings', 'Email processing', 'Administrative tasks'];
  }

  private identifyUnderutilizedSlots(planned: AnalyticsDataPoint[], actual: AnalyticsDataPoint[]): string[] {
    return ['Early morning slots', 'Late afternoon slots'];
  }

  private recommendOptimalTimeBlocks(): { activity: string; recommendedDuration: number; bestTimeSlot: string }[] {
    return [
      { activity: 'Deep work', recommendedDuration: 90, bestTimeSlot: '9:00-10:30 AM' },
      { activity: 'Email processing', recommendedDuration: 30, bestTimeSlot: '11:00-11:30 AM' },
      { activity: 'Meetings', recommendedDuration: 45, bestTimeSlot: '2:00-2:45 PM' }
    ];
  }

  private calculateVelocity(progressData: AnalyticsDataPoint[]): number {
    if (progressData.length < 2) return 0;
    
    const recent = progressData.slice(-5);
    const timeDiff = new Date(recent[recent.length - 1].timestamp).getTime() - new Date(recent[0].timestamp).getTime();
    const progressDiff = recent[recent.length - 1].value - recent[0].value;
    
    return progressDiff / (timeDiff / (24 * 60 * 60 * 1000)); // Progress per day
  }

  private projectCompletion(currentProgress: number, velocity: number): string {
    if (velocity <= 0) return 'Unable to project';
    
    const remainingProgress = 100 - currentProgress;
    const daysToComplete = remainingProgress / velocity;
    const completionDate = new Date(Date.now() + daysToComplete * 24 * 60 * 60 * 1000);
    
    return completionDate.toLocaleDateString();
  }

  private calculateVelocityTrend(progressData: AnalyticsDataPoint[]): 'accelerating' | 'stable' | 'slowing' {
    if (progressData.length < 6) return 'stable';
    
    const recentVelocity = this.calculateVelocity(progressData.slice(-3));
    const olderVelocity = this.calculateVelocity(progressData.slice(-6, -3));
    
    const change = (recentVelocity - olderVelocity) / Math.abs(olderVelocity);
    
    if (change > 0.2) return 'accelerating';
    if (change < -0.2) return 'slowing';
    return 'stable';
  }

  private identifyBlockers(progressData: AnalyticsDataPoint[]): string[] {
    // Analyze patterns in low-progress periods
    return ['Competing priorities', 'Lack of resources', 'Unclear next steps'];
  }

  private identifyAccelerators(progressData: AnalyticsDataPoint[]): string[] {
    // Analyze patterns in high-progress periods
    return ['Clear deadlines', 'Collaborative support', 'Focused time blocks'];
  }

  private recommendAdjustments(velocity: number, trend: string): string[] {
    const recommendations: string[] = [];
    
    if (velocity < 0.5) {
      recommendations.push('Break down goals into smaller milestones');
      recommendations.push('Allocate more time to this goal');
    }
    
    if (trend === 'slowing') {
      recommendations.push('Review and address current blockers');
      recommendations.push('Consider adjusting scope or timeline');
    }
    
    return recommendations;
  }

  private async runAnalysis() {
    console.log('Running scheduled analytics analysis...');
    
    try {
      await this.generateAIInsights();
      this.lastAnalysisTime = new Date().toISOString();
      this.saveData();
    } catch (error) {
      console.error('Error during analytics analysis:', error);
    }
  }

  /**
   * Get current insights
   */
  getCurrentInsights(): AIInsight[] {
    return this.insights.filter(insight => new Date(insight.validUntil) > new Date());
  }

  /**
   * Dismiss an insight
   */
  dismissInsight(insightId: string) {
    this.insights = this.insights.filter(insight => insight.id !== insightId);
    this.saveData();
  }

  /**
   * Get analytics summary for dashboard
   */
  getAnalyticsSummary() {
    const recentMetrics = this.getProductivityMetrics(
      new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      new Date()
    );

    const activeInsights = this.getCurrentInsights();
    const criticalInsights = activeInsights.filter(i => i.priority === 'critical').length;
    const highPriorityInsights = activeInsights.filter(i => i.priority === 'high').length;

    return {
      productivityScore: recentMetrics.productivityScore,
      tasksCompleted: recentMetrics.tasksCompleted,
      focusHours: Math.round(recentMetrics.focusTime / 60),
      totalInsights: activeInsights.length,
      criticalInsights,
      highPriorityInsights,
      lastAnalysis: this.lastAnalysisTime
    };
  }
}

export const advancedAnalyticsService = new AdvancedAnalyticsService();
export type { 
  ProductivityMetrics, 
  PillarHealth, 
  AIInsight, 
  TimeBlockingAnalysis, 
  GoalProgressAnalytics 
};