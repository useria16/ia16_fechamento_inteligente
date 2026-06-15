export type StatusConciliacao =
  | 'rascunho'
  | 'arquivos_enviados'
  | 'em_processamento'
  | 'processado'
  | 'com_divergencias'
  | 'aprovado'
  | 'reaberto'
  | 'cancelado'
  | 'erro'

export interface Conciliacao {
  id: string
  empresa_id: string
  empresa_nome: string
  tipo_conciliacao: string
  periodo_inicio: string
  periodo_fim: string
  status: StatusConciliacao
  quantidade_divergencias: number
  criado_em: string
}

export interface ResumoConciliacoes {
  total: number
  em_processamento: number
  com_divergencias: number
  aprovadas: number
}

export interface ConciliacaoDetalhe {
  id: string
  empresa_id: string
  empresa_nome: string
  titulo: string
  tipo_conciliacao: string
  periodo_inicio: string
  periodo_fim: string
  status: StatusConciliacao
  quantidade_registros: number
  quantidade_conciliados: number
  quantidade_divergencias: number
  quantidade_divergentes: number
  quantidade_pendentes: number
  percentual_conciliado: number
  aprovado_em: string | null
  aprovado_por_usuario_id?: string | null
  observacao_aprovacao?: string | null
  reaberto_em?: string | null
  reaberto_por_usuario_id?: string | null
  motivo_reabertura?: string | null
  criado_em: string
  atualizado_em: string
}

export interface NovaConciliacao {
  titulo: string
  tipo_conciliacao: string
  periodo_inicio: string
  periodo_fim: string
  empresa_id?: string
}

export interface FiltroConciliacoes {
  empresa_id?: string
  tipo_conciliacao?: string
  status?: StatusConciliacao | ''
  periodo_inicio?: string
  periodo_fim?: string
  busca?: string
}

export interface ResultadoProcessamentoConciliacao {
  conciliacao_id: string
  status: StatusConciliacao
  quantidade_arquivos: number
  quantidade_registros: number
  quantidade_conciliados: number
  quantidade_divergentes: number
  quantidade_pendentes: number
  valor_total_processado: number
  pronto_para_revisao: boolean
  mensagem_processamento: string
}
