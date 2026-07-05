---
name: ia16-supabase
description: Configura, diagnostica e valida o Supabase no projeto iA16 Fechamento Inteligente usando npx supabase, migrations, schemas e regras de segurança
---

# ia16-supabase

Você é responsável por ajudar na configuração, diagnóstico e validação do Supabase no projeto iA16 Fechamento Inteligente.

## Objetivo

Garantir que o Supabase esteja configurado de forma segura, reproduzível e alinhada com a arquitetura do projeto.

O projeto usa:

- Supabase Postgres
- Supabase Auth
- Supabase Storage
- Supabase RLS
- Supabase CLI via `npx supabase`
- migrations versionadas
- banco com objetos customizados em português

## Regra principal

Sempre começar com diagnóstico.

Nunca assumir que o Supabase já está configurado.

Nunca alterar produção sem confirmação explícita do usuário.

Nunca salvar credenciais no repositório.

## Perguntas iniciais obrigatórias

Antes de executar qualquer configuração, pergunte:

```text
Qual ambiente você quer configurar?

1. Local
2. Desenvolvimento remoto
3. Produção
```

Depois pergunte:

```text
Qual schema será usado para os objetos da aplicação?

1. public
2. outro schema
```

Se o usuário escolher outro schema, peça o nome.

Exemplo:

```text
ia16
```

## Diagnóstico inicial obrigatório

Executar ou orientar a execução dos comandos:

```bash
node -v
npm -v
npx supabase --version
ls -la
ls -la supabase
ls -la supabase/migrations
git status
```

Se `node -v` mostrar versão menor que 20, avisar que o projeto deve usar Node.js 20 ou superior para trabalhar com Supabase CLI via npm/npx.

Se `npx supabase --version` falhar, orientar instalar o Supabase CLI como dependência de desenvolvimento:

```bash
npm install supabase --save-dev
```

Não usar:

```bash
npm install -g supabase
```

## Verificar se já existe configuração Supabase

Verificar se existe:

```text
supabase/
supabase/config.toml
supabase/migrations/
```

Se não existir pasta `supabase/`, orientar:

```bash
npx supabase init
```

Se existir, analisar a estrutura e informar:

* se `config.toml` existe
* se `migrations/` existe
* se existem migrations
* se o projeto parece estar linkado a um projeto remoto
* se há indícios de configuração local

## Ambientes

### Ambiente local

Usar para desenvolvimento e testes sem afetar ambiente remoto.

Comandos principais:

```bash
npx supabase start
npx supabase stop
npx supabase status
```

Usar ambiente local sempre que possível para testar migrations.

### Desenvolvimento remoto

Usar para validar integração com um projeto Supabase remoto de desenvolvimento.

Antes de usar, validar se o projeto está linkado:

```bash
npx supabase link --project-ref <project_ref>
```

Nunca solicitar token para ser colado em arquivo versionado.

### Produção

Produção exige confirmação explícita do usuário antes de qualquer ação.

Antes de qualquer comando que altere produção, exibir:

```text
Atenção: esta ação pode alterar o banco de produção. Confirma que deseja continuar?
```

Sem confirmação explícita, não executar.

## Validação do schema

Depois que o usuário informar o schema, validar se ele existe.

Para validar schema, usar uma query como referência:

```sql
select schema_name
from information_schema.schemata
where schema_name = '<schema_informado>';
```

Se o schema não existir, perguntar:

```text
O schema `<schema_informado>` não existe. Deseja criar esse schema via migration?
```

Se autorizado, criar migration.

Exemplo de criação de schema:

```sql
create schema if not exists ia16;
```

## Padrão de migrations

Toda alteração estrutural deve ser feita com migration.

Criar migration com:

```bash
npx supabase migration new nome_da_migration
```

Regras para nomes de migrations:

* usar português
* usar snake_case
* descrever a alteração
* evitar nome genérico

Exemplos corretos:

```text
cria_schema_ia16
cria_tabelas_empresas_usuarios
cria_tipos_configuracoes_regras_conciliacao
cria_tabelas_fechamentos_financeiros
cria_politicas_rls_iniciais
```

Exemplos proibidos:

```text
create_users
create_companies
financial_closings
daxx_tables
```

## Banco de dados em português

Todos os objetos customizados do banco devem estar em português.

Inclui:

* schemas
* tabelas
* colunas
* enums
* constraints
* índices
* views
* funções
* triggers
* migrations

Exceção:

* objetos internos do Supabase, como `auth.users`, não devem ser renomeados.

## Objetos esperados no projeto

Tabelas principais do MVP:

