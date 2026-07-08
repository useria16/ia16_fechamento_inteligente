export type ModoRetencaoArquivo =
  | 'somente_memoria'
  | 'temporario'
  | 'persistente'

export interface PoliticaRetencaoArquivo {
  id: string
  empresa_id: string
  modo_retencao: ModoRetencaoArquivo
  salvar_arquivo_original: boolean
  salvar_resultado_processado: boolean
  salvar_linhas_processadas: boolean
  salvar_metadados: boolean
  tempo_retencao_horas: number | null
  excluir_arquivo_original_apos_processamento: boolean
  permitir_download_original: boolean
  permitir_reprocessamento_sem_reenvio: boolean
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

export type AtualizacaoPoliticaRetencaoArquivo = Omit<
  PoliticaRetencaoArquivo,
  'id' | 'empresa_id' | 'criado_em' | 'atualizado_em'
>

export const modoRetencaoLabels: Record<ModoRetencaoArquivo, string> = {
  somente_memoria: 'Somente em memória',
  temporario: 'Temporário',
  persistente: 'Persistente',
}
