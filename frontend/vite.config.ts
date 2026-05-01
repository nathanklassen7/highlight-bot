import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  server: {
    proxy: {
      "/api": "http://localhost:8080",
      "/clips/file": "http://localhost:8080",
      "/clips/snapshot": "http://localhost:8080",
      "/trim": "http://localhost:8080",
      "/socket.io": { target: "http://localhost:8080", ws: true },
    },
  },
  esbuild: {
    jsx: "automatic",
    loader: "tsx",
  },
});
