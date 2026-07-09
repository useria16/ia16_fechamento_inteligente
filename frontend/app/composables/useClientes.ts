export interface Cliente {
  id: string
  nome: string
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

export interface NovoCliente {
  nome: string
}

export interface AtualizacaoCliente {
  nome?: string
  ativo?: boolean
}

export function useClientes() {
  const clientes = ref<Cliente[]>([])
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
      const dados = await api.get<Cliente[]>('/api/v1/clientes')
      clientes.value = Array.isArray(dados) ? dados : []
    } catch (e: any) {
      erro.value = extrairErro(e)
      clientes.value = []
    } finally {
      carregando.value = false
    }
  }

  async function criar(dados: NovoCliente): Promise<Cliente> {
    salvando.value = true
    erro.value = null
    try {
      const api = useApi()
      return await api.post<Cliente>('/api/v1/clientes', dados)
    } catch (e: any) {
      erro.value = extrairErro(e)
      throw e
    } finally {
      salvando.value = false
    }
  }

  async function obter(id: string): Promise<Cliente> {
    const api = useApi()
    return await api.get<Cliente>(`/api/v1/clientes/${id}`)
  }

  async function atualizar(id: string, dados: AtualizacaoCliente): Promise<Cliente> {
    salvando.value = true
    erro.value = null
    try {
      const api = useApi()
      return await api.patch<Cliente>(`/api/v1/clientes/${id}`, dados)
    } catch (e: any) {
      erro.value = extrairErro(e)
      throw e
    } finally {
      salvando.value = false
    }
  }

  return { clientes, carregando, salvando, erro, carregar, criar, obter, atualizar }
}
