import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'json-summary', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'dist/',
        'coverage/',
        '**/*.test.{js,jsx}',
        '**/*.spec.{js,jsx}',
        '**/*.config.{js,jsx}',
        'src/test/',
        'scripts/',
        '.eslintrc.js',
        'src/main.jsx'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        },
        'src/components/': {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90
        },
        'src/lib/': {
          branches: 95,
          functions: 95,
          lines: 95,
          statements: 95
        }
      }
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})