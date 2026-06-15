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

  const autenticado = computed(() => !!sessao.value)
  const token = computed(() => sessao.value?.access_token ?? null)
  const perfil = computed(() => perfilUsuario.value)

  async function carregarPerfil(_userId: string) {
    try {
      const config = useRuntimeConfig()
      const accessToken = getSupabase().auth.getSession().then(s => s.data.session?.access_token)
      const token = await accessToken
      if (!token) return

      const res = await fetch(`${config.public.apiBaseUrl}/api/v1/auth/eu`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return
      const json = await res.json()
      if (json?.dados?.perfil) perfilUsuario.value = json.dados.perfil
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
      else perfilUsuario.value = null
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
    navigateTo("/login")
  }

  return { sessao, carregando, erro, autenticado, token, perfil, inicializar, entrar, sair }
})
