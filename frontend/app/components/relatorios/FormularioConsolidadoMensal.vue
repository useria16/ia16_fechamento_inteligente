<template>
  <div class="bg-white rounded-xl border border-slate-200 p-6 space-y-6">

    <!-- Cabeçalho -->
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center shrink-0">
        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <div>
        <p class="text-sm font-semibold text-slate-800">Consolidado Mensal</p>
        <p class="text-xs text-slate-500 mt-0.5">
          Gera uma planilha Excel com as conciliações do mês selecionado.
        </p>
      </div>
    </div>

    <!-- Formulário -->
    <form class="space-y-4" @submit.prevent="onSubmit">

      <!-- Mês + Ano -->
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-600">Mês <span class="text-red-400">*</span></label>
          <select
            v-model="form.mes"
            class="w-full rounded-lg border px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="erros.mes ? 'border-red-400' : 'border-slate-200'"
          >
            <option v-for="m in meses" :key="m.valor" :value="m.valor">{{ m.label }}</option>
          </select>
          <p v-if="erros.mes" class="text-xs text-red-500">{{ erros.mes }}</p>
        </div>

        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-600">Ano <span class="text-red-400">*</span></label>
          <select
            v-model="form.ano"
            class="w-full rounded-lg border px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="erros.ano ? 'border-red-400' : 'border-slate-200'"
          >
            <option v-for="a in anos" :key="a" :value="a">{{ a }}</option>
          </select>
          <p v-if="erros.ano" class="text-xs text-red-500">{{ erros.ano }}</p>
        </div>
      </div>

      <!-- Modelo de conciliação — fixo nesta versão -->
      <div class="space-y-1">
        <label class="block text-xs font-medium text-slate-600">Modelo de conciliação</label>
        <p class="text-sm text-slate-700 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
          Extrato Anotado
        </p>
      </div>

      <!-- Empresa — apenas admin_ia16 -->
      <div v-if="isAdmin" class="space-y-1">
        <label class="block text-xs font-medium text-slate-600">Empresa <span class="text-red-400">*</span></label>
        <select
          v-model="form.empresa_id"
          :disabled="carregandoEmpresas"
          class="w-full rounded-lg border px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          :class="erros.empresa_id ? 'border-red-400' : 'border-slate-200'"
        >
          <option value="">
            {{ carregandoEmpresas ? 'Carregando empresas...' : empresas.length === 0 ? 'Nenhuma empresa disponível' : 'Selecione a empresa' }}
          </option>
          <option v-for="e in empresas" :key="e.id" :value="e.id">{{ e.nome }}</option>
        </select>
        <p v-if="erros.empresa_id" class="text-xs text-red-500">{{ erros.empresa_id }}</p>
      </div>

      <!-- Feedback -->
      <div
        v-if="feedbackMensagem"
        :class="[
          'flex items-start gap-3 rounded-lg border px-4 py-3 text-sm',
          feedbackTipo === 'sucesso'
            ? 'bg-green-50 border-green-200 text-green-700'
            : 'bg-red-50 border-red-200 text-red-600',
        ]"
      >
        <svg class="w-4 h-4 mt-0.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path v-if="feedbackTipo === 'sucesso'" stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        </svg>
        <span>{{ feedbackMensagem }}</span>
      </div>

      <!-- Botão -->
      <div class="pt-1">
        <button
          type="submit"
          :disabled="baixando"
          :class="[
            'inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors',
            baixando
              ? 'text-slate-400 bg-slate-100 cursor-not-allowed'
              : 'text-white bg-blue-600 hover:bg-blue-700 cursor-pointer',
          ]"
        >
          <svg v-if="baixando" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          {{ baixando ? 'Gerando consolidado...' : 'Exportar consolidado mensal' }}
        </button>
      </div>

    </form>

    <!-- Informativo -->
    <div class="rounded-lg bg-slate-50 border border-slate-100 px-4 py-3 text-xs text-slate-500 space-y-1">
      <p class="font-medium text-slate-600">O consolidado inclui:</p>
      <ul class="list-disc list-inside space-y-0.5 pl-1">
        <li>Todas as conciliações aprovadas ou processadas do mês</li>
        <li>Resumo com totais do período</li>
        <li>Todos os lançamentos do mês em uma única planilha</li>
        <li>Lista dos dias incluídos com totais por dia</li>
        <li>Pendências e divergências do mês</li>
      </ul>
    </div>

  </div>
</template>

<script setup lang="ts">
import { consolidadoMensalSchema } from '~/schemas/relatorio.schema'
import type { ConsolidadoMensalForm } from '~/schemas/relatorio.schema'

const auth = useAuthStore()
const { baixando, erro, sucesso, baixarConsolidado, limparFeedback } = useConsolidadoMensal()
const { empresas, carregando: carregandoEmpresas, carregar: carregarEmpresas } = useEmpresas()

const isAdmin = computed(() => auth.perfil === 'admin_ia16')

const agora = new Date()
const form = reactive<ConsolidadoMensalForm>({
  ano: agora.getFullYear(),
  mes: agora.getMonth() + 1,
  tipo_conciliacao: 'extrato_anotado',
  empresa_id: undefined,
})

const erros = reactive<Partial<Record<keyof ConsolidadoMensalForm, string>>>({})
const feedbackMensagem = ref<string | null>(null)
const feedbackTipo = ref<'sucesso' | 'erro'>('sucesso')

onMounted(async () => {
  if (isAdmin.value) {
    await carregarEmpresas()
    // Pré-seleciona automaticamente se houver apenas uma empresa
    if (empresas.value.length === 1) {
      form.empresa_id = empresas.value[0].id
    }
  }
})

const meses = [
  { valor: 1, label: 'Janeiro' }, { valor: 2, label: 'Fevereiro' },
  { valor: 3, label: 'Março' }, { valor: 4, label: 'Abril' },
  { valor: 5, label: 'Maio' }, { valor: 6, label: 'Junho' },
  { valor: 7, label: 'Julho' }, { valor: 8, label: 'Agosto' },
  { valor: 9, label: 'Setembro' }, { valor: 10, label: 'Outubro' },
  { valor: 11, label: 'Novembro' }, { valor: 12, label: 'Dezembro' },
]

const anoAtual = agora.getFullYear()
const anos = Array.from({ length: 5 }, (_, i) => anoAtual - i)


function exibirFeedback(tipo: 'sucesso' | 'erro', mensagem: string) {
  feedbackTipo.value = tipo
  feedbackMensagem.value = mensagem
  setTimeout(() => {
    feedbackMensagem.value = null
    limparFeedback()
  }, 6000)
}

function validar(): boolean {
  Object.keys(erros).forEach(k => delete (erros as any)[k])

  const resultado = consolidadoMensalSchema.safeParse(form)
  if (!resultado.success) {
    for (const issue of resultado.error.issues) {
      const campo = issue.path[0] as keyof ConsolidadoMensalForm
      if (campo && !erros[campo]) erros[campo] = issue.message
    }
    return false
  }

  if (isAdmin.value && !form.empresa_id?.trim()) {
    erros.empresa_id = 'Selecione uma empresa para exportar.'
    return false
  }

  return true
}

async function onSubmit() {
  if (!validar()) return

  const ok = await baixarConsolidado(form)
  if (ok) {
    exibirFeedback('sucesso', 'Consolidado mensal exportado com sucesso.')
  } else if (erro.value) {
    exibirFeedback('erro', erro.value)
  }
}
</script>
