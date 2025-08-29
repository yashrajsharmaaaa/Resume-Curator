/**
 * SkillsGapVisualization Component for Resume Curator
 * 
 * Interactive charts for skills gap analysis and compatibility visualization
 * as required by Requirements 3.3, 4.4, 4.5, 7.1.
 */

import { useState, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadialBarChart,
  RadialBar,
  Legend
} from 'recharts';
import { 
  ChartBarIcon,
  ChartPieIcon,
  AdjustmentsHorizontalIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

const SkillsGapVisualization = ({
  compatibilityScore,
  skillsAnalysis,
  skillCategorization,
  className = ''
}) => {
  const [activeChart, setActiveChart] = useState('compatibility');
  const [showLegend, setShowLegend] = useState(true);

  // Color schemes
  const colors = {
    primary: '#3B82F6',
    secondary: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    purple: '#8B5CF6',
    indigo: '#6366F1',
    pink: '#EC4899',
    teal: '#14B8A6'
  };

  // Chart configurations
  const chartTypes = [
    { id: 'compatibility', label: 'Compatibility Score', icon: ChartBarIcon },
    { id: 'skills', label: 'Skills Breakdown', icon: ChartPieIcon },
    { id: 'categories', label: 'Skill Categories', icon: AdjustmentsHorizontalIcon }
  ];

  // Prepare compatibility score data
  const compatibilityData = useMemo(() => {
    if (!compatibilityScore?.component_scores) return [];
    
    return Object.entries(compatibilityScore.component_scores).map(([key, value]) => ({
      name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      score: Math.round(value),
      fill: value >= 80 ? colors.secondary : 
            value >= 60 ? colors.primary : 
            value >= 40 ? colors.warning : colors.danger
    }));
  }, [compatibilityScore, colors.danger, colors.primary, colors.secondary, colors.warning]);

  // Prepare skills breakdown data
  const skillsData = useMemo(() => {
    if (!skillsAnalysis) return [];
    
    return [
      {
        name: 'Technical Skills',
        value: skillsAnalysis.technical_skills?.length || 0,
        fill: colors.primary
      },
      {
        name: 'Soft Skills',
        value: skillsAnalysis.soft_skills?.length || 0,
        fill: colors.secondary
      },
      {
        name: 'Tools & Software',
        value: skillsAnalysis.tools_and_software?.length || 0,
        fill: colors.purple
      },
      {
        name: 'Certifications',
        value: skillsAnalysis.certifications?.length || 0,
        fill: colors.warning
      }
    ].filter(item => item.value > 0);
  }, [skillsAnalysis, colors.primary, colors.purple, colors.secondary, colors.warning]);

  // Prepare skill categories data
  const categoriesData = useMemo(() => {
    if (!skillCategorization) return [];
    
    const categories = [
      { key: 'technical_skills', label: 'Technical', color: colors.primary },
      { key: 'soft_skills', label: 'Soft Skills', color: colors.secondary },
      { key: 'domain_skills', label: 'Domain', color: colors.purple },
      { key: 'tools_and_platforms', label: 'Tools', color: colors.indigo },
      { key: 'certifications', label: 'Certifications', color: colors.warning },
      { key: 'languages', label: 'Languages', color: colors.pink },
      { key: 'methodologies', label: 'Methodologies', color: colors.teal }
    ];

    return categories.map(cat => ({
      name: cat.label,
      value: skillCategorization[cat.key]?.skills?.length || 0,
      confidence: Math.round((skillCategorization[cat.key]?.confidence_scores ? 
        Object.values(skillCategorization[cat.key].confidence_scores).reduce((a, b) => a + b, 0) / 
        Object.values(skillCategorization[cat.key].confidence_scores).length : 0) * 100),
      fill: cat.color
    })).filter(item => item.value > 0);
  }, [skillCategorization, colors.indigo, colors.pink, colors.primary, colors.purple, colors.secondary, colors.teal, colors.warning]);

  // Custom tooltip for compatibility chart
  const CompatibilityTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{label}</p>
          <p className="text-sm text-gray-600">
            Score: <span className="font-medium" style={{ color: data.payload.fill }}>
              {data.value}%
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for pie charts
  const PieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">
            Count: <span className="font-medium" style={{ color: data.payload.fill }}>
              {data.value}
            </span>
            {data.payload.confidence && (
              <>
                <br />
                Confidence: <span className="font-medium">
                  {data.payload.confidence}%
                </span>
              </>
            )}
          </p>
        </div>
      );
    }
    return null;
  };

  // Compatibility gauge data
  const gaugeData = useMemo(() => {
    if (!compatibilityScore?.overall_score) return [];
    
    const score = compatibilityScore.overall_score;
    return [
      {
        name: 'Score',
        value: score,
        fill: score >= 80 ? colors.secondary : 
              score >= 60 ? colors.primary : 
              score >= 40 ? colors.warning : colors.danger
      }
    ];
  }, [compatibilityScore, colors.danger, colors.primary, colors.secondary, colors.warning]);

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Skills Gap Analysis
          </h3>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowLegend(!showLegend)}
              className="flex items-center space-x-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              {showLegend ? (
                <EyeSlashIcon className="h-4 w-4" />
              ) : (
                <EyeIcon className="h-4 w-4" />
              )}
              <span>{showLegend ? 'Hide' : 'Show'} Legend</span>
            </button>
          </div>
        </div>
        
        {/* Chart type selector */}
        <div className="flex space-x-1 mt-4 bg-gray-100 rounded-lg p-1">
          {chartTypes.map((chart) => {
            const ChartIcon = chart.icon;
            return (
              <button
                key={chart.id}
                onClick={() => setActiveChart(chart.id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeChart === chart.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <ChartIcon className="h-4 w-4" />
                <span>{chart.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Chart Content */}
      <div className="p-6">
        {activeChart === 'compatibility' && (
          <div className="space-y-6">
            {/* Overall Score Gauge */}
            <div className="text-center">
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                Overall Compatibility Score
              </h4>
              <div className="flex justify-center">
                <div className="relative w-64 h-32">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart
                      cx="50%"
                      cy="100%"
                      innerRadius="60%"
                      outerRadius="90%"
                      startAngle={180}
                      endAngle={0}
                      data={gaugeData}
                    >
                      <RadialBar
                        dataKey="value"
                        cornerRadius={10}
                        fill={gaugeData[0]?.fill}
                      />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex items-end justify-center pb-4">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-gray-900">
                        {Math.round(compatibilityScore?.overall_score || 0)}%
                      </div>
                      <div className="text-sm text-gray-500">
                        Compatibility
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Component Scores Bar Chart */}
            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                Score Breakdown by Component
              </h4>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={compatibilityData}
                    margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="name" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      fontSize={12}
                    />
                    <YAxis 
                      domain={[0, 100]}
                      fontSize={12}
                    />
                    <Tooltip content={<CompatibilityTooltip />} />
                    <Bar 
                      dataKey="score" 
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeChart === 'skills' && (
          <div className="space-y-6">
            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                Skills Distribution
              </h4>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={skillsData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      dataKey="value"
                      label={({ name, value, percent }) => 
                        `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                      }
                    >
                      {skillsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip content={<PieTooltip />} />
                    {showLegend && <Legend />}
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Skills Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {skillsData.map((skill, index) => (
                <div key={index} className="text-center p-4 bg-gray-50 rounded-lg">
                  <div 
                    className="text-2xl font-bold mb-1"
                    style={{ color: skill.fill }}
                  >
                    {skill.value}
                  </div>
                  <div className="text-sm text-gray-600">{skill.name}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeChart === 'categories' && (
          <div className="space-y-6">
            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                Skill Categories with Confidence Levels
              </h4>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={categoriesData}
                    margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="name" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      fontSize={12}
                    />
                    <YAxis fontSize={12} />
                    <Tooltip content={<PieTooltip />} />
                    <Bar 
                      dataKey="value" 
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Categories Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categoriesData.map((category, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h5 className="font-medium text-gray-900">{category.name}</h5>
                    <div 
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: category.fill }}
                    />
                  </div>
                  <div className="text-2xl font-bold text-gray-900 mb-1">
                    {category.value}
                  </div>
                  <div className="text-sm text-gray-500">
                    Skills identified
                  </div>
                  {category.confidence > 0 && (
                    <div className="mt-2">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>Confidence</span>
                        <span>{category.confidence}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1">
                        <div
                          className="h-1 rounded-full"
                          style={{ 
                            width: `${category.confidence}%`,
                            backgroundColor: category.fill
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No data message */}
        {((activeChart === 'compatibility' && compatibilityData.length === 0) ||
          (activeChart === 'skills' && skillsData.length === 0) ||
          (activeChart === 'categories' && categoriesData.length === 0)) && (
          <div className="text-center py-12">
            <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              No Data Available
            </h4>
            <p className="text-gray-500">
              Complete the analysis to see visualization data.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SkillsGapVisualization;