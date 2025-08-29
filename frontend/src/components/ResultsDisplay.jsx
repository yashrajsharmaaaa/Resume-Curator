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
  missingSkills = [], 
  topRecommendations = [] 
}) => {
  // Limit recommendations to maximum 5 items
  const limitedRecommendations = topRecommendations.slice(0, 5);

  return (
    <div className="space-y-xl">
      {/* Compatibility Score */}
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-md text-gray-800">
          Compatibility Score
        </h2>
        <div className="text-3xl font-bold text-gray-800">
          {Math.round(compatibilityScore)}%
        </div>
      </div>

      {/* Missing Skills */}
      {missingSkills.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-md text-gray-800">
            Missing Skills
          </h3>
          <ul className="space-y-sm">
            {missingSkills.map((skill, index) => (
              <li key={index} className="text-base text-gray-700">
                • {skill}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Top Recommendations */}
      {limitedRecommendations.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-md text-gray-800">
            Top Recommendations
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