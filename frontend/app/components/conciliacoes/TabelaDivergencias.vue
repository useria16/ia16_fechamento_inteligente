<template>
  <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">

    <!-- Sem resultados -->
    <div v-if="divergencias.length === 0" class="px-6 py-12 text-center">
      <svg class="w-10 h-10 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm text-slate-500">Nenhuma divergência encontrada.</p>
    </div>

    <!-- Tabela -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 border-b border-slate-200">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Tipo</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Severidade</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Descrição</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wide">Valor prev.</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wide">Valor real.</th>
            <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wide">Diferença</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Status</th>
            <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wide">Ação</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="div in divergencias"
            :key="div.id"
            class="hover:bg-slate-50 transition-colors"
          >
            <td class="px-4 py-3">
              <span class="text-xs text-slate-600">{{ labelTipo(div.tipo_divergencia) }}</span>
            </td>
            <td class="px-4 py-3">
              <ConciliacoesSeveridadeDivergenciaBadge :severidade="div.severidade" />
            </td>
            <td class="px-4 py-3 max-w-[280px]">
              <p class="text-slate-700 line-clamp-2 leading-snug">{{ div.descricao }}</p>
              <p v-if="div.observacao" class="text-xs text-slate-400 mt-0.5 line-clamp-1 italic">
                "{{ div.observacao }}"
              </p>
            </td>
            <td class="px-4 py-3 text-right tabular-nums text-slate-600">
              {{ div.valor_previsto != null ? formatarValor(div.valor_previsto) : '—' }}
            </td>
            <td class="px-4 py-3 text-right tabular-nums text-slate-600">
              {{ div.valor_realizado != null ? formatarValor(div.valor_realizado) : '—' }}
            </td>
            <td class="px-4 py-3 text-center">
              <span
                v-if="div.diferenca_dias != null && div.diferenca_dias !== 0"
                class="text-xs text-amber-600"
              >
                {{ div.diferenca_dias > 0 ? '+' : '' }}{{ div.diferenca_dias }}d
              </span>
              <span
                v-else-if="div.diferenca_valor != null && Number(div.diferenca_valor) !== 0"
                class="text-xs text-red-600 tabular-nums"
              >
                {{ formatarValor(div.diferenca_valor) }}
              </span>
              <span v-else class="text-slate-300">—</span>
            </td>
            <td class="px-4 py-3">
              <ConciliacoesStatusDivergenciaBadge :status="div.status" />
            </td>
            <td class="px-4 py-3 text-center">
              <button
                class="text-xs text-blue-600 hover:text-blue-800 font-medium transition-colors px-2 py-1 rounded hover:bg-blue-50"
                @click="$emit('revisar', div)"
              >
                Revisar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Rodapé com contagem -->
    <div v-if="divergencias.length > 0" class="px-4 py-3 border-t border-slate-100 bg-slate-50 text-xs text-slate-400">
      {{ divergencias.length }} registro{{ divergencias.length !== 1 ? 's' : '' }} para revisão
    </div>

  </div>
</template>

<script setup lang="ts">
import type { Divergencia } from '~/types/divergencia'
import { labelTipoDivergencia } from '~/types/divergencia'

defineProps<{ divergencias: Divergencia[] }>()
defineEmits<{ revisar: [Divergencia] }>()

function labelTipo(tipo: string) {
  return labelTipoDivergencia(tipo)
}

function formatarValor(valor: number | null) {
  if (valor == null) return '—'
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(valor))
}
</script>
