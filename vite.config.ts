import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  server: {
    // el proxy del preview apunta a IPv4; sin esto vite escucha solo en ::1
    host: "127.0.0.1",
    allowedHosts: true,
  },
  build: {
    sourcemap: false,
  },
});
