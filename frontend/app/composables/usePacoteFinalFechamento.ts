import type { AprovarFechamentoPayload, ReabrirFechamentoPayload, RespostaAprovacao, RespostaReabertura } from '~/types/aprovacaoFechamento'
import type { ConciliacaoDetalhe } from '~/types/conciliacao'

const STATUS_PODE_APROVAR = new Set(['processado', 'com_divergencias', 'reaberto'])
const STATUS_PODE_EXPORTAR = new Set(['processado', 'com_divergencias', 'aprovado', 'reaberto'])

export function usePacoteFinalFechamento(conciliacaoId: string, tipoConciliacao?: string) {
  const api = useApi()
  const isExtratoAnotado = tipoConciliacao === 'extrato_anotado'

  // Para fluxo bilateral: verificar divergências abertas
  const { contadores, carregando: carregandoDivergencias, carregarDivergencias } = useResultadoConciliacao(conciliacaoId)

  // Para extrato_anotado: verificar lançamentos pendentes
  const { contadores: contadoresExtrato, carregando: carregandoExtrato, carregar: carregarExtrato } = useExtratoAnotado(conciliacaoId)

  const carregandoPendencias = computed(() =>
    isExtratoAnotado ? carregandoExtrato.value : carregandoDivergencias.value,
  )

  const aprovando  = ref(false)
  const reabrindo  = ref(false)
  const exportando = ref(false)

  const erroAprovacao  = ref<string | null>(null)
  const erroReabertura = ref<string | null>(null)
  const erroExportacao = ref<string | null>(null)

  const temDivergenciasAbertas = computed(() => {
    if (isExtratoAnotado) {
      return contadoresExtrato.value.pendentes > 0 || contadoresExtrato.value.em_revisao > 0
    }
    return contadores.value.abertas > 0 || contadores.value.em_analise > 0
  })

  function podeAprovar(status: string)  { return STATUS_PODE_APROVAR.has(status) }
  function podeExportar(status: string) { return STATUS_PODE_EXPORTAR.has(status) }
  function podeReabrir(status: string)  { return status === 'aprovado' }

  async function aprovarFechamento(
    payload: AprovarFechamentoPayload,
  ): Promise<ConciliacaoDetalhe | null> {
    aprovando.value = true
    erroAprovacao.value = null
    try {
      const resposta = await api.post<{ sucesso: boolean; dados: RespostaAprovacao }>(
        `/api/v1/conciliacoes/${conciliacaoId}/aprovar`,
        payload,
      )
      const detalhe = await api.get<{ sucesso: boolean; dados: ConciliacaoDetalhe }>(
        `/api/v1/conciliacoes/${conciliacaoId}`,
      )
      return detalhe.dados
    } catch (e: any) {
      const codigoErro = (e?.data as any)?.erro?.codigo as string | undefined
      if (codigoErro === 'LANCAMENTOS_PENDENTES_IMPEDEM_APROVACAO') {
        erroAprovacao.value = 'Existem lançamentos pendentes de revisão. Revise ou ignore todos antes de aprovar o fechamento.'
      } else if (codigoErro === 'DIVERGENCIAS_ABERTAS_IMPEDEM_APROVACAO') {
        erroAprovacao.value = 'Existem divergências abertas ou em análise. Resolva ou ignore todas antes de aprovar o fechamento.'
      } else if (codigoErro === 'PERFIL_SEM_PERMISSAO_APROVACAO') {
        erroAprovacao.value = 'Seu perfil não tem permissão para aprovar fechamentos.'
      } else {
        erroAprovacao.value = (e?.data as any)?.erro?.mensagem ?? e?.message ?? 'Não foi possível aprovar o fechamento.'
      }
      return null
    } finally {
      aprovando.value = false
    }
  }

  async function reabrirFechamento(
    payload: ReabrirFechamentoPayload,
  ): Promise<ConciliacaoDetalhe | null> {
    reabrindo.value = true
    erroReabertura.value = null
    try {
      await api.post<{ sucesso: boolean; dados: RespostaReabertura }>(
        `/api/v1/conciliacoes/${conciliacaoId}/reabrir`,
        payload,
      )
      const detalhe = await api.get<{ sucesso: boolean; dados: ConciliacaoDetalhe }>(
        `/api/v1/conciliacoes/${conciliacaoId}`,
      )
      return detalhe.dados
    } catch (e: any) {
      const codigoErro = (e?.data as any)?.erro?.codigo as string | undefined
      if (codigoErro === 'FECHAMENTO_NAO_ESTA_APROVADO') {
        erroReabertura.value = 'Somente fechamentos aprovados podem ser reabertos.'
      } else if (codigoErro === 'PERFIL_SEM_PERMISSAO_REABERTURA') {
        erroReabertura.value = 'Seu perfil não tem permissão para reabrir fechamentos.'
      } else {
        erroReabertura.value = (e?.data as any)?.erro?.mensagem ?? e?.message ?? 'Não foi possível reabrir o fechamento.'
      }
      return null
    } finally {
      reabrindo.value = false
    }
  }

  async function exportarRelatorio(): Promise<boolean> {
    exportando.value = true
    erroExportacao.value = null
    try {
      await api.download(`/api/v1/conciliacoes/${conciliacaoId}/exportar`)
      return true
    } catch (e: any) {
      erroExportacao.value = (e?.data as any)?.erro?.mensagem ?? e?.message ?? 'Não foi possível exportar o relatório.'
      return false
    } finally {
      exportando.value = false
    }
  }

  async function carregarPendencias() {
    if (isExtratoAnotado) {
      await carregarExtrato()
    } else {
      await carregarDivergencias()
    }
  }

  return {
    // estado pendências (unificado)
    carregandoDivergencias: carregandoPendencias,
    temDivergenciasAbertas,
    carregarDivergencias: carregarPendencias,
    contadores,
    contadoresExtrato,
    // loading
    aprovando,
    reabrindo,
    exportando,
    // erros
    erroAprovacao,
    erroReabertura,
    erroExportacao,
    // guards
    podeAprovar,
    podeExportar,
    podeReabrir,
    // ações
    aprovarFechamento,
    reabrirFechamento,
    exportarRelatorio,
  }
}
