import React from 'react';
import { Card, Button } from '../ui';

const ResumeCard = ({ resume, onClick }) => {
  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadgeColor = (score) => {
    if (score >= 90) return 'bg-green-100 text-green-800';
    if (score >= 70) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Card className="hover:shadow-lg transition-shadow duration-200 cursor-pointer" onClick={onClick}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
            </svg>
            <h3 className="font-semibold text-gray-900 truncate" title={resume.fileName}>
              {resume.fileName}
            </h3>
          </div>
          
          <div className="space-y-1 text-sm text-gray-500">
            <p>Uploaded: {formatDate(resume.uploadDate)}</p>
            <p>Size: {formatFileSize(resume.fileSize)}</p>
          </div>
        </div>

        {resume.score && (
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreBadgeColor(resume.score)}`}>
            {resume.score}%
          </div>
        )}
      </div>

      {resume.analysis && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Analysis Score</span>
            <span className={`text-lg font-bold ${getScoreColor(resume.score)}`}>
              {resume.score}%
            </span>
          </div>
          
          {resume.analysis.keySkills && resume.analysis.keySkills.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-600 mb-1">Key Skills Found:</p>
              <div className="flex flex-wrap gap-1">
                {resume.analysis.keySkills.slice(0, 3).map((skill, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                    {skill}
                  </span>
                ))}
                {resume.analysis.keySkills.length > 3 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                    +{resume.analysis.keySkills.length - 3} more
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="flex space-x-2">
        <Button 
          variant="primary" 
          size="sm" 
          className="flex-1"
          onClick={(e) => {
            e.stopPropagation();
            onClick?.(resume);
          }}
        >
          View Analysis
        </Button>
        <Button 
          variant="secondary" 
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            // Handle download or other actions
          }}
        >
          Download
        </Button>
      </div>
    </Card>
  );
};

export default ResumeCard;