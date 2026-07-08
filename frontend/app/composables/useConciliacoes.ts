import type { Conciliacao, ConciliacaoDetalhe, FiltroConciliacoes, NovaConciliacao, ResumoConciliacoes, ResultadoProcessamentoConciliacao } from '~/types/conciliacao'

// TODO: substituir por chamada real da API quando contrato estiver implementado
// GET /api/v1/conciliacoes
// GET /api/v1/conciliacoes/resumo
const MOCK_CONCILIACOES: Conciliacao[] = [
  { id: '1', empresa_id: 'e1', empresa_nome: 'Daxx Omnimedia',  tipo_conciliacao: 'Bancária',    periodo_inicio: '2026-05-01', periodo_fim: '2026-05-31', status: 'aprovado',         quantidade_divergencias: 0,  criado_em: '2026-05-02T10:00:00Z' },
  { id: '2', empresa_id: 'e1', empresa_nome: 'Daxx Omnimedia',  tipo_conciliacao: 'Bancária',    periodo_inicio: '2026-04-01', periodo_fim: '2026-04-30', status: 'com_divergencias', quantidade_divergencias: 12, criado_em: '2026-04-02T10:00:00Z' },
  { id: '3', empresa_id: 'e2', empresa_nome: 'Cliente B',       tipo_conciliacao: 'Caixa',       periodo_inicio: '2026-05-01', periodo_fim: '2026-05-31', status: 'em_processamento', quantidade_divergencias: 0,  criado_em: '2026-05-03T09:00:00Z' },
  { id: '4', empresa_id: 'e2', empresa_nome: 'Cliente B',       tipo_conciliacao: 'Recebíveis',  periodo_inicio: '2026-05-01', periodo_fim: '2026-05-31', status: 'rascunho',         quantidade_divergencias: 0,  criado_em: '2026-05-04T08:00:00Z' },
  { id: '5', empresa_id: 'e3', empresa_nome: 'Cliente C',       tipo_conciliacao: 'Adquirentes', periodo_inicio: '2026-05-01', periodo_fim: '2026-05-31', status: 'com_divergencias', quantidade_divergencias: 7,  criado_em: '2026-05-01T11:00:00Z' },
  { id: '6', empresa_id: 'e1', empresa_nome: 'Daxx Omnimedia',  tipo_conciliacao: 'Bancária',    periodo_inicio: '2026-03-01', periodo_fim: '2026-03-31', status: 'aprovado',         quantidade_divergencias: 0,  criado_em: '2026-03-02T10:00:00Z' },
  { id: '7', empresa_id: 'e2', empresa_nome: 'Cliente B',       tipo_conciliacao: 'Caixa',       periodo_inicio: '2026-04-01', periodo_fim: '2026-04-30', status: 'processado',       quantidade_divergencias: 0,  criado_em: '2026-04-03T09:00:00Z' },
  { id: '8', empresa_id: 'e3', empresa_nome: 'Cliente C',       tipo_conciliacao: 'Vendas',      periodo_inicio: '2026-05-01', periodo_fim: '2026-05-31', status: 'arquivos_enviados',quantidade_divergencias: 0,  criado_em: '2026-05-05T14:00:00Z' },
  { id: '9', empresa_id: 'e1', empresa_nome: 'Daxx Omnimedia',  tipo_conciliacao: 'Bancária',    periodo_inicio: '2026-02-01', periodo_fim: '2026-02-28', status: 'cancelado',        quantidade_divergencias: 0,  criado_em: '2026-02-02T10:00:00Z' },
  { id:'10', empresa_id: 'e2', empresa_nome: 'Cliente B',       tipo_conciliacao: 'Recebíveis',  periodo_inicio: '2026-04-01', periodo_fim: '2026-04-30', status: 'erro',             quantidade_divergencias: 0,  criado_em: '2026-04-04T08:00:00Z' },
]

export function useConciliacoes() {
  const conciliacoes = ref<Conciliacao[]>([])
  const carregando = ref(false)
  const erro = ref<string | null>(null)

  const filtros = ref<FiltroConciliacoes>({
    empresa_id: '',
    tipo_conciliacao: '',
    status: '',
    periodo_inicio: '',
    periodo_fim: '',
    busca: '',
  })

  const resumo = computed<ResumoConciliacoes>(() => ({
    total:            conciliacoes.value.length,
    em_processamento: conciliacoes.value.filter(c => c.status === 'em_processamento').length,
    com_divergencias: conciliacoes.value.filter(c => c.status === 'com_divergencias').length,
    aprovadas:        conciliacoes.value.filter(c => c.status === 'aprovado').length,
  }))

  const conciliacoesFiltradas = computed(() => {
    const f = filtros.value
    return conciliacoes.value.filter(c => {
      if (f.empresa_id    && c.empresa_id !== f.empresa_id)         return false
      if (f.tipo_conciliacao && c.tipo_conciliacao !== f.tipo_conciliacao) return false
      if (f.status        && c.status !== f.status)                 return false
      if (f.busca         && !c.empresa_nome.toLowerCase().includes(f.busca.toLowerCase())
                          && !c.tipo_conciliacao.toLowerCase().includes(f.busca.toLowerCase())) return false
      return true
    })
  })

  async function carregar() {
    carregando.value = true
    erro.value = null
    try {
      const api = useApi()
      const params = new URLSearchParams()
      const f = filtros.value
      if (f.empresa_id)      params.set('empresa_id', f.empresa_id)
      if (f.tipo_conciliacao) params.set('tipo_conciliacao', f.tipo_conciliacao)
      if (f.status)          params.set('status', f.status)
      if (f.periodo_inicio)  params.set('periodo_inicio', f.periodo_inicio)
      if (f.periodo_fim)     params.set('periodo_fim', f.periodo_fim)
      if (f.busca)           params.set('busca', f.busca)

      const qs = params.toString()
      const resposta = await api.get(`/api/v1/conciliacoes${qs ? '?' + qs : ''}`)
      conciliacoes.value = resposta.dados ?? []
    } catch {
      // fallback para mock em desenvolvimento
      conciliacoes.value = MOCK_CONCILIACOES
      erro.value = null
    } finally {
      carregando.value = false
    }
  }

  function limparFiltros() {
    filtros.value = { empresa_id: '', tipo_conciliacao: '', status: '', periodo_inicio: '', periodo_fim: '', busca: '' }
  }

  async function buscarPorId(id: string): Promise<ConciliacaoDetalhe> {
    const api = useApi()
    const resposta = await api.get<{ sucesso: boolean; dados: ConciliacaoDetalhe }>(`/api/v1/conciliacoes/${id}`)
    return resposta.dados
  }

  async function criar(dados: NovaConciliacao): Promise<Conciliacao> {
    const api = useApi()
    const resposta = await api.post<{ sucesso: boolean; dados: Conciliacao }>('/api/v1/conciliacoes', dados)
    return resposta.dados
  }

  async function processarConciliacao(conciliacaoId: string): Promise<ResultadoProcessamentoConciliacao> {
    const api = useApi()
    const resposta = await api.post<{ sucesso: boolean; dados: ResultadoProcessamentoConciliacao }>(
      `/api/v1/conciliacoes/${conciliacaoId}/processar`,
      {},
    )
    return resposta.dados
  }

  return {
    conciliacoes: conciliacoesFiltradas,
    resumo,
    filtros,
    carregando,
    erro,
    carregar,
    limparFiltros,
    criar,
    buscarPorId,
    processarConciliacao,
  }
}
