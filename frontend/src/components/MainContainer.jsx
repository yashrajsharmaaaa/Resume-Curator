/**
 * MainContainer Layout Component - Monochromatic Design
 * 
 * Centered single-column layout with responsive padding.
 * Max-width constraints for optimal reading line length.
 * Responsive breakpoints for mobile, tablet, and desktop.
 * 
 * Requirements: 8.1, 8.2, 8.4
 */

const MainContainer = ({ 
  children, 
  maxWidth = 'sm' 
}) => {
  const maxWidthClasses = {
    sm: 'max-w-2xl',   // 640px - optimal for reading
    md: 'max-w-4xl',   // 896px - for wider content
    lg: 'max-w-6xl'    // 1152px - for full layouts
  };

  return (
    <div className={`
      container 
      ${maxWidthClasses[maxWidth] || maxWidthClasses.sm}
      mx-auto
    `}>
      {children}
    </div>
  );
};

export default MainContainer;