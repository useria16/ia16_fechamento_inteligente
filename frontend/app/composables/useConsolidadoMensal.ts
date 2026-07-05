import type { ConsolidadoMensalForm } from '~/schemas/relatorio.schema'

export function useConsolidadoMensal() {
  const api = useApi()

  const baixando = ref(false)
  const erro = ref<string | null>(null)
  const sucesso = ref(false)

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
      const codigoErro = (e?.data as any)?.erro?.codigo as string | undefined
      if (codigoErro === 'SEM_CONCILIACOES_NO_PERIODO') {
        erro.value = 'Nenhuma conciliação encontrada para este mês e tipo de conciliação.'
      } else if (codigoErro === 'EMPRESA_OBRIGATORIA') {
        erro.value = 'Selecione uma empresa para exportar.'
      } else if (codigoErro === 'SEM_PERMISSAO_EMPRESA') {
        erro.value = 'Sem permissão para exportar dados desta empresa.'
      } else {
        erro.value = (e?.data as any)?.erro?.mensagem ?? e?.message ?? 'Não foi possível gerar o consolidado mensal.'
      }
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
    limparFeedback,
  }
}
