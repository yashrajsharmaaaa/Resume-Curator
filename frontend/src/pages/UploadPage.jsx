import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import { Card } from '../components/ui';
import { FileUpload, UploadProgress } from '../components/upload';
import { useApp } from '../context/AppContext';

const UploadPage = () => {
  const navigate = useNavigate();
  const { dispatch } = useApp();
  const [uploadState, setUploadState] = useState({
    isUploading: false,
    progress: 0,
    error: null,
    uploadedFile: null
  });

  const handleFileSelect = async (file, error) => {
    if (error) {
      setUploadState(prev => ({ ...prev, error }));
      return;
    }

    if (!file) return;

    // Start upload process
    setUploadState({
      isUploading: true,
      progress: 0,
      error: null,
      uploadedFile: file
    });

    dispatch({ type: 'SET_UPLOADING', payload: true });

    try {
      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setUploadState(prev => ({ ...prev, progress }));
      }

      // Simulate successful upload
      const resumeData = {
        id: Date.now().toString(),
        fileName: file.name,
        fileSize: file.size,
        uploadDate: new Date().toISOString().split('T')[0],
        score: Math.floor(Math.random() * 30) + 70 // Random score between 70-100
      };

      dispatch({ type: 'ADD_RESUME', payload: resumeData });

      setUploadState(prev => ({ 
        ...prev, 
        isUploading: false,
        progress: 100
      }));

      // Navigate to results after a short delay
      setTimeout(() => {
        navigate('/results');
      }, 1500);

    } catch (uploadError) {
      setUploadState(prev => ({ 
        ...prev, 
        isUploading: false,
        error: 'Upload failed. Please try again.'
      }));
      dispatch({ type: 'SET_ERROR', payload: 'Upload failed. Please try again.' });
    }
  };

  const handleStartOver = () => {
    setUploadState({
      isUploading: false,
      progress: 0,
      error: null,
      uploadedFile: null
    });
    dispatch({ type: 'CLEAR_ERROR' });
  };

  return (
    <div>
      <PageHeader 
        title="Upload Resume" 
        subtitle="Upload your resume to get started with analysis"
      />
      
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          {uploadState.uploadedFile && uploadState.progress > 0 ? (
            <div className="space-y-6">
              <UploadProgress
                progress={uploadState.progress}
                fileName={uploadState.uploadedFile.name}
                status={uploadState.progress === 100 ? 'success' : 'uploading'}
              />
              
              {uploadState.progress === 100 && (
                <div className="text-center">
                  <div className="mb-4">
                    <svg className="mx-auto h-12 w-12 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Upload Successful!
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Redirecting to analysis results...
                  </p>
                </div>
              )}
            </div>
          ) : (
            <FileUpload
              onFileSelect={handleFileSelect}
              isUploading={uploadState.isUploading}
              error={uploadState.error}
            />
          )}
        </Card>

        {uploadState.error && (
          <div className="text-center">
            <button
              onClick={handleStartOver}
              className="text-primary hover:text-blue-700 text-sm font-medium"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadPage;