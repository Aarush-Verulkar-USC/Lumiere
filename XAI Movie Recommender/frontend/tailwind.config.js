/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Figtree', 'sans-serif'],
      },
      colors: {
        // Dark theme palette
        navy: {
          50: '#e6eaf2',
          100: '#ccd5e5',
          200: '#99abcb',
          300: '#6681b1',
          400: '#335797',
          500: '#192655',  // Main dark navy background
          600: '#141f44',
          700: '#101833',
          800: '#0c1022',
          900: '#080811',
        },
        // Primary blue
        primary: {
          50: '#e9f2fc',
          100: '#d3e5f9',
          200: '#a7cbf3',
          300: '#7bb1ed',
          400: '#4f97e7',
          500: '#3876BF',  // Main bright blue
          600: '#2d5e99',
          700: '#224773',
          800: '#172f4d',
          900: '#0c1826',
        },
        // Accent gold/orange
        accent: {
          50: '#fdf6ed',
          100: '#fbeddb',
          200: '#f7dbb7',
          300: '#f3c993',
          400: '#efb76f',
          500: '#E1AA74',  // Main gold/orange
          600: '#b4885d',
          700: '#876646',
          800: '#5a442f',
          900: '#2d2217',
        },
        // Light cream
        cream: {
          50: '#FFFFFF',
          100: '#FEFDF9',
          200: '#F3F0CA',  // Main cream for text/highlights
          300: '#ebe8b7',
          400: '#e3e0a4',
          500: '#dbd891',
          600: '#afa974',
          700: '#837f57',
          800: '#57543a',
          900: '#2c2a1d',
        },
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
        'blob': '30% 70% 70% 30% / 30% 30% 70% 70%',
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'soft-lg': '0 10px 40px -10px rgba(0, 0, 0, 0.1)',
        'inner-soft': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'bounce-soft': 'bounceSoft 2s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(-5%)' },
          '50%': { transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [],
}
