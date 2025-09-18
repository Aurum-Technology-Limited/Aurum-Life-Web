// This file redirects all exports to the .tsx version
// to avoid TypeScript compilation issues with JSX syntax

export {
  type PerformanceMetrics,
  cacheManager,
  performanceMonitor,
  useDebounce,
  useThrottle,
  useMemoizedComputation,
  useRenderPerformance,
  useOptimizedFetch,
  useIntersectionObserver,
  preloadComponent,
  prefetchRoute,
  clearUnusedData,
  registerOptimizedServiceWorker,
  optimizeImage,
  reportPerformanceMetrics,
  runPerformanceAudit,
} from './performanceOptimizations.tsx';

export { default } from './performanceOptimizations.tsx';