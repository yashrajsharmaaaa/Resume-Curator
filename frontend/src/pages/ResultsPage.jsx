import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import { Button } from '../components/ui';
import { ResultsDisplay } from '../components/display';
import { useApp } from '../context/AppContext';

const ResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentResume } = useApp();

  // Get resume from navigation state or context
  const resume = location.state?.resume || currentResume;

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const handleUploadNew = () => {
    navigate('/');
  };

  return (
    <div>
      <PageHeader 
        title="Analysis Results" 
        subtitle={resume ? `Analysis for ${resume.fileName}` : "Detailed analysis of your resume"}
      >
        <div className="flex space-x-3">
          <Button variant="secondary" onClick={handleBackToDashboard}>
            Back to Dashboard
          </Button>
          <Button variant="primary" onClick={handleUploadNew}>
            Upload New Resume
          </Button>
        </div>
      </PageHeader>
      
      <div className="max-w-4xl mx-auto">
        <ResultsDisplay resume={resume} />
      </div>
    </div>
  );
};

export default ResultsPage;