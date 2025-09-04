import React, { Suspense, lazy, useMemo } from 'react';
import { Skeleton } from './skeleton';

// Lazy load chart components on demand
const ChartComponents = {
  Line: lazy(() => 
    import('react-chartjs-2').then(module => ({ default: module.Line }))
  ),
  Bar: lazy(() => 
    import('react-chartjs-2').then(module => ({ default: module.Bar }))
  ),
  Doughnut: lazy(() => 
    import('react-chartjs-2').then(module => ({ default: module.Doughnut }))
  ),
  Pie: lazy(() => 
    import('react-chartjs-2').then(module => ({ default: module.Pie }))
  ),
  Radar: lazy(() => 
    import('react-chartjs-2').then(module => ({ default: module.Radar }))
  ),
  PolarArea: lazy(() => 
    import('react-chartjs-2').then(module => ({ default: module.PolarArea }))
  )
};

// Chart loading skeleton
const ChartSkeleton = ({ height = 300, className = '' }) => (
  <div className={`flex items-center justify-center ${className}`} style={{ height }}>
    <Skeleton className="w-full h-full" />
  </div>
);

/**
 * Lazy Chart Component
 * Dynamically loads chart components only when needed
 * This significantly reduces initial bundle size
 */
export function LazyChart({ 
  type, 
  data, 
  options, 
  height = 300,
  className = '',
  ...props 
}) {
  // Get the appropriate chart component
  const ChartComponent = useMemo(() => {
    return ChartComponents[type] || ChartComponents.Line;
  }, [type]);

  // Memoize chart options for performance
  const memoizedOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    ...options
  }), [options]);

  return (
    <Suspense fallback={<ChartSkeleton height={height} className={className} />}>
      <div style={{ height }} className={className}>
        <ChartComponent 
          data={data} 
          options={memoizedOptions} 
          {...props} 
        />
      </div>
    </Suspense>
  );
}

// Export individual lazy chart components for direct use
export const LazyLine = (props) => <LazyChart type="Line" {...props} />;
export const LazyBar = (props) => <LazyChart type="Bar" {...props} />;
export const LazyDoughnut = (props) => <LazyChart type="Doughnut" {...props} />;
export const LazyPie = (props) => <LazyChart type="Pie" {...props} />;
export const LazyRadar = (props) => <LazyChart type="Radar" {...props} />;
export const LazyPolarArea = (props) => <LazyChart type="PolarArea" {...props} />;

export default LazyChart;