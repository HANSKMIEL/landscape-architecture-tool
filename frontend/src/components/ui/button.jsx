import React from 'react';
import { cva } from 'class-variance-authority';
import { cn } from '@/lib/utils';

// Enhanced button variants using design tokens
const buttonVariants = cva(
  // Base styles with design system tokens
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ring-offset-background select-none",
  {
    variants: {
      variant: {
        // Landscape-themed variants using design tokens
        default: "bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700 shadow-sm hover:shadow-md",
        destructive: "bg-error-500 text-white hover:bg-error-600 active:bg-error-700 shadow-sm hover:shadow-md",
        outline: "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-primary-300 active:bg-gray-100 shadow-sm",
        secondary: "bg-secondary-500 text-white hover:bg-secondary-600 active:bg-secondary-700 shadow-sm hover:shadow-md",
        ghost: "text-gray-700 hover:bg-gray-100 hover:text-primary-600 active:bg-gray-200",
        link: "text-primary-600 underline-offset-4 hover:underline hover:text-primary-700 active:text-primary-800",
        
        // New landscape-specific variants
        nature: "bg-green-600 text-white hover:bg-green-700 active:bg-green-800 shadow-sm hover:shadow-md",
        earth: "bg-amber-600 text-white hover:bg-amber-700 active:bg-amber-800 shadow-sm hover:shadow-md",
        water: "bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-sm hover:shadow-md",
        success: "bg-success-500 text-white hover:bg-success-600 active:bg-success-700 shadow-sm hover:shadow-md",
        warning: "bg-warning-500 text-white hover:bg-warning-600 active:bg-warning-700 shadow-sm hover:shadow-md",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 px-3 text-xs",
        lg: "h-12 px-6 text-base",
        xl: "h-14 px-8 text-lg",
        icon: "h-10 w-10",
        "icon-sm": "h-8 w-8",
        "icon-lg": "h-12 w-12",
      },
      fullWidth: {
        true: "w-full",
        false: "w-auto",
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      fullWidth: false,
    },
  }
)

const Button = React.forwardRef(({ 
  className, 
  variant = "default", 
  size = "default", 
  fullWidth = false,
  asChild = false, 
  children,
  onClick,
  disabled = false,
  type = "button",
  loading = false,
  icon: Icon = null,
  iconPosition = "left",
  ...props 
}, ref) => {
  // Handle click events
  const handleClick = (e) => {
    if (disabled || loading) {
      e.preventDefault();
      return;
    }
    if (onClick) {
      onClick(e);
    }
  };

  // Render loading spinner
  const LoadingSpinner = () => (
    <svg
      className="animate-spin h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );

  const buttonContent = (
    <>
      {loading && iconPosition === "left" && <LoadingSpinner />}
      {Icon && !loading && iconPosition === "left" && <Icon className="h-4 w-4" />}
      {children && (
        <span className={cn(
          (Icon || loading) && iconPosition === "left" && "ml-2",
          (Icon || loading) && iconPosition === "right" && "mr-2"
        )}>
          {children}
        </span>
      )}
      {Icon && !loading && iconPosition === "right" && <Icon className="h-4 w-4" />}
      {loading && iconPosition === "right" && <LoadingSpinner />}
    </>
  );

  if (asChild) {
    return React.cloneElement(children, {
      className: cn(buttonVariants({ variant, size, fullWidth }), className),
      onClick: handleClick,
      disabled: disabled || loading,
      ref,
      ...props
    });
  }

  return (
    <button
      className={cn(buttonVariants({ variant, size, fullWidth }), className)}
      ref={ref}
      onClick={handleClick}
      disabled={disabled || loading}
      type={type}
      {...props}
    >
      {buttonContent}
    </button>
  );
});

Button.displayName = "Button";

export { Button, buttonVariants };

