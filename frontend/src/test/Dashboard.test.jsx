import { render, screen } from '@testing-library/react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'

describe('Card Components', () => {
  it('renders card with content', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Title</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Test content</p>
        </CardContent>
      </Card>
    )

    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('renders card without header', () => {
    render(
      <Card>
        <CardContent>
          <p>Content only</p>
        </CardContent>
      </Card>
    )

    expect(screen.getByText('Content only')).toBeInTheDocument()
  })
})