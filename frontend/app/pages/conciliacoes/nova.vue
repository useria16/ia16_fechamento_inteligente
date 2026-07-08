<template>
  <div class="p-6 max-w-2xl">

    <!-- Cabeçalho -->
    <div class="mb-6">
      <NuxtLink to="/conciliacoes" class="text-sm text-slate-400 hover:text-slate-600 transition-colors">
        ← Conciliações
      </NuxtLink>
      <h1 class="text-2xl font-semibold text-slate-800 mt-2">Nova Conciliação</h1>
      <p class="text-sm text-slate-500 mt-1">Preencha os dados para iniciar uma nova conciliação.</p>
    </div>

    <!-- Formulário em card -->
    <div class="bg-white rounded-xl border border-slate-200 p-6">
      <ConciliacoesFormularioNovaConciliacao
        :is-admin="auth.perfil === 'admin_ia16'"
        @cancelar="navigateTo('/conciliacoes')"
        @criada="onCriada"
      />
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "default", middleware: "auth" })

const auth = useAuthStore()

function onCriada(id: string) {
  navigateTo(`/conciliacoes/${id}`)
}
</script>
