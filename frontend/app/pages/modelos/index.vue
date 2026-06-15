<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-semibold text-gray-900">Modelos de Arquivo</h1>
      <NuxtLink
        to="/modelos/novo"
        class="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700"
      >
        Novo modelo
      </NuxtLink>
    </div>

    <div v-if="carregando" class="text-sm text-gray-500">Carregando...</div>

    <div v-else-if="erro" class="text-sm text-red-600">{{ erro }}</div>

    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Tipo de arquivo</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Colunas mapeadas</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Status</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="modelo in modelos" :key="modelo.id">
            <td class="px-4 py-3 text-gray-900">{{ modelo.nome }}</td>
            <td class="px-4 py-3 text-gray-600">{{ TIPOS_LABEL[modelo.tipo_arquivo] ?? modelo.tipo_arquivo }}</td>
            <td class="px-4 py-3 text-gray-600">{{ Object.keys(modelo.mapeamento_colunas ?? {}).length }} campos</td>
            <td class="px-4 py-3">
              <span
                :class="modelo.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
                class="px-2 py-0.5 rounded-full text-xs font-medium"
              >
                {{ modelo.ativo ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <NuxtLink :to="`/modelos/${modelo.id}`" class="text-blue-600 hover:underline">Editar</NuxtLink>
            </td>
          </tr>
          <tr v-if="modelos.length === 0">
            <td colspan="5" class="px-4 py-6 text-center text-gray-400">Nenhum modelo cadastrado</td>
          </tr>
        </tbody>
      </table>

      <div v-if="paginacao && paginacao.total_paginas > 1" class="px-4 py-3 border-t border-gray-100 flex items-center gap-3 text-sm text-gray-600">
        <button :disabled="pagina === 1" class="disabled:opacity-40" @click="pagina--">Anterior</button>
        <span>{{ pagina }} / {{ paginacao.total_paginas }}</span>
        <button :disabled="pagina >= paginacao.total_paginas" class="disabled:opacity-40" @click="pagina++">Próxima</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const TIPOS_LABEL: Record<string, string> = {
  extrato_bancario: 'Extrato bancário',
  relatorio_vendas: 'Relatório de vendas',
  relatorio_recebiveis: 'Relatório de recebíveis',
  planilha_interna: 'Planilha interna',
  taxas_adquirente: 'Taxas adquirente',
  outro: 'Outro',
}

const api = useApi()
const modelos = ref<any[]>([])
const paginacao = ref<any>(null)
const carregando = ref(true)
const erro = ref<string | null>(null)
const pagina = ref(1)

async function carregar() {
  carregando.value = true
  erro.value = null
  try {
    const res = await api.get<any>(`/api/v1/modelos-arquivo?pagina=${pagina.value}&limite=20`)
    modelos.value = res.dados
    paginacao.value = res.paginacao
  } catch (e: any) {
    erro.value = e.message
  } finally {
    carregando.value = false
  }
}

watch(pagina, carregar)
onMounted(carregar)
</script>
