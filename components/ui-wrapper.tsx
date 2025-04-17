'use client'

import React, { ReactElement, cloneElement, ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { GlassmorphicContainer, GlassmorphicContainerProps } from './ui/glassmorphic-container'

// Function to apply glassmorphic styles to any component
export function withGlassmorphic<P extends React.ComponentProps<any>>(
  Component: React.ComponentType<P>,
  glassmorphicProps?: Partial<GlassmorphicContainerProps>
): React.FC<P & Partial<GlassmorphicContainerProps>> {
  const WithGlassmorphic = (props: P & Partial<GlassmorphicContainerProps>) => {
    const { className, ...componentProps } = props as any

    // Extract glassmorphic specific props
    const {
      hoverable,
      padding,
      elevation,
      rounded,
      opacity,
      ...restProps
    } = componentProps

    return (
      <GlassmorphicContainer
        hoverable={hoverable ?? glassmorphicProps?.hoverable}
        padding={padding ?? glassmorphicProps?.padding}
        elevation={elevation ?? glassmorphicProps?.elevation}
        rounded={rounded ?? glassmorphicProps?.rounded}
        opacity={opacity ?? glassmorphicProps?.opacity}
        className={className}
      >
        <Component {...restProps} />
      </GlassmorphicContainer>
    )
  }

  WithGlassmorphic.displayName = `withGlassmorphic(${Component.displayName || Component.name || 'Component'})`
  return WithGlassmorphic
}

// Component to automatically apply Apple-style glassmorphic UI to children
export interface AppleUIProps extends Partial<GlassmorphicContainerProps> {
  children: ReactNode
  component?: 'div' | 'section' | 'article' | 'aside' | 'main' | 'nav' | 'container'
  wrapChildren?: boolean // If true, wraps each child individually
}

export function AppleUI({
  children,
  component = 'div',
  wrapChildren = false,
  className,
  ...glassmorphicProps
}: AppleUIProps) {
  // If we're not wrapping individual children, just wrap them all
  if (!wrapChildren) {
    return (
      <GlassmorphicContainer className={className} {...glassmorphicProps}>
        {children}
      </GlassmorphicContainer>
    )
  }

  // Otherwise, wrap each individual child
  return React.createElement(
    component,
    { className },
    React.Children.map(children, (child) => {
      if (React.isValidElement<{ className?: string }>(child)) {
        return (
          <GlassmorphicContainer {...glassmorphicProps} className={cn('mb-4', child.props.className)}>
            {child}
          </GlassmorphicContainer>
        )
      }
      return child
    })
  )
}

// Component that adds Apple-style floating divider
export function AppleDivider({ className }: { className?: string }) {
  return <div className={cn('apple-divider my-4', className)} />
}

// Component for creating Apple-style sections with proper spacing
export function AppleSection({ 
  children, 
  title, 
  className,
  ...glassmorphicProps 
}: { 
  children: ReactNode
  title?: string 
  className?: string
} & Partial<GlassmorphicContainerProps>) {
  return (
    <section className={cn('mb-6', className)}>
      {title && <h2 className="text-xl font-medium mb-3">{title}</h2>}
      <GlassmorphicContainer {...glassmorphicProps}>
        {children}
      </GlassmorphicContainer>
    </section>
  )
} 