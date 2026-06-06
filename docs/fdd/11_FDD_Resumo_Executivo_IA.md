# FDD 11, Resumo executivo com IA opcional

## 1. Objetivo

Gerar uma explicação simples do fechamento, usando IA apenas como camada de apoio.

## 2. Escopo

No MVP, a IA deve gerar resumo textual a partir de dados consolidados, sem alterar valores financeiros e sem tomar decisão automática.

## 3. Regras de negócio

- IA não pode alterar registros.
- IA não pode conciliar sozinha.
- IA só recebe dados consolidados e divergências relevantes.
- O resumo deve ser salvo.
- O usuário deve saber que o texto é uma sugestão.
- O resumo pode ser editado manualmente no futuro, mas isso não entra no MVP.

## 4. Entrada da IA

- total processado
- total conciliado
- total divergente
- percentual conciliado
- quantidade de divergências
- principais tipos de divergência
- divergências críticas

## 5. Saída esperada

- resumo executivo
- principais pontos de atenção
- ações recomendadas

## 6. Tabela sugerida

Pode usar `relatorios_fechamento` com tipo `resumo_fechamento`, ou criar campo em `fechamentos_financeiros`.

Recomendação para MVP:

- campo `resumo_executivo` em `fechamentos_financeiros`
- campo `acoes_recomendadas` em `fechamentos_financeiros`

## 7. APIs

### POST `/api/fechamentos/{id}/gerar-resumo`

Gera resumo executivo.

## 8. Critérios de aceite

- Sistema gera resumo a partir do fechamento.
- Resumo não altera dados financeiros.
- Erro de IA não quebra o processamento financeiro.
- Usuário visualiza resumo no relatório.

## 9. Tarefas para Claude Code

- Criar serviço `servico_resumo_ia`.
- Criar prompt interno.
- Criar endpoint.
- Salvar resultado no fechamento.
- Exibir no relatório.
