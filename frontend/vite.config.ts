import path from 'node:path'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const envDir = path.resolve(__dirname, '..')
  const env = loadEnv(mode, envDir, '')
  const devPort = Number(env.VITE_DEV_PORT || '5177')
  const apiProxyTarget = env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8300'

  return {
    envDir,
    plugins: [vue()],
    server: {
      port: devPort,
      proxy: {
        '/api': apiProxyTarget,
        '/uploads': apiProxyTarget,
      },
    },
    build: {
      outDir: path.resolve(__dirname, '../app/static'),
      emptyOutDir: true,
    },
  }
})
