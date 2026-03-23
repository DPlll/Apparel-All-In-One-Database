import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        vintage: {
          50:  "#FAF6EE",
          100: "#F3EBD8",
          200: "#E3D4B5",
          300: "#CDB990",
        },
        terra: {
          100: "#FCE8DF",
          200: "#F4C5AF",
          400: "#D4724A",
          500: "#B85835",
          600: "#8F4226",
        },
        drift: {
          400: "#9B8870",
          600: "#5E4A38",
          900: "#271811",
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
