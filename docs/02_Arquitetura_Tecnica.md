# Arquitetura técnica do MVP

## 1. Visão geral

A arquitetura será composta por frontend Nuxt 4, backend FastAPI, banco e serviços Supabase, armazenamento Supabase Storage e execução em VPS com Docker.

## 2. Componentes

```text
Usuário
  |
  v
Nginx na VPS
  |
  |-- Frontend Nuxt 4
  |
  |-- Backend FastAPI
          |
          |-- Supabase Postgres
          |-- Supabase Storage
          |-- Supabase Auth
          |-- Pandas/OpenPyXL
```

## 3. Frontend

Stack:

- Nuxt 4
- Vue
- TypeScript
- Tailwind CSS
- Pinia
- Zod
- Supabase JS

Responsabilidades:

- login
- navegação
- dashboard
- upload de arquivos
- criação de fechamentos
- visualização de status
- visualização de divergências
- exportação
- consumo da API FastAPI

## 4. Backend

Stack:

- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- Pandas
- OpenPyXL

Responsabilidades:

- validar requisições
- receber metadados dos arquivos
- processar planilhas
- normalizar dados
- executar conciliação
- gravar resultados no Supabase Postgres
- gerar arquivos exportáveis
- gravar logs de processamento
- gerar resumo simples do fechamento

## 5. Supabase

Responsabilidades:

- autenticação
- banco Postgres
- storage de arquivos
- políticas RLS
- relacionamento entre usuários e empresas

## 6. VPS

Serviços em Docker Compose:

- `nginx`
- `frontend`
- `backend`

O banco não roda na VPS, pois o Supabase permanece como serviço gerenciado.

## 7. Comunicação

### Frontend para Backend

O Nuxt consome a API FastAPI para:

- listar empresas
- listar fechamentos
- enviar metadados de upload
- iniciar processamento
- consultar divergências
- baixar relatórios

### Backend para Supabase

O FastAPI acessa o Supabase Postgres via SQLAlchemy e usa Supabase Storage para arquivos.

## 8. Storage

Estrutura sugerida de buckets:

```text
arquivos-originais
arquivos-processados
relatorios
```

Estrutura sugerida de path:

```text
empresa_id/fechamento_id/originais/nome_arquivo.xlsx
empresa_id/fechamento_id/processados/resultado.xlsx
empresa_id/fechamento_id/relatorios/relatorio.xlsx
```

## 9. Segurança

- autenticação via Supabase Auth
- JWT enviado pelo frontend
- backend valida token antes de executar ações
- RLS por empresa
- arquivos vinculados a empresa e fechamento
- usuário não pode acessar dados de outra empresa

## 10. Banco

Todos os objetos customizados devem usar português.

Exemplo:

- `empresas`
- `usuarios`
- `fontes_dados`
- `arquivos_enviados`
- `fechamentos_financeiros`
- `transacoes_financeiras`
- `divergencias_conciliacao`
- `logs_processamento`

## 11. Reprocessamento

Cada fechamento pode ser reprocessado.

Regras:

- manter histórico de logs
- marcar processamento anterior como substituído ou registrar nova tentativa
- não apagar arquivo original
- atualizar status do fechamento
- regenerar saídas

## 12. Observabilidade mínima

Registrar logs em tabela:

- início do processamento
- validação de arquivo
- erro de leitura
- erro de coluna obrigatória
- quantidade de registros lidos
- quantidade conciliada
- quantidade divergente
- conclusão do processamento
## 12. Núcleo configurável de conciliação

A arquitetura deve separar o núcleo comum de conciliação das regras específicas de cada cliente.

```text
Arquivos enviados
  |
  v
Modelos de arquivo
  |
  v
Normalização
  |
  v
Tipo de conciliação
  |
  v
Configuração de conciliação
  |
  v
Regras de conciliação
  |
  v
Motor de conciliação
  |
  v
Divergências e relatórios
```

O motor de conciliação não deve conhecer diretamente o nome do cliente.

Ele deve receber:

- empresa
- fechamento
- tipo de conciliação
- fontes de dados
- modelos de arquivo
- regras configuradas
- tolerâncias de valor e data

A partir disso, deve executar o processamento.

## 13. Novas tabelas estruturais para múltiplos clientes

Para suportar mais de um cliente e mais de um cenário financeiro, incluir:

```text
tipos_conciliacao
configuracoes_conciliacao
regras_conciliacao
```

Essas tabelas permitem que a Daxx use conciliação bancária e outro cliente use conciliação de caixa e recebíveis sem criar fluxos separados no código.
