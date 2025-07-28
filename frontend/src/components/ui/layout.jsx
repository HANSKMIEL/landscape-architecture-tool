import React from 'react'
import { cn } from '@/lib/utils'

/**
 * Container component with responsive padding and max-width constraints
 */
export const Container = React.forwardRef(({ 
  className, 
  size = 'default', 
  children, 
  ...props 
}, ref) => {
  const sizeClasses = {
    narrow: 'container-narrow',
    default: 'container-landscape', 
    wide: 'container-wide',
    full: 'w-full px-4 sm:px-6 lg:px-8'
  }

  return (
    <div
      ref={ref}
      className={cn(sizeClasses[size], className)}
      {...props}
    >
      {children}
    </div>
  )
})
Container.displayName = 'Container'

/**
 * Grid component with responsive layouts
 */
export const Grid = React.forwardRef(({ 
  className, 
  variant = 'default',
  cols = {},
  gap = 'md',
  children, 
  ...props 
}, ref) => {
  const gapClasses = {
    sm: 'gap-4',
    md: 'gap-6', 
    lg: 'gap-8',
    xl: 'gap-12'
  }
  
  const variantClasses = {
    default: 'grid-landscape',
    cards: 'grid-cards',
    dashboard: 'grid-dashboard',
    auto: 'grid grid-cols-1',
    custom: 'grid'
  }
  
  // Build responsive grid classes
  const responsiveClasses = []
  if (cols.base) responsiveClasses.push(`grid-cols-${cols.base}`)
  if (cols.sm) responsiveClasses.push(`sm:grid-cols-${cols.sm}`)
  if (cols.md) responsiveClasses.push(`md:grid-cols-${cols.md}`)
  if (cols.lg) responsiveClasses.push(`lg:grid-cols-${cols.lg}`)
  if (cols.xl) responsiveClasses.push(`xl:grid-cols-${cols.xl}`)
  
  const baseClass = variant === 'custom' ? variantClasses.custom : variantClasses[variant]
  
  return (
    <div
      ref={ref}
      className={cn(
        baseClass,
        gapClasses[gap],
        responsiveClasses.join(' '),
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
})
Grid.displayName = 'Grid'

/**
 * Stack component for vertical layouts with consistent spacing
 */
export const Stack = React.forwardRef(({ 
  className, 
  space = 'md',
  align = 'start',
  children, 
  ...props 
}, ref) => {
  const spaceClasses = {
    xs: 'space-y-1',
    sm: 'space-y-2', 
    md: 'space-y-4',
    lg: 'space-y-6',
    xl: 'space-y-8'
  }
  
  const alignClasses = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch'
  }

  return (
    <div
      ref={ref}
      className={cn(
        'flex flex-col',
        spaceClasses[space],
        alignClasses[align],
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
})
Stack.displayName = 'Stack'

/**
 * Flex component for horizontal layouts
 */
export const Flex = React.forwardRef(({ 
  className, 
  direction = 'row',
  align = 'start',
  justify = 'start',
  wrap = false,
  gap = 'md',
  children, 
  ...props 
}, ref) => {
  const directionClasses = {
    row: 'flex-row',
    'row-reverse': 'flex-row-reverse',
    col: 'flex-col',
    'col-reverse': 'flex-col-reverse'
  }
  
  const alignClasses = {
    start: 'items-start',
    center: 'items-center', 
    end: 'items-end',
    stretch: 'items-stretch',
    baseline: 'items-baseline'
  }
  
  const justifyClasses = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
    around: 'justify-around',
    evenly: 'justify-evenly'
  }
  
  const gapClasses = {
    xs: 'gap-1',
    sm: 'gap-2',
    md: 'gap-4', 
    lg: 'gap-6',
    xl: 'gap-8'
  }

  return (
    <div
      ref={ref}
      className={cn(
        'flex',
        directionClasses[direction],
        alignClasses[align],
        justifyClasses[justify],
        gapClasses[gap],
        wrap && 'flex-wrap',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
})
Flex.displayName = 'Flex'

/**
 * Section component for page sections with consistent spacing
 */
export const Section = React.forwardRef(({ 
  className, 
  spacing = 'default',
  children, 
  ...props 
}, ref) => {
  const spacingClasses = {
    tight: 'py-8',
    default: 'py-12 sm:py-16',
    loose: 'py-16 sm:py-20',
    none: ''
  }

  return (
    <section
      ref={ref}
      className={cn(spacingClasses[spacing], className)}
      {...props}
    >
      {children}
    </section>
  )
})
Section.displayName = 'Section'

/**
 * Box component - general purpose container with responsive spacing
 */
export const Box = React.forwardRef(({ 
  className, 
  p = 0,
  px = null,
  py = null,
  m = 0,
  mx = null,
  my = null,
  children, 
  ...props 
}, ref) => {
  const classes = []
  
  // Padding
  if (px !== null) classes.push(`px-${px}`)
  else if (p) classes.push(`p-${p}`)
  
  if (py !== null) classes.push(`py-${py}`)
  else if (p && px === null) classes.push(`p-${p}`)
  
  // Margin
  if (mx !== null) classes.push(`mx-${mx}`)
  else if (m) classes.push(`m-${m}`)
  
  if (my !== null) classes.push(`my-${my}`)
  else if (m && mx === null) classes.push(`m-${m}`)

  return (
    <div
      ref={ref}
      className={cn(classes.join(' '), className)}
      {...props}
    >
      {children}
    </div>
  )
})
Box.displayName = 'Box'