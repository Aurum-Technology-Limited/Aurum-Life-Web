import React from 'react';

const MicroBarChart = ({ data, barColor = '#10B981', height = 60 }) => {
  if (!data || data.length === 0) {
    return <div className="text-gray-500 text-sm">No data available</div>;
  }

  const maxValue = Math.max(...data.map(d => d.value));
  
  return (
    <div className="flex items-end gap-1" style={{ height: `${height}px` }}>
      {data.map((item, index) => {
        const barHeight = maxValue > 0 ? (item.value / maxValue) * (height - 20) : 0;
        
        return (
          <div key={index} className="flex flex-col items-center flex-1 min-w-0">
            <div 
              className="w-full rounded-t transition-all duration-300 hover:opacity-80"
              style={{ 
                height: `${barHeight}px`,
                backgroundColor: barColor,
                minHeight: item.value > 0 ? '2px' : '0px'
              }}
              title={`${item.label}: ${item.value}`}
            />
            <div className="text-[10px] text-gray-500 mt-1 truncate w-full text-center">
              {item.label}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default MicroBarChart;