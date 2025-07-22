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
  ArrowLeft,
  Target,
  CheckCircle2,
  Clock,
  AlertTriangle
} from 'lucide-react';
import { insightsAPI } from '../services/api';

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

  // Chart.js configurations
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
    scales: currentView === 'overview' && insightsData?.areas?.length > 0 ? {
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
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            {currentView !== 'overview' && (
              <button
                onClick={handleBackToOverview}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Overview</span>
              </button>
            )}
            <div>
              <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
                {currentView === 'overview' ? 'Productivity Insights' : 
                 currentView === 'area' ? `${drillDownData?.area?.name} - Projects` :
                 `${drillDownData?.project?.name} - Tasks`}
              </h1>
              <p className="text-gray-400 mt-1">
                Data-driven overview of your progress and productivity
              </p>
            </div>
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

        {/* Overview View */}
        {currentView === 'overview' && (
          <>
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
                  Progress by Area
                </h3>
                {insightsData?.areas && insightsData.areas.length > 0 ? (
                  <div className="h-80">
                    <Bar data={areasChartData} options={chartOptions} />
                  </div>
                ) : (
                  <div className="h-80 flex items-center justify-center">
                    <div className="text-center">
                      <BarChart3 className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                      <p className="text-gray-400">No areas found</p>
                      <p className="text-gray-500 text-sm mt-2">Create some life areas to see progress visualization</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Areas List with Drill-down */}
            {insightsData?.areas && insightsData.areas.length > 0 && (
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-white mb-6">Areas Overview</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {insightsData.areas.map((area) => (
                    <div
                      key={area.id}
                      onClick={() => loadAreaDrillDown(area.id)}
                      className="p-4 bg-gray-800/50 border border-gray-700 rounded-lg hover:border-gray-600 cursor-pointer transition-all duration-200 hover:shadow-lg"
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
          </>
        )}

        {/* Area Drill-down View */}
        {currentView === 'area' && drillDownData && (
          <div className="space-y-6">
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">
                Projects in {drillDownData.area.name}
              </h3>
              {drillDownData.projects.length > 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {drillDownData.projects.map((project) => (
                    <div
                      key={project.id}
                      onClick={() => loadProjectDrillDown(project.id)}
                      className="p-4 bg-gray-800/50 border border-gray-700 rounded-lg hover:border-gray-600 cursor-pointer transition-all duration-200"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-white">{project.name}</h4>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          project.priority === 'high' ? 'bg-red-400/10 text-red-400' :
                          project.priority === 'medium' ? 'bg-yellow-400/10 text-yellow-400' :
                          'bg-green-400/10 text-green-400'
                        }`}>
                          {project.priority}
                        </span>
                      </div>
                      <div className="space-y-2">
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div
                            className="h-2 rounded-full transition-all duration-300"
                            style={{
                              backgroundColor: drillDownData.area.color,
                              width: `${project.completion_percentage}%`
                            }}
                          />
                        </div>
                        <div className="flex justify-between text-sm text-gray-400">
                          <span>{project.completed_tasks}/{project.total_tasks} tasks</span>
                          <span>{project.completion_percentage}% complete</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Target className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No projects found in this area</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Project Drill-down View */}
        {currentView === 'project' && drillDownData && (
          <div className="space-y-6">
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">
                Tasks in {drillDownData.project.name}
              </h3>
              {drillDownData.tasks.length > 0 ? (
                <div className="space-y-3">
                  {drillDownData.tasks.map((task) => (
                    <div key={task.id} className="p-4 bg-gray-800/50 border border-gray-700 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`w-2 h-2 rounded-full ${
                            task.status === 'completed' ? 'bg-green-400' :
                            task.status === 'in-progress' ? 'bg-yellow-400' :
                            'bg-gray-400'
                          }`} />
                          <span className="text-white font-medium">{task.title}</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            task.priority === 'high' ? 'bg-red-400/10 text-red-400' :
                            task.priority === 'medium' ? 'bg-yellow-400/10 text-yellow-400' :
                            'bg-green-400/10 text-green-400'
                          }`}>
                            {task.priority}
                          </span>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            task.status === 'completed' ? 'bg-green-400/10 text-green-400' :
                            task.status === 'in-progress' ? 'bg-yellow-400/10 text-yellow-400' :
                            'bg-gray-400/10 text-gray-400'
                          }`}>
                            {task.status.replace('-', ' ')}
                          </span>
                        </div>
                      </div>
                      {task.description && (
                        <p className="text-gray-400 text-sm mt-2">{task.description}</p>
                      )}
                      {task.due_date && (
                        <div className="flex items-center mt-2 text-xs text-gray-500">
                          <Calendar className="h-3 w-3 mr-1" />
                          Due: {new Date(task.due_date).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircle2 className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No tasks found in this project</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Insights;