```text
empresas
usuarios
fontes_dados
tipos_conciliacao
configuracoes_conciliacao
regras_conciliacao
modelos_arquivo
arquivos_enviados
fechamentos_financeiros
transacoes_financeiras
itens_conciliacao
divergencias_conciliacao
relatorios_fechamento
logs_processamento
```

## Tabelas estruturais para multiconciliação

O projeto deve suportar múltiplos clientes e múltiplos tipos de conciliação.

Tabelas obrigatórias:

```text
tipos_conciliacao
configuracoes_conciliacao
regras_conciliacao
```

Não criar tabelas com nome de cliente.

Proibido:

```text
conciliacao_daxx
regras_daxx
arquivos_daxx
```

Correto:

```text
configuracoes_conciliacao
regras_conciliacao
modelos_arquivo
```

## RLS

Toda tabela sensível deve considerar RLS.

Tabelas sensíveis:

```text
empresas
usuarios
fontes_dados
modelos_arquivo
arquivos_enviados
fechamentos_financeiros
transacoes_financeiras
itens_conciliacao
divergencias_conciliacao
relatorios_fechamento
logs_processamento
configuracoes_conciliacao
regras_conciliacao
```

Regras:

* usuário cliente só acessa dados da própria empresa
* admin iA16 pode acessar múltiplas empresas
* nenhuma tabela sensível deve ficar sem política de acesso
* políticas devem ser criadas via migration
* políticas devem ter nomes em português

## Storage

Validar buckets necessários para o MVP:

```text
arquivos-originais
arquivos-processados
relatorios
```

Antes de criar buckets, perguntar se esses nomes serão mantidos.

Arquivos esperados:

* planilhas Excel originais
* planilhas processadas
* relatórios exportados

Regras:

* não armazenar arquivos fora dos buckets definidos
* caminhos devem incluir empresa e fechamento
* exemplo de path:

```text
empresa_id/fechamento_id/originais/nome_arquivo.xlsx
empresa_id/fechamento_id/processados/resultado.xlsx
empresa_id/fechamento_id/relatorios/relatorio.xlsx
```

## MCP Supabase

MCP pode ser usado para:

* diagnóstico
* consulta de schema
* consulta de tabelas
* consulta de migrations
* documentação
* validação de estrutura

MCP não deve ser usado para:

* alterar produção sem confirmação
* aplicar migration em produção sem aprovação
* executar SQL destrutivo
* acessar dados sensíveis sem necessidade

Se usar MCP, preferir:

* escopo por `project_ref`
* modo `read_only=true` quando consultar dados reais
* ambiente de desenvolvimento remoto
* nunca usar service_role key no projeto

## Geração de tipos TypeScript

Quando o schema estiver definido e o projeto estiver linkado, orientar gerar tipos para o frontend:

```bash
npx supabase gen types typescript --project-id <project_ref> --schema <schema> > frontend/types/supabase.ts
```

Se houver múltiplos schemas, confirmar qual schema será usado.

## Comandos seguros

Comandos permitidos normalmente:

```bash
npx supabase --version
npx supabase init
npx supabase start
npx supabase stop
npx supabase status
npx supabase migration list
npx supabase migration new nome_da_migration
npx supabase gen types typescript
```

Comandos que exigem confirmação:

```bash
npx supabase link --project-ref <project_ref>
npx supabase db push
npx supabase db reset
npx supabase db diff
```

Comandos em produção exigem confirmação explícita adicional.

## Comandos proibidos sem autorização explícita

Não executar sem autorização clara:

```bash
npx supabase db reset
npx supabase db push
drop schema
drop table
truncate table
delete from
alter table ... drop column
```

## Arquivos sensíveis

Nunca versionar:

```text
.env
.env.*
backend/.env
frontend/.env
tokens
chaves
senhas
service_role keys
database password
JWT secret
project access token
arquivos em secrets/
credentials.json
```

Se encontrar algum desses arquivos no `git status`, alertar imediatamente.

## Checklist de validação

Ao final da configuração, validar:

```bash
node -v
npx supabase --version
ls -la supabase
ls -la supabase/migrations
git status
```

Informar:

1. ambiente configurado
2. schema escolhido
3. se o schema já existia ou será criado
4. status da pasta `supabase/`
5. status das migrations
6. buckets necessários
7. riscos de segurança encontrados
8. próximo comando recomendado

## Saída obrigatória

Sempre responder com:

1. Diagnóstico encontrado.
2. Ambiente escolhido.
3. Schema escolhido.
4. Se o schema existe ou precisa ser criado.
5. Estrutura Supabase encontrada no projeto.
6. Migrations existentes ou pendentes.
7. Situação de RLS.
8. Situação de Storage.
9. Alertas de segurança.
10. Próximo passo recomendado.
