import type { ArquivoEnviado } from '~/types/arquivo'

export function useArquivos() {
  const arquivos = ref<ArquivoEnviado[]>([])
  const carregando = ref(false)
  const enviando = ref(false)
  const erro = ref<string | null>(null)

  async function listar(conciliacaoId: string) {
    carregando.value = true
    erro.value = null
    try {
      const api = useApi()
      const resposta = await api.get<{ sucesso: boolean; dados: ArquivoEnviado[] }>(
        `/api/v1/conciliacoes/${conciliacaoId}/arquivos`
      )
      arquivos.value = resposta.dados ?? []
    } catch (e: any) {
      erro.value = 'Não foi possível carregar os arquivos.'
    } finally {
      carregando.value = false
    }
  }

  async function enviar(conciliacaoId: string, arquivo: File, tipoArquivo: string): Promise<ArquivoEnviado> {
    enviando.value = true
    erro.value = null
    try {
      const auth = useAuthStore()
      const config = useRuntimeConfig()

      const formData = new FormData()
      formData.append('arquivo', arquivo)
      formData.append('tipo_arquivo', tipoArquivo)

      const res = await fetch(`${config.public.apiBaseUrl}/api/v1/conciliacoes/${conciliacaoId}/arquivos`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${auth.token}` },
        body: formData,
      })

      if (!res.ok) {
        const dados = await res.json().catch(() => ({}))
        throw new Error(dados.detail ?? `Erro ${res.status}`)
      }

      const resposta = await res.json()
      const novo = resposta.dados as ArquivoEnviado
      arquivos.value.unshift(novo)
      return novo
    } catch (e: any) {
      erro.value = e.message ?? 'Não foi possível enviar o arquivo.'
      throw e
    } finally {
      enviando.value = false
    }
  }

  async function remover(arquivoId: string) {
    try {
      const api = useApi()
      await api.del(`/api/v1/arquivos/${arquivoId}`)
      arquivos.value = arquivos.value.filter(a => a.id !== arquivoId)
    } catch (e: any) {
      throw new Error(e.message ?? 'Não foi possível remover o arquivo.')
    }
  }

  return { arquivos, carregando, enviando, erro, listar, enviar, remover }
}
