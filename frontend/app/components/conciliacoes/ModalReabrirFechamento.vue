<template>
  <Teleport to="body">
    <div
      v-if="aberto"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4"
      @click.self="$emit('fechar')"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-5">

        <!-- Cabeçalho -->
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <h2 class="text-base font-semibold text-slate-800">Reabrir fechamento</h2>
          </div>
          <button class="text-slate-400 hover:text-slate-600 transition-colors" @click="$emit('fechar')">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Descrição -->
        <p class="text-sm text-slate-500">
          O fechamento voltará para revisão. Os arquivos, itens e divergências não serão apagados.
        </p>

        <!-- Campo motivo -->
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-slate-700">
            Motivo da reabertura
            <span class="text-slate-400 font-normal">(opcional)</span>
          </label>
          <textarea
            v-model="motivo"
            rows="3"
            :disabled="confirmando"
            placeholder="Exemplo: Foi necessário revisar uma divergência após a aprovação."
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none disabled:opacity-60 disabled:bg-slate-50"
          />
        </div>

        <!-- Erro -->
        <div
          v-if="erro"
          class="flex items-start gap-2 rounded-lg bg-red-50 border border-red-200 px-3 py-2.5 text-sm text-red-700"
        >
          <svg class="w-4 h-4 mt-0.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
          <span>{{ erro }}</span>
        </div>

        <!-- Botões -->
        <div class="flex justify-end gap-3 pt-1">
          <button
            :disabled="confirmando"
            class="px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-60"
            @click="$emit('fechar')"
          >
            Cancelar
          </button>
          <button
            :disabled="confirmando"
            class="px-4 py-2 text-sm font-medium text-white bg-amber-600 rounded-lg hover:bg-amber-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
            @click="confirmar"
          >
            <svg v-if="confirmando" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ confirmando ? 'Reabrindo...' : 'Confirmar reabertura' }}
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
const props = defineProps<{
  aberto: boolean
  confirmando: boolean
  erro?: string | null
}>()

const emit = defineEmits<{
  fechar: []
  confirmar: [motivo: string | null]
}>()

const motivo = ref('')

watch(() => props.aberto, (aberto) => {
  if (aberto) motivo.value = ''
})

function confirmar() {
  emit('confirmar', motivo.value.trim() || null)
}
</script>
