/**
 * Privacy Controls Section Component
 * Main section component for granular privacy controls
 */

import React from 'react';
import { motion } from 'motion/react';
import GranularPrivacyControls from '../enhanced/GranularPrivacyControls';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Shield, Lock, Eye, Brain } from 'lucide-react';

const PrivacyControls: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="container-responsive space-y-6"
    >
      {/* Header Card */}
      <Card className="glassmorphism-card">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-3">
            <div className="p-2 bg-primary/20 rounded-full">
              <Shield className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Privacy Controls</h1>
              <p className="text-muted-foreground text-sm mt-1">
                Comprehensive control over your data privacy and AI feature permissions
              </p>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-3 glassmorphism-panel rounded-lg">
              <Lock className="w-5 h-5 text-blue-400" />
              <div>
                <h3 className="font-medium text-sm">Data Protection</h3>
                <p className="text-xs text-muted-foreground">Granular control over data collection</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3 p-3 glassmorphism-panel rounded-lg">
              <Brain className="w-5 h-5 text-purple-400" />
              <div>
                <h3 className="font-medium text-sm">AI Transparency</h3>
                <p className="text-xs text-muted-foreground">Control AI features and processing</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3 p-3 glassmorphism-panel rounded-lg">
              <Eye className="w-5 h-5 text-green-400" />
              <div>
                <h3 className="font-medium text-sm">Audit Trail</h3>
                <p className="text-xs text-muted-foreground">Complete visibility into data usage</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Granular Privacy Controls Component */}
      <GranularPrivacyControls />
    </motion.div>
  );
};

export default PrivacyControls;