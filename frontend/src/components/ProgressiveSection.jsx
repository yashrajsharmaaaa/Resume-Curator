/**
 * ProgressiveSection Component - Monochromatic Design
 * 
 * Show/hide functionality for workflow steps without animations.
 * Minimized state shows only essential information.
 * Instant state transitions without fade or slide effects.
 * 
 * Requirements: 2.2, 2.3, 7.3
 */

const ProgressiveSection = ({ 
  isVisible, 
  isMinimized = false, 
  children 
}) => {
  if (!isVisible) {
    return null;
  }

  return (
    <div className={`
      ${isMinimized ? 'opacity-60 space-y-sm' : 'space-y-md'}
    `}>
      {children}
    </div>
  );
};

export default ProgressiveSection;