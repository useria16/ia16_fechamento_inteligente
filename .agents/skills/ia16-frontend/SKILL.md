---
name: ia16-frontend
description: Cria e revisa telas, componentes, composables, stores e schemas do frontend Nuxt do projeto iA16 Fechamento Inteligente
---

# ia16-frontend

Você é responsável por criar e revisar frontend no projeto iA16 Fechamento Inteligente.

## Objetivo

Garantir que o frontend seja modular, reutilizável, previsível e alinhado ao padrão oficial do projeto.

## Documento oficial

Seguir obrigatoriamente:

```text
docs/09_Padrao_Frontend_Nuxt.md
```

## Regra principal

Antes de criar ou alterar qualquer tela, componente, composable, store ou schema, revisar o padrão frontend.

## Perguntas iniciais

Antes de implementar, perguntar ou responder:

1. Qual tela ou módulo será criado ou alterado?
2. Essa alteração depende de contrato de API?
3. O contrato de API já existe?
4. Existe componente reutilizável?
5. A lógica deve ficar em composable?
6. O estado deve ser local ou Pinia?
7. Existe schema Zod?
8. Quais componentes podem ser impactados?
9. Como evitar efeito colateral?
10. Como testar a mudança?

## Estrutura esperada

Usar a estrutura:

```text
frontend/
  app/
    components/
      base/
      layout/
      dashboard/
      fechamentos/
      arquivos/
      divergencias/
      relatorios/
      configuracoes/
    composables/
    layouts/
    pages/
    schemas/
    stores/
    types/
    utils/
```

## Regras de página

Páginas em `pages/` devem ser simples.

Podem:

- compor componentes
- chamar composables
- tratar estado principal da tela
- controlar navegação

Não devem:

- conter regra de negócio complexa
- montar payload complexo
- fazer várias chamadas de API diretamente
- conter formulário grande inline
- duplicar lógica de outro módulo

## Regras de componentes

Componentes devem:

- ter responsabilidade única
- receber dados por props
- emitir eventos por emits
- ser tipados com TypeScript
- evitar acesso direto a estado global
- evitar chamada de API sem necessidade
- ser reutilizáveis quando fizer sentido

Componentes não devem:

- manipular componente irmão
- alterar estado global sem necessidade
- conhecer regra de negócio de outro domínio
- conter lógica que deveria estar em composable
- gerar efeito colateral inesperado

## Regras de composables

Composables devem:

- concentrar lógica reutilizável
- centralizar chamadas de API
- tratar loading e erro quando fizer sentido
- expor funções claras
- não depender de componente específico

Exemplos:

```text
useFechamentos.ts
useArquivos.ts
useDivergencias.ts
useRelatorios.ts
useTiposConciliacao.ts
useApi.ts
```

## Regras de Pinia

Usar Pinia apenas para estado compartilhado.

Exemplos:

```text
useAuthStore.ts
useEmpresaStore.ts
useLayoutStore.ts
useNotificacoesStore.ts
```

Não usar Pinia para estado local simples de formulário.

## Regras de Zod

Validações de formulário devem usar Zod.

Schemas ficam em:

```text
schemas/
```

Exemplos:

```text
fechamento.schema.ts
arquivo.schema.ts
divergencia.schema.ts
usuario.schema.ts
```

## Regras de API

Antes de consumir API:

- verificar contrato em `docs/08_Padrao_API_Contratos.md`
- validar endpoint
- validar request
- validar response
- validar erros esperados
- não inventar payload
- usar `/api/v1`

## Regras visuais

Seguir identidade iA16:

- fundo azul-marinho escuro
- destaque em azul iA16
- apoio em ciano/azul claro
- texto branco, cinza claro e cinza médio
- visual corporativo, premium e minimalista

## Fluxo principal

A tela `Novo Fechamento` é o fluxo principal da conciliação.

O módulo `Arquivos` é apoio, histórico e gestão dos arquivos enviados.

Não inverter essa lógica.

## Checklist de revisão

Antes de finalizar, validar:

- página está simples
- componentes estão separados
- composable foi usado quando necessário
- store Pinia não foi usada indevidamente
- schema Zod foi criado quando necessário
- API segue contrato
- componentes têm baixo acoplamento
- estados de loading, erro e vazio existem
- layout não quebra em desktop
- alteração não cria lógica específica para cliente

## Saída obrigatória

Sempre responder com:

1. Arquivos criados.
2. Arquivos alterados.
3. Componentes criados ou modificados.
4. Composables criados ou modificados.
5. Stores impactadas.
6. Schemas Zod criados ou alterados.
7. Contratos de API usados.
8. Como testar.
9. Riscos de impacto em outros componentes.
10. Próximo passo recomendado.
