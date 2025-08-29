// Icons removed for monochromatic design

const StepIndicator = ({ currentStep }) => {
  const steps = [
    { 
      id: 'upload', 
      name: 'Upload Resume', 
      icon: Upload,
      completed: currentStep !== 'upload' && currentStep !== 'dashboard'
    },
    { 
      id: 'job', 
      name: 'Job Description', 
      icon: FileText,
      completed: currentStep === 'results'
    },
    { 
      id: 'results', 
      name: 'Analysis Results', 
      icon: BarChart3,
      completed: false
    }
  ];

  const getCurrentStepIndex = () => {
    switch (currentStep) {
      case 'upload':
      case 'dashboard':
        return 0;
      case 'job':
        return 1;
      case 'results':
        return 2;
      default:
        return 0;
    }
  };

  const currentStepIndex = getCurrentStepIndex();

  return (
    <div className="flex items-center justify-center">
      <div className="flex items-center space-x-8">
        {steps.map((step, index) => {
          const isActive = index === currentStepIndex;
          const isCompleted = step.completed || index < currentStepIndex;
          const StepIcon = step.icon;

          return (
            <div key={step.id} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 ${
                    isCompleted
                      ? 'text-white'
                      : isActive
                      ? 'text-white'
                      : 'text-gray-400'
                  }`}
                  style={{
                    backgroundColor: isCompleted
                      ? '#10B981'
                      : isActive
                      ? '#14121E'
                      : '#F3F4F6'
                  }}
                >
                  {isCompleted ? (
                    <Check className="w-6 h-6" />
                  ) : (
                    <StepIcon className="w-6 h-6" />
                  )}
                </div>
                <span
                  className={`text-sm font-medium mt-2 transition-colors duration-300 ${
                    isActive ? 'font-urbanist' : 'font-gilroy'
                  }`}
                  style={{
                    color: isCompleted || isActive ? '#14121E' : '#6B7280'
                  }}
                >
                  {step.name}
                </span>
              </div>
              
              {index < steps.length - 1 && (
                <div
                  className="w-16 h-0.5 mx-4 transition-colors duration-300"
                  style={{
                    backgroundColor: index < currentStepIndex ? '#10B981' : '#E5E7EB'
                  }}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default StepIndicator;