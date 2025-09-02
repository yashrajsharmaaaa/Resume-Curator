import React from 'react';

const Card = ({ 
  children, 
  className = '', 
  padding = 'md',
  shadow = true,
  ...props 
}) => {
  const baseClasses = 'bg-white rounded-lg border border-gray-200';
  
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };
  
  const shadowClasses = shadow ? 'shadow-sm hover:shadow-md transition-shadow duration-200' : '';
  
  const classes = `${baseClasses} ${paddingClasses[padding]} ${shadowClasses} ${className}`.trim();
  
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

export default Card;