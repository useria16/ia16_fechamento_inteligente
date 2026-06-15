<template>
  <!-- Toolbar: filtros + salvar -->
  <div class="px-4 py-2.5 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2 bg-white">
    <div class="flex flex-wrap gap-1.5">
      <button
        v-for="op in filtroOpcoes"
        :key="op.valor"
        class="px-3 py-1 text-xs rounded-full border transition-colors"
        :class="filtroAtivo === op.valor
          ? 'bg-blue-600 text-white border-blue-600'
          : 'text-slate-600 border-slate-200 hover:bg-slate-50'"
        @click="filtroAtivo = op.valor"
      >
        {{ op.label }}
      </button>
    </div>
    <div class="flex items-center gap-3">
      <span v-if="temAlteracoes" class="text-xs text-amber-600 font-medium">
        {{ qtdAlterados }} linha{{ qtdAlterados > 1 ? 's' : '' }} com alterações
      </span>
      <button
        :disabled="!temAlteracoes || salvando"
        class="inline-flex items-center gap-2 px-4 py-1.5 text-sm font-medium rounded-lg transition-colors"
        :class="temAlteracoes && !salvando
          ? 'bg-blue-600 text-white hover:bg-blue-700'
          : 'bg-slate-100 text-slate-400 cursor-not-allowed'"
        @click="onSalvar"
      >
        <svg v-if="salvando" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        {{ salvando ? 'Salvando...' : 'Salvar alterações' }}
      </button>
    </div>
  </div>

  <!-- Planilha -->
  <div class="overflow-x-auto">
    <table class="border-collapse text-xs w-full" style="table-layout: fixed; min-width: 1140px">

      <!--
        Colunas numéricas/fixas têm largura explícita.
        As duas colunas de descrição (sem width) dividem o espaço restante.
        min-width: 1140px garante scroll horizontal em telas muito estreitas.
      -->
      <colgroup>
        <col style="width: 90px">   <!-- DATA -->
        <col>                        <!-- DESC BANCO — cresce com o container -->
        <col>                        <!-- DESC FORNECEDOR — cresce com o container -->
        <col style="width: 130px">  <!-- NF / DOC -->
        <col style="width: 130px">  <!-- VALOR NF/DOC -->
        <col style="width: 130px">  <!-- ENTRADA EXTRATO -->
        <col style="width: 130px">  <!-- SAÍDA EXTRATO -->
        <col style="width: 130px">  <!-- SALDO -->
        <col style="width: 170px">  <!-- iA16 -->
      </colgroup>

      <!-- Cabeçalho estilo Excel -->
      <thead>
        <tr style="background-color: #1F4E79">
          <th class="px-3 py-2 text-white font-semibold text-left whitespace-nowrap overflow-hidden border-r border-blue-800">DATA</th>
          <th class="px-3 py-2 text-white font-semibold text-left overflow-hidden border-r border-blue-800 truncate">DESCRIÇÃO LANÇAMENTO BANCO</th>
          <th class="px-3 py-2 text-white font-semibold text-left overflow-hidden border-r border-blue-800 truncate">DESCRIÇÃO FORNECEDOR/CLIENTE</th>
          <th class="px-3 py-2 text-white font-semibold text-left overflow-hidden border-r border-blue-800 whitespace-nowrap">NF / DOC</th>
          <th class="px-3 py-2 text-white font-semibold text-right overflow-hidden border-r border-blue-800 whitespace-nowrap">VALOR NF/DOC</th>
          <th class="px-3 py-2 text-white font-semibold text-right overflow-hidden border-r border-blue-800 whitespace-nowrap">ENTRADA</th>
          <th class="px-3 py-2 text-white font-semibold text-right overflow-hidden border-r border-blue-800 whitespace-nowrap">SAÍDA</th>
          <th class="px-3 py-2 text-white font-semibold text-right overflow-hidden border-r border-blue-900/60 whitespace-nowrap">SALDO</th>
          <!-- Indicador iA16 (status + fluxo) -->
          <th class="px-2 py-2 text-blue-200 font-medium text-center overflow-hidden" style="background-color: #152f4e">iA16</th>
        </tr>
      </thead>

      <tbody>
        <template v-for="(l, idx) in lancamentosFiltrados" :key="l.id">

          <!-- Linha principal -->
          <tr
            class="border-b border-slate-200 transition-colors"
            :class="[
              alteracoes[l.id] ? 'bg-amber-50' : (idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'),
              l.status_revisao === 'ignorado' ? 'opacity-40' : '',
            ]"
          >
            <!-- DATA (somente leitura) -->
            <td class="px-3 py-1.5 text-slate-600 whitespace-nowrap border-r border-slate-200 font-mono tabular-nums">
              {{ formatarData(l.data_lancamento) }}
            </td>

            <!-- DESCRIÇÃO BANCO (somente leitura) -->
            <td class="px-3 py-1.5 text-slate-800 border-r border-slate-200 overflow-hidden">
              <p class="truncate" :title="l.descricao_banco">{{ l.descricao_banco }}</p>
            </td>

            <!-- DESCRIÇÃO FORNECEDOR/CLIENTE (editável) -->
            <td class="p-0 border-r border-slate-200 overflow-hidden">
              <input
                type="text"
                :value="getValor(l.id, 'descricao_negocio') ?? l.descricao_negocio ?? ''"
                :placeholder="l.razao_social ?? ''"
                class="w-full min-w-0 px-3 py-1.5 bg-transparent outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 focus:bg-white text-slate-900 placeholder:text-slate-400"
                @input="e => marcar(l.id, 'descricao_negocio', (e.target as HTMLInputElement).value)"
              />
            </td>

            <!-- NF / DOC (editável) -->
            <td class="p-0 border-r border-slate-200 overflow-hidden">
              <input
                type="text"
                :value="getValor(l.id, 'nf_doc') ?? l.nf_doc ?? ''"
                placeholder="—"
                class="w-full min-w-0 px-3 py-1.5 bg-transparent outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 focus:bg-white text-slate-900 placeholder:text-slate-400"
                @input="e => marcar(l.id, 'nf_doc', (e.target as HTMLInputElement).value)"
              />
            </td>

            <!-- VALOR NF/DOC (editável numérico) -->
            <td class="p-0 border-r border-slate-200 overflow-hidden">
              <input
                type="text"
                inputmode="decimal"
                :value="getValor(l.id, 'valor_nf_doc') ?? (l.valor_nf_doc != null ? String(l.valor_nf_doc) : '')"
                placeholder="—"
                class="w-full min-w-0 px-3 py-1.5 bg-transparent outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 focus:bg-white text-slate-900 placeholder:text-slate-400 text-right font-mono"
                @input="e => marcar(l.id, 'valor_nf_doc', (e.target as HTMLInputElement).value)"
              />
            </td>

            <!-- ENTRADA EXTRATO (somente leitura) -->
            <td class="px-3 py-1.5 text-right border-r border-slate-200 whitespace-nowrap font-mono tabular-nums">
              <span v-if="l.tipo_movimento === 'entrada'" class="text-green-700 font-medium">
                {{ fmtValor(l.valor) }}
              </span>
            </td>

            <!-- SAÍDA EXTRATO (somente leitura) -->
            <td class="px-3 py-1.5 text-right border-r border-slate-200 whitespace-nowrap font-mono tabular-nums">
              <span v-if="l.tipo_movimento === 'saida'" class="text-red-600 font-medium">
                {{ fmtValor(l.valor) }}
              </span>
            </td>

            <!-- SALDO (somente leitura) -->
            <td class="px-3 py-1.5 text-right border-r border-slate-100 whitespace-nowrap font-mono tabular-nums"
                :class="l.saldo != null && l.saldo < 0 ? 'text-red-600' : 'text-slate-700'">
              {{ l.saldo != null ? fmtValor(l.saldo) : '—' }}
            </td>

            <!-- Indicador iA16: status + fluxo + toggle expand -->
            <td class="px-2 py-1.5 text-center border-l border-slate-300 bg-slate-50/60">
              <button
                class="inline-flex items-center justify-center gap-1 w-full"
                @click="toggleExpandido(l.id)"
              >
                <!-- Status dot -->
                <span
                  class="w-2 h-2 rounded-full flex-shrink-0"
                  :class="statusPonto(l.status_revisao)"
                  :title="l.status_revisao"
                />
                <!-- Fluxo badge compacto -->
                <span
                  v-if="l.tipo_conferencia_fluxo"
                  class="text-xs px-1.5 py-0.5 rounded font-medium leading-none"
                  :class="CONFERENCIA_CLASSES[l.tipo_conferencia_fluxo]"
                  :title="l.observacao_sistema ?? ''"
                >
                  {{ CONFERENCIA_LABELS[l.tipo_conferencia_fluxo] }}
                </span>
                <!-- Seta expand -->
                <svg
                  class="w-3 h-3 text-slate-400 transition-transform flex-shrink-0"
                  :class="expandidos.has(l.id) ? 'rotate-90' : ''"
                  fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </td>
          </tr>

          <!-- Painel de assistência iA16 (expandível) -->
          <tr v-if="expandidos.has(l.id)" class="bg-slate-50 border-b border-slate-200">
            <td colspan="9" class="px-6 py-3">
              <div class="flex flex-wrap items-start gap-6">

                <!-- Status -->
                <div class="flex flex-col gap-1 min-w-[130px]">
                  <label class="text-slate-400 font-semibold uppercase text-xs tracking-wide">Status</label>
                  <select
                    :value="getValor(l.id, 'status_revisao') ?? l.status_revisao"
                    class="border border-slate-200 rounded px-2 py-1 text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-400"
                    :class="statusSelectClasse(String(getValor(l.id, 'status_revisao') ?? l.status_revisao))"
                    @change="e => marcar(l.id, 'status_revisao', (e.target as HTMLSelectElement).value)"
                  >
                    <option value="pendente">Pendente</option>
                    <option value="em_revisao">Em revisão</option>
                    <option value="revisado">Revisado</option>
                    <option value="ignorado">Ignorado</option>
                  </select>
                </div>

                <!-- Categoria -->
                <div class="flex flex-col gap-1 flex-1 min-w-[150px] max-w-[250px]">
                  <label class="text-slate-400 font-semibold uppercase text-xs tracking-wide">Categoria</label>
                  <input
                    type="text"
                    :value="getValor(l.id, 'categoria') ?? l.categoria ?? ''"
                    :placeholder="l.categoria_sugerida ?? 'Categoria'"
                    class="border border-slate-200 rounded px-2 py-1 text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-400 text-slate-900 placeholder:text-slate-400"
                    @input="e => marcar(l.id, 'categoria', (e.target as HTMLInputElement).value)"
                  />
                  <button
                    v-if="l.categoria_sugerida && !getValor(l.id, 'categoria') && !l.categoria"
                    class="text-left text-blue-500 text-xs hover:underline"
                    @click="marcar(l.id, 'categoria', l.categoria_sugerida)"
                  >
                    Usar sugestão: {{ l.categoria_sugerida }}
                  </button>
                </div>

                <!-- Observação -->
                <div class="flex flex-col gap-1 flex-1 min-w-[180px] max-w-[320px]">
                  <label class="text-slate-400 font-semibold uppercase text-xs tracking-wide">Observação</label>
                  <input
                    type="text"
                    :value="getValor(l.id, 'observacao') ?? l.observacao ?? ''"
                    placeholder="Observação livre"
                    class="border border-slate-200 rounded px-2 py-1 text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-400 text-slate-900 placeholder:text-slate-400"
                    @input="e => marcar(l.id, 'observacao', (e.target as HTMLInputElement).value)"
                  />
                </div>

                <!-- Conferência com fluxo -->
                <div v-if="l.tipo_conferencia_fluxo" class="flex flex-col gap-1 flex-1 min-w-[200px]">
                  <label class="text-slate-400 font-semibold uppercase text-xs tracking-wide">Conferência com Fluxo</label>
                  <div class="flex items-center gap-2 flex-wrap">
                    <span
                      class="px-2 py-0.5 rounded-full text-xs font-medium"
                      :class="CONFERENCIA_CLASSES[l.tipo_conferencia_fluxo]"
                    >
                      {{ CONFERENCIA_LABELS_MODAL[l.tipo_conferencia_fluxo] }}
                    </span>
                  </div>
                  <p v-if="l.observacao_sistema" class="text-slate-600 text-xs leading-relaxed">
                    {{ l.observacao_sistema }}
                  </p>
                  <p v-if="l.descricao_prevista || l.data_prevista" class="text-slate-500 text-xs">
                    <span v-if="l.descricao_prevista">{{ l.descricao_prevista }}</span>
                    <span v-if="l.data_prevista"> · {{ l.data_prevista }}</span>
                    <span v-if="l.valor_previsto"> · R$ {{ fmtValor(l.valor_previsto) }}</span>
                  </p>
                </div>

              </div>
            </td>
          </tr>

        </template>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { AtualizarLancamentoAnotado, LancamentoExtratoAnotado, StatusRevisao } from '~/types/extratoAnotado'
