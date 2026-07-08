<template>
  <span :class="['inline-flex px-2 py-0.5 rounded text-xs font-medium', classes]">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { labelSeveridade } from '~/types/divergencia'

const props = defineProps<{ severidade: string }>()

const CONFIG: Record<string, string> = {
  baixa: 'bg-green-50 text-green-700',
  media: 'bg-amber-50 text-amber-700',
  alta:  'bg-red-50   text-red-700',
}

const classes = computed(() => CONFIG[props.severidade] ?? CONFIG.media)
const label = computed(() => labelSeveridade(props.severidade))
</script>
