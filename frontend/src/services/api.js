/**
 * API service for Resume Curator
 * Handles all backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class ApiError extends Error {
  constructor(message, status, details = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

/**
 * Make HTTP request with error handling
 */
async function makeRequest(url, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.error?.message || `HTTP ${response.status}`,
        response.status,
        errorData.error?.details || {}
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Network or other errors
    throw new ApiError(
      'Network error. Please check your connection.',
      0,
      { originalError: error.message }
    );
  }
}

/**
 * Upload resume file
 */
export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.error?.message || `Upload failed: HTTP ${response.status}`,
        response.status,
        errorData.error?.details || {}
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    throw new ApiError(
      'Upload failed. Please check your connection.',
      0,
      { originalError: error.message }
    );
  }
}

/**
 * Start resume analysis
 */
export async function startAnalysis(resumeId, jobDescription) {
  return makeRequest('/analyze', {
    method: 'POST',
    body: JSON.stringify({
      resume_id: resumeId,
      job_description: jobDescription,
    }),
  });
}

/**
 * Get analysis results
 */
export async function getAnalysis(analysisId) {
  return makeRequest(`/analysis/${analysisId}`);
}

/**
 * Poll for analysis completion
 */
export async function pollAnalysis(analysisId, maxAttempts = 30, intervalMs = 2000) {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const result = await getAnalysis(analysisId);
      
      // Check if analysis is complete
      if (result.analysis_data && 
          result.analysis_data.status !== 'processing' && 
          result.analysis_data.status !== 'pending') {
        return result;
      }
      
      // Wait before next attempt
      if (attempt < maxAttempts - 1) {
        await new Promise(resolve => setTimeout(resolve, intervalMs));
      }
    } catch (error) {
      // If it's a 404, the analysis might not exist yet, continue polling
      if (error.status === 404 && attempt < maxAttempts - 1) {
        await new Promise(resolve => setTimeout(resolve, intervalMs));
        continue;
      }
      throw error;
    }
  }
  
  throw new ApiError('Analysis timed out', 408, { maxAttempts, intervalMs });
}

/**
 * Health check
 */
export async function healthCheck() {
  return makeRequest('/health');
}

export { ApiError };