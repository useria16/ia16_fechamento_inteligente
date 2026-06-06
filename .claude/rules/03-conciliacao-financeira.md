# Conciliação financeira

## Princípio

A conciliação deve ser determinística, auditável e explicável.

IA não pode decidir valores financeiros.

IA pode ajudar apenas com:

- resumo executivo
- explicação textual
- sugestão de observação
- sugestão de ação

## Tipos de conciliação iniciais

- bancaria
- caixa
- recebiveis
- caixa_recebiveis
- vendas_recebimentos
- adquirentes
- outro

## Regras iniciais

O motor deve suportar regras como:

- documento igual
- valor igual
- valor com tolerância
- data igual
- data com tolerância
- descrição semelhante
- registro existente em uma fonte e ausente em outra
- duplicidade
- divergência de valor
- divergência de data

## Estrutura esperada

Um fechamento financeiro deve:

- pertencer a uma empresa
- ter um tipo de conciliação
- usar uma configuração de conciliação
- possuir arquivos vinculados
- gerar transações normalizadas
- gerar itens de conciliação
- gerar divergências
- gerar relatório final

## Regra proibida

Não criar lógica como:

- se empresa for Daxx, aplicar regra X
- se cliente for Y, aplicar regra Z

Use sempre configuração, tipo de conciliação e regras cadastradas.
