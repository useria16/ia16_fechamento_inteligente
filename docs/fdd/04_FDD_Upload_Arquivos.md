# FDD 04, Upload de arquivos

## 1. Objetivo

Permitir que o cliente envie planilhas financeiras para processamento.

## 2. Escopo

Upload de arquivos Excel, armazenamento no Supabase Storage, registro dos metadados e associação com empresa, fonte e fechamento.

## 3. Regras de negócio

- Aceitar arquivos `.xlsx`.
- Aceitar `.csv` somente se configurado.
- Todo arquivo deve pertencer a uma empresa.
- Todo arquivo deve ter tipo.
- Arquivo pode ser associado a um fechamento.
- Arquivo original nunca deve ser sobrescrito.
- Arquivo inválido deve ser rejeitado com mensagem clara.

## 4. Tabela

`arquivos_enviados`

## 5. Colunas principais

- `id`
- `empresa_id`
- `fechamento_id`
- `fonte_dados_id`
- `modelo_arquivo_id`
- `nome_original`
- `nome_armazenado`
- `tipo_arquivo`
- `caminho_storage`
- `tamanho_bytes`
- `status`
- `mensagem_erro`
- `criado_por_usuario_id`
- `criado_em`
- `atualizado_em`

## 6. Status de arquivo

- `enviado`
- `validado`
- `invalido`
- `processado`
- `erro`

## 7. Telas

- `/arquivos`
- `/arquivos/enviar`
- `/arquivos/[id]`

## 8. APIs

### POST `/api/arquivos`

Recebe metadados e arquivo.

### GET `/api/arquivos`

Lista arquivos.

### GET `/api/arquivos/{id}`

Detalha arquivo.

### DELETE `/api/arquivos/{id}`

Inativa ou remove logicamente o arquivo.

## 9. Critérios de aceite

- Usuário envia arquivo Excel.
- Arquivo é salvo no Supabase Storage.
- Metadados são gravados em `arquivos_enviados`.
- Arquivo aparece na listagem.
- Arquivo fica vinculado à empresa correta.
- Arquivo inválido recebe status `invalido`.

## 10. Tarefas para Claude Code

- Configurar upload no frontend.
- Criar endpoint de upload no FastAPI.
- Integrar Supabase Storage.
- Criar migration `arquivos_enviados`.
- Criar validação de extensão e tamanho.
- Criar tela de listagem e tela de envio.
