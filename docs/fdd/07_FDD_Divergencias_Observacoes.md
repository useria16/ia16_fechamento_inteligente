# FDD 07, Divergências e observações

## 1. Objetivo

Permitir que o usuário revise divergências, registre observações e marque pendências como resolvidas.

## 2. Escopo

Listagem, filtros, detalhe, observação, mudança de status e resolução manual.

## 3. Tipos de divergência

- `valor_diferente`
- `data_diferente`
- `registro_nao_encontrado`
- `registro_duplicado`
- `taxa_divergente`
- `recebimento_pendente`
- `categoria_inconsistente`
- `outro`

## 4. Níveis de severidade

- `baixa`
- `media`
- `alta`
- `critica`

## 5. Status da divergência

- `aberta`
- `em_analise`
- `resolvida`
- `ignorada`

## 6. Tabela

`divergencias_conciliacao`

## 7. Colunas principais

- `id`
- `empresa_id`
- `fechamento_id`
- `item_conciliacao_id`
- `tipo_divergencia`
- `severidade`
- `status`
- `descricao`
- `valor_esperado`
- `valor_encontrado`
- `diferenca_valor`
- `data_esperada`
- `data_encontrada`
- `observacao`
- `acao_sugerida`
- `resolvido_por_usuario_id`
- `resolvido_em`
- `criado_em`
- `atualizado_em`

## 8. Telas

- `/fechamentos/[id]/divergencias`
- `/fechamentos/[id]/divergencias/[divergenciaId]`

## 9. APIs

### GET `/api/fechamentos/{id}/divergencias`

Lista divergências do fechamento.

### GET `/api/divergencias/{id}`

Detalha divergência.

### PATCH `/api/divergencias/{id}`

Atualiza observação ou status.

### POST `/api/divergencias/{id}/resolver`

Marca como resolvida.

## 10. Critérios de aceite

- Usuário visualiza divergências.
- Usuário filtra por tipo, status e severidade.
- Usuário adiciona observação.
- Usuário marca divergência como resolvida.
- O fechamento atualiza contadores quando necessário.

## 11. Tarefas para Claude Code

- Criar migration `divergencias_conciliacao`.
- Criar endpoints.
- Criar tela de listagem.
- Criar filtros.
- Criar tela de detalhe.
- Criar ação de resolver.
