import * as React from "react"
import { cn } from "@/lib/utils"

interface GlassmorphicContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  className?: string
  hoverable?: boolean
  padding?: "none" | "small" | "medium" | "large"
  elevation?: "none" | "low" | "medium" | "high"
  rounded?: "none" | "small" | "medium" | "large" | "full"
  opacity?: "subtle" | "low" | "medium" | "high"
}

const GlassmorphicContainer = React.forwardRef<HTMLDivElement, GlassmorphicContainerProps>(
  ({ 
    children, 
    className, 
    hoverable = false,
    padding = "medium",
    elevation = "medium",
    rounded = "medium",
    opacity = "medium",
    ...props 
  }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "glassmorphic bg-gradient-card",
          // Padding variants
          padding === "none" && "p-0",
          padding === "small" && "p-3",
          padding === "medium" && "p-5",
          padding === "large" && "p-8",
          // Elevation variants
          elevation === "none" && "shadow-none",
          elevation === "low" && "shadow-sm",
          elevation === "medium" && "shadow-md",
          elevation === "high" && "shadow-xl",
          // Rounded variants
          rounded === "none" && "rounded-none",
          rounded === "small" && "rounded-lg",
          rounded === "medium" && "rounded-2xl",
          rounded === "large" && "rounded-3xl",
          rounded === "full" && "rounded-full",
          // Opacity variants
          opacity === "subtle" && "bg-opacity-20",
          opacity === "low" && "bg-opacity-25",
          opacity === "medium" && "bg-opacity-35",
          opacity === "high" && "bg-opacity-45",
          // Hover effect
          hoverable && "transition-all duration-200 hover:scale-[1.02] hover:bg-opacity-50",
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

GlassmorphicContainer.displayName = "GlassmorphicContainer"

export { GlassmorphicContainer, type GlassmorphicContainerProps } 