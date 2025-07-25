import { describe, it, expect } from 'vitest'
import { cn } from '../lib/utils'

describe('Utility Functions', () => {
  describe('cn function', () => {
    it('merges class names correctly', () => {
      const result = cn('px-4', 'py-2', 'bg-blue-500')
      expect(result).toContain('px-4')
      expect(result).toContain('py-2')
      expect(result).toContain('bg-blue-500')
    })

    it('handles conditional classes', () => {
      const result = cn('base-class', true && 'conditional-class', false && 'hidden-class')
      expect(result).toContain('base-class')
      expect(result).toContain('conditional-class')
      expect(result).not.toContain('hidden-class')
    })

    it('handles undefined and null values', () => {
      const result = cn('base-class', undefined, null, 'other-class')
      expect(result).toContain('base-class')
      expect(result).toContain('other-class')
    })
  })
})