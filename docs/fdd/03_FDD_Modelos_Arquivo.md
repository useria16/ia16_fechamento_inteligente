# FDD 03, Modelos de arquivo

## 1. Objetivo

Definir o padrão esperado de colunas para cada tipo de arquivo financeiro enviado pelo cliente.

## 2. Escopo

O MVP deve permitir criar modelos simples de arquivo por empresa e tipo de arquivo.

## 3. Tipos de arquivo

- `extrato_bancario`
- `relatorio_vendas`
- `relatorio_recebiveis`
- `planilha_interna`
- `taxas_adquirente`
- `outro`

## 4. Regras de negócio

- Cada modelo pertence a uma empresa.
- Cada modelo possui tipo de arquivo.
- O modelo define colunas esperadas.
- O processamento usa o modelo para normalizar dados.
- No MVP, o cadastro pode ser simples, usando JSON de mapeamento.

## 5. Tabela

`modelos_arquivo`

## 6. Colunas principais

- `id`
- `empresa_id`
- `nome`
- `tipo_arquivo`
- `mapeamento_colunas`
- `ativo`
- `criado_em`
- `atualizado_em`

## 7. Exemplo de mapeamento

```json
{
  "data": "Data Venda",
  "valor_bruto": "Valor Bruto",
  "valor_liquido": "Valor Líquido",
  "documento": "Documento",
  "descricao": "Descrição"
}
```

## 8. Telas

- `/modelos`
- `/modelos/novo`
- `/modelos/[id]`

## 9. APIs

### GET `/api/modelos-arquivo`

Lista modelos.

### POST `/api/modelos-arquivo`

Cria modelo.

### PATCH `/api/modelos-arquivo/{id}`

Atualiza modelo.

## 10. Critérios de aceite

- Admin cria modelo de arquivo.
- Modelo pode ser associado a arquivos enviados.
- Backend consegue ler o mapeamento.
- Colunas customizadas ficam armazenadas em JSON.

## 11. Tarefas para Claude Code

- Criar migration `modelos_arquivo`.
- Criar schemas Pydantic.
- Criar endpoints.
- Criar tela de cadastro.
- Criar validação básica do JSON de mapeamento.
