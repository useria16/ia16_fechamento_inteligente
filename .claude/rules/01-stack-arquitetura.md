# Stack e arquitetura

## Stack oficial

Frontend:

- Nuxt 4
- Vue
- TypeScript
- Tailwind CSS
- Pinia
- Zod

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

- VPS
- Docker
- Docker Compose
- Nginx

## Regra arquitetural

Separar:

- frontend
- backend
- banco
- storage
- motor de conciliação
- regras de conciliação
- exportação

O motor de conciliação não deve conhecer nome de cliente.

Ele deve receber:

- empresa
- fechamento
- tipo de conciliação
- configuração de conciliação
- fontes de dados
- modelos de arquivo
- regras configuradas
- tolerâncias de valor e data
