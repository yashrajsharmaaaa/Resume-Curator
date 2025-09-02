import React, { useState, useCallback } from 'react';
import { Button, LoadingSpinner } from '../ui';

const FileUpload = ({ onFileSelect, isUploading = false, error = null }) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const validateFile = (file) => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf'];

    if (!allowedTypes.includes(file.type)) {
      return 'Please upload a PDF file only.';
    }

    if (file.size > maxSize) {
      return 'File size must be less than 10MB.';
    }

    return null;
  };

  const handleFileSelect = useCallback((file) => {
    const validationError = validateFile(file);
    if (validationError) {
      onFileSelect(null, validationError);
      return;
    }

    onFileSelect(file, null);
  }, [onFileSelect]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleInputChange = useCallback((e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleButtonClick = () => {
    document.getElementById('file-input').click();
  };

  return (
    <div className="w-full">
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200
          ${isDragOver ? 'border-primary bg-blue-50' : 'border-gray-300'}
          ${isUploading ? 'pointer-events-none opacity-50' : 'hover:border-primary hover:bg-gray-50'}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          id="file-input"
          type="file"
          accept=".pdf"
          onChange={handleInputChange}
          className="hidden"
          disabled={isUploading}
        />

        {isUploading ? (
          <div className="flex flex-col items-center">
            <LoadingSpinner size="lg" className="mb-4" />
            <p className="text-gray-600">Uploading your resume...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-4"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Upload your resume
            </h3>
            
            <p className="text-gray-500 mb-4">
              Drag and drop your PDF file here, or click to browse
            </p>
            
            <Button variant="primary" onClick={handleButtonClick}>
              Choose File
            </Button>
            
            <p className="text-xs text-gray-400 mt-3">
              PDF files only, up to 10MB
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;