<template>
  <div class="bg-white rounded-xl border border-slate-200 p-6 space-y-6">

    <!-- Cabeçalho da seção -->
    <div class="flex items-center gap-3">
      <div
        class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
        :class="conciliacao.status === 'aprovado' ? 'bg-green-50' : 'bg-blue-50'"
      >
        <svg
          class="w-5 h-5"
          :class="conciliacao.status === 'aprovado' ? 'text-green-600' : 'text-blue-600'"
          fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div>
        <p class="text-sm font-semibold text-slate-800">
          {{ conciliacao.status === 'aprovado' ? 'Fechamento aprovado' : 'Pacote final do fechamento' }}
        </p>
        <p class="text-xs text-slate-500 mt-0.5">
          {{ conciliacao.status === 'aprovado'
            ? 'Exporte o relatório consolidado ou reabra o fechamento se necessário.'
            : 'Finalize a revisão, aprove o fechamento e exporte o relatório consolidado.' }}
        </p>
      </div>
    </div>

    <!-- Carregando pendências -->
    <div v-if="carregandoDivergencias" class="text-xs text-slate-400">
      Verificando pendências de revisão...
    </div>

    <!-- Aviso de bloqueio de aprovação -->
    <div
      v-else-if="podeAprovar(conciliacao.status) && temDivergenciasAbertas"
      class="flex items-start gap-3 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800"
    >
      <svg class="w-4 h-4 mt-0.5 shrink-0 text-amber-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
      </svg>
      <div v-if="conciliacao.tipo_conciliacao === 'extrato_anotado'">
        <p class="font-medium">Lançamentos pendentes</p>
        <p class="mt-0.5 text-amber-700">
          Revise ou ignore todos os lançamentos do extrato antes de aprovar o fechamento.
        </p>
      </div>
      <div v-else>
        <p class="font-medium">Divergências pendentes</p>
        <p class="mt-0.5 text-amber-700">
          Resolva ou ignore todas as divergências antes de aprovar o fechamento.
          <NuxtLink :to="`/conciliacoes/${conciliacao.id}/divergencias`" class="underline hover:no-underline ml-1">
            Ir para revisão
          </NuxtLink>
        </p>
      </div>
    </div>

    <!-- Feedback de ação -->
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

    <!-- Botões de ação -->
    <div class="flex flex-wrap items-start gap-3">

      <!-- Aprovar fechamento -->
      <div v-if="podeAprovar(conciliacao.status)" class="flex flex-col gap-1">
        <button
          :disabled="aprovando || temDivergenciasAbertas || carregandoDivergencias"
          :class="[
            'inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors',
            (aprovando || temDivergenciasAbertas || carregandoDivergencias)
              ? 'text-slate-400 bg-slate-100 cursor-not-allowed'
              : 'text-white bg-green-600 hover:bg-green-700 cursor-pointer',
          ]"
          @click="abrirModalAprovar"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          Aprovar fechamento
        </button>
        <p
          v-if="temDivergenciasAbertas"
          class="text-xs text-slate-400 max-w-xs"
        >
          A aprovação será liberada após revisar ou ignorar todos os lançamentos.
        </p>
      </div>

      <!-- Exportar relatório -->
      <button
        v-if="podeExportar(conciliacao.status)"
        :disabled="exportando"
        class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        @click="onExportar"
      >
        <svg v-if="exportando" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        {{ exportando ? 'Exportando...' : 'Exportar relatório' }}
      </button>

      <!-- Reabrir fechamento -->
      <button
        v-if="podeReabrir(conciliacao.status)"
        :disabled="reabrindo"
        class="inline-flex items-center gap-2 px-4 py-2 text-sm text-amber-700 border border-amber-200 rounded-lg hover:bg-amber-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        @click="abrirModalReabrir"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Reabrir fechamento
      </button>

    </div>

    <!-- Bloco de aprovação -->
    <div
      v-if="conciliacao.aprovado_em"
      class="rounded-lg bg-green-50 border border-green-100 px-4 py-4 space-y-2"
    >
      <p class="text-xs font-semibold text-green-700 uppercase tracking-wide">Aprovação</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
        <div>
          <span class="text-slate-500">Aprovado em:</span>
          <span class="ml-1.5 text-slate-800">{{ formatarData(conciliacao.aprovado_em) }}</span>
        </div>
        <div>
          <span class="text-slate-500">Aprovado por:</span>
          <span class="ml-1.5 text-slate-800">{{ conciliacao.aprovado_por_usuario_id ?? 'Usuário não identificado' }}</span>
        </div>
        <div v-if="conciliacao.observacao_aprovacao" class="sm:col-span-2">
          <span class="text-slate-500">Observação:</span>
          <span class="ml-1.5 text-slate-700 italic">{{ conciliacao.observacao_aprovacao }}</span>
        </div>
      </div>
    </div>

    <!-- Bloco de reabertura -->
    <div
      v-if="conciliacao.reaberto_em"
      class="rounded-lg bg-amber-50 border border-amber-100 px-4 py-4 space-y-2"
    >
      <p class="text-xs font-semibold text-amber-700 uppercase tracking-wide">Reabertura</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
        <div>
          <span class="text-slate-500">Reaberto em:</span>
          <span class="ml-1.5 text-slate-800">{{ formatarData(conciliacao.reaberto_em) }}</span>
        </div>
        <div>
          <span class="text-slate-500">Reaberto por:</span>
          <span class="ml-1.5 text-slate-800">{{ conciliacao.reaberto_por_usuario_id ?? 'Usuário não identificado' }}</span>
        </div>
        <div v-if="conciliacao.motivo_reabertura" class="sm:col-span-2">
          <span class="text-slate-500">Motivo:</span>
          <span class="ml-1.5 text-slate-700 italic">{{ conciliacao.motivo_reabertura }}</span>
        </div>
      </div>
    </div>

  </div>

  <!-- Modal de aprovação -->
  <ConciliacoesModalAprovarFechamento
    :aberto="modalAprovarAberto"
    :confirmando="aprovando"
    :erro="erroAprovacao"
    @fechar="modalAprovarAberto = false"
    @confirmar="onConfirmarAprovacao"
  />

  <!-- Modal de reabertura -->
  <ConciliacoesModalReabrirFechamento
    :aberto="modalReabrirAberto"
    :confirmando="reabrindo"
    :erro="erroReabertura"
    @fechar="modalReabrirAberto = false"
    @confirmar="onConfirmarReabertura"
  />
