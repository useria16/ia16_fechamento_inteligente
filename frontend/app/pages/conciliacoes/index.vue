<template>
  <div class="p-6 space-y-6">

    <!-- Cabeçalho -->
    <div class="flex items-start justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-800">Conciliações</h1>
        <p class="text-sm text-slate-500 mt-1">Gerencie as conciliações financeiras da sua empresa.</p>
      </div>
      <NuxtLink
        to="/conciliacoes/nova"
        class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
      >
        Nova Conciliação
      </NuxtLink>
    </div>

    <!-- Erro -->
    <div v-if="erro" class="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3">
      {{ erro }}
    </div>

    <!-- Carregando -->
    <div v-else-if="carregando" class="text-sm text-slate-400">
      Carregando conciliações...
    </div>

    <template v-else>
      <!-- Cards de resumo -->
      <ConciliacoesCardsResumoConciliacoes :resumo="resumo" />

      <!-- Filtros -->
      <ConciliacoesFiltrosConciliacoes
        :filtros="filtros"
        :is-admin="auth.perfil === 'admin_ia16'"
        @limpar="limparFiltros"
      />

      <!-- Tabela -->
      <ConciliacoesTabelaConciliacoes :conciliacoes="conciliacoes" />
    </template>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "default", middleware: "auth" })

const auth = useAuthStore()
const { conciliacoes, resumo, filtros, carregando, erro, carregar, limparFiltros } = useConciliacoes()

onMounted(carregar)
</script>
