import type { PoliticaRetencaoArquivo, AtualizacaoPoliticaRetencaoArquivo } from '~/types/politicaRetencaoArquivo'

export function usePoliticaRetencaoArquivos() {
  const politica = ref<PoliticaRetencaoArquivo | null>(null)
  const carregando = ref(false)
  const salvando = ref(false)
  const erro = ref<string | null>(null)

  async function buscarPoliticaRetencaoArquivos(empresaId: string): Promise<PoliticaRetencaoArquivo> {
    carregando.value = true
    erro.value = null
    try {
      const api = useApi()
      const resposta = await api.get<{ sucesso: boolean; dados: PoliticaRetencaoArquivo }>(
        `/api/v1/empresas/${empresaId}/politica-retencao-arquivos`
      )
      politica.value = resposta.dados
      return resposta.dados
    } catch (e: any) {
      erro.value = e?.data?.erro?.mensagem ?? e.message ?? 'Erro ao carregar política de retenção.'
      throw e
    } finally {
      carregando.value = false
    }
  }

  async function atualizarPoliticaRetencaoArquivos(
    empresaId: string,
    payload: AtualizacaoPoliticaRetencaoArquivo,
  ): Promise<PoliticaRetencaoArquivo> {
    salvando.value = true
    erro.value = null
    try {
      const api = useApi()
      const resposta = await api.put<{ sucesso: boolean; dados: PoliticaRetencaoArquivo }>(
        `/api/v1/empresas/${empresaId}/politica-retencao-arquivos`,
        payload,
      )
      politica.value = resposta.dados
      return resposta.dados
    } catch (e: any) {
      erro.value = e?.data?.erro?.mensagem ?? e.message ?? 'Erro ao salvar política de retenção.'
      throw e
    } finally {
      salvando.value = false
    }
  }

  return { politica, carregando, salvando, erro, buscarPoliticaRetencaoArquivos, atualizarPoliticaRetencaoArquivos }
}
