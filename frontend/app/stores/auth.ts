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

  const autenticado = computed(() => !!sessao.value)
  const token = computed(() => sessao.value?.access_token ?? null)
  const perfil = computed(() => sessao.value?.usuario?.perfil ?? null)

  async function inicializar() {
    if (!import.meta.client) return

    const supabase = getSupabase()
    const { data } = await supabase.auth.getSession()
    sessao.value = data.session

    supabase.auth.onAuthStateChange((_event, novaSessao) => {
      sessao.value = novaSessao
    })
  }

  async function entrar(email: string, senha: string) {
    carregando.value = true
    erro.value = null
    try {
      const { data, error } = await getSupabase().auth.signInWithPassword({ email, password: senha })
      if (error) throw error
      sessao.value = data.session
    } catch (e: any) {
      erro.value = e.message ?? "Erro ao fazer login"
    } finally {
      carregando.value = false
    }
  }

  async function sair() {
    await getSupabase().auth.signOut()
    sessao.value = null
    navigateTo("/login")
  }

  return { sessao, carregando, erro, autenticado, token, perfil, inicializar, entrar, sair }
})
