import defaultTheme from 'tailwindcss/defaultTheme'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter var', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          600: '#2563EB',
          800: '#1e40af',
        },
        accent: '#10B981',
        danger: '#EF4444',
        surface: {
          dark: '#0F172A',
          light: '#0B1220',
        },
        text: {
          primary: '#E6EEF8',
          muted: '#94A3B8',
        },
        border: {
          default: '#1F2A44',
        },
      },
      fontSize: {
        h1: ['36px', { lineHeight: '48px', fontWeight: '600' }],
        h2: ['28px', { lineHeight: '36px', fontWeight: '600' }],
        h3: ['20px', { lineHeight: '28px', fontWeight: '600' }],
        base: ['16px', { lineHeight: '24px', fontWeight: '400' }],
        sm: ['13px', { lineHeight: '20px', fontWeight: '400' }],
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'base': '16px',
        'lg': '20px',
        'xl': '24px',
        '2xl': '32px',
        '3xl': '40px',
        '4xl': '48px',
      },
      borderRadius: {
        sm: '0.375rem',
        md: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        soft: '0 12px 30px rgba(2, 6, 23, 0.6)',
        lg: '0 10px 25px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        fadeIn: 'fadeIn 300ms ease-out',
        slideUp: 'slideUp 300ms ease-out',
      },
      keyframes: {
        fadeIn: {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        },
        slideUp: {
          'from': { opacity: '0', transform: 'translateY(8px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      transitionTimingFunction: {
        smooth: 'cubic-bezier(.2,.9,.2,1)',
      },
      transitionDuration: {
        fast: '120ms',
        standard: '240ms',
        slow: '420ms',
      },
    },
  },
  plugins: [],
}
