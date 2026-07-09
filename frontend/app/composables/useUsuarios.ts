export interface UsuarioSistema {
  id: string
  cliente_id: string | null
  empresa_id: string | null  // legado
  usuario_auth_id: string
  nome: string
  email: string
  perfil: 'admin_ia16' | 'cliente_admin' | 'cliente_operador'
  ativo: boolean
  troca_senha_obrigatoria: boolean
}

export interface NovoUsuario {
  nome: string
  email: string
  perfil: string
  cliente_id?: string | null
  senha_temporaria: string
}

export function useUsuarios() {
  const usuarios = ref<UsuarioSistema[]>([])
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
      usuarios.value = await api.get<UsuarioSistema[]>('/api/v1/usuarios')
    } catch (e: any) {
      erro.value = extrairErro(e)
      usuarios.value = []
    } finally {
      carregando.value = false
    }
  }

  async function criar(dados: NovoUsuario) {
    salvando.value = true
    erro.value = null
    try {
      const api = useApi()
      return await api.post<UsuarioSistema>('/api/v1/usuarios', dados)
    } catch (e: any) {
      erro.value = extrairErro(e)
      throw e
    } finally {
      salvando.value = false
    }
  }

  async function atualizar(id: string, dados: Partial<UsuarioSistema>) {
    salvando.value = true
    erro.value = null
    try {
      const api = useApi()
      return await api.patch<UsuarioSistema>(`/api/v1/usuarios/${id}`, dados)
    } catch (e: any) {
      erro.value = extrairErro(e)
      throw e
    } finally {
      salvando.value = false
    }
  }

  async function resetarSenha(id: string, senhaTemporaria: string) {
    salvando.value = true
    erro.value = null
    try {
      const api = useApi()
      return await api.post<UsuarioSistema>(`/api/v1/usuarios/${id}/resetar-senha`, {
        senha_temporaria: senhaTemporaria,
      })
    } catch (e: any) {
      erro.value = extrairErro(e)
      throw e
    } finally {
      salvando.value = false
    }
  }

  return { usuarios, carregando, salvando, erro, carregar, criar, atualizar, resetarSenha }
}
