import userEvent from '@testing-library/user-event'

// Setup user event for tests
export const setupUser = (options = {}) => {
  return userEvent.setup(options)
}