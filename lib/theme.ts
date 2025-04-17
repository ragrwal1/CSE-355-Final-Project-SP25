/**
 * Simple theme configuration
 * This is the ONLY place to edit colors for the entire application
 */

// Base colors
const colors = {
  background: '#1e1e1e',
  surface: 'rgba(46, 46, 46, 0.7)',
  element: 'rgba(58, 58, 58, 0.7)',
  textPrimary: '#f7f7f7',
  textSecondary: '#a3a3a3',
  border: 'rgba(255, 255, 255, 0.1)',
};

// Core styling
const styling = {
  blur: '12px',
  radius: '12px',
  shadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
};

// Export CSS variables for direct application
export const cssVariables = `
  :root {
    --color-background: ${colors.background};
    --color-surface: ${colors.surface};
    --color-element: ${colors.element};
    --color-text-primary: ${colors.textPrimary};
    --color-text-secondary: ${colors.textSecondary};
    --color-border: ${colors.border};
    
    --style-blur: ${styling.blur};
    --style-radius: ${styling.radius};
    --style-shadow: ${styling.shadow};
  }
`;

// Simple function to apply theme
export function applyTheme() {
  if (typeof document === 'undefined') return;
  
  const style = document.createElement('style');
  style.textContent = cssVariables;
  document.head.appendChild(style);
} 