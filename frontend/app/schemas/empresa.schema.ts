import { z } from 'zod'

export const empresaCreateSchema = z.object({
  nome: z.string().trim().min(2, 'Informe o nome da empresa'),
  cnpj: z.string().transform(valor => valor.replace(/\D/g, '')).refine(
    valor => valor.length === 14,
    'CNPJ deve conter 14 dígitos',
  ),
})

export type EmpresaCreateForm = z.input<typeof empresaCreateSchema>
