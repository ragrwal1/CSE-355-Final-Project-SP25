'use client'

import React, { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { GlassmorphicContainerProps } from '@/components/ui/glassmorphic-container'
import { AppleUI, AppleSection } from '@/components/ui-wrapper'

export interface UseAppleUIOptions extends Partial<GlassmorphicContainerProps> {
  wrapChildren?: boolean
}

/**
 * Custom hook for applying Apple-style glassmorphic UI
 * 
 * This hook makes it easy to apply the Apple-style UI to any component
 * by providing utility functions and styled components.
 */
export function useAppleUI() {
  // Function to apply glassmorphic styles to any content
  const applyGlassmorphic = (
    content: ReactNode, 
    options?: UseAppleUIOptions
  ) => {
    return (
      <AppleUI
        opacity={options?.opacity || "medium"}
        rounded={options?.rounded || "medium"}
        hoverable={options?.hoverable}
        padding={options?.padding || "medium"}
        elevation={options?.elevation || "medium"}
        className={options?.className}
        wrapChildren={options?.wrapChildren}
      >
        {content}
      </AppleUI>
    )
  }
  
  // Function to create a section with a title
  const createSection = (
    title: string,
    content: ReactNode,
    options?: UseAppleUIOptions
  ) => {
    return (
      <AppleSection
        title={title}
        opacity={options?.opacity || "medium"}
        rounded={options?.rounded || "medium"}
        hoverable={options?.hoverable}
        padding={options?.padding || "medium"}
        elevation={options?.elevation || "medium"}
        className={options?.className}
      >
        {content}
      </AppleSection>
    )
  }
  
  // Predefined glassmorphic class combinations for common use cases
  const glassClasses = {
    // Base glassmorphic style
    base: 'glassmorphic bg-gradient-card',
    
    // Different opacity levels
    subtle: 'glassmorphic bg-gradient-card bg-opacity-25',
    medium: 'glassmorphic bg-gradient-card bg-opacity-35',
    strong: 'glassmorphic bg-gradient-card bg-opacity-45',
    
    // Interactive elements
    button: 'glassmorphic-button button-hitbox',
    input: 'glassmorphic-input',
    
    // Container types with different padding
    panel: 'glassmorphic bg-gradient-card p-5 rounded-2xl',
    card: 'glassmorphic bg-gradient-card p-4 rounded-2xl',
    dialog: 'glassmorphic bg-gradient-card p-6 rounded-2xl',
  }
  
  // Function to combine glassmorphic classes with custom classes
  const combineClasses = (baseType: keyof typeof glassClasses, customClasses?: string) => {
    return cn(glassClasses[baseType], customClasses)
  }
  
  return {
    applyGlassmorphic,
    createSection,
    glassClasses,
    combineClasses
  }
} 