<template>
  <div class="max-w-lg">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink to="/fontes" class="text-sm text-gray-500 hover:text-gray-700">← Fontes</NuxtLink>
      <h1 class="text-xl font-semibold text-gray-900">Nova fonte de dados</h1>
    </div>

    <form class="bg-white rounded-lg shadow p-6 space-y-4" @submit.prevent="salvar">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
        <input
          v-model="form.nome"
          type="text"
          required
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ex: Extrato Bradesco"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
        <select
          v-model="form.tipo"
          required
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Selecione...</option>
          <option value="excel_manual">Excel manual</option>
          <option value="banco">Banco</option>
          <option value="adquirente">Adquirente</option>
          <option value="erp">ERP</option>
          <option value="google_drive">Google Drive</option>
          <option value="outro">Outro</option>
        </select>
      </div>

      <div v-if="auth.perfil === 'admin_ia16'">
        <label class="block text-sm font-medium text-gray-700 mb-1">ID da empresa</label>
        <input
          v-model="form.empresa_id"
          type="text"
          required
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="UUID da empresa"
        />
      </div>

      <div v-if="erro" class="text-sm text-red-600">{{ erro }}</div>

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

const api = useApi()
const auth = useAuthStore()
const router = useRouter()

const form = ref({ nome: '', tipo: '', empresa_id: '' })
const salvando = ref(false)
const erro = ref<string | null>(null)

async function salvar() {
  salvando.value = true
  erro.value = null
  try {
    const corpo: Record<string, any> = { nome: form.value.nome, tipo: form.value.tipo }
    if (auth.perfil === 'admin_ia16') corpo.empresa_id = form.value.empresa_id
    await api.post('/api/v1/fontes-dados', corpo)
    router.push('/fontes')
  } catch (e: any) {
    erro.value = e.message
  } finally {
    salvando.value = false
  }
}
</script>
