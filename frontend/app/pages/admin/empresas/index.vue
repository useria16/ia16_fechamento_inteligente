<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-semibold text-gray-900">Empresas</h1>
      <NuxtLink
        to="/admin/empresas/nova"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700"
      >
        Nova empresa
      </NuxtLink>
    </div>

    <div v-if="carregando" class="text-sm text-gray-500">Carregando...</div>

    <div v-else-if="erro" class="text-sm text-red-600">{{ erro }}</div>

    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700">CNPJ</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Status</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="empresa in empresas" :key="empresa.id">
            <td class="px-4 py-3 text-gray-900">{{ empresa.nome }}</td>
            <td class="px-4 py-3 text-gray-600">{{ empresa.cnpj }}</td>
            <td class="px-4 py-3">
              <span
                :class="empresa.status === 'ativa' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
                class="px-2 py-0.5 rounded-full text-xs font-medium"
              >
                {{ empresa.status }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <NuxtLink :to="`/admin/empresas/${empresa.id}`" class="text-blue-600 hover:underline">Editar</NuxtLink>
            </td>
          </tr>
          <tr v-if="empresas.length === 0">
            <td colspan="4" class="px-4 py-6 text-center text-gray-400">Nenhuma empresa cadastrada</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" })

const api = useApi()
const empresas = ref<any[]>([])
const carregando = ref(true)
const erro = ref<string | null>(null)

onMounted(async () => {
  try {
    empresas.value = await api.get("/api/empresas")
  } catch (e: any) {
    erro.value = e.message
  } finally {
    carregando.value = false
  }
})
</script>
