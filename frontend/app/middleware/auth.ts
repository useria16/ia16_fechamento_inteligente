export default defineNuxtRouteMiddleware((to) => {
  if (!import.meta.client) return

  const auth = useAuthStore()

  if (to.path === "/login") return

  if (!auth.autenticado) {
    return navigateTo("/login")
  }

  if (auth.trocaSenhaObrigatoria && to.path !== "/alterar-senha") {
    return navigateTo("/alterar-senha")
  }

})
