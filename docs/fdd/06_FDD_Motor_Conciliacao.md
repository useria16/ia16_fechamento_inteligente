# FDD 06, Motor de conciliação

## 1. Objetivo

Processar planilhas financeiras, normalizar dados e identificar registros conciliados, pendentes e divergentes.

## 2. Escopo

O MVP terá regras determinísticas simples, baseadas em data, valor, documento, descrição e origem.

## 3. Regras de negócio

- O motor deve ler arquivos associados ao fechamento.
- O motor deve usar o modelo de arquivo para normalizar colunas.
- O motor deve gravar transações financeiras normalizadas.
- O motor deve comparar registros por critérios configurados.
- O motor deve classificar cada item.
- O motor deve registrar divergências.
- O motor deve atualizar o resumo do fechamento.

## 4. Tabelas

- `transacoes_financeiras`
- `itens_conciliacao`
- `divergencias_conciliacao`
- `logs_processamento`

## 5. Critérios iniciais de conciliação

Ordem recomendada:

1. documento igual e valor igual
2. data próxima e valor igual
3. descrição similar e valor igual
4. valor próximo com diferença dentro de tolerância configurada
5. registro sem par correspondente

## 6. Status de conciliação

- `conciliado`
- `divergente`
- `pendente`
- `duplicado`
- `nao_encontrado`
- `erro`

## 7. Tabela transacoes_financeiras

Colunas principais:

- `id`
- `empresa_id`
- `fechamento_id`
- `arquivo_id`
- `fonte_dados_id`
- `data_transacao`
- `descricao`
- `valor`
- `tipo_movimento`
- `documento`
- `categoria`
- `identificador_externo`
- `dados_originais`
- `criado_em`

## 8. Tabela itens_conciliacao

Colunas principais:

- `id`
- `empresa_id`
- `fechamento_id`
- `transacao_origem_id`
- `transacao_destino_id`
- `status`
- `criterio_conciliacao`
- `diferenca_valor`
- `diferenca_dias`
- `observacao`
- `criado_em`
- `atualizado_em`

## 9. Critérios de aceite

- Motor lê arquivo Excel.
- Motor normaliza colunas.
- Motor grava transações.
- Motor identifica registros conciliados.
- Motor identifica divergências.
- Motor atualiza fechamento.
- Motor grava logs.

## 10. Tarefas para Claude Code

- Criar serviço Python `motor_conciliacao`.
- Criar leitores de Excel.
- Criar normalizadores.
- Criar regras de comparação.
- Criar gravação em banco.
- Criar testes unitários para regras.
- Criar logs de processamento.
