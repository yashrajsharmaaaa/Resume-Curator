import React from 'react';

const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };
  
  const classes = `animate-spin rounded-full border-2 border-gray-300 border-t-primary ${sizeClasses[size]} ${className}`.trim();
  
  return <div className={classes} />;
};

export default LoadingSpinner;