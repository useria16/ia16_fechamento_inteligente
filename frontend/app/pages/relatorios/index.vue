<template>
  <div class="p-6 space-y-6">

    <!-- Cabeçalho da página -->
    <div>
      <h1 class="text-xl font-semibold text-slate-800">Relatórios</h1>
      <p class="mt-1 text-sm text-slate-500">
        Exporte consolidados mensais e relatórios das conciliações financeiras.
      </p>
    </div>

    <!-- Grid de relatórios disponíveis -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">

      <!-- Consolidado mensal -->
      <RelatoriosFormularioConsolidadoMensal />

      <!-- Exportação diária — informativo -->
      <div class="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-slate-50 flex items-center justify-center shrink-0">
            <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-800">Exportação Diária</p>
            <p class="text-xs text-slate-500 mt-0.5">
              Para exportar uma conciliação individual, acesse a conciliação desejada.
            </p>
          </div>
        </div>
        <p class="text-xs text-slate-500">
          A exportação diária fica disponível dentro de cada conciliação após o processamento,
          no bloco <span class="font-medium text-slate-600">Pacote Final do Fechamento</span>.
        </p>
        <NuxtLink
          to="/conciliacoes"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          Ver conciliações
        </NuxtLink>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default', middleware: 'auth' })
</script>
