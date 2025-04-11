/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#4299e1',
          DEFAULT: '#3182ce',
          dark: '#2c5282',
        },
        secondary: {
          light: '#9ae6b4',
          DEFAULT: '#68d391',
          dark: '#38a169',
        },
        accent: {
          light: '#faf089',
          DEFAULT: '#f6e05e',
          dark: '#d69e2e',
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        heading: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
} 