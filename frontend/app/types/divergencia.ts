export type StatusDivergencia = 'aberta' | 'em_analise' | 'resolvida' | 'ignorada'

export type TipoDivergencia =
  | 'divergencia_data'
  | 'divergencia_valor'
  | 'previsto_nao_realizado'
  | 'realizado_nao_previsto'
  | 'duplicidade_extrato'
  | 'duplicidade_fluxo'
  | 'pendente_analise_manual'

export type SeveridadeDivergencia = 'baixa' | 'media' | 'alta'

export interface Divergencia {
  id: string
  item_conciliacao_id: string
  tipo_divergencia: TipoDivergencia | string
  severidade: SeveridadeDivergencia | string
  descricao: string
  valor_previsto: number | null
  valor_realizado: number | null
  diferenca_valor: number | null
  data_prevista: string | null
  data_realizada: string | null
  diferenca_dias: number | null
  status: StatusDivergencia
  observacao: string | null
  resolvido_em: string | null
  atualizado_por_usuario_id: string | null
  criado_em: string
  atualizado_em: string
}

export interface AtualizarDivergenciaPayload {
  status?: StatusDivergencia
  observacao?: string
}

export interface FiltroDivergencias {
  status: StatusDivergencia | ''
  tipo_divergencia: string
  severidade: string
  busca: string
}

export const LABELS_STATUS_DIVERGENCIA: Record<string, string> = {
  aberta:     'Aberta',
  em_analise: 'Em análise',
  resolvida:  'Resolvida',
  ignorada:   'Ignorada',
}

export const LABELS_TIPO_DIVERGENCIA: Record<string, string> = {
  divergencia_data:         'Divergência de data',
  divergencia_valor:        'Divergência de valor',
  previsto_nao_realizado:   'Previsto não realizado',
  realizado_nao_previsto:   'Realizado não previsto',
  duplicidade_extrato:      'Duplicidade no extrato',
  duplicidade_fluxo:        'Duplicidade no fluxo',
  pendente_analise_manual:  'Pendente para análise',
}

export const LABELS_SEVERIDADE: Record<string, string> = {
  baixa: 'Baixa',
  media: 'Média',
  alta:  'Alta',
}

export function labelStatusDivergencia(s: string) {
  return LABELS_STATUS_DIVERGENCIA[s] ?? s
}

export function labelTipoDivergencia(t: string) {
  return LABELS_TIPO_DIVERGENCIA[t] ?? t
}

export function labelSeveridade(s: string) {
  return LABELS_SEVERIDADE[s] ?? s
}
