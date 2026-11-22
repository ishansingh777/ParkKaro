import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        parkGreen: "#10B981",
        parkBlue: "#2563EB",
        parkRed: "#EF4444",
      },
    },
  },
  plugins: [],
};
export default config;
