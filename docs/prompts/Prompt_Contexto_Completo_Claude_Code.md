# Contexto completo para Claude Code

Você está desenvolvendo o MVP do iA16 Fechamento Inteligente.

## Produto

Aplicação para fechamento financeiro assistido. O cliente envia planilhas Excel, o sistema processa, identifica divergências, gera resumo e exporta resultado.

## Não é ERP

Não implementar contas a pagar completo, contas a receber completo, fiscal, boletos, banco automático ou integração com ERP no MVP.

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

## Banco de dados

Todos os objetos customizados devem estar em português.

Tabelas principais:

- `empresas`
- `usuarios`
- `fontes_dados`
- `modelos_arquivo`
- `arquivos_enviados`
- `fechamentos_financeiros`
- `transacoes_financeiras`
- `itens_conciliacao`
- `divergencias_conciliacao`
- `relatorios_fechamento`
- `logs_processamento`

## Módulos do MVP

1. Autenticação, empresas e usuários
2. Fontes de dados
3. Modelos de arquivo
4. Upload de arquivos
5. Fechamentos financeiros
6. Motor de conciliação
7. Divergências e observações
8. Relatórios e exportação
9. Dashboard
10. Logs de processamento
11. Resumo executivo com IA opcional

## Regra de implementação

Antes de escrever código, listar arquivos que serão criados ou modificados.

Depois de escrever código, informar como testar.
