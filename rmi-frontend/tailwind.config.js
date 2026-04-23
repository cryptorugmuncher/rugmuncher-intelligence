/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'crypto-dark': '#0a0a0f',
        'crypto-card': '#12121a',
        'crypto-border': '#1e1e2e',
        'neon-green': '#00ff88',
        'neon-blue': '#00d4ff',
        'neon-purple': '#8b5cf6',
        'neon-red': '#ff3366',
        'neon-yellow': '#ffcc00',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
