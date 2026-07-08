import type { ConsolidadoMensalForm, ConsolidadoPeriodoForm } from '~/schemas/relatorio.schema'

export function useConsolidadoMensal() {
  const api = useApi()

  const baixando = ref(false)
  const erro = ref<string | null>(null)
  const sucesso = ref(false)

  function tratarErroDownload(e: any, contexto: 'mes' | 'periodo') {
    const erroApi = (e?.data as any)?.detail?.erro ?? (e?.data as any)?.erro
    const codigoErro = erroApi?.codigo as string | undefined
    if (codigoErro === 'SEM_CONCILIACOES_NO_PERIODO') {
      erro.value = contexto === 'mes'
        ? 'Nenhuma conciliação encontrada para este mês. Verifique se há conciliações aprovadas ou processadas no período.'
        : 'Nenhuma conciliação encontrada para o período informado. Verifique se há conciliações aprovadas ou processadas no intervalo.'
    } else if (codigoErro === 'EMPRESA_OBRIGATORIA') {
      erro.value = 'Selecione uma empresa para exportar.'
    } else if (codigoErro === 'SEM_PERMISSAO_EMPRESA') {
      erro.value = 'Sem permissão para exportar dados desta empresa.'
    } else if (codigoErro === 'EMPRESA_NAO_ENCONTRADA') {
      erro.value = 'Empresa não encontrada. Selecione outra empresa.'
    } else if (codigoErro === 'PERIODO_INVALIDO') {
      erro.value = 'Data final deve ser igual ou posterior à data inicial.'
    } else {
      erro.value = erroApi?.mensagem ?? 'Não foi possível gerar a planilha de conciliação.'
    }
  }

  async function baixarConsolidado(form: ConsolidadoMensalForm): Promise<boolean> {
    baixando.value = true
    erro.value = null
    sucesso.value = false

    const params = new URLSearchParams({
      ano: String(form.ano),
      mes: String(form.mes),
      tipo_conciliacao: form.tipo_conciliacao,
    })

    if (form.empresa_id) {
      params.set('empresa_id', form.empresa_id)
    }

    try {
      await api.download(`/api/v1/conciliacoes/exportar-mensal?${params.toString()}`)
      sucesso.value = true
      return true
    } catch (e: any) {
      tratarErroDownload(e, 'mes')
      return false
    } finally {
      baixando.value = false
    }
  }

  async function baixarConsolidadoPeriodo(form: ConsolidadoPeriodoForm): Promise<boolean> {
    baixando.value = true
    erro.value = null
    sucesso.value = false

    const params = new URLSearchParams({
      data_inicio: form.data_inicio,
      data_fim: form.data_fim,
      tipo_conciliacao: form.tipo_conciliacao,
    })

    if (form.empresa_id) {
      params.set('empresa_id', form.empresa_id)
    }

    try {
      await api.download(`/api/v1/conciliacoes/exportar-periodo?${params.toString()}`)
      sucesso.value = true
      return true
    } catch (e: any) {
      tratarErroDownload(e, 'periodo')
      return false
    } finally {
      baixando.value = false
    }
  }

  function limparFeedback() {
    erro.value = null
    sucesso.value = false
  }

  return {
    baixando,
    erro,
    sucesso,
    baixarConsolidado,
    baixarConsolidadoPeriodo,
    limparFeedback,
  }
}
