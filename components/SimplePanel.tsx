import React from 'react';

interface SimplePanelProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
}

/**
 * A simple panel component that uses the basic theme
 * This replaces the more complex GlassmorphicContainer
 */
export function SimplePanel({ 
  children, 
  className = '', 
  hoverable = false
}: SimplePanelProps) {
  const baseClasses = 'panel';
  const hoverClasses = hoverable ? 'transition-all duration-200 hover:bg-opacity-60' : '';
  const allClasses = `${baseClasses} ${hoverClasses} ${className}`;
  
  return (
    <div className={allClasses}>
      {children}
    </div>
  );
} 