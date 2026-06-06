# Padrão de desenvolvimento

## Antes de implementar

Sempre listar:

- arquivos que serão criados
- arquivos que serão modificados
- objetivo da mudança
- FDD ou documento de referência

## Durante a implementação

Respeitar:

- arquitetura multicliente
- banco em português
- SQLAlchemy 2.x
- FastAPI no backend
- Nuxt 4 no frontend
- Supabase para auth, banco, storage e RLS
- Docker para execução

## Depois de implementar

Sempre informar:

- o que foi implementado
- como testar
- comandos necessários
- próximos passos
- riscos ou pendências

## Proibições

- Não criar lógica hardcoded para cliente.
- Não criar tabela em inglês.
- Não usar SQLModel.
- Não adicionar Open Finance no MVP.
- Não adicionar ERP no MVP.
- Não transformar o produto em sistema financeiro completo.
