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

## Ambientes

O projeto usa dois schemas no mesmo banco Supabase:

| Ambiente | Schema | Storage prefix |
|---|---|---|
| Dev | `ia16_fechamento_dev` | `dev/` |
| Prod | `ia16_fechamento_prod` | `prod/` |

### Arquivos de variáveis de ambiente

```
backend/.env.example   ← template versionado
backend/.env           ← desenvolvimento local (não versionado)
backend/.env.prod      ← produção na VPS (não versionado)

frontend/.env.example  ← template versionado
frontend/.env          ← desenvolvimento local (não versionado)
frontend/.env.prod     ← produção na VPS (não versionado)
```

Os arquivos `.env` e `.env.prod` nunca são versionados. Copie o `.env.example` para criar o seu:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

## Setup local

### 1. Backend

```bash
# Instalar dependências no ambiente virtual
make setup-backend

# Copiar e preencher variáveis de ambiente
cp backend/.env.example backend/.env

# Rodar em modo desenvolvimento
make dev-backend
# → http://localhost:8000/api/health
# → http://localhost:8000/api/docs
```

### 2. Frontend

```bash
cd frontend
npm install

# Copiar e preencher variáveis de ambiente
cp .env.example .env

# Rodar em modo desenvolvimento
npm run dev
# → http://localhost:3000
```

### 3. Ambiente completo com Docker (similar à produção)

```bash
# Copiar os .env antes de subir
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Subir todos os serviços (Nginx + frontend + backend)
make docker-up
# → http://localhost
```

## Migrations

O Alembic rastreia as migrations em cada schema de forma independente.

```bash
# Aplicar migrations no dev
make migrate-dev

# Aplicar migrations no prod
make migrate-prod

# Promover dev → prod (aplica o que está pendente no prod)
make promote

# Ver revisão atual em cada schema
make diff-schemas
```

### Fluxo de promoção

1. Crie e teste a migration em dev: `make migrate-dev`
2. Valide o comportamento
3. Promova para prod: `make promote`

## Deploy na VPS

```bash
# Copiar os arquivos de produção como .env
cp backend/.env.prod backend/.env
cp frontend/.env.prod frontend/.env

# Subir os serviços
make docker-up
```

## Documentação

Consultar a pasta `docs/` para PRD, arquitetura, padrões e FDDs.
