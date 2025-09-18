import { motion } from 'motion/react';
import { cn } from '../../lib/utils';
import { Card, CardContent, CardHeader } from '../ui/card';
import { Skeleton } from '../ui/skeleton';

interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

export function SkeletonCard({ className, animate = true }: SkeletonProps) {
  return (
    <Card className={cn("glassmorphism-card", className)}>
      <CardHeader>
        <div className="flex items-center space-x-4">
          <Skeleton className="h-12 w-12 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-[200px]" />
            <Skeleton className="h-4 w-[160px]" />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-[90%]" />
          <Skeleton className="h-4 w-[60%]" />
        </div>
      </CardContent>
    </Card>
  );
}

export function SkeletonDashboard() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-[200px]" />
          <Skeleton className="h-4 w-[300px]" />
        </div>
        <Skeleton className="h-10 w-[120px]" />
      </div>

      {/* Stats grid skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="glassmorphism-card">
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Skeleton className="h-8 w-8 rounded-lg" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-[80px]" />
                  <Skeleton className="h-6 w-[40px]" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main content skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  );
}

export function SkeletonList({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i} className="glassmorphism-card">
          <CardContent className="p-4">
            <div className="flex items-center space-x-4">
              <Skeleton className="h-10 w-10 rounded-lg" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-[70%]" />
                <Skeleton className="h-3 w-[40%]" />
              </div>
              <Skeleton className="h-8 w-8 rounded-full" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export function SkeletonForm() {
  return (
    <Card className="glassmorphism-card">
      <CardHeader>
        <Skeleton className="h-6 w-[150px]" />
        <Skeleton className="h-4 w-[250px]" />
      </CardHeader>
      <CardContent className="space-y-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-4 w-[80px]" />
            <Skeleton className="h-10 w-full" />
          </div>
        ))}
        <div className="flex justify-end space-x-2">
          <Skeleton className="h-10 w-[80px]" />
          <Skeleton className="h-10 w-[100px]" />
        </div>
      </CardContent>
    </Card>
  );
}

export function SkeletonCalendar() {
  return (
    <Card className="glassmorphism-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <Skeleton className="h-6 w-[120px]" />
          <div className="flex space-x-2">
            <Skeleton className="h-8 w-8" />
            <Skeleton className="h-8 w-8" />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Calendar grid */}
        <div className="grid grid-cols-7 gap-2 mb-4">
          {Array.from({ length: 7 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
        <div className="grid grid-cols-7 gap-2">
          {Array.from({ length: 35 }).map((_, i) => (
            <div key={i} className="aspect-square">
              <Skeleton className="h-full w-full" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

interface ProgressiveSkeletonProps {
  isLoading: boolean;
  children: React.ReactNode;
  skeleton: React.ReactNode;
  className?: string;
}

export function ProgressiveSkeleton({ 
  isLoading, 
  children, 
  skeleton, 
  className 
}: ProgressiveSkeletonProps) {
  return (
    <motion.div
      className={className}
      initial={false}
      animate={{ opacity: isLoading ? 0.7 : 1 }}
      transition={{ duration: 0.2 }}
    >
      {isLoading ? skeleton : children}
    </motion.div>
  );
}

interface ContentRevealProps {
  isLoading: boolean;
  children: React.ReactNode;
  className?: string;
}

export function ContentReveal({ isLoading, children, className }: ContentRevealProps) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 20 }}
      animate={{ 
        opacity: isLoading ? 0 : 1, 
        y: isLoading ? 20 : 0 
      }}
      transition={{ 
        duration: 0.3,
        delay: isLoading ? 0 : 0.1
      }}
    >
      {children}
    </motion.div>
  );
}

interface ShimmerProps {
  className?: string;
  width?: string | number;
  height?: string | number;
}

export function Shimmer({ className, width = '100%', height = '1rem' }: ShimmerProps) {
  return (
    <div
      className={cn("shimmer rounded", className)}
      style={{ width, height }}
    />
  );
}

export function SkeletonNavigation() {
  return (
    <div className="space-y-2 p-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="flex items-center space-x-3 p-2">
          <Skeleton className="h-6 w-6" />
          <Skeleton className="h-4 w-[100px]" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonBreadcrumbs() {
  return (
    <div className="flex items-center space-x-2 mb-6">
      <Skeleton className="h-4 w-[60px]" />
      <span className="text-muted-foreground">/</span>
      <Skeleton className="h-4 w-[80px]" />
      <span className="text-muted-foreground">/</span>
      <Skeleton className="h-4 w-[100px]" />
    </div>
  );
}