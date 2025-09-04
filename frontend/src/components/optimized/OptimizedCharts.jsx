import React, { memo, useMemo } from 'react';
import { LazyChart } from '../ui/LazyChart';
import { arePropsEqual } from '../../hooks/useMemorization';

/**
 * Optimized DonutChart with React.memo
 * Only re-renders when data actually changes
 */
export const OptimizedDonutChart = memo(({ 
  data, 
  title, 
  size = 'md', 
  showLegend = true 
}) => {
  // Memoize chart data to prevent recreation on every render
  const chartData = useMemo(() => ({
    labels: data.labels,
    datasets: [
      {
        data: data.values,
        backgroundColor: data.colors || [
          '#F4B400', // Aurum Gold
          '#3B82F6', // Blue
          '#10B981', // Green
          '#EF4444', // Red
          '#8B5CF6', // Purple
          '#F59E0B', // Amber
        ],
        borderColor: '#0B0D14',
        borderWidth: 2,
        hoverBackgroundColor: data.colors?.map(color => color + 'CC') || [
          '#F4B400CC',
          '#3B82F6CC', 
          '#10B981CC',
          '#EF4444CC',
          '#8B5CF6CC',
          '#F59E0BCC',
        ],
        hoverBorderWidth: 3,
      },
    ],
  }), [data.labels, data.values, data.colors]);

  // Memoize chart options
  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: showLegend,
        position: 'bottom',
        labels: {
          color: '#ffffff',
          padding: 12,
          font: {
            size: 12,
          },
          generateLabels: (chart) => {
            const data = chart.data;
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label, i) => {
                const dataset = data.datasets[0];
                const value = dataset.data[i];
                const total = dataset.data.reduce((acc, val) => acc + val, 0);
                const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                
                return {
                  text: `${label}: ${value} (${percentage}%)`,
                  fillStyle: dataset.backgroundColor[i],
                  strokeStyle: dataset.borderColor,
                  lineWidth: dataset.borderWidth,
                  hidden: false,
                  index: i,
                };
              });
            }
            return [];
          },
        },
      },
      tooltip: {
        backgroundColor: '#1F2937',
        titleColor: '#F4B400',
        bodyColor: '#ffffff',
        borderColor: '#374151',
        borderWidth: 1,
        callbacks: {
          label: function (context) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
            return `${label}: ${value} (${percentage}%)`;
          },
        },
      },
    },
    cutout: '65%',
    elements: {
      arc: {
        borderJoinStyle: 'round',
      },
    },
  }), [showLegend]);

  const total = useMemo(() => 
    data.values.reduce((acc, val) => acc + val, 0), 
    [data.values]
  );

  const sizeClasses = {
    sm: 'w-20 h-20',
    md: 'w-32 h-32', 
    lg: 'w-48 h-48',
    xl: 'w-64 h-64'
  };

  return (
    <div className="flex flex-col items-center">
      {title && (
        <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      )}
      <div className={`relative ${sizeClasses[size]}`}>
        <LazyChart
          type="Doughnut"
          data={chartData}
          options={options}
          height={300}
        />
        {/* Center text showing total */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{total}</div>
            <div className="text-xs text-gray-400">Total</div>
          </div>
        </div>
      </div>
    </div>
  );
}, arePropsEqual);

/**
 * Optimized LineChart for time series data
 * Prevents re-renders unless data changes
 */
export const OptimizedLineChart = memo(({ 
  data, 
  title,
  height = 300,
  showLegend = true 
}) => {
  const chartData = useMemo(() => ({
    labels: data.labels,
    datasets: data.datasets.map(dataset => ({
      ...dataset,
      borderColor: dataset.borderColor || '#F4B400',
      backgroundColor: dataset.backgroundColor || '#F4B40020',
      tension: dataset.tension || 0.4,
      pointRadius: dataset.pointRadius || 3,
      pointHoverRadius: dataset.pointHoverRadius || 5,
    }))
  }), [data]);

  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: showLegend,
        position: 'top',
        labels: {
          color: '#ffffff',
          padding: 15,
        },
      },
      tooltip: {
        backgroundColor: '#1F2937',
        titleColor: '#F4B400',
        bodyColor: '#ffffff',
        borderColor: '#374151',
        borderWidth: 1,
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      x: {
        grid: {
          color: '#374151',
          borderColor: '#374151',
        },
        ticks: {
          color: '#9CA3AF',
        },
      },
      y: {
        grid: {
          color: '#374151',
          borderColor: '#374151',
        },
        ticks: {
          color: '#9CA3AF',
        },
      },
    },
  }), [showLegend]);

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      )}
      <div style={{ height }}>
        <LazyChart
          type="Line"
          data={chartData}
          options={options}
          height={height}
        />
      </div>
    </div>
  );
}, arePropsEqual);

/**
 * Optimized BarChart component
 * Memoized to prevent unnecessary re-renders
 */
export const OptimizedBarChart = memo(({ 
  data, 
  title,
  height = 300,
  horizontal = false,
  stacked = false,
  showLegend = true 
}) => {
  const chartData = useMemo(() => ({
    labels: data.labels,
    datasets: data.datasets.map(dataset => ({
      ...dataset,
      backgroundColor: dataset.backgroundColor || '#F4B400',
      borderColor: dataset.borderColor || '#F4B400',
      borderWidth: dataset.borderWidth || 1,
    }))
  }), [data]);

  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: horizontal ? 'y' : 'x',
    plugins: {
      legend: {
        display: showLegend,
        position: 'top',
        labels: {
          color: '#ffffff',
          padding: 15,
        },
      },
      tooltip: {
        backgroundColor: '#1F2937',
        titleColor: '#F4B400',
        bodyColor: '#ffffff',
        borderColor: '#374151',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        stacked,
        grid: {
          color: '#374151',
          borderColor: '#374151',
        },
        ticks: {
          color: '#9CA3AF',
        },
      },
      y: {
        stacked,
        grid: {
          color: '#374151',
          borderColor: '#374151',
        },
        ticks: {
          color: '#9CA3AF',
        },
      },
    },
  }), [horizontal, stacked, showLegend]);

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      )}
      <div style={{ height }}>
        <LazyChart
          type="Bar"
          data={chartData}
          options={options}
          height={height}
        />
      </div>
    </div>
  );
}, arePropsEqual);