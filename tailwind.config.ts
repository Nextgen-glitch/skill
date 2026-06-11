import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand red/white/blue on OLED black
        ink: {
          DEFAULT: "#0F0F23", // background
          soft: "#15152e",
          card: "#1a1a33",
        },
        brand: {
          blue: "#1d3a9e",
          "blue-bright": "#2f4fd6",
          red: "#e23b2e",
          "red-bright": "#ff4a3a",
          white: "#f8fafc",
        },
        cta: "#22c55e", // green — reserved for Book Now only
        border: "#2a2a4d",
      },
      fontFamily: {
        display: ["var(--font-righteous)", "system-ui", "sans-serif"],
        body: ["var(--font-poppins)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        "glow-red": "0 0 30px -5px rgba(226,59,46,0.55)",
        "glow-blue": "0 0 30px -5px rgba(47,79,214,0.55)",
        "glow-cta": "0 0 28px -4px rgba(34,197,94,0.6)",
      },
      keyframes: {
        floaty: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-12px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        floaty: "floaty 6s ease-in-out infinite",
        shimmer: "shimmer 2.5s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;
