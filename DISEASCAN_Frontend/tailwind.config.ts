import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
          950: '#030712',
        },
      },
      animation: {
        'pulse-fade': 'pulse-fade 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'typing': 'typing 0.7s steps(1, end)',
      },
      keyframes: {
        'pulse-fade': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        'typing': {
          'from': { width: '0' },
          'to': { width: '100%' },
        },
      },
    },
  },
} as const satisfies Config
