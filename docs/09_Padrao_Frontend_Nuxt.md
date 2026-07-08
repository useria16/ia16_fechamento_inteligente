# Padrão Frontend Nuxt

## 1. Objetivo

Este documento define o padrão oficial de desenvolvimento frontend do projeto iA16 Fechamento Inteligente.

O objetivo é garantir que o frontend seja modular, previsível, reutilizável e seguro para evoluir sem quebrar outras partes da aplicação.

A aplicação usa:

- Nuxt 4
- Vue
- TypeScript
- Tailwind CSS
- Pinia
- Zod

## 2. Princípio principal

Nenhuma tela deve concentrar toda a lógica.

Uma página deve apenas compor a tela, carregar componentes e coordenar ações principais.

A regra geral é:

```text
pages/
  define rotas e composição da tela

components/
  contém componentes visuais reutilizáveis

composables/
  contém lógica reutilizável e chamadas de API

stores/
  contém estado compartilhado com Pinia

schemas/
  contém validações com Zod

types/
  contém tipos TypeScript
```

## 3. Estrutura recomendada

A estrutura inicial do frontend deve seguir este padrão:

```text
frontend/
  app/
    assets/
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
    middleware/
    pages/
    plugins/
    schemas/
    stores/
    types/
    utils/
```

## 4. Padrão de páginas

As páginas em `pages/` devem ser simples.

Uma página pode:

- definir rota
- montar layout
- chamar composables
- passar dados para componentes
- tratar estados principais de carregamento
- redirecionar usuário quando necessário

Uma página não deve:

- conter regra de negócio complexa
- conter validação manual extensa
- montar payloads complexos
- chamar várias APIs diretamente sem composable
- conter componentes grandes inline
- manipular estado global sem necessidade

Exemplo ruim:

```text
pages/fechamentos/novo.vue
  contém formulário inteiro
  contém upload
  contém chamada de API
  contém validação
  contém regra de negócio
  contém tratamento de erro
```

Exemplo correto:

```text
pages/fechamentos/novo.vue
components/fechamentos/FormularioNovoFechamento.vue
components/fechamentos/SeletorTipoConciliacao.vue
components/fechamentos/UploadArquivosFechamento.vue
composables/useFechamentos.ts
composables/useArquivos.ts
schemas/fechamento.schema.ts
types/fechamento.ts
```

## 5. Padrão de componentes

Componentes devem ser reutilizáveis, isolados e previsíveis.

Cada componente deve ter responsabilidade única.

Um componente deve:

- receber dados por `props`
- comunicar ações por `emit`
- evitar dependência direta de outros componentes irmãos
- evitar chamada direta de API, salvo componentes container autorizados
- evitar alteração direta de store global sem necessidade
- ter nome claro
- ter tipagem TypeScript
- ser fácil de testar visualmente

Um componente não deve:

- conhecer regra de negócio que deveria estar em composable
- alterar comportamento de outro componente por efeito colateral
- depender de variável global escondida
- duplicar lógica já existente em composable
- fazer múltiplas responsabilidades ao mesmo tempo

## 6. Tipos de componentes

### Componentes base

Ficam em:

```text
components/base/
```

Exemplos:

```text
BaseButton.vue
BaseInput.vue
BaseSelect.vue
BaseModal.vue
BaseTable.vue
BaseCard.vue
BaseBadge.vue
BaseAlert.vue
BaseLoading.vue
```

Regras:

- não devem ter regra de negócio
- devem ser genéricos
- devem ser reutilizáveis em qualquer módulo
- devem receber comportamento por props e emits

### Componentes de layout

Ficam em:

```text
components/layout/
```

Exemplos:

```text
AppSidebar.vue
AppTopbar.vue
AppShell.vue
AppBreadcrumb.vue
```

Regras:

- podem conhecer estrutura geral da aplicação
- não devem conhecer regra financeira
- não devem processar dados de conciliação

### Componentes de domínio

Ficam em pastas específicas:

```text
components/fechamentos/
components/arquivos/
components/divergencias/
components/relatorios/
components/configuracoes/
```

Exemplos:

