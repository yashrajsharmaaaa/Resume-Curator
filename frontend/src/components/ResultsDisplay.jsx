/**
 * ResultsDisplay Component - Monochromatic Design
 * 
 * Clean results layout with large compatibility score display.
 * Simple list components for missing skills and recommendations.
 * Uses typography hierarchy instead of colors for visual emphasis.
 * 
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
 */

const ResultsDisplay = ({
  compatibilityScore,
  strengths = [],
  areasForImprovement = [],
  missingSkills = [],
  topRecommendations = [],
  overallAssessment = ""
}) => {
  // Limit items to maximum 5 for better display
  const limitedStrengths = strengths.slice(0, 5);
  const limitedImprovements = areasForImprovement.slice(0, 5);
  const limitedMissingSkills = missingSkills.slice(0, 5);
  const limitedRecommendations = topRecommendations.slice(0, 5);

  return (
    <div className="space-y-xl">
      {/* Compatibility Score */}
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-md text-gray-800">
          Job Match Score
        </h2>
        <div className="text-3xl font-bold text-gray-800">
          {Math.round(compatibilityScore)}%
        </div>
        {overallAssessment && (
          <p className="text-sm text-gray-600 mt-sm max-w-md mx-auto">
            {overallAssessment}
          </p>
        )}
      </div>

      {/* Resume Strengths */}
      {limitedStrengths.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-md text-gray-800">
            Resume Strengths
          </h3>
          <ul className="space-y-sm">
            {limitedStrengths.map((strength, index) => (
              <li key={index} className="text-base text-gray-700">
                ✓ {strength}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Areas for Improvement */}
      {limitedImprovements.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-md text-gray-800">
            Areas for Improvement
          </h3>
          <ul className="space-y-sm">
            {limitedImprovements.map((improvement, index) => (
              <li key={index} className="text-base text-gray-700">
                • {improvement}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Missing Skills Gap */}
      {limitedMissingSkills.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-md text-gray-800">
            Skills Gap Analysis
          </h3>
          <ul className="space-y-sm">
            {limitedMissingSkills.map((skill, index) => (
              <li key={index} className="text-base text-gray-700">
                ⚠ {skill}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Improvement Suggestions */}
      {limitedRecommendations.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-md text-gray-800">
            Improvement Suggestions
          </h3>
          <ol className="space-y-sm">
            {limitedRecommendations.map((recommendation, index) => (
              <li key={index} className="text-base text-gray-700">
                {index + 1}. {typeof recommendation === 'string'
                  ? recommendation
                  : recommendation.title || recommendation.description || 'Recommendation'
                }
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;