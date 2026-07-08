<template>
  <div class="bg-white rounded-xl border border-slate-200 p-6">
    <div class="flex items-start justify-between mb-4">
      <div>
        <h2 class="text-lg font-semibold text-slate-800">{{ conciliacao.titulo }}</h2>
        <p class="text-sm text-slate-500 mt-0.5">{{ conciliacao.empresa_nome }}</p>
      </div>
      <ConciliacoesStatusConciliacaoBadge :status="conciliacao.status" :tipo-conciliacao="conciliacao.tipo_conciliacao" />
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
      <div>
        <p class="text-xs text-slate-400 uppercase tracking-wide">Tipo</p>
        <p class="text-slate-700 font-medium mt-1">{{ conciliacao.tipo_conciliacao }}</p>
      </div>
      <div>
        <p class="text-xs text-slate-400 uppercase tracking-wide">Período</p>
        <p class="text-slate-700 font-medium mt-1">{{ periodo }}</p>
      </div>
      <div>
        <p class="text-xs text-slate-400 uppercase tracking-wide">Criado em</p>
        <p class="text-slate-700 font-medium mt-1">{{ dataFormatada(conciliacao.criado_em) }}</p>
      </div>
      <div v-if="conciliacao.aprovado_em">
        <p class="text-xs text-slate-400 uppercase tracking-wide">Aprovado em</p>
        <p class="text-slate-700 font-medium mt-1">{{ dataFormatada(conciliacao.aprovado_em) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ConciliacaoDetalhe } from '~/types/conciliacao'

const props = defineProps<{ conciliacao: ConciliacaoDetalhe }>()

const periodo = computed(() => {
  const ini = new Date(props.conciliacao.periodo_inicio + 'T00:00:00').toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })
  const fim = new Date(props.conciliacao.periodo_fim + 'T00:00:00').toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })
  return ini === fim ? ini : `${ini} – ${fim}`
})

function dataFormatada(iso: string) {
  return new Date(iso).toLocaleDateString('pt-BR')
}
</script>
