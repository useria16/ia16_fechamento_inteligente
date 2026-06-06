# Domínio de negócio

## Perfis de usuário

Três perfis definidos. Usar exatamente esses nomes:

```text
admin_ia16       → acessa todas as empresas
cliente_admin    → acessa própria empresa, gerencia usuários da empresa
cliente_operador → acessa própria empresa, executa operações de fechamento
```

Telas administrativas (`/admin/*`) são acessíveis apenas pelo `admin_ia16`.

## Status de fechamento

Enum em português, usar exatamente estes valores:

```text
rascunho
arquivos_enviados
em_processamento
processado
com_divergencias
aprovado
erro
cancelado
```

## Tipos de divergência

```text
valor_diferente
data_diferente
registro_nao_encontrado
registro_duplicado
taxa_divergente
recebimento_pendente
categoria_inconsistente
outro
```

## Status de conciliação de item

```text
conciliado
divergente
pendente
duplicado
nao_encontrado
erro
```

## Tipos de fonte de dados

```text
excel_manual
banco
adquirente
erp
google_drive
outro
```

## Tipos de arquivo

```text
extrato_bancario
relatorio_vendas
relatorio_recebiveis
planilha_interna
taxas_adquirente
outro
```

## Operadores de regra de conciliação

```text
igual
valor_igual
valor_com_tolerancia
data_igual
data_com_tolerancia
texto_contem
texto_similar
existe
nao_existe
```

## Ordem dos critérios do motor de conciliação

O motor deve aplicar nesta ordem:

1. documento igual e valor igual
2. data próxima e valor igual
3. descrição similar e valor igual
4. valor próximo dentro de tolerância configurada
5. registro sem par correspondente

## Reprocessamento

Fechamento pode ser reprocessado. Regras obrigatórias:

- nunca apagar arquivo original
- manter histórico de logs
- marcar tentativa anterior como substituída
- atualizar status do fechamento
- regenerar saídas

## Rotas da API FastAPI

Padrão:

```text
GET  /api/empresas
POST /api/empresas
GET  /api/usuarios
POST /api/usuarios
GET  /api/fechamentos
POST /api/fechamentos
POST /api/fechamentos/{id}/processar
GET  /api/divergencias
GET  /api/tipos-conciliacao
POST /api/tipos-conciliacao
GET  /api/configuracoes-conciliacao
POST /api/configuracoes-conciliacao
POST /api/configuracoes-conciliacao/{id}/regras
```

## Rotas do frontend Nuxt

```text
/login
/dashboard
/fechamentos
/fechamentos/novo
/fechamentos/[id]
/divergencias
/admin/empresas
/admin/empresas/nova
/admin/empresas/[id]
/admin/usuarios
/admin/usuarios/novo
/tipos-conciliacao
/configuracoes-conciliacao
/configuracoes-conciliacao/nova
/configuracoes-conciliacao/[id]
```

## Ordem de implementação (sprints)

Respeitar a ordem definida no roadmap:

1. Sprint 1 — Base do projeto (Nuxt, FastAPI, Docker, Supabase, Alembic)
2. Sprint 2 — Autenticação, empresas e usuários
3. Sprint 3 — Fontes de dados e modelos de arquivo
4. Sprint 3.1 — Tipos, configurações e regras de conciliação
5. Sprint 4 — Upload de arquivos
6. Sprint 5 — Fechamentos financeiros
7. Sprint 6 — Motor de conciliação
8. Sprint 7 — Divergências e observações
9. Sprint 8 — Relatórios, exportação e dashboard

Não implementar uma sprint sem que a anterior esteja completa, salvo autorização explícita.

## FDD de referência por funcionalidade

| Funcionalidade | FDD |
|---|---|
| Autenticação, empresas, usuários | FDD 01 |
| Fontes de dados | FDD 02 |
| Modelos de arquivo | FDD 03 |
| Upload de arquivos | FDD 04 |
| Fechamentos financeiros | FDD 05 |
| Motor de conciliação | FDD 06 |
| Divergências e observações | FDD 07 |
| Relatórios e exportação | FDD 08 |
| Dashboard | FDD 09 |
| Logs de processamento | FDD 10 |
| Resumo executivo com IA | FDD 11 |
| Tipos, configurações e regras de conciliação | FDD 12 |

Sempre consultar o FDD correspondente antes de implementar qualquer funcionalidade.
