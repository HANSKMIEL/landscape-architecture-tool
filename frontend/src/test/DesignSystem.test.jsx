import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Container, Grid, Stack, Flex } from '@/components/ui/layout'

describe('Design System Components', () => {
  describe('Button Component', () => {
    it('renders with default variant', () => {
      render(<Button>Click me</Button>)
      const button = screen.getByRole('button', { name: /click me/i })
      expect(button).toBeInTheDocument()
    })

    it('applies correct variant classes', () => {
      render(<Button variant="nature">Nature Button</Button>)
      const button = screen.getByRole('button', { name: /nature button/i })
      expect(button).toHaveClass('bg-green-600')
    })

    it('handles click events', () => {
      const handleClick = vi.fn()
      render(<Button onClick={handleClick}>Click me</Button>)
      const button = screen.getByRole('button', { name: /click me/i })
      fireEvent.click(button)
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('respects disabled state', () => {
      const handleClick = vi.fn()
      render(<Button disabled onClick={handleClick}>Disabled</Button>)
      const button = screen.getByRole('button', { name: /disabled/i })
      expect(button).toBeDisabled()
      fireEvent.click(button)
      expect(handleClick).not.toHaveBeenCalled()
    })

    it('shows loading state', () => {
      render(<Button loading>Loading</Button>)
      const button = screen.getByRole('button', { name: /loading/i })
      expect(button).toBeDisabled()
      expect(button.querySelector('svg')).toBeInTheDocument() // Loading spinner
    })

    it('applies size variants correctly', () => {
      render(<Button size="lg">Large Button</Button>)
      const button = screen.getByRole('button', { name: /large button/i })
      expect(button).toHaveClass('h-12')
    })

    it('applies fullWidth prop correctly', () => {
      render(<Button fullWidth>Full Width</Button>)
      const button = screen.getByRole('button', { name: /full width/i })
      expect(button).toHaveClass('w-full')
    })
  })

  describe('Card Component', () => {
    it('renders basic card structure', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Card</CardTitle>
          </CardHeader>
          <CardContent>Card content</CardContent>
        </Card>
      )
      expect(screen.getByText('Test Card')).toBeInTheDocument()
      expect(screen.getByText('Card content')).toBeInTheDocument()
    })

    it('applies variant classes correctly', () => {
      const { container } = render(<Card variant="featured">Featured Card</Card>)
      const card = container.firstChild
      expect(card).toHaveClass('border-primary-200')
      expect(card).toHaveClass('bg-gradient-to-br')
    })

    it('handles click events for interactive cards', () => {
      const handleClick = vi.fn()
      render(<Card onClick={handleClick}>Clickable Card</Card>)
      const card = screen.getByText('Clickable Card')
      fireEvent.click(card)
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('applies size variants correctly', () => {
      const { container } = render(<Card size="lg">Large Card</Card>)
      const card = container.firstChild
      expect(card).toHaveClass('p-8')
    })
  })

  describe('Layout Components', () => {
    describe('Container', () => {
      it('renders with default size', () => {
        const { container } = render(<Container>Content</Container>)
        const containerEl = container.firstChild
        expect(containerEl).toHaveClass('container-landscape')
      })

      it('applies size variants correctly', () => {
        const { container } = render(<Container size="narrow">Content</Container>)
        const containerEl = container.firstChild
        expect(containerEl).toHaveClass('container-narrow')
      })
    })

    describe('Grid', () => {
      it('renders with default grid classes', () => {
        const { container } = render(<Grid>Grid content</Grid>)
        const gridEl = container.firstChild
        expect(gridEl).toHaveClass('grid-landscape')
      })

      it('applies responsive column classes', () => {
        const { container } = render(
          <Grid cols={{ base: 1, md: 2, lg: 3 }}>Grid content</Grid>
        )
        const gridEl = container.firstChild
        expect(gridEl).toHaveClass('grid-cols-1')
        expect(gridEl).toHaveClass('md:grid-cols-2')
        expect(gridEl).toHaveClass('lg:grid-cols-3')
      })

      it('applies gap variants correctly', () => {
        const { container } = render(<Grid gap="lg">Grid content</Grid>)
        const gridEl = container.firstChild
        expect(gridEl).toHaveClass('gap-8')
      })
    })

    describe('Stack', () => {
      it('renders with vertical layout', () => {
        const { container } = render(<Stack>Stack content</Stack>)
        const stackEl = container.firstChild
        expect(stackEl).toHaveClass('flex')
        expect(stackEl).toHaveClass('flex-col')
      })

      it('applies spacing correctly', () => {
        const { container } = render(<Stack space="lg">Stack content</Stack>)
        const stackEl = container.firstChild
        expect(stackEl).toHaveClass('space-y-6')
      })

      it('applies alignment correctly', () => {
        const { container } = render(<Stack align="center">Stack content</Stack>)
        const stackEl = container.firstChild
        expect(stackEl).toHaveClass('items-center')
      })
    })

    describe('Flex', () => {
      it('renders with horizontal layout by default', () => {
        const { container } = render(<Flex>Flex content</Flex>)
        const flexEl = container.firstChild
        expect(flexEl).toHaveClass('flex')
        expect(flexEl).toHaveClass('flex-row')
      })

      it('applies direction correctly', () => {
        const { container } = render(<Flex direction="col">Flex content</Flex>)
        const flexEl = container.firstChild
        expect(flexEl).toHaveClass('flex-col')
      })

      it('applies justify and align correctly', () => {
        const { container } = render(
          <Flex justify="center" align="center">Flex content</Flex>
        )
        const flexEl = container.firstChild
        expect(flexEl).toHaveClass('justify-center')
        expect(flexEl).toHaveClass('items-center')
      })

      it('applies wrap when specified', () => {
        const { container } = render(<Flex wrap>Flex content</Flex>)
        const flexEl = container.firstChild
        expect(flexEl).toHaveClass('flex-wrap')
      })
    })
  })

  describe('Design Tokens Integration', () => {
    it('uses consistent color classes', () => {
      render(<Button variant="default">Primary Button</Button>)
      const button = screen.getByRole('button', { name: /primary button/i })
      expect(button).toHaveClass('bg-primary-500')
    })

    it('applies landscape-specific color variants', () => {
      render(<Button variant="nature">Nature Button</Button>)
      const button = screen.getByRole('button', { name: /nature button/i })
      expect(button).toHaveClass('bg-green-600')
    })

    it('uses consistent spacing in layout components', () => {
      const { container } = render(<Grid gap="md">Grid</Grid>)
      const grid = container.firstChild
      expect(grid).toHaveClass('gap-6')
    })
  })
})