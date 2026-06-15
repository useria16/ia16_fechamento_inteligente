<template>
  <Teleport to="body">
    <div
      v-if="aberto && lancamento"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4"
      @click.self="$emit('fechar')"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 space-y-5">

        <!-- Cabeçalho -->
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-base font-semibold text-slate-800">Anotar lançamento</h2>
            <p class="text-xs text-slate-500 mt-0.5">
              {{ lancamento.data_lancamento }} · {{ lancamento.descricao_banco }}
            </p>
          </div>
          <button class="text-slate-400 hover:text-slate-600" @click="$emit('fechar')">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Info do lançamento -->
        <div class="rounded-lg bg-slate-50 border border-slate-200 px-4 py-3 grid grid-cols-2 gap-2 text-xs">
          <div>
            <span class="text-slate-500">Valor:</span>
            <span class="ml-1 font-semibold" :class="lancamento.tipo_movimento === 'entrada' ? 'text-green-700' : 'text-red-700'">
              {{ lancamento.tipo_movimento === 'entrada' ? '+' : '-' }}
              R$ {{ fmtValor(lancamento.valor) }}
            </span>
          </div>
          <div v-if="lancamento.razao_social">
            <span class="text-slate-500">Razão social:</span>
            <span class="ml-1 text-slate-700">{{ lancamento.razao_social }}</span>
          </div>
          <div v-if="lancamento.categoria_sugerida" class="col-span-2">
            <span class="text-slate-500">Sugestão automática:</span>
            <span class="ml-1 text-blue-700 font-medium">{{ lancamento.categoria_sugerida }}</span>
            <button
              class="ml-2 text-xs text-blue-500 underline hover:no-underline"
              @click="usarSugestao"
            >
              Usar
            </button>
          </div>
        </div>

        <!-- Conferência com fluxo de caixa -->
        <div
          v-if="lancamento.tipo_conferencia_fluxo"
          class="rounded-lg border px-4 py-3 text-xs space-y-1.5"
          :class="conferenciaFundoClasse(lancamento.tipo_conferencia_fluxo)"
        >
          <div class="flex items-center gap-2">
            <span class="font-semibold text-slate-700">Conferência com fluxo:</span>
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              :class="CONFERENCIA_CLASSES[lancamento.tipo_conferencia_fluxo]"
            >
              {{ CONFERENCIA_LABELS_MODAL[lancamento.tipo_conferencia_fluxo] }}
            </span>
          </div>
          <p v-if="lancamento.observacao_sistema" class="text-slate-600">
            {{ lancamento.observacao_sistema }}
          </p>
          <div v-if="lancamento.data_prevista || lancamento.valor_previsto || lancamento.descricao_prevista" class="grid grid-cols-2 gap-x-4 gap-y-1 pt-1 border-t border-slate-200/60">
            <div v-if="lancamento.descricao_prevista" class="col-span-2">
              <span class="text-slate-500">Categoria no fluxo:</span>
              <span class="ml-1 text-slate-700 font-medium">{{ lancamento.descricao_prevista }}</span>
            </div>
            <div v-if="lancamento.data_prevista">
              <span class="text-slate-500">Data prevista:</span>
              <span class="ml-1 text-slate-700">{{ lancamento.data_prevista }}</span>
            </div>
            <div v-if="lancamento.valor_previsto">
              <span class="text-slate-500">Valor previsto:</span>
              <span class="ml-1 text-slate-700">R$ {{ fmtValor(lancamento.valor_previsto) }}</span>
            </div>
          </div>
        </div>

        <!-- Formulário -->
        <div class="space-y-3">
          <div>
            <label class="text-sm font-medium text-slate-700 mb-1 block">Categoria</label>
            <input
              v-model="form.categoria"
              type="text"
              placeholder="Ex: Pagamento, Receita operacional, Despesa..."
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="text-sm font-medium text-slate-700 mb-1 block">Descrição do fornecedor/cliente</label>
            <input
              v-model="form.descricao_negocio"
              type="text"
              placeholder="Ex: Fornecedor ABC - Serviços de limpeza Mai/26"
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-sm font-medium text-slate-700 mb-1 block">NF / Documento</label>
              <input
                v-model="form.nf_doc"
                type="text"
                placeholder="Ex: NF 1234"
                class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="text-sm font-medium text-slate-700 mb-1 block">Status</label>
              <select
                v-model="form.status_revisao"
                class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="pendente">Pendente</option>
                <option value="em_revisao">Em revisão</option>
                <option value="revisado">Revisado</option>
                <option value="ignorado">Ignorado</option>
              </select>
            </div>
          </div>
          <div>
            <label class="text-sm font-medium text-slate-700 mb-1 block">Observação</label>
            <textarea
              v-model="form.observacao"
              rows="2"
              placeholder="Observação livre sobre este lançamento..."
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>
        </div>

        <!-- Erro -->
        <div v-if="erro" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {{ erro }}
        </div>

        <!-- Botões -->
        <div class="flex justify-end gap-3 pt-1">
          <button
            :disabled="salvando"
            class="px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-60"
            @click="$emit('fechar')"
          >
            Cancelar
          </button>
          <button
            :disabled="salvando"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-60 flex items-center gap-2"
            @click="salvar"
          >
            <svg v-if="salvando" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ salvando ? 'Salvando...' : 'Salvar anotação' }}
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import type { LancamentoExtratoAnotado, StatusRevisao, TipoConferenciaFluxo } from '~/types/extratoAnotado'
import { CONFERENCIA_LABELS_MODAL, CONFERENCIA_CLASSES } from '~/types/extratoAnotado'

