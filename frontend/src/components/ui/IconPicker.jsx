import React, { useState } from 'react';

const IconPicker = ({ 
  value, 
  onChange, 
  label = "Icon", 
  placeholder = "🎯",
  required = false,
  className = "",
  allowCustom = true,
  iconSet = "default" // "default", "pillars", "areas", "projects"
}) => {
  const [showCustomInput, setShowCustomInput] = useState(false);

  // Comprehensive icon sets for different use cases
  const iconSets = {
    default: [
      '🎯', '🏆', '⭐', '🚀', '💪', '📚', '✍️', '🧘',
      '🏃', '💡', '🎨', '🎵', '🌟', '🔥', '💎', '🎉',
      '📈', '🎪', '🎭', '🎲', '🎸', '🎤', '🎬', '📷',
      '🍎', '🌱', '🌈', '☀️', '🌙', '⚡', '🔮', '🎊'
    ],
    pillars: [
      '🎯', '🏃‍♂️', '💪', '🧠', '💼', '❤️', '🌟', '🚀', 
      '🌱', '🎨', '📚', '⚡', '🏠', '🌍', '💰', '🎵',
      '🍎', '🧘', '👥', '📱', '🔬', '⛰️', '🎭', '🏖️'
    ],
    areas: [
      '🎯', '💪', '💼', '❤️', '🧠', '🏠', '💰', '🎨',
      '📚', '🌟', '🚀', '🌱', '⚡', '🎵', '🍎', '🧘',
      '👥', '📱', '🔬', '⛰️', '🎭', '🏖️', '📊', '🎪'
    ],
    projects: [
      '🚀', '🎯', '💻', '📱', '🎨', '📚', '💡', '🔧',
      '🏗️', '📊', '💰', '🌟', '⚡', '🎪', '🎬', '📷',
      '🎵', '🎭', '🎨', '📝', '🔬', '⛰️', '🏆', '💎'
    ]
  };

  const currentIconSet = iconSets[iconSet] || iconSets.default;

  const handleIconSelect = (icon) => {
    onChange(icon);
    setShowCustomInput(false);
  };

  const handleCustomChange = (e) => {
    const customValue = e.target.value;
    // Limit to 2 characters to prevent long text entries
    if (customValue.length <= 2) {
      onChange(customValue);
    }
  };

  return (
    <div className={className}>
      <label className="block text-sm font-medium text-gray-300 mb-2">
        {label} {required && <span className="text-red-400">*</span>}
      </label>
      
      <div className="space-y-3">
        {/* Current Icon Display */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <span className="text-3xl">{value || placeholder}</span>
            <span className="text-gray-300">Selected Icon</span>
          </div>
          
          {allowCustom && (
            <button
              type="button"
              onClick={() => setShowCustomInput(!showCustomInput)}
              className="text-xs text-gray-400 hover:text-gray-300 underline"
            >
              {showCustomInput ? 'Hide Custom' : 'Custom Input'}
            </button>
          )}
        </div>
        
        {/* Emoji Picker Grid */}
        <div className="grid grid-cols-8 gap-2 p-3 bg-gray-800 rounded-lg border border-gray-700">
          {currentIconSet.map((emoji) => (
            <button
              key={emoji}
              type="button"
              onClick={() => handleIconSelect(emoji)}
              className={`text-xl p-2 rounded-lg transition-all hover:bg-gray-700 ${
                value === emoji 
                  ? 'bg-yellow-400 bg-opacity-20 border border-yellow-400' 
                  : 'hover:bg-gray-700'
              }`}
              title={`Select ${emoji}`}
            >
              {emoji}
            </button>
          ))}
        </div>
        
        {/* Custom Icon Input */}
        {allowCustom && showCustomInput && (
          <div>
            <label className="block text-xs text-gray-400 mb-1">
              Enter custom emoji (max 2 characters):
            </label>
            <input
              type="text"
              value={value}
              onChange={handleCustomChange}
              placeholder={placeholder}
              maxLength={2}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-center placeholder-gray-400 focus:border-yellow-400 focus:outline-none"
            />
          </div>
        )}
        
        {/* Quick Reset Button */}
        {value && value !== placeholder && (
          <button
            type="button"
            onClick={() => handleIconSelect(placeholder)}
            className="text-xs text-gray-400 hover:text-gray-300"
          >
            Reset to default ({placeholder})
          </button>
        )}
      </div>
    </div>
  );
};

export default IconPicker;