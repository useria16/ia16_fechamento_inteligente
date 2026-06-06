# FDD 10, Logs de processamento

## 1. Objetivo

Registrar eventos importantes do processamento para auditoria, suporte e diagnóstico de erros.

## 2. Escopo

Logs técnicos e operacionais de leitura, validação, processamento e exportação.

## 3. Regras de negócio

- Todo processamento deve gerar logs.
- Erros devem registrar mensagem clara.
- Logs devem estar vinculados a empresa e fechamento.
- Logs não devem expor segredos.
- Logs devem ajudar o suporte da iA16 a entender falhas.

## 4. Tabela

`logs_processamento`

## 5. Colunas principais

- `id`
- `empresa_id`
- `fechamento_id`
- `arquivo_id`
- `nivel`
- `evento`
- `mensagem`
- `detalhes`
- `criado_em`

## 6. Níveis

- `info`
- `aviso`
- `erro`

## 7. Eventos sugeridos

- `processamento_iniciado`
- `arquivo_lido`
- `arquivo_invalido`
- `coluna_obrigatoria_ausente`
- `normalizacao_concluida`
- `conciliacao_concluida`
- `relatorio_gerado`
- `processamento_finalizado`
- `processamento_com_erro`

## 8. Telas

- `/fechamentos/[id]/logs`

No MVP, essa tela pode ficar visível apenas para admin iA16.

## 9. APIs

### GET `/api/fechamentos/{id}/logs`

Lista logs do fechamento.

## 10. Critérios de aceite

- Processamento registra início.
- Processamento registra conclusão.
- Erros ficam gravados.
- Admin consegue consultar logs.
- Logs ajudam a entender falhas de arquivo.

## 11. Tarefas para Claude Code

- Criar migration `logs_processamento`.
- Criar helper de logging no backend.
- Integrar logs ao motor de conciliação.
- Criar endpoint de consulta.
- Criar tela simples para admin.
