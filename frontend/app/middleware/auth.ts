export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()

  if (to.path === "/login") return

  if (!auth.autenticado) {
    return navigateTo("/login")
  }

  if (to.path.startsWith("/admin") && auth.perfil !== "admin_ia16") {
    return navigateTo("/dashboard")
  }
})
