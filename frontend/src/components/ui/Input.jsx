import React from 'react';

const Input = ({ 
  label,
  error,
  className = '',
  type = 'text',
  ...props 
}) => {
  const baseClasses = 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary transition-colors duration-200';
  const errorClasses = error ? 'border-red-500 focus:ring-red-500' : 'border-gray-300';
  
  const inputClasses = `${baseClasses} ${errorClasses} ${className}`.trim();
  
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input
        type={type}
        className={inputClasses}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

export default Input;