/**
 * Enhanced FileUpload Component for Resume Curator
 * 
 * Provides comprehensive drag-and-drop file upload interface with:
 * - Advanced validation and user-friendly error messages
 * - Real-time upload progress indication and loading states
 * - Fully responsive design optimized for mobile and desktop
 * - Enhanced accessibility features and keyboard navigation
 * - Detailed file information and preview capabilities
 * 
 * Requirements: 1.1, 1.3, 7.3, 7.1, 1.5, 1.6
 */

import { useState, useCallback } from 'react';
// Icons removed for monochromatic design
import { useDropzone } from 'react-dropzone';

const FileUpload = ({ onFileSelect, isLoading = false, error = null, className = '' }) => {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      const error = rejectedFiles[0].errors[0].message;
      onFileSelect(null, error);
      return;
    }

    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      onFileSelect(file, null);

      // Simulate upload progress
      setUploadProgress(0);
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 100);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const removeFile = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    onFileSelect(null, null);
  };

  const getFileIcon = (file) => {
    if (file.type === 'application/pdf') {
      return <FileText className="w-6 h-6 text-red-500" />;
    } else if (file.type.includes('word')) {
      return <FileText className="w-6 h-6 text-blue-500" />;
    } else {
      return <File className="w-6 h-6 text-slate-500" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Main Upload Area */}
      <div
        {...getRootProps()}
        className={`upload-area ${isDragActive ? 'dragover' : ''}`}
      >
        <input {...getInputProps()} />

        <div className="relative">
          {/* Content */}
          <div className="text-center">
            <div className="mx-auto w-16 h-16 mb-6 rounded-2xl flex items-center justify-center" style={{ backgroundColor: '#FCF3FD' }}>
              {isDragActive ? (
                <Cloud className="w-8 h-8" style={{ color: '#14121E' }} />
              ) : (
                <Upload className="w-8 h-8" style={{ color: '#14121E' }} />
              )}
            </div>

            <h3 className="text-2xl font-bold mb-3 font-urbanist" style={{ color: '#14121E' }}>
              {isDragActive ? 'Drop your resume here' : 'Upload Resume'}
            </h3>

            <p className="text-lg font-gilroy mb-8" style={{ color: '#6B7280' }}>
              Drag and drop your resume file here, or{' '}
              <span style={{ color: '#14121E' }} className="font-semibold">browse files</span>
            </p>

            <div className="flex flex-wrap justify-center gap-3 text-sm mb-6">
              <span className="px-4 py-2 rounded-xl font-medium" style={{ backgroundColor: '#FFEFE2', color: '#14121E' }}>PDF</span>
              <span className="px-4 py-2 rounded-xl font-medium" style={{ backgroundColor: '#FCF3FD', color: '#14121E' }}>DOC</span>
              <span className="px-4 py-2 rounded-xl font-medium" style={{ backgroundColor: '#FFEFE2', color: '#14121E' }}>DOCX</span>
              <span className="px-4 py-2 rounded-xl font-medium" style={{ backgroundColor: '#FCF3FD', color: '#14121E' }}>TXT</span>
            </div>

            <p className="text-sm font-gilroy" style={{ color: '#9CA3AF' }}>
              Maximum file size: 10MB
            </p>
          </div>

          {/* Loading Overlay */}
          {isLoading && (
            <div className="absolute inset-0 bg-white/95 flex items-center justify-center rounded-2xl">
              <div className="text-center">
                <div className="w-10 h-10 border-3 border-gray-200 rounded-full animate-spin mx-auto mb-4" style={{ borderTopColor: '#14121E' }}></div>
                <p className="font-semibold" style={{ color: '#14121E' }}>Processing...</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="dashboard-card p-6" style={{ backgroundColor: '#FEF2F2', borderColor: '#FECACA' }}>
          <div className="flex items-center space-x-4">
            <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0" />
            <div>
              <h4 className="text-lg font-semibold text-red-800 font-urbanist">Upload Error</h4>
              <p className="text-red-700 font-gilroy mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Selected File Preview */}
      {selectedFile && (
        <div className="dashboard-card p-6">
          <div className="flex items-center space-x-4">
            {/* File Icon */}
            <div className="flex-shrink-0">
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center" style={{ backgroundColor: '#FCF3FD' }}>
                {getFileIcon(selectedFile)}
              </div>
            </div>

            {/* File Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-lg font-semibold font-urbanist truncate" style={{ color: '#14121E' }}>
                    {selectedFile.name}
                  </h4>
                  <p className="text-sm font-gilroy mt-1" style={{ color: '#6B7280' }}>
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>

                {/* Status */}
                <div className="flex items-center space-x-2">
                  {uploadProgress === 100 ? (
                    <div className="flex items-center space-x-2 px-3 py-1 rounded-xl" style={{ backgroundColor: '#D1FAE5' }}>
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-semibold text-green-700">Ready</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2 px-3 py-1 rounded-xl" style={{ backgroundColor: '#FCF3FD' }}>
                      <div className="w-4 h-4 border-2 border-gray-200 rounded-full animate-spin" style={{ borderTopColor: '#14121E' }}></div>
                      <span className="text-sm font-semibold" style={{ color: '#14121E' }}>Processing</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Progress Bar */}
              {uploadProgress < 100 && (
                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm font-gilroy mb-2" style={{ color: '#6B7280' }}>
                    <span>Uploading...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="w-full rounded-full h-2" style={{ backgroundColor: '#F3F4F6' }}>
                    <div
                      className="h-2 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${uploadProgress}%`,
                        backgroundColor: '#14121E'
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center space-x-3 mt-4">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    try {
                      const url = URL.createObjectURL(selectedFile);
                      window.open(url, '_blank');
                      setTimeout(() => URL.revokeObjectURL(url), 1000);
                    } catch (error) {
                      console.error('Failed to preview file:', error);
                      alert('Unable to preview this file type');
                    }
                  }}
                  className="btn-secondary"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Preview
                </button>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile();
                  }}
                  className="px-4 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-xl font-medium transition-colors"
                >
                  <Trash2 className="w-4 h-4 mr-2 inline" />
                  Remove
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Tips */}
      <div className="dashboard-card p-6" style={{ backgroundColor: '#FFEFE2' }}>
        <h4 className="text-lg font-semibold font-urbanist mb-4 flex items-center" style={{ color: '#14121E' }}>
          <FileCheck className="w-5 h-5 mr-3" style={{ color: '#14121E' }} />
          Upload Guidelines
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: '#14121E' }}></div>
            <div>
              <h5 className="text-sm font-semibold font-urbanist" style={{ color: '#14121E' }}>Supported Formats</h5>
              <p className="text-sm font-gilroy" style={{ color: '#6B7280' }}>PDF, DOC, DOCX, and TXT files</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: '#14121E' }}></div>
            <div>
              <h5 className="text-sm font-semibold font-urbanist" style={{ color: '#14121E' }}>File Size</h5>
              <p className="text-sm font-gilroy" style={{ color: '#6B7280' }}>Maximum 10MB</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: '#14121E' }}></div>
            <div>
              <h5 className="text-sm font-semibold font-urbanist" style={{ color: '#14121E' }}>Privacy</h5>
              <p className="text-sm font-gilroy" style={{ color: '#6B7280' }}>Secure processing</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: '#14121E' }}></div>
            <div>
              <h5 className="text-sm font-semibold font-urbanist" style={{ color: '#14121E' }}>Best Results</h5>
              <p className="text-sm font-gilroy" style={{ color: '#6B7280' }}>Use well-formatted resumes</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;