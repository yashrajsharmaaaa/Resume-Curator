/**
 * ResultsDashboard Component for Resume Curator
 * 
 * Displays compatibility score, missing skills, and recommendations
 * as required by Requirements 3.3, 3.4, 4.3, 6.2, 7.5.
 */

import { useState } from 'react';
import { 
  ChartBarIcon,
  ExclamationTriangleIcon,
  LightBulbIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  StarIcon,
  DocumentTextIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';
import { 
  ChartBarIcon as ChartBarIconSolid,
  StarIcon as StarIconSolid
} from '@heroicons/react/24/solid';

const ResultsDashboard = ({
  analysisResult,
  isLoading = false,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState('overview');

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow-lg p-8 ${className}`}>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="space-y-4">
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!analysisResult) {
    return null;
  }

  const {
    compatibility_score,
    recommendations,
    analysis_metadata,
    processing_time_ms,
    completed_at
  } = analysisResult;

  // Get score color and category
  const getScoreInfo = (score) => {
    if (score >= 80) {
      return {
        color: 'text-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        category: 'Excellent Match',
        icon: CheckCircleIcon,
        description: 'Your resume is an excellent match for this position!'
      };
    } else if (score >= 65) {
      return {
        color: 'text-blue-600',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        category: 'Good Match',
        icon: ChartBarIconSolid,
        description: 'Your resume is a good match with some areas for improvement.'
      };
    } else if (score >= 50) {
      return {
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        category: 'Fair Match',
        icon: ExclamationTriangleIcon,
        description: 'Your resume has potential but needs significant improvements.'
      };
    } else {
      return {
        color: 'text-red-600',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        category: 'Needs Improvement',
        icon: ExclamationTriangleIcon,
        description: 'Your resume needs substantial improvements to match this position.'
      };
    }
  };

  const scoreInfo = getScoreInfo(compatibility_score.overall_score);
  const ScoreIcon = scoreInfo.icon;

  // Tab configuration
  const tabs = [
    { id: 'overview', label: 'Overview', icon: ChartBarIcon },
    { id: 'recommendations', label: 'Recommendations', icon: LightBulbIcon },
    { id: 'details', label: 'Detailed Analysis', icon: DocumentTextIcon }
  ];

  // Component score breakdown
  const componentScores = compatibility_score.component_scores || {};
  const scoreComponents = [
    { 
      key: 'skills_match', 
      label: 'Skills Match', 
      icon: CpuChipIcon,
      description: 'How well your skills align with job requirements'
    },
    { 
      key: 'experience_level', 
      label: 'Experience Level', 
      icon: BriefcaseIcon,
      description: 'Your experience level compared to job requirements'
    },
    { 
      key: 'education_match', 
      label: 'Education Match', 
      icon: AcademicCapIcon,
      description: 'Your educational background alignment'
    },
    { 
      key: 'industry_experience', 
      label: 'Industry Experience', 
      icon: ArrowTrendingUpIcon,
      description: 'Your experience in the relevant industry'
    }
  ];

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="px-8 py-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Analysis Results
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Completed {new Date(completed_at).toLocaleString()} • 
              Processing time: {Math.round(processing_time_ms)}ms
            </p>
          </div>
          <div className="text-right">
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${scoreInfo.bgColor} ${scoreInfo.color} ${scoreInfo.borderColor} border`}>
              <ScoreIcon className="h-4 w-4 mr-1" />
              {scoreInfo.category}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-8" aria-label="Tabs">
          {tabs.map((tab) => {
            const TabIcon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors`}
              >
                <TabIcon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Compatibility Score */}
            <div className={`rounded-lg border p-6 ${scoreInfo.bgColor} ${scoreInfo.borderColor}`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <ScoreIcon className={`h-8 w-8 ${scoreInfo.color}`} />
                  <div>
                    <h3 className={`text-xl font-semibold ${scoreInfo.color}`}>
                      Compatibility Score
                    </h3>
                    <p className="text-sm text-gray-600">
                      {scoreInfo.description}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-4xl font-bold ${scoreInfo.color}`}>
                    {Math.round(compatibility_score.overall_score)}%
                  </div>
                  <div className="text-sm text-gray-500">
                    Confidence: {Math.round(compatibility_score.confidence_level * 100)}%
                  </div>
                </div>
              </div>
              
              {/* Score breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
                {scoreComponents.map((component) => {
                  const ComponentIcon = component.icon;
                  const score = componentScores[component.key] || 0;
                  
                  return (
                    <div key={component.key} className="bg-white rounded-lg p-4 border">
                      <div className="flex items-center space-x-2 mb-2">
                        <ComponentIcon className="h-5 w-5 text-gray-600" />
                        <span className="text-sm font-medium text-gray-900">
                          {component.label}
                        </span>
                      </div>
                      <div className="text-2xl font-bold text-gray-900 mb-1">
                        {Math.round(score)}%
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            score >= 80 ? 'bg-green-500' :
                            score >= 60 ? 'bg-blue-500' :
                            score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${Math.min(score, 100)}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-2">
                        {component.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Key Insights */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <LightBulbIcon className="h-5 w-5 mr-2 text-yellow-500" />
                Key Insights
              </h3>
              <div className="space-y-3">
                {compatibility_score.score_explanation?.slice(0, 3).map((insight, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-xs font-medium text-blue-600">{index + 1}</span>
                    </div>
                    <p className="text-sm text-gray-700">{insight}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Wins */}
            {recommendations?.quick_wins?.length > 0 && (
              <div className="bg-green-50 rounded-lg p-6 border border-green-200">
                <h3 className="text-lg font-semibold text-green-800 mb-4 flex items-center">
                  <StarIconSolid className="h-5 w-5 mr-2 text-green-600" />
                  Quick Wins
                </h3>
                <div className="space-y-3">
                  {recommendations.quick_wins.slice(0, 3).map((rec, index) => (
                    <div key={index} className="bg-white rounded-lg p-4 border border-green-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-green-800">{rec.title}</h4>
                          <p className="text-sm text-green-700 mt-1">{rec.specific_action}</p>
                        </div>
                        <div className="ml-4 text-right">
                          <div className="text-sm font-medium text-green-600">
                            Impact: {Math.round(rec.impact_score)}%
                          </div>
                          <div className="text-xs text-green-500">
                            {rec.effort_level} effort
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-semibold text-gray-900">
                Improvement Recommendations
              </h3>
              <div className="text-sm text-gray-500">
                {recommendations?.recommendations?.length || 0} recommendations
              </div>
            </div>

            {/* Priority Recommendations */}
            {recommendations?.priority_recommendations?.length > 0 && (
              <div className="space-y-4">
                <h4 className="text-lg font-medium text-gray-900 flex items-center">
                  <ExclamationTriangleIcon className="h-5 w-5 mr-2 text-red-500" />
                  High Priority
                </h4>
                {recommendations.priority_recommendations.map((rec, index) => (
                  <div key={index} className="border border-red-200 rounded-lg p-6 bg-red-50">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h5 className="font-semibold text-red-800">{rec.title}</h5>
                        <p className="text-sm text-red-700 mt-1">{rec.description}</p>
                      </div>
                      <div className="ml-4 text-right">
                        <div className="text-sm font-medium text-red-600">
                          Impact: {Math.round(rec.impact_score)}%
                        </div>
                        <div className="text-xs text-red-500 capitalize">
                          {rec.effort_level} effort
                        </div>
                      </div>
                    </div>
                    <div className="bg-white rounded-md p-3 border border-red-200">
                      <p className="text-sm text-gray-700">
                        <strong>Action:</strong> {rec.specific_action}
                      </p>
                      {rec.example && (
                        <p className="text-sm text-gray-600 mt-2">
                          <strong>Example:</strong> {rec.example}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* All Recommendations by Category */}
            {recommendations?.recommendations_by_category && (
              <div className="space-y-6">
                {Object.entries(recommendations.recommendations_by_category).map(([category, recs]) => (
                  <div key={category} className="space-y-4">
                    <h4 className="text-lg font-medium text-gray-900 capitalize">
                      {category.replace('_', ' ')}
                    </h4>
                    <div className="space-y-3">
                      {recs.slice(0, 5).map((rec, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h5 className="font-medium text-gray-900">{rec.title}</h5>
                              <p className="text-sm text-gray-600 mt-1">{rec.specific_action}</p>
                            </div>
                            <div className="ml-4 text-right">
                              <div className="text-sm font-medium text-gray-700">
                                {Math.round(rec.impact_score)}%
                              </div>
                              <div className="text-xs text-gray-500 capitalize">
                                {rec.effort_level}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'details' && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-gray-900">
              Detailed Analysis
            </h3>

            {/* Analysis Metadata */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                Analysis Summary
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg p-4 border">
                  <div className="text-2xl font-bold text-blue-600">
                    {analysis_metadata?.component_stats?.skills_analysis?.technical_skills_count || 0}
                  </div>
                  <div className="text-sm text-gray-600">Technical Skills Found</div>
                </div>
                <div className="bg-white rounded-lg p-4 border">
                  <div className="text-2xl font-bold text-green-600">
                    {analysis_metadata?.component_stats?.keyword_analysis?.match_percentage || 0}%
                  </div>
                  <div className="text-sm text-gray-600">Keyword Match</div>
                </div>
                <div className="bg-white rounded-lg p-4 border">
                  <div className="text-2xl font-bold text-purple-600">
                    {recommendations?.total_impact_score || 0}
                  </div>
                  <div className="text-sm text-gray-600">Total Impact Score</div>
                </div>
              </div>
            </div>

            {/* Processing Details */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <ClockIcon className="h-5 w-5 mr-2 text-gray-500" />
                Processing Details
              </h4>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">AI Enhanced:</span>
                  <span className="font-medium">
                    {analysis_metadata?.ai_enhanced ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Processing Time:</span>
                  <span className="font-medium">{Math.round(processing_time_ms)}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Algorithm Version:</span>
                  <span className="font-medium">
                    {analysis_metadata?.scoring_algorithm_version || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Confidence Level:</span>
                  <span className="font-medium">
                    {Math.round((compatibility_score.confidence_level || 0) * 100)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Improvement Suggestions */}
            {compatibility_score.improvement_suggestions?.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h4 className="text-lg font-medium text-blue-800 mb-4">
                  Improvement Suggestions
                </h4>
                <ul className="space-y-2">
                  {compatibility_score.improvement_suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="flex-shrink-0 w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                        <span className="text-xs font-medium text-blue-600">{index + 1}</span>
                      </div>
                      <span className="text-sm text-blue-700">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsDashboard;