import React, { memo, useCallback, useMemo } from 'react';
import { arePropsEqualIgnoreFunctions } from '../../hooks/useMemorization';

/**
 * Optimized JournalEntryCard
 * Only re-renders when entry data changes
 */
export const OptimizedJournalEntryCard = memo(({ 
  entry, 
  onClick, 
  isSelected 
}) => {
  const handleClick = useCallback(() => {
    onClick(entry.id);
  }, [entry.id, onClick]);

  const moodColors = {
    optimistic: 'text-yellow-400',
    inspired: 'text-purple-400',
    reflective: 'text-blue-400',
    challenging: 'text-orange-400',
    anxious: 'text-red-400',
    grateful: 'text-green-400',
    excited: 'text-pink-400',
    frustrated: 'text-red-500',
    peaceful: 'text-teal-400',
    motivated: 'text-indigo-400'
  };

  const formattedDate = useMemo(() => 
    new Date(entry.created_at).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }), 
    [entry.created_at]
  );

  const preview = useMemo(() => {
    const text = entry.content.replace(/<[^>]*>/g, '');
    return text.length > 150 ? text.substring(0, 150) + '...' : text;
  }, [entry.content]);

  return (
    <div
      onClick={handleClick}
      className={`
        p-5 rounded-lg border cursor-pointer transition-all
        ${isSelected ? 'border-yellow-500 bg-gray-800' : 'border-gray-700 hover:border-gray-600'}
      `}
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-white line-clamp-1">
          {entry.title}
        </h3>
        <span className="text-sm text-gray-500">{formattedDate}</span>
      </div>
      
      <p className="text-gray-400 text-sm mb-3 line-clamp-2">
        {preview}
      </p>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {entry.mood && (
            <span className={`text-sm ${moodColors[entry.mood] || 'text-gray-400'}`}>
              {entry.mood}
            </span>
          )}
          {entry.tags && entry.tags.length > 0 && (
            <div className="flex gap-1">
              {entry.tags.slice(0, 3).map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded-full"
                >
                  {tag}
                </span>
              ))}
              {entry.tags.length > 3 && (
                <span className="text-xs text-gray-500">
                  +{entry.tags.length - 3}
                </span>
              )}
            </div>
          )}
        </div>
        
        {entry.sentiment_score !== null && entry.sentiment_score !== undefined && (
          <div className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-full ${
              entry.sentiment_score > 0.3 ? 'bg-green-400' :
              entry.sentiment_score < -0.3 ? 'bg-red-400' :
              'bg-yellow-400'
            }`} />
            <span className="text-xs text-gray-500">
              {entry.sentiment_score > 0.3 ? 'Positive' :
               entry.sentiment_score < -0.3 ? 'Negative' :
               'Neutral'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}, arePropsEqualIgnoreFunctions);

/**
 * Optimized ProjectCard with area information
 */
export const OptimizedProjectCard = memo(({ 
  project, 
  area,
  onEdit, 
  onDelete, 
  onViewTasks,
  onUpdateStatus 
}) => {
  const statusColors = {
    'Not Started': 'text-gray-400 bg-gray-400/10',
    'In Progress': 'text-blue-400 bg-blue-400/10',
    'Completed': 'text-green-400 bg-green-400/10',
    'On Hold': 'text-yellow-400 bg-yellow-400/10'
  };

  const priorityColors = {
    high: 'text-red-400',
    medium: 'text-yellow-400',
    low: 'text-green-400'
  };

  const completionPercentage = useMemo(() => 
    Math.round(project.completion_percentage || 0),
    [project.completion_percentage]
  );

  const daysUntilDeadline = useMemo(() => {
    if (!project.deadline) return null;
    const days = Math.ceil((new Date(project.deadline) - new Date()) / (1000 * 60 * 60 * 24));
    return days;
  }, [project.deadline]);

  return (
    <div 
      className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-all group"
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-yellow-400 transition-colors">
            {project.icon} {project.name}
          </h3>
          
          {area && (
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
              <span className="w-1 h-4 bg-gray-600 rounded-full" />
              <span>{area.name}</span>
            </div>
          )}
          
          {project.description && (
            <p className="text-gray-400 text-sm line-clamp-2">{project.description}</p>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit(project);
            }}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(project.id);
            }}
            className="p-2 hover:bg-red-500/20 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
      
      <div className="space-y-3">
        {/* Progress bar */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-500">Progress</span>
            <span className="text-gray-400">{completionPercentage}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-yellow-400 h-2 rounded-full transition-all"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
        </div>
        
        {/* Meta information */}
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4">
            <span className={`px-3 py-1 rounded-full ${statusColors[project.status] || statusColors['Not Started']}`}>
              {project.status}
            </span>
            <span className={priorityColors[project.priority] || 'text-gray-400'}>
              {project.priority} priority
            </span>
          </div>
          
          {daysUntilDeadline !== null && (
            <span className={`text-sm ${
              daysUntilDeadline < 0 ? 'text-red-400' :
              daysUntilDeadline <= 7 ? 'text-yellow-400' :
              'text-gray-500'
            }`}>
              {daysUntilDeadline < 0 
                ? `${Math.abs(daysUntilDeadline)} days overdue`
                : daysUntilDeadline === 0 
                ? 'Due today'
                : `${daysUntilDeadline} days left`
              }
            </span>
          )}
        </div>
        
        {/* Action buttons */}
        <div className="flex gap-2 pt-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onViewTasks(project);
            }}
            className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm"
          >
            View Tasks
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              const nextStatus = project.status === 'Not Started' ? 'In Progress' :
                               project.status === 'In Progress' ? 'Completed' :
                               project.status === 'Completed' ? 'On Hold' : 'Not Started';
              onUpdateStatus(project.id, nextStatus);
            }}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm"
          >
            Update Status
          </button>
        </div>
      </div>
    </div>
  );
}, arePropsEqualIgnoreFunctions);

/**
 * Virtualized list for large datasets
 * Only renders visible items
 */
export const VirtualizedList = memo(({ 
  items, 
  itemHeight, 
  renderItem,
  containerHeight = 600,
  overscan = 3 
}) => {
  const [scrollTop, setScrollTop] = React.useState(0);
  
  const visibleRange = useMemo(() => {
    const start = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const end = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    return { start, end };
  }, [scrollTop, itemHeight, containerHeight, overscan, items.length]);

  const visibleItems = useMemo(() => 
    items.slice(visibleRange.start, visibleRange.end + 1),
    [items, visibleRange]
  );

  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);

  const totalHeight = items.length * itemHeight;
  const offsetY = visibleRange.start * itemHeight;

  return (
    <div 
      className="relative overflow-auto"
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
          }}
        >
          {visibleItems.map((item, index) => (
            <div key={item.id} style={{ height: itemHeight }}>
              {renderItem(item, visibleRange.start + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});