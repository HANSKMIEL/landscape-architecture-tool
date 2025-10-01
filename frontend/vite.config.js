import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig(({ _command, mode }) => {
  // Load environment variables based on mode
  const env = loadEnv(mode, process.cwd(), '')
  
  // Determine base path based on environment
  let basePath = '/'
  if (mode === 'demo') {
    basePath = '/landscape-architecture-tool/'
  }
  
  // Determine if we're building for GitHub Pages
  const isGitHubPages = mode === 'demo'
  
  console.log(`Building for mode: ${mode}, base path: ${basePath}, GitHub Pages: ${isGitHubPages}`)
  
  return {
    plugins: [react()],
    base: basePath,
    define: {
      // Make environment variables available in the app
      'import.meta.env.VITE_BUILD_MODE': JSON.stringify(mode),
      'import.meta.env.VITE_IS_GITHUB_PAGES': JSON.stringify(isGitHubPages),
    },
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      port: 5174,
      host: true,
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:5000',
          changeOrigin: true,
          secure: false
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: mode !== 'production',
      // Enable cache busting with hashed filenames
      assetsInlineLimit: 0,
      rollupOptions: {
        output: {
          // Add hash to filenames for cache busting
          entryFileNames: 'assets/[name]-[hash].js',
          chunkFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash].[ext]',
          manualChunks: {
            // Vendor chunk for React and router
            vendor: ['react', 'react-dom', 'react-router-dom'],
            // UI components chunk
            ui: ['@radix-ui/react-accordion', '@radix-ui/react-alert-dialog', '@radix-ui/react-avatar', 
                '@radix-ui/react-checkbox', '@radix-ui/react-collapsible', '@radix-ui/react-context-menu',
                '@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-hover-card',
                '@radix-ui/react-label', '@radix-ui/react-menubar', '@radix-ui/react-navigation-menu',
                '@radix-ui/react-popover', '@radix-ui/react-progress', '@radix-ui/react-radio-group',
                '@radix-ui/react-scroll-area', '@radix-ui/react-select', '@radix-ui/react-separator',
                '@radix-ui/react-slider', '@radix-ui/react-slot', '@radix-ui/react-switch',
                '@radix-ui/react-tabs', '@radix-ui/react-toast', '@radix-ui/react-toggle',
                '@radix-ui/react-toggle-group', '@radix-ui/react-tooltip'],
            // Charts and visualization
            charts: ['recharts'],
            // Icons
            icons: ['lucide-react'],
            // Utilities
            utils: ['class-variance-authority', 'clsx', 'tailwind-merge', 'date-fns', 'react-day-picker', 'react-hot-toast', 'sonner']
          }
        }
      }
    },
    css: {
      // Remove PostCSS configuration entirely
    },
  }
})
