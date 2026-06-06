# FDD 08, Relatórios e exportação

## 1. Objetivo

Gerar saídas úteis para o cliente após o processamento do fechamento.

## 2. Escopo

Relatório do fechamento, exportação Excel e arquivo de divergências.

## 3. Saídas do MVP

- planilha conciliada
- relatório de divergências
- resumo do fechamento
- arquivo processado armazenado no Supabase Storage

## 4. Regras de negócio

- Relatório só pode ser gerado após processamento.
- Exportação deve conter informações do fechamento.
- Exportação deve respeitar empresa do usuário.
- Arquivos exportados devem ficar vinculados ao fechamento.
- Exportações devem ser registradas.

## 5. Tabela

`relatorios_fechamento`

## 6. Colunas principais

- `id`
- `empresa_id`
- `fechamento_id`
- `tipo_relatorio`
- `nome_arquivo`
- `caminho_storage`
- `formato`
- `gerado_por_usuario_id`
- `criado_em`

## 7. Tipos de relatório

- `planilha_conciliada`
- `relatorio_divergencias`
- `resumo_fechamento`

## 8. Telas

- `/fechamentos/[id]/relatorio`
- `/fechamentos/[id]/exportar`

## 9. APIs

### GET `/api/fechamentos/{id}/relatorio`

Retorna resumo do fechamento.

### POST `/api/fechamentos/{id}/exportar`

Gera arquivo exportável.

### GET `/api/relatorios/{id}/download`

Baixa arquivo.

## 10. Critérios de aceite

- Usuário visualiza resumo do fechamento.
- Usuário exporta planilha conciliada.
- Usuário exporta divergências.
- Arquivo fica salvo no storage.
- Usuário baixa o arquivo exportado.

## 11. Tarefas para Claude Code

- Criar migration `relatorios_fechamento`.
- Criar gerador Excel com OpenPyXL.
- Criar endpoint de exportação.
- Criar tela de relatório.
- Criar fluxo de download.
