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

- [x] Login via Supabase Auth
- [x] Sessão JWT validada no backend
- [x] Migration `empresas`
- [x] Migration `usuarios`
- [x] Model SQLAlchemy `Empresa`
- [x] Model SQLAlchemy `Usuario`
- [x] Schema Pydantic empresa
- [x] Schema Pydantic usuario
- [x] Endpoint `GET /api/empresas`
- [x] Endpoint `POST /api/empresas`
- [x] Endpoint `GET /api/usuarios`
- [x] Endpoint `POST /api/usuarios`
- [x] Endpoint `PATCH /api/usuarios/{id}`
- [x] Perfil `admin_ia16` funcional
- [x] Perfil `cliente_admin` funcional
- [x] Perfil `cliente_operador` funcional
- [x] Tela `/login`
- [x] Tela `/admin/empresas`
- [x] Tela `/admin/empresas/nova`
- [x] Tela `/admin/empresas/[id]`
- [x] Tela `/admin/usuarios`
- [x] Tela `/admin/usuarios/novo`
- [x] Store Pinia para sessão
- [x] Políticas RLS iniciais (empresas, usuarios)

## Sprint 3 — Fontes de dados e modelos de arquivo ✅ CONCLUÍDA (backend)

- [x] Migration `fontes_dados` (003)
- [x] Migration `modelos_arquivo` (004)
- [x] Model SQLAlchemy `FonteDados`
- [x] Model SQLAlchemy `ModeloArquivo`
- [x] Endpoint `GET /api/v1/fontes-dados`
- [x] Endpoint `POST /api/v1/fontes-dados`
- [x] Endpoint `GET /api/v1/modelos-arquivo`
- [x] Endpoint `POST /api/v1/modelos-arquivo`
- [ ] Tela de fontes de dados (frontend pendente)
- [ ] Tela de modelos de arquivo (frontend pendente)
- [x] Definição de colunas esperadas por tipo de arquivo (normalizadores implementados)

## Sprint 3.1 — Tipos, configurações e regras de conciliação ⚠️ NÃO IMPLEMENTADA

> Decisão de implementação: o motor atual usa campo texto `tipo_conciliacao`
> em `fechamentos_financeiros` diretamente, sem FK para tabelas separadas.
> Essa sprint será necessária para habilitar configuração de regras por cliente.
> Não bloqueia o piloto Daxx.

- [ ] Migration `tipos_conciliacao`
- [ ] Migration `configuracoes_conciliacao`
- [ ] Migration `regras_conciliacao`
- [ ] Atualização de `fechamentos_financeiros` com `tipo_conciliacao_id` e `configuracao_conciliacao_id`
- [ ] Model SQLAlchemy `TipoConciliacao`
- [ ] Model SQLAlchemy `ConfiguracaoConciliacao`
- [ ] Model SQLAlchemy `RegraConciliacao`
- [ ] Schema Pydantic para cada model
- [ ] Endpoint `GET /api/v1/tipos-conciliacao`
- [ ] Endpoint `POST /api/v1/tipos-conciliacao`
- [ ] Endpoint `GET /api/v1/configuracoes-conciliacao`
- [ ] Endpoint `POST /api/v1/configuracoes-conciliacao`
- [ ] Endpoint `PATCH /api/v1/configuracoes-conciliacao/{id}`
- [ ] Endpoint `POST /api/v1/configuracoes-conciliacao/{id}/regras`
- [ ] Seed inicial com tipos de conciliação
- [ ] Tela `/tipos-conciliacao`
- [ ] Tela `/configuracoes-conciliacao`
- [ ] Tela `/configuracoes-conciliacao/nova`
- [ ] Tela `/configuracoes-conciliacao/[id]`

## Sprint 4 — Upload de arquivos ✅ CONCLUÍDA (2026-06-09)

- [x] Bucket Supabase Storage `arquivos-originais` criado e funcional
- [x] Migration `arquivos_enviados` (006)
- [x] Migration `politicas_retencao_arquivos` (009) — com política automática por empresa
- [x] Model SQLAlchemy `ArquivoEnviado`
- [x] Endpoint `POST /api/v1/conciliacoes/{id}/arquivos` — upload com multipart
- [x] Endpoint `GET /api/v1/conciliacoes/{id}/arquivos` — listagem com retenção
- [x] Endpoint `DELETE /api/v1/arquivos/{id}` — remoção de arquivo
- [x] Validação de extensão (.xlsx, .xls)
- [x] Validação de tamanho (10 MB)
- [x] Gravação de metadados no banco com campos de retenção
- [x] Tela de upload integrada em `/conciliacoes/[id]`
- [x] Listagem de arquivos com status e política de retenção
- [x] Associação de arquivo com fechamento
- [x] Validação frontend: extensão e tamanho antes do upload (Sprint 8B)
- [x] Botão "Processar" bloqueado sem extrato_bancario + planilha_interna (Sprint 8B)

## Sprint 5 — Fechamentos financeiros ✅ CONCLUÍDA (2026-06-09)

- [x] Migration `fechamentos_financeiros` (005)
- [x] Migrations adicionais (008, 013, 014): valores, aprovação, reabertura
- [x] Model SQLAlchemy `FechamentoFinanceiro`
- [x] Endpoint `GET /api/v1/conciliacoes` — listagem com filtros e paginação
- [x] Endpoint `POST /api/v1/conciliacoes` — criação
- [x] Endpoint `GET /api/v1/conciliacoes/{id}` — detalhe completo
- [x] Endpoint `POST /api/v1/conciliacoes/{id}/processar` — processamento
- [x] Endpoint `POST /api/v1/conciliacoes/{id}/aprovar` — aprovação (Sprint 8A)
- [x] Endpoint `POST /api/v1/conciliacoes/{id}/reabrir` — reabertura (Sprint 8A)
- [x] Endpoint `GET /api/v1/conciliacoes/{id}/exportar` — exportação Excel (Sprint 8A)
- [x] Tela `/conciliacoes`
- [x] Tela `/conciliacoes/nova`
- [x] Tela `/conciliacoes/[id]` — detalhe com seções de revisão e pacote final
- [x] Alterar status do fechamento (rascunho → arquivos_enviados → processado → aprovado → reaberto)
- [x] Associar arquivos ao fechamento
- [x] Listagem com histórico e filtros