</template>

<script setup lang="ts">
import type { ConciliacaoDetalhe } from '~/types/conciliacao'

const props = defineProps<{
  conciliacao: ConciliacaoDetalhe
}>()

const emit = defineEmits<{
  atualizada: [conciliacao: ConciliacaoDetalhe]
}>()

const {
  carregandoDivergencias,
  temDivergenciasAbertas,
  carregarDivergencias,
  aprovando,
  reabrindo,
  exportando,
  erroAprovacao,
  erroReabertura,
  erroExportacao,
  podeAprovar,
  podeExportar,
  podeReabrir,
  aprovarFechamento,
  reabrirFechamento,
  exportarRelatorio,
} = usePacoteFinalFechamento(props.conciliacao.id, props.conciliacao.tipo_conciliacao)

const modalAprovarAberto = ref(false)
const modalReabrirAberto = ref(false)
const feedbackMensagem = ref<string | null>(null)
const feedbackTipo = ref<'sucesso' | 'erro'>('sucesso')

function exibirFeedback(tipo: 'sucesso' | 'erro', mensagem: string) {
  feedbackTipo.value = tipo
  feedbackMensagem.value = mensagem
  setTimeout(() => { feedbackMensagem.value = null }, 5000)
}

// Carrega divergências ao montar se status permite aprovação
onMounted(async () => {
  if (podeAprovar(props.conciliacao.status)) {
    await carregarDivergencias()
  }
})

watch(() => props.conciliacao.status, async (novoStatus) => {
  if (podeAprovar(novoStatus)) {
    await carregarDivergencias()
  }
})

function abrirModalAprovar() {
  modalAprovarAberto.value = true
}

function abrirModalReabrir() {
  modalReabrirAberto.value = true
}

async function onConfirmarAprovacao(observacao: string | null) {
  const atualizada = await aprovarFechamento({ observacao_aprovacao: observacao })
  if (atualizada) {
    modalAprovarAberto.value = false
    exibirFeedback('sucesso', 'Fechamento aprovado com sucesso.')
    emit('atualizada', atualizada)
  }
}

async function onConfirmarReabertura(motivo: string | null) {
  const atualizada = await reabrirFechamento({ motivo })
  if (atualizada) {
    modalReabrirAberto.value = false
    exibirFeedback('sucesso', 'Fechamento reaberto para revisão.')
    emit('atualizada', atualizada)
    await carregarDivergencias()
  }
}

async function onExportar() {
  const sucesso = await exportarRelatorio()
  if (sucesso) {
    exibirFeedback('sucesso', 'Relatório exportado com sucesso.')
  } else if (erroExportacao.value) {
    exibirFeedback('erro', erroExportacao.value)
  }
}

function formatarData(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}
</script>
