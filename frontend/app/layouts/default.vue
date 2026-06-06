<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-6">
        <span class="font-semibold text-gray-900">iA16 Fechamento</span>
        <NuxtLink to="/dashboard" class="text-sm text-gray-600 hover:text-gray-900">Dashboard</NuxtLink>
        <template v-if="auth.perfil === 'admin_ia16'">
          <NuxtLink to="/admin/empresas" class="text-sm text-gray-600 hover:text-gray-900">Empresas</NuxtLink>
          <NuxtLink to="/admin/usuarios" class="text-sm text-gray-600 hover:text-gray-900">Usuários</NuxtLink>
        </template>
      </div>
      <button
        class="text-sm text-gray-500 hover:text-gray-700"
        @click="auth.sair()"
      >
        Sair
      </button>
    </nav>
    <main class="p-6">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore()
</script>
