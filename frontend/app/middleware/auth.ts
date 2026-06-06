export default defineNuxtRouteMiddleware((to) => {
  if (!import.meta.client) return

  const auth = useAuthStore()

  if (to.path === "/login") return

  if (!auth.autenticado) {
    return navigateTo("/login")
  }

  if (to.path.startsWith("/admin") && auth.perfil !== "admin_ia16") {
    return navigateTo("/dashboard")
  }
})
