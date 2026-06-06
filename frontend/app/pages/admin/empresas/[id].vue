<template>
  <div class="max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink to="/admin/empresas" class="text-gray-400 hover:text-gray-600">← Voltar</NuxtLink>
      <h1 class="text-xl font-semibold text-gray-900">Editar empresa</h1>
    </div>

    <div v-if="carregando" class="text-sm text-gray-500">Carregando...</div>

    <form v-else @submit.prevent="submeter" class="bg-white rounded-lg shadow p-6 space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
        <input
          v-model="form.nome"
          type="text"
          required
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">CNPJ</label>
        <input
          :value="empresa?.cnpj"
          type="text"
          disabled
          class="w-full border border-gray-200 rounded px-3 py-2 text-sm bg-gray-50 text-gray-400"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
        <select
          v-model="form.status"
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="ativa">Ativa</option>
          <option value="inativa">Inativa</option>
        </select>
      </div>

      <p v-if="erro" class="text-sm text-red-600">{{ erro }}</p>

      <div class="flex gap-3 pt-2">
        <button
          type="submit"
          :disabled="salvando"
          class="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {{ salvando ? "Salvando..." : "Salvar" }}
        </button>
        <NuxtLink to="/admin/empresas" class="px-4 py-2 rounded text-sm text-gray-600 hover:bg-gray-100">
          Cancelar
        </NuxtLink>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" })

const route = useRoute()
const api = useApi()
const empresa = ref<any>(null)
const carregando = ref(true)
const salvando = ref(false)
const erro = ref<string | null>(null)
const form = reactive({ nome: "", status: "ativa" })

onMounted(async () => {
  try {
    empresa.value = await api.get(`/api/empresas/${route.params.id}`)
    form.nome = empresa.value.nome
    form.status = empresa.value.status
  } catch (e: any) {
    erro.value = e.message
  } finally {
    carregando.value = false
  }
})

async function submeter() {
  salvando.value = true
  erro.value = null
  try {
    await api.patch(`/api/empresas/${route.params.id}`, form)
    navigateTo("/admin/empresas")
  } catch (e: any) {
    erro.value = e.message
  } finally {
    salvando.value = false
  }
}
</script>
