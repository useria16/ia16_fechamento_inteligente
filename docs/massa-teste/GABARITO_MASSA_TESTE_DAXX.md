# Gabarito da Massa de Teste — Sprint 6

## Visão geral

| Item | Valor |
|---|---|
| Empresa fictícia | EMPRESA SINTESE LTDA |
| Conta bancária | 0099999-1 / Agência 0001 |
| Período do teste | 10/06/2026 a 14/06/2026 |
| Schema de destino | ia16_fechamento_dev |
| Bucket de destino | arquivos-originais |
| Tolerância de data | 3 dias (configurável) |
| Tolerância de valor | 1,00% do valor (configurável) |

---

## Cenários e registros esperados

---

### CENARIO_01 — Match perfeito

| Campo | Extrato | Fluxo de Caixa |
|---|---|---|
| Data | 10/06/2026 | 10/06/2026 |
| Razão Social / Categoria | CENARIO_01_MATCH_PERFEITO SERVICOS LTDA | Folha de Pagamento (PJ) - CENARIO_01_MATCH_PERFEITO |
| Valor | -1.500,00 | -1.500,00 |
| NF/DOC | 001 | — |

**Resultado esperado:** `conciliado`

**Observação:** Data igual, valor igual, categoria compatível. Par perfeito. O motor deve associar automaticamente.

---

### CENARIO_01B — Match perfeito (receita)

| Campo | Extrato | Fluxo de Caixa |
|---|---|---|
| Data | 10/06/2026 | 10/06/2026 |
| Razão Social / Categoria | CENARIO_01B_MATCH_PERFEITO COMERCIO SA | Receita Operacional - VENDAS (CLIENTE) - CENARIO_01B |
| Valor | +8.200,00 | +8.200,00 |

**Resultado esperado:** `conciliado`

**Observação:** Match em receita. Mesmo comportamento do CENARIO_01.

---

### CENARIO_01C — Match perfeito (adicional)

| Campo | Extrato | Fluxo de Caixa |
|---|---|---|
| Data | 14/06/2026 | 14/06/2026 |
| Razão Social / Categoria | CENARIO_01C_MATCH_PERFEITO ADICIONAL COMERCIO | Receita Operacional - VENDAS (CLIENTE) - CENARIO_01C |
| Valor | +2.100,00 | +2.100,00 |

**Resultado esperado:** `conciliado`

---

### CENARIO_02 — Valor igual, data diferente

| Campo | Extrato | Fluxo de Caixa |
|---|---|---|
| Data | **11/06/2026** | **10/06/2026** |
| Razão Social / Categoria | CENARIO_02_DATA_DIFERENTE TECNOLOGIA LTDA | Internet - CENARIO_02_DATA_DIFERENTE |
| Valor | -320,00 | -320,00 |
| Diferença de data | 1 dia | — |

**Resultado esperado:** `divergencia_data`

**Tolerância:** Dentro de 3 dias → deve ser sinalizado como divergência de data, mas ainda conciliável com confirmação.

**Observação:** O boleto foi pago 1 dia após o previsto. Valor idêntico. O motor deve encontrar a correspondência e marcar a data como divergente.

---

### CENARIO_03 — Previsto não realizado

| Campo | Extrato | Fluxo de Caixa |
|---|---|---|
| Data | — (não existe) | 14/06/2026 |
| Razão Social / Categoria | — | Freelancer Variável - CENARIO_03_PREVISTO_NAO_REALIZADO |
| Valor | — | -400,00 |

**Resultado esperado:** `previsto_nao_realizado`

**Observação:** Item estava planejado no fluxo para 14/06/2026, mas não gerou lançamento bancário. Motor deve listar como não conciliado no lado do fluxo.

---

### CENARIO_04 — Realizado não previsto

| Campo | Extrato | Fluxo de Caixa |
|---|---|---|
| Data | 11/06/2026 | — (não existe) |
| Razão Social / Categoria | CENARIO_04_REALIZADO_NAO_PREVISTO AUTONOMO | — |
| Valor | -950,00 | — |

