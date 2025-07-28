// Utility functions for coverage testing

// Helper to ensure all code paths are tested
export const testAllCodePaths = (component, scenarios) => {
  scenarios.forEach(scenario => {
    test(`${component.name} - ${scenario.name}`, scenario.test);
  });
};

// Helper to test error boundaries and edge cases
export const testErrorScenarios = (component, errorScenarios) => {
  errorScenarios.forEach(scenario => {
    test(`${component.name} error: ${scenario.name}`, () => {
      // Suppress console.error for expected errors
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      try {
        scenario.test();
      } finally {
        consoleSpy.mockRestore();
      }
    });
  });
};

// Helper to ensure all props are tested
export const testAllProps = (Component, propTests) => {
  Object.entries(propTests).forEach(([propName, tests]) => {
    describe(`${Component.name} prop: ${propName}`, () => {
      tests.forEach(test => {
        it(test.description, test.test);
      });
    });
  });
};

// Helper to test component lifecycle methods
export const testLifecycleMethods = (Component, lifecycleTests) => {
  lifecycleTests.forEach(test => {
    it(`lifecycle: ${test.name}`, test.test);
  });
};