/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#07090d",
        panel: "#0d1117",
        border: "#1c232d",
        amberAccent: "#f5a524",
        upGreen: "#2ee6a6",
        downRed: "#ff4d5e",
        textPrimary: "#e8edf3",
        textMuted: "#7d8794",
      },
      fontFamily: {
        display: ['"Inter Tight"', '"Space Grotesk"', "sans-serif"],
        sans: ['"Inter"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
