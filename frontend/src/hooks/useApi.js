/**
 * useApi Hook for Resume Curator Frontend
 * 
 * Provides React hook for managing API calls with loading states,
 * error handling, and automatic retries.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { apiService, API_ERROR_CODES } from '../services/api';

// Custom hook for API calls
export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const abortControllerRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const execute = useCallback(async (apiCall, options = {}) => {
    const {
      onSuccess = null,
      onError = null,
      onFinally = null,
      resetOnStart = true,
    } = options;

    try {
      // Cancel previous request if still running
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      abortControllerRef.current = new AbortController();

      if (resetOnStart) {
        setError(null);
        setData(null);
      }
      setLoading(true);

      const result = await apiCall();
      
      setData(result);
      if (onSuccess) {
        onSuccess(result);
      }
      
      return result;
    } catch (err) {
      // Don't set error if request was aborted
      if (err.name !== 'AbortError') {
        setError(err);
        if (onError) {
          onError(err);
        }
      }
      throw err;
    } finally {
      setLoading(false);
      if (onFinally) {
        onFinally();
      }
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setData(null);
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  return {
    loading,
    error,
    data,
    execute,
    reset,
  };
};

// Hook for file upload with progress
export const useFileUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const uploadFile = useCallback(async (file, options = {}) => {
    const { onSuccess = null, onError = null } = options;

    try {
      setUploading(true);
      setProgress(0);
      setError(null);
      setResult(null);

      const result = await apiService.uploadFile(file, (progressPercent) => {
        setProgress(progressPercent);
      });

      setResult(result);
      if (onSuccess) {
        onSuccess(result);
      }

      return result;
    } catch (err) {
      setError(err);
      if (onError) {
        onError(err);
      }
      throw err;
    } finally {
      setUploading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setUploading(false);
    setProgress(0);
    setError(null);
    setResult(null);
  }, []);

  return {
    uploading,
    progress,
    error,
    result,
    uploadFile,
    reset,
  };
};

// Hook for analysis with polling
export const useAnalysis = () => {
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [analysisId, setAnalysisId] = useState(null);
  const pollingIntervalRef = useRef(null);

  const startAnalysis = useCallback(async (analysisData, options = {}) => {
    const { onProgress = null, onSuccess = null, onError = null } = options;

    try {
      setAnalyzing(true);
      setProgress(0);
      setCurrentStep('Starting analysis...');
      setError(null);
      setResult(null);

      // Start analysis
      const startResult = await apiService.startAnalysis(analysisData);
      setAnalysisId(startResult.analysis_id);

      // Poll for progress
      pollingIntervalRef.current = setInterval(async () => {
        try {
          const progressResult = await apiService.getAnalysisProgress(startResult.analysis_id);
          
          setProgress(progressResult.progress_percentage);
          setCurrentStep(progressResult.current_step);

          if (onProgress) {
            onProgress(progressResult);
          }

          // Check if completed
          if (progressResult.status === 'completed') {
            clearInterval(pollingIntervalRef.current);
            
            // Get final result
            const finalResult = await apiService.getAnalysisResult(startResult.analysis_id);
            setResult(finalResult);
            setAnalyzing(false);

            if (onSuccess) {
              onSuccess(finalResult);
            }
          } else if (progressResult.status === 'failed') {
            clearInterval(pollingIntervalRef.current);
            const error = new Error(progressResult.error_message || 'Analysis failed');
            error.code = 'ANALYSIS_FAILED';
            throw error;
          }
        } catch (pollError) {
          clearInterval(pollingIntervalRef.current);
          setAnalyzing(false);
          setError(pollError);
          if (onError) {
            onError(pollError);
          }
        }
      }, 2000); // Poll every 2 seconds

      return startResult;
    } catch (err) {
      setAnalyzing(false);
      setError(err);
      if (onError) {
        onError(err);
      }
      throw err;
    }
  }, []);

  const cancelAnalysis = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }
    setAnalyzing(false);
    setProgress(0);
    setCurrentStep('');
  }, []);

  const reset = useCallback(() => {
    cancelAnalysis();
    setError(null);
    setResult(null);
    setAnalysisId(null);
  }, [cancelAnalysis]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  return {
    analyzing,
    progress,
    currentStep,
    error,
    result,
    analysisId,
    startAnalysis,
    cancelAnalysis,
    reset,
  };
};

// Hook for health check
export const useHealthCheck = () => {
  const [healthy, setHealthy] = useState(null);
  const [checking, setChecking] = useState(false);
  const [lastCheck, setLastCheck] = useState(null);

  const checkHealth = useCallback(async () => {
    try {
      setChecking(true);
      await apiService.healthCheck();
      setHealthy(true);
      setLastCheck(new Date());
    } catch {
      setHealthy(false);
      setLastCheck(new Date());
    } finally {
      setChecking(false);
    }
  }, []);

  // Auto check on mount
  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return {
    healthy,
    checking,
    lastCheck,
    checkHealth,
  };
};

// Hook for validation
export const useValidation = () => {
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [error, setError] = useState(null);

  const validateRequest = useCallback(async (analysisData) => {
    try {
      setValidating(true);
      setError(null);
      
      const result = await apiService.validateAnalysisRequest(analysisData);
      setValidationResult(result);
      
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setValidating(false);
    }
  }, []);

  const reset = useCallback(() => {
    setValidating(false);
    setValidationResult(null);
    setError(null);
  }, []);

  return {
    validating,
    validationResult,
    error,
    validateRequest,
    reset,
  };
};

// Error handling utilities
export const getErrorMessage = (error) => {
  if (!error) return '';
  
  // Use custom message if available
  if (error.message) {
    return error.message;
  }

  // Fallback based on error code
  switch (error.code) {
    case API_ERROR_CODES.NETWORK_ERROR:
      return 'Network error. Please check your internet connection.';
    case API_ERROR_CODES.TIMEOUT:
      return 'Request timed out. Please try again.';
    case API_ERROR_CODES.RATE_LIMITED:
      return 'Too many requests. Please wait a moment and try again.';
    case API_ERROR_CODES.SERVER_ERROR:
      return 'Server error. Please try again later.';
    case API_ERROR_CODES.VALIDATION_ERROR:
      return 'Please check your input and try again.';
    default:
      return 'An unexpected error occurred. Please try again.';
  }
};

export const isRetryableError = (error) => {
  if (!error) return false;
  
  const retryableCodes = [
    API_ERROR_CODES.NETWORK_ERROR,
    API_ERROR_CODES.TIMEOUT,
    API_ERROR_CODES.SERVER_ERROR,
    API_ERROR_CODES.BAD_GATEWAY,
    API_ERROR_CODES.SERVICE_UNAVAILABLE,
  ];
  
  return retryableCodes.includes(error.code);
};

export default useApi;