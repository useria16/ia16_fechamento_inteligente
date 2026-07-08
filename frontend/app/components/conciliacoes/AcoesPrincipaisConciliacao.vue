<template>
  <div class="flex flex-wrap items-center gap-3">

    <!-- Aviso: arquivos mínimos ausentes para processar -->
    <div
      v-if="acaoPrincipal?.evento === 'processar' && arquivosMinimosPresentes === false"
      class="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 max-w-xs"
    >
      Envie um extrato bancário e uma planilha interna para preparar o fechamento.
    </div>

    <!-- Botão principal por status -->
    <button
      v-if="acaoPrincipal"
      :disabled="processando
        || (acaoPrincipal.evento === 'processar' && props.status === 'em_processamento')
        || (acaoPrincipal.evento === 'processar' && arquivosMinimosPresentes === false)"
      class="px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
      @click="$emit(acaoPrincipal.evento as any)"
    >
      <svg
        v-if="processando && acaoPrincipal.evento === 'processar'"
        class="w-4 h-4 animate-spin"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      {{ processando && acaoPrincipal.evento === 'processar' ? 'Processando...' : acaoPrincipal.label }}
    </button>

    <!-- Ações secundárias -->
    <button
      v-if="podeReprocessar"
      :disabled="processando"
      class="px-4 py-2 text-sm border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
      @click="$emit('reprocessar')"
    >
      Reprocessar
    </button>

    <button
      v-if="podeCancelar"
      :disabled="processando"
      class="px-4 py-2 text-sm border border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
      @click="$emit('cancelar')"
    >
      Cancelar
    </button>

    <NuxtLink
      to="/conciliacoes"
      class="px-4 py-2 text-sm text-slate-500 hover:text-slate-700 transition-colors"
    >
      Voltar
    </NuxtLink>

  </div>
</template>

<script setup lang="ts">
import type { StatusConciliacao } from '~/types/conciliacao'

const props = defineProps<{
  status: StatusConciliacao
  processando?: boolean
  arquivosMinimosPresentes?: boolean
  tipoConciliacao?: string
}>()

defineEmits<{
  enviarArquivos: []
  processar: []
  revisarDivergencias: []
  revisarExtratoAnotado: []
  verRelatorio: []
  reprocessar: []
  cancelar: []
}>()

const isExtratoAnotado = computed(() => props.tipoConciliacao === 'extrato_anotado')

const ACOES_PRINCIPAIS: Partial<Record<StatusConciliacao, { label: string; evento: string }>> = {
  rascunho:          { label: 'Enviar arquivos',          evento: 'enviarArquivos' },
  arquivos_enviados: { label: 'Processar conciliação',    evento: 'processar' },
  em_processamento:  { label: 'Aguardando processamento', evento: 'processar' },
  com_divergencias:  { label: 'Revisar divergências',     evento: 'revisarDivergencias' },
}

const ACOES_EXTRATO_ANOTADO: Partial<Record<StatusConciliacao, { label: string; evento: string }>> = {
  rascunho:          { label: 'Enviar extrato',         evento: 'enviarArquivos' },
  arquivos_enviados: { label: 'Processar extrato',      evento: 'processar' },
  em_processamento:  { label: 'Processando extrato...', evento: 'processar' },
  // com_divergencias e processado: CTA principal está no card de revisão abaixo — não duplicar
}

const acaoPrincipal   = computed(() =>
  isExtratoAnotado.value
    ? (ACOES_EXTRATO_ANOTADO[props.status] ?? null)
    : (ACOES_PRINCIPAIS[props.status] ?? null)
)
const podeCancelar    = computed(() => props.status === 'rascunho')
const podeReprocessar = computed(() =>
  ['processado', 'com_divergencias', 'reaberto'].includes(props.status) && !isExtratoAnotado.value
)
</script>