**Resultado esperado:** `realizado_nao_previsto`

**Observação:** Lançamento ocorreu no banco mas não havia previsão no fluxo. Motor deve listar como não conciliado no lado do extrato.

---

### CENARIO_05 — Valor diferente

| Campo | Extrato | Fluxo de Caixa |
|---|---|---|
| Data | 12/06/2026 | 12/06/2026 |
| Razão Social / Categoria | CENARIO_05_VALOR_DIFERENTE RECURSOS LTDA | Folha de Pagamento (PJ) - CENARIO_05_VALOR_DIFERENTE |
| Valor | **-3.400,00** | **-3.600,00** |
| Diferença de valor | 200,00 (5,56%) | — |

**Resultado esperado:** `divergencia_valor`

**Tolerância de valor:** A diferença é de 5,56% — acima da tolerância de 1%. Deve gerar divergência de valor.

**Observação:** Folha paga com valor inferior ao previsto. O motor deve encontrar o par pela data e categoria, registrar a divergência de 200,00 e sinalizar para revisão manual.

---

### CENARIO_06 — Antecipação de recebimento

| Campo | Extrato | Fluxo de Caixa |
|---|---|---|
| Data extrato | **12/06/2026** | — |
| Data fluxo | — | **15/06/2026** |
| Razão Social / Categoria | CENARIO_06_ANTECIPACAO_RECEBIMENTO CLIENTE SA | Receita Operacional - VENDAS (CLIENTE) - CENARIO_06 |
| Valor | +5.500,00 | +5.500,00 |
| Diferença de data | 3 dias (antecipado) | — |

**Resultado esperado:** `divergencia_data` (subtipo: antecipação)

**Observação:** Recebimento chegou 3 dias antes do previsto. Valor idêntico. Dentro da tolerância de data (3 dias). O motor deve conciliar com flag de divergência de data = antecipação.

---

### CENARIO_07 — Pagamento atrasado

| Campo | Extrato | Fluxo de Caixa |
|---|---|---|
| Data extrato | **13/06/2026** | — |
| Data fluxo | — | **10/06/2026** |
| Razão Social / Categoria | CENARIO_07_PAGAMENTO_ATRASADO FORNECEDOR ME | Aluguel PE - CENARIO_07_PAGAMENTO_ATRASADO |
| Valor | -780,00 | -780,00 |
| Diferença de data | 3 dias (atrasado) | — |

**Resultado esperado:** `divergencia_data` (subtipo: atraso)

**Observação:** Pagamento ocorreu 3 dias após o previsto. Valor idêntico. Dentro da tolerância. O motor deve conciliar com flag de divergência de data = atraso.

---

### CENARIO_08 — Duplicidade no extrato

| Lançamento | Extrato | Fluxo de Caixa |
|---|---|---|
| 1ª ocorrência (CEN08a) | 13/06/2026, PIX ENVIADO, CENARIO_08_DUPLICIDADE_EXTRATO DIARISTA ME, -200,00 | Limpeza / Diarista, 13/06/2026, -200,00 |
| 2ª ocorrência (CEN08b) | 13/06/2026, PIX ENVIADO, CENARIO_08_DUPLICIDADE_EXTRATO DIARISTA ME, -200,00 | — (sem correspondência) |

**Resultado aprovado (Sprint 6B):**
- CEN08a → `conciliado` (match perfeito com o único previsto disponível)
- CEN08b → `duplicidade_extrato` (ocorrência excedente — sinalizada para revisão manual)

**Decisão técnica do motor — regra conservadora de duplicidade:**
O motor adota a abordagem conservadora: a primeira ocorrência de um grupo duplicado participa normalmente do matching. Apenas as ocorrências excedentes são flagadas como `duplicidade_extrato`. Essa decisão foi validada na Sprint 6B e evita penalizar o lançamento que possui par previsto claro.

Essa regra é aplicada também para o lado do fluxo (`duplicidade_fluxo`): a primeira previsão duplicada é mantida no pool de matching; as demais são flagadas.

