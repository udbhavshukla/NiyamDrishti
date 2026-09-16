/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom 4-color authority brand palette
        'brand-navy': '#0A2947',
        'brand-cream': '#F3E4C9',
        'brand-sage': '#D3D4C0',
        'brand-bronze': '#8B5E3C',

        // Mandatory statutory semantic status colors
        compliant: {
          DEFAULT: '#16a34a', // green-600
          light: '#f0fdf4',   // green-50
          border: '#bbf7d0',  // green-200
          dark: '#15803d',    // green-700
        },
        violation: {
          DEFAULT: '#dc2626', // red-600
          light: '#fef2f2',   // red-50
          border: '#fecaca',  // red-200
          dark: '#b91c1c',    // red-700
        },
        review: {
          DEFAULT: '#d97706', // amber-600
          light: '#fffbeb',   // amber-50
          border: '#fde68a',  // amber-200
          dark: '#b45309',    // amber-700
        },
        processing: {
          DEFAULT: '#2563eb', // blue-600
          light: '#eff6ff',   // blue-50
          border: '#bfdbfe',  // blue-200
          dark: '#1d4ed8',    // blue-700
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      }
    },
  },
  plugins: [],
}
