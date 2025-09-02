import React from 'react';
import { Smile, Frown, Meh, Heart, TrendingUp } from 'lucide-react';

/**
 * Sentiment Indicator Component
 * Displays emotional sentiment with emoji, color, and optional details
 */
const SentimentIndicator = ({ 
  sentimentScore, 
  sentimentCategory, 
  sentimentEmoji,
  emotionalKeywords = [],
  showDetails = false,
  showTrend = false,
  size = 'medium',
  className = ''
}) => {
  // Fallback emoji based on category
  const getEmoji = () => {
    if (sentimentEmoji) return sentimentEmoji;
    
    const emojiMap = {
      'very_positive': '😄',
      'positive': '😊',
      'neutral': '😐',
      'negative': '😞',
      'very_negative': '😢'
    };
    return emojiMap[sentimentCategory] || '😐';
  };

  // Get color based on sentiment
  const getColor = () => {
    const colorMap = {
      'very_positive': '#10B981',
      'positive': '#34D399', 
      'neutral': '#6B7280',
      'negative': '#F59E0B',
      'very_negative': '#EF4444'
    };
    return colorMap[sentimentCategory] || '#6B7280';
  };

  // Get human-readable label
  const getLabel = () => {
    const labelMap = {
      'very_positive': 'Very Positive',
      'positive': 'Positive',
      'neutral': 'Neutral', 
      'negative': 'Negative',
      'very_negative': 'Very Negative'
    };
    return labelMap[sentimentCategory] || 'Unknown';
  };

  // Size configurations
  const sizeConfig = {
    small: {
      emoji: 'text-lg',
      container: 'p-2',
      text: 'text-xs'
    },
    medium: {
      emoji: 'text-2xl', 
      container: 'p-3',
      text: 'text-sm'
    },
    large: {
      emoji: 'text-4xl',
      container: 'p-4', 
      text: 'text-base'
    }
  };

  const config = sizeConfig[size] || sizeConfig.medium;
  const color = getColor();

  if (!sentimentCategory) {
    return (
      <div className={`inline-flex items-center gap-2 ${className}`}>
        <span className="text-gray-400 text-sm">No sentiment data</span>
      </div>
    );
  }

  return (
    <div className={`inline-flex items-center gap-3 ${className}`}>
      {/* Sentiment Emoji */}
      <div 
        className={`${config.container} rounded-lg border-2 flex items-center justify-center`}
        style={{ borderColor: color, backgroundColor: `${color}20` }}
      >
        <span className={config.emoji}>{getEmoji()}</span>
      </div>

      {/* Sentiment Details */}
      {showDetails && (
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span 
              className={`${config.text} font-medium`}
              style={{ color: color }}
            >
              {getLabel()}
            </span>
            {sentimentScore !== undefined && (
              <span className="text-xs text-gray-400">
                ({sentimentScore > 0 ? '+' : ''}{sentimentScore.toFixed(2)})
              </span>
            )}
          </div>
          
          {/* Emotional Keywords */}
          {emotionalKeywords && emotionalKeywords.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {emotionalKeywords.slice(0, 3).map((keyword, index) => (
                <span 
                  key={index}
                  className="px-2 py-1 text-xs rounded-full border"
                  style={{ 
                    borderColor: `${color}40`, 
                    backgroundColor: `${color}10`,
                    color: color
                  }}
                >
                  {keyword}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Trend Indicator */}
      {showTrend && sentimentScore !== undefined && (
        <div className="flex items-center">
          {sentimentScore > 0.2 ? (
            <TrendingUp className="h-4 w-4 text-green-400" />
          ) : sentimentScore < -0.2 ? (
            <TrendingUp className="h-4 w-4 text-red-400 transform rotate-180" />
          ) : (
            <Meh className="h-4 w-4 text-gray-400" />
          )}
        </div>
      )}
    </div>
  );
};

/**
 * Compact Sentiment Badge for list views
 */
export const SentimentBadge = ({ sentimentCategory, sentimentScore, sentimentEmoji, size = 'small' }) => (
  <SentimentIndicator
    sentimentCategory={sentimentCategory}
    sentimentScore={sentimentScore}
    sentimentEmoji={sentimentEmoji}
    showDetails={false}
    size={size}
    className="flex-shrink-0"
  />
);

/**
 * Detailed Sentiment Card for full displays
 */
export const SentimentCard = ({ 
  sentimentScore, 
  sentimentCategory, 
  sentimentEmoji,
  emotionalKeywords,
  emotionalThemes,
  dominantEmotions,
  emotionalIntensity,
  analysisDate
}) => {
  const color = {
    'very_positive': '#10B981',
    'positive': '#34D399',
    'neutral': '#6B7280', 
    'negative': '#F59E0B',
    'very_negative': '#EF4444'
  }[sentimentCategory] || '#6B7280';

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
      <div className="flex items-center gap-3 mb-3">
        <SentimentIndicator
          sentimentScore={sentimentScore}
          sentimentCategory={sentimentCategory}
          sentimentEmoji={sentimentEmoji}
          size="medium"
        />
        <div>
          <h4 className="text-white font-medium">Emotional Analysis</h4>
          {analysisDate && (
            <p className="text-xs text-gray-400">
              Analyzed {new Date(analysisDate).toLocaleDateString()}
            </p>
          )}
        </div>
      </div>

      {/* Emotional Details */}
      <div className="space-y-3">
        {/* Emotional Keywords */}
        {emotionalKeywords && emotionalKeywords.length > 0 && (
          <div>
            <p className="text-xs text-gray-400 mb-1">Emotional Keywords</p>
            <div className="flex flex-wrap gap-1">
              {emotionalKeywords.map((keyword, index) => (
                <span 
                  key={index}
                  className="px-2 py-1 text-xs rounded-full border"
                  style={{ 
                    borderColor: `${color}40`, 
                    backgroundColor: `${color}10`,
                    color: color
                  }}
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Dominant Emotions */}
        {dominantEmotions && dominantEmotions.length > 0 && (
          <div>
            <p className="text-xs text-gray-400 mb-1">Primary Emotions</p>
            <div className="flex flex-wrap gap-1">
              {dominantEmotions.map((emotion, index) => (
                <span 
                  key={index}
                  className="px-2 py-1 text-xs rounded-full bg-purple-600/20 text-purple-400 border border-purple-600/30"
                >
                  {emotion}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Emotional Intensity */}
        {emotionalIntensity !== undefined && (
          <div>
            <p className="text-xs text-gray-400 mb-1">Emotional Intensity</p>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-700 rounded-full h-2">
                <div 
                  className="h-2 rounded-full"
                  style={{ 
                    width: `${emotionalIntensity * 100}%`,
                    backgroundColor: color
                  }}
                />
              </div>
              <span className="text-xs" style={{ color }}>
                {Math.round(emotionalIntensity * 100)}%
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SentimentIndicator;