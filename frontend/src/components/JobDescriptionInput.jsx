/**
 * JobDescriptionInput Component for Resume Curator
 * 
 * Provides text area with character count, validation, and responsive design
 * as required by Requirements 2.1, 2.2, 2.3, 2.4, 7.1.
 */

import { useState, useCallback, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
// Icons removed for monochromatic design

const JobDescriptionInput = ({ 
  value = '', 
  onChange, 
  isValid = false, 
  error = null, 
  onSubmit,
  className = '' 
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const [wordCount, setWordCount] = useState(0);

  useEffect(() => {
    setCharCount(value.length);
    setWordCount(value.trim() ? value.trim().split(/\s+/).length : 0);
  }, [value]);

  const handleChange = useCallback((e) => {
    const newValue = e.target.value;
    onChange(newValue);
  }, [onChange]);

  const handleFocus = () => setIsFocused(true);
  const handleBlur = () => setIsFocused(false);

  const getValidationStatus = () => {
    if (charCount === 0) return 'empty';
    if (charCount < 50) return 'too-short';
    if (charCount > 5000) return 'too-long';
    if (isValid) return 'valid';
    return 'invalid';
  };

  const getStatusColor = () => {
    const status = getValidationStatus();
    switch (status) {
      case 'valid': return 'text-green-600';
      case 'too-short': return 'text-yellow-600';
      case 'too-long': return 'text-red-600';
      case 'invalid': return 'text-red-600';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = () => {
    const status = getValidationStatus();
    switch (status) {
      case 'valid': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'too-short': return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'too-long': return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'invalid': return <AlertCircle className="w-5 h-5 text-red-600" />;
      default: return <FileText className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusMessage = () => {
    const status = getValidationStatus();
    switch (status) {
      case 'valid': return 'Job description is ready for analysis';
      case 'too-short': return `Add ${50 - charCount} more characters (minimum 50)`;
      case 'too-long': return `Remove ${charCount - 5000} characters (maximum 5000)`;
      case 'invalid': return error || 'Please provide a valid job description';
      default: return 'Enter the job description you want to analyze';
    }
  };

  const tips = [
    {
      icon: Target,
      title: 'Be Specific',
      description: 'Include specific technologies, tools, and requirements'
    },
    {
      icon: Lightbulb,
      title: 'Key Responsibilities',
      description: 'List main duties and responsibilities clearly'
    },
    {
      icon: TrendingUp,
      title: 'Experience Level',
      description: 'Mention required years of experience and seniority'
    },
    {
      icon: Sparkles,
      title: 'Preferred Skills',
      description: 'Include both required and preferred qualifications'
    }
  ];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <motion.div
          className="mx-auto w-20 h-20 mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Target className="w-10 h-10 text-white" />
        </motion.div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Job Description Analysis
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Paste or type the job description you want to analyze. Our AI will compare it with your resume and provide detailed insights.
        </p>
      </motion.div>

      {/* Main Input Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="dashboard-card p-6">
          <div className="mb-4">
            <label htmlFor="job-description" className="block text-sm font-semibold text-gray-900 mb-2">
              Job Description
            </label>
            
            <div className={`relative rounded-xl border-2 transition-all duration-300 ${
              isFocused 
                ? 'border-blue-500 shadow-glow-blue' 
                : isValid 
                  ? 'border-green-300' 
                  : error 
                    ? 'border-red-300' 
                    : 'border-gray-300'
            }`}>
              <textarea
                id="job-description"
                value={value}
                onChange={handleChange}
                onFocus={handleFocus}
                onBlur={handleBlur}
                placeholder="Paste the job description here... For example: We are looking for a Senior Software Engineer with 5+ years of experience in React, Node.js, and AWS. The ideal candidate should have strong problem-solving skills and experience with microservices architecture..."
                className="w-full h-64 p-4 text-gray-900 placeholder-gray-500 bg-transparent border-0 resize-none focus:outline-none focus:ring-0 text-sm leading-relaxed"
                disabled={false}
              />
              
              {/* Status indicator */}
              <div className="absolute top-4 right-4">
                {getStatusIcon()}
              </div>
            </div>
          </div>

          {/* Validation Status */}
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className={`flex items-center space-x-2 p-3 rounded-lg ${
                getValidationStatus() === 'valid' 
                  ? 'bg-green-50 border border-green-200' 
                  : getValidationStatus() === 'too-short'
                    ? 'bg-yellow-50 border border-yellow-200'
                    : 'bg-red-50 border border-red-200'
              }`}
            >
              {getStatusIcon()}
              <span className={`text-sm font-medium ${getStatusColor()}`}>
                {getStatusMessage()}
              </span>
            </motion.div>
          </AnimatePresence>

          {/* Character and Word Count */}
          <div className="flex items-center justify-between mt-4 text-sm text-gray-500">
            <div className="flex items-center space-x-4">
              <span>{charCount} characters</span>
              <span>•</span>
              <span>{wordCount} words</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4" />
              <span>Estimated analysis time: 2-3 minutes</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Tips Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="dashboard-card p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Lightbulb className="w-5 h-5 text-yellow-600 mr-2" />
          Tips for Better Analysis
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tips.map((tip, index) => (
            <motion.div
              key={tip.title}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                <tip.icon className="w-4 h-4 text-white" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-gray-900">{tip.title}</h4>
                <p className="text-sm text-gray-600 mt-1">{tip.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Example Job Description */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="dashboard-card p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <FileText className="w-5 h-5 text-blue-600 mr-2" />
          Example Job Description
        </h3>
        <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700 leading-relaxed">
          <p className="mb-3">
            <strong>Senior Software Engineer</strong>
          </p>
          <p className="mb-3">
            We are seeking a Senior Software Engineer to join our growing team. The ideal candidate will have 5+ years of experience in full-stack development with expertise in React, Node.js, and cloud technologies.
          </p>
          <p className="mb-3">
            <strong>Requirements:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1 mb-3">
            <li>5+ years of experience in software development</li>
            <li>Strong proficiency in JavaScript/TypeScript, React, and Node.js</li>
            <li>Experience with cloud platforms (AWS, Azure, or GCP)</li>
            <li>Knowledge of database design and SQL</li>
            <li>Experience with microservices architecture</li>
            <li>Strong problem-solving and communication skills</li>
          </ul>
          <p>
            <strong>Nice to have:</strong> Experience with Docker, Kubernetes, CI/CD pipelines, and agile methodologies.
          </p>
        </div>
      </motion.div>

      {/* Action Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex justify-center"
      >
        <motion.button
          onClick={onSubmit}
          disabled={!isValid || charCount === 0}
          className={`px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 ${
            isValid && charCount > 0
              ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg hover:shadow-xl hover:scale-105'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          }`}
          whileHover={isValid && charCount > 0 ? { scale: 1.05 } : {}}
          whileTap={isValid && charCount > 0 ? { scale: 0.95 } : {}}
        >
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5" />
            <span>Analyze Compatibility</span>
          </div>
        </motion.button>
      </motion.div>
    </div>
  );
};

export default JobDescriptionInput;