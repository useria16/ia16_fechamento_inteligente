<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    :class="classe"
  >
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { labelStatus } from '~/utils/statusConciliacao'

const props = defineProps<{
  status: string
  tipoConciliacao?: string
}>()

const CLASSES: Record<string, string> = {
  rascunho:          'bg-slate-100 text-slate-600',
  arquivos_enviados: 'bg-blue-50  text-blue-600',
  em_processamento:  'bg-blue-100 text-blue-700',
  processado:        'bg-teal-100 text-teal-700',
  com_divergencias:  'bg-red-100  text-red-600',
  aprovado:          'bg-green-100 text-green-700',
  cancelado:         'bg-slate-100 text-slate-400',
  erro:              'bg-red-100  text-red-700',
}

const classe = computed(() => CLASSES[props.status] ?? 'bg-slate-100 text-slate-500')

const label = computed(() => {
  if (props.tipoConciliacao === 'extrato_anotado' && props.status === 'com_divergencias') {
    return 'Pendente de revisão'
  }
  return labelStatus(props.status)
})
</script>
