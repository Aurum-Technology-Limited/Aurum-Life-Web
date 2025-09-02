import React from 'react';
import { 
  X, 
  BookOpen, 
  CheckSquare, 
  Folder, 
  Sun, 
  Brain, 
  Circle,
  ArrowRight,
  TrendingUp
} from 'lucide-react';

const SimilarContentModal = ({ isOpen, onClose, data, onItemSelect }) => {
  if (!isOpen || !data) return null;

  const getEntityIcon = (entityType) => {
    const icons = {
      journal_entry: BookOpen,
      task: CheckSquare,
      project: Folder,
      daily_reflection: Sun,
      ai_insight: Brain
    };
    return icons[entityType] || Circle;
  };

  const getConfidenceColor = (level) => {
    const colors = {
      high: 'text-green-400 bg-green-400/10',
      medium: 'text-yellow-400 bg-yellow-400/10',
      low: 'text-orange-400 bg-orange-400/10'
    };
    return colors[level] || colors.low;
  };

  const handleItemClick = (item) => {
    if (onItemSelect) {
      onItemSelect(item);
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-600 rounded-lg">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">Similar Content</h2>
              <p className="text-sm text-gray-400">
                Content similar to "{data.sourceEntity?.title}"
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Source Entity Info */}
        <div className="p-6 bg-gray-800/30 border-b border-gray-700/50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600/20 rounded-lg">
              {React.createElement(getEntityIcon(data.sourceEntity?.type), {
                className: "h-4 w-4 text-blue-400"
              })}
            </div>
            <div>
              <p className="text-sm text-gray-400">Source:</p>
              <p className="font-medium text-white">{data.sourceEntity?.title}</p>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto p-6">
          {data.similarContent && data.similarContent.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm text-gray-400">
                  Found {data.totalResults} similar items
                </p>
              </div>

              {data.similarContent.map((item, index) => {
                const IconComponent = getEntityIcon(item.entity_type);
                
                return (
                  <button
                    key={`${item.entity_type}-${item.id}-${index}`}
                    onClick={() => handleItemClick(item)}
                    className="w-full text-left p-4 bg-gray-800/50 hover:bg-gray-700/50 rounded-lg transition-colors border border-gray-700/50 hover:border-gray-600"
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 bg-purple-600/20 rounded-lg flex-shrink-0">
                        <IconComponent className="h-4 w-4 text-purple-400" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-white truncate">
                            {item.title}
                          </h3>
                          <span className={`px-2 py-1 text-xs rounded-full ${getConfidenceColor(item.confidence_level)}`}>
                            {item.similarity_score}%
                          </span>
                        </div>
                        
                        <p className="text-sm text-gray-400 mb-2">
                          {item.entity_display_name}
                          {item.metadata?.project_name && (
                            <span className="ml-2 text-gray-500">
                              • {item.metadata.project_name}
                            </span>
                          )}
                          {item.metadata?.status && (
                            <span className="ml-2 text-gray-500">
                              • {item.metadata.status}
                            </span>
                          )}
                        </p>
                        
                        <p className="text-sm text-gray-300 line-clamp-3">
                          {item.content_preview}
                        </p>
                        
                        {item.created_at && (
                          <p className="text-xs text-gray-500 mt-2">
                            {new Date(item.created_at).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                      
                      <ArrowRight className="h-4 w-4 text-gray-500 flex-shrink-0" />
                    </div>
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12">
              <TrendingUp className="h-16 w-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-400 mb-2">No similar content found</h3>
              <p className="text-sm text-gray-500">
                Try adjusting the similarity threshold or check back later as you add more content
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-700/50 text-center">
          <p className="text-xs text-gray-500">
            Similarity scores are based on semantic meaning and context
          </p>
        </div>
      </div>
    </div>
  );
};

export default SimilarContentModal;