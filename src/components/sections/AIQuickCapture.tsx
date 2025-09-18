import { useState } from 'react';
import { motion } from 'motion/react';
import { Brain, Zap, BarChart3, Settings, Plus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import QuickCaptureManager from '../enhanced/QuickCaptureManager';
import RAGInsightsDashboard from '../enhanced/RAGInsightsDashboard';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';

export default function AIQuickCapture() {
  const [activeTab, setActiveTab] = useState('capture');
  const { 
    openQuickCapture, 
    getUnprocessedQuickCapture,
    quickCaptureItems 
  } = useEnhancedFeaturesStore();

  const unprocessedCount = getUnprocessedQuickCapture().length;
  const totalCaptureCount = quickCaptureItems.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <div className="flex items-center justify-center space-x-3">
          <div className="p-3 bg-[rgba(244,208,63,0.1)] rounded-xl">
            <Brain className="w-8 h-8 text-[#F4D03F]" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">AI Quick Capture</h1>
            <p className="text-[#B8BCC8]">
              Advanced RAG-powered categorization for instant organization
            </p>
          </div>
        </div>

        <div className="flex items-center justify-center space-x-4">
          <Badge variant="outline" className="border-[#F4D03F] text-[#F4D03F]">
            <Zap className="w-3 h-3 mr-1" />
            RAG Enabled
          </Badge>
          <Badge variant="outline" className="border-[rgba(244,208,63,0.3)] text-[#B8BCC8]">
            {totalCaptureCount} total items
          </Badge>
          {unprocessedCount > 0 && (
            <Badge className="bg-red-500 text-white">
              {unprocessedCount} pending
            </Badge>
          )}
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-white mb-2">Quick Actions</h2>
                <p className="text-[#B8BCC8]">
                  Capture thoughts instantly with AI-powered categorization
                </p>
              </div>
              <Button
                onClick={openQuickCapture}
                className="aurum-gradient text-[#0B0D14] hover:shadow-lg"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Capture
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Main Content Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 glassmorphism-panel p-1">
            <TabsTrigger 
              value="capture" 
              className="data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14]"
            >
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4" />
                <span>Quick Capture</span>
                {unprocessedCount > 0 && (
                  <Badge className="bg-red-500 text-white ml-2 h-5 min-w-5 text-xs">
                    {unprocessedCount}
                  </Badge>
                )}
              </div>
            </TabsTrigger>
            <TabsTrigger 
              value="insights" 
              className="data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14]"
            >
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-4 h-4" />
                <span>RAG Insights</span>
              </div>
            </TabsTrigger>
            <TabsTrigger 
              value="settings" 
              className="data-[state=active]:bg-[#F4D03F] data-[state=active]:text-[#0B0D14]"
            >
              <div className="flex items-center space-x-2">
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </div>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="capture" className="space-y-6">
            <QuickCaptureManager />
          </TabsContent>

          <TabsContent value="insights" className="space-y-6">
            <RAGInsightsDashboard />
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="w-5 h-5 text-[#F4D03F]" />
                  <span>RAG Configuration</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* RAG Settings */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 glassmorphism-panel rounded-lg">
                    <div>
                      <h4 className="text-white font-medium">Auto-categorization</h4>
                      <p className="text-[#B8BCC8] text-sm">
                        Automatically suggest categories for new captures
                      </p>
                    </div>
                    <div className="text-green-400 font-medium">Enabled</div>
                  </div>

                  <div className="flex items-center justify-between p-4 glassmorphism-panel rounded-lg">
                    <div>
                      <h4 className="text-white font-medium">Learning Mode</h4>
                      <p className="text-[#B8BCC8] text-sm">
                        Continuously improve from user feedback
                      </p>
                    </div>
                    <div className="text-green-400 font-medium">Active</div>
                  </div>

                  <div className="flex items-center justify-between p-4 glassmorphism-panel rounded-lg">
                    <div>
                      <h4 className="text-white font-medium">Confidence Threshold</h4>
                      <p className="text-[#B8BCC8] text-sm">
                        Minimum confidence required for auto-categorization
                      </p>
                    </div>
                    <div className="text-[#F4D03F] font-medium">70%</div>
                  </div>

                  <div className="flex items-center justify-between p-4 glassmorphism-panel rounded-lg">
                    <div>
                      <h4 className="text-white font-medium">Context Analysis</h4>
                      <p className="text-[#B8BCC8] text-sm">
                        Use time, recent activity, and user patterns for categorization
                      </p>
                    </div>
                    <div className="text-green-400 font-medium">Enhanced</div>
                  </div>
                </div>

                {/* Future enhancements placeholder */}
                <div className="border-t border-[rgba(244,208,63,0.1)] pt-6">
                  <h4 className="text-white font-medium mb-4">Coming Soon</h4>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3 text-[#B8BCC8] text-sm">
                      <div className="w-2 h-2 bg-[#F4D03F] rounded-full opacity-50"></div>
                      <span>Custom categorization rules</span>
                    </div>
                    <div className="flex items-center space-x-3 text-[#B8BCC8] text-sm">
                      <div className="w-2 h-2 bg-[#F4D03F] rounded-full opacity-50"></div>
                      <span>Integration with external AI models</span>
                    </div>
                    <div className="flex items-center space-x-3 text-[#B8BCC8] text-sm">
                      <div className="w-2 h-2 bg-[#F4D03F] rounded-full opacity-50"></div>
                      <span>Advanced sentiment analysis</span>
                    </div>
                    <div className="flex items-center space-x-3 text-[#B8BCC8] text-sm">
                      <div className="w-2 h-2 bg-[#F4D03F] rounded-full opacity-50"></div>
                      <span>Collaborative learning across users</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>

      {/* Feature Highlights */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
          <CardContent className="p-6 text-center">
            <div className="p-3 bg-[rgba(244,208,63,0.1)] rounded-lg w-fit mx-auto mb-4">
              <Brain className="w-6 h-6 text-[#F4D03F]" />
            </div>
            <h3 className="text-white font-medium mb-2">Smart Categorization</h3>
            <p className="text-[#B8BCC8] text-sm">
              RAG-powered AI analyzes context, keywords, and patterns to suggest the perfect category
            </p>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
          <CardContent className="p-6 text-center">
            <div className="p-3 bg-[rgba(16,185,129,0.1)] rounded-lg w-fit mx-auto mb-4">
              <Zap className="w-6 h-6 text-green-400" />
            </div>
            <h3 className="text-white font-medium mb-2">Continuous Learning</h3>
            <p className="text-[#B8BCC8] text-sm">
              System improves accuracy over time by learning from your feedback and corrections
            </p>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0 bg-card text-card-foreground">
          <CardContent className="p-6 text-center">
            <div className="p-3 bg-[rgba(59,130,246,0.1)] rounded-lg w-fit mx-auto mb-4">
              <BarChart3 className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-white font-medium mb-2">Advanced Analytics</h3>
            <p className="text-[#B8BCC8] text-sm">
              Detailed insights into categorization accuracy and system performance
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}