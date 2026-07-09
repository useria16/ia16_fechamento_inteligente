import { z } from 'zod'

export const clienteCreateSchema = z.object({
  nome: z.string().trim().min(2, 'Informe o nome do cliente'),
})

export const clientePatchSchema = z.object({
  nome: z.string().trim().min(2, 'Informe o nome do cliente').optional(),
  ativo: z.boolean().optional(),
})

export type ClienteCreateForm = z.input<typeof clienteCreateSchema>
export type ClientePatchForm = z.input<typeof clientePatchSchema>
