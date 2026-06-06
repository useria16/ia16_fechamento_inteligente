<template>
  <div>
    <h1 class="text-xl font-semibold text-gray-900 mb-2">Dashboard</h1>
    <p class="text-gray-500 text-sm mb-8">Bem-vindo, {{ auth.sessao?.user?.email }}</p>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl">
      <NuxtLink
        v-for="item in menu"
        :key="item.to"
        :to="item.to"
        class="bg-white rounded-lg shadow p-5 hover:shadow-md transition-shadow"
      >
        <p class="font-medium text-gray-900">{{ item.titulo }}</p>
        <p class="text-sm text-gray-500 mt-1">{{ item.descricao }}</p>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" })

const auth = useAuthStore()

const menu = computed(() => {
  const itens = [
    { to: "/fechamentos", titulo: "Fechamentos", descricao: "Gerenciar fechamentos financeiros" },
    { to: "/divergencias", titulo: "Divergências", descricao: "Revisar divergências encontradas" },
  ]

  if (auth.perfil === "admin_ia16") {
    itens.push(
      { to: "/admin/empresas", titulo: "Empresas", descricao: "Cadastro de empresas clientes" },
      { to: "/admin/usuarios", titulo: "Usuários", descricao: "Gerenciar usuários da plataforma" },
    )
  }

  return itens
})
</script>
