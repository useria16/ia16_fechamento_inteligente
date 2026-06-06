---
name: ia16-criar-regra-conciliacao
description: Cria ou ajusta regra de conciliação financeira configurável
---

# Criar regra de conciliação

Crie regras de conciliação sem hardcode por cliente.

## Regras obrigatórias

- Toda regra deve pertencer a uma configuração de conciliação.
- Toda configuração deve pertencer a uma empresa.
- Toda configuração deve pertencer a um tipo de conciliação.
- Não criar regra com nome de cliente.
- Não usar IA para decidir valores.
- A regra deve ser auditável e explicável.

## Operadores permitidos inicialmente

- igual
- valor_igual
- valor_com_tolerancia
- data_igual
- data_com_tolerancia
- texto_contem
- texto_similar
- existe
- nao_existe

## Ao criar uma regra

Informe:

- nome da regra
- tipo de conciliação
- campos comparados
- operador
- tolerância
- prioridade
- resultado esperado
- tipo de divergência gerado quando falhar
