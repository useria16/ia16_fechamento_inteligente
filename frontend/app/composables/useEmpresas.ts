export interface Empresa {
  id: string
  nome: string
  cnpj: string
  status: string
}

export function useEmpresas() {
  const empresas = ref<Empresa[]>([])
  const carregando = ref(false)

  async function carregar() {
    carregando.value = true
    try {
      const api = useApi()
      const dados = await api.get<Empresa[]>('/api/empresas')
      empresas.value = Array.isArray(dados) ? dados : []
    } catch {
      empresas.value = []
    } finally {
      carregando.value = false
    }
  }

  return { empresas, carregando, carregar }
}
