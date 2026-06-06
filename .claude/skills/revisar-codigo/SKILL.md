---
name: revisar-codigo
description: Revisa código do projeto conforme arquitetura, segurança e regras de negócio
---

# Revisar código

Revise a implementação atual considerando as regras do projeto.

## Verificar

- se a aplicação continua multicliente
- se não existe lógica específica para Daxx
- se objetos de banco estão em português
- se SQLAlchemy 2.x está sendo usado corretamente
- se Supabase Auth está sendo respeitado
- se RLS foi considerado
- se arquivos sensíveis não foram expostos
- se o motor de conciliação é determinístico
- se IA não altera dados financeiros
- se frontend, backend e motor estão bem separados

## Saída esperada

- problemas encontrados
- risco de cada problema
- arquivos afetados
- recomendações
- correções sugeridas
- ordem recomendada de ajuste
