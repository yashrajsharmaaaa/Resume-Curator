/**
 * CleanTextInput Component - Monochromatic Design
 * 
 * Minimal text area component with subtle background and no decorative borders.
 * Character count display appears only when approaching limits.
 * Focus states using outline-only styling.
 * 
 * Requirements: 4.1, 4.2, 4.3, 4.4
 */

import { useState, useCallback } from 'react';

const CleanTextInput = ({ 
  value, 
  onChange, 
  placeholder, 
  maxLength = 5000,
  showCharCount = true 
}) => {
  const [isFocused, setIsFocused] = useState(false);
  
  const charCount = value.length;
  const isApproachingLimit = charCount >= maxLength * 0.9;
  const showCount = showCharCount && isApproachingLimit;

  const handleChange = useCallback((e) => {
    const newValue = e.target.value;
    if (newValue.length <= maxLength) {
      onChange(newValue);
    }
  }, [onChange, maxLength]);

  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);

  return (
    <div className="space-y-xs">
      {/* Text Area */}
      <textarea
        value={value}
        onChange={handleChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        placeholder={placeholder}
        className={`
          w-full min-h-32 p-md text-base resize-none
          ${isFocused ? 'bg-white' : 'bg-gray-50'}
          border-0 focus-outline
        `}
        rows={6}
      />

      {/* Character Count */}
      {showCount && (
        <div className={`text-xs text-right ${charCount >= maxLength ? 'text-error' : 'text-gray-500'}`}>
          {charCount}/{maxLength}
        </div>
      )}
    </div>
  );
};

export default CleanTextInput;