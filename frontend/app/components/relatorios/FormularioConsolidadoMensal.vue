<template>
  <div class="bg-white rounded-xl border border-slate-200 p-6 space-y-6">

    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center shrink-0">
        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <div>
        <p class="text-sm font-semibold text-slate-800">Planilha de Conciliação</p>
        <p class="text-xs text-slate-500 mt-0.5">
          Exporte conciliações acumuladas por mês ou por período selecionado.
        </p>
      </div>
    </div>

    <div class="space-y-4">
      <div class="space-y-1">
        <label class="block text-xs font-medium text-slate-600">Modelo de conciliação</label>
        <p class="text-sm text-slate-700 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
          Extrato Anotado
        </p>
      </div>

      <div v-if="isAdmin" class="space-y-1">
        <label class="block text-xs font-medium text-slate-600">Empresa <span class="text-red-400">*</span></label>
        <select
          v-model="empresaId"
          :disabled="carregandoEmpresas"
          class="w-full rounded-lg border px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          :class="erroEmpresa ? 'border-red-400' : 'border-slate-200'"
        >
          <option value="">
            {{ carregandoEmpresas ? 'Carregando empresas...' : empresas.length === 0 ? 'Nenhuma empresa disponível' : 'Selecione a empresa' }}
          </option>
          <option v-for="e in empresas" :key="e.id" :value="e.id">{{ e.nome }}</option>
        </select>
        <p v-if="erroEmpresa" class="text-xs text-red-500">{{ erroEmpresa }}</p>
      </div>
    </div>

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

    <form class="space-y-5" @submit.prevent="onSubmit">
      <div class="space-y-2">
        <label class="block text-xs font-medium text-slate-600">Período da exportação</label>
        <div class="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1">
          <button
            type="button"
            class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
            :class="modoExportacao === 'mensal'
              ? 'bg-white text-blue-700 shadow-sm'
              : 'text-slate-500 hover:text-slate-800'"
            @click="selecionarModo('mensal')"
          >
            Mensal
          </button>
          <button
            type="button"
            class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
            :class="modoExportacao === 'periodo'
              ? 'bg-white text-blue-700 shadow-sm'
              : 'text-slate-500 hover:text-slate-800'"
            @click="selecionarModo('periodo')"
          >
            Por período
          </button>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 p-4">
        <div v-if="modoExportacao === 'mensal'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="block text-xs font-medium text-slate-600">Mês <span class="text-red-400">*</span></label>
            <select
              v-model="formMensal.mes"
              class="w-full rounded-lg border px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="errosMensal.mes ? 'border-red-400' : 'border-slate-200'"
            >
              <option v-for="m in meses" :key="m.valor" :value="m.valor">{{ m.label }}</option>
            </select>
            <p v-if="errosMensal.mes" class="text-xs text-red-500">{{ errosMensal.mes }}</p>
          </div>

          <div class="space-y-1">
            <label class="block text-xs font-medium text-slate-600">Ano <span class="text-red-400">*</span></label>
            <select
              v-model="formMensal.ano"
              class="w-full rounded-lg border px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="errosMensal.ano ? 'border-red-400' : 'border-slate-200'"
            >
              <option v-for="a in anos" :key="a" :value="a">{{ a }}</option>
            </select>
            <p v-if="errosMensal.ano" class="text-xs text-red-500">{{ errosMensal.ano }}</p>
          </div>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="block text-xs font-medium text-slate-600">Data inicial <span class="text-red-400">*</span></label>
            <input
              v-model="formPeriodo.data_inicio"
              type="date"
              class="w-full rounded-lg border px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="errosPeriodo.data_inicio ? 'border-red-400' : 'border-slate-200'"
            />
            <p v-if="errosPeriodo.data_inicio" class="text-xs text-red-500">{{ errosPeriodo.data_inicio }}</p>
          </div>

          <div class="space-y-1">
            <label class="block text-xs font-medium text-slate-600">Data final <span class="text-red-400">*</span></label>
            <input
              v-model="formPeriodo.data_fim"
              type="date"
              class="w-full rounded-lg border px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="errosPeriodo.data_fim ? 'border-red-400' : 'border-slate-200'"
            />
            <p v-if="errosPeriodo.data_fim" class="text-xs text-red-500">{{ errosPeriodo.data_fim }}</p>
          </div>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <p class="text-xs text-slate-500">
          {{ textoAjudaModo }}
        </p>
        <button
          type="submit"
          :disabled="baixando"
          :class="botaoClasse"
        >
          {{ baixando ? 'Gerando...' : 'Exportar planilha' }}
        </button>
      </div>
    </form>

    <div class="rounded-lg bg-slate-50 border border-slate-100 px-4 py-3 text-xs text-slate-500">
      A planilha exportada mantém o layout da conciliação diária, com lançamentos acumulados em uma única aba.
    </div>

  </div>
</template>

<script setup lang="ts">
import { consolidadoMensalSchema, consolidadoPeriodoSchema } from '~/schemas/relatorio.schema'
import type { ConsolidadoMensalForm, ConsolidadoPeriodoForm } from '~/schemas/relatorio.schema'

