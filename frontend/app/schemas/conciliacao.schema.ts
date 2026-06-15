import { z } from 'zod'

export const novaConciliacaoSchema = z.object({
  titulo: z.string().min(3, 'Título deve ter ao menos 3 caracteres'),
  tipo_conciliacao: z.string().min(1, 'Selecione o tipo de conciliação'),
  periodo_inicio: z.string().min(1, 'Informe o início do período'),
  periodo_fim: z.string().min(1, 'Informe o fim do período'),
  empresa_id: z.string().optional(),
}).refine(
  d => !d.periodo_inicio || !d.periodo_fim || d.periodo_fim >= d.periodo_inicio,
  { message: 'O fim do período deve ser posterior ao início', path: ['periodo_fim'] },
)

export type NovaConciliacaoForm = z.infer<typeof novaConciliacaoSchema>
