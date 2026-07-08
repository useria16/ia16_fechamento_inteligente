import { z } from 'zod'

const anoAtual = new Date().getFullYear()

export const consolidadoMensalSchema = z.object({
  ano: z
    .number({ invalid_type_error: 'Informe o ano' })
    .int()
    .min(2000, 'Ano inválido')
    .max(anoAtual + 1, 'Ano inválido'),
  mes: z
    .number({ invalid_type_error: 'Informe o mês' })
    .int()
    .min(1, 'Mês inválido')
    .max(12, 'Mês inválido'),
  tipo_conciliacao: z.string().min(1, 'Selecione o tipo de conciliação'),
  empresa_id: z.string().optional(),
})

export type ConsolidadoMensalForm = z.infer<typeof consolidadoMensalSchema>

export const consolidadoPeriodoSchema = z.object({
  data_inicio: z.string().min(1, 'Informe a data inicial'),
  data_fim: z.string().min(1, 'Informe a data final'),
  tipo_conciliacao: z.string().min(1, 'Selecione o tipo de conciliação'),
  empresa_id: z.string().optional(),
}).refine(
  dados => new Date(`${dados.data_inicio}T00:00:00`) <= new Date(`${dados.data_fim}T00:00:00`),
  {
    path: ['data_fim'],
    message: 'Data final deve ser igual ou posterior à data inicial',
  },
)

export type ConsolidadoPeriodoForm = z.infer<typeof consolidadoPeriodoSchema>
