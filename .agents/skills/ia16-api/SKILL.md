# Skill: ia16-api

## Quando usar

Acione esta skill SEMPRE que for:

- criar um novo endpoint no backend (FastAPI)
- criar uma nova chamada de API no frontend (Nuxt 4)
- revisar um endpoint existente
- implementar qualquer funcionalidade que envolva comunicação entre frontend e backend

## Objetivo

Garantir que todo endpoint siga o padrão oficial definido em `docs/08_Padrao_API_Contratos.md`.

## O que esta skill faz

1. Lê o documento `docs/08_Padrao_API_Contratos.md` para garantir que o padrão está sendo seguido.
2. Gera ou revisa o contrato do endpoint antes de qualquer implementação.
3. Valida que request e response usam nomes em português.
4. Valida que a resposta segue o padrão `sucesso`, `dados`, `mensagem`, `erro` e `paginacao`.
5. Valida que autenticação, autorização e vínculo com empresa estão previstos.
6. Garante que o contrato está alinhado entre Nuxt 4, FastAPI, Pydantic e Supabase.

## Fluxo obrigatório

### Passo 1 — Ler o padrão

Antes de gerar qualquer contrato, ler:

```text
docs/08_Padrao_API_Contratos.md
```

### Passo 2 — Identificar o módulo

Perguntar ou identificar:

- Qual o módulo? (ex: fechamentos, divergencias, arquivos)
- Qual a ação? (CRUD ou ação de negócio)
- Quem pode usar? (admin_ia16 / cliente_admin / cliente_operador)

### Passo 3 — Gerar o contrato

Usar a estrutura obrigatória da seção 14 do documento de padrão:

```md
# Contrato de API: [Nome do Módulo]

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

### Passo 4 — Validar o contrato

Checar antes de liberar a implementação:

- [ ] Endpoint começa com `/api/v1`
- [ ] Todos os campos do body e response estão em português
- [ ] Response de sucesso segue padrão `sucesso`, `dados`, `mensagem`
- [ ] Response de lista inclui `paginacao`
- [ ] Erros seguem padrão `sucesso: false`, `erro.codigo`, `erro.mensagem`
- [ ] Permissões estão definidas por perfil
- [ ] Vínculo com `empresa_id` está validado para clientes
- [ ] Não existe payload inventado

### Passo 5 — Liberar para implementação

Somente após validação completa do contrato, autorizar:

- implementação do schema Pydantic no backend
- implementação do composable ou store no frontend
- geração da migration se necessário

## Proibições

- Não gerar contrato com campos em inglês.
- Não liberar endpoint sem contrato validado.
- Não inventar payload a partir de suposições.
- Não alterar regra de negócio sem consultar o FDD correspondente.

## Referência

- `docs/08_Padrao_API_Contratos.md`
- `.Codex/rules/06-padrao-api-contratos.md`
- FDD correspondente ao módulo sendo implementado
