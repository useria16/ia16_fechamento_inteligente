export interface AprovarFechamentoPayload {
  observacao_aprovacao?: string | null
}

export interface ReabrirFechamentoPayload {
  motivo?: string | null
}

export interface RespostaAprovacao {
  id: string
  status: string
  aprovado_em: string
  aprovado_por_usuario_id: string
  observacao_aprovacao: string | null
}

export interface RespostaReabertura {
  id: string
  status: string
  reaberto_em: string
  reaberto_por_usuario_id: string
}
