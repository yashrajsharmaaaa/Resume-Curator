/**
 * ProgressIndicator Component for Resume Curator
 * 
 * Provides progress indicators for file processing and analysis
 * as required by Requirements 7.3, 7.4, 1.6.
 */

import { useState, useEffect } from 'react';
import { 
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

const ProgressIndicator = ({
  steps = [],
  currentStep = 0,
  status = 'processing', // 'processing', 'completed', 'error', 'waiting'
  showEstimatedTime = true,
  estimatedTimeRemaining = null,
  compact = false,
  className = ''
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);

  // Track elapsed time
  useEffect(() => {
    if (status === 'processing') {
      const startTime = Date.now();
      const interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [status]);

  // Format time
  const formatTime = (seconds) => {
    if (seconds < 60) {
      return `${seconds}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  // Get step status
  const getStepStatus = (stepIndex) => {
    if (stepIndex < currentStep) return 'completed';
    if (stepIndex === currentStep) {
      return status === 'error' ? 'error' : 'active';
    }
    return 'pending';
  };

  // Get step icon
  const getStepIcon = (stepIndex, stepStatus) => {
    switch (stepStatus) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'active':
        return status === 'error' ? (
          <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
        ) : (
          <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />
        );
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return (
          <div className="h-5 w-5 rounded-full border-2 border-gray-300 bg-white" />
        );
    }
  };

  // Get step classes
  const getStepClasses = (stepStatus) => {
    switch (stepStatus) {
      case 'completed':
        return 'text-green-700';
      case 'active':
        return status === 'error' ? 'text-red-700' : 'text-blue-700';
      case 'error':
        return 'text-red-700';
      default:
        return 'text-gray-500';
    }
  };

  // Get connector classes
  const getConnectorClasses = (stepIndex) => {
    const stepStatus = getStepStatus(stepIndex);
    if (stepStatus === 'completed') {
      return 'bg-green-500';
    }
    if (stepStatus === 'active' && status !== 'error') {
      return 'bg-blue-500';
    }
    if (stepStatus === 'error') {
      return 'bg-red-500';
    }
    return 'bg-gray-300';
  };

  if (compact) {
    // Compact version - just a progress bar
    const progressPercentage = steps.length > 0 ? (currentStep / steps.length) * 100 : 0;
    
    return (
      <div className={`w-full ${className}`}>
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            {steps[currentStep]?.label || 'Processing...'}
          </span>
          {showEstimatedTime && estimatedTimeRemaining && (
            <span className="text-xs text-gray-500">
              ~{formatTime(estimatedTimeRemaining)} remaining
            </span>
          )}
        </div>
        <div className="bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              status === 'error' ? 'bg-red-500' : 'bg-blue-500'
            }`}
            style={{ width: `${Math.min(progressPercentage, 100)}%` }}
          />
        </div>
        {status === 'processing' && (
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Step {currentStep + 1} of {steps.length}</span>
            <span>Elapsed: {formatTime(elapsedTime)}</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`w-full max-w-2xl ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-medium text-gray-900">
          Analysis Progress
        </h3>
        {showEstimatedTime && (
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            {estimatedTimeRemaining && (
              <div className="flex items-center space-x-1">
                <ClockIcon className="h-4 w-4" />
                <span>~{formatTime(estimatedTimeRemaining)} remaining</span>
              </div>
            )}
            <span>Elapsed: {formatTime(elapsedTime)}</span>
          </div>
        )}
      </div>

      {/* Steps */}
      <div className="space-y-4">
        {steps.map((step, index) => {
          const stepStatus = getStepStatus(index);
          
          return (
            <div key={index} className="relative">
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="absolute left-2.5 top-8 w-0.5 h-8 -ml-px">
                  <div className={`w-full h-full ${getConnectorClasses(index)}`} />
                </div>
              )}
              
              {/* Step content */}
              <div className="flex items-start space-x-3">
                {/* Icon */}
                <div className="flex-shrink-0">
                  {getStepIcon(index, stepStatus)}
                </div>
                
                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className={`text-sm font-medium ${getStepClasses(stepStatus)}`}>
                      {step.label}
                    </p>
                    {stepStatus === 'completed' && step.duration && (
                      <span className="text-xs text-gray-500">
                        {formatTime(step.duration)}
                      </span>
                    )}
                  </div>
                  
                  {step.description && (
                    <p className="text-xs text-gray-500 mt-1">
                      {step.description}
                    </p>
                  )}
                  
                  {/* Progress bar for active step */}
                  {stepStatus === 'active' && step.progress !== undefined && (
                    <div className="mt-2">
                      <div className="bg-gray-200 rounded-full h-1">
                        <div
                          className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(step.progress, 100)}%` }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Error message */}
                  {stepStatus === 'error' && step.error && (
                    <p className="text-xs text-red-600 mt-1">
                      {step.error}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Overall status */}
      <div className="mt-6 p-4 rounded-lg border">
        {status === 'completed' ? (
          <div className="flex items-center space-x-2 text-green-700">
            <CheckCircleIcon className="h-5 w-5" />
            <span className="font-medium">Analysis completed successfully!</span>
          </div>
        ) : status === 'error' ? (
          <div className="flex items-center space-x-2 text-red-700">
            <ExclamationTriangleIcon className="h-5 w-5" />
            <span className="font-medium">Analysis failed. Please try again.</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2 text-blue-700">
            <ArrowPathIcon className="h-5 w-5 animate-spin" />
            <span className="font-medium">
              {steps[currentStep]?.label || 'Processing your request...'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressIndicator;