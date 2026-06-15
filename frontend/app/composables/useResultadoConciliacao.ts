import type { Divergencia, AtualizarDivergenciaPayload, FiltroDivergencias } from '~/types/divergencia'

export function useResultadoConciliacao(conciliacaoId: string) {
  const api = useApi()

  const divergencias = ref<Divergencia[]>([])
  const carregando = ref(false)
  const erro = ref<string | null>(null)

  const filtros = ref<FiltroDivergencias>({
    status: '',
    tipo_divergencia: '',
    severidade: '',
    busca: '',
  })

  const divergenciasFiltradas = computed(() => {
    const f = filtros.value
    return divergencias.value.filter((d) => {
      if (f.status && d.status !== f.status) return false
      if (f.tipo_divergencia && d.tipo_divergencia !== f.tipo_divergencia) return false
      if (f.severidade && d.severidade !== f.severidade) return false
      if (f.busca) {
        const busca = f.busca.toLowerCase()
        const emDescricao = d.descricao.toLowerCase().includes(busca)
        const emTipo = d.tipo_divergencia.toLowerCase().includes(busca)
        if (!emDescricao && !emTipo) return false
      }
      return true
    })
  })

  const contadores = computed(() => ({
    total:      divergencias.value.length,
    abertas:    divergencias.value.filter((d) => d.status === 'aberta').length,
    em_analise: divergencias.value.filter((d) => d.status === 'em_analise').length,
    resolvidas: divergencias.value.filter((d) => d.status === 'resolvida').length,
    ignoradas:  divergencias.value.filter((d) => d.status === 'ignorada').length,
  }))

  async function carregarDivergencias() {
    carregando.value = true
    erro.value = null
    try {
      const params = new URLSearchParams({ limite: '200' })
      const resposta = await api.get<{ sucesso: boolean; dados: Divergencia[] }>(
        `/api/v1/conciliacoes/${conciliacaoId}/divergencias?${params}`,
      )
      divergencias.value = resposta.dados ?? []
    } catch (e: any) {
      erro.value = e.message ?? 'Não foi possível carregar as divergências.'
    } finally {
      carregando.value = false
    }
  }

  async function atualizarDivergencia(
    divergenciaId: string,
    payload: AtualizarDivergenciaPayload,
  ): Promise<Divergencia> {
    const resposta = await api.patch<{ sucesso: boolean; dados: Divergencia }>(
      `/api/v1/divergencias/${divergenciaId}`,
      payload,
    )
    const atualizada = resposta.dados
    const idx = divergencias.value.findIndex((d) => d.id === divergenciaId)
    if (idx !== -1) divergencias.value[idx] = atualizada
    return atualizada
  }

  function limparFiltros() {
    filtros.value = { status: '', tipo_divergencia: '', severidade: '', busca: '' }
  }

  return {
    divergencias: divergenciasFiltradas,
    todasDivergencias: divergencias,
    contadores,
    filtros,
    carregando,
    erro,
    carregarDivergencias,
    atualizarDivergencia,
    limparFiltros,
  }
}
