# Landscape Architecture Design System

A comprehensive design system built for the Landscape Architecture Management Tool, featuring design tokens, responsive layouts, and landscape-themed components.

## Overview

This design system provides a consistent visual language and component library that reflects the natural aesthetics of landscape architecture while maintaining professional functionality.

## 🎨 Design Tokens

### Color Palette

Our color system is inspired by natural landscapes and provides semantic meaning across the application.

#### Primary Colors
- **Primary Green** (`#22c55e`): Main brand color representing nature and growth
- **Secondary Blue** (`#3b82f6`): Complementary color representing water and sky

#### Landscape Theme Colors
- **Nature Green** (`#16a34a`): Deep forest green for natural elements
- **Earth Brown** (`#d97706`): Warm earth tones for ground elements  
- **Water Blue** (`#2563eb`): Clear water blue for water features
- **Stone Gray** (`#4b5563`): Neutral stone color for hardscape elements

#### Status Colors
- **Success** (`#10b981`): Positive actions and confirmations
- **Warning** (`#f59e0b`): Cautionary states and alerts
- **Error** (`#ef4444`): Error states and destructive actions
- **Info** (`#3b82f6`): Informational content

### Typography

#### Font Stack
- **Primary**: Inter (clean, modern sans-serif)
- **Monospace**: JetBrains Mono (code and technical content)

#### Typography Scale
```
text-xs    : 0.75rem (12px)
text-sm    : 0.875rem (14px)  
text-base  : 1rem (16px)
text-lg    : 1.125rem (18px)
text-xl    : 1.25rem (20px)
text-2xl   : 1.5rem (24px)
text-3xl   : 1.875rem (30px)
text-4xl   : 2.25rem (36px)
text-5xl   : 3rem (48px)
text-6xl   : 3.75rem (60px)
```

### Spacing Scale

Consistent spacing using a harmonic scale:
```
xs:  0.25rem (4px)
sm:  0.5rem (8px)
md:  1rem (16px)
lg:  1.5rem (24px)
xl:  2rem (32px)
2xl: 3rem (48px)
3xl: 4rem (64px)
4xl: 6rem (96px)
5xl: 8rem (128px)
```

### Border Radius
```
sm:  0.25rem
md:  0.5rem (default)
lg:  0.75rem
xl:  1rem
2xl: 1.5rem
```

### Shadows
```
sm:  Subtle shadow for hover states
md:  Default shadow for cards
lg:  Elevated shadow for modals
xl:  Deep shadow for overlays
```

## 🧩 Components

### Button Component

Enhanced button with multiple variants and states.

#### Variants
- `default`: Primary green button
- `secondary`: Secondary blue button  
- `outline`: Outlined button with hover fill
- `ghost`: Transparent button with hover background
- `link`: Text-only link-style button
- `nature`: Deep green nature-themed button
- `earth`: Warm earth-toned button
- `water`: Blue water-themed button
- `success`: Green success button
- `warning`: Orange warning button
- `destructive`: Red error/delete button

#### Sizes  
- `sm`: Small button (32px height)
- `default`: Standard button (40px height)
- `lg`: Large button (48px height)
- `xl`: Extra large button (56px height)
- `icon`: Square icon button
- `icon-sm`: Small icon button
- `icon-lg`: Large icon button

#### Props
- `variant`: Button style variant
- `size`: Button size
- `fullWidth`: Make button full width
- `loading`: Show loading spinner and disable
- `icon`: Icon component to display
- `iconPosition`: Position of icon (`left` | `right`)
- `disabled`: Disable the button
- `onClick`: Click handler

#### Usage
```jsx
import { Button } from '@/components/ui/button'

// Basic usage
<Button>Click me</Button>

// With variants
<Button variant="nature">Plant Tree</Button>
<Button variant="water">Add Water Feature</Button>

// With sizes
<Button size="lg">Large Action</Button>
<Button size="sm">Small Action</Button>

// With states
<Button loading>Saving...</Button>
<Button disabled>Unavailable</Button>

// Full width
<Button fullWidth>Submit Form</Button>
```

### Card Component

Flexible card container with multiple visual variants.

#### Variants
- `default`: Standard card with subtle shadow
- `elevated`: Enhanced shadow for prominence  
- `featured`: Gradient background for featured content
- `landscape`: Nature-inspired gradient for landscape content
- `interactive`: Hover effects for clickable cards
- `success`: Green background for success states
- `warning`: Yellow background for warnings
- `error`: Red background for errors
- `info`: Blue background for information

#### Sizes
- `sm`: Compact card (16px padding)
- `default`: Standard card (24px padding)
- `lg`: Spacious card (32px padding)

#### Sub-components
- `CardHeader`: Header section with title and description
- `CardTitle`: Card title styling
- `CardDescription`: Subtitle/description styling  
- `CardContent`: Main content area
- `CardFooter`: Footer section for actions

#### Usage
```jsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'

<Card variant="landscape">
  <CardHeader>
    <CardTitle>Garden Design</CardTitle>
    <CardDescription>Beautiful landscape project</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Project details and information...</p>
  </CardContent>
</Card>
```

## 📐 Layout System

### Container

Responsive container with max-width constraints.

#### Sizes
- `narrow`: 800px max width for focused content
- `default`: 1200px max width for general layout
- `wide`: 1400px max width for dashboard layouts
- `full`: Full width with responsive padding

