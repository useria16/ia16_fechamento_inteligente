# Padrão de API e Contratos

## 1. Objetivo

Este documento define o padrão oficial de criação de APIs do projeto iA16 Fechamento Inteligente.

O objetivo é garantir alinhamento entre frontend Nuxt 4, backend FastAPI e banco Supabase, evitando divergências de nomes, payloads, respostas e regras de negócio.

## 2. O que é contrato de API

Contrato de API é a definição formal de como frontend e backend conversam.

Cada contrato deve descrever:

- endpoint
- método HTTP
- objetivo
- permissões
- parâmetros de rota
- query params
- body da requisição
- resposta de sucesso
- respostas de erro
- status HTTP
- regras de negócio
- validações
- exemplos JSON
- impacto no frontend
- impacto no backend

Nenhum endpoint deve ser implementado sem contrato definido.

## 3. Versão da API

Toda API deve usar versionamento desde o início:

```text
/api/v1
```

## 4. Idioma e nomenclatura

Como o banco de dados do projeto usa português, a API também deve usar português.

Usar:

```text
empresa_id
fechamento_id
tipo_conciliacao_id
configuracao_conciliacao_id
criado_em
atualizado_em
```

Evitar:

```text
company_id
closing_id
reconciliation_type_id
created_at
updated_at
```

## 5. Convenção de endpoints

Usar REST simples para recursos.

### CRUD

```text
GET    /api/v1/empresas
POST   /api/v1/empresas
GET    /api/v1/empresas/{id}
PATCH  /api/v1/empresas/{id}
DELETE /api/v1/empresas/{id}
```

### Ações de negócio

Usar endpoints explícitos para ações.

```text
POST /api/v1/fechamentos/{id}/processar
POST /api/v1/fechamentos/{id}/reprocessar
POST /api/v1/fechamentos/{id}/aprovar
POST /api/v1/divergencias/{id}/resolver
POST /api/v1/fechamentos/{id}/exportar
```

## 6. Padrão de resposta de sucesso

### Objeto único

```json
{
  "sucesso": true,
  "dados": {
    "id": "uuid",
    "status": "rascunho"
  },
  "mensagem": "Operação realizada com sucesso"
}
```

### Lista

```json
{
  "sucesso": true,
  "dados": [],
  "paginacao": {
    "pagina": 1,
    "limite": 20,
    "total": 0,
    "total_paginas": 0
  }
}
```

## 7. Padrão de resposta de erro

```json
{
  "sucesso": false,
  "erro": {
    "codigo": "ARQUIVO_INVALIDO",
    "mensagem": "O arquivo enviado não possui as colunas obrigatórias.",
    "detalhes": {
      "colunas_ausentes": ["data", "valor", "descricao"]
    }
  }
}
```

## 8. Status HTTP

Usar os códigos HTTP de forma consistente.

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
500 Internal Server Error
```

Exemplos:

```text
Arquivo sem coluna obrigatória = 422
Usuário tentando acessar empresa de outro cliente = 403
Fechamento inexistente = 404
Processar fechamento sem arquivo = 409
```

## 9. Paginação

Toda listagem deve suportar paginação.

Query params padrão:

```text
pagina
limite
```

Exemplo:

```text
GET /api/v1/fechamentos?pagina=1&limite=20
```

Resposta:

```json
{
  "sucesso": true,
  "dados": [],
  "paginacao": {
    "pagina": 1,
    "limite": 20,
    "total": 100,
    "total_paginas": 5
  }
}
```

## 10. Filtros

Listagens devem prever filtros relevantes.

Exemplos:

```text
GET /api/v1/fechamentos?status=processado
GET /api/v1/divergencias?fechamento_id=uuid&status=aberta
GET /api/v1/arquivos?tipo_arquivo=extrato_bancario
```

## 11. Autenticação e autorização

Toda API sensível deve validar:

- usuário autenticado
- vínculo com empresa
- permissão para ação
- perfil do usuário

Perfis iniciais:

```text
admin_ia16
cliente_admin
cliente_operador
```

Regras gerais:

- cliente acessa apenas dados da própria empresa
- admin iA16 pode acessar múltiplas empresas
- cliente operador não altera regras de conciliação
- cliente não acessa configurações críticas do motor

## 12. Idempotência e ações críticas

Ações críticas não devem gerar duplicidade.

Exemplo:

```text
POST /api/v1/fechamentos/{id}/processar
```

Se o fechamento já estiver em processamento, retornar:

```http
409 Conflict
```

Resposta:

```json
{
  "sucesso": false,
  "erro": {
    "codigo": "FECHAMENTO_EM_PROCESSAMENTO",
    "mensagem": "Este fechamento já está em processamento."
  }
}
```

## 13. OpenAPI

O FastAPI deve gerar o contrato OpenAPI automaticamente.

Endpoints de documentação:

```text
/docs
/openapi.json
```

Os schemas Pydantic devem ser usados como base formal do contrato.

## 14. Estrutura obrigatória de contrato

Cada contrato deve seguir este formato:

```md
# Contrato de API, Nome do Módulo

