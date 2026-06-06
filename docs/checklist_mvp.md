# Checklist MVP — iA16 Fechamento Inteligente

## Sprint 1 — Base do projeto

- [x] Projeto Nuxt 4 criado
- [x] Projeto FastAPI criado
- [x] Docker Compose configurado
- [x] Nginx básico configurado
- [x] Variáveis de ambiente definidas (.env.example)
- [x] Conexão com Supabase configurada
- [x] SQLAlchemy 2.x configurado
- [x] Alembic configurado com schema dinâmico (ia16_fechamento_dev / ia16_fechamento_prod)
- [x] Estrutura inicial de migrations criada
- [x] Schemas Supabase criados (ia16_fechamento_dev, ia16_fechamento_prod)
- [x] Makefile com comandos de setup, migrations e deploy

## Sprint 2 — Autenticação, empresas e usuários

- [ ] Login via Supabase Auth
- [ ] Sessão JWT validada no backend
- [ ] Migration `empresas`
- [ ] Migration `usuarios`
- [ ] Model SQLAlchemy `Empresa`
- [ ] Model SQLAlchemy `Usuario`
- [ ] Schema Pydantic empresa
- [ ] Schema Pydantic usuario
- [ ] Endpoint `GET /api/empresas`
- [ ] Endpoint `POST /api/empresas`
- [ ] Endpoint `GET /api/usuarios`
- [ ] Endpoint `POST /api/usuarios`
- [ ] Endpoint `PATCH /api/usuarios/{id}`
- [ ] Perfil `admin_ia16` funcional
- [ ] Perfil `cliente_admin` funcional
- [ ] Perfil `cliente_operador` funcional
- [ ] Tela `/login`
- [ ] Tela `/admin/empresas`
- [ ] Tela `/admin/empresas/nova`
- [ ] Tela `/admin/empresas/[id]`
- [ ] Tela `/admin/usuarios`
- [ ] Tela `/admin/usuarios/novo`
- [ ] Store Pinia para sessão
- [ ] Políticas RLS iniciais (empresas, usuarios)

## Sprint 3 — Fontes de dados e modelos de arquivo

- [ ] Migration `fontes_dados`
- [ ] Migration `modelos_arquivo`
- [ ] Model SQLAlchemy `FonteDados`
- [ ] Model SQLAlchemy `ModeloArquivo`
- [ ] Endpoint `GET /api/fontes-dados`
- [ ] Endpoint `POST /api/fontes-dados`
- [ ] Endpoint `GET /api/modelos-arquivo`
- [ ] Endpoint `POST /api/modelos-arquivo`
- [ ] Tela de fontes de dados
- [ ] Tela de modelos de arquivo
- [ ] Definição de colunas esperadas por tipo de arquivo

## Sprint 3.1 — Tipos, configurações e regras de conciliação

- [ ] Migration `tipos_conciliacao`
- [ ] Migration `configuracoes_conciliacao`
- [ ] Migration `regras_conciliacao`
- [ ] Atualização de `fechamentos_financeiros` com `tipo_conciliacao_id` e `configuracao_conciliacao_id`
- [ ] Model SQLAlchemy `TipoConciliacao`
- [ ] Model SQLAlchemy `ConfiguracaoConciliacao`
- [ ] Model SQLAlchemy `RegraConciliacao`
- [ ] Schema Pydantic para cada model
- [ ] Endpoint `GET /api/tipos-conciliacao`
- [ ] Endpoint `POST /api/tipos-conciliacao`
- [ ] Endpoint `GET /api/configuracoes-conciliacao`
- [ ] Endpoint `POST /api/configuracoes-conciliacao`
- [ ] Endpoint `PATCH /api/configuracoes-conciliacao/{id}`
- [ ] Endpoint `POST /api/configuracoes-conciliacao/{id}/regras`
- [ ] Seed inicial com tipos de conciliação
- [ ] Tela `/tipos-conciliacao`
- [ ] Tela `/configuracoes-conciliacao`
- [ ] Tela `/configuracoes-conciliacao/nova`
- [ ] Tela `/configuracoes-conciliacao/[id]`

## Sprint 4 — Upload de arquivos

- [ ] Buckets Supabase Storage criados (arquivos-originais, arquivos-processados, relatorios)
- [ ] Migration `arquivos_enviados`
- [ ] Model SQLAlchemy `ArquivoEnviado`
- [ ] Endpoint upload de arquivo
- [ ] Validação de extensão (.xlsx, .xls)
- [ ] Validação de tamanho
- [ ] Gravação de metadados no banco
- [ ] Tela de upload
- [ ] Listagem de arquivos enviados
- [ ] Associação de arquivo com fechamento

## Sprint 5 — Fechamentos financeiros

- [ ] Migration `fechamentos_financeiros`
- [ ] Model SQLAlchemy `FechamentoFinanceiro`
- [ ] Endpoint `GET /api/fechamentos`
- [ ] Endpoint `POST /api/fechamentos`
- [ ] Endpoint `GET /api/fechamentos/{id}`
- [ ] Endpoint `PATCH /api/fechamentos/{id}`
- [ ] Tela `/fechamentos`
- [ ] Tela `/fechamentos/novo`
- [ ] Tela `/fechamentos/[id]`
- [ ] Alterar status do fechamento
- [ ] Associar arquivos ao fechamento
- [ ] Listagem com histórico

## Sprint 6 — Motor de conciliação

- [ ] Migration `transacoes_financeiras`
- [ ] Migration `itens_conciliacao`
- [ ] Serviço `motor_conciliacao`
- [ ] Leitor de Excel (Pandas/OpenPyXL)
- [ ] Normalizador de colunas por modelo de arquivo
- [ ] Regra 1: documento igual e valor igual
- [ ] Regra 2: data próxima e valor igual
- [ ] Regra 3: descrição similar e valor igual
- [ ] Regra 4: valor dentro de tolerância configurada
- [ ] Regra 5: registro sem par correspondente
- [ ] Gravação de transações normalizadas
- [ ] Gravação de itens conciliados
- [ ] Gravação de divergências
- [ ] Atualização do status do fechamento
- [ ] Logs de processamento
- [ ] Endpoint `POST /api/fechamentos/{id}/processar`
- [ ] Botão processar no frontend
- [ ] Suporte a reprocessamento (sem apagar original)
- [ ] Testes unitários das regras

## Sprint 7 — Divergências e observações

- [ ] Migration `divergencias_conciliacao`
- [ ] Listagem de divergências
- [ ] Filtros (status, tipo, severidade, valor, data)
- [ ] Tela de detalhe da divergência
- [ ] Campo de observação na divergência
- [ ] Alterar status da divergência (aberta, resolvida, ignorada, em_analise)
- [ ] Contadores por tipo de divergência
- [ ] RLS em divergencias_conciliacao

## Sprint 8 — Relatórios, exportação e dashboard

- [ ] Resumo do fechamento (total processado, conciliado, divergente, percentual)
- [ ] Exportação Excel da planilha conciliada
- [ ] Exportação Excel do relatório de divergências
- [ ] Geração de relatório em Supabase Storage
- [ ] Migration `relatorios_fechamento`
- [ ] Tela de dashboard (`/dashboard`)
- [ ] Indicadores: total processado, conciliado, divergente, percentual, divergências abertas, últimos fechamentos
- [ ] Histórico de fechamentos
- [ ] Resumo executivo com IA (opcional — apenas texto explicativo)
