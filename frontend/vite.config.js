import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// The frontend calls "/api/..." and Vite forwards it to the FastAPI backend.
// Use 127.0.0.1 (not "localhost"): on Windows with Node 17+ "localhost" can
// resolve to IPv6 (::1) while uvicorn only listens on IPv4, which gives
// "connection refused" even though the backend is running.
const BACKEND_URL = process.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: BACKEND_URL,
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 4173,
    proxy: {
      "/api": {
        target: BACKEND_URL,
        changeOrigin: true,
      },
    },
  },
});