## Endpoint

`MÉTODO /api/v1/recurso`

## Objetivo

## Permissões

## Request

### Path params

### Query params

### Body

## Response de sucesso

## Responses de erro

## Regras de negócio

## Validações

## Impacto no frontend

## Impacto no backend

## Exemplo de uso

## Checklist de aceite
```

## 15. Endpoints iniciais do MVP

```text
/api/v1/auth/me

/api/v1/empresas
/api/v1/usuarios

/api/v1/tipos-conciliacao
/api/v1/configuracoes-conciliacao
/api/v1/regras-conciliacao

/api/v1/fontes-dados
/api/v1/modelos-arquivo

/api/v1/arquivos
/api/v1/arquivos/{id}

/api/v1/fechamentos
/api/v1/fechamentos/{id}
/api/v1/fechamentos/{id}/processar
/api/v1/fechamentos/{id}/reprocessar
/api/v1/fechamentos/{id}/aprovar

/api/v1/fechamentos/{id}/divergencias
/api/v1/divergencias/{id}
/api/v1/divergencias/{id}/resolver

/api/v1/fechamentos/{id}/relatorio
/api/v1/fechamentos/{id}/exportar

/api/v1/conciliacoes/exportar-mensal
/api/v1/conciliacoes/exportar-periodo

