import React from 'react';

const PageHeader = ({ title, subtitle, children }) => {
  return (
    <div className="mb-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          {subtitle && (
            <p className="mt-2 text-lg text-gray-600">{subtitle}</p>
          )}
        </div>
        {children && (
          <div className="mt-4 sm:mt-0">
            {children}
          </div>
        )}
      </div>
    </div>
  );
};

export default PageHeader;