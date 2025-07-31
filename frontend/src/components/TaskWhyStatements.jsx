import React, { useState, useEffect } from 'react';
import { BulbIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/outline';

const TaskWhyStatements = ({ taskIds = null, showAll = false }) => {
  const [whyStatements, setWhyStatements] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(showAll);

  useEffect(() => {
    fetchWhyStatements();
  }, [taskIds]);

  const fetchWhyStatements = async () => {
    try {
      setLoading(true);
      setError(null);

      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');

      if (!token) {
        setError('Authentication required');
        return;
      }

      // Build URL with task IDs if provided
      let url = `${BACKEND_URL}/api/ai/task-why-statements`;
      if (taskIds && taskIds.length > 0) {
        url += `?task_ids=${taskIds.join(',')}`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setWhyStatements(data.why_statements || []);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load task context');
      }
    } catch (err) {
      console.error('Error fetching why statements:', err);
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleExpanded = () => {
    setExpanded(!expanded);
  };

  if (loading) {
    return (
      <div className="mt-4 p-4 bg-gray-800 rounded-lg">
        <div className="flex items-center space-x-2">
          <BulbIcon className="h-5 w-5 text-yellow-400 animate-pulse" />
          <span className="text-gray-300">Loading task context...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-4 p-4 bg-red-900 border border-red-700 rounded-lg">
        <div className="flex items-center space-x-2">
          <BulbIcon className="h-5 w-5 text-red-400" />
          <span className="text-red-300">Error: {error}</span>
        </div>
      </div>
    );
  }

  if (!whyStatements.length) {
    return (
      <div className="mt-4 p-4 bg-gray-800 rounded-lg">
        <div className="flex items-center space-x-2">
          <BulbIcon className="h-5 w-5 text-gray-400" />
          <span className="text-gray-400">No active tasks found for context</span>
        </div>
      </div>
    );
  }

  const displayedStatements = expanded ? whyStatements : whyStatements.slice(0, 3);

  return (
    <div className="mt-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <BulbIcon className="h-5 w-5 text-yellow-400" />
          <h3 className="text-lg font-semibold text-white">Why These Tasks Matter</h3>
        </div>
        {whyStatements.length > 3 && (
          <button
            onClick={handleToggleExpanded}
            className="flex items-center space-x-1 text-yellow-400 hover:text-yellow-300"
          >
            <span className="text-sm">
              {expanded ? 'Show Less' : `Show All (${whyStatements.length})`}
            </span>
            {expanded ? (
              <ChevronUpIcon className="h-4 w-4" />
            ) : (
              <ChevronDownIcon className="h-4 w-4" />
            )}
          </button>
        )}
      </div>

      <div className="space-y-4">
        {displayedStatements.map((statement, index) => (
          <div key={statement.task_id || index} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-2 h-2 mt-2 bg-yellow-400 rounded-full"></div>
              <div className="flex-1">
                <h4 className="font-medium text-white mb-1">{statement.task_name}</h4>
                <p className="text-gray-300 text-sm leading-relaxed">{statement.why_statement}</p>
                
                {/* Show project and pillar connections if available */}
                {(statement.project_connection || statement.pillar_connection) && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {statement.project_connection && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-900 text-blue-200">
                        📋 {statement.project_connection}
                      </span>
                    )}
                    {statement.pillar_connection && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-900 text-purple-200">
                        🏛️ {statement.pillar_connection}
                      </span>
                    )}
                    {statement.area_connection && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-900 text-green-200">
                        🎯 {statement.area_connection}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary footer */}
      <div className="mt-4 p-3 bg-gray-900 rounded-lg">
        <p className="text-xs text-gray-400 text-center">
          Showing context for {displayedStatements.length} of {whyStatements.length} active tasks
        </p>
      </div>
    </div>
  );
};

export default TaskWhyStatements;