<template>
  <div class="p-6 space-y-6">

    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-sm">
      <NuxtLink to="/conciliacoes" class="text-slate-400 hover:text-slate-600">Conciliações</NuxtLink>
      <span class="text-slate-300">/</span>
      <NuxtLink :to="`/conciliacoes/${route.params.id}`" class="text-slate-400 hover:text-slate-600">Detalhe</NuxtLink>
      <span class="text-slate-300">/</span>
      <span class="text-slate-600">Revisão do extrato</span>
    </div>

    <!-- Cabeçalho -->
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-semibold text-slate-800">Revisão do extrato bancário</h1>
        <p class="text-sm text-slate-500 mt-1">Edite diretamente na tabela. Clique em <strong>Salvar alterações</strong> quando terminar.</p>
      </div>
      <NuxtLink
        :to="`/conciliacoes/${route.params.id}`"
        class="px-4 py-2 text-sm text-slate-500 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
      >
        ← Voltar ao fechamento
      </NuxtLink>
    </div>

    <!-- Feedback de save -->
    <div
      v-if="feedbackSalvar"
      class="flex items-center gap-2 rounded-lg border px-4 py-3 text-sm"
      :class="feedbackSalvar.tipo === 'sucesso'
        ? 'bg-green-50 border-green-200 text-green-700'
        : 'bg-red-50 border-red-200 text-red-600'"
    >
      <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path v-if="feedbackSalvar.tipo === 'sucesso'" stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        <path v-else stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01" />
      </svg>
      {{ feedbackSalvar.mensagem }}
    </div>

    <!-- Ação em massa: confirmar lançamentos no fluxo -->
    <div
      v-if="!carregando && qtdNoFluxoPendentes > 0"
      class="flex items-center justify-between gap-4 bg-green-50 border border-green-200 rounded-xl px-5 py-4"
    >
      <div>
        <p class="text-sm font-semibold text-green-800">
          {{ qtdNoFluxoPendentes }} lançamento{{ qtdNoFluxoPendentes > 1 ? 's' : '' }} encontrado{{ qtdNoFluxoPendentes > 1 ? 's' : '' }} no fluxo de caixa
        </p>
        <p class="text-xs text-green-700 mt-0.5">
          Esses lançamentos têm correspondência confirmada por categoria e data. Você pode confirmá-los todos de uma vez.
        </p>
      </div>
      <button
        :disabled="confirmandoNoFluxo"
        class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors shrink-0"
        :class="confirmandoNoFluxo
          ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
          : 'bg-green-600 text-white hover:bg-green-700'"
        @click="confirmarNoFluxo"
      >
        <svg v-if="confirmandoNoFluxo" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        {{ confirmandoNoFluxo ? 'Confirmando...' : 'Confirmar lançamentos no fluxo' }}
      </button>
    </div>

    <!-- Cards de contadores -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-white rounded-xl border border-slate-200 p-4 text-center">
        <p class="text-2xl font-bold text-slate-800">{{ contadores.total }}</p>
        <p class="text-xs text-slate-500 mt-1">Total</p>
      </div>
      <div class="bg-white rounded-xl border border-amber-100 p-4 text-center">
        <p class="text-2xl font-bold text-amber-600">{{ contadores.pendentes }}</p>
        <p class="text-xs text-amber-600 mt-1">Pendentes</p>
      </div>
      <div class="bg-white rounded-xl border border-green-100 p-4 text-center">
        <p class="text-2xl font-bold text-green-700">{{ contadores.revisados }}</p>
        <p class="text-xs text-green-600 mt-1">Revisados</p>
      </div>
      <div class="bg-white rounded-xl border border-slate-200 p-4 text-center">
        <p class="text-2xl font-bold text-slate-400">{{ contadores.ignorados }}</p>
        <p class="text-xs text-slate-400 mt-1">Ignorados</p>
      </div>
    </div>

    <!-- Cards de valores -->
    <div class="grid grid-cols-2 gap-3">
      <div class="bg-white rounded-xl border border-green-100 px-4 py-3 flex items-center gap-3">
        <svg class="w-5 h-5 text-green-600 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        <div>
          <p class="text-xs text-slate-500">Total entradas</p>
          <p class="text-sm font-semibold text-green-700">R$ {{ fmtValor(totalEntradas) }}</p>
        </div>
      </div>
      <div class="bg-white rounded-xl border border-red-100 px-4 py-3 flex items-center gap-3">
        <svg class="w-5 h-5 text-red-500 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20 12H4" />
        </svg>
        <div>
          <p class="text-xs text-slate-500">Total saídas</p>
          <p class="text-sm font-semibold text-red-600">R$ {{ fmtValor(totalSaidas) }}</p>
        </div>
      </div>
    </div>

    <!-- Carregando -->
    <div v-if="carregando" class="text-sm text-slate-400">Carregando lançamentos...</div>

    <!-- Erro -->
    <div v-else-if="erro" class="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3">{{ erro }}</div>

    <!-- Tabela editável -->
    <div v-else-if="lancamentos.length > 0" class="bg-white rounded-xl border border-slate-200 overflow-hidden">
      <ConciliacoesTabelaExtratoAnotadoEditavel
        ref="tabelaRef"
        :lancamentos="lancamentos"
        :salvando="salvandoLote"
        @salvar="onSalvarLote"
        @abrirDetalhes="abrirDetalhes"
      />
    </div>

    <!-- Vazio -->
    <div v-else class="bg-white rounded-xl border border-slate-200 px-6 py-16 text-center">
      <p class="text-sm text-slate-500">Nenhum lançamento encontrado.</p>
      <p class="text-xs text-slate-400 mt-1">Processe o extrato bancário para gerar os lançamentos.</p>
    </div>

  </div>

  <!-- Modal de detalhes (conferência com fluxo + edição avançada) -->
  <ConciliacoesModalAnotarLancamento
    :aberto="modalAberto"
    :lancamento="lancamentoSelecionado"
    :salvando="atualizando"
    :erro="erro"
    @fechar="fecharModal"
    @salvar="onSalvarModal"
  />
