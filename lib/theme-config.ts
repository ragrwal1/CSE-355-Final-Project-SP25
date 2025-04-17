/**
 * Glassmorphic UI Theme Configuration
 * This file contains all the configuration for the glassmorphic UI theme
 */

export const themeConfig = {
  // Base colors
  colors: {
    // Dark gray base theme (Apple-like)
    base: {
      dark: "#1e1e1e",        // Lighter dark background (was #0d0d0d)
      medium: "#2c2c2e",      // Apple dark mode card background
      light: "#3a3a3c",       // Apple secondary background
    },
    // Accent colors
    accent: {
      primary: "#a3a3a3",     // Apple gray
      secondary: "#7a7a7a",   // Apple darker gray (lighter than before)
    },
    // Text colors
    text: {
      primary: "#f7f7f7",     // Apple white text
      secondary: "#ebebf5",   // Apple secondary text (with opacity 0.6)
      muted: "#a3a3a3",       // Apple muted text
    }
  },
  
  // Glassmorphic effect values (Apple-style)
  glass: {
    background: "rgba(44, 44, 46, 0.35)",
    border: "1px solid rgba(255, 255, 255, 0.1)",
    backdropFilter: "blur(20px)",
    boxShadow: "0 4px 12px 0 rgba(0, 0, 0, 0.15)",
    borderRadius: "16px",
    hover: {
      background: "rgba(58, 58, 60, 0.4)",
    },
    active: {
      background: "rgba(70, 70, 72, 0.45)",
    }
  },
  
  // Button styles
  button: {
    padding: "0.75rem 1.5rem",
    borderRadius: "12px",
    transition: "all 0.2s ease",
    hitbox: {
      padding: "0.5rem",      // Extra padding for hit area
    }
  },
  
  // Card styles
  card: {
    padding: "1.5rem",
    margin: "1rem 0",
    borderRadius: "16px",
  },
  
  // Input styles
  input: {
    background: "rgba(44, 44, 46, 0.35)",
    border: "1px solid rgba(255, 255, 255, 0.1)",
    borderRadius: "12px",
    padding: "0.75rem 1rem",
  }
};

// CSS variables for the glassmorphic theme (Apple-style)
export const glassmorphicCssVariables = {
  light: {
    // We'll keep light mode dark as well for consistency
    background: "240 3% 12%",
    foreground: "0 0% 100%",
    card: "240 3% 16%",
    cardForeground: "0 0% 100%",
    popover: "240 3% 16%",
    popoverForeground: "0 0% 100%",
    primary: "0 0% 90%",
    primaryForeground: "0 0% 12%",
    secondary: "240 3% 20%",
    secondaryForeground: "0 0% 100%",
    muted: "240 3% 20%",
    mutedForeground: "0 0% 70%",
    accent: "240 3% 20%",
    accentForeground: "0 0% 100%",
    border: "240 3% 20%",
    input: "240 3% 16%",
    ring: "240 5% 70%",
  },
  dark: {
    background: "240 3% 12%",
    foreground: "0 0% 100%",
    card: "240 3% 16%",
    cardForeground: "0 0% 100%",
    popover: "240 3% 16%",
    popoverForeground: "0 0% 100%",
    primary: "0 0% 90%",
    primaryForeground: "0 0% 12%",
    secondary: "240 3% 20%",
    secondaryForeground: "0 0% 100%",
    muted: "240 3% 20%",
    mutedForeground: "0 0% 70%",
    accent: "240 3% 20%",
    accentForeground: "0 0% 100%",
    border: "240 3% 20%",
    input: "240 3% 16%",
    ring: "240 5% 70%",
  }
};

// CSS class for Apple-style glassmorphic effect
export const glassmorphicClass = `
  bg-opacity-35 
  backdrop-blur-2xl 
  border border-white/10
  shadow-lg
  rounded-2xl
`;

// CSS class for button with extended hitbox
export const buttonHitboxClass = `
  relative
  before:absolute 
  before:inset-0 
  before:-m-2
  before:content-['']
`; 