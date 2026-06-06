# iA16 Fechamento Inteligente

Plataforma multicliente para conciliação financeira configurável.

## Stack

- **Frontend:** Nuxt 4, Vue 3, TypeScript, Tailwind CSS, Pinia, Zod
- **Backend:** FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, Pandas
- **Banco:** Supabase Postgres + Auth + Storage + RLS
- **Infra:** VPS, Docker, Docker Compose, Nginx

## Estrutura de branches

```
main       ← produção (protegida, sem push direto)
develop    ← integração
feature/*  ← desenvolvimento de funcionalidades
```

## Documentação

Consultar a pasta `docs/` para PRD, arquitetura, padrões e FDDs.
