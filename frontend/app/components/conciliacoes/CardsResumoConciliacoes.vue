<template>
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
    <div
      v-for="card in cards"
      :key="card.label"
      class="bg-white rounded-xl border border-slate-200 p-5"
    >
      <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">{{ card.label }}</p>
      <p class="text-3xl font-bold mt-2" :class="card.cor">{{ card.valor }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ResumoConciliacoes } from '~/types/conciliacao'

const props = defineProps<{ resumo: ResumoConciliacoes }>()

const cards = computed(() => [
  { label: 'Total de conciliações', valor: props.resumo.total,            cor: 'text-slate-800' },
  { label: 'Em processamento',      valor: props.resumo.em_processamento, cor: 'text-blue-600'  },
  { label: 'Com divergências',      valor: props.resumo.com_divergencias, cor: 'text-red-500'   },
  { label: 'Aprovadas',             valor: props.resumo.aprovadas,        cor: 'text-green-600' },
])
</script>
