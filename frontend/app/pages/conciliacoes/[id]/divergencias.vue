<template>
  <div class="p-6 space-y-6">

    <!-- Breadcrumb -->
    <nav class="flex items-center gap-1.5 text-sm text-slate-400">
      <NuxtLink to="/conciliacoes" class="hover:text-slate-600 transition-colors">Conciliações</NuxtLink>
      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
      </svg>
      <NuxtLink :to="`/conciliacoes/${route.params.id}`" class="hover:text-slate-600 transition-colors">
        Detalhe
      </NuxtLink>
      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
      </svg>
      <span class="text-slate-600">Divergências</span>
    </nav>

    <!-- Título -->
    <div>
      <h1 class="text-2xl font-semibold text-slate-800">Divergências do fechamento</h1>
      <p class="text-sm text-slate-500 mt-1">Revise as pendências encontradas na preparação automática do fechamento.</p>
    </div>

    <!-- Carregando -->
    <div v-if="carregando" class="text-sm text-slate-400 py-8 text-center">Carregando divergências...</div>

    <!-- Erro -->
    <div v-else-if="erro" class="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3">
      {{ erro }}
    </div>

    <template v-else>

      <!-- Resumo de registros para revisão -->
      <div v-if="breakdownTipo.total > 0" class="flex flex-wrap items-center gap-4 bg-slate-50 rounded-xl border border-slate-200 px-5 py-3 text-sm">
        <span class="font-semibold text-slate-700">
          {{ breakdownTipo.total }} registro{{ breakdownTipo.total !== 1 ? 's' : '' }} para revisão
        </span>
        <span class="text-slate-300">|</span>
        <span class="text-red-600 font-medium">{{ breakdownTipo.divergencias }} divergência{{ breakdownTipo.divergencias !== 1 ? 's' : '' }} encontrada{{ breakdownTipo.divergencias !== 1 ? 's' : '' }}</span>
        <span v-if="breakdownTipo.pendentes > 0" class="text-slate-300">|</span>
        <span v-if="breakdownTipo.pendentes > 0" class="text-amber-600 font-medium">{{ breakdownTipo.pendentes }} pendência{{ breakdownTipo.pendentes !== 1 ? 's' : '' }} para análise manual</span>
      </div>

      <!-- Contadores por status -->
      <div class="flex flex-wrap gap-3">
        <button
          v-for="item in statusCards"
          :key="item.valor"
          :class="[
            'px-4 py-2.5 rounded-xl border text-sm font-medium transition-all',
            filtros.status === item.valor
              ? 'bg-blue-600 border-blue-600 text-white shadow-sm'
              : 'bg-white border-slate-200 text-slate-600 hover:border-blue-300 hover:text-blue-600',
          ]"
          @click="toggleFiltroStatus(item.valor)"
        >
          {{ item.label }}
          <span
            :class="[
              'ml-1.5 inline-flex items-center justify-center w-5 h-5 rounded-full text-xs',
              filtros.status === item.valor ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-500',
            ]"
          >
            {{ item.qtd }}
          </span>
        </button>
      </div>

      <!-- Filtros detalhados -->
      <ConciliacoesFiltrosDivergencias
        v-model="filtros"
        @limpar="limparFiltros"
      />

      <!-- Feedback de salvar -->
      <div
        v-if="feedbackRevisao"
        :class="[
          'flex items-center gap-2 text-sm rounded-lg px-4 py-3 border',
          feedbackRevisao.tipo === 'sucesso'
            ? 'bg-green-50 border-green-200 text-green-700'
            : 'bg-red-50 border-red-200 text-red-600',
        ]"
      >
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path v-if="feedbackRevisao.tipo === 'sucesso'" stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
        {{ feedbackRevisao.mensagem }}
      </div>

      <!-- Tabela -->
      <ConciliacoesTabelaDivergencias
        :divergencias="divergencias"
        @revisar="abrirModal"
      />

    </template>

    <!-- Modal de revisão -->
    <ConciliacoesModalRevisaoDivergencia
      :divergencia="divergenciaSelecionada"
      :salvando="salvando"
      @fechar="fecharModal"
      @salvar="onSalvar"
    />

  </div>
</template>

<script setup lang="ts">
import type { Divergencia, StatusDivergencia } from '~/types/divergencia'

definePageMeta({ layout: 'default', middleware: 'auth' })

const route = useRoute()
const conciliacaoId = route.params.id as string

const {
  divergencias,
  todasDivergencias,
  contadores,
  filtros,
  carregando,
  erro,
  carregarDivergencias,
  atualizarDivergencia,
  limparFiltros,
} = useResultadoConciliacao(conciliacaoId)

const divergenciaSelecionada = ref<Divergencia | null>(null)
const salvando = ref(false)
const feedbackRevisao = ref<{ tipo: 'sucesso' | 'erro'; mensagem: string } | null>(null)

// Breakdown por tipo: separa divergências de pendências para análise
const breakdownTipo = computed(() => {
  const todos = todasDivergencias.value
  const pendentes = todos.filter(d => d.tipo_divergencia === 'pendente_analise_manual').length
  const divergencias_reais = todos.length - pendentes
  return { total: todos.length, divergencias: divergencias_reais, pendentes }
})

const statusCards = computed(() => [
  { label: 'Todos', valor: '' as StatusDivergencia | '', qtd: contadores.value.total },
  { label: 'Abertas', valor: 'aberta' as StatusDivergencia, qtd: contadores.value.abertas },
  { label: 'Em análise', valor: 'em_analise' as StatusDivergencia, qtd: contadores.value.em_analise },
  { label: 'Resolvidas', valor: 'resolvida' as StatusDivergencia, qtd: contadores.value.resolvidas },
  { label: 'Ignoradas', valor: 'ignorada' as StatusDivergencia, qtd: contadores.value.ignoradas },
])

function toggleFiltroStatus(valor: StatusDivergencia | '') {
  filtros.value.status = filtros.value.status === valor ? '' : valor
}

function abrirModal(div: Divergencia) {
  divergenciaSelecionada.value = div
  feedbackRevisao.value = null
}

function fecharModal() {
  divergenciaSelecionada.value = null
}

async function onSalvar(payload: { status: StatusDivergencia; observacao: string }) {
  if (!divergenciaSelecionada.value) return
  salvando.value = true
  try {
    const dados: Record<string, unknown> = {}
    if (payload.status !== divergenciaSelecionada.value.status) {
      dados.status = payload.status
    }
    if (payload.observacao !== (divergenciaSelecionada.value.observacao ?? '')) {
      dados.observacao = payload.observacao
    }
    if (Object.keys(dados).length === 0) {
      fecharModal()
      return
    }
    await atualizarDivergencia(divergenciaSelecionada.value.id, dados)
    feedbackRevisao.value = { tipo: 'sucesso', mensagem: 'Revisão salva com sucesso.' }
    fecharModal()
    setTimeout(() => { feedbackRevisao.value = null }, 4000)
  } catch (e: any) {
    feedbackRevisao.value = {
      tipo: 'erro',
      mensagem: e?.data?.erro?.mensagem ?? e?.message ?? 'Não foi possível salvar a revisão.',
    }
  } finally {
    salvando.value = false
  }
}

onMounted(() => carregarDivergencias())
</script>
