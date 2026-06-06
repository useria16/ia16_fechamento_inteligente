# iA16 Fechamento Inteligente

## Objetivo do projeto

Desenvolver o MVP do iA16 Fechamento Inteligente, uma aplicação multicliente para conciliação financeira configurável.

O produto deve atender inicialmente:

- Daxx Omnimedia, com conciliação bancária
- Segundo cliente, com conciliação de caixa, recebíveis e controles financeiros

A aplicação não deve ser construída como uma solução exclusiva para a Daxx. A Daxx é apenas o primeiro cliente piloto.

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

## Regras obrigatórias

- Não criar aplicação específica para a Daxx.
- Não criar tabelas, colunas, regras, services, rotas ou componentes com nome de cliente.
- A aplicação deve ser multicliente e multiconciliação.
- Todo objeto customizado do banco deve estar em português.
- Usar SQLAlchemy 2.x.
- Não usar SQLModel.
- Não implementar Open Finance no MVP.
- Não implementar ERP no MVP.
- Não transformar a aplicação em ERP financeiro.
- Não criar cadastro público de usuários.
- Acesso de usuários deve ser criado ou controlado pela iA16.
- O motor de conciliação deve ser baseado em regras determinísticas.
- IA pode apoiar resumo executivo, explicações e observações, mas não pode alterar dados financeiros.
- Antes de alterar arquivos, liste arquivos que serão criados ou modificados.
- Depois de alterar arquivos, explique como testar.
- Não versionar `.env`, chaves, tokens, senhas ou dados sensíveis.

## Conceito central

Fechamento financeiro:

- pertence a uma empresa
- possui tipo de conciliação
- usa configuração de conciliação
- recebe arquivos
- normaliza dados
- aplica regras
- gera transações
- gera divergências
- gera relatórios

## Tipos de conciliação iniciais

- bancaria
- caixa
- recebiveis
- caixa_recebiveis
- vendas_recebimentos
- adquirentes
- outro

## Documentos de referência

Antes de implementar qualquer funcionalidade, consultar os documentos na pasta `docs/`, especialmente:

- `docs/01_PRD_Produto.md`
- `docs/02_Arquitetura_Tecnica.md`
- `docs/03_Padrao_Banco_Dados.md`
- `docs/05_Funcionalidades_Negocio.md`
- `docs/07_Estrategia_Multicliente_Multiconciliacao.md`
- `docs/fdd/12_FDD_Tipos_Configuracoes_Regras_Conciliacao.md`

## Forma de trabalho

Para cada implementação:

1. Ler o documento FDD relacionado.
2. Listar arquivos que serão criados ou alterados.
3. Confirmar se a mudança respeita a arquitetura multicliente.
4. Confirmar se os objetos de banco estão em português.
5. Implementar backend, frontend, migrations e testes quando aplicável.
6. Explicar como testar.
7. Informar pontos pendentes.
