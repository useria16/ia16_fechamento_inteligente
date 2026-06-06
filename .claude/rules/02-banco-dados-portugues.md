# Banco de dados em português

## Regra obrigatória

Todos os objetos customizados do banco devem estar em português.

Inclui:

- tabelas
- colunas
- enums
- constraints
- índices
- views
- funções
- triggers
- migrations

## Exceção

Objetos internos do Supabase, como `auth.users`, não devem ser renomeados.

## Padrão

Usar `snake_case`.

## Exemplos corretos

- empresas
- usuarios
- fontes_dados
- tipos_conciliacao
- configuracoes_conciliacao
- regras_conciliacao
- modelos_arquivo
- arquivos_enviados
- fechamentos_financeiros
- transacoes_financeiras
- itens_conciliacao
- divergencias_conciliacao
- relatorios_fechamento
- logs_processamento

## Exemplos proibidos

- companies
- users
- data_sources
- financial_closings
- reconciliation_rules
- daxx_conciliacao
- regras_daxx
- arquivos_daxx

## Regras adicionais

- Não criar tabela com nome de cliente.
- Não criar coluna com nome de cliente.
- Não criar enum em inglês.
- Não criar constraint ou índice em inglês.
- Não criar migration com nome em inglês.