#### Usage
```jsx
import { Container } from '@/components/ui/layout'

<Container size="narrow">
  <p>Focused content area</p>
</Container>
```

### Grid

Responsive CSS Grid with flexible column configurations.

#### Variants
- `default`: Auto-fit grid with 300px min columns
- `cards`: Responsive card grid (1-4 columns)
- `dashboard`: Dashboard layout (2-3 columns)
- `custom`: Custom grid for manual configuration

#### Props
- `cols`: Responsive column configuration
  - `base`: Base columns (mobile first)
  - `sm`: Columns at small breakpoint (640px+)
  - `md`: Columns at medium breakpoint (768px+)  
  - `lg`: Columns at large breakpoint (1024px+)
  - `xl`: Columns at extra large breakpoint (1280px+)
- `gap`: Gap between grid items (`sm` | `md` | `lg` | `xl`)

#### Usage
```jsx
import { Grid } from '@/components/ui/layout'

<Grid cols={{ base: 1, md: 2, lg: 3 }} gap="md">
  <Card>Item 1</Card>
  <Card>Item 2</Card>
  <Card>Item 3</Card>
</Grid>
```

### Stack

Vertical layout with consistent spacing.

#### Props
- `space`: Vertical spacing (`xs` | `sm` | `md` | `lg` | `xl`)
- `align`: Horizontal alignment (`start` | `center` | `end` | `stretch`)

#### Usage
```jsx
import { Stack } from '@/components/ui/layout'

<Stack space="lg" align="center">
  <h1>Title</h1>
  <p>Description</p>
  <Button>Action</Button>
</Stack>
```

### Flex

Horizontal layout with flexible configuration.

#### Props
- `direction`: Flex direction (`row` | `row-reverse` | `col` | `col-reverse`)
- `align`: Cross-axis alignment (`start` | `center` | `end` | `stretch` | `baseline`)
- `justify`: Main-axis alignment (`start` | `center` | `end` | `between` | `around` | `evenly`)
- `wrap`: Allow flex wrap
- `gap`: Gap between items (`xs` | `sm` | `md` | `lg` | `xl`)

#### Usage
```jsx
import { Flex } from '@/components/ui/layout'

<Flex justify="between" align="center" gap="md">
  <h2>Title</h2>
  <Button>Action</Button>
</Flex>
```

## 📱 Responsive Design

### Breakpoints
```
sm:  640px
md:  768px  
lg:  1024px
xl:  1280px
2xl: 1536px
```

### Mobile-First Approach
All components are designed mobile-first with progressive enhancement for larger screens.

### Responsive Utilities
- `.responsive-padding`: Responsive horizontal padding
- `.responsive-margin`: Responsive horizontal margins  
- `.responsive-text`: Responsive text sizing

## 🎯 Usage Guidelines

### Color Usage
- Use primary green for main actions and brand elements
- Use secondary blue for secondary actions and information
- Use landscape theme colors for context-specific elements
- Use status colors consistently for feedback states

### Typography Hierarchy
- Use consistent heading scales (h1-h6 with corresponding text sizes)
- Maintain proper contrast ratios for accessibility
- Use font weights purposefully (medium for emphasis, semibold for headings)

### Spacing Consistency
- Use the defined spacing scale for all layouts
- Maintain consistent gaps in grids and stacks
- Use padding consistently within components

### Component Composition
- Combine layout components for complex layouts
- Use cards as containers for related content
- Stack buttons logically with appropriate variants

## 🔧 Development

### CSS Architecture
The design system uses a layered CSS approach:

1. **Base Layer** (`@layer base`): Reset styles and typography
2. **Component Layer** (`@layer components`): Reusable component classes
3. **Utility Layer** (`@layer utilities`): Custom utility classes

### Tailwind Integration
- Design tokens are defined in `tailwind.config.js`
- Custom CSS variables provide flexible theming
- PostCSS processes Tailwind directives

### Testing
Comprehensive test suite covers:
- Component rendering and props
- Variant class application
- Event handling
- Accessibility compliance

Run tests with:
```bash
npm run test
```

## 🚀 Getting Started

1. **Import components:**
```jsx
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'  
import { Container, Grid, Stack, Flex } from '@/components/ui/layout'
```

2. **Use design tokens:**
```jsx
// Via Tailwind classes
<div className="bg-primary-500 text-white p-md rounded-lg">

// Via CSS custom properties  
<div style={{ backgroundColor: 'var(--primary)' }}>
```

3. **Compose layouts:**
```jsx
<Container>
  <Stack space="lg">
    <h1>Page Title</h1>
    <Grid cols={{ md: 2, lg: 3 }}>
      <Card>Content 1</Card>
      <Card>Content 2</Card>
      <Card>Content 3</Card>
    </Grid>
  </Stack>
</Container>
```

## 📚 Examples

Visit `/design-system` route in the application to see a comprehensive showcase of all components, variants, and layout patterns in action.

The showcase includes:
- Color palette demonstrations
- Button variant examples
- Card type comparisons  
- Layout system examples
- Typography scale display
- Responsive behavior testing

## 🔄 Future Enhancements

- [ ] Dark mode support
- [ ] Additional landscape-themed components
- [ ] Animation and transition utilities
- [ ] Form components with design system integration
- [ ] Advanced layout patterns (Masonry, etc.)
- [ ] Component documentation generator
- [ ] Visual regression testing
- [ ] Figma design tokens integration