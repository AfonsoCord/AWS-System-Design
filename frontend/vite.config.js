import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api' : {
        target:'http://django-env2.eba-k8qtghv3.us-east-1.elasticbeanstalk.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/,''),
      }
    }
  }
})
