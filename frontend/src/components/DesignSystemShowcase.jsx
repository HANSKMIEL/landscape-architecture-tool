import React from 'react';

// Button component with landscape-inspired variants
export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  className = '',
  ...props 
}) => {
  const baseClasses = 'btn';
  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    nature: 'btn-nature',
    earth: 'btn-earth',
    water: 'btn-water',
    outline: 'btn-outline'
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
};

// Card component with landscape themes
export const Card = ({ 
  children, 
  variant = 'default', 
  interactive = false,
  className = '',
  ...props 
}) => {
  const baseClasses = 'card';
  const variantClasses = {
    default: '',
    landscape: 'card-landscape',
    water: 'card-water',
    earth: 'card-earth'
  };
  
  const interactiveClass = interactive ? 'card-interactive' : '';
  const classes = `${baseClasses} ${variantClasses[variant]} ${interactiveClass} ${className}`;

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

// Container component with size variants
export const Container = ({ 
  children, 
  size = 'default',
  className = '',
  ...props 
}) => {
  const sizeClasses = {
    narrow: 'max-w-3xl mx-auto px-4',
    default: 'max-w-6xl mx-auto px-4',
    wide: 'max-w-7xl mx-auto px-4'
  };

  const classes = `${sizeClasses[size]} ${className}`;

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

// Stack component for consistent spacing
export const Stack = ({ 
  children, 
  space = 'md',
  className = '',
  ...props 
}) => {
  const spaceClasses = {
    sm: 'stack-sm',
    md: 'stack',
    lg: 'stack-lg'
  };

  const classes = `${spaceClasses[space]} ${className}`;

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

// Grid component for responsive layouts
export const Grid = ({ 
  children, 
  cols = 'auto',
  gap = 'md',
  className = '',
  ...props 
}) => {
  const colsClasses = {
    auto: 'grid-cols-auto',
    responsive: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4'
  };

  const gapClasses = {
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-6'
  };

  const classes = `grid ${colsClasses[cols]} ${gapClasses[gap]} ${className}`;

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

// Design System Showcase Component
export const DesignSystemShowcase = () => {
  return (
    <Container size="wide" className="py-8">
      <Stack space="lg">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Landscape Architecture Design System
          </h1>
          <p className="text-slate-600 text-lg">
            A comprehensive design system inspired by natural landscapes, 
            featuring earth tones, organic patterns, and sustainable design principles.
          </p>
        </div>

        {/* Button Variants */}
        <div>
          <h2 className="text-2xl font-semibold text-slate-800 mb-4">Button Variants</h2>
          <div className="flex flex-wrap gap-4">
            <Button variant="primary">Primary Action</Button>
            <Button variant="nature">Plant Tree</Button>
            <Button variant="water">Add Water Feature</Button>
            <Button variant="earth">Install Pathway</Button>
            <Button variant="outline">Secondary Action</Button>
          </div>
        </div>

        {/* Card Variants */}
        <div>
          <h2 className="text-2xl font-semibold text-slate-800 mb-4">Card Variants</h2>
          <Grid cols="responsive" gap="md">
            <Card variant="landscape">
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                Landscape Project
              </h3>
              <p className="text-green-700">
                Beautiful garden design with native plants and sustainable practices.
              </p>
            </Card>
            
            <Card variant="water">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">
                Water Features
              </h3>
              <p className="text-blue-700">
                Elegant fountains and water gardens that enhance outdoor spaces.
              </p>
            </Card>

            <Card variant="earth">
              <h3 className="text-lg font-semibold text-amber-800 mb-2">
                Hardscaping
              </h3>
              <p className="text-amber-700">
                Natural stone pathways and retaining walls using local materials.
              </p>
            </Card>
          </Grid>
        </div>

        {/* Interactive Cards */}
        <div>
          <h2 className="text-2xl font-semibold text-slate-800 mb-4">Interactive Elements</h2>
          <Grid cols="responsive" gap="md">
            <Card variant="landscape" interactive>
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                Click to Explore
              </h3>
              <p className="text-green-700">
                This card has hover effects and interactive states.
              </p>
            </Card>
          </Grid>
        </div>

        {/* Color Palette */}
        <div>
          <h2 className="text-2xl font-semibold text-slate-800 mb-4">Color Palette</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500 rounded-lg mx-auto mb-2 shadow-landscape"></div>
              <p className="text-sm font-medium">Primary Green</p>
              <p className="text-xs text-slate-600">#22c55e</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500 rounded-lg mx-auto mb-2 shadow-water"></div>
              <p className="text-sm font-medium">Secondary Blue</p>
              <p className="text-xs text-slate-600">#3b82f6</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-lime-500 rounded-lg mx-auto mb-2"></div>
              <p className="text-sm font-medium">Nature Green</p>
              <p className="text-xs text-slate-600">#84cc16</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-amber-600 rounded-lg mx-auto mb-2 shadow-earth"></div>
              <p className="text-sm font-medium">Earth Brown</p>
              <p className="text-xs text-slate-600">#d97706</p>
            </div>
          </div>
        </div>

        {/* Typography */}
        <div>
          <h2 className="text-2xl font-semibold text-slate-800 mb-4">Typography</h2>
          <Stack space="sm">
            <h1 className="text-4xl font-bold text-slate-900">Heading 1</h1>
            <h2 className="text-3xl font-semibold text-slate-800">Heading 2</h2>
            <h3 className="text-2xl font-medium text-slate-700">Heading 3</h3>
            <p className="text-base text-slate-600">
              Body text using Inter font family with proper line height and spacing
              for optimal readability across all devices and screen sizes.
            </p>
            <p className="text-sm text-slate-500">
              Small text for captions, metadata, and secondary information.
            </p>
          </Stack>
        </div>
      </Stack>
    </Container>
  );
};

export default DesignSystemShowcase;