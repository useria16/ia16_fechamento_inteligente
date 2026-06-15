import { z } from 'zod'

export const TIPOS_ARQUIVO_PERMITIDOS = [
  'extrato_bancario',
  'relatorio_vendas',
  'relatorio_recebiveis',
  'planilha_interna',
  'taxas_adquirente',
  'outro',
] as const

export const EXTENSOES_PERMITIDAS = ['.xlsx', '.xls']
export const TAMANHO_MAXIMO_BYTES = 10 * 1024 * 1024 // 10 MB

export const uploadArquivoSchema = z.object({
  tipo_arquivo: z.enum(TIPOS_ARQUIVO_PERMITIDOS, {
    errorMap: () => ({ message: 'Selecione o tipo de arquivo.' }),
  }),
})

export function validarArquivoLocal(arquivo: File): string | null {
  const ext = '.' + arquivo.name.split('.').pop()?.toLowerCase()
  if (!EXTENSOES_PERMITIDAS.includes(ext)) {
    return `Extensão não permitida. Use: ${EXTENSOES_PERMITIDAS.join(', ')}`
  }
  if (arquivo.size > TAMANHO_MAXIMO_BYTES) {
    return 'O arquivo excede o tamanho máximo de 10 MB.'
  }
  return null
}
