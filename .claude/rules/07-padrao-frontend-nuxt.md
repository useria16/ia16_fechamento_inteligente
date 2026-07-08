# Padrão Frontend Nuxt

## Regra obrigatória

Toda criação ou alteração no frontend deve seguir:

```text
docs/09_Padrao_Frontend_Nuxt.md
```

## Stack

- Nuxt 4
- Vue
- TypeScript
- Tailwind CSS
- Pinia
- Zod

## Regras principais

- Não criar páginas gigantes.
- Não colocar regra de negócio complexa em `pages/`.
- Usar componentes reutilizáveis.
- Usar composables para lógica reutilizável.
- Usar Pinia apenas para estado compartilhado.
- Usar Zod para validações.
- Usar TypeScript em tipos de domínio.
- Usar contratos de API antes de consumir backend.
- Evitar acoplamento entre componentes.
- Evitar efeitos colaterais ao alterar componentes.
- Manter componentes base genéricos.
- Manter componentes de domínio dentro da pasta correta.

## Fluxo principal do produto

```text
Novo Fechamento = executar conciliação
Arquivos = histórico, consulta e apoio aos uploads
```

## Antes de criar ou alterar frontend

Confirmar:

1. Existe contrato de API?
2. Existe componente reutilizável?
3. A lógica pertence a composable?
4. O estado é local ou global?
5. Existe schema Zod?
6. A alteração pode impactar outro componente?
7. Como testar loading, erro e sucesso?

## Proibições

- Não consumir endpoint sem contrato.
- Não inventar payload no frontend.
- Não criar componente acoplado a cliente específico.
- Não criar lógica específica para Daxx.
- Não alterar componente base sem revisar todos os usos.
- Não usar store global para estado local de formulário.
