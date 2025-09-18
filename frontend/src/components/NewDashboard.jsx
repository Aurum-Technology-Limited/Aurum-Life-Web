import React from 'react';
import { StrategicOverview } from './dashboard/StrategicOverview';
import { SystemStatus } from './dashboard/SystemStatus';
import { TodaysFocus } from './dashboard/TodaysFocus';
import { AIInsights } from './dashboard/AIInsights';
import { StrategicMetrics } from './dashboard/StrategicMetrics';
import { StrategicIntelligence } from './dashboard/StrategicIntelligence';
import { StrategicProjectAssessment } from './StrategicProjectAssessment';
import { QuickActions } from './dashboard/QuickActions';

/**
 * New Dashboard component with modern design
 * Converted from TypeScript to JavaScript
 */
const NewDashboard = () => {
  return (
    <section className="space-y-4 lg:space-y-6">
      {/* Strategic Overview + System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 lg:gap-6">
        <div className="xl:col-span-2">
          <StrategicOverview />
        </div>
        <div>
          <SystemStatus />
        </div>
      </div>

      {/* Today's Focus + AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 lg:gap-6">
        <div className="xl:col-span-2">
          <TodaysFocus />
        </div>
        <div>
          <AIInsights />
        </div>
      </div>

      {/* Strategic Metrics Panel */}
      <StrategicMetrics />

      {/* Strategic Intelligence Panel */}
      <StrategicIntelligence />

      {/* Strategic Project Assessment */}
      <StrategicProjectAssessment />

      {/* Quick Actions */}
      <QuickActions />
    </section>
  );
};

export default NewDashboard;
