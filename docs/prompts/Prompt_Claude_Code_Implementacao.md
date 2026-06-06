# Prompt mestre para Claude Code

Você é o agente responsável por implementar o MVP do iA16 Fechamento Inteligente.

## Contexto

O produto é uma aplicação enxuta para fechamento financeiro assistido. O cliente envia planilhas Excel, a aplicação processa a conciliação, identifica divergências, gera relatórios e permite exportação.

## Stack obrigatória

Frontend:

- Nuxt 4
- Vue
- TypeScript
- Tailwind CSS
- Pinia
- Zod
- Supabase JS

Backend:

- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- Pandas
- OpenPyXL

Banco e serviços:

- Supabase Postgres
- Supabase Auth
- Supabase Storage
- Supabase RLS

Infra:

- Docker
- Docker Compose
- Nginx
- VPS

## Regras obrigatórias

1. Todos os objetos customizados do banco devem estar em português.
2. Tabelas, colunas, enums, constraints, índices, views, funções e migrations devem usar português.
3. Não criar cadastro público de usuários.
4. Não implementar Open Finance no MVP.
5. Não implementar ERP, adquirentes ou integração bancária no MVP.
6. Não transformar o produto em ERP.
7. Separar frontend, backend e motor de conciliação.
8. Usar migrations versionadas com Alembic.
9. Usar SQLAlchemy 2.x, não SQLModel.
10. Garantir segregação por empresa.

## Ordem de implementação

1. Criar estrutura do projeto.
2. Configurar Docker Compose.
3. Criar backend FastAPI.
4. Configurar SQLAlchemy e Alembic.
5. Criar migrations iniciais.
6. Criar frontend Nuxt.
7. Implementar autenticação.
8. Implementar empresas e usuários.
9. Implementar fontes de dados.
10. Implementar modelos de arquivo.
11. Implementar upload.
12. Implementar fechamentos.
13. Implementar motor de conciliação.
14. Implementar divergências.
15. Implementar relatórios.
16. Implementar dashboard.

## Entrega esperada

Gerar código limpo, modular, testável e com comentários apenas onde ajudam a entender regras de domínio.

Antes de alterar arquivos, sempre listar:

- arquivos que serão criados
- arquivos que serão modificados
- objetivo da mudança

Depois da alteração, informar:

- o que foi implementado
- como testar
- próximos passos