const props = defineProps<{
  aberto: boolean
  lancamento: LancamentoExtratoAnotado | null
  salvando: boolean
  erro?: string | null
}>()

const emit = defineEmits<{
  fechar: []
  salvar: [payload: {
    categoria: string | null
    descricao_negocio: string | null
    nf_doc: string | null
    observacao: string | null
    status_revisao: StatusRevisao
  }]
}>()

const form = reactive({
  categoria: '',
  descricao_negocio: '',
  nf_doc: '',
  observacao: '',
  status_revisao: 'pendente' as StatusRevisao,
})

watch(() => props.lancamento, (l) => {
  if (l) {
    form.categoria = l.categoria ?? l.categoria_sugerida ?? ''
    form.descricao_negocio = l.descricao_negocio ?? ''
    form.nf_doc = l.nf_doc ?? ''
    form.observacao = l.observacao ?? ''
    form.status_revisao = l.status_revisao
  }
}, { immediate: true })

function usarSugestao() {
  if (props.lancamento?.categoria_sugerida) {
    form.categoria = props.lancamento.categoria_sugerida
  }
}

function fmtValor(v: unknown): string {
  const n = Number(v ?? 0)
  return isNaN(n) ? '0.00' : n.toFixed(2)
}

function conferenciaFundoClasse(tipo: TipoConferenciaFluxo | null): string {
  if (!tipo) return 'bg-slate-50 border-slate-200'
  const map: Record<TipoConferenciaFluxo, string> = {
    encontrado:               'bg-green-50 border-green-200',
    data_diferente:           'bg-amber-50 border-amber-200',
    nao_encontrado:           'bg-red-50 border-red-200',
    valor_diferente:          'bg-orange-50 border-orange-200',
    possivel_correspondencia: 'bg-blue-50 border-blue-200',
    pendente_analise:         'bg-slate-50 border-slate-200',
  }
  return map[tipo] ?? 'bg-slate-50 border-slate-200'
}

function salvar() {
  emit('salvar', {
    categoria: form.categoria.trim() || null,
    descricao_negocio: form.descricao_negocio.trim() || null,
    nf_doc: form.nf_doc.trim() || null,
    observacao: form.observacao.trim() || null,
    status_revisao: form.status_revisao,
  })
}
</script>
