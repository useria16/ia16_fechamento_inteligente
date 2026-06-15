import { z } from 'zod'

export const atualizarDivergenciaSchema = z
  .object({
    status: z
      .enum(['aberta', 'em_analise', 'resolvida', 'ignorada'])
      .optional(),
    observacao: z.string().max(2000, 'Observação muito longa').optional(),
  })
  .refine(
    (data) => data.status !== undefined || data.observacao !== undefined,
    { message: 'Informe ao menos o status ou uma observação.' },
  )

export type AtualizarDivergenciaForm = z.infer<typeof atualizarDivergenciaSchema>
