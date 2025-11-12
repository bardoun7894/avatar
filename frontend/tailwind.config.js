/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      screens: {
        'xs': '375px',
        'portrait': {'raw': '(orientation: portrait)'},
        'landscape': {'raw': '(orientation: landscape)'},
        'tall': {'raw': '(min-aspect-ratio: 9/16)'},  // For tall portrait screens like event displays
        'wide': {'raw': '(min-aspect-ratio: 16/9)'},  // For wide landscape screens
      },
      colors: {
        primary: '#0b73da',
        'background-light': '#f5f7f8',
        'background-dark': '#101922',
      },
      fontFamily: {
        display: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg: '0.5rem',
        xl: '1rem',
        '2xl': '1.5rem',
        full: '9999px',
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
