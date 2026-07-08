<template>
  <!-- Overlay -->
  <Teleport to="body">
    <div
      v-if="divergencia"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      @click.self="$emit('fechar')"
    >
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('fechar')" />

      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">

        <!-- Cabeçalho -->
        <div class="flex items-start justify-between p-6 border-b border-slate-100">
          <div>
            <p class="text-xs font-medium text-blue-600 uppercase tracking-wide mb-1">Revisão de divergência</p>
            <h2 class="text-base font-semibold text-slate-800">{{ labelTipo(divergencia.tipo_divergencia) }}</h2>
          </div>
          <button
            class="text-slate-400 hover:text-slate-600 transition-colors ml-4 shrink-0"
            @click="$emit('fechar')"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6 space-y-5">

          <!-- Badges -->
          <div class="flex items-center gap-2 flex-wrap">
            <ConciliacoesSeveridadeDivergenciaBadge :severidade="divergencia.severidade" />
            <ConciliacoesStatusDivergenciaBadge :status="divergencia.status" />
          </div>

          <!-- Descrição -->
          <div class="bg-slate-50 rounded-lg p-4">
            <p class="text-sm text-slate-700 leading-relaxed">{{ divergencia.descricao }}</p>
          </div>

          <!-- Valores/Datas -->
          <div v-if="temDados" class="grid grid-cols-2 gap-3 text-sm">
            <div v-if="divergencia.valor_previsto != null" class="space-y-0.5">
              <p class="text-xs text-slate-500">Valor previsto</p>
              <p class="font-medium text-slate-800 tabular-nums">{{ formatarValor(divergencia.valor_previsto) }}</p>
            </div>
            <div v-if="divergencia.valor_realizado != null" class="space-y-0.5">
              <p class="text-xs text-slate-500">Valor realizado</p>
              <p class="font-medium text-slate-800 tabular-nums">{{ formatarValor(divergencia.valor_realizado) }}</p>
            </div>
            <div v-if="divergencia.data_prevista" class="space-y-0.5">
              <p class="text-xs text-slate-500">Data prevista</p>
              <p class="font-medium text-slate-800">{{ formatarData(divergencia.data_prevista) }}</p>
            </div>
            <div v-if="divergencia.data_realizada" class="space-y-0.5">
              <p class="text-xs text-slate-500">Data realizada</p>
              <p class="font-medium text-slate-800">{{ formatarData(divergencia.data_realizada) }}</p>
            </div>
          </div>

          <!-- Formulário de revisão -->
          <div class="border-t border-slate-100 pt-5 space-y-4">
            <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Revisão</p>

            <!-- Status -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Status da revisão</label>
              <select
                v-model="form.status"
                class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                <option value="aberta">Aberta</option>
                <option value="em_analise">Em análise</option>
                <option value="resolvida">Resolvida</option>
                <option value="ignorada">Ignorada</option>
              </select>
            </div>

            <!-- Observação -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Observação</label>
              <textarea
                v-model="form.observacao"
                rows="3"
                placeholder="Descreva o resultado da análise, a decisão tomada ou orientações para o time financeiro..."
                class="w-full text-sm border border-slate-200 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              />
            </div>

            <!-- Feedback -->
            <div
              v-if="feedback"
              :class="[
                'text-sm rounded-lg px-4 py-2.5',
                feedback.tipo === 'sucesso'
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-red-50 text-red-600 border border-red-200',
              ]"
            >
              {{ feedback.mensagem }}
            </div>
          </div>
        </div>

        <!-- Rodapé -->
        <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-100 bg-slate-50 rounded-b-2xl">
          <button
            class="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 transition-colors"
            @click="$emit('fechar')"
          >
            Cancelar
          </button>
          <button
            :disabled="salvando"
            class="px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
            @click="salvar"
          >
            <svg v-if="salvando" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ salvando ? 'Salvando...' : 'Salvar revisão' }}
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import type { Divergencia, StatusDivergencia } from '~/types/divergencia'
import { labelTipoDivergencia } from '~/types/divergencia'

const props = defineProps<{
  divergencia: Divergencia | null
  salvando?: boolean
}>()

const emit = defineEmits<{
  fechar: []
  salvar: [{ status: StatusDivergencia; observacao: string }]
}>()

const form = reactive({
  status: '' as StatusDivergencia,
  observacao: '',
})

const feedback = ref<{ tipo: 'sucesso' | 'erro'; mensagem: string } | null>(null)

watch(() => props.divergencia, (div) => {
  if (div) {
    form.status = div.status
    form.observacao = div.observacao ?? ''
    feedback.value = null
  }
}, { immediate: true })

const temDados = computed(() => {
  const d = props.divergencia
  if (!d) return false
  return d.valor_previsto != null || d.valor_realizado != null || d.data_prevista || d.data_realizada
})

function labelTipo(tipo: string) {
  return labelTipoDivergencia(tipo)
}

function formatarValor(v: number | null) {
  if (v == null) return '—'
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(v))
}

function formatarData(d: string | null) {
  if (!d) return '—'
  return new Date(d + 'T00:00:00').toLocaleDateString('pt-BR')
}

function salvar() {
  emit('salvar', { status: form.status, observacao: form.observacao })
}
</script>