const auth = useAuthStore()
const { baixando, erro, baixarConsolidado, baixarConsolidadoPeriodo, limparFeedback } = useConsolidadoMensal()
const { empresas, carregando: carregandoEmpresas, carregar: carregarEmpresas } = useEmpresas()

const isAdmin = computed(() => auth.perfil === 'admin_ia16')

const agora = new Date()
const hoje = agora.toISOString().slice(0, 10)
const primeiroDiaMes = new Date(agora.getFullYear(), agora.getMonth(), 1).toISOString().slice(0, 10)

const empresaId = ref('')
const erroEmpresa = ref<string | null>(null)

const formMensal = reactive<ConsolidadoMensalForm>({
  ano: agora.getFullYear(),
  mes: agora.getMonth() + 1,
  tipo_conciliacao: 'extrato_anotado',
  empresa_id: undefined,
})

const formPeriodo = reactive<ConsolidadoPeriodoForm>({
  data_inicio: primeiroDiaMes,
  data_fim: hoje,
  tipo_conciliacao: 'extrato_anotado',
  empresa_id: undefined,
})

const errosMensal = reactive<Partial<Record<keyof ConsolidadoMensalForm, string>>>({})
const errosPeriodo = reactive<Partial<Record<keyof ConsolidadoPeriodoForm, string>>>({})
const feedbackMensagem = ref<string | null>(null)
const feedbackTipo = ref<'sucesso' | 'erro'>('sucesso')
const modoExportacao = ref<'mensal' | 'periodo'>('mensal')

const botaoClasse = computed(() => [
  'inline-flex items-center justify-center gap-2 w-full sm:w-auto px-4 py-2 text-sm font-medium rounded-lg transition-colors',
  baixando.value
    ? 'text-slate-400 bg-slate-100 cursor-not-allowed'
    : 'text-white bg-blue-600 hover:bg-blue-700 cursor-pointer',
])

const textoAjudaModo = computed(() => (
  modoExportacao.value === 'mensal'
    ? 'Exporta todas as conciliações encontradas no mês selecionado.'
    : 'Exporta todas as conciliações encontradas entre as datas informadas.'
))

onMounted(async () => {
  if (isAdmin.value) {
    await carregarEmpresas()
    if (empresas.value.length === 1) {
      empresaId.value = empresas.value[0].id
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

function validarEmpresa(): boolean {
  erroEmpresa.value = null
  if (isAdmin.value && !empresaId.value.trim()) {
    erroEmpresa.value = 'Selecione uma empresa para exportar.'
    return false
  }
  return true
}

function aplicarEmpresa<T extends { empresa_id?: string }>(form: T): T {
  form.empresa_id = empresaId.value || undefined
  return form
}

function limparErrosFormulario() {
  Object.keys(errosMensal).forEach(k => delete (errosMensal as any)[k])
  Object.keys(errosPeriodo).forEach(k => delete (errosPeriodo as any)[k])
}

function selecionarModo(modo: 'mensal' | 'periodo') {
  modoExportacao.value = modo
  limparErrosFormulario()
  limparFeedback()
  feedbackMensagem.value = null
}

function validarMensal(): boolean {
  Object.keys(errosMensal).forEach(k => delete (errosMensal as any)[k])
  if (!validarEmpresa()) return false

  const resultado = consolidadoMensalSchema.safeParse(aplicarEmpresa(formMensal))
  if (!resultado.success) {
    for (const issue of resultado.error.issues) {
      const campo = issue.path[0] as keyof ConsolidadoMensalForm
      if (campo && !errosMensal[campo]) errosMensal[campo] = issue.message
    }
    return false
  }
  return true
}

function validarPeriodo(): boolean {
  Object.keys(errosPeriodo).forEach(k => delete (errosPeriodo as any)[k])
  if (!validarEmpresa()) return false

  const resultado = consolidadoPeriodoSchema.safeParse(aplicarEmpresa(formPeriodo))
  if (!resultado.success) {
    for (const issue of resultado.error.issues) {
      const campo = issue.path[0] as keyof ConsolidadoPeriodoForm
      if (campo && !errosPeriodo[campo]) errosPeriodo[campo] = issue.message
    }
    return false
  }
  return true
}

async function onSubmitMensal() {
  if (!validarMensal()) return

  const ok = await baixarConsolidado(formMensal)
  if (ok) {
    exibirFeedback('sucesso', 'Planilha mensal exportada com sucesso.')
  } else if (erro.value) {
    exibirFeedback('erro', erro.value)
  }
}

async function onSubmitPeriodo() {
  if (!validarPeriodo()) return

  const ok = await baixarConsolidadoPeriodo(formPeriodo)
  if (ok) {
    exibirFeedback('sucesso', 'Planilha por período exportada com sucesso.')
  } else if (erro.value) {
    exibirFeedback('erro', erro.value)
  }
}

async function onSubmit() {
  if (modoExportacao.value === 'mensal') {
    await onSubmitMensal()
    return
  }

  await onSubmitPeriodo()
}
</script>
