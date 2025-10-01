/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      // Landscape-inspired color palette with semantic naming
      colors: {
        // Primary greens - representing growth and nature
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',  // Main brand green
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16'
        },
        
        // Secondary blues - representing water and sky
        secondary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',  // Main secondary blue
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554'
        },

        // Nature theme - various natural elements
        nature: {
          50: '#f7fee7',
          100: '#ecfccb',
          200: '#d9f99d',
          300: '#bef264',
          400: '#a3e635',
          500: '#84cc16',  // Fresh green
          600: '#65a30d',
          700: '#4d7c0f',
          800: '#365314',
          900: '#1a2e05'
        },

        // Earth theme - soil, bark, stone
        earth: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',  // Warm earth tone
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917'
        },

        // Water theme - blues and aquas
        water: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',  // Clear water blue
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63'
        },

        // Stone theme - grays and neutrals
        stone: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',  // Natural stone
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917'
        }
      },

      // Comprehensive spacing scale using harmonic progression
      spacing: {
        'xs': '0.25rem',    // 4px
        'sm': '0.5rem',     // 8px
        'md': '1rem',       // 16px
        'lg': '1.5rem',     // 24px
        'xl': '2rem',       // 32px
        '2xl': '3rem',      // 48px
        '3xl': '4rem',      // 64px
        '4xl': '6rem',      // 96px
        '5xl': '8rem',      // 128px
      },

      // Typography system with Inter font family
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Georgia', 'serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },

      // Enhanced border radius scale
      borderRadius: {
        'none': '0',
        'xs': '0.125rem',   // 2px
        'sm': '0.25rem',    // 4px
        'DEFAULT': '0.5rem', // 8px
        'md': '0.75rem',    // 12px
        'lg': '1rem',       // 16px
        'xl': '1.5rem',     // 24px
        '2xl': '2rem',      // 32px
        'full': '9999px',
      },

      // Custom shadows for landscape aesthetics
      boxShadow: {
        'landscape-soft': '0 2px 8px rgba(34, 197, 94, 0.1)',
        'landscape-medium': '0 4px 16px rgba(34, 197, 94, 0.15)',
        'landscape-hard': '0 8px 32px rgba(34, 197, 94, 0.2)',
        'water-soft': '0 2px 8px rgba(6, 182, 212, 0.1)',
        'earth-soft': '0 2px 8px rgba(120, 113, 108, 0.1)',
      },

      // Animation and transitions
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-gentle': 'bounceGentle 2s infinite',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },

      // Container sizes for responsive layouts
      container: {
        center: true,
        padding: '1rem',
        screens: {
          'narrow': '800px',
          'DEFAULT': '1200px',
          'wide': '1400px',
        },
      },
    },
  },
  plugins: [],
};