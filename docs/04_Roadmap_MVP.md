# Roadmap de implementação do MVP

## Sprint 1, Base do projeto

Objetivo: criar estrutura inicial do monorepo, frontend, backend e conexão com Supabase.

Entregas:

- projeto Nuxt 4
- projeto FastAPI
- Docker Compose
- Nginx básico
- variáveis de ambiente
- conexão Supabase
- setup SQLAlchemy
- setup Alembic
- estrutura inicial de migrations

## Sprint 2, Autenticação, empresas e usuários

Objetivo: permitir acesso seguro e controle por empresa.

Entregas:

- login
- sessão com Supabase Auth
- tabela `empresas`
- tabela `usuarios`
- vínculo com `auth.users`
- perfil admin iA16
- perfil cliente
- tela de empresas
- tela de usuários
- políticas RLS iniciais

## Sprint 3, Fontes de dados e modelos de arquivo

Objetivo: preparar a base para upload e normalização.

Entregas:

- tabela `fontes_dados`
- tabela `modelos_arquivo`
- cadastro de fonte Excel manual
- cadastro de modelo de arquivo
- definição de colunas esperadas por tipo de arquivo
- tela simples de fontes
- tela simples de modelos

## Sprint 4, Upload de arquivos

Objetivo: permitir envio e armazenamento de planilhas.

Entregas:

- bucket no Supabase Storage
- tabela `arquivos_enviados`
- upload Excel
- validação de extensão
- validação de tamanho
- gravação de metadados
- listagem de arquivos
- associação opcional com fechamento

## Sprint 5, Fechamentos financeiros

Objetivo: permitir criação e controle dos fechamentos.

Entregas:

- tabela `fechamentos_financeiros`
- criar fechamento
- editar fechamento em rascunho
- associar arquivos
- alterar status
- listagem
- tela de detalhe

## Sprint 6, Motor de conciliação

Objetivo: processar arquivos e gerar resultados.

Entregas:

- leitura com Pandas/OpenPyXL
- normalização dos dados
- regras iniciais de conciliação
- gravação de transações
- gravação de itens conciliados
- gravação de divergências
- logs de processamento
- botão processar

## Sprint 7, Divergências e observações

Objetivo: permitir revisão operacional.

Entregas:

- listagem de divergências
- filtros
- detalhe da divergência
- campo de observação
- alterar status da divergência
- marcar como resolvido
- contadores por tipo de divergência

## Sprint 8, Relatórios, exportação e dashboard

Objetivo: entregar valor final ao cliente.

Entregas:

- resumo do fechamento
- exportação Excel
- relatório de divergências
- dashboard simples
- histórico de fechamentos
- indicadores principais
## Sprint 3.1, Tipos e configurações de conciliação

Objetivo: preparar a aplicação para atender múltiplos tipos de conciliação e múltiplos clientes.

Entregas:

- tabela `tipos_conciliacao`
- tabela `configuracoes_conciliacao`
- tabela `regras_conciliacao`
- vínculo de fechamento com tipo e configuração
- seed inicial de tipos de conciliação
- tela administrativa simples para configuração
- atualização do motor para ler regras configuradas
