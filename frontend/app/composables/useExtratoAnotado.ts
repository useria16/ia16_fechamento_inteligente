import type { AtualizarLancamentoAnotado, LancamentoExtratoAnotado } from '~/types/extratoAnotado'

function normalizarLancamento(l: Record<string, unknown>): LancamentoExtratoAnotado {
  return {
    ...(l as unknown as LancamentoExtratoAnotado),
    valor: Number(l.valor ?? 0),
    saldo: l.saldo == null ? null : Number(l.saldo),
    confianca_sugestao: l.confianca_sugestao == null ? null : Number(l.confianca_sugestao),
    confianca_conferencia: l.confianca_conferencia == null ? null : Number(l.confianca_conferencia),
    valor_previsto: l.valor_previsto == null ? null : Number(l.valor_previsto),
    valor_nf_doc: l.valor_nf_doc == null ? null : Number(l.valor_nf_doc),
  }
}

export function useExtratoAnotado(conciliacaoId: string) {
  const api = useApi()

  const lancamentos = ref<LancamentoExtratoAnotado[]>([])
  const carregando = ref(false)
  const atualizando = ref(false)
  const erro = ref<string | null>(null)

  const contadores = computed(() => ({
    total:        lancamentos.value.length,
    pendentes:    lancamentos.value.filter(l => l.status_revisao === 'pendente').length,
    revisados:    lancamentos.value.filter(l => l.status_revisao === 'revisado').length,
    ignorados:    lancamentos.value.filter(l => l.status_revisao === 'ignorado').length,
    em_revisao:   lancamentos.value.filter(l => l.status_revisao === 'em_revisao').length,
    no_fluxo:     lancamentos.value.filter(l => l.tipo_conferencia_fluxo === 'encontrado').length,
    nao_localizado: lancamentos.value.filter(l => l.tipo_conferencia_fluxo === 'nao_encontrado').length,
    para_revisar: lancamentos.value.filter(l => l.tipo_conferencia_fluxo === 'possivel_correspondencia' || l.tipo_conferencia_fluxo === 'data_diferente').length,
  }))

  const totalEntradas = computed(() =>
    lancamentos.value.filter(l => l.tipo_movimento === 'entrada').reduce((s, l) => s + Number(l.valor ?? 0), 0)
  )
  const totalSaidas = computed(() =>
    lancamentos.value.filter(l => l.tipo_movimento === 'saida').reduce((s, l) => s + Number(l.valor ?? 0), 0)
  )

  async function carregar() {
    carregando.value = true
    erro.value = null
    try {
      const resposta = await api.get<{ sucesso: boolean; dados: LancamentoExtratoAnotado[]; paginacao: any }>(
        `/api/v1/conciliacoes/${conciliacaoId}/extrato-anotado?limite=200`,
      )
      lancamentos.value = (resposta.dados ?? []).map(l => normalizarLancamento(l as unknown as Record<string, unknown>))
    } catch (e: any) {
      erro.value = e.message ?? 'Não foi possível carregar os lançamentos.'
    } finally {
      carregando.value = false
    }
  }

  async function anotar(lancamentoId: string, dados: AtualizarLancamentoAnotado): Promise<LancamentoExtratoAnotado | null> {
    atualizando.value = true
    try {
      const resposta = await api.patch<{ sucesso: boolean; dados: LancamentoExtratoAnotado }>(
        `/api/v1/extrato-anotado/${lancamentoId}`,
        dados,
      )
      const atualizado = normalizarLancamento(resposta.dados as unknown as Record<string, unknown>)
      const idx = lancamentos.value.findIndex(l => l.id === lancamentoId)
      if (idx !== -1) lancamentos.value.splice(idx, 1, atualizado)
      return atualizado
    } catch (e: any) {
      erro.value = e.message ?? 'Não foi possível atualizar o lançamento.'
      return null
    } finally {
      atualizando.value = false
    }
  }

  return {
    lancamentos,
    carregando,
    atualizando,
    erro,
    contadores,
    totalEntradas,
    totalSaidas,
    carregar,
    anotar,
  }
}
