/** @type {import('tailwindcss').Config} */
// Locked design tokens — see docs/DESIGN.md ("Paper Atlas", v3).
// Concept: the catalog is paper; the telescope is night.
// Chrome is light paper + ink + gold-ink accents. The two 3D canvases
// (Graph3DExplorer, Stack3DVisualizer) are the ONLY sanctioned dark surfaces.
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Warm paper surface ladder (canvas -> cards -> wells)
        paper: {
          50: '#fffdf7',   // cards, raised surfaces
          100: '#f7f3e8',  // page canvas
          200: '#efe9d8',  // wells, inputs, insets
          300: '#e0d8c2',  // hairline borders
          400: '#c9bea2',  // strong borders, tracks
          500: '#a99a78',
          600: '#8a7c5e',
          700: '#6b6049',
          800: '#4a4331',
          900: '#2b2619',
        },
        // Starlight gold — as ink on paper (deepened for contrast)
        star: {
          200: '#ffe3a8',
          300: '#ffd88a',
          400: '#f7c34d',
          500: '#f2b13d',  // solid CTA surfaces
          600: '#d99a22',
          700: '#a3690d',  // gold ink on paper (text/icons)
          800: '#7d5108',
          900: '#3d2f0d',
          950: '#241c07',
        },
        // Secondary telemetry accent (dark canvases only)
        ion: {
          300: '#7ee0d2',
          400: '#4cc9b8',
          500: '#2fa898',
          600: '#238578',
          700: '#1d6e63',
          900: '#0c2f2b',
          950: '#08201d',
        },
      },
      fontFamily: {
        // Plate-atlas serif display; Instrument Sans body; JetBrains Mono data
        display: ['"Fraunces"', 'Georgia', 'serif'],
        sans: ['"Instrument Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      borderRadius: {
        // Three-step vocabulary: 6 / 10 / 14 (+ pills)
        sm: '4px',
        DEFAULT: '6px',
        md: '7px',
        lg: '8px',
        xl: '10px',
        '2xl': '14px',
        '3xl': '14px',
      },
      letterSpacing: {
        catalog: '0.14em',
      },
    },
  },
  plugins: [],
}
