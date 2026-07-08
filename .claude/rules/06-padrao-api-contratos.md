# Padrão de API e Contratos

## Regra central

Nenhum endpoint deve ser implementado sem contrato definido.

Nenhuma tela do frontend deve consumir payload inventado.

## Versão obrigatória

```text
/api/v1
```

## Idioma

Requests e responses devem usar nomes em português, alinhados ao banco de dados.

Exemplos corretos:

```text
empresa_id
fechamento_id
tipo_conciliacao_id
criado_em
atualizado_em
```

Exemplos proibidos:

```text
company_id
closing_id
created_at
updated_at
```

## Padrão de resposta de sucesso

Objeto único:

```json
{
  "sucesso": true,
  "dados": {},
  "mensagem": "Operação realizada com sucesso"
}
```

Lista paginada:

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

## Padrão de resposta de erro

```json
{
  "sucesso": false,
  "erro": {
    "codigo": "CODIGO_ERRO",
    "mensagem": "Mensagem descritiva.",
    "detalhes": {}
  }
}
```

## Autenticação e autorização

Toda API sensível deve validar:

- usuário autenticado
- vínculo com empresa
- permissão para ação
- perfil do usuário

## Proibições

- Não criar endpoint sem contrato.
- Não inventar payload no frontend.
- Não alterar regras de negócio fora dos documentos de referência.
- Não usar inglês em campos de request ou response.

## Documento de referência completo

`docs/08_Padrao_API_Contratos.md`

## Skill de apoio

Usar a skill `ia16-api` antes de implementar qualquer endpoint.
