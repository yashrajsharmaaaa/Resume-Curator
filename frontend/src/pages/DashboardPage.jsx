import React from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import { Button } from '../components/ui';
import { ResumeCard, StatCard } from '../components/display';
import { useApp } from '../context/AppContext';

const DashboardPage = () => {
  const navigate = useNavigate();
  const { resumes } = useApp();

  const handleResumeClick = (resume) => {
    navigate('/results', { state: { resume } });
  };

  const handleUploadNew = () => {
    navigate('/');
  };
  const totalResumes = resumes.length;
  const averageScore = totalResumes > 0 
    ? Math.round(resumes.reduce((sum, resume) => sum + (resume.score || 0), 0) / totalResumes)
    : null;
  
  const highScoreResumes = resumes.filter(resume => (resume.score || 0) >= 90).length;
  const averageScoreDisplay = averageScore !== null ? `${averageScore}%` : 'No data';
  const averageScoreSubtitle = totalResumes > 0 ? 'Across all resumes' : 'Upload resumes to see average';
  const totalResumesSubtitle = totalResumes > 0 ? 'Uploaded resumes' : 'No resumes uploaded yet';
  const highScoreSubtitle = totalResumes > 0 ? '90% or above' : 'Upload resumes to track high scores';
  
  const pageSubtitle = totalResumes > 0 
    ? 'Overview of your uploaded resumes' 
    : 'Get started by uploading your first resume for analysis';

  return (
    <div className="space-y-8">
      <PageHeader 
        title="Dashboard" 
        subtitle={pageSubtitle}
      >
        <Button variant="primary" onClick={handleUploadNew}>
          Upload New Resume
        </Button>
      </PageHeader>


      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Total Resumes"
          value={totalResumes}
          subtitle={totalResumesSubtitle}
          color="blue"
          icon={
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
            </svg>
          }
        />
        
        <StatCard
          title="Average Score"
          value={averageScoreDisplay}
          subtitle={averageScoreSubtitle}
          color="green"
          icon={
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
            </svg>
          }
        />
        
        <StatCard
          title="High Scores"
          value={highScoreResumes}
          subtitle={highScoreSubtitle}
          color="purple"
          icon={
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          }
        />
      </div>
      
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Your Resumes</h2>
        
        {resumes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resumes.map((resume) => (
              <ResumeCard 
                key={resume.id} 
                resume={resume} 
                onClick={() => handleResumeClick(resume)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-16 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border-2 border-dashed border-gray-300">
            <div className="mx-auto max-w-md">
              <svg className="mx-auto h-16 w-16 text-gray-400 mb-6" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Ready to analyze your resume?</h3>
              <p className="text-gray-600 mb-2">Upload your resume to get instant AI-powered analysis and insights.</p>
              <p className="text-sm text-gray-500 mb-6">
                Get detailed feedback on skills, formatting, and suggestions for improvement.
              </p>
              <div className="space-y-3">
                <Button variant="primary" onClick={handleUploadNew} className="w-full sm:w-auto">
                  Upload Your First Resume
                </Button>
                <p className="text-xs text-gray-400">
                  Supports PDF and DOCX files up to 10MB
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;