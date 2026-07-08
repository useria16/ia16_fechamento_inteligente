export function useApi() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()

  function cabecalhosBase(): Record<string, string> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`
    return headers
  }

  async function requisitar<T>(
    metodo: string,
    caminho: string,
    corpo?: unknown,
  ): Promise<T> {
    const url = `${config.public.apiBaseUrl}${caminho}`
    const resposta = await fetch(url, {
      method: metodo,
      headers: cabecalhosBase(),
      body: corpo ? JSON.stringify(corpo) : undefined,
    })

    if (!resposta.ok) {
      const dados = await resposta.json().catch(() => ({}))
      throw Object.assign(new Error(dados.detail ?? `Erro ${resposta.status}`), { data: dados })
    }

    return resposta.json()
  }

  async function download(caminho: string): Promise<void> {
    const url = `${config.public.apiBaseUrl}${caminho}`
    const resposta = await fetch(url, {
      method: 'GET',
      headers: cabecalhosBase(),
    })

    if (!resposta.ok) {
      const dados = await resposta.json().catch(() => ({}))
      throw Object.assign(new Error(dados.detail ?? `Erro ${resposta.status}`), { data: dados })
    }

    const blob = await resposta.blob()
    const disposition = resposta.headers.get('Content-Disposition') ?? ''
    const match = disposition.match(/filename="?([^";\n]+)"?/)
    const nomeArquivo = match?.[1] ?? 'relatorio.xlsx'

    const objectUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = objectUrl
    link.download = nomeArquivo
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(objectUrl)
  }

  return {
    get: <T>(caminho: string) => requisitar<T>('GET', caminho),
    post: <T>(caminho: string, corpo: unknown) => requisitar<T>('POST', caminho, corpo),
    put: <T>(caminho: string, corpo: unknown) => requisitar<T>('PUT', caminho, corpo),
    patch: <T>(caminho: string, corpo: unknown) => requisitar<T>('PATCH', caminho, corpo),
    del: <T>(caminho: string) => requisitar<T>('DELETE', caminho),
    download,
  }
}
