<template>
  <div class="p-6 space-y-6">

    <!-- Breadcrumb -->
    <NuxtLink to="/conciliacoes" class="inline-flex items-center gap-1 text-sm text-slate-400 hover:text-slate-600 transition-colors">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
      </svg>
      Conciliações
    </NuxtLink>

    <!-- Carregando -->
    <div v-if="carregando" class="text-sm text-slate-400">Carregando conciliação...</div>

    <!-- Erro -->
    <div v-else-if="erro" class="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3">
      {{ erro }}
    </div>

    <template v-else-if="conciliacao">

      <!-- Título + ações -->
      <div class="flex items-start justify-between gap-4">
        <div>
          <h1 class="text-2xl font-semibold text-slate-800">Detalhe da Conciliação</h1>
          <p class="text-sm text-slate-500 mt-1">{{ conciliacao.titulo }}</p>
        </div>
        <ConciliacoesAcoesPrincipaisConciliacao
          :status="conciliacao.status"
          :processando="processando"
          :arquivos-minimos-presentes="arquivosMinimosPresentes"
          :tipo-conciliacao="conciliacao.tipo_conciliacao"
          @enviar-arquivos="onEnviarArquivos"
          @processar="onProcessar"
          @revisar-divergencias="onRevisarDivergencias"
          @revisar-extrato-anotado="onRevisarExtratoAnotado"
          @ver-relatorio="onVerRelatorio"
          @reprocessar="onReprocessar"
          @cancelar="onCancelar"
        />
      </div>

      <!-- Feedback de processamento -->
      <div
        v-if="feedbackProcessamento"
        :class="[
          'flex items-start gap-3 rounded-lg border px-4 py-3 text-sm',
          feedbackProcessamento.tipo === 'sucesso'
            ? 'bg-green-50 border-green-200 text-green-700'
            : 'bg-red-50 border-red-200 text-red-600',
        ]"
      >
        <svg class="w-4 h-4 mt-0.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path v-if="feedbackProcessamento.tipo === 'sucesso'" stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        </svg>
        <span>{{ feedbackProcessamento.mensagem }}</span>
      </div>

      <!-- Dados principais -->
      <ConciliacoesDetalheConciliacao :conciliacao="conciliacao" />

      <!-- Resumo de revisão — apenas para fluxo bilateral -->
      <ConciliacoesResumoRevisaoFechamento
        v-if="(conciliacao.status === 'com_divergencias' || conciliacao.status === 'processado')
              && conciliacao.tipo_conciliacao !== 'extrato_anotado'"
        :conciliacao="conciliacao"
      />

      <!-- CTA de lançamentos — apenas para extrato_anotado após processamento -->
      <div
        v-if="conciliacao.tipo_conciliacao === 'extrato_anotado'
              && (conciliacao.status === 'com_divergencias' || conciliacao.status === 'processado')"
        class="bg-white rounded-xl border p-5 flex items-center justify-between gap-4"
        :class="temPendentesExtrato ? 'border-blue-100' : 'border-slate-200'"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
            :class="temPendentesExtrato ? 'bg-blue-50' : 'bg-green-50'"
          >
            <svg v-if="temPendentesExtrato" class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <svg v-else class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-800">
              {{ temPendentesExtrato ? 'Lançamentos prontos para revisão' : 'Extrato revisado' }}
            </p>
            <p class="text-xs text-slate-500 mt-0.5">
              {{ temPendentesExtrato
                 ? 'Revise categorias, observações, documentos e conferência com o fluxo de caixa.'
                 : 'Todos os lançamentos foram revisados ou ignorados. Pronto para aprovação.' }}
            </p>
          </div>
        </div>
        <NuxtLink
          :to="`/conciliacoes/${conciliacao.id}/extrato-anotado`"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors shrink-0"
          :class="temPendentesExtrato
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'border border-slate-200 text-slate-600 hover:bg-slate-50'"
        >
          {{ temPendentesExtrato ? 'Revisar lançamentos' : 'Ver lançamentos' }}
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </NuxtLink>
      </div>

      <!-- Pacote final do fechamento -->
      <ConciliacoesPacoteFinalFechamento
        v-if="mostrarPacoteFinal"
        :conciliacao="conciliacao"
        @atualizada="onConciliacaoAtualizada"
      />


      <!-- Cards de resumo do motor -->
      <ConciliacoesCardsResumoConciliacaoDetalhe :conciliacao="conciliacao" />

      <!-- Arquivos -->
      <ConciliacoesArquivosConciliacao
        :conciliacao-id="conciliacao.id"
        :status="conciliacao.status"
        @atualizada="onArquivosAtualizado"
      />

    </template>

  </div>
