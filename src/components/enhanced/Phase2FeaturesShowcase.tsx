/**
 * Phase 2 Features Showcase Component
 * Demonstrates and provides access to all Phase 2 advanced features
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Zap, Brain, Search, Smartphone, 
  BarChart3, Sync, Cloud, Star, 
  Lightbulb, Target, TrendingUp,
  ChevronRight, X, Play, Settings,
  Download, Share2, Globe, Wifi
} from 'lucide-react';
import { usePhase2Store, useAdvancedAnalytics, useSmartSearch, usePWAFeatures } from '../../stores/phase2IntegrationStore';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import SmartSearchInterface from './SmartSearchInterface';
import AdvancedAnalyticsDashboard from './AdvancedAnalyticsDashboard';
import Phase2StatusBar from './Phase2StatusBar';
import toast from '../../utils/toast';

interface Phase2FeaturesShowcaseProps {
  className?: string;
}

const Phase2FeaturesShowcase: React.FC<Phase2FeaturesShowcaseProps> = ({
  className = ''
}) => {
  const [activeDemo, setActiveDemo] = useState<string | null>(null);
  const [showSearchDemo, setShowSearchDemo] = useState(false);
  const [showAnalyticsDemo, setShowAnalyticsDemo] = useState(false);

  const {
    productivityMetrics,
    aiInsights,
    loadAnalytics,
    generateInsights,
    trackAnalyticsEvent
  } = useAdvancedAnalytics();

  const {
    searchResults,
    performSearch,
    clearSearchResults
  } = useSmartSearch();

  const {
    pwaCapabilities,
    installPromptAvailable,
    promptInstall,
    shareContent,
    cacheOfflineData
  } = usePWAFeatures();

  const phase2Features = [
    {
      id: 'real-time-sync',
      title: 'Real-Time Data Synchronization',
      description: 'Seamless data sync across devices with conflict resolution',
      icon: <Sync className="w-6 h-6" />,
      color: 'bg-blue-500/20 text-blue-300',
      capabilities: [
        'Automatic background sync',
        'Offline queue management', 
        'Conflict resolution',
        'Real-time updates'
      ],
      demoAction: () => {
        toast.success('Real-time sync is running in the background!');
        // Simulate a sync event
        usePhase2Store.getState().publishDataChange({
          type: 'task',
          operation: 'update',
          data: { id: 'demo', title: 'Demo Task Updated' },
          userId: 'demo'
        });
      }
    },
    {
      id: 'ai-analytics',
      title: 'AI-Powered Analytics',
      description: 'Intelligent insights and predictive productivity analytics',
      icon: <Brain className="w-6 h-6" />,
      color: 'bg-purple-500/20 text-purple-300',
      capabilities: [
        'Productivity scoring',
        'Pillar health analysis',
        'AI-generated insights',
        'Predictive analytics'
      ],
      demoAction: () => setShowAnalyticsDemo(true)
    },
    {
      id: 'smart-search',
      title: 'Intelligent Search',
      description: 'Cross-hierarchy search with AI suggestions and filters',
      icon: <Search className="w-6 h-6" />,
      color: 'bg-green-500/20 text-green-300',
      capabilities: [
        'Semantic search',
        'Smart suggestions',
        'Advanced filters',
        'Search history'
      ],
      demoAction: () => setShowSearchDemo(true)
    },
    {
      id: 'pwa-features',
      title: 'Progressive Web App',
      description: 'Native app experience with offline capabilities',
      icon: <Smartphone className="w-6 h-6" />,
      color: 'bg-orange-500/20 text-orange-300',
      capabilities: [
        'Offline functionality',
        'App installation',
        'Push notifications',
        'Background sync'
      ],
      demoAction: async () => {
        if (installPromptAvailable) {
          await promptInstall();
        } else {
          await cacheOfflineData();
          toast.success('Data cached for offline use!');
        }
      }
    }
  ];

  const handleDemoFeature = async (feature: typeof phase2Features[0]) => {
    setActiveDemo(feature.id);
    
    // Track demo interaction
    trackAnalyticsEvent('feature_demo', 1, {
      feature: feature.id,
      timestamp: new Date().toISOString()
    });

    try {
      await feature.demoAction();
    } catch (error) {
      console.error('Demo error:', error);
      toast.error('Demo failed to run');
    }

    // Clear active demo after animation
    setTimeout(() => setActiveDemo(null), 2000);
  };

  const handleShareFeatures = async () => {
    await shareContent({
      title: 'Aurum Life Phase 2 Features',
      text: 'Check out these amazing new features in Aurum Life!',
      url: window.location.href
    });
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center space-y-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 px-4 py-2 glassmorphism-panel rounded-full"
        >
          <Star className="w-5 h-5 text-primary" />
          <span className="text-sm font-medium text-primary">Phase 2 Features</span>
          <Badge variant="secondary" className="text-xs">New</Badge>
        </motion.div>
        
        <h1 className="text-3xl font-bold text-foreground">
          Advanced Capabilities
        </h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Experience the next level of personal productivity with AI-powered insights, 
          real-time synchronization, and progressive web app features.
        </p>
      </div>

      {/* Phase 2 Status Bar */}
      <Phase2StatusBar />

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {phase2Features.map((feature, index) => (
          <motion.div
            key={feature.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className={`glassmorphism-card transition-all duration-300 ${
              activeDemo === feature.id ? 'ring-2 ring-primary scale-105' : 'hover:scale-102'
            }`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-full ${feature.color}`}>
                      {feature.icon}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{feature.title}</CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Capabilities List */}
                <div className="space-y-2">
                  {feature.capabilities.map((capability, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                      <span className="text-foreground">{capability}</span>
                    </div>
                  ))}
                </div>

                {/* Demo Button */}
                <Button
                  onClick={() => handleDemoFeature(feature)}
                  disabled={activeDemo === feature.id}
                  className="w-full group"
                  variant="outline"
                >
                  {activeDemo === feature.id ? (
                    <>
                      <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full mr-2" />
                      Running Demo...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Try Demo
                      <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-0.5 transition-transform" />
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Quick Stats */}
      {(productivityMetrics || aiInsights.length > 0) && (
        <Card className="glassmorphism-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              Phase 2 Analytics Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {productivityMetrics && (
                <div className="text-center p-4 glassmorphism-panel rounded-lg">
                  <div className="text-2xl font-bold text-primary">
                    {productivityMetrics.productivityScore}%
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Productivity Score
                  </div>
                </div>
              )}
              
              <div className="text-center p-4 glassmorphism-panel rounded-lg">
                <div className="text-2xl font-bold text-green-400">
                  {aiInsights.length}
                </div>
                <div className="text-xs text-muted-foreground">
                  AI Insights
                </div>
              </div>
              
              <div className="text-center p-4 glassmorphism-panel rounded-lg">
                <div className="text-2xl font-bold text-blue-400">
                  {searchResults.length}
                </div>
                <div className="text-xs text-muted-foreground">
                  Search Results
                </div>
              </div>
              
              <div className="text-center p-4 glassmorphism-panel rounded-lg">
                <div className="text-2xl font-bold text-orange-400">
                  {Object.values(pwaCapabilities).filter(Boolean).length}
                </div>
                <div className="text-xs text-muted-foreground">
                  PWA Features
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap justify-center gap-4">
        <Button
          onClick={loadAnalytics}
          variant="outline"
          className="flex items-center gap-2"
        >
          <TrendingUp className="w-4 h-4" />
          Refresh Analytics
        </Button>
        
        <Button
          onClick={generateInsights}
          variant="outline"
          className="flex items-center gap-2"
        >
          <Lightbulb className="w-4 h-4" />
          Generate AI Insights
        </Button>
        
        <Button
          onClick={handleShareFeatures}
          variant="outline"
          className="flex items-center gap-2"
        >
          <Share2 className="w-4 h-4" />
          Share Features
        </Button>
        
        {installPromptAvailable && (
          <Button
            onClick={promptInstall}
            className="flex items-center gap-2 bg-primary text-primary-foreground"
          >
            <Download className="w-4 h-4" />
            Install App
          </Button>
        )}
      </div>

      {/* Search Demo Modal */}
      <Dialog open={showSearchDemo} onOpenChange={setShowSearchDemo}>
        <DialogContent className="max-w-4xl max-h-[80vh] p-0 glassmorphism-card">
          <DialogHeader className="p-6 pb-0">
            <DialogTitle className="flex items-center gap-2">
              <Search className="w-5 h-5 text-primary" />
              Smart Search Demo
            </DialogTitle>
          </DialogHeader>
          <div className="p-6">
            <SmartSearchInterface 
              onClose={() => setShowSearchDemo(false)}
              placeholder="Try searching for tasks, projects, or any content..."
            />
          </div>
        </DialogContent>
      </Dialog>

      {/* Analytics Demo Modal */}
      <Dialog open={showAnalyticsDemo} onOpenChange={setShowAnalyticsDemo}>
        <DialogContent className="max-w-6xl max-h-[90vh] p-0 glassmorphism-card">
          <DialogHeader className="p-6 pb-0">
            <DialogTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary" />
              Advanced Analytics Demo
            </DialogTitle>
          </DialogHeader>
          <div className="p-6 max-h-[calc(90vh-100px)] overflow-y-auto custom-scrollbar">
            <AdvancedAnalyticsDashboard />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Phase2FeaturesShowcase;