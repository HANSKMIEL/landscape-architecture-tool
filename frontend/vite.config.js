import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
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
    sourcemap: false,
    minify: 'terser',
    reportCompressedSize: false, // Disable reporting for faster builds
    chunkSizeWarningLimit: 600, // Increase warning limit
    rollupOptions: {
      output: {
        // Improved manual chunking strategy
        manualChunks: (id) => {
          // Node modules chunking
          if (id.includes('node_modules')) {
            // React ecosystem
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
              return 'react-vendor';
            }
            
            // Radix UI components
            if (id.includes('@radix-ui')) {
              return 'radix-ui';
            }
            
            // Charts and visualization
            if (id.includes('recharts') || id.includes('d3')) {
              return 'charts';
            }
            
            // Utility libraries
            if (id.includes('lodash') || id.includes('date-fns') || id.includes('clsx') || 
                id.includes('class-variance-authority') || id.includes('tailwind-merge')) {
              return 'utils';
            }
            
            // Icons
            if (id.includes('lucide-react') || id.includes('heroicons')) {
              return 'icons';
            }
            
            // Large libraries that should be separate
            if (id.includes('monaco-editor')) {
              return 'monaco';
            }
            
            // Everything else goes to vendor
            return 'vendor';
          }
          
          // Application code chunking
          if (id.includes('/src/')) {
            // Components that are likely to be shared
            if (id.includes('/components/ui/')) {
              return 'ui-components';
            }
            
            // Pages/routes
            if (id.includes('/pages/') || id.includes('/routes/')) {
              return 'pages';
            }
            
            // Services and utilities
            if (id.includes('/services/') || id.includes('/utils/') || id.includes('/lib/')) {
              return 'app-utils';
            }
          }
        },
        
        // Optimize chunk names
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? 
            chunkInfo.facadeModuleId.split('/').pop().replace('.js', '') : 'chunk';
          return `assets/[name]-[hash].js`;
        },
        
        // Optimize asset names
        assetFileNames: (assetInfo) => {
          const extType = assetInfo.name.split('.').pop();
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            return `assets/images/[name]-[hash][extname]`;
          }
          if (/woff|woff2|eot|ttf|otf/i.test(extType)) {
            return `assets/fonts/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        }
      },
      
      // External dependencies (don't bundle these)
      external: (id) => {
        // Keep some large dependencies external if they're not critical
        return false; // Bundle everything for now, can be adjusted based on needs
      }
    },
    
    // Terser options for better minification
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.warn'], // Remove specific console methods
        passes: 2 // Multiple passes for better compression
      },
      mangle: {
        safari10: true // Fix Safari 10 issues
      },
      format: {
        comments: false // Remove comments
      }
    }
  },
  
  // Optimize dependency pre-bundling
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@radix-ui/react-accordion',
      '@radix-ui/react-alert-dialog',
      '@radix-ui/react-avatar',
      '@radix-ui/react-checkbox',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      'lucide-react',
      'clsx',
      'class-variance-authority',
      'tailwind-merge'
    ],
    exclude: [] // Don't exclude any dependencies from pre-bundling
  },
  
  css: {
    // CSS code splitting
    codeSlice: true,
    // PostCSS optimizations will be handled by Tailwind
  }
})

