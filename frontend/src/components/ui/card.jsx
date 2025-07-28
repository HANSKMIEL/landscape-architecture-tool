import * as React from "react"
import { cva } from "class-variance-authority"
import { cn } from "@/lib/utils"

// Enhanced card variants using design tokens
const cardVariants = cva(
  "bg-card text-card-foreground flex flex-col rounded-lg border shadow-sm transition-all duration-200",
  {
    variants: {
      variant: {
        default: "border-gray-200 shadow-sm hover:shadow-md",
        elevated: "border-gray-200 shadow-md hover:shadow-lg",
        featured: "border-primary-200 bg-gradient-to-br from-primary-50 to-secondary-50 shadow-md hover:shadow-lg",
        landscape: "border-green-200 bg-gradient-to-br from-green-50 to-blue-50 shadow-md hover:shadow-lg",
        interactive: "border-gray-200 shadow-sm hover:shadow-md hover:border-primary-300 cursor-pointer",
        success: "border-green-200 bg-green-50 shadow-sm",
        warning: "border-yellow-200 bg-yellow-50 shadow-sm",
        error: "border-red-200 bg-red-50 shadow-sm",
        info: "border-blue-200 bg-blue-50 shadow-sm",
      },
      size: {
        sm: "p-4 gap-3",
        default: "p-6 gap-4",
        lg: "p-8 gap-6",
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

function Card({
  className,
  variant = "default",
  size = "default",
  fullWidth = false,
  onClick,
  ...props
}) {
  return (
    <div
      data-slot="card"
      className={cn(cardVariants({ variant, size, fullWidth }), className)}
      onClick={onClick}
      {...props} />
  );
}

function CardHeader({
  className,
  ...props
}) {
  return (
    <div
      data-slot="card-header"
      className={cn(
        "grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 has-data-[slot=card-action]:grid-cols-[1fr_auto]",
        className
      )}
      {...props} />
  );
}

function CardTitle({
  className,
  ...props
}) {
  return (
    <div
      data-slot="card-title"
      className={cn("leading-none font-semibold", className)}
      {...props} />
  );
}

function CardDescription({
  className,
  ...props
}) {
  return (
    <div
      data-slot="card-description"
      className={cn("text-muted-foreground text-sm", className)}
      {...props} />
  );
}

function CardAction({
  className,
  ...props
}) {
  return (
    <div
      data-slot="card-action"
      className={cn(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end",
        className
      )}
      {...props} />
  );
}

function CardContent({
  className,
  ...props
}) {
  return (<div data-slot="card-content" className={cn("px-6", className)} {...props} />);
}

function CardFooter({
  className,
  ...props
}) {
  return (
    <div
      data-slot="card-footer"
      className={cn("flex items-center px-6 [.border-t]:pt-6", className)}
      {...props} />
  );
}

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction,
  CardDescription,
  CardContent,
  cardVariants,
}
