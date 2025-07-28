import React from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Container, Grid, Stack, Flex } from '@/components/ui/layout'
import { Badge } from '@/components/ui/badge'

/**
 * Design System Showcase Component
 * Demonstrates the implemented design tokens, components, and layout system
 */
const DesignSystemShowcase = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <Container size="wide">
        <Stack space="xl">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Landscape Architecture Design System
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              A comprehensive design system featuring design tokens, responsive layouts, 
              and landscape-themed components for professional architecture tools.
            </p>
          </div>

          {/* Color Palette */}
          <Card variant="featured" size="lg">
            <CardHeader>
              <CardTitle className="text-2xl">Color Palette</CardTitle>
              <CardDescription>
                Primary colors inspired by natural landscapes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Grid cols={{ base: 2, md: 4, lg: 6 }} gap="md">
                <div className="text-center">
                  <div className="w-16 h-16 bg-primary-500 rounded-lg mx-auto mb-2 shadow-md"></div>
                  <span className="text-sm font-medium">Primary</span>
                  <div className="text-xs text-gray-500">#22c55e</div>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-secondary-500 rounded-lg mx-auto mb-2 shadow-md"></div>
                  <span className="text-sm font-medium">Secondary</span>
                  <div className="text-xs text-gray-500">#3b82f6</div>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-green-600 rounded-lg mx-auto mb-2 shadow-md"></div>
                  <span className="text-sm font-medium">Nature</span>
                  <div className="text-xs text-gray-500">#16a34a</div>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-amber-600 rounded-lg mx-auto mb-2 shadow-md"></div>
                  <span className="text-sm font-medium">Earth</span>
                  <div className="text-xs text-gray-500">#d97706</div>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-600 rounded-lg mx-auto mb-2 shadow-md"></div>
                  <span className="text-sm font-medium">Water</span>
                  <div className="text-xs text-gray-500">#2563eb</div>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-gray-600 rounded-lg mx-auto mb-2 shadow-md"></div>
                  <span className="text-sm font-medium">Stone</span>
                  <div className="text-xs text-gray-500">#4b5563</div>
                </div>
              </Grid>
            </CardContent>
          </Card>

          {/* Button Variants */}
          <Card variant="default" size="lg">
            <CardHeader>
              <CardTitle className="text-2xl">Button Components</CardTitle>
              <CardDescription>
                Enhanced buttons with landscape-themed variants and design tokens
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Stack space="lg">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Primary Variants</h3>
                  <Flex wrap gap="md">
                    <Button variant="default">Default</Button>
                    <Button variant="secondary">Secondary</Button>
                    <Button variant="outline">Outline</Button>
                    <Button variant="ghost">Ghost</Button>
                    <Button variant="link">Link</Button>
                  </Flex>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-4">Landscape Variants</h3>
                  <Flex wrap gap="md">
                    <Button variant="nature">Nature</Button>
                    <Button variant="earth">Earth</Button>
                    <Button variant="water">Water</Button>
                  </Flex>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-4">Status Variants</h3>
                  <Flex wrap gap="md">
                    <Button variant="success">Success</Button>
                    <Button variant="warning">Warning</Button>
                    <Button variant="destructive">Error</Button>
                  </Flex>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-4">Sizes</h3>
                  <Flex align="center" gap="md">
                    <Button size="sm">Small</Button>
                    <Button size="default">Default</Button>
                    <Button size="lg">Large</Button>
                    <Button size="xl">Extra Large</Button>
                  </Flex>
                </div>
              </Stack>
            </CardContent>
          </Card>

          {/* Card Variants */}
          <Card variant="default" size="lg">
            <CardHeader>
              <CardTitle className="text-2xl">Card Components</CardTitle>
              <CardDescription>
                Flexible card components with multiple variants and styling options
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Grid cols={{ base: 1, md: 2, lg: 3 }} gap="lg">
                <Card variant="default">
                  <CardHeader>
                    <CardTitle>Default Card</CardTitle>
                    <CardDescription>Standard card with subtle shadow</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">
                      Perfect for general content and information display.
                    </p>
                  </CardContent>
                </Card>
                
                <Card variant="elevated">
                  <CardHeader>
                    <CardTitle>Elevated Card</CardTitle>
                    <CardDescription>Enhanced shadow for emphasis</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">
                      Use for important content that needs attention.
                    </p>
                  </CardContent>
                </Card>
                
                <Card variant="landscape">
                  <CardHeader>
                    <CardTitle>Landscape Card</CardTitle>
                    <CardDescription>Nature-inspired gradient background</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">
                      Themed for landscape architecture content.
                    </p>
                  </CardContent>
                </Card>
                
                <Card variant="success">
                  <CardHeader>
                    <CardTitle>Success Card</CardTitle>
                    <CardDescription>For positive feedback</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Badge variant="success">Completed</Badge>
                  </CardContent>
                </Card>
                
                <Card variant="warning">
                  <CardHeader>
                    <CardTitle>Warning Card</CardTitle>
                    <CardDescription>For important notices</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Badge variant="warning">Attention</Badge>
                  </CardContent>
                </Card>
                
                <Card variant="interactive" onClick={() => alert('Card clicked!')}>
                  <CardHeader>
                    <CardTitle>Interactive Card</CardTitle>
                    <CardDescription>Clickable with hover effects</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">
                      Click me to see interaction!
                    </p>
                  </CardContent>
                </Card>
              </Grid>
            </CardContent>
          </Card>

          {/* Layout System */}
          <Card variant="default" size="lg">
            <CardHeader>
              <CardTitle className="text-2xl">Layout System</CardTitle>
              <CardDescription>
                Responsive layout components for consistent spacing and alignment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Stack space="lg">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Container Sizes</h3>
                  <Stack space="md">
                    <div className="bg-gray-100 border-2 border-dashed border-gray-300 p-4 rounded">
                      <Container size="narrow">
                        <div className="bg-primary-100 p-4 rounded text-center">
                          Narrow Container (800px max)
                        </div>
                      </Container>
                    </div>
                    <div className="bg-gray-100 border-2 border-dashed border-gray-300 p-4 rounded">
                      <Container size="default">
                        <div className="bg-secondary-100 p-4 rounded text-center">
                          Default Container (1200px max)
                        </div>
                      </Container>
                    </div>
                  </Stack>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-4">Responsive Grid</h3>
                  <Grid cols={{ base: 1, sm: 2, md: 3, lg: 4 }} gap="md">
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((item) => (
                      <div key={item} className="bg-primary-100 p-4 rounded text-center">
                        Grid Item {item}
                      </div>
                    ))}
                  </Grid>
                </div>
              </Stack>
            </CardContent>
          </Card>

          {/* Typography Scale */}
          <Card variant="default" size="lg">
            <CardHeader>
              <CardTitle className="text-2xl">Typography Scale</CardTitle>
              <CardDescription>
                Consistent typography hierarchy with design tokens
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Stack space="md">
                <div className="text-6xl font-bold text-gray-900">Heading 1</div>
                <div className="text-5xl font-bold text-gray-900">Heading 2</div>
                <div className="text-4xl font-bold text-gray-900">Heading 3</div>
                <div className="text-3xl font-semibold text-gray-800">Heading 4</div>
                <div className="text-2xl font-semibold text-gray-800">Heading 5</div>
                <div className="text-xl font-medium text-gray-700">Heading 6</div>
                <div className="text-lg text-gray-600">Large text for introductions</div>
                <div className="text-base text-gray-600">Body text for main content</div>
                <div className="text-sm text-gray-500">Small text for captions</div>
                <div className="text-xs text-gray-400">Extra small text for metadata</div>
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      </Container>
    </div>
  )
}

export default DesignSystemShowcase