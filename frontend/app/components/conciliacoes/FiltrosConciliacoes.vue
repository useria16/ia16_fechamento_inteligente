<template>
  <div class="bg-white rounded-xl border border-slate-200 p-4">
    <div class="flex flex-wrap gap-3">

      <!-- Busca -->
      <input
        v-model="filtros.busca"
        type="text"
        placeholder="Buscar por empresa ou tipo..."
        class="flex-1 min-w-48 px-3 py-2 text-sm border border-slate-200 rounded-lg text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <!-- Empresa — apenas admin_ia16 -->
      <select
        v-if="isAdmin"
        v-model="filtros.empresa_id"
        class="px-3 py-2 text-sm border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Todas as empresas</option>
        <option v-for="e in empresas" :key="e.id" :value="e.id">{{ e.nome }}</option>
      </select>

      <!-- Tipo -->
      <select
        v-model="filtros.tipo_conciliacao"
        class="px-3 py-2 text-sm border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Todos os tipos</option>
        <option v-for="t in tipos" :key="t" :value="t">{{ t }}</option>
      </select>

      <!-- Status -->
      <select
        v-model="filtros.status"
        class="px-3 py-2 text-sm border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Todos os status</option>
        <option v-for="(label, valor) in statusOpcoes" :key="valor" :value="valor">{{ label }}</option>
      </select>

      <!-- Limpar -->
      <button
        class="px-3 py-2 text-sm text-slate-500 hover:text-slate-700 transition-colors"
        @click="$emit('limpar')"
      >
        Limpar
      </button>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { FiltroConciliacoes } from '~/types/conciliacao'
import { statusConciliacaoLabels } from '~/utils/statusConciliacao'

defineProps<{
  filtros: FiltroConciliacoes
  isAdmin: boolean
}>()

defineEmits<{ limpar: [] }>()

const statusOpcoes = statusConciliacaoLabels

const empresas = [
  { id: 'e1', nome: 'Daxx Omnimedia' },
  { id: 'e2', nome: 'Cliente B' },
  { id: 'e3', nome: 'Cliente C' },
]

const tipos = ['Bancária', 'Caixa', 'Recebíveis', 'Adquirentes', 'Vendas']
</script>
