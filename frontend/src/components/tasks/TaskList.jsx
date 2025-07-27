import React, { memo, useCallback } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { AlertCircle } from 'lucide-react';
import { Card } from '../ui/card';
import TaskItem from './TaskItem';
import TaskFilters from './TaskFilters';
import { useTaskQueries } from './hooks/useTaskQueries';

/**
 * TaskList Component - Optimized for performance
 * 
 * Features:
 * - Virtual scrolling for large lists
 * - Memoized to prevent unnecessary re-renders
 * - Efficient filtering and sorting
 * - Proper error handling
 */
const TaskList = memo(({ projectId = null, showFilters = true }) => {
  const { 
    tasks, 
    isLoading, 
    error, 
    filters, 
    setFilters,
    refetch 
  } = useTaskQueries(projectId);

  // Virtual scrolling setup for performance
  const parentRef = React.useRef(null);
  
  const rowVirtualizer = useVirtualizer({
    count: tasks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80, // Estimated height of each task item
    overscan: 5, // Render 5 items outside of visible area
  });

  // Memoized task renderer
  const renderTask = useCallback((task) => (
    <TaskItem
      key={task.id}
      task={task}
      onUpdate={() => refetch()}
    />
  ), [refetch]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="flex items-center gap-2 text-destructive">
          <AlertCircle className="h-5 w-5" />
          <span>Error loading tasks: {error.message}</span>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {showFilters && (
        <TaskFilters
          filters={filters}
          onFiltersChange={setFilters}
          taskCount={tasks.length}
        />
      )}

      {tasks.length === 0 ? (
        <Card className="p-8">
          <div className="text-center text-muted-foreground">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No tasks found</p>
            {filters.status !== 'all' && (
              <p className="text-sm mt-2">
                Try adjusting your filters
              </p>
            )}
          </div>
        </Card>
      ) : (
        <div
          ref={parentRef}
          className="h-[600px] overflow-auto"
          style={{
            contain: 'strict',
          }}
        >
          <div
            style={{
              height: `${rowVirtualizer.getTotalSize()}px`,
              width: '100%',
              position: 'relative',
            }}
          >
            {rowVirtualizer.getVirtualItems().map((virtualItem) => (
              <div
                key={virtualItem.key}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: `${virtualItem.size}px`,
                  transform: `translateY(${virtualItem.start}px)`,
                }}
              >
                {renderTask(tasks[virtualItem.index])}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

TaskList.displayName = 'TaskList';

export default TaskList;