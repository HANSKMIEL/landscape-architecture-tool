import React from 'react';
import { cn } from '@/lib/utils';

const Button = React.forwardRef(({ 
  className, 
  variant = "default", 
  size = "default", 
  asChild = false, 
  children,
  onClick,
  disabled = false,
  type = "button",
  ...props 
}, ref) => {
  
  // Base button styles
  const baseStyles = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background";
  
  // Variant styles
  const __variants = {
    default: "bg-green-600 text-white hover:bg-green-700 active:bg-green-800",
    destructive: "bg-red-600 text-white hover:bg-red-700 active:bg-red-800",
    outline: "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-gray-400 active:bg-gray-100",
    secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 active:bg-gray-300",
    ghost: "text-gray-700 hover:bg-gray-100 active:bg-gray-200",
    link: "underline-offset-4 hover:underline text-green-600 hover:text-green-700"
  };
  
  // Size styles
  const __sizes = {
    default: "h-10 py-2 px-4",
    sm: "h-9 px-3 rounded-md",
    lg: "h-11 px-8 rounded-md",
    icon: "h-10 w-10"
  };
  
  // Combine all styles
  const buttonStyles = cn(
    baseStyles,
    variants[variant],
    sizes[size],
    className
  );
  
  // Handle click events
  const handleClick = (e) => {
    if (disabled) {
      e.preventDefault();
      return;
    }
    if (onClick) {
      onClick(e);
    }
  };

  if (asChild) {
    return React.cloneElement(children, {
      className: buttonStyles,
      onClick: handleClick,
      disabled,
      ref,
      ...props
    });
  }

  return (
    <button
      className={buttonStyles}
      ref={ref}
      onClick={handleClick}
      disabled={disabled}
      type={type}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = "Button";

export { Button };

