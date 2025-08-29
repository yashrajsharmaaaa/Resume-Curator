/**
 * MinimalFileUpload Component - Monochromatic Design
 * 
 * Clean file upload component with subtle borders and minimal styling.
 * Implements drag-and-drop functionality with opacity-based visual feedback.
 * Includes file validation with inline error display using monochromatic styling.
 * 
 * Requirements: 3.1, 3.2, 3.3, 3.4
 */

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const MinimalFileUpload = ({ 
  onFileSelect, 
  isProcessing = false, 
  error = null 
}) => {
  const [isDragActive, setIsDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      const error = rejectedFiles[0].errors[0].message;
      onFileSelect(null, error);
      return;
    }

    const file = acceptedFiles[0];
    if (file) {
      onFileSelect(file, null);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false),
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled: isProcessing
  });

  return (
    <div className="space-y-sm">
      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`
          w-full h-48 border-2 border-dashed border-gray-200 
          flex items-center justify-center
          ${isDragActive ? 'border-gray-800' : ''}
          ${isProcessing ? 'disabled-opacity' : 'hover-opacity focus-outline'}
        `}
        style={{
          cursor: isProcessing ? 'not-allowed' : 'pointer'
        }}
      >
        <input {...getInputProps()} />
        
        <div className="text-center">
          {isProcessing ? (
            <p className="text-base text-gray-500">Processing...</p>
          ) : isDragActive ? (
            <p className="text-base text-gray-800">Drop resume here</p>
          ) : (
            <p className="text-base text-gray-700">Drop resume here or click to select</p>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <p className="text-sm text-error">{error}</p>
      )}
    </div>
  );
};

export default MinimalFileUpload;