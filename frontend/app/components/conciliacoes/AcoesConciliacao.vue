<template>
  <div class="flex items-center gap-2 justify-end">
    <!-- Única ação visível na listagem: abrir o detalhe -->
    <NuxtLink
      :to="`/conciliacoes/${conciliacao.id}`"
      class="text-xs text-blue-600 hover:underline font-medium"
    >
      Ver
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import type { Conciliacao } from '~/types/conciliacao'
defineProps<{ conciliacao: Conciliacao }>()
</script>
