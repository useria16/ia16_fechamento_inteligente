# FDD 12, Tipos, configurações e regras de conciliação

## 1. Objetivo

Permitir que a aplicação atenda múltiplos clientes e múltiplos tipos de conciliação usando configuração, sem criar código específico para cada empresa.

## 2. Escopo

Inclui cadastro de tipos de conciliação, configuração de conciliação por empresa e regras de conciliação.

## 3. Tipos de conciliação iniciais

- `bancaria`
- `caixa`
- `recebiveis`
- `caixa_recebiveis`
- `vendas_recebimentos`
- `adquirentes`
- `outro`

## 4. Regras de negócio

- Todo fechamento deve ter um tipo de conciliação.
- Uma empresa pode ter várias configurações de conciliação.
- Uma configuração pertence a uma empresa e a um tipo de conciliação.
- Regras pertencem a uma configuração.
- O motor de conciliação deve aplicar as regras da configuração selecionada.
- Não deve haver regra hardcoded por cliente.
- Regras podem começar simples, com estrutura tabular ou JSON.

## 5. Tabelas

- `tipos_conciliacao`
- `configuracoes_conciliacao`
- `regras_conciliacao`

## 6. Colunas principais

### tipos_conciliacao

- `id`
- `nome`
- `codigo`
- `descricao`
- `ativo`
- `criado_em`
- `atualizado_em`

### configuracoes_conciliacao

- `id`
- `empresa_id`
- `tipo_conciliacao_id`
- `nome`
- `fonte_verdade_id`
- `tolerancia_valor`
- `tolerancia_dias`
- `parametros`
- `ativo`
- `criado_em`
- `atualizado_em`

### regras_conciliacao

- `id`
- `configuracao_conciliacao_id`
- `nome`
- `ordem`
- `campo_origem`
- `campo_destino`
- `operador`
- `peso`
- `obrigatoria`
- `ativo`
- `criado_em`
- `atualizado_em`

## 7. Operadores iniciais

- `igual`
- `valor_igual`
- `valor_com_tolerancia`
- `data_igual`
- `data_com_tolerancia`
- `texto_contem`
- `texto_similar`
- `existe`
- `nao_existe`

## 8. Telas

- `/tipos-conciliacao`
- `/configuracoes-conciliacao`
- `/configuracoes-conciliacao/nova`
- `/configuracoes-conciliacao/[id]`

No MVP, essas telas podem ser acessadas apenas pelo admin iA16.

## 9. APIs

### GET `/api/tipos-conciliacao`

Lista tipos de conciliação.

### POST `/api/tipos-conciliacao`

Cria tipo de conciliação.

### GET `/api/configuracoes-conciliacao`

Lista configurações.

### POST `/api/configuracoes-conciliacao`

Cria configuração.

### PATCH `/api/configuracoes-conciliacao/{id}`

Atualiza configuração.

### POST `/api/configuracoes-conciliacao/{id}/regras`

Cria regra de conciliação.

## 10. Critérios de aceite

- Admin cria tipo de conciliação.
- Admin cria configuração para uma empresa.
- Admin define tolerância de valor e data.
- Admin cria regras de conciliação.
- Fechamento usa tipo e configuração.
- Motor aplica regras da configuração selecionada.
- Daxx pode usar conciliação bancária.
- Outro cliente pode usar caixa/recebíveis sem alterar o código base.

## 11. Tarefas para Claude Code

- Criar migrations das três tabelas.
- Atualizar `fechamentos_financeiros` com `tipo_conciliacao_id` e `configuracao_conciliacao_id`.
- Criar models SQLAlchemy.
- Criar schemas Pydantic.
- Criar endpoints CRUD.
- Atualizar tela de criação de fechamento para selecionar tipo/configuração.
- Atualizar motor de conciliação para carregar regras da configuração.
- Criar seed inicial com tipos de conciliação.
