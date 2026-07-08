export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  future: { compatibilityVersion: 4 },

  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt"],

  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL ?? "",
      supabaseUrl: process.env.NUXT_PUBLIC_SUPABASE_URL || "",
      supabaseAnonKey: process.env.NUXT_PUBLIC_SUPABASE_ANON_KEY || "",
      supabaseSchema: process.env.NUXT_PUBLIC_SUPABASE_SCHEMA || "ia16_fechamento_dev",
    },
  },

  routeRules: {
    // NUXT_INTERNAL_API_URL = http://backend:8000 em Docker, http://127.0.0.1:8000 em dev local
    '/api/**': { proxy: `${process.env.NUXT_INTERNAL_API_URL ?? 'http://127.0.0.1:8000'}/api/**` },
  },

  typescript: {
    strict: true,
  },

  devtools: { enabled: false },
})
