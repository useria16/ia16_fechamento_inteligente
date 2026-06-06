# FDD 02, Fontes de dados

## 1. Objetivo

Cadastrar as origens dos dados financeiros usados no fechamento.

## 2. Escopo

No MVP, a fonte ativa será Excel manual. As demais fontes devem existir no modelo para evolução futura.

## 3. Tipos de fonte

- `excel_manual`
- `banco`
- `adquirente`
- `erp`
- `google_drive`
- `outro`

## 4. Regras de negócio

- Toda fonte pertence a uma empresa.
- Uma empresa pode ter várias fontes.
- No MVP, somente fonte `excel_manual` será processada.
- Fontes futuras podem ficar com status inativo.

## 5. Tabela

`fontes_dados`

## 6. Colunas principais

- `id`
- `empresa_id`
- `nome`
- `tipo`
- `status`
- `configuracao`
- `criado_em`
- `atualizado_em`

## 7. Telas

- `/fontes`
- `/fontes/nova`
- `/fontes/[id]`

## 8. APIs

### GET `/api/fontes-dados`

Lista fontes da empresa.

### POST `/api/fontes-dados`

Cria fonte.

### PATCH `/api/fontes-dados/{id}`

Atualiza fonte.

### DELETE `/api/fontes-dados/{id}`

Inativa fonte.

## 9. Critérios de aceite

- Usuário cria fonte de dados Excel manual.
- Fonte fica vinculada à empresa correta.
- Usuário cliente não visualiza fontes de outra empresa.
- Sistema permite manter fontes futuras sem processamento ativo.

## 10. Tarefas para Claude Code

- Criar migration `fontes_dados`.
- Criar enum em português para tipo de fonte.
- Criar endpoints CRUD.
- Criar tela de listagem e cadastro.
- Criar validações com Zod no frontend.
