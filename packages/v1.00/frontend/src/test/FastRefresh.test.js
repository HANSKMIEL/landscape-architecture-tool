// Jest provides describe, it, and expect globally

// Test to validate Fast Refresh compatibility
describe('Fast Refresh Compatibility', () => {
  it('should import variants from separate utility file', async () => {
    // Test that variants are properly exported from lib/variants
    const { badgeVariants, toggleVariants } = await import('../../src/lib/variants.js')
    expect(badgeVariants).toBeDefined()
    expect(toggleVariants).toBeDefined()
    expect(typeof badgeVariants).toBe('function')
    expect(typeof toggleVariants).toBe('function')
  })

  it('should import constants from separate constants file', async () => {
    // Test that constants are properly exported from lib/constants
    const { SIDEBAR_WIDTH, SIDEBAR_COOKIE_NAME } = await import('../../src/lib/constants.js')
    expect(SIDEBAR_WIDTH).toBe('16rem')
    expect(SIDEBAR_COOKIE_NAME).toBe('sidebar_state')
  })

  it('should import hooks from separate hooks file', async () => {
    // Test that hooks are properly exported from hooks/useSidebar
    const { useSidebar } = await import('../../src/hooks/useSidebar.js')
    expect(useSidebar).toBeDefined()
    expect(typeof useSidebar).toBe('function')
  })
})