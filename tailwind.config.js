/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.{html,js,svg}", "./templates/**/*.{html,js,svg}"],
  theme: {
    fontFamily: {
      'sans': ["'Inter'", 'sans-serif'],
    },
    extend: {
      fontFamily: {
        'ibm-mono': ["'IBM Plex Mono'", 'monospace'],
      },
      colors: {
        'primary-50': '#F0F4F8',
        'primary-100': '#D9E2EC',
        'primary-200': '#BCCCDC',
        'primary-300': '#9FB3C8',
        'primary-400': '#829AB1',
        'primary-500': '#627D98',
        'primary-600': '#486581',
        'primary-700': '#334E68',
        'primary-800': '#243B53',
        'primary-900': '#102A43'
      }
    },
  },
  plugins: [],
}
