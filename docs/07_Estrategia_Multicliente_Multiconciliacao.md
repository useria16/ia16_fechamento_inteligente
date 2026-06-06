# Estratégia multicliente e multiconciliação

## 1. Objetivo

Este documento orienta como iniciar o iA16 Fechamento Inteligente atendendo dois clientes com necessidades próximas, mas não idênticas.

Cliente 1: Daxx Omnimedia, conciliação bancária.

Cliente 2: conciliação de caixa, recebíveis e controles financeiros.

O objetivo é evitar dois riscos:

1. criar uma aplicação específica demais para a Daxx
2. criar uma aplicação grande demais antes de validar o MVP

## 2. Decisão de produto

A aplicação será uma plataforma de conciliação financeira configurável.

Ela deve ter um núcleo comum e tipos de conciliação.

```text
Núcleo comum:
- empresas
- usuários
- fontes de dados
- modelos de arquivo
- uploads
- fechamentos
- normalização
- regras
- conciliação
- divergências
- relatórios
- logs

Tipos de conciliação:
- bancaria
- caixa
- recebiveis
- caixa_recebiveis
- vendas_recebimentos
- adquirentes
```

## 3. O que será comum para todos os clientes

As seguintes funcionalidades devem ser iguais para todos:

- login
- cadastro de empresas
- usuários por empresa
- fontes de dados
- upload de arquivos
- modelos de arquivo
- criação de fechamento
- processamento
- divergências
- observações
- exportação
- dashboard
- logs

## 4. O que pode variar por cliente

Os seguintes itens podem variar por empresa:

- tipo de conciliação
- arquivos obrigatórios
- fonte de verdade
- modelos de arquivo
- colunas esperadas
- regras de comparação
- tolerância de valor
- tolerância de data
- tipos de divergência priorizados
- formato da planilha final

## 5. Como atender a Daxx

Configuração inicial:

```text
empresa = Daxx Omnimedia
tipo_conciliacao = bancaria
entrada = extratos, planilhas internas, relatórios externos
objetivo = identificar divergências entre movimentações e controles
saída = planilha marcada com conciliados, divergentes e pendentes
```

## 6. Como atender o segundo cliente

Configuração inicial:

```text
empresa = Cliente 2
tipo_conciliacao = caixa_recebiveis
entrada = caixa, vendas, recebíveis, relatórios de cartão, planilhas internas
objetivo = conferir o que vendeu, o que entrou, o que ficou pendente e o que divergiu
saída = visão de caixa, recebíveis pendentes, divergências e fechamento do período
```

## 7. Modelo conceitual

```text
empresa
  possui usuarios
  possui fontes_dados
  possui modelos_arquivo
  possui configuracoes_conciliacao

tipo_conciliacao
  define a categoria do processamento

configuracao_conciliacao
  pertence a empresa
  pertence a tipo_conciliacao
  define tolerâncias
  define fonte de verdade
  possui regras

fechamento_financeiro
  pertence a empresa
  usa tipo_conciliacao
  usa configuracao_conciliacao
  possui arquivos
  gera transações
  gera divergências
  gera relatórios
```

## 8. Regras de implementação

- Não criar código hardcoded para Daxx.
- Não criar tabelas com nome de cliente.
- Não criar uma tela diferente para cada cliente.
- Usar configuração para diferenciar os cenários.
- O motor de conciliação deve receber a configuração e aplicar as regras.
- O layout de exportação pode ter variações, mas deve partir de uma estrutura comum.

## 9. MVP recomendado

Para a primeira versão, implementar:

1. tipos de conciliação
2. configuração de conciliação por empresa
3. modelos de arquivo por empresa e tipo de conciliação
4. regras simples em JSON ou tabela
5. motor de conciliação com regras determinísticas
6. exportação Excel comum

## 10. O que não fazer agora

Não implementar no MVP:

- motor visual de regras
- construtor de workflows
- integração bancária automática
- Open Finance
- ERP
- conciliação fiscal
- BI avançado
- múltiplos layouts altamente customizados

## 11. Frase guia

A aplicação deve permitir cadastrar empresas diferentes, cada uma com seus tipos de conciliação, arquivos, regras e tolerâncias, usando o mesmo núcleo de fechamento financeiro.