/api/v1/dashboard/resumo
/api/v1/logs-processamento
```

## 16. Contrato — Empresas

### `GET /api/v1/empresas`

Lista empresas disponíveis para o usuário autenticado.

#### Permissões

| Perfil | Comportamento |
|---|---|
| `admin_ia16` | Lista todas as empresas. |
| `cliente_admin`, `cliente_operador` | Lista somente a empresa vinculada ao usuário. |

#### Resposta de sucesso — `200 OK`

```json
[
  {
    "id": "uuid",
    "nome": "DAXX MIDIA LTDA",
    "cnpj": "11775820000171",
    "status": "ativa",
    "criado_em": "2026-07-08T00:00:00Z",
    "atualizado_em": "2026-07-08T00:00:00Z"
  }
]
```

### `POST /api/v1/empresas`

Cria uma empresa. Uso restrito ao perfil `admin_ia16`.

#### Body

```json
{
  "nome": "DAXX MIDIA LTDA",
  "cnpj": "11.775.820/0001-71"
}
```

#### Regras

- `nome` é obrigatório.
- `cnpj` é obrigatório.
- O backend normaliza o CNPJ para apenas números.
- CNPJ deve conter 14 dígitos.
- CNPJ não pode estar duplicado.

#### Resposta de sucesso — `201 Created`

```json
{
  "id": "uuid",
  "nome": "DAXX MIDIA LTDA",
  "cnpj": "11775820000171",
  "status": "ativa",
  "criado_em": "2026-07-08T00:00:00Z",
  "atualizado_em": "2026-07-08T00:00:00Z"
}
```

#### Erros

| HTTP | Quando |
|---|---|
| `401` | Usuário não autenticado. |
| `403` | Usuário não tem perfil `admin_ia16`. |
| `409` | CNPJ já cadastrado. |
| `422` | CNPJ inválido ou body incompleto. |

### `GET /api/v1/empresas/{empresa_id}`

Retorna uma empresa pelo ID.

- `admin_ia16` pode acessar qualquer empresa.
- Usuários clientes só podem acessar a própria empresa.

### `PATCH /api/v1/empresas/{empresa_id}`

Atualiza dados básicos da empresa. Uso restrito ao perfil `admin_ia16`.

#### Body

```json
{
  "nome": "DAXX MIDIA LTDA",
  "status": "ativa"
}
```

## 17. Contrato — Exportação Mensal de Conciliação

### `GET /api/v1/conciliacoes/exportar-mensal`

Gera e retorna uma planilha Excel com todos os lançamentos conciliados de uma empresa, tipo e mês, acumulados em uma única aba no layout da planilha mensal padrão.

**Importante:** esta rota estática deve estar registrada antes de `/{conciliacao_id}` no router para não ser capturada pela rota dinâmica (FastAPI/Starlette resolve por ordem de registro).

#### Query params

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `ano` | inteiro | sim | Ano do período. Entre 2000 e 2100. |
| `mes` | inteiro | sim | Mês do período. Entre 1 e 12. |
| `tipo_conciliacao` | string | sim | Tipo de conciliação (ex: `extrato_anotado`, `bancaria`). |
| `empresa_id` | string (UUID) | condicional | Obrigatório para `admin_ia16`. Ignorado para usuários comuns (usa empresa do perfil). |
| `status_incluidos` | string | não | Status separados por vírgula. Padrão: `processado,com_divergencias,aprovado,reaberto`. |

#### Comportamento por perfil

| Perfil | Comportamento |
|---|---|
| `cliente_operador`, `cliente_admin` | Exporta somente a empresa vinculada ao perfil. `empresa_id` é ignorado se informado. |
| `admin_ia16` | Deve informar `empresa_id`. Pode exportar qualquer empresa. |

#### Regras

- O endpoint nunca mistura dados de empresas diferentes.
- O período é determinado pelo campo `periodo_inicio` do fechamento.
- Conciliações com `periodo_inicio` no mês/ano informado são incluídas.
- Conciliações fora do mês não são incluídas.
- Os lançamentos de todos os dias do mês são acumulados em ordem por data.

#### Resposta de sucesso — `200 OK`

```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="Conciliacao_<Nome_da_Empresa>_<Nome_do_Mes>_<Ano>.xlsx"
```

Exemplo de nome: `Conciliacao_Empresa_Exemplo_Junho_2026.xlsx`

Corpo: binário do arquivo Excel com **uma única aba** no layout da planilha conciliada mensal:

| Linha | Conteúdo |
|---|---|
| 1 | `Atualização:` / `metadados["atualizacao"]` do arquivo de extrato, ou data/hora atual como fallback |
| 2 | `Nome:` / `metadados["nome"]` do arquivo de extrato, ou nome da empresa como fallback |
| 3 | `Agência:` / `metadados["agencia"]` do arquivo de extrato, ou vazio se não disponível |
| 4 | `Conta:` / `metadados["conta"]` do arquivo de extrato, ou vazio se não disponível |
| 5 | (vazia) |
| 6 | `Periodo:  <Mês>/<Ano>` |
| 7 | (vazia) |
| 8 | Cabeçalho da tabela |
| 9 | `SALDO TOTAL DISPONÍVEL DIA` — saldo antes do primeiro lançamento do mês |
| 10+ | Lançamentos acumulados do mês em ordem cronológica |
| última | `SALDO TOTAL DISPONÍVEL DIA` — saldo final (fórmula acumulada) |

**Metadados:** o service busca todos os `ArquivoEnviado` com `tipo_arquivo = "extrato_bancario"` vinculados aos fechamentos do mês, em ordem cronológica, e seleciona o mais completo seguindo esta prioridade:
1. Primeiro arquivo que tiver `agencia` **e** `conta` preenchidos — usado imediatamente.
2. Se nenhum tiver ambos, usa o primeiro que tiver pelo menos `agencia` **ou** `conta`.
3. Se nenhum arquivo tiver metadados úteis, aplica fallback: `Nome` = nome da empresa, `Agência` e `Conta` = vazios, `Atualização` = data/hora atual.

Colunas da tabela (linha 8):

| Coluna | Campo |
|---|---|
| DATA | Data do lançamento |
| DESCRIÇÃO LANÇAMENTO BANCO | Descrição do extrato bancário |
| DESCRIÇÃO FORNECEDOR/CLIENTE | Razão social / descrição de negócio |
| NF / DOC | Número de nota fiscal ou documento |
| VALOR NF/DOC | Valor da nota fiscal ou documento |
| ENTRADA EXTRATO | Valor quando tipo_movimento = entrada |
| SAIDA EXTRATO | Valor quando tipo_movimento = saida |
| SALDO | Saldo do lançamento (quando disponível) |

Nome da aba: abreviação PT-BR do mês + 2 últimos dígitos do ano (ex: `Jun26`, `Dez25`).

#### Erros

| HTTP | Código | Quando |
|---|---|---|
| `400` | `EMPRESA_OBRIGATORIA` | `admin_ia16` não informou `empresa_id`. |
| `400` | `USUARIO_SEM_EMPRESA` | Usuário não tem empresa vinculada. |
| `403` | `SEM_PERMISSAO_EMPRESA` | Usuário tentou informar `empresa_id` diferente da própria empresa. |
| `404` | `EMPRESA_NAO_ENCONTRADA` | `empresa_id` não existe no banco. |
| `404` | `SEM_CONCILIACOES_NO_PERIODO` | Nenhuma conciliação encontrada para o mês/tipo informados. |
| `422` | — | Query params obrigatórios ausentes ou inválidos (FastAPI padrão). |
| `500` | `ERRO_GERACAO_CONSOLIDADO` | Falha inesperada ao gerar o Excel. |

#### Exemplo de request

```
GET /api/v1/conciliacoes/exportar-mensal?ano=2026&mes=6&tipo_conciliacao=extrato_anotado
Authorization: Bearer <token>
```

#### Exemplo com admin

```
GET /api/v1/conciliacoes/exportar-mensal?ano=2026&mes=6&tipo_conciliacao=extrato_anotado&empresa_id=<uuid>
Authorization: Bearer <token>
```

## 18. Contrato — Exportação de Conciliação por Período

### `GET /api/v1/conciliacoes/exportar-periodo`

Gera e retorna uma planilha Excel com todos os lançamentos conciliados de uma empresa, tipo e intervalo livre de datas, acumulados em uma única aba no mesmo layout da exportação mensal.

Este endpoint não substitui a exportação mensal. Ele atende cenários em que o cliente precisa exportar um período personalizado, por exemplo `15/06/2026` até `15/07/2026`.

**Importante:** esta rota estática deve estar registrada antes de `/{conciliacao_id}` no router para não ser capturada pela rota dinâmica.

#### Query params

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `data_inicio` | data ISO (`YYYY-MM-DD`) | sim | Data inicial do período. |
| `data_fim` | data ISO (`YYYY-MM-DD`) | sim | Data final do período. |
| `tipo_conciliacao` | string | sim | Tipo de conciliação. Nesta fase operacional, a tela usa `extrato_anotado`. |
| `empresa_id` | string (UUID) | condicional | Obrigatório para `admin_ia16`. Usuários comuns usam a empresa do perfil. |
| `status_incluidos` | string | não | Status separados por vírgula. Padrão: `processado,com_divergencias,aprovado,reaberto`. |

#### Comportamento por perfil

| Perfil | Comportamento |
|---|---|
| `cliente_operador`, `cliente_admin` | Exporta somente a empresa vinculada ao perfil. Se informar outra empresa, recebe `403`. |
| `admin_ia16` | Deve informar `empresa_id`. Pode exportar qualquer empresa. |

#### Regras

- O endpoint nunca mistura dados de empresas diferentes.
- A exportação por período mantém a exportação mensal existente.
- O período é determinado pelo campo `periodo_inicio` do fechamento.
- Conciliações com `periodo_inicio >= data_inicio` e `periodo_inicio <= data_fim` são incluídas.
- `data_inicio` deve ser menor ou igual a `data_fim`.
- Os lançamentos de todos os fechamentos encontrados são acumulados em ordem cronológica.
- O layout da planilha deve ser o mesmo da exportação mensal e da conciliação diária para `extrato_anotado`.
- O cabeçalho deve usar os metadados do arquivo de extrato com a mesma prioridade da exportação mensal.

#### Resposta de sucesso — `200 OK`

```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="Conciliacao_<Nome_da_Empresa>_<DataInicial>_a_<DataFinal>.xlsx"
```

Exemplo de nome: `Conciliacao_Empresa_Exemplo_15-06-2026_a_15-07-2026.xlsx`

Corpo: binário do arquivo Excel com **uma única aba** no layout da planilha conciliada:

| Linha | Conteúdo |
|---|---|
| 1 | `Atualização:` / `metadados["atualizacao"]` do arquivo de extrato, ou data/hora atual como fallback |
| 2 | `Nome:` / `metadados["nome"]` do arquivo de extrato, ou nome da empresa como fallback |
| 3 | `Agência:` / `metadados["agencia"]` do arquivo de extrato, ou vazio se não disponível |
| 4 | `Conta:` / `metadados["conta"]` do arquivo de extrato, ou vazio se não disponível |
| 5 | (vazia) |
| 6 | `Periodo:  <DataInicial> a <DataFinal>` |
| 7 | (vazia) |
| 8 | Cabeçalho da tabela |
| 9 | `SALDO TOTAL DISPONÍVEL DIA` — saldo antes do primeiro lançamento do período |
| 10+ | Lançamentos acumulados do período em ordem cronológica |
| última | `SALDO TOTAL DISPONÍVEL DIA` — saldo final (fórmula acumulada) |

Nome da aba: intervalo curto com dia, mês abreviado PT-BR e ano final com 2 dígitos. Exemplo: `15Jun-15Jul26`.

#### Erros

| HTTP | Código | Quando |
|---|---|---|
| `400` | `PERIODO_INVALIDO` | `data_inicio` é maior que `data_fim`. |
| `400` | `EMPRESA_OBRIGATORIA` | `admin_ia16` não informou `empresa_id`. |
| `400` | `USUARIO_SEM_EMPRESA` | Usuário não tem empresa vinculada. |
| `403` | `SEM_PERMISSAO_EMPRESA` | Usuário tentou informar `empresa_id` diferente da própria empresa. |
| `404` | `EMPRESA_NAO_ENCONTRADA` | `empresa_id` não existe no banco. |
| `404` | `SEM_CONCILIACOES_NO_PERIODO` | Nenhuma conciliação encontrada para o intervalo/tipo informados. |
| `422` | — | Query params obrigatórios ausentes ou inválidos (FastAPI padrão). |
| `500` | `ERRO_GERACAO_CONSOLIDADO` | Falha inesperada ao gerar o Excel. |

#### Exemplo de request

```
GET /api/v1/conciliacoes/exportar-periodo?data_inicio=2026-06-15&data_fim=2026-07-15&tipo_conciliacao=extrato_anotado
Authorization: Bearer <token>
```

#### Exemplo com admin

```
GET /api/v1/conciliacoes/exportar-periodo?data_inicio=2026-06-15&data_fim=2026-07-15&tipo_conciliacao=extrato_anotado&empresa_id=<uuid>
Authorization: Bearer <token>
```

## 19. Regra final

Nenhuma tela do frontend deve ser implementada consumindo payloads inventados.

Nenhum endpoint do backend deve ser implementado sem contrato.

O contrato de API é a ponte oficial entre Nuxt e FastAPI.
