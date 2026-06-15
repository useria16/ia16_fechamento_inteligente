<template>
  <div class="flex flex-wrap gap-3 items-end">

    <!-- Busca -->
    <div class="flex-1 min-w-[180px]">
      <label class="block text-xs text-slate-500 mb-1">Buscar</label>
      <input
        v-model="filtrosLocal.busca"
        type="text"
        placeholder="Descrição ou tipo..."
        class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>

    <!-- Status -->
    <div class="min-w-[140px]">
      <label class="block text-xs text-slate-500 mb-1">Status</label>
      <select
        v-model="filtrosLocal.status"
        class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
      >
        <option value="">Todos</option>
        <option value="aberta">Aberta</option>
        <option value="em_analise">Em análise</option>
        <option value="resolvida">Resolvida</option>
        <option value="ignorada">Ignorada</option>
      </select>
    </div>

    <!-- Tipo -->
    <div class="min-w-[180px]">
      <label class="block text-xs text-slate-500 mb-1">Tipo</label>
      <select
        v-model="filtrosLocal.tipo_divergencia"
        class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
      >
        <option value="">Todos</option>
        <option value="divergencia_data">Divergência de data</option>
        <option value="divergencia_valor">Divergência de valor</option>
        <option value="previsto_nao_realizado">Previsto não realizado</option>
        <option value="realizado_nao_previsto">Realizado não previsto</option>
        <option value="duplicidade_extrato">Duplicidade no extrato</option>
        <option value="duplicidade_fluxo">Duplicidade no fluxo</option>
        <option value="pendente_analise_manual">Pendente para análise</option>
      </select>
    </div>

    <!-- Severidade -->
    <div class="min-w-[120px]">
      <label class="block text-xs text-slate-500 mb-1">Severidade</label>
      <select
        v-model="filtrosLocal.severidade"
        class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
      >
        <option value="">Todas</option>
        <option value="alta">Alta</option>
        <option value="media">Média</option>
        <option value="baixa">Baixa</option>
      </select>
    </div>

    <!-- Limpar -->
    <button
      v-if="temFiltro"
      class="text-sm text-slate-500 hover:text-slate-800 px-3 py-2 transition-colors"
      @click="$emit('limpar')"
    >
      Limpar filtros
    </button>

  </div>
</template>

<script setup lang="ts">
import type { FiltroDivergencias } from '~/types/divergencia'

const props = defineProps<{ modelValue: FiltroDivergencias }>()
const emit = defineEmits<{
  'update:modelValue': [FiltroDivergencias]
  limpar: []
}>()

const filtrosLocal = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const temFiltro = computed(() =>
  !!(filtrosLocal.value.busca || filtrosLocal.value.status || filtrosLocal.value.tipo_divergencia || filtrosLocal.value.severidade)
)
</script>
