<template>
  <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">

    <!-- Vazia -->
    <div v-if="conciliacoes.length === 0" class="px-6 py-16 text-center text-slate-400 text-sm">
      Nenhuma conciliação encontrada.
    </div>

    <table v-else class="w-full text-sm">
      <thead>
        <tr class="border-b border-slate-100 text-xs text-slate-400 uppercase tracking-wide">
          <th class="text-left px-5 py-3 font-medium">Empresa</th>
          <th class="text-left px-5 py-3 font-medium">Tipo</th>
          <th class="text-left px-5 py-3 font-medium">Período</th>
          <th class="text-left px-5 py-3 font-medium">Status</th>
          <th class="text-center px-5 py-3 font-medium">Divergências</th>
          <th class="text-left px-5 py-3 font-medium">Criado em</th>
          <th class="text-right px-5 py-3 font-medium">Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="c in conciliacoes"
          :key="c.id"
          class="border-b border-slate-50 hover:bg-slate-50 transition-colors"
        >
          <td class="px-5 py-3 text-slate-800 font-medium">{{ c.empresa_nome }}</td>
          <td class="px-5 py-3 text-slate-500">{{ c.tipo_conciliacao }}</td>
          <td class="px-5 py-3 text-slate-500 whitespace-nowrap">{{ periodo(c) }}</td>
          <td class="px-5 py-3">
            <ConciliacoesStatusConciliacaoBadge :status="c.status" :tipo-conciliacao="c.tipo_conciliacao" />
          </td>
          <td class="px-5 py-3 text-center" :class="c.quantidade_divergencias > 0 ? 'text-red-500 font-semibold' : 'text-slate-400'">
            {{ c.quantidade_divergencias }}
          </td>
          <td class="px-5 py-3 text-slate-400 whitespace-nowrap">{{ dataFormatada(c.criado_em) }}</td>
          <td class="px-5 py-3">
            <ConciliacoesAcoesConciliacao :conciliacao="c" />
          </td>
        </tr>
      </tbody>
    </table>

  </div>
</template>

<script setup lang="ts">
import type { Conciliacao } from '~/types/conciliacao'

defineProps<{ conciliacoes: Conciliacao[] }>()

function periodo(c: Conciliacao): string {
  const ini = new Date(c.periodo_inicio).toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })
  const fim = new Date(c.periodo_fim).toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })
  return ini === fim ? ini : `${ini} – ${fim}`
}

function dataFormatada(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR')
}
</script>
