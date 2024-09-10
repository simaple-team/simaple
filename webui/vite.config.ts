import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import { copyFile, mkdir } from "node:fs/promises";
import path from "node:path";

// https://vitejs.dev/config/
export default defineConfig({
  optimizeDeps: { exclude: ["pyodide"] },
  plugins: [
    react(),
    {
      name: "vite-plugin-pyodide",
      generateBundle: async () => {
        const assetsDir = "dist/assets";
        await mkdir(assetsDir, { recursive: true });
        const files = [
          "pyodide-lock.json",
          "pyodide.asm.js",
          "pyodide.asm.wasm",
          "python_stdlib.zip",
        ];
        for (const file of files) {
          await copyFile(
            path.join("node_modules/pyodide", file),
            path.join(assetsDir, file),
          );
        }
      },
    },
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
