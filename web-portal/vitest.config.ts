/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { configDefaults } from "vitest/config";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test-setup.ts",
    coverage: {
      provider: "v8",
      // json-summary is required for the coverage dashboard
      reporter: ["text", "json", "html", "json-summary"],
      reportsDirectory: "./coverage",
      exclude: [
        ...configDefaults.exclude,
        "postcss.config.js",
        "tailwind.config.js",
        "eslint.config.js",
        "vite.config.ts",
        "vitest.config.ts",
        "src/main.tsx", // Entry point is usually excluded from unit tests
        "src/vite-env.d.ts",
        "src/models/**", // Exclude TypeScript interfaces
        "public/**", // Exclude static assets
      ],
    },
  },
});