</template>

<script setup lang="ts">
import type { LancamentoExtratoAnotado, StatusRevisao, AtualizarLancamentoAnotado } from '~/types/extratoAnotado'

definePageMeta({ layout: 'default', middleware: 'auth' })

const route = useRoute()
const conciliacaoId = route.params.id as string

const {
  lancamentos, carregando, atualizando, erro,
  contadores, totalEntradas, totalSaidas,
  carregar, anotar,
} = useExtratoAnotado(conciliacaoId)

onMounted(() => carregar())

// ── Confirmar lançamentos no fluxo ────────────────────────────────────────────

const confirmandoNoFluxo = ref(false)

// Lançamentos com conferência "encontrado" que ainda estão pendentes
const qtdNoFluxoPendentes = computed(() =>
  lancamentos.value.filter(
    l => l.tipo_conferencia_fluxo === 'encontrado'
      && (l.status_revisao === 'pendente' || l.status_revisao === 'em_revisao'),
  ).length,
)

async function confirmarNoFluxo() {
  if (confirmandoNoFluxo.value) return
  const alvos = lancamentos.value.filter(
    l => l.tipo_conferencia_fluxo === 'encontrado'
      && (l.status_revisao === 'pendente' || l.status_revisao === 'em_revisao'),
  )
  if (alvos.length === 0) return

  confirmandoNoFluxo.value = true
  feedbackSalvar.value = null
  let salvos = 0

  try {
    for (const l of alvos) {
      const resultado = await anotar(l.id, { status_revisao: 'revisado' })
      if (resultado) salvos++
    }
    feedbackSalvar.value = {
      tipo: 'sucesso',
      mensagem: `${salvos} lançamento${salvos > 1 ? 's' : ''} confirmado${salvos > 1 ? 's' : ''} como revisado${salvos > 1 ? 's' : ''}.`,
    }
    setTimeout(() => { feedbackSalvar.value = null }, 5000)
  } finally {
    confirmandoNoFluxo.value = false
  }
}

// ── Save em lote ─────────────────────────────────────────────────────────────

const tabelaRef = ref()
const salvandoLote = ref(false)
const feedbackSalvar = ref<{ tipo: 'sucesso' | 'erro'; mensagem: string } | null>(null)

async function onSalvarLote(batch: Array<{ id: string; dados: AtualizarLancamentoAnotado }>) {
  if (salvandoLote.value) return
  salvandoLote.value = true
  feedbackSalvar.value = null
  let salvos = 0
  let erros = 0

  try {
    for (const item of batch) {
      const resultado = await anotar(item.id, item.dados)
      if (resultado) salvos++
      else erros++
    }
  } finally {
    salvandoLote.value = false
  }

  // Limpar alterações do componente (salvo ou não — ver comentário)
  // Para demo: clear all após tentativa, falhas precisam ser refeitas
  tabelaRef.value?.limparAlteracoes()

  if (erros === 0) {
    feedbackSalvar.value = { tipo: 'sucesso', mensagem: `${salvos} lançamento${salvos > 1 ? 's' : ''} salvo${salvos > 1 ? 's' : ''} com sucesso.` }
  } else {
    feedbackSalvar.value = { tipo: 'erro', mensagem: `${salvos} salvo${salvos !== 1 ? 's' : ''}, ${erros} com falha. Revise e salve novamente os itens não salvos.` }
  }

  setTimeout(() => { feedbackSalvar.value = null }, 6000)
}

// ── Modal de detalhes ─────────────────────────────────────────────────────────

const modalAberto = ref(false)
const lancamentoSelecionado = ref<LancamentoExtratoAnotado | null>(null)

function abrirDetalhes(l: LancamentoExtratoAnotado) {
  lancamentoSelecionado.value = l
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  lancamentoSelecionado.value = null
}

async function onSalvarModal(payload: {
  categoria: string | null
  descricao_negocio: string | null
  nf_doc: string | null
  observacao: string | null
  status_revisao: StatusRevisao
}) {
  if (!lancamentoSelecionado.value) return
  const atualizado = await anotar(lancamentoSelecionado.value.id, payload)
  if (atualizado) fecharModal()
}

// ── Helper formatação ─────────────────────────────────────────────────────────

function fmtValor(v: unknown): string {
  const n = Number(v ?? 0)
  return isNaN(n) ? '0.00' : n.toFixed(2)
}
</script>
