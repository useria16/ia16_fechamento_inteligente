<template>
  <div class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink to="/modelos" class="text-sm text-gray-500 hover:text-gray-700">← Modelos</NuxtLink>
      <h1 class="text-xl font-semibold text-gray-900">Editar modelo de arquivo</h1>
    </div>

    <div v-if="carregando" class="text-sm text-gray-500">Carregando...</div>

    <form v-else class="bg-white rounded-lg shadow p-6 space-y-5" @submit.prevent="salvar">
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
        <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de arquivo</label>
        <input
          :value="modelo?.tipo_arquivo"
          disabled
          class="w-full border border-gray-200 bg-gray-50 rounded px-3 py-2 text-sm text-gray-500"
        />
        <p class="text-xs text-gray-400 mt-1">O tipo não pode ser alterado após criação.</p>
      </div>

      <div class="flex items-center gap-2">
        <input id="ativo" v-model="form.ativo" type="checkbox" class="rounded" />
        <label for="ativo" class="text-sm text-gray-700">Modelo ativo</label>
      </div>

      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-gray-700">Mapeamento de colunas</label>
          <button type="button" class="text-xs text-blue-600 hover:underline" @click="adicionarColuna">+ Adicionar coluna</button>
        </div>
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

      <div v-if="erroMsg" class="text-sm text-red-600">{{ erroMsg }}</div>

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

const route = useRoute()
const router = useRouter()
const api = useApi()

const modelo = ref<any>(null)
const form = ref({ nome: '', ativo: true })
const colunas = ref<{ campo: string; coluna: string }[]>([])
const carregando = ref(true)
const salvando = ref(false)
const erroMsg = ref<string | null>(null)

onMounted(async () => {
  try {
    const res = await api.get<any>(`/api/v1/modelos-arquivo/${route.params.id}`)
    modelo.value = res.dados
    form.value = { nome: res.dados.nome, ativo: res.dados.ativo }
    colunas.value = Object.entries(res.dados.mapeamento_colunas ?? {}).map(([campo, coluna]) => ({
      campo,
      coluna: coluna as string,
    }))
  } catch (e: any) {
    erroMsg.value = e.message
  } finally {
    carregando.value = false
  }
})

function adicionarColuna() {
  colunas.value.push({ campo: '', coluna: '' })
}

function removerColuna(idx: number) {
  colunas.value.splice(idx, 1)
}

async function salvar() {
  salvando.value = true
  erroMsg.value = null

  const mapeamento: Record<string, string> = {}
  for (const linha of colunas.value) {
    if (linha.campo && linha.coluna) mapeamento[linha.campo] = linha.coluna
  }

  try {
    await api.patch(`/api/v1/modelos-arquivo/${route.params.id}`, {
      nome: form.value.nome,
      ativo: form.value.ativo,
      mapeamento_colunas: mapeamento,
    })
    router.push('/modelos')
  } catch (e: any) {
    erroMsg.value = e.message
  } finally {
    salvando.value = false
  }
}
</script>
