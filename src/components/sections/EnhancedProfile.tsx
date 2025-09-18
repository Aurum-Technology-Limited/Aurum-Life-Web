/**
 * Enhanced Profile Section Component
 * Main section component for the enhanced user profile
 */

import React from 'react';
import { motion } from 'motion/react';
import EnhancedUserProfile from '../enhanced/EnhancedUserProfile';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { User, Sparkles } from 'lucide-react';

const EnhancedProfile: React.FC = () => {
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
              <User className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Enhanced Profile</h1>
              <p className="text-muted-foreground text-sm mt-1">
                Manage your profile, AI preferences, and view personal insights
              </p>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Enhanced User Profile Component */}
      <EnhancedUserProfile />
    </motion.div>
  );
};

export default EnhancedProfile;