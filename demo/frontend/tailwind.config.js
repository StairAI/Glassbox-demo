/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#0a0e1a',
          secondary: '#141b2d',
          node: '#1a2332',
        },
        accent: {
          green: '#00ff88',
          red: '#ff4444',
          yellow: '#ffbb00',
          blue: '#00aaff',
        },
        text: {
          primary: '#e0e6ed',
          secondary: '#8b95a8',
          dim: '#5a6477',
        },
        signal: {
          buy: '#00ff88',
          sell: '#ff4444',
          hold: '#ffbb00',
        },
        border: {
          active: '#00ff88',
          inactive: '#2a3447',
        },
      },
    },
  },
  plugins: [],
}
