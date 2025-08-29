/**
 * EssentialButton Component - Monochromatic Design
 * 
 * Button component with primary and secondary variants using monochromatic colors.
 * Hover and disabled states using opacity variations only.
 * Consistent 48px height and typography alignment.
 * 
 * Requirements: 4.5, 6.1, 6.2
 */

import { useCallback } from 'react';

const EssentialButton = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  disabled = false,
  type = 'button',
  className = ''
}) => {
  const handleClick = useCallback((e) => {
    if (!disabled && onClick) {
      onClick(e);
    }
  }, [disabled, onClick]);

  const baseClasses = `
    h-12 px-6 text-base font-medium
    ${variant === 'primary' 
      ? 'bg-gray-800 text-white' 
      : 'bg-gray-50 text-gray-800'
    }
    ${disabled ? 'disabled-opacity' : 'hover-opacity'}
    focus-outline
    ${className}
  `;

  return (
    <button
      type={type}
      onClick={handleClick}
      disabled={disabled}
      className={baseClasses.trim()}
    >
      {children}
    </button>
  );
};

export default EssentialButton;