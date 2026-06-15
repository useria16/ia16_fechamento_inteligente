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

/api/v1/dashboard/resumo
/api/v1/logs-processamento
```

## 16. Regra final

Nenhuma tela do frontend deve ser implementada consumindo payloads inventados.

Nenhum endpoint do backend deve ser implementado sem contrato.

O contrato de API é a ponte oficial entre Nuxt e FastAPI.
