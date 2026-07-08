export interface Empresa {
  id: string
  nome: string
  cnpj: string
  status: string
}

export interface NovaEmpresa {
  nome: string
  cnpj: string
}

export interface AtualizacaoEmpresa {
  nome?: string
  status?: 'ativa' | 'inativa'
}

export function useEmpresas() {
  const empresas = ref<Empresa[]>([])
  const carregando = ref(false)
  const salvando = ref(false)
  const erro = ref<string | null>(null)

  function extrairErro(e: any): string {
    const detalhe = e?.data?.detail
    if (typeof detalhe === 'string') return detalhe
    if (Array.isArray(detalhe)) return detalhe[0]?.msg ?? 'Não foi possível concluir a operação.'
    return e?.message ?? 'Não foi possível concluir a operação.'
  }

  async function carregar() {
    carregando.value = true
    erro.value = null
    try {
      const api = useApi()
      const dados = await api.get<Empresa[]>('/api/v1/empresas')
      empresas.value = Array.isArray(dados) ? dados : []
    } catch (e: any) {
      erro.value = extrairErro(e)
      empresas.value = []
    } finally {
      carregando.value = false
    }
  }

  async function criar(dados: NovaEmpresa): Promise<Empresa> {
    salvando.value = true
    erro.value = null
    try {
      const api = useApi()
      return await api.post<Empresa>('/api/v1/empresas', dados)
    } catch (e: any) {
      erro.value = extrairErro(e)
      throw e
    } finally {
      salvando.value = false
    }
  }

  async function obter(id: string): Promise<Empresa> {
    const api = useApi()
    return await api.get<Empresa>(`/api/v1/empresas/${id}`)
  }

  async function atualizar(id: string, dados: AtualizacaoEmpresa): Promise<Empresa> {
    salvando.value = true
    erro.value = null
    try {
      const api = useApi()
      return await api.patch<Empresa>(`/api/v1/empresas/${id}`, dados)
    } catch (e: any) {
      erro.value = extrairErro(e)
      throw e
    } finally {
      salvando.value = false
    }
  }

  return { empresas, carregando, salvando, erro, carregar, criar, obter, atualizar }
}
