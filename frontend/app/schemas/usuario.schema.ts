import { z } from 'zod'

export const usuarioCreateSchema = z.object({
  nome: z.string().trim().min(2, 'Informe o nome do usuário'),
  email: z.string().trim().email('Informe um e-mail válido'),
  perfil: z.enum(['admin_ia16', 'cliente_admin', 'cliente_operador']),
  cliente_id: z.string().optional(),
  senha_temporaria: z.string().min(8, 'Senha temporária deve ter pelo menos 8 caracteres'),
}).superRefine((dados, ctx) => {
  if (dados.perfil !== 'admin_ia16' && !dados.cliente_id) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['cliente_id'],
      message: 'Selecione o cliente/grupo do usuário',
    })
  }
})

export type UsuarioCreateForm = z.infer<typeof usuarioCreateSchema>
