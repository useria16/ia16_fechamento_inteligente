# iA16 Fechamento Inteligente, pacote de especificação do MVP

Este pacote contém os documentos base para desenvolver o MVP no Claude Code.

## Ordem sugerida de leitura

1. `01_PRD_Produto.md`
2. `02_Arquitetura_Tecnica.md`
3. `03_Padrao_Banco_Dados.md`
4. `04_Roadmap_MVP.md`
5. `05_Funcionalidades_Negocio.md`
6. `06_Escopo_Cliente_Daxx_Conciliacao_Bancaria.md`
7. Documentos da pasta `fdd/`
8. Prompts da pasta `prompts/`

## Objetivo do MVP

Criar uma aplicação enxuta, funcional e confiável para fechamento financeiro assistido, permitindo que o cliente envie planilhas, processe conciliações, visualize divergências e gere relatórios.

## Stack oficial

- Nuxt 4
- Vue
- TypeScript
- Tailwind CSS
- Pinia
- Zod
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- Pandas
- OpenPyXL
- Supabase Postgres
- Supabase Auth
- Supabase Storage
- Supabase RLS
- Docker
- Docker Compose
- Nginx
- VPS

## Decisão importante

Todos os objetos customizados do banco de dados devem ser criados em português.

Isso inclui:

- tabelas
- colunas
- enums
- constraints
- índices
- views
- funções
- migrations
- comentários

Observação: objetos internos e gerenciados pelo Supabase, como `auth.users`, não devem ser renomeados.
## Atualização multicliente

O pacote agora inclui estratégia para múltiplos clientes e múltiplos tipos de conciliação.

Novo documento:

- `07_Estrategia_Multicliente_Multiconciliacao.md`

Novo FDD:

- `fdd/12_FDD_Tipos_Configuracoes_Regras_Conciliacao.md`