</template>

<script setup lang="ts">
import type { ConciliacaoDetalhe } from '~/types/conciliacao'
import type { ArquivoEnviado } from '~/types/arquivo'

definePageMeta({ layout: 'default', middleware: 'auth' })

const route = useRoute()
const { buscarPorId, processarConciliacao } = useConciliacoes()

const conciliacao = ref<ConciliacaoDetalhe | null>(null)
const carregando = ref(true)
const erro = ref<string | null>(null)
const processando = ref(false)
const feedbackProcessamento = ref<{ tipo: 'sucesso' | 'erro'; mensagem: string } | null>(null)

const STATUS_PACOTE_FINAL = new Set(['processado', 'com_divergencias', 'aprovado', 'reaberto'])
const mostrarPacoteFinal = computed(
  () => conciliacao.value != null && STATUS_PACOTE_FINAL.has(conciliacao.value.status),
)

// Para extrato_anotado: determina se há lançamentos pendentes de revisão.
// com_divergencias = itens aguardando; processado = todos revisados/ignorados.
const temPendentesExtrato = computed(() =>
  conciliacao.value?.status === 'com_divergencias',
)

const arquivosAtuais = ref<ArquivoEnviado[]>([])
const arquivosMinimosPresentes = computed(() => {
  const tipos = arquivosAtuais.value.filter(a => !a.excluido_em).map(a => a.tipo_arquivo)
  if (conciliacao.value?.tipo_conciliacao === 'extrato_anotado') {
    return tipos.includes('extrato_bancario')
  }
  return tipos.includes('extrato_bancario') && tipos.includes('planilha_interna')
})

async function recarregar() {
  try {
    conciliacao.value = await buscarPorId(route.params.id as string)
  } catch (e: any) {
    erro.value = e.message ?? 'Não foi possível carregar a conciliação.'
  }
}

onMounted(async () => {
  try {
    conciliacao.value = await buscarPorId(route.params.id as string)
  } catch (e: any) {
    erro.value = e.message ?? 'Não foi possível carregar a conciliação.'
  } finally {
    carregando.value = false
  }
})

async function onProcessar() {
  if (!conciliacao.value || processando.value) return
  processando.value = true
  feedbackProcessamento.value = null
  try {
    const resultado = await processarConciliacao(conciliacao.value.id)
    feedbackProcessamento.value = {
      tipo: 'sucesso',
      mensagem: resultado.mensagem_processamento,
    }
    await recarregar()
  } catch (e: any) {
    const mensagem = e?.data?.erro?.mensagem ?? e?.message ?? 'Erro ao processar conciliação.'
    feedbackProcessamento.value = { tipo: 'erro', mensagem }
    await recarregar()
  } finally {
    processando.value = false
  }
}

function onConciliacaoAtualizada(atualizada: ConciliacaoDetalhe) {
  conciliacao.value = atualizada
}

function onArquivosAtualizado(lista: ArquivoEnviado[]) {
  arquivosAtuais.value = lista
  recarregar()
}

function onEnviarArquivos() {
  const el = document.getElementById('secao-upload-arquivos')
  el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function onRevisarDivergencias() { navigateTo(`/conciliacoes/${route.params.id}/divergencias`) }
function onRevisarExtratoAnotado() { navigateTo(`/conciliacoes/${route.params.id}/extrato-anotado`) }
function onVerRelatorio()        { /* tratado pelo PacoteFinalFechamento */ }
function onReprocessar()         { onProcessar() }
function onCancelar()            { navigateTo('/conciliacoes') }
</script>
