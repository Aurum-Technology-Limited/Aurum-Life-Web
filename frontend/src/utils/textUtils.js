/**
 * Text utility functions for dynamic sizing and validation
 */

// Character limits for different components
export const CHARACTER_LIMITS = {
  AREA_NAME: 45,
  AREA_DESCRIPTION: 200,
  PROJECT_NAME: 50,
  PROJECT_DESCRIPTION: 250,
  PILLAR_NAME: 40,
  PILLAR_DESCRIPTION: 150,
  TASK_NAME: 60,
  TASK_DESCRIPTION: 300,
  ACHIEVEMENT_NAME: 40,
  ACHIEVEMENT_DESCRIPTION: 150
};

/**
 * Get dynamic font size class based on text length
 * @param {string} text - The text to analyze
 * @param {string} type - The type of text (title, subtitle, etc.)
 * @returns {string} - CSS class for font size
 */
export const getDynamicFontSize = (text, type = 'title') => {
  if (!text) return 'text-dynamic-base';
  
  const length = text.length;
  
  switch (type) {
    case 'title':
      if (length > 35) return 'text-dynamic-xs';
      if (length > 25) return 'text-dynamic-sm';
      if (length > 15) return 'text-dynamic-base';
      return 'text-dynamic-lg';
      
    case 'subtitle':
      if (length > 40) return 'text-dynamic-xs';
      if (length > 30) return 'text-dynamic-sm';
      return 'text-dynamic-base';
      
    case 'badge':
      if (length > 12) return 'text-xs';
      return 'text-xs';
      
    default:
      return 'text-dynamic-base';
  }
};

/**
 * Get dynamic line clamp based on text length
 * @param {string} text - The text to analyze
 * @param {number} maxLines - Maximum lines allowed
 * @returns {string} - CSS class for line clamping
 */
export const getDynamicLineClamp = (text, maxLines = 2) => {
  if (!text) return '';
  
  const estimatedLines = Math.ceil(text.length / 35); // Rough estimate
  const actualLines = Math.min(estimatedLines, maxLines);
  
  return `line-clamp-${actualLines}`;
};

/**
 * Validate text length and return status
 * @param {string} text - The text to validate
 * @param {number} maxLength - Maximum allowed length
 * @returns {object} - Validation result with status and message
 */
export const validateTextLength = (text, maxLength) => {
  if (!text) {
    return { valid: true, status: 'empty', message: '', remaining: maxLength };
  }
  
  const length = text.length;
  const remaining = maxLength - length;
  
  if (length > maxLength) {
    return {
      valid: false,
      status: 'error',
      message: `Text is too long (${length}/${maxLength})`,
      remaining: remaining
    };
  }
  
  if (length > maxLength * 0.9) {
    return {
      valid: true,
      status: 'warning',
      message: `Approaching limit (${length}/${maxLength})`,
      remaining: remaining
    };
  }
  
  return {
    valid: true,
    status: 'normal',
    message: '',
    remaining: remaining
  };
};

/**
 * Truncate text with word boundaries
 * @param {string} text - The text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} - Truncated text
 */
export const smartTruncate = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text;
  
  // Try to truncate at word boundary
  const truncated = text.substring(0, maxLength);
  const lastSpace = truncated.lastIndexOf(' ');
  
  if (lastSpace > maxLength * 0.7) {
    return truncated.substring(0, lastSpace) + '...';
  }
  
  return truncated + '...';
};

/**
 * Create a character counter component data
 * @param {string} text - Current text
 * @param {number} maxLength - Maximum length
 * @returns {object} - Counter component data
 */
export const getCharacterCounterData = (text, maxLength) => {
  const validation = validateTextLength(text, maxLength);
  
  return {
    count: text ? text.length : 0,
    max: maxLength,
    remaining: validation.remaining,
    status: validation.status,
    className: `char-counter ${validation.status}`
  };
};