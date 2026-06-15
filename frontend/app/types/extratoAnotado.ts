export type StatusRevisao = 'pendente' | 'em_revisao' | 'revisado' | 'ignorado'

export type TipoConferenciaFluxo =
  | 'encontrado'
  | 'data_diferente'
  | 'nao_encontrado'
  | 'valor_diferente'
  | 'possivel_correspondencia'
  | 'pendente_analise'

export interface LancamentoExtratoAnotado {
  id: string
  fechamento_id: string
  arquivo_id: string
  data_lancamento: string
  descricao_banco: string
  razao_social: string | null
  documento: string | null
  valor: number
  tipo_movimento: 'entrada' | 'saida'
  saldo: number | null
  linha_origem: number | null
  categoria: string | null
  descricao_negocio: string | null
  nf_doc: string | null
  valor_nf_doc: number | null
  observacao: string | null
  categoria_sugerida: string | null
  confianca_sugestao: number | null
  status_revisao: StatusRevisao
  atualizado_por_usuario_id: string | null
  criado_em: string
  atualizado_em: string
  // Conferência com fluxo de caixa
  previsto_no_fluxo: boolean | null
  tipo_conferencia_fluxo: TipoConferenciaFluxo | null
  confianca_conferencia: number | null
  observacao_sistema: string | null
  data_prevista: string | null
  valor_previsto: number | null
  descricao_prevista: string | null
}

export interface AtualizarLancamentoAnotado {
  categoria?: string | null
  descricao_negocio?: string | null
  nf_doc?: string | null
  valor_nf_doc?: number | null
  observacao?: string | null
  status_revisao?: StatusRevisao | null
}

export const STATUS_REVISAO_LABELS: Record<StatusRevisao, string> = {
  pendente:   'Pendente',
  em_revisao: 'Em revisão',
  revisado:   'Revisado',
  ignorado:   'Ignorado',
}

// Labels curtos para a tabela
export const CONFERENCIA_LABELS: Record<TipoConferenciaFluxo, string> = {
  encontrado:               'No fluxo',
  data_diferente:           'Data dif.',
  nao_encontrado:           'Não prev.',
  valor_diferente:          'Valor dif.',
  possivel_correspondencia: 'Revisar',
  pendente_analise:         'Pendente',
}

// Labels completos para o modal e exportação
export const CONFERENCIA_LABELS_MODAL: Record<TipoConferenciaFluxo, string> = {
  encontrado:               'Previsto no fluxo',
  data_diferente:           'Data diferente',
  nao_encontrado:           'Não encontrado',
  valor_diferente:          'Valor diferente',
  possivel_correspondencia: 'Revisar',
  pendente_analise:         'Pendente',
}

export const CONFERENCIA_CLASSES: Record<TipoConferenciaFluxo, string> = {
  encontrado:               'bg-green-100 text-green-700',
  data_diferente:           'bg-amber-100 text-amber-700',
  nao_encontrado:           'bg-red-100 text-red-600',
  valor_diferente:          'bg-orange-100 text-orange-700',
  possivel_correspondencia: 'bg-yellow-100 text-yellow-700',
  pendente_analise:         'bg-slate-100 text-slate-500',
}
