import { describe, it, expect } from 'vitest'

// Test to validate Fast Refresh compatibility
describe('Fast Refresh Compatibility', () => {
  it('should import variants from separate utility file', () => {
    // Test that variants are properly exported from lib/variants
    const { badgeVariants, toggleVariants } = require('../../src/lib/variants.js')
    expect(badgeVariants).toBeDefined()
    expect(toggleVariants).toBeDefined()
    expect(typeof badgeVariants).toBe('function')
    expect(typeof toggleVariants).toBe('function')
  })

  it('should import constants from separate constants file', () => {
    // Test that constants are properly exported from lib/constants
    const { SIDEBAR_WIDTH, SIDEBAR_COOKIE_NAME } = require('../../src/lib/constants.js')
    expect(SIDEBAR_WIDTH).toBe('16rem')
    expect(SIDEBAR_COOKIE_NAME).toBe('sidebar_state')
  })

  it('should import hooks from separate hooks file', () => {
    // Test that hooks are properly exported from hooks/useSidebar
    const { useSidebar } = require('../../src/hooks/useSidebar.js')
    expect(useSidebar).toBeDefined()
    expect(typeof useSidebar).toBe('function')
  })
})