import { CONFERENCIA_LABELS, CONFERENCIA_LABELS_MODAL, CONFERENCIA_CLASSES } from '~/types/extratoAnotado'

const props = defineProps<{
  lancamentos: LancamentoExtratoAnotado[]
  salvando?: boolean
}>()

const emit = defineEmits<{
  salvar: [batch: Array<{ id: string; dados: AtualizarLancamentoAnotado }>]
}>()

// ── Filtro ───────────────────────────────────────────────────────────────────

const filtroAtivo = ref('todos')
const filtroOpcoes = [
  { valor: 'todos',    label: 'Todos' },
  { valor: 'pendente', label: 'Pendentes' },
  { valor: 'revisado', label: 'Revisados' },
  { valor: 'ignorado', label: 'Ignorados' },
]

const lancamentosFiltrados = computed(() =>
  filtroAtivo.value === 'todos'
    ? props.lancamentos
    : props.lancamentos.filter(l => l.status_revisao === filtroAtivo.value),
)

// ── Expandir linhas (painel iA16) ─────────────────────────────────────────────

const expandidos = ref(new Set<string>())

function toggleExpandido(id: string) {
  if (expandidos.value.has(id)) {
    expandidos.value.delete(id)
  } else {
    expandidos.value.add(id)
  }
}

