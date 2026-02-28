/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html'
  ],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Fraunces', 'serif'],
        body: ['Manrope', 'sans-serif']
      },
      colors: {
        ink: '#1f1b16',
        sand: '#f6f1e8',
        oat: '#ece4d5',
        bronze: '#9f7a35',
        mist: '#efeae1'
      },
      boxShadow: {
        card: '0 10px 35px -15px rgba(31, 27, 22, 0.35)'
      }
    }
  },
  plugins: [require('@tailwindcss/typography')]
}
