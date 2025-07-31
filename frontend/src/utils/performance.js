import React from 'react';

// Performance monitoring utility for React components
export const usePerformanceMonitor = (componentName) => {
  const renderStart = performance.now();
  
  const logPerformance = () => {
    const renderTime = performance.now() - renderStart;
    if (renderTime > 16) { // Only log if render takes more than 16ms (60fps threshold)
      console.warn(`🐌 Slow render: ${componentName} took ${renderTime.toFixed(2)}ms`);
    }
  };

  // Log performance on unmount
  React.useEffect(() => {
    return () => {
      logPerformance();
    };
  }, []);

  return renderStart;
};

// Component performance wrapper
export const withPerformanceMonitoring = (WrappedComponent, componentName) => {
  return React.memo((props) => {
    usePerformanceMonitor(componentName);
    return <WrappedComponent {...props} />;
  });
};

// Bundle size analyzer - helps identify large components
export const analyzeBundleSize = () => {
  if (process.env.NODE_ENV === 'development') {
    console.group('📦 Bundle Analysis');
    console.log('Use webpack-bundle-analyzer for detailed bundle analysis');
    console.log('Run: npx webpack-bundle-analyzer build/static/js/*.js');
    console.groupEnd();
  }
};