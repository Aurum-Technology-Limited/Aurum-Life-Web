import React from 'react';

const Dashboard = () => {
  return (
    <div className="min-h-screen p-4 sm:p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      {/* Full-width container */}
      {/* Top alignment score progress - temporarily removed during refactoring */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
        <h3 className="text-lg font-semibold text-white mb-2">Alignment Progress</h3>
        <p className="text-gray-400 text-sm">
          Alignment progress tracking has been temporarily removed during refactoring.
        </p>
      </div>

      {/* Calendar-first planning hub - temporarily removed during refactoring */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-2">Calendar Board</h3>
        <p className="text-gray-400 text-sm">
          Calendar planning has been temporarily removed during refactoring.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;