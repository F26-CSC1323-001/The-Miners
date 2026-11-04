// import { defineConfig } from 'vite'

// // https://vite.dev/config/
// export default defineConfig({
//   server: {
//     allowedHosts: ['taunt-trapper-uncolored.ngrok-free.dev', 'taunt-trapper-uncolored.ngrok-free.dev/api/video']
//   }
// })


import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:5000',
          changeOrigin: true,
          headers: { 'ngrok-skip-browser-warning': '1' },
      //  allowedHosts: ['taunt-trapper-uncolored.ngrok-free.dev', 'taunt-trapper-uncolored.ngrok-free.dev/api/video']
        },
      },
    },
  }
})
