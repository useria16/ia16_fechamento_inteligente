<template>
  <div class="max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink to="/fontes" class="text-sm text-gray-500 hover:text-gray-700">← Fontes</NuxtLink>
      <h1 class="text-xl font-semibold text-gray-900">Editar fonte de dados</h1>
    </div>

    <div v-if="carregando" class="text-sm text-gray-500">Carregando...</div>

    <form v-else class="bg-white rounded-lg shadow p-6 space-y-4" @submit.prevent="salvar">
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
        <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
        <input
          :value="fonte?.tipo"
          disabled
          class="w-full border border-gray-200 bg-gray-50 rounded px-3 py-2 text-sm text-gray-500"
        />
        <p class="text-xs text-gray-400 mt-1">O tipo não pode ser alterado após criação.</p>
      </div>

      <div class="flex items-center gap-2">
        <input id="ativo" v-model="form.ativo" type="checkbox" class="rounded" />
        <label for="ativo" class="text-sm text-gray-700">Fonte ativa</label>
      </div>

      <div v-if="erroMsg" class="text-sm text-red-600">{{ erroMsg }}</div>

      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink to="/fontes" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">Cancelar</NuxtLink>
        <button
          type="submit"
          :disabled="salvando"
          class="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {{ salvando ? 'Salvando...' : 'Salvar' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const api = useApi()

const fonte = ref<any>(null)
const form = ref({ nome: '', ativo: true })
const carregando = ref(true)
const salvando = ref(false)
const erroMsg = ref<string | null>(null)

onMounted(async () => {
  try {
    const res = await api.get<any>(`/api/v1/fontes-dados/${route.params.id}`)
    fonte.value = res.dados
    form.value = { nome: res.dados.nome, ativo: res.dados.ativo }
  } catch (e: any) {
    erroMsg.value = e.message
  } finally {
    carregando.value = false
  }
})

async function salvar() {
  salvando.value = true
  erroMsg.value = null
  try {
    await api.patch(`/api/v1/fontes-dados/${route.params.id}`, form.value)
    router.push('/fontes')
  } catch (e: any) {
    erroMsg.value = e.message
  } finally {
    salvando.value = false
  }
}
</script>
