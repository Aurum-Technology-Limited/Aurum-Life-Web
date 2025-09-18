import { useMemo } from 'react';

interface LightweightLineChartProps {
  data: Array<{ [key: string]: any }>;
  xKey: string;
  yKey: string;
  color?: string;
  height?: number;
}

export function LightweightLineChart({ 
  data, 
  xKey, 
  yKey, 
  color = '#F4D03F', 
  height = 200 
}: LightweightLineChartProps) {
  const pathData = useMemo(() => {
    if (!data.length) return '';
    
    const width = 300;
    const maxY = Math.max(...data.map(d => d[yKey]));
    const minY = Math.min(...data.map(d => d[yKey]));
    const range = maxY - minY;
    
    const points = data.map((d, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - (((d[yKey] - minY) / range) * (height - 40)) - 20;
      return `${x},${y}`;
    });
    
    return `M ${points.join(' L ')}`;
  }, [data, xKey, yKey, height]);

  return (
    <div className="w-full" style={{ height }}>
      <svg width="100%" height={height} viewBox={`0 0 300 ${height}`}>
        <path
          d={pathData}
          fill="none"
          stroke={color}
          strokeWidth="2"
          className="drop-shadow-sm"
        />
        {data.map((d, i) => {
          const x = (i / (data.length - 1)) * 300;
          const maxY = Math.max(...data.map(d => d[yKey]));
          const minY = Math.min(...data.map(d => d[yKey]));
          const range = maxY - minY;
          const y = height - (((d[yKey] - minY) / range) * (height - 40)) - 20;
          
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r="3"
              fill={color}
              className="drop-shadow-sm"
            />
          );
        })}
      </svg>
    </div>
  );
}

interface LightweightBarChartProps {
  data: Array<{ name: string; value: number; color?: string }>;
  height?: number;
}

export function LightweightBarChart({ data, height = 200 }: LightweightBarChartProps) {
  const maxValue = Math.max(...data.map(d => d.value));
  
  return (
    <div className="w-full" style={{ height }}>
      <div className="flex items-end space-x-2 h-full">
        {data.map((item, index) => (
          <div key={index} className="flex-1 flex flex-col items-center">
            <div
              className="w-full rounded-t"
              style={{
                height: `${(item.value / maxValue) * (height - 30)}px`,
                backgroundColor: item.color || '#F4D03F',
                minHeight: '4px'
              }}
            />
            <span className="text-xs text-[#B8BCC8] mt-1 truncate w-full text-center">
              {item.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

interface LightweightPieChartProps {
  data: Array<{ name: string; value: number; color: string }>;
  size?: number;
}

export function LightweightPieChart({ data, size = 150 }: LightweightPieChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0);
  let currentAngle = 0;
  
  const slices = data.map(item => {
    const startAngle = currentAngle;
    const sliceAngle = (item.value / total) * 360;
    currentAngle += sliceAngle;
    
    const startX = size/2 + (size/3) * Math.cos((startAngle - 90) * Math.PI / 180);
    const startY = size/2 + (size/3) * Math.sin((startAngle - 90) * Math.PI / 180);
    const endX = size/2 + (size/3) * Math.cos((currentAngle - 90) * Math.PI / 180);
    const endY = size/2 + (size/3) * Math.sin((currentAngle - 90) * Math.PI / 180);
    
    const largeArcFlag = sliceAngle > 180 ? 1 : 0;
    
    return {
      ...item,
      path: `M ${size/2} ${size/2} L ${startX} ${startY} A ${size/3} ${size/3} 0 ${largeArcFlag} 1 ${endX} ${endY} Z`
    };
  });
  
  return (
    <div className="flex items-center space-x-4">
      <svg width={size} height={size}>
        {slices.map((slice, index) => (
          <path
            key={index}
            d={slice.path}
            fill={slice.color}
            className="drop-shadow-sm"
          />
        ))}
      </svg>
      <div className="flex-1 space-y-1">
        {data.map((item, index) => (
          <div key={index} className="flex items-center space-x-2">
            <div 
              className="w-3 h-3 rounded" 
              style={{ backgroundColor: item.color }}
            />
            <span className="text-sm text-[#B8BCC8]">{item.name}</span>
            <span className="text-sm text-white">{item.value}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Generic LightweightChart component that handles different chart types
interface LightweightChartProps {
  type: 'line' | 'bar' | 'doughnut' | 'pie';
  data: any;
  options?: any;
  height?: number;
  size?: number;
}

export function LightweightChart({ type, data, options, height = 200, size = 150 }: LightweightChartProps) {
  switch (type) {
    case 'line':
      // Convert Chart.js-style data to our format
      const lineData = data.datasets?.[0]?.data?.map((value, index) => ({
        [data.labels?.[index] || `point-${index}`]: data.labels?.[index] || `Point ${index + 1}`,
        value: value
      })) || [];
      
      return (
        <LightweightLineChart
          data={lineData}
          xKey="label"
          yKey="value"
          color={data.datasets?.[0]?.borderColor || '#F4D03F'}
          height={height}
        />
      );
      
    case 'bar':
      const barData = data.datasets?.[0]?.data?.map((value, index) => ({
        name: data.labels?.[index] || `Bar ${index + 1}`,
        value: value,
        color: Array.isArray(data.datasets[0].backgroundColor) 
          ? data.datasets[0].backgroundColor[index] 
          : data.datasets[0].backgroundColor || '#F4D03F'
      })) || [];
      
      return <LightweightBarChart data={barData} height={height} />;
      
    case 'doughnut':
    case 'pie':
      const pieData = data.datasets?.[0]?.data?.map((value, index) => ({
        name: data.labels?.[index] || `Slice ${index + 1}`,
        value: value,
        color: Array.isArray(data.datasets[0].backgroundColor) 
          ? data.datasets[0].backgroundColor[index] 
          : data.datasets[0].backgroundColor?.[index] || '#F4D03F'
      })) || [];
      
      return <LightweightPieChart data={pieData} size={size} />;
      
    default:
      return <div className="text-[#B8BCC8] text-center py-8">Unsupported chart type: {type}</div>;
  }
}

// Make LightweightChart the default export as well
export default LightweightChart;