```text
FormularioNovoFechamento.vue
TabelaFechamentos.vue
UploadArquivosFechamento.vue
TabelaDivergencias.vue
ResumoFechamento.vue
```

Regras:

- podem conhecer o domínio do módulo
- devem receber dados por props
- devem emitir ações
- devem usar composables para chamadas de API, quando necessário
- não devem acessar diretamente lógica de outro domínio sem necessidade

## 7. Padrão de composables

Composables devem concentrar lógica reutilizável.

Ficam em:

```text
composables/
```

Exemplos:

```text
useFechamentos.ts
useArquivos.ts
useDivergencias.ts
useRelatorios.ts
useTiposConciliacao.ts
useApi.ts
useAuth.ts
```

Um composable pode:

- chamar APIs
- montar query params
- tratar loading
- tratar erros
- expor funções reutilizáveis
- transformar dados para uso da tela
- centralizar chamadas relacionadas a um domínio

Um composable não deve:

- conter HTML
- manipular visual diretamente
- depender de componente específico
- misturar domínios sem necessidade

## 8. Padrão de stores Pinia

Stores devem ser usadas apenas para estado compartilhado.

Ficam em:

```text
stores/
```

Exemplos:

```text
useAuthStore.ts
useEmpresaStore.ts
useLayoutStore.ts
useNotificacoesStore.ts
```

Usar store para:

- sessão do usuário
- empresa atual
- permissões
- estado global de layout
- notificações globais

Não usar store para:

- estado local de formulário
- dados temporários de uma única tela
- controle simples de modal local
- evitar passagem correta de props

## 9. Padrão de schemas Zod

Validações de formulário devem usar Zod.

Ficam em:

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

Cada schema deve:

- validar campos obrigatórios
- validar tipos
- validar datas
- validar valores numéricos
- gerar mensagens claras para o usuário

Exemplo conceitual:

```ts
export const criarFechamentoSchema = z.object({
  titulo: z.string().min(3),
  periodo_inicio: z.string(),
  periodo_fim: z.string(),
  tipo_conciliacao_id: z.string().uuid(),
  configuracao_conciliacao_id: z.string().uuid()
})
```

## 10. Padrão de types TypeScript

Tipos compartilhados devem ficar em:

```text
types/
```

Exemplos:

```text
fechamento.ts
arquivo.ts
divergencia.ts
empresa.ts
usuario.ts
api.ts
```

Os tipos devem usar nomes em português quando representam dados da aplicação.

Exemplos corretos:

```ts
export interface FechamentoFinanceiro {
  id: string
  empresa_id: string
  titulo: string
  status: string
  criado_em: string
}
```

Evitar:

```ts
export interface FinancialClosing {
  company_id: string
  created_at: string
}
```

## 11. Padrão de chamadas API

Toda chamada de API deve seguir o contrato definido em:

```text
docs/08_Padrao_API_Contratos.md
```

Regras:

- não inventar payload no frontend
- não consumir endpoint sem contrato
- não tratar resposta fora do padrão
- usar `/api/v1`
- usar nomes em português
- centralizar cliente HTTP em composable, por exemplo `useApi.ts`

Padrão esperado de resposta:

```ts
interface ApiResposta<T> {
  sucesso: boolean
  dados?: T
  mensagem?: string
  erro?: {
    codigo: string
    mensagem: string
    detalhes?: Record<string, unknown>
  }
  paginacao?: {
    pagina: number
    limite: number
    total: number
    total_paginas: number
  }
}
```

## 12. Padrão visual

A identidade visual deve seguir o padrão da iA16.

Direção visual:

- fundo azul-marinho escuro
- sidebar azul-marinho escuro
- azul iA16 como cor principal de destaque
- ciano/azul claro como cor de apoio
- texto branco, cinza claro e cinza médio
- cards escuros com borda sutil
- visual corporativo, premium e minimalista

Evitar:

- visual colorido demais
- aparência de ERP antigo
- excesso de bordas
- excesso de informações em uma tela
- componentes visuais inconsistentes

## 13. Sidebar e módulos

A sidebar do MVP deve priorizar simplicidade.

Menu principal:

```text
Dashboard
Novo Fechamento
Fechamentos
Arquivos
Divergências
Relatórios
Configurações
```

