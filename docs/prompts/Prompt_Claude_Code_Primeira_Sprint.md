# Prompt para primeira sprint no Claude Code

Implemente a base inicial do projeto iA16 Fechamento Inteligente.

## Objetivo da sprint

Criar a estrutura inicial do projeto com frontend Nuxt 4, backend FastAPI, Docker Compose, Nginx, SQLAlchemy, Alembic e configuração para Supabase.

## Stack

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
- Supabase Postgres
- Supabase Auth
- Supabase Storage
- Docker
- Docker Compose
- Nginx

## Regras obrigatórias

- Todos os objetos customizados do banco devem estar em português.
- Não usar SQLModel.
- Não criar cadastro público.
- Não implementar módulos fora da sprint.
- Não criar funcionalidades de ERP.
- Não implementar integração bancária.

## Estrutura sugerida

```text
ia16-fechamento-inteligente/
  frontend/
  backend/
  infra/
    nginx/
  docker-compose.yml
  .env.example
  README.md
```

## Entregas

1. Criar projeto Nuxt 4 em `frontend`.
2. Criar projeto FastAPI em `backend`.
3. Criar Dockerfile do frontend.
4. Criar Dockerfile do backend.
5. Criar docker-compose com frontend, backend e nginx.
6. Criar configuração inicial do Nginx.
7. Criar conexão SQLAlchemy com Supabase Postgres.
8. Criar setup Alembic.
9. Criar `.env.example`.
10. Criar endpoint `/health` no backend.
11. Criar página inicial simples no frontend.
12. Atualizar README com comandos de execução.

## Critérios de aceite

- `docker compose up` sobe frontend, backend e nginx.
- Frontend responde no domínio ou porta configurada.
- Backend responde `/health`.
- Backend consegue inicializar configuração de banco.
- Alembic está pronto para criar migrations.
