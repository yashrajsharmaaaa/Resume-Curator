import React from 'react';
import { Card } from '../ui';

const ResultsDisplay = ({ resume }) => {
  if (!resume) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="text-gray-500">No resume data available</p>
        </div>
      </Card>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score) => {
    if (score >= 90) return 'bg-green-50 border-green-200';
    if (score >= 70) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const mockAnalysis = {
    score: resume.score || 85,
    strengths: [
      'Strong technical skills in React and JavaScript',
      'Good project management experience',
      'Clear and well-structured resume format'
    ],
    improvements: [
      'Add more quantifiable achievements',
      'Include relevant certifications',
      'Expand on leadership experience'
    ],
    missingSkills: [
      'TypeScript',
      'AWS Cloud Services',
      'Agile/Scrum methodology'
    ],
    recommendations: [
      'Consider adding a professional summary section',
      'Include links to portfolio projects',
      'Add relevant keywords for ATS optimization'
    ]
  };

  return (
    <div className="space-y-6">
      {/* Score Overview */}
      <Card className={`border-2 ${getScoreBackground(mockAnalysis.score)}`}>
        <div className="text-center">
          <div className={`text-4xl font-bold mb-2 ${getScoreColor(mockAnalysis.score)}`}>
            {mockAnalysis.score}%
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Resume Analysis Score
          </h2>
          <p className="text-gray-600">
            {mockAnalysis.score >= 90 ? 'Excellent resume!' : 
             mockAnalysis.score >= 70 ? 'Good resume with room for improvement' : 
             'Resume needs significant improvements'}
          </p>
        </div>
      </Card>

      {/* Strengths */}
      <Card>
        <div className="flex items-center mb-4">
          <svg className="w-6 h-6 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900">Strengths</h3>
        </div>
        <ul className="space-y-2">
          {mockAnalysis.strengths.map((strength, index) => (
            <li key={index} className="flex items-start">
              <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
              <span className="text-gray-700">{strength}</span>
            </li>
          ))}
        </ul>
      </Card>

      {/* Areas for Improvement */}
      <Card>
        <div className="flex items-center mb-4">
          <svg className="w-6 h-6 text-yellow-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900">Areas for Improvement</h3>
        </div>
        <ul className="space-y-2">
          {mockAnalysis.improvements.map((improvement, index) => (
            <li key={index} className="flex items-start">
              <span className="w-2 h-2 bg-yellow-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
              <span className="text-gray-700">{improvement}</span>
            </li>
          ))}
        </ul>
      </Card>

      {/* Missing Skills */}
      <Card>
        <div className="flex items-center mb-4">
          <svg className="w-6 h-6 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900">Missing Skills</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {mockAnalysis.missingSkills.map((skill, index) => (
            <span key={index} className="px-3 py-1 bg-red-100 text-red-800 text-sm rounded-full">
              {skill}
            </span>
          ))}
        </div>
      </Card>

      {/* Recommendations */}
      <Card>
        <div className="flex items-center mb-4">
          <svg className="w-6 h-6 text-blue-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
        </div>
        <ul className="space-y-2">
          {mockAnalysis.recommendations.map((recommendation, index) => (
            <li key={index} className="flex items-start">
              <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
              <span className="text-gray-700">{recommendation}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
};

export default ResultsDisplay;