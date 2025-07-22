import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
} from 'chart.js';
import { Pie, Bar, Doughnut } from 'react-chartjs-2';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar, 
  Filter,
  Target,
  CheckCircle2,
  Clock,
  AlertTriangle
} from 'lucide-react';
import { insightsAPI } from '../services/api';
import { useDataContext } from '../contexts/DataContext';
import Breadcrumb from './Breadcrumb';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Insights = () => {
  console.log('📊 Insights component initialized!');
  
  const [insightsData, setInsightsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDateRange, setSelectedDateRange] = useState('all_time');
  const [selectedAreaId, setSelectedAreaId] = useState(null); // For drill-down functionality
  const [selectedAreaName, setSelectedAreaName] = useState(''); // For breadcrumb display

  const dateRangeOptions = [
    { value: 'weekly', label: 'Last 7 Days' },
    { value: 'monthly', label: 'Last 30 Days' },
    { value: 'yearly', label: 'Last Year' },
    { value: 'all_time', label: 'All Time' }
  ];

  const loadInsightsData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Build API URL with filters
      let apiUrl = `/insights?date_range=${selectedDateRange}`;
      if (selectedAreaId) {
        apiUrl += `&area_id=${selectedAreaId}`;
      }
      
      const response = await insightsAPI.getInsights(selectedDateRange, selectedAreaId);
      setInsightsData(response.data);
      console.log('📊 Insights data loaded:', response.data);
    } catch (err) {
      setError('Failed to load insights data');
      console.error('Error loading insights:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInsightsData();
  }, [selectedDateRange, selectedAreaId]); // Re-fetch when date range or area changes

  const handleAreaClick = (areaId, areaName) => {
    console.log('🖱️ Area clicked:', areaId, areaName);
    setSelectedAreaId(areaId);
    setSelectedAreaName(areaName);
  };

  const handleBackToGlobal = () => {
    console.log('🔄 Returning to global view');
    setSelectedAreaId(null);
    setSelectedAreaName('');
  };

  const handleDateRangeChange = (range) => {
    setSelectedDateRange(range);
    // Keep current area selection when changing date range
  };

  // Generate breadcrumb items based on current state
  const getBreadcrumbItems = () => {
    const items = [
      {
        name: 'Insights',
        onClick: selectedAreaId ? handleBackToGlobal : undefined,
        href: selectedAreaId ? '#' : undefined
      }
    ];

    if (selectedAreaId && selectedAreaName) {
      items.push({
        name: selectedAreaName,
        href: undefined,
        onClick: undefined
      });
    }

    return items;
  };
  const taskStatusChartData = {
    labels: ['Completed', 'In Progress', 'To Do', 'Overdue'],
    datasets: [
      {
        data: insightsData ? [
          insightsData.task_status_breakdown.completed,
          insightsData.task_status_breakdown.in_progress,
          insightsData.task_status_breakdown.todo,
          insightsData.task_status_breakdown.overdue
        ] : [],
        backgroundColor: [
          '#10B981', // Green for completed
          '#F59E0B', // Yellow for in progress
          '#6B7280', // Gray for todo
          '#EF4444'  // Red for overdue
        ],
        borderWidth: 2,
        borderColor: '#1F2937'
      }
    ]
  };

  const areasChartData = {
    labels: insightsData?.areas?.map(area => area.name) || [],
    datasets: [
      {
        label: 'Completion %',
        data: insightsData?.areas?.map(area => area.completion_percentage) || [],
        backgroundColor: insightsData?.areas?.map(area => area.color + '80') || [],
        borderColor: insightsData?.areas?.map(area => area.color) || [],
        borderWidth: 2
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#ffffff',
          padding: 20
        }
      },
      tooltip: {
        backgroundColor: '#1F2937',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#F4B400',
        borderWidth: 1
      }
    },
    onClick: (event, activeElements) => {
      // Handle click on Progress by Area chart
      if (activeElements.length > 0 && insightsData?.areas) {
        const clickedIndex = activeElements[0].index;
        const clickedArea = insightsData.areas[clickedIndex];
        if (clickedArea && !selectedAreaId) { // Only drill down if not already filtered
          handleAreaClick(clickedArea.id, clickedArea.name);
        }
      }
    },
    scales: !selectedAreaId && insightsData?.areas?.length > 0 ? {
      y: {
        beginAtZero: true,
        max: 100,
        grid: {
          color: '#374151'
        },
        ticks: {
          color: '#9CA3AF',
          callback: function(value) {
            return value + '%';
          }
        }
      },
      x: {
        grid: {
          color: '#374151'
        },
        ticks: {
          color: '#9CA3AF'
        }
      }
    } : undefined
  };

  if (loading) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-64 bg-gray-800 rounded-xl"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-900/20 border border-red-600 rounded-lg p-6 text-center">
            <AlertTriangle className="mx-auto h-12 w-12 text-red-400 mb-4" />
            <h3 className="text-lg font-medium text-red-400 mb-2">Error Loading Insights</h3>
            <p className="text-red-300">{error}</p>
            <button
              onClick={loadInsightsData}
              className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-7xl mx-auto">
        {/* Breadcrumb */}
        <Breadcrumb items={getBreadcrumbItems()} />
        
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
              {selectedAreaId ? `${selectedAreaName} - Insights` : 'Productivity Insights'}
            </h1>
            <p className="text-gray-400 mt-1">
              {selectedAreaId 
                ? `Detailed insights for ${selectedAreaName}` 
                : 'Data-driven overview of your progress and productivity'
              }
            </p>
          </div>

          {/* Date Range Filter */}
          <div className="flex items-center space-x-4">
            <Filter className="h-5 w-5 text-gray-400" />
            <select
              value={selectedDateRange}
              onChange={(e) => handleDateRangeChange(e.target.value)}
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
            >
              {dateRangeOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Tasks</p>
                <p className="text-3xl font-bold text-white">{insightsData?.overall_stats?.total_tasks || 0}</p>
              </div>
              <Target className="h-8 w-8 text-blue-400" />
            </div>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Completed</p>
                <p className="text-3xl font-bold text-green-400">{insightsData?.overall_stats?.completed_tasks || 0}</p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-green-400" />
            </div>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">In Progress</p>
                <p className="text-3xl font-bold text-yellow-400">{insightsData?.overall_stats?.in_progress_tasks || 0}</p>
              </div>
              <Clock className="h-8 w-8 text-yellow-400" />
            </div>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Completion Rate</p>
                <p className="text-3xl font-bold" style={{ color: '#F4B400' }}>
                  {insightsData?.overall_stats?.completion_rate || 0}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8" style={{ color: '#F4B400' }} />
            </div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Task Status Pie Chart */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" style={{ color: '#F4B400' }} />
              Task Status Breakdown
            </h3>
            {insightsData?.overall_stats?.total_tasks > 0 ? (
              <div className="h-80 flex items-center justify-center">
                <Pie data={taskStatusChartData} options={chartOptions} />
              </div>
            ) : (
              <div className="h-80 flex items-center justify-center">
                <div className="text-center">
                  <Target className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No tasks found for this time period</p>
                </div>
              </div>
            )}
          </div>

          {/* Areas Progress Chart */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" style={{ color: '#F4B400' }} />
              {selectedAreaId ? 'Project Progress' : 'Progress by Area'}
              {!selectedAreaId && (
                <span className="text-xs text-gray-400 ml-2">(Click to drill down)</span>
              )}
            </h3>
            {insightsData?.areas && insightsData.areas.length > 0 ? (
              <div className="h-80">
                <Bar data={areasChartData} options={chartOptions} />
              </div>
            ) : (
              <div className="h-80 flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">
                    {selectedAreaId ? 'No projects found in this area' : 'No areas found'}
                  </p>
                  <p className="text-gray-500 text-sm mt-2">
                    {selectedAreaId 
                      ? 'Create some projects to see progress visualization'
                      : 'Create some life areas to see progress visualization'
                    }
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Areas/Projects List */}
        {insightsData?.areas && insightsData.areas.length > 0 && (
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">
              {selectedAreaId ? 'Projects in this Area' : 'Areas Overview'}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {insightsData.areas.map((area) => (
                <div
                  key={area.id}
                  onClick={() => !selectedAreaId ? handleAreaClick(area.id, area.name) : undefined}
                  className={`p-4 bg-gray-800/50 border border-gray-700 rounded-lg transition-all duration-200 hover:shadow-lg ${
                    !selectedAreaId ? 'hover:border-gray-600 cursor-pointer' : ''
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-white">{area.name}</h4>
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: area.color }}
                    />
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between text-gray-400">
                      <span>Projects:</span>
                      <span>{area.total_projects}</span>
                    </div>
                    <div className="flex justify-between text-gray-400">
                      <span>Tasks:</span>
                      <span>{area.completed_tasks}/{area.total_tasks}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Completion:</span>
                      <span className="text-white font-medium">{area.completion_percentage}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Insights;