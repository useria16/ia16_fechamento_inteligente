# Padrão de banco de dados

## 1. Diretriz principal

Todos os objetos customizados do banco devem ser criados em português.

Isso inclui:

- tabelas
- colunas
- enums
- constraints
- índices
- views
- funções
- triggers
- migrations
- comentários

## 2. Exceção

Objetos gerenciados pelo Supabase, como `auth.users`, não devem ser alterados.

As tabelas próprias da aplicação devem referenciar o usuário do Supabase por meio de colunas em português, por exemplo:

```sql
usuario_auth_id uuid not null references auth.users(id)
```

## 3. Convenção de nomes

- usar `snake_case`
- tabelas no plural
- colunas em português
- evitar abreviações ambíguas
- usar nomes descritivos

## 4. Tabelas principais

```text
empresas
usuarios
fontes_dados
modelos_arquivo
arquivos_enviados
fechamentos_financeiros
transacoes_financeiras
recebiveis
itens_conciliacao
divergencias_conciliacao
relatorios_fechamento
logs_processamento
```

## 5. Enums sugeridos

```text
status_fechamento
tipo_fonte_dados
tipo_arquivo
status_arquivo
status_conciliacao
tipo_divergencia
nivel_severidade
perfil_usuario
```

## 6. Status de fechamento

Valores sugeridos:

```text
rascunho
arquivos_enviados
em_processamento
processado
com_divergencias
aprovado
erro
cancelado
```

## 7. Tipos de fonte de dados

```text
excel_manual
banco
adquirente
erp
google_drive
outro
```

## 8. Tipos de arquivo

```text
extrato_bancario
relatorio_vendas
relatorio_recebiveis
planilha_interna
taxas_adquirente
outro
```

## 9. Tipos de divergência

```text
valor_diferente
data_diferente
registro_nao_encontrado
registro_duplicado
taxa_divergente
recebimento_pendente
categoria_inconsistente
outro
```

## 10. Exemplo de migration

```sql
create table empresas (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    cnpj text,
    status text not null default 'ativa',
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

create table usuarios (
    id uuid primary key default gen_random_uuid(),
    empresa_id uuid not null references empresas(id),
    usuario_auth_id uuid not null references auth.users(id),
    nome text not null,
    email text not null,
    perfil text not null default 'cliente',
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);
```

## 11. SQLAlchemy

Mesmo usando SQLAlchemy, os nomes reais do banco devem ficar em português.

Exemplo:

```python
class FechamentoFinanceiro(Base):
    __tablename__ = "fechamentos_financeiros"

    id = Column(UUID(as_uuid=True), primary_key=True)
    empresa_id = Column(UUID(as_uuid=True), nullable=False)
    data_referencia = Column(Date, nullable=False)
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
```

## 12. Índices sugeridos

```sql
create index idx_usuarios_empresa_id on usuarios(empresa_id);
create index idx_arquivos_enviados_fechamento_id on arquivos_enviados(fechamento_id);
create index idx_fechamentos_financeiros_empresa_id on fechamentos_financeiros(empresa_id);
create index idx_fechamentos_financeiros_periodo on fechamentos_financeiros(periodo_inicio, periodo_fim);
create index idx_transacoes_financeiras_empresa_data on transacoes_financeiras(empresa_id, data_transacao);
create index idx_divergencias_conciliacao_fechamento_id on divergencias_conciliacao(fechamento_id);
```

## 13. RLS

Cada tabela sensível deve ter política por empresa.

Regra conceitual:

- usuário só acessa registros da empresa à qual está vinculado
- admin iA16 pode acessar todas as empresas
- usuário cliente não pode editar dados de outra empresa
## 14. Tabelas para conciliação configurável

### tipos_conciliacao

Objetivo: definir os tipos de conciliação suportados pela aplicação.

Exemplos de códigos:

```text
bancaria
caixa
recebiveis
caixa_recebiveis
vendas_recebimentos
adquirentes
outro
```

Colunas sugeridas:

```sql
create table tipos_conciliacao (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    codigo text not null unique,
    descricao text,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);
```

### configuracoes_conciliacao

Objetivo: definir como uma empresa executa um tipo de conciliação.

```sql
create table configuracoes_conciliacao (
    id uuid primary key default gen_random_uuid(),
    empresa_id uuid not null references empresas(id),
    tipo_conciliacao_id uuid not null references tipos_conciliacao(id),
    nome text not null,
    fonte_verdade_id uuid references fontes_dados(id),
    tolerancia_valor numeric(14,2) not null default 0,
    tolerancia_dias integer not null default 0,
    parametros jsonb not null default '{}'::jsonb,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);
```

### regras_conciliacao

Objetivo: armazenar regras aplicadas no motor de conciliação.

```sql
create table regras_conciliacao (
    id uuid primary key default gen_random_uuid(),
    configuracao_conciliacao_id uuid not null references configuracoes_conciliacao(id),
    nome text not null,
    ordem integer not null,
    campo_origem text not null,
    campo_destino text not null,
    operador text not null,
    peso numeric(5,2),
    obrigatoria boolean not null default false,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);
```

## 15. Ajuste na tabela fechamentos_financeiros

A tabela `fechamentos_financeiros` deve possuir referência para o tipo e configuração de conciliação.

Colunas adicionais sugeridas:

```sql
tipo_conciliacao_id uuid references tipos_conciliacao(id),
configuracao_conciliacao_id uuid references configuracoes_conciliacao(id)
```

## 16. Regra de nomenclatura para clientes

Não criar tabelas, colunas ou regras com nome de cliente.

Evitar:

```text
conciliacao_daxx
arquivos_daxx
regras_daxx
```

Usar:

```text
configuracoes_conciliacao
regras_conciliacao
modelos_arquivo
```
