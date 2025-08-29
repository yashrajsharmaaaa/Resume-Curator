// Icons removed for monochromatic design

const QuickStats = ({ selectedFile, analysisResult }) => {
  if (!selectedFile && !analysisResult) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {/* File Status */}
      <div className="metric-card">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#FCF3FD' }}>
            <FileText className="w-5 h-5" style={{ color: '#14121E' }} />
          </div>
          <div>
            <p className="text-sm font-gilroy" style={{ color: '#6B7280' }}>Resume Status</p>
            <p className="text-lg font-semibold font-urbanist" style={{ color: '#14121E' }}>
              {selectedFile ? 'Uploaded' : 'Not uploaded'}
            </p>
          </div>
        </div>
      </div>

      {/* Processing Time */}
      <div className="metric-card">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#FFEFE2' }}>
            <Clock className="w-5 h-5" style={{ color: '#14121E' }} />
          </div>
          <div>
            <p className="text-sm font-gilroy" style={{ color: '#6B7280' }}>Processing Time</p>
            <p className="text-lg font-semibold font-urbanist" style={{ color: '#14121E' }}>
              {analysisResult ? '~2.3s' : 'Pending'}
            </p>
          </div>
        </div>
      </div>

      {/* Compatibility Score */}
      <div className="metric-card">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#FCF3FD' }}>
            <TrendingUp className="w-5 h-5" style={{ color: '#14121E' }} />
          </div>
          <div>
            <p className="text-sm font-gilroy" style={{ color: '#6B7280' }}>Compatibility</p>
            <p className="text-lg font-semibold font-urbanist" style={{ color: '#14121E' }}>
              {analysisResult ? `${Math.round(analysisResult.compatibility_score.overall_score)}%` : 'Not analyzed'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuickStats;