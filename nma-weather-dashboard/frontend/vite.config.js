import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // lets the dev server call the FastAPI backend without CORS pain
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
