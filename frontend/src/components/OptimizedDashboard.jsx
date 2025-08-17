import React from 'react';
import AlignmentProgressBar from './AlignmentProgressBar';
import CalendarBoard from './CalendarBoard';

const Dashboard = () => {
  return (
    <div className="min-h-screen p-4 sm:p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      {/* Full-width container */}
      {/* Top alignment score progress */}
      <AlignmentProgressBar />

      {/* Calendar-first planning hub (full width) */}
      <CalendarBoard />
    </div>
  );
};

export default Dashboard;