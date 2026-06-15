<template>
  <span :class="['inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium', classes]">
    <span :class="['w-1.5 h-1.5 rounded-full', dotClass]" />
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { labelStatusDivergencia } from '~/types/divergencia'

const props = defineProps<{ status: string }>()

const CONFIG: Record<string, { bg: string; text: string; dot: string }> = {
  aberta:     { bg: 'bg-red-50',    text: 'text-red-700',    dot: 'bg-red-500' },
  em_analise: { bg: 'bg-blue-50',   text: 'text-blue-700',   dot: 'bg-blue-500' },
  resolvida:  { bg: 'bg-green-50',  text: 'text-green-700',  dot: 'bg-green-500' },
  ignorada:   { bg: 'bg-slate-100', text: 'text-slate-500',  dot: 'bg-slate-400' },
}

const cfg = computed(() => CONFIG[props.status] ?? CONFIG.aberta)
const classes = computed(() => `${cfg.value.bg} ${cfg.value.text}`)
const dotClass = computed(() => cfg.value.dot)
const label = computed(() => labelStatusDivergencia(props.status))
</script>