**Observação:** Mesmo beneficiário, mesma data, mesmo valor, dois lançamentos no extrato. O fluxo só tem uma previsão de -200,00. A decisão final sobre a duplicidade (erro do banco vs. pagamento legítimo) permanece manual.

---

### CENARIO_09 — Duplicidade no fluxo de caixa

| Lançamento | Extrato | Fluxo de Caixa |
|---|---|---|
| Realizado (CEN09) | 14/06/2026, BOLETO PAGO, CENARIO_09_DUPLICIDADE_FLUXO SOFTWARE LTDA, -650,00 | — |
| Previsão A (CEN09A) | — | Licenças de Software - CENARIO_09A_DUPLICIDADE_FLUXO, 14/06/2026, -650,00 |
| Previsão B (CEN09B) | — | Licenças de Software - CENARIO_09B_DUPLICIDADE_FLUXO, 14/06/2026, -650,00 |

**Resultado aprovado (Sprint 6B):**
- CEN09B → `duplicidade_fluxo` (segunda previsão idêntica — flagada antes do matching)
- CEN09A → mantida no pool de matching → conciliada com CEN09 (extrato) → `conciliado`

**Observação:** O fluxo previu o mesmo gasto duas vezes na mesma data. O extrato tem apenas um pagamento. Pela regra conservadora de duplicidade, CEN09B é removida do pool antes do matching. CEN09 casa com CEN09A normalmente. A decisão final sobre a duplicidade no fluxo (erro de planejamento vs. pagamento parcelado) é manual.

---

### CENARIO_10 — Pendente para análise manual

| Campo | Extrato | Fluxo de Caixa |
|---|---|---|
| Data | 14/06/2026 | — |
| Razão Social | CENARIO_10_PENDENTE_ANALISE TRANSF S/IDENTIFICACAO | — |
| Valor | +3.700,00 | — |

**Resultado esperado:** `pendente_analise_manual`

**Observação:** TED recebida sem identificação clara de origem. Não há correspondência direta no fluxo de caixa. O motor não deve tentar conciliar automaticamente — deve registrar como pendente para análise humana.

---

## Resumo dos resultados aprovados (Sprint 6B)

| Código | Cenário | tipo_item | E existe? | F existe? |
|---|---|---|---|---|
| CEN01a | Match perfeito (despesa) | `conciliado` | ✅ | ✅ |
| CEN01b | Match perfeito (receita) | `conciliado` | ✅ | ✅ |
| CEN01c | Match perfeito (adicional) | `conciliado` | ✅ | ✅ |
| CEN08a | Duplicidade extrato (1ª — conciliada) | `conciliado` | ✅ | ✅ |
| CEN09  | Duplicidade fluxo (extrato — conciliado com 09A) | `conciliado` | ✅ | ✅ |
| CEN02  | Data diferente (1 dia) | `divergencia_data` | ✅ | ✅ |
| CEN06  | Antecipação de recebimento (3 dias) | `divergencia_data` | ✅ | ✅ |
| CEN07  | Pagamento atrasado (3 dias) | `divergencia_data` | ✅ | ✅ |
| CEN05  | Valor diferente (-5,56%) | `divergencia_valor` | ✅ | ✅ |
| CEN03  | Previsto não realizado | `previsto_nao_realizado` | ❌ | ✅ |
| CEN04  | Realizado não previsto | `realizado_nao_previsto` | ✅ | ❌ |
| CEN08b | Duplicidade extrato (2ª — excedente) | `duplicidade_extrato` | ✅ | ❌ |
| CEN09B | Duplicidade fluxo (previsão excedente) | `duplicidade_fluxo` | ❌ | ✅ |
| CEN10  | Pendente análise manual | `pendente_analise_manual` | ✅ | ❌ |

---

## Tolerâncias iniciais recomendadas

