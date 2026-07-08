<template>
  <div class="bg-white rounded-xl border border-slate-200 p-6 space-y-5">

    <!-- Cabeçalho -->
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center shrink-0">
          <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
        </div>
        <div>
          <p class="text-sm font-semibold text-slate-800">Fechamento preparado para revisão</p>
          <p class="text-xs text-slate-500 mt-0.5">O motor identificou pendências que precisam da sua análise.</p>
        </div>
      </div>

      <NuxtLink
        v-if="conciliacaoId"
        :to="`/conciliacoes/${conciliacaoId}/divergencias`"
        class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors shrink-0"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
        </svg>
        Revisar divergências
      </NuxtLink>
    </div>

    <!-- Cards de revisão -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">

      <div class="rounded-lg bg-green-50 border border-green-100 p-4 text-center">
        <p class="text-2xl font-bold text-green-700">{{ conciliados }}</p>
        <p class="text-xs text-green-600 mt-1 font-medium">Conciliados</p>
      </div>

      <div class="rounded-lg border p-4 text-center"
        :class="divergentes > 0 ? 'bg-red-50 border-red-100' : 'bg-slate-50 border-slate-200'">
        <p class="text-2xl font-bold" :class="divergentes > 0 ? 'text-red-700' : 'text-slate-500'">
          {{ divergentes }}
        </p>
        <p class="text-xs mt-1 font-medium" :class="divergentes > 0 ? 'text-red-600' : 'text-slate-400'">
          Divergências
        </p>
      </div>

      <div class="rounded-lg border p-4 text-center"
        :class="pendentes > 0 ? 'bg-amber-50 border-amber-100' : 'bg-slate-50 border-slate-200'">
        <p class="text-2xl font-bold" :class="pendentes > 0 ? 'text-amber-700' : 'text-slate-500'">
          {{ pendentes }}
        </p>
        <p class="text-xs mt-1 font-medium" :class="pendentes > 0 ? 'text-amber-600' : 'text-slate-400'">
          Pendentes
        </p>
      </div>

      <div class="rounded-lg bg-slate-50 border border-slate-200 p-4 text-center">
        <p class="text-2xl font-bold text-blue-600">{{ percentual }}%</p>
        <p class="text-xs text-slate-400 mt-1 font-medium">Conciliado</p>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import type { ConciliacaoDetalhe } from '~/types/conciliacao'

const props = defineProps<{ conciliacao: ConciliacaoDetalhe }>()

const conciliacaoId = computed(() => props.conciliacao.id)
const conciliados   = computed(() => props.conciliacao.quantidade_conciliados)
const divergentes   = computed(() => (props.conciliacao as any).quantidade_divergentes ?? props.conciliacao.quantidade_divergencias)
const pendentes     = computed(() => (props.conciliacao as any).quantidade_pendentes ?? 0)
const percentual    = computed(() => props.conciliacao.percentual_conciliado ?? 0)
</script>
