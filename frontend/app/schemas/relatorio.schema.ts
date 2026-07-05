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
