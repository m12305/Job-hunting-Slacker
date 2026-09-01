import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 开发时将 /api 代理到后端 FastAPI。
// 默认 8000；若后端换端口，可设环境变量 VITE_API_TARGET（如 VITE_API_TARGET=http://127.0.0.1:8001 npm run dev）。
// 注意：请勿直接改 target 为不存在的端口，否则页面请求会 500。
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    host: '127.0.0.1',
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          echarts: ['echarts'],
        },
      },
    },
  },
})