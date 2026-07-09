import { defineStore } from "pinia"
import { createClient, type SupabaseClient } from "@supabase/supabase-js"

let _supabase: SupabaseClient | null = null

function getSupabase(): SupabaseClient {
  if (!_supabase) {
    const config = useRuntimeConfig()
    _supabase = createClient(config.public.supabaseUrl, config.public.supabaseAnonKey)
  }
  return _supabase
}

export const useAuthStore = defineStore("auth", () => {
  const sessao = ref<any>(null)
  const carregando = ref(false)
  const erro = ref<string | null>(null)
  const perfilUsuario = ref<string | null>(null)
  const usuarioAtual = ref<any>(null)

  const autenticado = computed(() => !!sessao.value)
  const token = computed(() => sessao.value?.access_token ?? null)
  const perfil = computed(() => perfilUsuario.value)
  const usuario = computed(() => usuarioAtual.value)
  const trocaSenhaObrigatoria = computed(() => !!usuarioAtual.value?.troca_senha_obrigatoria)
  const clienteId = computed<string | null>(() => usuarioAtual.value?.cliente_id ?? null)
  const empresasDisponiveis = computed<Array<{ id: string; nome: string; cnpj: string }>>(
    () => usuarioAtual.value?.empresas ?? [],
  )

  async function carregarPerfil(_userId: string) {
    try {
      const config = useRuntimeConfig()
      const accessToken = getSupabase().auth.getSession().then(s => s.data.session?.access_token)
      const accessTokenAtual = await accessToken
      if (!accessTokenAtual) return

      const res = await fetch(`${config.public.apiBaseUrl}/api/v1/auth/eu`, {
        headers: { Authorization: `Bearer ${accessTokenAtual}` },
      })
      if (!res.ok) return
      const json = await res.json()
      if (json?.dados) {
        usuarioAtual.value = json.dados
        perfilUsuario.value = json.dados.perfil
      }
    } catch {
      // perfil permanece null — sidebar exibe todos os itens como fallback
    }
  }

  async function inicializar() {
    if (!import.meta.client) return

    const supabase = getSupabase()
    const { data } = await supabase.auth.getSession()
    sessao.value = data.session
    if (data.session?.user?.id) await carregarPerfil(data.session.user.id)

    supabase.auth.onAuthStateChange(async (_event, novaSessao) => {
      sessao.value = novaSessao
      if (novaSessao?.user?.id) await carregarPerfil(novaSessao.user.id)
      else {
        perfilUsuario.value = null
        usuarioAtual.value = null
      }
    })
  }

  async function entrar(email: string, senha: string) {
    carregando.value = true
    erro.value = null
    try {
      const { data, error } = await getSupabase().auth.signInWithPassword({ email, password: senha })
      if (error) throw error
      sessao.value = data.session
      if (data.session?.user?.id) await carregarPerfil(data.session.user.id)
    } catch (e: any) {
      erro.value = e.message ?? "Erro ao fazer login"
    } finally {
      carregando.value = false
    }
  }

  async function sair() {
    await getSupabase().auth.signOut()
    sessao.value = null
    perfilUsuario.value = null
    usuarioAtual.value = null
    navigateTo("/login")
  }

  async function trocarSenha(novaSenha: string) {
    carregando.value = true
    erro.value = null
    try {
      const config = useRuntimeConfig()
      const accessToken = token.value
      if (!accessToken) throw new Error("Sessão não encontrada")

      const res = await fetch(`${config.public.apiBaseUrl}/api/v1/auth/trocar-senha`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ nova_senha: novaSenha }),
      })

      const json = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(json?.detail ?? "Não foi possível alterar a senha")
      }

      if (json?.dados) {
        usuarioAtual.value = json.dados
        perfilUsuario.value = json.dados.perfil
      }
    } catch (e: any) {
      erro.value = e.message ?? "Erro ao alterar senha"
      throw e
    } finally {
      carregando.value = false
    }
  }

  return {
    sessao,
    carregando,
    erro,
    autenticado,
    token,
    perfil,
    usuario,
    trocaSenhaObrigatoria,
    clienteId,
    empresasDisponiveis,
    inicializar,
    entrar,
    sair,
    trocarSenha,
  }
})
