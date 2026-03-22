import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sand: {
          50:  "#fdfcfa",
          100: "#f9f6f1",
          200: "#f2ede4",
          300: "#e5ddd0",
        },
        rose: {
          100: "#fdf0ee",
          200: "#f9dbd7",
          400: "#e8a99f",
          500: "#d97e73",
          600: "#c4675b",
        },
        stone: {
          400: "#a09080",
          600: "#6b5d52",
          900: "#2c201a",
        },
      },
      fontFamily: {
        sans:  ["var(--font-inter)",    "system-ui", "sans-serif"],
        serif: ["var(--font-cormorant)", "Georgia",   "serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
