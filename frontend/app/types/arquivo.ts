import type { ModoRetencaoArquivo } from '~/types/politicaRetencaoArquivo'
export type { ModoRetencaoArquivo }

export type TipoArquivo =
  | 'extrato_bancario'
  | 'planilha_interna'

export type StatusArquivo =
  | 'enviado'
  | 'validado'
  | 'invalido'
  | 'processado'
  | 'erro'

export interface ArquivoEnviado {
  id: string
  empresa_id: string
  conciliacao_id: string
  nome_original: string
  tipo_arquivo: TipoArquivo | string
  status: StatusArquivo | string
  tamanho_bytes: number
  // Campos de retenção (nullable em arquivos anteriores à migration 009)
  modo_retencao?: ModoRetencaoArquivo | null
  arquivo_persistido?: boolean
  expira_em?: string | null
  excluido_em?: string | null
  hash_arquivo?: string | null
  metadados?: Record<string, unknown>
  arquivo_disponivel?: boolean
  permitir_download_original?: boolean
  permitir_reprocessamento_sem_reenvio?: boolean
  criado_em: string
}

export const tipoArquivoLabels: Record<string, string> = {
  extrato_bancario: 'Extrato Bancário',
  planilha_interna: 'Fluxo de Caixa',
}

export const statusArquivoLabels: Record<string, string> = {
  enviado:   'Enviado',
  validado:  'Validado',
  invalido:  'Inválido',
  processado:'Processado',
  erro:      'Erro',
}