## Sprint 6 — Motor de conciliação ✅ CONCLUÍDA (2026-06-09)

- [x] Migration `itens_conciliacao` (011)
- [x] Migration `divergencias_conciliacao` (011)
- [x] Migration `quantidade_pendentes` em fechamentos_financeiros (011)
- [x] Serviço `motor_conciliacao` com 8 classificações específicas
- [x] Leitor de Excel (Pandas/OpenPyXL) — Sprint 6A
- [x] Normalizador de colunas por modelo de arquivo — Sprint 6A
- [x] Detecção de duplicidade no extrato (`duplicidade_extrato`)
- [x] Detecção de duplicidade no fluxo (`duplicidade_fluxo`)
- [x] Match perfeito (mesma data, mesmo valor) → `conciliado`
- [x] Divergência de data (mesmo valor, data 1–3 dias) → `divergencia_data`
- [x] Divergência de valor (data próxima, valor diferente ≤30%) → `divergencia_valor`
- [x] Previsto sem realização → `previsto_nao_realizado`
- [x] Realizado sem previsão → `realizado_nao_previsto` ou `pendente_analise_manual`
- [x] Gravação de itens conciliados e divergências
- [x] Atualização do status do fechamento (processado / com_divergencias / erro)
- [x] Logs de processamento
- [x] Endpoint `POST /api/v1/conciliacoes/{id}/processar`
- [x] Suporte a reprocessamento (DELETE antes de re-gravar)
- [x] Testes unitários das 8 classificações (28 testes, 28 passando)
- [x] Gabarito validado: 5 conciliados, 3 divergencia_data, 1 divergencia_valor, 1 previsto_nao_realizado, 1 realizado_nao_previsto, 1 duplicidade_extrato, 1 duplicidade_fluxo, 1 pendente_analise_manual
- [x] Botão processar e tela de resultado no frontend (Sprint 7)

## Sprint 7 — Divergências, observações e revisão do fechamento

### Backend

- [x] Migration `divergencias_conciliacao` (011)
- [x] `GET /api/v1/conciliacoes/{id}/itens` (criado Sprint 6B)
- [x] `GET /api/v1/conciliacoes/{id}/divergencias` com filtros de status, tipo e severidade (criado Sprint 6B)
- [x] `PATCH /api/v1/divergencias/{id}` — alterar status e observação (Sprint 7A)
- [x] Validação de transição de status (aberta → em_analise → resolvida / ignorada)
- [x] RLS em divergencias_conciliacao (select, insert, update por empresa — migration 012)
- [ ] Endpoint `GET /api/v1/conciliacoes/{id}` já retorna `quantidade_pendentes` ✅

### Frontend

- [x] Tela `/conciliacoes/[id]` — com seção "Fechamento preparado para revisão" e cards de contadores
- [x] Botão "Revisar divergências" leva para `/conciliacoes/[id]/divergencias`
- [x] Tela `/conciliacoes/[id]/divergencias` — listagem de registros de `divergencias_conciliacao`
- [x] Filtros por status (aberta / em_analise / resolvida / ignorada), tipo e severidade
- [x] Modal de revisão com detalhe, observação e seletor de status
- [x] PATCH `/api/v1/divergencias/{id}` integrado — atualiza linha sem reload
- [x] Contadores locais: total, abertas, em_analise, resolvidas, ignoradas
- [x] Linguagem orientada a revisão ("Fechamento preparado", "Divergências do fechamento", "Pendências para análise", "Revisar divergências", "Salvar revisão")

## Sprint 8 — Relatórios, exportação e pacote final ✅ CONCLUÍDA (2026-06-09)

### Sprint 8A — Pacote final do fechamento
- [x] Endpoint `POST /api/v1/conciliacoes/{id}/aprovar` com validação de divergências abertas
- [x] Endpoint `POST /api/v1/conciliacoes/{id}/reabrir`
- [x] Endpoint `GET /api/v1/conciliacoes/{id}/exportar` — Excel em memória com 5 abas
- [x] Migration 013: `observacao_aprovacao`, `reaberto_em`, `reaberto_por_usuario_id`
- [x] Migration 014: `motivo_reabertura`
- [x] Componente `PacoteFinalFechamento.vue` com botões Aprovar / Exportar / Reabrir
- [x] Modal de aprovação e modal de reabertura
- [x] Bloqueio de aprovação com divergências abertas ou em_analise
- [x] Logs: `fechamento_aprovado`, `fechamento_reaberto`, `relatorio_fechamento_exportado`

### Sprint 8B — Upload real de arquivos (validação ponta a ponta)
- [x] Stub `alert` de upload substituído por scroll para seção de arquivos
- [x] Validação frontend: extensão e tamanho antes do envio (`arquivo.schema.ts`)
- [x] Botão "Processar" bloqueado sem `extrato_bancario` + `planilha_interna`
- [x] Mensagem de orientação ao usuário quando arquivos mínimos ausentes

### Pendente do Sprint 8 original
- [ ] Dashboard `/dashboard` com indicadores reais (planejado para Sprint 10)
- [ ] Resumo executivo com IA (fora do MVP)
- [ ] Geração de relatório em Supabase Storage (decidido: download direto em memória para MVP)
