# FDD 01, Autenticação, empresas e usuários

## 1. Objetivo

Permitir que usuários acessem a aplicação com segurança e fiquem vinculados a uma empresa.

## 2. Escopo

Inclui login, sessão, cadastro administrativo de empresas e usuários, perfis básicos e segregação por empresa.

## 3. Perfis

- `admin_ia16`: acessa todas as empresas
- `cliente_admin`: acessa dados da própria empresa e gerencia usuários da empresa
- `cliente_operador`: acessa dados da própria empresa e executa operações de fechamento

## 4. Regras de negócio

- Não haverá cadastro público.
- Usuários serão criados pela iA16 ou por usuário autorizado.
- Todo usuário cliente deve estar vinculado a uma empresa.
- Um usuário cliente não pode acessar dados de outra empresa.
- O login será feito via Supabase Auth.
- A tabela `usuarios` deve manter o vínculo com `auth.users`.

## 5. Tabelas

- `empresas`
- `usuarios`

## 6. Colunas principais

### empresas

- `id`
- `nome`
- `cnpj`
- `status`
- `criado_em`
- `atualizado_em`

### usuarios

- `id`
- `empresa_id`
- `usuario_auth_id`
- `nome`
- `email`
- `perfil`
- `ativo`
- `criado_em`
- `atualizado_em`

## 7. Telas

- `/login`
- `/admin/empresas`
- `/admin/empresas/nova`
- `/admin/empresas/[id]`
- `/admin/usuarios`
- `/admin/usuarios/novo`

## 8. APIs

### GET `/api/empresas`

Lista empresas permitidas para o usuário autenticado.

### POST `/api/empresas`

Cria empresa.

### GET `/api/usuarios`

Lista usuários.

### POST `/api/usuarios`

Cria usuário vinculado a empresa.

### PATCH `/api/usuarios/{id}`

Atualiza dados básicos do usuário.

## 9. Critérios de aceite

- Usuário consegue fazer login.
- Usuário sem vínculo ativo não acessa a aplicação.
- Admin iA16 consegue cadastrar empresa.
- Admin iA16 consegue cadastrar usuário.
- Cliente visualiza apenas dados da própria empresa.
- Objetos do banco criados em português.

## 10. Tarefas para Claude Code

- Criar migrations `empresas` e `usuarios`.
- Criar models SQLAlchemy em português.
- Criar schemas Pydantic.
- Criar endpoints FastAPI.
- Criar páginas Nuxt.
- Criar store Pinia para sessão.
- Validar JWT do Supabase no backend.