// ── Alterações locais ─────────────────────────────────────────────────────────

const alteracoes = ref<Record<string, Record<string, string | null>>>({})

function getValor(id: string, campo: string): string | null | undefined {
  return alteracoes.value[id]?.[campo]
}

function marcar(id: string, campo: string, valor: string) {
  if (!alteracoes.value[id]) alteracoes.value[id] = {}
  alteracoes.value[id][campo] = valor
}

const temAlteracoes = computed(() => Object.keys(alteracoes.value).length > 0)
const qtdAlterados  = computed(() => Object.keys(alteracoes.value).length)

function limparAlteracoes() {
  alteracoes.value = {}
}

defineExpose({ limparAlteracoes })

// ── Montar batch e emitir ─────────────────────────────────────────────────────

function normStr(v: string | null | undefined): string | null {
  if (v == null) return null
  const t = String(v).trim()
  return t || null
}

function normNum(v: string | null | undefined): number | null {
  if (v == null || String(v).trim() === '') return null
  const n = parseFloat(String(v).replace(',', '.'))
  return isNaN(n) ? null : n
}

function onSalvar() {
  const batch = Object.entries(alteracoes.value).map(([id, campos]) => {
    const dados: AtualizarLancamentoAnotado = {}
    if ('descricao_negocio' in campos) dados.descricao_negocio = normStr(campos.descricao_negocio)
    if ('nf_doc'            in campos) dados.nf_doc            = normStr(campos.nf_doc)
    if ('valor_nf_doc'      in campos) dados.valor_nf_doc      = normNum(campos.valor_nf_doc)
    if ('categoria'         in campos) dados.categoria         = normStr(campos.categoria)
    if ('observacao'        in campos) dados.observacao        = normStr(campos.observacao)
    if ('status_revisao'    in campos) dados.status_revisao    = campos.status_revisao as StatusRevisao
    return { id, dados }
  })
  emit('salvar', batch)
}

// ── Helpers visuais ───────────────────────────────────────────────────────────

function fmtValor(v: unknown): string {
  const n = Number(v ?? 0)
  return isNaN(n) ? '—' : n.toFixed(2)
}

function formatarData(d: string): string {
  if (!d) return '—'
  // Formato: DD/MM/YYYY se for ISO
  const parts = d.split('-')
  if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`
  return d
}

function statusPonto(s: string): string {
  return {
    pendente:   'bg-amber-400',
    em_revisao: 'bg-blue-400',
    revisado:   'bg-green-500',
    ignorado:   'bg-slate-300',
  }[s] ?? 'bg-slate-300'
}

function statusSelectClasse(s: string): string {
  return {
    pendente:   'text-amber-700',
    em_revisao: 'text-blue-700',
    revisado:   'text-green-700',
    ignorado:   'text-slate-400',
  }[s] ?? 'text-slate-700'
}
</script>
