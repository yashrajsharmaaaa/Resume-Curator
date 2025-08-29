import { useState, useCallback } from 'react'
import MainContainer from './components/MainContainer'
import ProgressiveSection from './components/ProgressiveSection'
import MinimalFileUpload from './components/MinimalFileUpload'
import CleanTextInput from './components/CleanTextInput'
import EssentialButton from './components/EssentialButton'
import ResultsDisplay from './components/ResultsDisplay'
import { uploadResume, startAnalysis, pollAnalysis, ApiError } from './services/api'

function App() {
  // Essential state only
  const [currentStep, setCurrentStep] = useState('upload') // 'upload' | 'input' | 'analyze' | 'results'
  const [resumeData, setResumeData] = useState(null) // Backend resume data
  const [jobDescription, setJobDescription] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState(null)
  const [error, setError] = useState(null)

  // Handle file selection and upload
  const handleFileSelect = useCallback(async (file, fileError) => {
    if (fileError) {
      setError(fileError)
      return
    }

    setError(null)
    setIsProcessing(true)

    try {
      // Upload file to backend
      const uploadResult = await uploadResume(file)
      setResumeData(uploadResult)
      setCurrentStep('input')
    } catch (apiError) {
      if (apiError instanceof ApiError) {
        setError(apiError.message)
      } else {
        setError('Failed to upload resume. Please try again.')
      }
    } finally {
      setIsProcessing(false)
    }
  }, [])

  // Handle job description change
  const handleJobDescriptionChange = useCallback((value) => {
    setJobDescription(value)
    setError(null)
  }, [])

  // Handle analysis submission
  const handleAnalyze = useCallback(async () => {
    if (!resumeData || jobDescription.length < 50) {
      setError('Please upload a resume and provide a job description (minimum 50 characters)')
      return
    }

    setIsProcessing(true)
    setError(null)
    setCurrentStep('analyze')

    try {
      // Start analysis
      const analysisResponse = await startAnalysis(resumeData.id, jobDescription)

      // Poll for completion
      const completedAnalysis = await pollAnalysis(analysisResponse.id)

      // Transform backend data to frontend format
      const transformedResults = transformAnalysisData(completedAnalysis)

      setAnalysisResults(transformedResults)
      setCurrentStep('results')
    } catch (apiError) {
      if (apiError instanceof ApiError) {
        setError(apiError.message)
      } else {
        setError('Analysis failed. Please try again.')
      }
      setCurrentStep('input')
    } finally {
      setIsProcessing(false)
    }
  }, [resumeData, jobDescription])

  // Transform backend analysis data to frontend format
  const transformAnalysisData = useCallback((backendData) => {
    const analysisData = backendData.analysis_data || {}

    return {
      compatibilityScore: backendData.compatibility_score || analysisData.compatibility_score || 0,
      missingSkills: analysisData.missing_skills || analysisData.gaps || [],
      topRecommendations: analysisData.recommendations || analysisData.suggestions || []
    }
  }, [])

  // Handle starting over
  const handleStartOver = useCallback(() => {
    setCurrentStep('upload')
    setResumeData(null)
    setJobDescription('')
    setAnalysisResults(null)
    setError(null)
  }, [])

  return (
    <div className="min-h-screen bg-white">
      <MainContainer>
        <div className="space-y-xl">
          {/* Upload Step */}
          <ProgressiveSection
            isVisible={currentStep === 'upload'}
          >
            <div className="text-center mb-lg">
              <h1 className="text-3xl font-bold mb-md text-gray-800">
                Resume Analysis
              </h1>
              <p className="text-base text-gray-700">
                Upload your resume to get AI-powered insights and recommendations.
              </p>
            </div>

            <MinimalFileUpload
              onFileSelect={handleFileSelect}
              isProcessing={isProcessing}
              error={error}
            />
          </ProgressiveSection>

          {/* Job Description Input Step */}
          <ProgressiveSection
            isVisible={currentStep === 'input'}
          >
            <div className="text-center mb-lg">
              <h2 className="text-xl font-semibold mb-md text-gray-800">
                Job Description
              </h2>
              <p className="text-base text-gray-700">
                Paste the job description to analyze compatibility.
              </p>
            </div>

            <CleanTextInput
              value={jobDescription}
              onChange={handleJobDescriptionChange}
              placeholder="Paste the complete job description here, including requirements, responsibilities, and qualifications..."
              maxLength={5000}
            />

            {jobDescription.length >= 50 && (
              <div className="text-center mt-lg">
                <EssentialButton
                  onClick={handleAnalyze}
                  variant="primary"
                  disabled={isProcessing}
                >
                  Analyze Resume
                </EssentialButton>
              </div>
            )}
          </ProgressiveSection>

          {/* Processing Step */}
          <ProgressiveSection
            isVisible={currentStep === 'analyze'}
          >
            <div className="text-center">
              <h2 className="text-xl font-semibold mb-md text-gray-800">
                Analyzing Resume
              </h2>
              <p className="text-base text-gray-500">
                Processing your resume and job requirements...
              </p>
            </div>
          </ProgressiveSection>

          {/* Results Step */}
          <ProgressiveSection
            isVisible={currentStep === 'results'}
          >
            <div className="text-center mb-lg">
              <h2 className="text-xl font-semibold mb-md text-gray-800">
                Analysis Results
              </h2>
            </div>

            {analysisResults && (
              <ResultsDisplay
                compatibilityScore={analysisResults.compatibilityScore}
                missingSkills={analysisResults.missingSkills}
                topRecommendations={analysisResults.topRecommendations}
              />
            )}

            <div className="text-center mt-lg">
              <EssentialButton
                onClick={handleStartOver}
                variant="secondary"
              >
                Start New Analysis
              </EssentialButton>
            </div>
          </ProgressiveSection>

          {/* Error Display */}
          {error && (
            <div className="text-center">
              <p className="text-sm text-error">{error}</p>
            </div>
          )}
        </div>
      </MainContainer>
    </div>
  );
}

export default App;