| Tipo | Tolerância | Justificativa |
|---|---|---|
| Data | 3 dias corridos | Cobre fins de semana e feriados bancários |
| Valor | 1,00% do valor previsto | Cobre diferenças de centavos por arredondamento |
| Valor mínimo | R$ 0,01 | Diferenças menores são ignoradas |

---

## Contadores aprovados — Sprint 6B

Resultado validado em `2026-06-09` com o fechamento `48626b8e-cfb5-48d1-9774-a2c5607e9d55`.

| tipo_item | qtd | Cenários |
|---|---|---|
| `conciliado` | **5** | CEN01a, CEN01b, CEN01c, CEN08a, CEN09 |
| `divergencia_data` | 3 | CEN02, CEN06, CEN07 |
| `divergencia_valor` | 1 | CEN05 |
| `previsto_nao_realizado` | 1 | CEN03 |
| `realizado_nao_previsto` | 1 | CEN04 |
| `duplicidade_extrato` | 1 | CEN08b |
| `duplicidade_fluxo` | 1 | CEN09B |
| `pendente_analise_manual` | 1 | CEN10 |
| **Total de itens** | **14** | |

| Contador no fechamento | Valor |
|---|---|
| `quantidade_conciliados` | 5 |
| `quantidade_divergentes` | 8 |
| `quantidade_pendentes` | 1 |
| `status` | `com_divergencias` |
| `pronto_para_revisao` | `true` |

**Nota sobre contadores:**
- `quantidade_divergentes` = todos os `tipo_item` diferentes de `conciliado` e `pendente_analise_manual` (divergencia_data + divergencia_valor + previsto_nao_realizado + realizado_nao_previsto + duplicidade_extrato + duplicidade_fluxo = 8)
- `quantidade_pendentes` = apenas `pendente_analise_manual` (1)

| Fonte | Total de registros |
|---|---|
| Extrato bancário | 12 lançamentos |
| Fluxo de caixa | 11 previsões |

---

## Como usar no smoke test do Storage

```bash
# 1. Subir os arquivos pela conciliação real no frontend:
#    /conciliacoes/48626b8e-cfb5-48d1-9774-a2c5607e9d55

# 2. Enviar na ordem:
#    TESTE_Extrato_Lancamentos_banco.xlsx  → tipo: extrato_bancario
#    TESTE_Fluxo_Caixa_Daxx.xlsx          → tipo: planilha_interna

# 3. Validar no banco:
SELECT nome_original, modo_retencao, arquivo_persistido, expira_em, hash_arquivo
FROM ia16_fechamento_dev.arquivos_enviados
ORDER BY criado_em DESC LIMIT 5;

# 4. Clicar em "Processar conciliação" e verificar status = processado
# 5. Confirmar logs em logs_processamento
```

---

## Queries de validação (reprocessamento)

```sql
-- Itens por tipo
SELECT status, tipo_item, COUNT(*)
FROM ia16_fechamento_dev.itens_conciliacao
WHERE fechamento_id = '48626b8e-cfb5-48d1-9774-a2c5607e9d55'
GROUP BY status, tipo_item
ORDER BY status, tipo_item;

-- Divergências por tipo
SELECT tipo_divergencia, severidade, status, COUNT(*)
FROM ia16_fechamento_dev.divergencias_conciliacao
WHERE fechamento_id = '48626b8e-cfb5-48d1-9774-a2c5607e9d55'
GROUP BY tipo_divergencia, severidade, status
ORDER BY tipo_divergencia;

-- Resumo do fechamento
SELECT status, quantidade_conciliados, quantidade_divergentes, quantidade_pendentes
FROM ia16_fechamento_dev.fechamentos_financeiros
WHERE id = '48626b8e-cfb5-48d1-9774-a2c5607e9d55';
```

## Sprint 7 — Próximas entregas

- Tela de divergências do fechamento
- Listagem com filtros (status, tipo, severidade)
- Detalhe da divergência
- Campo de observação
- Alteração de status (aberta → em_analise → resolvida → ignorada)
- Resumo de revisão na página da conciliação
- Linguagem orientada a revisão do fechamento
