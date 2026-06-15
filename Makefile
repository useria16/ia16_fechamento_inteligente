.PHONY: help setup-backend migrate-dev migrate-prod promote diff-schemas \
        dev-backend dev-frontend docker-up docker-down limpar-arquivos-expirados

help:
	@echo "Comandos disponíveis:"
	@echo "  setup-backend   Cria .venv e instala dependências do backend"
	@echo "  migrate-dev     Aplica migrations no schema dev"
	@echo "  migrate-prod    Aplica migrations no schema prod"
	@echo "  promote         Promove migrations do dev para prod"
	@echo "  diff-schemas    Compara revisão atual entre dev e prod"
	@echo "  dev-backend     Inicia backend em modo desenvolvimento"
	@echo "  dev-frontend    Inicia frontend em modo desenvolvimento"
	@echo "  docker-up       Sobe todos os serviços com Docker Compose"
	@echo "  docker-down     Derruba os serviços"

# ── Ambiente Python ──────────────────────────────────────────────────────────

setup-backend:
	cd backend && python -m venv .venv
	cd backend && .venv/bin/pip install --upgrade pip
	cd backend && .venv/bin/pip install -r requirements.txt
	@echo "✔ Ambiente virtual criado. Ative com: source backend/.venv/bin/activate"

# ── Migrations ───────────────────────────────────────────────────────────────

migrate-dev:
	cd backend && DB_SCHEMA=ia16_fechamento_dev .venv/bin/alembic upgrade head

migrate-prod:
	cd backend && DB_SCHEMA=ia16_fechamento_prod .venv/bin/alembic upgrade head

promote:
	@echo "Promovendo dev → prod..."
	cd backend && DB_SCHEMA=ia16_fechamento_prod .venv/bin/alembic upgrade head
	@echo "✔ Schemas sincronizados"

diff-schemas:
	@echo "=== Dev ==="
	cd backend && DB_SCHEMA=ia16_fechamento_dev .venv/bin/alembic current
	@echo "=== Prod ==="
	cd backend && DB_SCHEMA=ia16_fechamento_prod .venv/bin/alembic current

# ── Desenvolvimento local ─────────────────────────────────────────────────────

dev-backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

# ── Docker ───────────────────────────────────────────────────────────────────

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

# ── Retenção de arquivos ─────────────────────────────────────────────────────

limpar-arquivos-expirados:
	cd backend && DB_SCHEMA=ia16_fechamento_dev .venv/bin/python -m scripts.limpar_arquivos_expirados
