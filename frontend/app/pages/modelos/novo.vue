<template>
  <div class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink to="/modelos" class="text-sm text-gray-500 hover:text-gray-700">← Modelos</NuxtLink>
      <h1 class="text-xl font-semibold text-gray-900">Novo modelo de arquivo</h1>
    </div>

    <form class="bg-white rounded-lg shadow p-6 space-y-5" @submit.prevent="salvar">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
        <input
          v-model="form.nome"
          type="text"
          required
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ex: Extrato Bancário Bradesco"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de arquivo</label>
        <select
          v-model="form.tipo_arquivo"
          required
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Selecione...</option>
          <option value="extrato_bancario">Extrato bancário</option>
          <option value="relatorio_vendas">Relatório de vendas</option>
          <option value="relatorio_recebiveis">Relatório de recebíveis</option>
          <option value="planilha_interna">Planilha interna</option>
          <option value="taxas_adquirente">Taxas adquirente</option>
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

      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-gray-700">Mapeamento de colunas</label>
          <button type="button" class="text-xs text-blue-600 hover:underline" @click="adicionarColuna">+ Adicionar coluna</button>
        </div>
        <p class="text-xs text-gray-400 mb-3">Mapeie os campos padrão do sistema para os nomes de colunas do arquivo Excel.</p>
        <div class="space-y-2">
          <div v-for="(linha, idx) in colunas" :key="idx" class="flex items-center gap-2">
            <select
              v-model="linha.campo"
              class="flex-1 border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Campo padrão...</option>
              <option value="data">data</option>
              <option value="valor_bruto">valor_bruto</option>
              <option value="valor_liquido">valor_liquido</option>
              <option value="documento">documento</option>
              <option value="descricao">descricao</option>
              <option value="tipo">tipo</option>
              <option value="categoria">categoria</option>
              <option value="taxa">taxa</option>
            </select>
            <span class="text-gray-400">→</span>
            <input
              v-model="linha.coluna"
              type="text"
              placeholder="Nome no Excel"
              class="flex-1 border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button type="button" class="text-gray-400 hover:text-red-500" @click="removerColuna(idx)">✕</button>
          </div>
          <div v-if="colunas.length === 0" class="text-xs text-gray-400 italic">Nenhuma coluna mapeada.</div>
        </div>
      </div>

      <div v-if="erro" class="text-sm text-red-600">{{ erro }}</div>

      <div class="flex justify-end gap-3 pt-2">
        <NuxtLink to="/modelos" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">Cancelar</NuxtLink>
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

const form = ref({ nome: '', tipo_arquivo: '', empresa_id: '' })
const colunas = ref<{ campo: string; coluna: string }[]>([])
const salvando = ref(false)
const erro = ref<string | null>(null)

function adicionarColuna() {
  colunas.value.push({ campo: '', coluna: '' })
}

function removerColuna(idx: number) {
  colunas.value.splice(idx, 1)
}

async function salvar() {
  salvando.value = true
  erro.value = null

  const mapeamento: Record<string, string> = {}
  for (const linha of colunas.value) {
    if (linha.campo && linha.coluna) mapeamento[linha.campo] = linha.coluna
  }

  try {
    const corpo: Record<string, any> = {
      nome: form.value.nome,
      tipo_arquivo: form.value.tipo_arquivo,
      mapeamento_colunas: mapeamento,
    }
    if (auth.perfil === 'admin_ia16') corpo.empresa_id = form.value.empresa_id
    await api.post('/api/v1/modelos-arquivo', corpo)
    router.push('/modelos')
  } catch (e: any) {
    erro.value = e.message
  } finally {
    salvando.value = false
  }
}
</script>
