<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-semibold text-gray-900">Usuários</h1>
      <NuxtLink
        to="/admin/usuarios/novo"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700"
      >
        Novo usuário
      </NuxtLink>
    </div>

    <div v-if="carregando" class="text-sm text-gray-500">Carregando...</div>

    <div v-else-if="erro" class="text-sm text-red-600">{{ erro }}</div>

    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700">E-mail</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Perfil</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="usuario in usuarios" :key="usuario.id">
            <td class="px-4 py-3 text-gray-900">{{ usuario.nome }}</td>
            <td class="px-4 py-3 text-gray-600">{{ usuario.email }}</td>
            <td class="px-4 py-3 text-gray-600">{{ usuario.perfil }}</td>
            <td class="px-4 py-3">
              <span
                :class="usuario.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
                class="px-2 py-0.5 rounded-full text-xs font-medium"
              >
                {{ usuario.ativo ? "ativo" : "inativo" }}
              </span>
            </td>
          </tr>
          <tr v-if="usuarios.length === 0">
            <td colspan="4" class="px-4 py-6 text-center text-gray-400">Nenhum usuário cadastrado</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" })

const api = useApi()
const usuarios = ref<any[]>([])
const carregando = ref(true)
const erro = ref<string | null>(null)

onMounted(async () => {
  try {
    usuarios.value = await api.get("/api/usuarios")
  } catch (e: any) {
    erro.value = e.message
  } finally {
    carregando.value = false
  }
})
</script>
