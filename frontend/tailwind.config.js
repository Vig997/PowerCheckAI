/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101828",
        panel: "#f8fafc",
        safe: "#16a34a",
        borderline: "#d97706",
        unsafe: "#dc2626",
      },
      boxShadow: {
        soft: "0 18px 42px rgba(15, 23, 42, 0.24), 0 4px 14px rgba(15, 23, 42, 0.14)",
        "soft-dark": "0 18px 42px rgba(34, 211, 238, 0.08), 0 4px 16px rgba(0, 0, 0, 0.42)",
      },
    },
  },
  plugins: [],
};
