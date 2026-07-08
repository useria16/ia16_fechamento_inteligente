---
name: ia16-criar-migration
description: Cria migration Alembic seguindo o padrão de banco em português
---

# Criar migration

Crie ou ajuste migrations usando Alembic.

## Regras obrigatórias

- Todos os objetos customizados devem estar em português.
- Usar `snake_case`.
- Não criar tabelas com nome de cliente.
- Não criar colunas em inglês.
- Não criar enums em inglês.
- Não criar índices ou constraints em inglês.
- Não alterar objetos internos do Supabase.
- Usar SQLAlchemy 2.x.

## Antes de criar

Liste:

- tabelas novas
- colunas novas
- relacionamentos
- índices
- constraints
- impacto nas tabelas existentes

## Depois de criar

Informe:

- comando para executar a migration
- comando para reverter
- como validar no banco