Função dos módulos:

```text
Dashboard = consulta e visão executiva
Novo Fechamento = fluxo principal de conciliação
Fechamentos = histórico e gestão dos fechamentos
Arquivos = histórico, consulta e apoio aos uploads
Divergências = revisão operacional
Relatórios = consulta e download
Configurações = restrito ou controlado pela iA16
```

Regra importante:

```text
Novo Fechamento é onde o usuário executa a conciliação.
Arquivos é apoio, histórico e gestão dos arquivos enviados.
```

## 14. Fluxo Novo Fechamento

A tela Novo Fechamento deve ser guiada.

Fluxo recomendado:

```text
1. Escolher tipo de conciliação
2. Informar período
3. Enviar ou selecionar arquivos
4. Validar arquivos
5. Processar conciliação
6. Revisar divergências
7. Exportar resultado
```

Componentes sugeridos:

```text
FormularioNovoFechamento.vue
SeletorTipoConciliacao.vue
SeletorPeriodoFechamento.vue
UploadArquivosFechamento.vue
ResumoArquivosFechamento.vue
BotaoProcessarFechamento.vue
```

## 15. Fluxo Arquivos

O módulo Arquivos deve servir como apoio.

Permitir:

- listar arquivos enviados
- visualizar status de validação
- baixar arquivo original
- ver fechamento vinculado
- enviar arquivo avulso, se permitido
- vincular arquivo a fechamento, se permitido

Não deve ser o caminho principal da conciliação.

## 16. Isolamento e impacto entre componentes

Alterar um componente não deve gerar efeito colateral inesperado em outro componente.

Para isso:

- componente deve ter props claras
- componente deve emitir eventos claros
- componente não deve alterar estado global sem necessidade
- componente não deve importar componente irmão para manipular seu estado
- componente não deve depender de estrutura interna de outro componente
- componente base deve ser genérico e estável
- componente de domínio deve ficar isolado no domínio correto

Antes de alterar componente reutilizável, verificar:

- onde ele é usado
- quais props existem
- quais eventos emite
- se a mudança quebra compatibilidade
- se é melhor criar novo componente em vez de alterar o existente

## 17. Estados de tela

Toda tela de listagem ou operação deve prever:

- carregando
- vazio
- erro
- sucesso
- sem permissão
- dados carregados

Exemplos:

```text
Nenhum fechamento encontrado.
Nenhum arquivo enviado.
Nenhuma divergência aberta.
Você não tem permissão para acessar esta área.
```

## 18. Responsividade

O MVP deve priorizar desktop, mas não deve quebrar em telas menores.

Regras:

- sidebar pode recolher em telas menores
- tabelas devem ter scroll horizontal quando necessário
- cards devem quebrar linha
- formulários devem ser legíveis
- modais não devem ultrapassar a tela

## 19. Acessibilidade básica

Componentes devem considerar:

- labels em inputs
- foco visível
- botões com texto claro
- mensagens de erro compreensíveis
- contraste adequado
- navegação básica por teclado

## 20. Checklist antes de criar tela ou componente

Antes de implementar, responder:

1. Esta tela já existe?
2. Este componente pode ser reutilizado?
3. A lógica deve ficar em composable?
4. O estado deve ser local ou Pinia?
5. Existe schema Zod?
6. Existe contrato de API?
7. Quais componentes serão impactados?
8. A mudança pode gerar efeito colateral?
9. Como testar visualmente?
10. Como testar erro e loading?

## 21. Proibições

Não fazer:

- página gigante com toda lógica dentro
- componente que chama API sem necessidade
- componente que altera store global sem necessidade
- duplicar lógica em várias telas
- criar componente específico demais quando poderia ser reutilizável
- misturar lógica de fechamento com lógica de arquivo sem separação
- consumir API sem contrato
- usar nomes em inglês para entidades do domínio
- quebrar componente base usado em várias telas sem revisar impactos

## 22. Regra final

O frontend deve ser modular, reutilizável e previsível.

Toda tela deve ser construída com componentes pequenos, composables claros, contratos de API definidos e baixo acoplamento entre partes.
