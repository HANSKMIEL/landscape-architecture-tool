# Dual Testing Framework Setup

This project now supports both Jest and Vitest testing frameworks, giving developers flexibility to choose their preferred testing environment.

## Framework Comparison

| Feature | Jest | Vitest |
|---------|------|--------|
| **Performance** | Good | Faster |
| **Vite Integration** | Via Babel | Native |
| **Industry Adoption** | Widespread | Growing |
| **Configuration** | Babel-based | Vite-based |
| **Watch Mode** | Traditional | Hot Module Replacement |

## Available Scripts

### Jest Scripts
```bash
npm test              # Run Jest tests
npm run test:run      # Run Jest tests (explicit)
npm run test:watch    # Jest watch mode
npm run test:coverage # Jest coverage report
```

### Vitest Scripts
```bash
npm run test:vitest         # Run Vitest tests
npm run test:vitest:run     # Run Vitest tests (explicit)
npm run test:vitest:watch   # Vitest watch mode
npm run test:vitest:ui      # Vitest UI (requires @vitest/ui)
npm run test:vitest:coverage # Vitest coverage report
```

## Configuration Files

### Jest Configuration
- **jest.config.js**: Main Jest configuration
- **babel.config.json**: Babel presets for ES6/React transformation
- **src/test/setup.js**: Jest test setup and mocks

### Vitest Configuration
- **vitest.config.js**: Main Vitest configuration
- **src/test/setup-vitest.js**: Vitest test setup and mocks
- **src/test/mocks/server-vitest.js**: Vitest-compatible mock server

## Coverage Reports

- **Jest**: Coverage reports in `./coverage/`
- **Vitest**: Coverage reports in `./coverage-vitest/`

## Test Infrastructure

Both frameworks share the same test utilities:
- **React Testing Library**: Component testing
- **jest-axe**: Accessibility testing
- **Test Helpers**: Form interaction, loading states, error handling
- **Mock Data**: API response mocking

## Current Test Status

- **Core Infrastructure Tests**: ✅ Passing in both frameworks
- **Component Tests**: ⚠️ Some issues with API mocking (unrelated to dual setup)
- **Total**: 18+ tests passing in both Jest and Vitest

## Best Practices

1. **Choose One Framework Per Project Phase**: While both are available, teams should typically standardize on one framework for consistency.

2. **Jest for**: Enterprise projects, complex mocking scenarios, established workflows

3. **Vitest for**: Vite-based projects, faster development cycles, modern tooling

4. **Migration Path**: Tests written for one framework can be easily adapted for the other since both use the same Testing Library APIs.

## Framework-Specific Features

### Jest-Specific
- Uses Babel for transformation
- Traditional Node.js-based environment
- Extensive Jest ecosystem plugins

### Vitest-Specific  
- Native ES module support
- Hot Module Replacement in watch mode
- Better Vite integration and performance
- Uses vi instead of jest for mocking

## Getting Started

To run tests with your preferred framework:

```bash
# Quick start with Jest (default)
npm test

# Quick start with Vitest
npm run test:vitest

# Watch mode comparison
npm run test:watch        # Jest watch
npm run test:vitest:watch # Vitest watch
```

Both frameworks will produce equivalent results for the same test suites.