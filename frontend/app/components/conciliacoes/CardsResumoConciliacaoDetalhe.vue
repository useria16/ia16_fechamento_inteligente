<template>
  <!-- Cards para extrato_anotado: métricas de revisão -->
  <div v-if="isExtratoAnotado" class="grid grid-cols-2 lg:grid-cols-4 gap-4">

    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Total processado</p>
      <p class="text-3xl font-bold text-slate-800 mt-2">{{ conciliacao.quantidade_registros }}</p>
      <p class="text-xs text-slate-400 mt-1">lançamentos</p>
    </div>

    <div class="bg-white rounded-xl border border-green-100 p-5">
      <p class="text-xs font-medium text-green-600 uppercase tracking-wide">Revisados</p>
      <p class="text-3xl font-bold text-green-600 mt-2">{{ contadores.revisados }}</p>
      <p class="text-xs text-green-500 mt-1">confirmados</p>
    </div>

    <div class="bg-white rounded-xl p-5" :class="contadores.pendentes > 0 ? 'border border-amber-200' : 'border border-slate-200'">
      <p class="text-xs font-medium uppercase tracking-wide" :class="contadores.pendentes > 0 ? 'text-amber-600' : 'text-slate-500'">
        Pendentes
      </p>
      <p class="text-3xl font-bold mt-2" :class="contadores.pendentes > 0 ? 'text-amber-600' : 'text-slate-400'">
        {{ contadores.pendentes }}
      </p>
      <p class="text-xs mt-1" :class="contadores.pendentes > 0 ? 'text-amber-500' : 'text-slate-400'">
        aguardando revisão
      </p>
    </div>

    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">No fluxo</p>
      <p class="text-3xl font-bold mt-2" :class="contadores.no_fluxo > 0 ? 'text-blue-600' : 'text-slate-400'">
        {{ contadores.no_fluxo }}
      </p>
      <p class="text-xs text-slate-400 mt-1">encontrados</p>
    </div>

  </div>

  <!-- Cards para conciliação bilateral: métricas originais -->
  <div v-else class="grid grid-cols-2 lg:grid-cols-4 gap-4">
    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Total processado</p>
      <p class="text-3xl font-bold text-slate-800 mt-2">{{ conciliacao.quantidade_registros }}</p>
      <p class="text-xs text-slate-400 mt-1">registros</p>
    </div>
    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Conciliados</p>
      <p class="text-3xl font-bold text-green-600 mt-2">{{ conciliacao.quantidade_conciliados }}</p>
      <p class="text-xs text-slate-400 mt-1">registros</p>
    </div>
    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Divergências</p>
      <p class="text-3xl font-bold mt-2" :class="conciliacao.quantidade_divergencias > 0 ? 'text-red-500' : 'text-slate-800'">
        {{ conciliacao.quantidade_divergencias }}
      </p>
      <p class="text-xs text-slate-400 mt-1">registros</p>
    </div>
    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">% Conciliado</p>
      <p class="text-3xl font-bold mt-2" :class="conciliacao.percentual_conciliado >= 100 ? 'text-green-600' : conciliacao.percentual_conciliado > 0 ? 'text-blue-600' : 'text-slate-400'">
        {{ conciliacao.percentual_conciliado }}%
      </p>
      <p class="text-xs text-slate-400 mt-1">do total</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ConciliacaoDetalhe } from '~/types/conciliacao'

const props = defineProps<{ conciliacao: ConciliacaoDetalhe }>()

const isExtratoAnotado = computed(() => props.conciliacao.tipo_conciliacao === 'extrato_anotado')

// Para extrato_anotado: carrega contadores de revisão
const { contadores, carregar } = useExtratoAnotado(props.conciliacao.id)

onMounted(() => {
  if (isExtratoAnotado.value) carregar()
})

watch(() => props.conciliacao.status, () => {
  if (isExtratoAnotado.value) carregar()
})
</script>
