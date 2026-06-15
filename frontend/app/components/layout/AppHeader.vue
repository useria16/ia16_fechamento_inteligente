<template>
  <header class="h-14 shrink-0 flex items-center justify-between px-6 bg-white border-b border-slate-200 z-10">
    <div class="flex items-center gap-2">
      <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-600 font-bold text-white text-xs">
        iA
      </div>
      <span class="text-sm font-semibold text-slate-800">iA16</span>
      <span class="text-sm text-slate-700">Fechamento Inteligente</span>
    </div>
    <div class="flex items-center gap-3">
      <span class="text-xs text-slate-700">{{ auth.sessao?.user?.email }}</span>
      <button
        class="w-8 h-8 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center hover:bg-blue-700 transition-colors"
        @click="auth.sair()"
        title="Sair"
      >
        {{ inicial }}
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const inicial = computed(() => auth.sessao?.user?.email?.[0]?.toUpperCase() ?? "U")
</script>
