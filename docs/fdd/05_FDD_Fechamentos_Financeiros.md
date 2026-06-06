# FDD 05, Fechamentos financeiros

## 1. Objetivo

Permitir que o usuário crie e acompanhe fechamentos financeiros por período.

## 2. Escopo

Criar fechamento, vincular arquivos, iniciar processamento, acompanhar status e visualizar resumo.

## 3. Regras de negócio

- Fechamento pertence a uma empresa.
- Fechamento possui período início e fim.
- Fechamento deve ter pelo menos um arquivo antes do processamento.
- Fechamento em processamento não pode ser editado.
- Fechamento pode ser reprocessado.
- Fechamento processado pode ter divergências.
- Fechamento pode ser aprovado manualmente.

## 4. Tabela

`fechamentos_financeiros`

## 5. Colunas principais

- `id`
- `empresa_id`
- `titulo`
- `data_referencia`
- `periodo_inicio`
- `periodo_fim`
- `status`
- `valor_total_processado`
- `valor_total_conciliado`
- `valor_total_divergente`
- `quantidade_registros`
- `quantidade_conciliados`
- `quantidade_divergentes`
- `criado_por_usuario_id`
- `aprovado_por_usuario_id`
- `aprovado_em`
- `criado_em`
- `atualizado_em`

## 6. Status

- `rascunho`
- `arquivos_enviados`
- `em_processamento`
- `processado`
- `com_divergencias`
- `aprovado`
- `erro`
- `cancelado`

## 7. Telas

- `/fechamentos`
- `/fechamentos/novo`
- `/fechamentos/[id]`
- `/fechamentos/[id]/processamento`

## 8. APIs

### GET `/api/fechamentos`

Lista fechamentos.

### POST `/api/fechamentos`

Cria fechamento.

### GET `/api/fechamentos/{id}`

Detalha fechamento.

### PATCH `/api/fechamentos/{id}`

Atualiza fechamento.

### POST `/api/fechamentos/{id}/processar`

Inicia processamento.

### POST `/api/fechamentos/{id}/aprovar`

Aprova fechamento.

## 9. Critérios de aceite

- Usuário cria fechamento.
- Usuário associa arquivos.
- Sistema impede processamento sem arquivo.
- Sistema atualiza status durante processamento.
- Sistema exibe resumo após processamento.
- Usuário pode aprovar fechamento processado.

## 10. Tarefas para Claude Code

- Criar migration `fechamentos_financeiros`.
- Criar endpoints.
- Criar telas.
- Criar fluxo de status.
- Integrar botão de processamento ao backend.
