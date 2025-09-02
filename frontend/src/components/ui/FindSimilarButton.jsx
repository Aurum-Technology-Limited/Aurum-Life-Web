import React, { useState } from 'react';
import { Search, Loader2, Sparkles } from 'lucide-react';
import { semanticSearchAPI } from '../../services/api';

const FindSimilarButton = ({ 
  entityType, 
  entityId, 
  entityTitle,
  onResults,
  className = "",
  size = "sm",
  variant = "outline"
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleFindSimilar = async (e) => {
    e.stopPropagation(); // Prevent parent click events
    
    if (!entityId || !entityType) {
      console.warn('FindSimilarButton: Missing entityId or entityType');
      return;
    }

    setIsLoading(true);
    try {
      const response = await semanticSearchAPI.findSimilar(entityType, entityId, 5, 0.4);
      
      if (onResults) {
        onResults({
          sourceEntity: response.source_entity,
          similarContent: response.similar_content,
          totalResults: response.total_results
        });
      }
    } catch (error) {
      console.error('Find similar failed:', error);
      // Could show a toast notification here
    } finally {
      setIsLoading(false);
    }
  };

  const sizeClasses = {
    xs: 'px-2 py-1 text-xs',
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  const variantClasses = {
    outline: 'border border-gray-600 text-gray-300 hover:border-purple-500 hover:text-purple-400 hover:bg-purple-500/10',
    solid: 'bg-purple-600 text-white hover:bg-purple-700',
    ghost: 'text-gray-400 hover:text-purple-400 hover:bg-purple-500/10'
  };

  const iconSize = {
    xs: 'h-3 w-3',
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5'
  };

  return (
    <button
      onClick={handleFindSimilar}
      disabled={isLoading}
      className={`
        inline-flex items-center gap-2 rounded-lg font-medium transition-all duration-200
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
      title={`Find content similar to "${entityTitle || 'this item'}"`}
    >
      {isLoading ? (
        <Loader2 className={`${iconSize[size]} animate-spin`} />
      ) : (
        <Sparkles className={iconSize[size]} />
      )}
      {size !== 'xs' && (
        <span>Find Similar</span>
      )}
    </button>
  );
};

export default FindSimilarButton;