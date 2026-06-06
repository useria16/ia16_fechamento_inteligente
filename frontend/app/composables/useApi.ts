export function useApi() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()

  async function requisitar<T>(
    metodo: string,
    caminho: string,
    corpo?: unknown,
  ): Promise<T> {
    const url = `${config.public.apiBaseUrl}${caminho}`
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    }

    if (auth.token) {
      headers["Authorization"] = `Bearer ${auth.token}`
    }

    const resposta = await fetch(url, {
      method: metodo,
      headers,
      body: corpo ? JSON.stringify(corpo) : undefined,
    })

    if (!resposta.ok) {
      const dados = await resposta.json().catch(() => ({}))
      throw new Error(dados.detail ?? `Erro ${resposta.status}`)
    }

    return resposta.json()
  }

  return {
    get: <T>(caminho: string) => requisitar<T>("GET", caminho),
    post: <T>(caminho: string, corpo: unknown) => requisitar<T>("POST", caminho, corpo),
    patch: <T>(caminho: string, corpo: unknown) => requisitar<T>("PATCH", caminho, corpo),
    del: <T>(caminho: string) => requisitar<T>("DELETE", caminho),
  }
}
