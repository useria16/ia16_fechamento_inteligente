export const statusConciliacaoLabels: Record<string, string> = {
  rascunho:          'Rascunho',
  arquivos_enviados: 'Arquivos enviados',
  em_processamento:  'Em processamento',
  processado:        'Processado',
  com_divergencias:  'Com divergências',
  aprovado:          'Aprovado',
  reaberto:          'Reaberto',
  erro:              'Erro',
  cancelado:         'Cancelado',
}

export function labelStatus(status: string): string {
  return statusConciliacaoLabels[status] ?? status
}
