import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const DonutChart = ({ data, title, size = 'md', showLegend = true }) => {
  const sizeClasses = {
    sm: 'w-20 h-20',
    md: 'w-32 h-32', 
    lg: 'w-48 h-48',
    xl: 'w-64 h-64'
  };

  const chartData = {
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
        borderColor: '#0B0D14', // Dark border to match theme
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
  };

  const options = {
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
    cutout: '65%', // Creates the donut hole
    elements: {
      arc: {
        borderJoinStyle: 'round',
      },
    },
  };

  const total = data.values.reduce((acc, val) => acc + val, 0);

  return (
    <div className="flex flex-col items-center">
      {title && (
        <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      )}
      <div className={`relative ${sizeClasses[size]}`}>
        <Doughnut data={chartData} options={options} />
        {/* Center text showing total */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{total}</div>
            <div className="text-xs text-gray-400">Total</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DonutChart;